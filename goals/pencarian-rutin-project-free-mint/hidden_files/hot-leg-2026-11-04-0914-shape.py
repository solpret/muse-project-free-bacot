#!/usr/bin/env python3
"""Hot-leg 0914: on-chain shape probe for 18 new Sourcify feed contracts (read-only)."""
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
FEED=['0x90361581D9Df642dEF496d1f64376a93A4932aFC', '0x53E7602E2CbAE677b3a4E56Fe7212e0E7D19A9be', '0xD047562bD12Eb459964551477903710A1d8E25eE', '0xCE648e11906D793DF647f0851f1Eac08dB687777', '0x2017Ab674C69EBB1EAA8Eb05bcD7a72Edac01630', '0x545A12090624C95fb96ef9a4cE9B60E58BE98ee9', '0xe0DEB1A792EeBD9cbA7Fd74B70A283Bfa2630771', '0xb07ce968eea65375DF54dc68BF9f16BB92a0E636', '0x5574bA84eCb30e561747C74a988a3962044fD691', '0xE6D3A485d82ac9BDbEF350c1158A568c5eFa371b', '0x3E25C4ceC8C43ADE9f0699a8E25C6734B315d31e', '0xb489c398aaC594318bD8c6CDFa84A3656a6D2180', '0x3e2fE9F2a406D6Ef7270ebB563350b70d6857777', '0xAEA9b066e3FC6F767BBb60f41C18E4239C6447E9', '0x731671b47236A2492bA673CdcD3d0351c61bCbc0', '0x6E6a298c669A8a01B65FFAbFD74aEa52F39Df9bC', '0x8D1151Be37c1Be46740768F0b8443CA59433a95E', '0xDF00Cb0086C88E0ae8a82F3F59c00dB5a28dAe0c']
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
json.dump(dict(zip(FEED,res)),open("hot-leg-2026-11-04-0914-shape.json","w"),indent=1)
print("DONE")
