#!/usr/bin/env python3
"""Hot-leg 0734: threaded RPC probes (read-only): shape for 20 new Sourcify feed contracts + re-read subset (copy of 0654 items)."""
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
def block():
    p=json.dumps({"jsonrpc":"2.0","id":1,"method":"eth_blockNumber","params":[]}).encode()
    for ep in EPS:
        try:
            req=urllib.request.Request(ep,data=p,headers={"Content-Type":"application/json"},method="POST")
            with urllib.request.urlopen(req,timeout=6) as r: return int(json.load(r)["result"],16)
        except Exception: continue
    return None
feed=['0x4E5bc7648579d7b69A2FC6749236D221A7aB79d7', '0x8eEc320ed004189EFf3532EB6254E89ab0240719', '0x9c5455dFbf6D09f235016DE7369fC885F42eca07', '0xf8fEA6D0D6901dD4005bfa5672193dDC53AB63Ef', '0xc8aC4D7eef09D3276cfa11C33b00A8D916360B8D', '0x782Be72C0137F7d9295ED50b282ca89df0B8C1F2', '0x2f7F514D2E2a72C98173FcAD70cd4B1CD2208Cda', '0x208a1173a3e39949a70b1338Bd855F60479D9882', '0x964EBCe23a238bc0ca2708537718E29b405c542a', '0x157351Ad781992Fc0F1aad03AF61cec6069Ad785', '0x768F7426Dd6f196a772F71a318072156D3c72c95', '0xa9163834f56570Ed1Cd0FaED6E304C74992D40D9', '0xbEAff86Ed5709E39eE7e33A98Ed68EB217685Cbf', '0x177973f574F8d1058d93F83cDBc0B2c247231935', '0xa09243C45D0D094e8B99243c0CaAc87B330C1f27', '0x688bcf2522cF300BCdA0867801784A1ef3350BC5', '0x157E85E1527b2d1c1188Cad9101Df5644beaf396', '0x1c0843625606d5d88a3f07158f222d78Fc787777', '0xd42898cEd7C5BF445Af3B9D75B5654d8Bac626C4', '0xB1e74d1DF19EB6bD2E36e610B69A16606660aeE2']
views=["totalSupply()","decimals()","freeClaimed()","freeMinted()","FREE_SUPPLY()","FREE_SLOTS()","freeSharesRemaining()","freeAvailable()"]
def probe(a):
    out={}
    for v in views: out[v]=iv(call(a,sel(v)))
    for fn in ("agentRegistry()","registry()"):
        raw=call(a,sel(fn)); out[fn]=("0x"+raw[-40:]) if raw and len(raw)>=42 else None
    return a,out
shape={}
with ThreadPoolExecutor(max_workers=20) as ex:
    for a,out in ex.map(probe,feed): shape[a]=out; print("SHAPE",a,out,flush=True)
json.dump({"shape":shape},open("hot-leg-2026-11-04-0734-feedshape.json","w"),indent=1)
print("DONE shape-only")
