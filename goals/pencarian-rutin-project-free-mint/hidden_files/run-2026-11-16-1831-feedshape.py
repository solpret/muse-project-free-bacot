#!/usr/bin/env python3
"""Sourcify feed shape-check run 1831: 4 contracts new vs hot-leg 1819 (verifiedAt 11:25-11:34Z)."""
import json, subprocess, urllib.request
NEW = ["0xE94E87715907C9ba3eA8055940E51bB93Deb9547","0x4B7E5b27220a64f21cC21F0DAD578967deEb4fE0","0x4B658456730Fd25450E40b7832221aEB3808c86B","0xb7160939593028032302a446c716bC6Fdf763742"]
FREE_VIEWS = ["freeSharesRemaining","freeClaimed","freeFor","freeLeft","freeUsed","freeAvailable","freeSharePoolExhausted","freeSharesClaimed","freeMinted","freeMintedBy"]
REG = "60b9262456de011f7d15a54cdd8c48baaa8b022f"
def get_abi(addr):
    for attempt in range(3):
        try:
            with urllib.request.urlopen(f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=stdJson", timeout=45) as r:
                d=json.load(r)
            sj=d.get("stdJson",{})
            srcs=sj.get("sources",{})
            out=[]
            for s in srcs.values():
                out.append(s.get("content",""))
            abi=None
            # try metadata
            meta=d.get("metadata",{})
            abi=meta.get("abi") or meta.get("output",{}).get("abi")
            return abi, "\n".join(out)
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
json.dump(res, open("run-2026-11-16-1831-feedshape.json","w"), indent=1)
print("DONE")
