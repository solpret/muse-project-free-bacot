#!/usr/bin/env python3
import json, sys
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _single
from Crypto.Hash import keccak
EPS=["https://bsc-dataseed.binance.org/","https://bsc-dataseed1.bnbchain.org/","https://bsc-dataseed2.bnbchain.org/"]
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
def sel(sig):
    k=keccak.new(digest_bits=256); k.update(sig.encode()); return "0x"+k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64,"0")
def call(to,data):
    for ep in EPS:
        try: return _single(ep,"eth_call",[{"to":to,"data":data},"latest"],8,retries=0),None
        except Exception as e: err=str(e)[:120]
    return None,err
def dec_str(v):
    if not v or len(v)<130: return v
    try:
        ln=int(v[130:194],16); raw=bytes.fromhex(v[194:194+ln*2]); return raw.decode(errors="replace")
    except Exception as e: return f"<decode err {e}> {v[:80]}"
TARGETS={
 "SYMBOL":"0x993C822E7d9bBC75aa6b5095bD90a011Ff38cF71",
 "Unbroken":"0x4443EA727b0761De5ff91Ac5E9F5F65C5E3C8b8c",
 "TRACE":"0xe5E2c43746F3A5E713C246592095D7cf82E808Cc",
 "CastDeep":"0x37f8f181ab2f2b2D4209AA9c77c34d8E8566C360",
}
for n,a in TARGETS.items():
    v,_=call(a,sel("contractURI()"))
    print(n,"contractURI:",dec_str(v))
    v2,_=call(a,sel("name()"))
    print(n,"name:",dec_str(v2))
    v3,_=call(a,sel("symbol()"))
    print(n,"symbol:",dec_str(v3))
# DPEG extras
D="0xEc77268Fbb7e8b62D1dE8b913440d301c7B8CF55"
for fn,arg in [("firstMintTime()",""),("freeUsedByAgent(address)",enc(USER)),("quoteCost(uint256)","0"*63+"1"),("freeMinted()",""),("opened()","")]:
    v,e=call(D,sel(fn)+arg)
    try: iv=int(v,16) if v else None
    except Exception: iv=None
    print("DPEG",fn,iv,"err",e if v is None else "")
