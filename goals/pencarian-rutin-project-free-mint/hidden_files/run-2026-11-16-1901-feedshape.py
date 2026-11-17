#!/usr/bin/env python3
"""Sourcify feed shape-check run 1901: 4 contracts new vs run 1831 (verifiedAt 11:25-11:34Z)."""
import json, subprocess, urllib.request
NEW = ["0xB30FAf20E96ec78eD7838cAC50e1333967CFBEC3","0x0C3e53Ba52566Dd00aE4bF7fB678547f45C78641","0x628Ef0215294A3B4600C34BB02f368e6733a3C91","0x785A96238A12268CBfcfB0dbD514cD2d3D82387C","0x41776Fe083239771798234B30DA0f6f1FD193ebf","0xC91867D7C614e69829e6e9f833Cc48C4B4c85A7B","0x72251b0682BD557C85eD85cd1Ad38bbC69A3be03","0xfF39D877d617eeaf7C5c8b5CC4303cfC6F383e03","0x98A63777f00e5e9b6B41d1EF013b1f1Bffd23270","0x177a452C28311CdEC485A06b6bd6Dbd9b14643c5","0x2D47a77A141e8D831Ee0F74a6A502b29094Ba942","0x548F6cb7EC4306e60918B89cE884bA06A7D2dB4C","0x2D3959bCbca7883d853E549afDD95FfCc3f3F220","0xA115d8CEE467eCEb8b9B3EFb66e5CA462CD21cA5"]
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
json.dump(res, open("run-2026-11-16-1901-feedshape.json","w"), indent=1)
print("DONE")
