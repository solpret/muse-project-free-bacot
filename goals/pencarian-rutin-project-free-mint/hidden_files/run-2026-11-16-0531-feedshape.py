#!/usr/bin/env python3
"""Feed shape-check run 2026-11-16 05:01 WIB: 4 newest Sourcify (top 21:31:24Z) + 7 retry-failed hot leg 0409. Read-only."""
import json, urllib.request, concurrent.futures
FREE_VIEWS = ["freeSharesRemaining","freeClaimed","freeFor","freeLeft","freeUsed","freeAvailable",
              "freeSharePoolExhausted","freeSharesClaimed","freeMinted","freeCardsRemaining"]
ADDRS = ['0xfc4061c0ec1BBd5afB3B813B9D214d4cc6d97fC9', '0xcd9CAD8d017164B85Aa82f5D5e0610f7C84da822', '0xa4943D2c855ae82b51D0C6949aA1ccA1046bdE64', '0x707863dFef1b9eccD07B45180b752470b52C784B', '0xCaf3251F998A5A7efC506d18CCA941C20ec7669E', '0x5af4ac1694485B1713993715D8bBAf20298dd52F', '0x29bfc1e3E3cEaBb844553044c0605ef97400d540', '0xA90d0B9001737Fa4Cb0bA4F73332Db9210909ff6', '0xA8181F0b7314C981622efA724B9299Af94f79603', '0xee6E134DabD09cB403Ad3Fe4e190bdfb6199a0b5']
def fetch(addr):
    url = f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "free-mint-search/0531"})
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
json.dump(out, open("run-2026-11-16-0531-feedshape.json","w"), indent=1)
print("S1_PASS:", [o["address"] for o in out if o.get("S1")])
print("S2_PASS:", [o["address"] for o in out if o.get("S2")])
