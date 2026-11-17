#!/usr/bin/env python3
"""Triage-2 run 0201: Coracle 0x2FCefA21..., Pixel Fox 0x9134ae94..., track-B binanceai re-check.
Read-only, curl transport 25s/call, progress flushed per view."""
import json, subprocess, time
from Crypto.Hash import keccak
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS=["https://bsc-dataseed1.bnbchain.org/","https://bsc-dataseed2.bnbchain.org/","https://bsc-dataseed.binance.org/"]
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64,"0")
def to_int(v):
    try:
        if v is None or v=="0x": return None
        return int(v,16)
    except Exception: return None
def post(ep,payload,timeout=25):
    out=subprocess.run(["curl","-sL","--max-time",str(timeout),"-X","POST",ep,"-H","Content-Type: application/json","-d",json.dumps(payload)],capture_output=True,text=True,timeout=timeout+5).stdout
    return json.loads(out)
def call(addr,sig,arg=None,raw=False):
    data=sel(sig)+(enc(arg) if arg else "")
    for ep in EPS:
        try:
            r=post(ep,{"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":addr,"data":data},"latest"]},timeout=25)
            if isinstance(r,dict) and "result" in r:
                return r["result"] if raw else to_int(r["result"])
            if isinstance(r,dict) and "error" in r: return "ERR:"+str(r["error"].get("message",""))[:60]
        except Exception: continue
    return None
def block():
    for ep in EPS:
        try:
            r=post(ep,{"jsonrpc":"2.0","id":1,"method":"eth_blockNumber","params":[]},timeout=25)
            return int(r["result"],16)
        except Exception: continue
    return None
def sourcify(addr):
    try:
        r=subprocess.run(["curl","-sL","--max-time","30",f"https://sourcify.dev/server/v2/contracts/56/{addr}"],capture_output=True,text=True,timeout=35).stdout
        sj=json.loads(r)
        abi=sj.get("abi") or (sj.get("stdJson") or {}).get("abi")
        fns=[f.get("name") for f in abi if isinstance(f,dict) and f.get("type")=="function"] if abi else None
        return {"match":sj.get("match"),"verifiedAt":sj.get("verifiedAt"),"fns":fns}
    except Exception as e:
        return {"error":repr(e)[:150]}
LEAN=["totalSupply()","totalMinted()","freeClaimed()","freeMinted()","FREE_SUPPLY()","MAX_SUPPLY()","mintOpen()","owner()","freeClaimed(address)","balanceOf(address)","mintedBy(address)","freeFor(address)","freeLeft()","freeUsed(address)","mintPrice()","PRICE()"]
out={"block":block()}
for name,addr in [("Coracle","0x2FCefA216dA37751E102399aCbe1dCC86Dc96eCf"),("PixelFox","0x9134ae94ab0739cf0e0f4f5e9cacfa5e1d029b0c")]:
    d={}
    for v in LEAN:
        arg=USER if "(address)" in v else None
        d[v]=call(addr,v,arg)
        print(f"{name} {v}={d[v]}",flush=True)
    d["contractURI_raw"]=str(call(addr,"contractURI()",raw=True))[:300]
    d["sourcify"]=sourcify(addr)
    if d["sourcify"].get("fns"):
        d["free_fns"]=[f for f in d["sourcify"]["fns"] if "free" in f.lower()]
        d["registry_fns"]=[f for f in d["sourcify"]["fns"] if "agent" in f.lower() or "registry" in f.lower()]
    out[name]=d
# binanceai track-B
MINT="0x46cb1D3efd4307506Cda7EbBa5a51be64746739E"; TOKEN="0x209173F09aFbCA053C0de9e9763f503e9fb54a3c"; PAIR="0x903ACC22B9BABCD427bfb9AF2C27a27a5aC7c698"
b={}
for v in ["launched()","failed()","isRefundPhase()","totalShares()"]:
    b[v]=call(MINT,v); print("binanceai",v,b[v],flush=True)
b["tokenClaimed_user"]=call(MINT,"tokenClaimed(address)",USER)
b["tokenBalance_user"]=call(TOKEN,"balanceOf(address)",USER)
b["pair_reserve0"]=call(PAIR,"getReserves()",raw=True)
print("binanceai claim/bal",b["tokenClaimed_user"],b["tokenBalance_user"],flush=True)
out["binanceai"]=b
out["block_end"]=block()
print(json.dumps(out,indent=1))
json.dump(out,open("run-2026-11-10-0201-triage2.json","w"),indent=1)
