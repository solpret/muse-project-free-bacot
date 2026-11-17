#!/usr/bin/env python3
"""Sourcify feed shape-check run 2301: 4 contracts new vs run 1831 (verifiedAt 11:25-11:34Z)."""
import json, subprocess, urllib.request
NEW = json.load(open("run-2026-11-16-2301-feedshape-new.json"))
FREE_VIEWS = ["freeSharesRemaining","freeClaimed","freeFor","freeLeft","freeUsed","freeAvailable","freeSharePoolExhausted","freeSharesClaimed","freeMinted","freeMintedBy"]
REG = "60b9262456de011f7d15a54cdd8c48baaa8b022f"
def get_abi(addr):
    for attempt in range(3):
        try:
            with urllib.request.urlopen(f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=metadata,abi", timeout=45) as r:
                d=json.load(r)
            abi=d.get("abi") or d.get("metadata",{}).get("output",{}).get("abi")
            # registry-bytes check via on-chain bytecode (stdJson dropped by Sourcify 2026-11-16)
            code=""
            try:
                import urllib.request as _u
                payload=json.dumps({"jsonrpc":"2.0","id":1,"method":"eth_getCode","params":[addr,"latest"]}).encode()
                req=_u.Request("https://bsc-dataseed.binance.org/", data=payload, headers={"Content-Type":"application/json"})
                with _u.urlopen(req, timeout=30) as r2:
                    code=json.load(r2).get("result","") or ""
            except Exception:
                code=""
            return abi, code
        except Exception as e:
            print(addr, "attempt", attempt, "err", str(e)[:80], flush=True)
    return None, ""
res={}
for a in NEW:
    abi, src = get_abi(a)
    if not abi:
        res[a]={"shape":"abi-unavailable"}; print(a,"ABI UNAVAILABLE"); continue
    names=[f.get("name","") for f in abi if f.get("type")=="function"]
    has_mint=any(n.startswith("mint") for n in names)
    has_quote=any("quote" in n.lower() or "cost" in n.lower() or "price" in n.lower() for n in names)
    free_views=[n for n in names if n in FREE_VIEWS]
    src_low=src.lower()
    has_reg=REG in src_low or any("agentidregistry" in n.lower() or "agentgate" in n.lower() for n in names)
    is_token=all(x in names for x in ["name","symbol","decimals","totalSupply"])
    has_mintfree="mintFree" in names
    s1 = has_mint and has_quote and bool(free_views) and has_reg
    s2 = is_token and has_mintfree and bool(free_views) and has_reg
    print(a, "fns=",len(names), "mint=",has_mint,"quote=",has_quote,"free_views=",free_views,"reg=",has_reg,"token=",is_token,"mintFree=",has_mintfree,"=> S1" if s1 else ("=> S2" if s2 else "=> NOT-SALE-SHAPE"))
    res[a]={"shape":"S1" if s1 else ("S2" if s2 else "checked-not-sale-shape"),"fns":len(names),"mint":has_mint,"quote":has_quote,"free_views":free_views,"registry":has_reg,"token":is_token,"mintFree":has_mintfree}
json.dump(res, open("run-2026-11-16-2301-feedshape.json","w"), indent=1)
print("DONE")
