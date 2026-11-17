#!/usr/bin/env python3
"""Sourcify feed shape-check run 2031: 4 contracts new vs run 1831 (verifiedAt 11:25-11:34Z)."""
import json, subprocess, urllib.request
NEW = ["0xBE31230214eA61A2070510c5d96D1fC279D22488", "0x2C9215a811ef9EEF59921D93625091874C21AbB4", "0xe4C882280c8252b1aDA9f7148c3e29f7589ebeD0", "0x70E90F5696e0d3C9730eEA2811E7f586751295E5", "0x4f80469f780f65b28809d705f131e916e9e3F6EA", "0x19c7F7F7a97cc3292C0425089393aB7258C6eaEC", "0xC4f2919fF39d1ec146d719E6758C0a1bD23D46e4", "0xbf9601022A2E866BE482829Fe48C11016245DC10", "0x6c24F3DF78A924C9c0A5025a7eE1F267BB7351C3", "0x0Fa0c41bB219612dB424Ae425d438A9e3e85A118", "0x89a5e105878E8317818fdc7893C94745278C1CfC", "0x776219617783e6A2aDd8A3373A0e9Db9b31E4358", "0x4F7d3Bf14b114f4B5650734d9DC24FB7635956eA", "0x05b02A9FD0b4F58bF013b4137D84593E7a0e6546", "0xf1afF8A2137582350122952e3c279EF71A32b556", "0x284E6a23d50d951A9Bfb1794585809c1600CFEF8", "0xa05136Fa248CAA6603977085C477Aa4EB8dFeDeE", "0x182bcB5c1E1611db8c83eDe75C7E518eACEad2A2", "0x458E735F2B2c55aCB35Eb01e0f2C0BBC88f4c726", "0x8d2B451C20A70F1D89f7781a233c25D6F04Ac670"]
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
json.dump(res, open("run-2026-11-16-2031-feedshape.json","w"), indent=1)
print("DONE")
