#!/usr/bin/env python3
"""Shape-check 8 feed-new addresses run 1801 via curl (urllib RemoteDisconnected)."""
import json, subprocess, concurrent.futures
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
FREE_VIEWS = ["freeSharesRemaining", "freeClaimed", "freeFor", "freeLeft", "freeUsed",
              "freeAvailable", "freeSharePoolExhausted", "freeSharesClaimed",
              "freeMinted", "freeCardsRemaining"]
def fetch(addr):
    try:
        r = subprocess.run(["curl","-sL","--max-time","25",
            f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi"],
            capture_output=True, text=True, timeout=30)
        meta = json.loads(r.stdout)
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
        is_token = bool(names & {"name", "symbol", "decimals", "totalSupply", "balanceOf"}) and "totalSupply" in names
        mintfree = "mintFree" in fns and any(len(e.get("inputs", [])) == 0 for e in fns["mintFree"])
        s1 = has_mint and has_quote and bool(free_views) and agent_ref
        s2 = is_token and mintfree and bool(names & {"freeClaimed", "freeMinted"}) and bool(names & {"FREE_SLOTS", "FREE_SUPPLY"}) and agent_ref
        is_nft = bool(names & {"tokenURI", "ownerOf", "safeTransferFrom"}) or "uri" in names
        free_mint_fn = bool(names & {"freeMint", "mintFree", "claimFree", "mint"}) or any(n.lower().startswith("freemint") for n in names)
        early_shape = is_nft and (agent_ref or free_mint_fn)
        return {"address": addr, "S1": s1, "S2": s2, "early_shape": early_shape,
                "has_mint": has_mint, "has_quote": has_quote, "free_views": free_views,
                "agent_ref": agent_ref, "is_token": is_token, "is_nft": is_nft,
                "fn_count": len(names)}
    except Exception as ex:
        return {"address": addr, "error": f"{type(ex).__name__}: {str(ex)[:120]}"}
new = json.load(open(BASE + "run-2026-11-11-1801-feed-new.json"))
with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:
    shapes = list(ex.map(fetch, new))
out = {"s1_pass": [s["address"] for s in shapes if s.get("S1")],
       "s2_pass": [s["address"] for s in shapes if s.get("S2")],
       "early_shape": [s["address"] for s in shapes if s.get("early_shape")],
       "shapes": shapes}
json.dump(out, open(BASE + "run-2026-11-11-1801-shape-retry.json", "w"), indent=1)
for s in shapes:
    print(s["address"], "S1", s.get("S1"), "S2", s.get("S2"), "early", s.get("early_shape"),
          "mint", s.get("has_mint"), "quote", s.get("has_quote"), "free", s.get("free_views"),
          "agent", s.get("agent_ref"), "token", s.get("is_token"), "nft", s.get("is_nft"),
          "fns", s.get("fn_count"), s.get("error",""), flush=True)
print("S1:", out["s1_pass"], "S2:", out["s2_pass"], "EARLY:", out["early_shape"], flush=True)
