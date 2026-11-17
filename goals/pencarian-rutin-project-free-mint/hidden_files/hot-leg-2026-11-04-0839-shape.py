#!/usr/bin/env python3
"""Hot-leg 0839: on-chain shape probe for 18 new Sourcify feed contracts (read-only)."""
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
FEED=["0x0d2CEc06cf73395404A9B87A5B23f4eE417ea90A","0x5DB4ea0Cb6E9B3109a09B9bBd5F35759167bEAeD","0xDE899991614529B2a63263809EFC4283EC682eE1","0xb0991558cbE0F31Bbfe6AeD9a39DaCe41aEA7f3B","0xbeB15f0d3472294B6A8C8D47CD05aE4AA57eE6B0","0x6ef09E4d535D8ec7897099789B35e3A4694d3541","0xc6A26eADD8f704A8851eeA7a14AeD1A39e1EFAd9","0x7483702c229151FBd80966Be1Df1aF67EeC426Ea","0xe71504018FF8260b43C98C64decB30E71ECf34eB","0xbE9d49e50E3D000c09262f4F5d99DB728Ad0A7F9","0x2014EDe1ba0094cf1788fEa32ACA2Aa606F8d908","0x784b551dA020A29416b54575Cde87A207A272DB3","0x4f63E878df8a8D5EAa99FD8BcEFA44f17b887777","0x7B1CC478deC30a14214a462e0e2f1DE1DC6A831a","0xfb60228E81F43d1fb8C255558a44669090ddF763","0xEAf930a21148e3B4456B5E8F24435F90f7C04905","0xC1CEbE1dE66Efdd0b415e5fbb5462469BB1b86ba","0xfc91976BE5B1f76A0513103c33e553d134Fc6De5"]
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
json.dump(dict(zip(FEED,res)),open("hot-leg-2026-11-04-0839-shape.json","w"),indent=1)
print("DONE")
