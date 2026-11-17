#!/usr/bin/env python3
"""Hot-leg 1019: on-chain shape probe for 18 new Sourcify feed contracts (read-only)."""
import json, urllib.request
from concurrent.futures import ThreadPoolExecutor
from Crypto.Hash import keccak
EPS=["https://bsc-dataseed.binance.org/","https://bsc-dataseed1.bnbchain.org/"]
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def call(to,data):
    p=json.dumps({"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":to,"data":data},"latest"]}).encode()
    for ep in EPS:
        try:
            req=urllib.request.Request(ep,data=p,headers={"Content-Type":"application/json"},method="POST")
            with urllib.request.urlopen(req,timeout=6) as r: v=json.load(r)["result"]
            return v if v and v!="0x" else None
        except Exception: continue
    return None
def iv(v):
    try: return int(v,16) if v else None
    except Exception: return None
def sv(v):
    try:
        if not v or len(v)<130: return None
        ln=int(v[66:130],16)
        return bytes.fromhex(v[130:130+ln*2]).decode(errors="replace")
    except Exception: return None
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"; u=USER[2:].lower().rjust(64,"0")
FEED=['0xdA010BbF925ceC1199342048dd5ec41dcFe042e7', '0xc88cdaf3cDf6CaE56326FDC594459e482f6b8cC7', '0x592941f758f2275789c2c6c355BDDc31BDb5eb26', '0xACe39a806c6F73789Ae72433E1FDFB90E0Cf9313', '0x2F1200108c34aA786c33Aa6F99E89E0342B028ed', '0x683b66D51f202401979969BF69C42a01fe07122E', '0x6a9fA5794BD5C94772A2d9ed155bAc8196c8D6ab', '0x1e32a2F84e1D37dDEEF8A3fd867E67719ae33Bd3', '0x01199ab5C2216673ce9cd56f42b0f4D829939820', '0x02b14f1355D7d1E19987d585fcAD343A9D2f3c85', '0xC1F0ed0B5eb08DE8DC4616806C42155b17b8cCE9', '0x4C9D25A2CA7a70369eC28d554Ad4bb9587ad4D59', '0xDc1710F7EA8b1c2581993ff857a0A4CE302CC009', '0x07F6339D2b6131a2aAbaF4A96273C1f6F89679e1', '0x23E170ea123b0de33336D446a252e663b7277777', '0x67F416a5ACb3735886fa655374d3a15Ac4aA49F1', '0xC894c0A54eaBA28cC5E2a3C6005706F83Daf934B', '0x539B8b1B3939D8a752Af5183910c99C291dBc01f', '0xac790d42Ce877680b1D0581A026396e7ce89C629', '0x4d6CF1957Bb94Ba641018709B602215b30651Fb3']
def probe(a):
    out={}
    out["name"]=sv(call(a,sel("name()")))
    out["symbol"]=sv(call(a,sel("symbol()")))
    out["decimals"]=iv(call(a,sel("decimals()")))
    out["totalSupply"]=iv(call(a,sel("totalSupply()")))
    for f in ["freeClaimed()","freeMinted()","FREE_SLOTS()","FREE_SUPPLY()","freeSharesRemaining()","freeClaimed(address)"]:
        arg=u if f.endswith("(address)") else ""
        out[f]=iv(call(a,sel(f)+arg))
    out["agentRegistry"]=call(a,sel("agentRegistry()"))
    out["registry"]=call(a,sel("registry()"))
    return out
with ThreadPoolExecutor(max_workers=18) as ex:
    res=list(ex.map(probe,FEED))
for a,o in zip(FEED,res): print(a,o,flush=True)
json.dump(dict(zip(FEED,res)),open("hot-leg-2026-11-04-1019-shape.json","w"),indent=1)
print("DONE")
