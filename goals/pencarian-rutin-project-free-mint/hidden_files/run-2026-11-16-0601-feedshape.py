#!/usr/bin/env python3
"""Feed shape-check run 2026-11-16 06:01 WIB: 4 newest Sourcify (top 21:31:24Z) + 7 retry-failed hot leg 0409. Read-only."""
import json, urllib.request, concurrent.futures
FREE_VIEWS = ["freeSharesRemaining","freeClaimed","freeFor","freeLeft","freeUsed","freeAvailable",
              "freeSharePoolExhausted","freeSharesClaimed","freeMinted","freeCardsRemaining"]
ADDRS = ['0x9d57bF127C0eB502c0bDee8110Fa1505c3c277A7', '0x1b8894391a3DcFe7e248C321103265AB52E273e0', '0xdb7A8fa53F96cf4744c21BB6c78a2272ec6566e5', '0xcD327d73900916c6Dd7029421779D0F170BCD794', '0x8A24C9316D1764111a3FeBb760E4e263035A2082', '0x2F44E2ED12d263D1C68D48B9679EeaA0d425198F', '0x0469bB805b193BA1DEb554A0788D935c083C7702', '0x428eBbfC3Db7FAc67BFb23736fafdB6293f48690', '0x4374554C518cB6a54Cf6f45A6584755728f1477A', '0x30836C4d172f5fB4467D682ffD834589B83e013B']
def fetch(addr):
    url = f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "free-mint-search/0601"})
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
json.dump(out, open("run-2026-11-16-0601-feedshape.json","w"), indent=1)
print("S1_PASS:", [o["address"] for o in out if o.get("S1")])
print("S2_PASS:", [o["address"] for o in out if o.get("S2")])
