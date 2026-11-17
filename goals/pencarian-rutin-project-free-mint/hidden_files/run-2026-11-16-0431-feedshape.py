#!/usr/bin/env python3
"""Feed shape-check run 2026-11-16 04:31 WIB: 4 newest Sourcify (top 21:31:24Z) + 7 retry-failed hot leg 0409. Read-only."""
import json, urllib.request, concurrent.futures
FREE_VIEWS = ["freeSharesRemaining","freeClaimed","freeFor","freeLeft","freeUsed","freeAvailable",
              "freeSharePoolExhausted","freeSharesClaimed","freeMinted","freeCardsRemaining"]
ADDRS = ['0x3e70260aeF959E8Ef06fbd16dD7d242C9f2b1c82','0x96F27bC154B717D116C29dA70705C395700A044b',
 '0xe375AF1906566493265dE5E94B0100D7Cba725b9','0x9Ef86C31aC03f4D91DB96FadEDAfAa9Be1919379',
 '0x140cC2b3cD7962FD3c7deB2Ef1EbBb1535df8790','0xF959566e6a503cf47FbBB488427ADe1d894C3488',
 '0x7c6da71826B8BB36a1d2bD295B9E96F6A6907e39','0x20D31f8727A0327c6aB889c37f97f273bf1423a6',
 '0xd0B25A98766C30A77734613C7b17b1b4eB145a77','0xEF084929164d10842635D2b29C8a6b421b0D521e',
 '0x139D318F2f0fFf4415288D932d47DaA72EA12457']
def fetch(addr):
    url = f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "free-mint-search/0431"})
        with urllib.request.urlopen(req, timeout=20) as r:
            meta = json.loads(r.read().decode())
        abi = meta.get("abi", [])
        names = {e["name"] for e in abi if e.get("type") == "function"}
        has_mint = any(n.lower().startswith("mint") for n in names)
        has_quote = bool(names & {"quote","cost","getQuote","mintCost","price","getPrice"})
        free_views = sorted(names & set(FREE_VIEWS))
        agent_ref = bool(names & {"agentId","agentRegistry","registry","getAgentId","agentGate","AgentGate"})
        s1 = has_mint and has_quote and bool(free_views) and agent_ref
        is_token = bool(names & {"name","symbol","decimals","totalSupply"})
        mintfree = "mintFree" in names
        s2 = is_token and mintfree and bool(names & {"freeClaimed","freeMinted"}) and bool(names & {"FREE_SLOTS","FREE_SUPPLY"}) and agent_ref
        return {"address": addr, "S1": s1, "S2": s2, "has_mint": has_mint, "has_quote": has_quote,
                "free_views": free_views, "agent_ref": agent_ref, "is_token": is_token, "n_fns": len(names)}
    except Exception as ex:
        return {"address": addr, "error": f"{type(ex).__name__}: {str(ex)[:150]}"}
with concurrent.futures.ThreadPoolExecutor(max_workers=11) as ex:
    out = list(ex.map(fetch, ADDRS))
for o in out: print(json.dumps(o))
json.dump(out, open("run-2026-11-16-0431-feedshape.json","w"), indent=1)
print("S1_PASS:", [o["address"] for o in out if o.get("S1")])
print("S2_PASS:", [o["address"] for o in out if o.get("S2")])
