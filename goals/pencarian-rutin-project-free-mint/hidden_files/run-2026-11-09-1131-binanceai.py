#!/usr/bin/env python3
"""Track-B binanceai.fun re-check run 1131 — curl transport, read-only."""
import json, subprocess
from Crypto.Hash import keccak
MINT="0x46cb1D3efd4307506Cda7EbBa5a51be64746739E"
TOKEN="0x209173F09aFbCA053C0de9e9763f503e9fb54a3c"
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS=["https://bsc-dataseed1.bnbchain.org/","https://bsc-dataseed2.bnbchain.org/"]
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64,"0")
def to_int(v):
    try: return int(v,16) if v not in (None,"0x") else None
    except Exception: return None
def post(ep,payload,timeout=25):
    out=subprocess.run(["curl","-sL","--max-time",str(timeout),"-X","POST",ep,"-H","Content-Type: application/json","-d",json.dumps(payload)],capture_output=True,text=True,timeout=timeout+5).stdout
    return json.loads(out)
def batch(addr,views):
    calls=[];keys=[]
    for i,sig in enumerate(views):
        base=sig.split("(")[0]
        if "(address)" in sig: data=sel(sig)+enc(USER); key=base+"_user"
        else: data=sel(sig); key=base
        calls.append({"jsonrpc":"2.0","id":i+1,"method":"eth_call","params":[{"to":addr,"data":data},"latest"]}); keys.append(key)
    for ep in EPS:
        try:
            res=post(ep,calls)
            if not isinstance(res,list) or len(res)!=len(calls): continue
            return {k:(None if (isinstance(it,dict) and "error" in it) else (to_int(it.get("result")) if isinstance(it,dict) else None)) for it,k in zip(res,keys)}
        except Exception: continue
    return None
def block():
    for ep in EPS:
        try:
            r=post(ep,{"jsonrpc":"2.0","id":1,"method":"eth_blockNumber","params":[]})
            return int(r["result"],16)
        except Exception: continue
    return None
out={"block":block()}
out["mint"]=batch(MINT,["launched()","failed()","isRefundPhase()","totalShares()","tokenClaimed(address)"])
out["token_balance"]=batch(TOKEN,["balanceOf(address)"])
print(json.dumps(out,indent=1))
json.dump(out,open("run-2026-11-09-1131-binanceai.json","w"),indent=1)
