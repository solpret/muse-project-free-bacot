#!/usr/bin/env python3
"""Feed shape-check run 2026-11-14 18:31 WIB: 7 Sourcify contracts new vs run 1831. Read-only."""
import json, urllib.request, concurrent.futures
FREE_VIEWS = ["freeSharesRemaining","freeClaimed","freeFor","freeLeft","freeUsed","freeAvailable",
              "freeSharePoolExhausted","freeSharesClaimed","freeMinted","freeCardsRemaining"]
ADDRS = ['0xAFE2aa712bb4187f00EdCD333C50f6D92772AA1c', '0xbbD1F94a435598309E1e8261c5ECEd5932E6a2ae', '0xA4C66c5e87059CB560758bB7cE87f1737cC79Cce', '0xF423486D0B021E457c0132b3144728DEa105f028', '0x651a15460F62dF9d9B77ea0324fc948F6b94b5fA', '0x0126652bFCfEcfE7E9638a413d41D528bcc56420', '0xfDFe4113D8dFC4a580b48767d63A9D780CAd3638', '0x0E7487C42b636C2dc691f9B37359888908ecDc97', '0x67144992ce6d0948ff183968D0fCD11773A4E153']
def fetch(addr):
    url = f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "free-mint-search/1901"})
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
with concurrent.futures.ThreadPoolExecutor(max_workers=9) as ex:
    out = list(ex.map(fetch, ADDRS))
for o in out: print(json.dumps(o))
json.dump(out, open("run-2026-11-14-1901-feedshape.json","w"), indent=1)
print("S1_PASS:", [o["address"] for o in out if o.get("S1")])
print("S2_PASS:", [o["address"] for o in out if o.get("S2")])
