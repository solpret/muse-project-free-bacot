#!/usr/bin/env python3
"""Feed shape-check run 2026-11-11 0801 WIB (main job route 5a).
Shape-checks the 20 newly verified Sourcify contracts from
run-2026-11-11-0901-feed.json for SALE shape S1/S2 and for agent-mint
early-lead shape (ERC721/1155 + registry/AgentGate/free-mint).
Read-only; writes run-2026-11-11-0901-feed-shape.json only.
Does NOT write hot-leg-seen.json (hot leg owns that file)."""
import json, time, urllib.request, concurrent.futures

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
FREE_VIEWS = ["freeSharesRemaining", "freeClaimed", "freeFor", "freeLeft", "freeUsed",
              "freeAvailable", "freeSharePoolExhausted", "freeSharesClaimed",
              "freeMinted", "freeCardsRemaining"]
EXCLUDED = {"0x827e83e49bd7e15b67efa0e90fc25f17b8d96124",
            "0x8b47354e7b76b1970a0d06365c8244a810d37493"}
REGISTRY = "0x60b9262456de011f7d15a54cdd8c48baaa8b022f"

feed = json.load(open(BASE + "run-2026-11-11-0901-feed.json"))
items = feed.get("results", feed if isinstance(feed, list) else [])
addrs = [it.get("address") for it in items if isinstance(it, dict) and it.get("address")]

def fetch_abi(addr):
    url = f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "free-bacot/1.0"})
        with urllib.request.urlopen(req, timeout=15) as r:
            meta = json.loads(r.read().decode())
        abi = meta.get("abi", [])
        fns = {}
        for e in abi:
            if e.get("type") == "function":
                fns.setdefault(e["name"], []).append(e)
        names = set(fns)
        has_mint = any(n.lower().startswith("mint") for n in names)
        has_quote = bool(names & {"quote", "cost", "getQuote", "mintCost", "price", "getPrice"})
        free_views = sorted(names & set(FREE_VIEWS))
        agent_ref = bool(names & {"agentId", "agentRegistry", "registry", "getAgentId", "agentGate", "AgentGate"})
        is_token = bool(names & {"name", "symbol", "decimals", "totalSupply"})
        mintfree = "mintFree" in fns and any(len(e.get("inputs", [])) == 0 for e in fns["mintFree"])
        s1 = has_mint and has_quote and bool(free_views) and agent_ref
        s2 = is_token and mintfree and bool(names & {"freeClaimed", "freeMinted"}) and bool(names & {"FREE_SLOTS", "FREE_SUPPLY"}) and agent_ref
        # early-lead agent-mint shape: NFT markers + (registry ref or free-mint fn)
        is_nft = bool(names & {"tokenURI", "ownerOf", "safeTransferFrom"}) or "uri" in names
        free_mint_fn = bool(names & {"freeMint", "mintFree", "claimFree", "mint"}) or any(
            n.lower().startswith("freemint") for n in names)
        early_shape = is_nft and (agent_ref or free_mint_fn)
        return {"address": addr, "verifiedAt": next((it.get("verifiedAt") for it in items if it.get("address") == addr), None),
                "S1": s1, "S2": s2, "early_shape": early_shape,
                "has_mint": has_mint, "has_quote": has_quote, "free_views": free_views,
                "agent_ref": agent_ref, "is_token": is_token, "is_nft": is_nft,
                "fn_count": len(names), "fns": sorted(names)[:60]}
    except Exception as ex:
        return {"address": addr, "error": f"{type(ex).__name__}: {str(ex)[:120]}"}

t0 = time.time()
with concurrent.futures.ThreadPoolExecutor(max_workers=10) as ex:
    shapes = list(ex.map(fetch_abi, addrs))
out = {"started_wib": "2026-11-11 09:01 WIB", "elapsed_s": round(time.time() - t0, 1),
       "s1_pass": [s["address"] for s in shapes if s.get("S1")],
       "s2_pass": [s["address"] for s in shapes if s.get("S2")],
       "early_shape": [s["address"] for s in shapes if s.get("early_shape")],
       "shapes": shapes}
json.dump(out, open(BASE + "run-2026-11-11-0901-feed-shape.json", "w"), indent=1)
for s in shapes:
    print(s["address"], "S1" if s.get("S1") else "-", "S2" if s.get("S2") else "-",
          "EARLY" if s.get("early_shape") else "-",
          s.get("error", f"fns={s.get('fn_count')} free={s.get('free_views')} agent={s.get('agent_ref')} nft={s.get('is_nft')}"))
print(f"DONE {len(shapes)} in {time.time()-t0:.1f}s S1={len(out['s1_pass'])} S2={len(out['s2_pass'])} EARLY={len(out['early_shape'])}")
