#!/usr/bin/env python3
"""Hot-leg 0914: sequential shape-check of 7 new Sourcify feed contracts."""
import json, time, urllib.request
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
FREE_VIEWS = ["freeSharesRemaining", "freeClaimed", "freeFor", "freeLeft", "freeUsed",
              "freeAvailable", "freeSharePoolExhausted", "freeSharesClaimed",
              "freeMinted", "freeCardsRemaining"]
REGISTRY = "0x60b9262456de011f7d15a54cdd8c48baaa8b022f"
addrs = ["0xD3E2c70B7d1C4da8Ef21046dF27050F17Da94fA9","0x0728781C25027845be6Bf73F82c347a7821F9a01",
"0x190D21eC62B71A5C3e08c6179b1b7a68eAbcC54E","0x1203D08F14370bd8E046C1b8AabA7fB718aB3278",
"0x5e362c702A7f69b7BBC66588B684c6f1126bf0B0","0x03Fe20Ec986c2E558B37825D9860Fd9a161f5c68",
"0xdef5061B688bB16Fe8336EEbaA44c672Cdd8A7A2"]
def fetch_abi(addr):
    url = f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "free-bacot/1.0"})
        with urllib.request.urlopen(req, timeout=30) as r:
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
        is_nft = bool(names & {"tokenURI", "ownerOf", "safeTransferFrom"}) or "uri" in names
        free_mint_fn = bool(names & {"freeMint", "mintFree", "claimFree", "mint"}) or any(n.lower().startswith("freemint") for n in names)
        early_shape = is_nft and (agent_ref or free_mint_fn)
        return {"address": addr, "S1": s1, "S2": s2, "early_shape": early_shape,
                "has_mint": has_mint, "has_quote": has_quote, "free_views": free_views,
                "agent_ref": agent_ref, "is_token": is_token, "is_nft": is_nft,
                "fn_count": len(names), "fns": sorted(names)[:60]}
    except Exception as ex:
        return {"address": addr, "error": f"{type(ex).__name__}: {str(ex)[:120]}"}
t0=time.time(); out=[]
for a in addrs:
    r=fetch_abi(a); out.append(r)
    print(a, "S1" if r.get("S1") else "-", "S2" if r.get("S2") else "-", "EARLY" if r.get("early_shape") else "-",
          r.get("error", f"fns={r.get('fn_count')} free={r.get('free_views')} agent={r.get('agent_ref')} nft={r.get('is_nft')}"))
    time.sleep(1)
json.dump({"started_wib":"2026-11-11 09:14 WIB","elapsed_s":round(time.time()-t0,1),
 "s1_pass":[s["address"] for s in out if s.get("S1")],"s2_pass":[s["address"] for s in out if s.get("S2")],
 "early_shape":[s["address"] for s in out if s.get("early_shape")],"shapes":out},
 open(BASE+"hot-leg-2026-11-11-0914-shape.json","w"),indent=1)
print(f"DONE {len(out)} in {time.time()-t0:.1f}s")
