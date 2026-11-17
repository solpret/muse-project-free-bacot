#!/usr/bin/env python3
"""Feed shape-check run 2026-11-16 07:01 WIB: 4 newest Sourcify (top 23:33:56Z) + 7 retry-failed hot leg 0409. Read-only."""
import json, urllib.request, concurrent.futures
FREE_VIEWS = ["freeSharesRemaining","freeClaimed","freeFor","freeLeft","freeUsed","freeAvailable",
              "freeSharePoolExhausted","freeSharesClaimed","freeMinted","freeCardsRemaining"]
ADDRS = ['0x6A8ba31ffC9b45C0dAc24696B481a87F6Cba837E', '0x6C27fB16BAE5C14B9466BB32Ea573B4F306098cb', '0x5B8aCc3B13dB75e1578AeeEaE1D2D6fBdb096C80', '0x4587C52427A8B9aC410A22d801dE4AB168580659', '0x582412E0d428fe4f300765206FDfb6D1ed757316', '0xc3b87be1d4ed2fa7BF2f2DcDb9a88f3fD4aE8448', '0xD45CeB305e0aEC1AA5eF190c72C13416370826c9', '0x313f3a38ECE6c793bD6807f90D80Bb3f16958938', '0x51B4576744Ee349ecc61ca9380a40CDe62210535', '0x5934E86c5429020F26b87Af2C9235EF366911475']
def fetch(addr):
    url = f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "free-mint-search/0731"})
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
json.dump(out, open("run-2026-11-16-0731-feedshape.json","w"), indent=1)
print("S1_PASS:", [o["address"] for o in out if o.get("S1")])
print("S2_PASS:", [o["address"] for o in out if o.get("S2")])
