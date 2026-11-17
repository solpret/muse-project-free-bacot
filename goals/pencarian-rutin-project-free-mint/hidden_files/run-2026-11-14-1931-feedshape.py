#!/usr/bin/env python3
"""Feed shape-check run 2026-11-14 19:31 WIB: 16 Sourcify contracts new vs run 1831. Read-only."""
import json, urllib.request, concurrent.futures
FREE_VIEWS = ["freeSharesRemaining","freeClaimed","freeFor","freeLeft","freeUsed","freeAvailable",
              "freeSharePoolExhausted","freeSharesClaimed","freeMinted","freeCardsRemaining"]
ADDRS = ['0xFdb394bc545c858Cca4FC86ed7C0fdd77A8871E9', '0x28A101efb094b50E97679136FC0B21eD3787C4f0', '0x24d274bE1aC504bd35537D1Cc13AD7Dc1c4a97B4', '0x660Ebde3D72DBf44919C5E7C89d6B376b4E98888', '0xD2576E52Fce75950b4267a1F2E2934664363D590', '0xB8b7eF8D49981F8987Dfc271DCa50E24ce87AbEb', '0x1D02c90d14e68a7Bc7a19f29466Bd76b5EE2332a', '0xe5f1367d3B47B4Adc27c3279A50992a8C4dc2453', '0xd583a4440f487E20540adA4A2774a12A1bCF1635', '0xBCD34515d3d3A67069404d063edf189FaFD66Cc7', '0x970570A711eD5A0d42A5A883579cb2eB8755DCe3', '0x6Ab5680426cF4b45E4c666702aA6fB5C33AAa659', '0xbdE91D62f433bE364940A89d8d151cd408ADeD67', '0x625f168F2f48F4D3e742c2E722131248A270400d', '0xD3c4781D263794A4973D1e4036A696714D4EB926', '0x88a48aeE3c327a30Fc75BD4C5eED1a3FB52FEf9D']
def fetch(addr):
    url = f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "free-mint-search/1931"})
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
with concurrent.futures.ThreadPoolExecutor(max_workers=16) as ex:
    out = list(ex.map(fetch, ADDRS))
for o in out: print(json.dumps(o))
json.dump(out, open("run-2026-11-14-1931-feedshape.json","w"), indent=1)
print("S1_PASS:", [o["address"] for o in out if o.get("S1")])
print("S2_PASS:", [o["address"] for o in out if o.get("S2")])
