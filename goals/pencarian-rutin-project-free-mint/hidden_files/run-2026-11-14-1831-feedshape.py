#!/usr/bin/env python3
"""Feed shape-check run 2026-11-14 18:31 WIB: 7 Sourcify contracts new vs run 1801. Read-only."""
import json, urllib.request, concurrent.futures
FREE_VIEWS = ["freeSharesRemaining","freeClaimed","freeFor","freeLeft","freeUsed","freeAvailable",
              "freeSharePoolExhausted","freeSharesClaimed","freeMinted","freeCardsRemaining"]
ADDRS = ["0xbDcaBF218A54ae484a9F8C6edb202C8939b6EDA5","0x153De4d87E22B29bC78c4365f4340a9E6bE720d8",
         "0x15927990f7167478aadc4E11CAf8762d21AAA8F1","0x024899bD1C82b89Da3C52E108beB19A2CC27B378",
         "0x7ED704a0E28523bdc06198d41d831086E5c42a6F","0x8A25a5929A18c132EAf47a2b497c86aD00eA5b9e",
         "0x0bfeB5c0cBd65A707E1c2b271cF206B9729f0E5d"]
def fetch(addr):
    url = f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "free-mint-search/1831"})
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
with concurrent.futures.ThreadPoolExecutor(max_workers=7) as ex:
    out = list(ex.map(fetch, ADDRS))
for o in out: print(json.dumps(o))
json.dump(out, open("run-2026-11-14-1831-feedshape.json","w"), indent=1)
print("S1_PASS:", [o["address"] for o in out if o.get("S1")])
print("S2_PASS:", [o["address"] for o in out if o.get("S2")])
