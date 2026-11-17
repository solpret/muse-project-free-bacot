#!/usr/bin/env python3
"""Hot-leg 1149: on-chain shape probe for 20 new Sourcify feed contracts (read-only)."""
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
FEED=['0x854396f212B36e0f17176297deEc9a6084f5F06b', '0xcbDa33B2737D8085e30FF1468cd9fcAe46501d3E', '0xE9e1fad4b2D43a7620c1C2CA588F174710000000', '0x22DB4e218Fd7D21ec51291564a2D32EAe0FBC313']
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
json.dump(dict(zip(FEED,res)),open("hot-leg-2026-11-04-1149-shape.json","w"),indent=1)
print("DONE")
