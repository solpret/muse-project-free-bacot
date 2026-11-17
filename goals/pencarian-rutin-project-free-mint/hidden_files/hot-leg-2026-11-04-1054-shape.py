#!/usr/bin/env python3
"""Hot-leg 1054: on-chain shape probe for 18 new Sourcify feed contracts (read-only)."""
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
FEED=['0xe5FaF4A1f2541D29bEB3AA8B46C7CE13197A2694','0x185329b0F1cDA4F0ab78457257f9fab36D38D30D','0xc9b564f88Ef9F4762CC93b4D60C1106D8E9e640E','0xec4Ca5667bB425AD3055AAcbA13DAbb315B35677','0x06a05A1A3E799bcBa392F407fe7F391286C9d6ea','0x461b5625eeb3262b4849b3d17dbF6a40b7a08460','0xbCAF27e93aDa604fd0cF27643925cD1e5137edD8','0x9B17c3a9B4F62C362315ff558b57064722034af4','0x1bC5198802CaD2e3C53F6f7c37c23A1825397777','0x119032B1f266CCd20ec7B6d6904CC1a0A154917b','0x69f87a4bE1245B832142fdF3a2cB553de5fD36Bf','0x9315410d7F77737A942cA8C7Bd7C49661ab5734E','0xDc5dBFe3Eb46672CEE5B6A08E9BaEC173F870aa6','0x88221Aadce4f4720cC17Bae34a43aF23f7B2334d','0x6cde6F2e48D44e180f1aE16eec8a38fCeDA8a91F','0x17b9f124F58674C31a6245dF41178544bA6E3A24','0xB4F8B5B90DEBa70a06563A6b9fcb486bB2c05555','0x1Fd48A6805F60994f7CDD9e2B83521e735457401','0x90dED7616D094A27A20Cc669f9C5867062435B7F','0xeA24Bf86Dab8329FC9cD1905c320a3F80ebAd86C']
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
json.dump(dict(zip(FEED,res)),open("hot-leg-2026-11-04-1054-shape.json","w"),indent=1)
print("DONE")
