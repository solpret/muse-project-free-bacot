#!/usr/bin/env python3
"""Hot-leg Sourcify shape-check (S1/S2), read-only. Run 2026-11-10 05:09 WIB.
Feed: 9 contracts newly verified since the 05:04 run (verifiedAt 22:05:18-22:10:15Z)."""
import json, urllib.request, concurrent.futures
FEED = ["0xf8bc135614bcA7B1dC9A24b1CDD2C1593534D948","0x6939797A69f3f08D49DC7E52280db17511711B84",
"0xc5aCb349f6c9cC28bf0EF5C9f3d9D2c5561dcb94","0x799B6cCdB18fCB0E56c49A0d114196D8cD92d1A6",
"0x1528abC57482eC65561dd637EDE2812Bb641aBCA","0x89E34D81E4b507331a2A69d6C548317EEa5440F2",
"0x1492022b0a6BF17aB1CDc78ed80A8AB63fE8f5A4","0x81Eb79A56d140416aA2A65972D5001630Be276e0",
"0x8B55D1be2b6f09A006f866b4A47707dE7196F6ea"]
FREE_VIEWS = ["freeSharesRemaining","freeClaimed","freeFor","freeLeft","freeUsed","freeAvailable",
              "freeSharePoolExhausted","freeSharesClaimed","freeMinted","freeCardsRemaining"]
def fetch(addr):
    url = f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi"
    try:
        req = urllib.request.Request(url, headers={"User-Agent":"hot-leg/1.0"})
        with urllib.request.urlopen(req, timeout=15) as r:
            meta = json.loads(r.read().decode())
        abi = meta.get("abi", [])
        fns = {}
        for e in abi:
            if e.get("type") == "function":
                fns.setdefault(e["name"], []).append(e)
        names = set(fns)
        has_mint = any(n.lower().startswith("mint") for n in names)
        has_quote = bool(names & {"quote","cost","getQuote","mintCost","price","getPrice"})
        free_views = sorted(names & set(FREE_VIEWS))
        agent_ref = bool(names & {"agentId","agentRegistry","registry","getAgentId","agentGate","AgentGate"})
        s1 = has_mint and has_quote and bool(free_views) and agent_ref
        is_token = bool(names & {"name","symbol","decimals","totalSupply"})
        mintfree = "mintFree" in fns and any(len(e.get("inputs",[]))==0 for e in fns["mintFree"])
        s2 = is_token and mintfree and bool(names & {"freeClaimed","freeMinted"}) and bool(names & {"FREE_SLOTS","FREE_SUPPLY"}) and agent_ref
        return {"address": addr, "functions": sorted(names),
                "S1": s1, "S2": s2, "has_mint": has_mint, "has_quote": has_quote,
                "free_views": free_views, "agent_ref": agent_ref, "is_token": is_token}
    except Exception as ex:
        return {"address": addr, "error": f"{type(ex).__name__}: {str(ex)[:120]}"}
with concurrent.futures.ThreadPoolExecutor(max_workers=9) as ex:
    out = list(ex.map(fetch, FEED))
for o in out:
    print(json.dumps(o))
json.dump(out, open("/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/hot-leg-2026-11-10-0509-sourcify.json","w"), indent=1)
print("S1_PASS:", [o["address"] for o in out if o.get("S1")])
print("S2_PASS:", [o["address"] for o in out if o.get("S2")])
