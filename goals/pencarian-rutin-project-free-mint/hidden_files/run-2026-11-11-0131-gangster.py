#!/usr/bin/env python3
"""Run 0131: quick read Agentic Gangster 0x0a2a07ef09dd7d83e2312476f0588abaa3e34ce3. Read-only."""
import json, subprocess, time
from Crypto.Hash import keccak
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS=["https://bsc-dataseed.binance.org/","https://bsc-dataseed1.bnbchain.org/","https://bsc-dataseed2.bnbchain.org/"]
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64,"0")
def ti(v):
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
            return {k:(None if isinstance(it,dict) and "error" in it else ti(it.get("result")) if isinstance(it,dict) else None) for it,k in zip(res,keys)}
        except Exception: continue
    return None
def raw(addr,sig):
    for ep in EPS:
        try:
            res=post(ep,{"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":addr,"data":sel(sig)},"latest"]})
            if isinstance(res,dict) and "result" in res and res["result"] not in (None,"0x"): return res["result"]
        except Exception: continue
    return None
ADDR="0x0a2a07ef09dd7d83e2312476f0588abaa3e34ce3"
VIEWS=["totalSupply()","totalMinted()","freeClaimed()","freeMinted()","FREE_SUPPLY()","MAX_SUPPLY()","mintOpen()","balanceOf(address)","mintedBy(address)"]
v=batch(ADDR,VIEWS)
print("views:",v,flush=True)
code=None
for ep in EPS:
    try:
        r=post(ep,{"jsonrpc":"2.0","id":1,"method":"eth_getCode","params":[ADDR,"latest"]})
        if isinstance(r,dict) and r.get("result"): code=r["result"]; break
    except Exception: continue
print("registry_bytes:", ("60b9262456de011f7d15a54cdd8c48baaa8b022f" in (code or "").lower()), "code_len:", (len(code)-2 if code else None),flush=True)
print("owner:", raw(ADDR,"owner()"),flush=True)
json.dump({"address":ADDR,"views":v,"registry_bytes":("60b9262456de011f7d15a54cdd8c48baaa8b022f" in (code or "").lower())},open("run-2026-11-11-0131-gangster.json","w"),indent=1)
print("DONE")
