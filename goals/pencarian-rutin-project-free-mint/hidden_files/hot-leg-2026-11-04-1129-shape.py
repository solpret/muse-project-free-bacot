#!/usr/bin/env python3
"""Hot-leg 1129: on-chain shape probe for 20 new Sourcify feed contracts (read-only)."""
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
FEED=['0x18EfB091189c0Fd8c05406bBD52ad9cF1Fb187f2', '0x39ea46A521FA125E7811174C6EEE45Ad6e89704f', '0x597542e6dd54E84Cc0dFA50C84049877E851e1a7', '0xA96006818F7B72B97593323c77359f579adBF4c7', '0x4DE64D5A500d121186dDc8c472fE52604b8A0901', '0xD09904317d7Ad3661AEF482b59BE77C5fDe1D073', '0xC8B7a5f44B8DB4e16a589C4CbFF71da6bD237B23', '0x5f24B3d4F4FCc41829633d208736605A130097f7', '0x7DD0BDE3767810B80E7A8aAD3cEc3c4Be1EA6509', '0x2d07d9d4FD330d84c851DA3EF1aA4b10755Cc6e2', '0x3b2D485F1fe26Fe448A84Fd00Bd05083964bD980', '0x558713F9192CB7494B13e17D72A52E5a3096125D', '0xD63e09c71FB6365e94c3394049bf9D416aCc9764', '0x3Cf5bF646E4428be0c6d7b143127b452b8cDD82A', '0xE399FEE19258E6dDB012eC806877aC102eda7777', '0x7b95409486787636f2576781a28bB6aD38FC1638', '0xBF8B86EE256c9D1616f2432294433b161FB22305', '0x2A95D54aF80600042E0DB3a971E55F39B04C5802', '0xC02754d030c0ABDD54838Dbd797298BaD82FB30e', '0xF8e43c4d7fdFD52E96457cd53ad71BbA62A1B6F2']
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
with ThreadPoolExecutor(max_workers=20) as ex:
    res=list(ex.map(probe,FEED))
for a,o in zip(FEED,res): print(a,o,flush=True)
json.dump(dict(zip(FEED,res)),open("hot-leg-2026-11-04-1129-shape.json","w"),indent=1)
print("DONE")
