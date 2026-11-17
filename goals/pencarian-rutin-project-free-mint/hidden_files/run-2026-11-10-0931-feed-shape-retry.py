#!/usr/bin/env python3
"""Retry 5 timed-out Sourcify ABIs, sequential, 60s timeout. Read-only."""
import json, urllib.request, time
FEED = ["0x94F8F6F4Da3Dfd0549DE5c3422A4FfB41Aba673e","0x136AC70EE85529ef961ccC7076de77e4e929D6dF","0x09e664F447D854b0C413f63E4D6e78070B411AeB","0x4F8cbCD1F336D873CAEC5e479ecc689624107037","0xC828186ea59599048c27B23D564eCb6A3e5Bf142"]
FREE_VIEWS = ["freeSharesRemaining","freeClaimed","freeFor","freeLeft","freeUsed","freeAvailable",
              "freeSharePoolExhausted","freeSharesClaimed","freeMinted","freeCardsRemaining"]
def fetch(addr):
    url = f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi"
    try:
        req = urllib.request.Request(url, headers={"User-Agent":"free-bacot/0931-retry"})
        with urllib.request.urlopen(req, timeout=60) as r:
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
        return {"address": addr, "functions": sorted(names), "S1": s1, "S2": s2,
                "has_mint": has_mint, "has_quote": has_quote, "free_views": free_views,
                "agent_ref": agent_ref, "is_token": is_token}
    except Exception as ex:
        return {"address": addr, "error": f"{type(ex).__name__}: {str(ex)[:150]}"}
out=[]
for a in FEED:
    o=fetch(a); out.append(o); print(json.dumps(o), flush=True); time.sleep(2)
json.dump(out, open("run-2026-11-10-0931-feed-shape-retry.json","w"), indent=1)
print("S1_PASS:", [o["address"] for o in out if o.get("S1")])
print("S2_PASS:", [o["address"] for o in out if o.get("S2")])
print("ERRORS:", [(o["address"], o.get("error")) for o in out if o.get("error")])
