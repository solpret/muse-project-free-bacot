#!/usr/bin/env python3
"""Hot-leg 0944: on-chain shape probe for 18 new Sourcify feed contracts (read-only)."""
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
FEED=['0xB3617e96Ab2005AF2BC33Cc4D1665BA5A2A9a956', '0xebe345A90E680A925B58d75ADFa2978A95087777', '0x81f6e0f00b9e2aA038d2AFE58929A595D10E182e', '0xF814948D87b72491B781B90f7aC8B6F895D03133', '0x698C25084bE9930dD7bcCBbfad8C88c8f8362927', '0x90a6311E286415E93B8Ab9518B2967497A24e8a0', '0x4613297D064384668e87bDfa87d558391d0f6B77', '0x4793e78550484AF4D84510F00D3e321440c5Ab85', '0x50B0052cc11911654939b0cC4515160009493e2d', '0x3d707902946f0aF79C6Df898945Bba3B6729F8e0', '0x8b768a897c8B0097f6BfF5729D73C0ab123Eaa57', '0xB78c5A470ba8a37CD6F533485aCfFa4b9Cf14B59', '0x6B1BeB07D6cbd0A72cD904962AE6EaE261770A0f', '0x4587aBb377E95d69b86a44d3eFf4BFeB430A7777', '0x7fBaE4001E8d85883B4781d114076f8179389C43', '0xa6Ca72004777FE6452c98cd658734E58f85C5a90', '0xFA75C8314ef2f7a7d96B69d09919c62E716810af', '0x1A93C0E0E922876166615D9cB33e682AEC8c650A']
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
json.dump(dict(zip(FEED,res)),open("hot-leg-2026-11-04-0944-shape.json","w"),indent=1)
print("DONE")
