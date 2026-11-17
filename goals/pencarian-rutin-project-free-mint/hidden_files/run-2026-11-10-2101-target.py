#!/usr/bin/env python3
"""Run 2101 targeted reads: BYTEBLOOM/KERNELMONK status+freeLeft; binanceai claim state. Read-only."""
import json, subprocess
from Crypto.Hash import keccak
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64,"0")
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS=["https://bsc-dataseed.binance.org/","https://bsc-dataseed1.bnbchain.org/","https://bsc-dataseed2.bnbchain.org/"]
def post(ep,payload,timeout=25):
    out=subprocess.run(["curl","-sL","--max-time",str(timeout),"-X","POST",ep,"-H","Content-Type: application/json","-d",json.dumps(payload)],capture_output=True,text=True,timeout=timeout+5).stdout
    return json.loads(out)
def batch(addr, sigs):
    calls=[];keys=[]
    for i,sig in enumerate(sigs):
        base=sig.split("(")[0]
        if "(address)" in sig: data=sel(sig)+enc(USER); key=base+"_user"
        else: data=sel(sig); key=base
        calls.append({"jsonrpc":"2.0","id":i+1,"method":"eth_call","params":[{"to":addr,"data":data},"latest"]}); keys.append(key)
    for ep in EPS:
        try:
            res=post(ep,calls,timeout=25)
            if not isinstance(res,list) or len(res)!=len(calls): continue
            d={}
            for item,key in zip(res,keys):
                r=item.get("result")
                d[key]=r
            return d
        except Exception: continue
    return None
def u(h):
    if h is None or h=="0x": return None
    try: return int(h,16)
    except Exception: return h
def tup(h):
    if h is None or h=="0x": return None
    try:
        b=bytes.fromhex(h[2:])
        return [int.from_bytes(b[i:i+32],"big") for i in range(0,len(b),32)]
    except Exception: return h
out={}
for label,addr in [("BYTEBLOOM","0x74bbDAD7c027C56bE30A7fEaC6F7371B95f1c32B"),("KERNELMONK","0x016b9CE7508628e4Fb19E4fAF3129Fdc41b150d7")]:
    r=batch(addr,["status()","freeLeft()","totalSupply()","mintOpen()"])
    d={}
    if r:
        d["status_tuple"]=tup(r.get("status"))
        d["freeLeft_tuple"]=tup(r.get("freeLeft"))
        d["totalSupply"]=u(r.get("totalSupply")); d["mintOpen"]=u(r.get("mintOpen"))
    out[label]=d
    print(label,json.dumps(d),flush=True)
r=batch("0x46cb1D3efd4307506Cda7EbBa5a51be64746739E",["launched()","failed()","isRefundPhase()","totalShares()","tokenClaimed(address)"])
d={}
if r:
    for k,v in r.items(): d[k]=u(v)
out["binanceai"]=d
print("binanceai",json.dumps(d),flush=True)
# block
for ep in EPS:
    try:
        h=post(ep,{"jsonrpc":"2.0","id":1,"method":"eth_blockNumber","params":[]},timeout=25)
        out["block"]=int(h["result"],16); break
    except Exception: continue
print("BLOCK",out.get("block"))
json.dump(out,open("run-2026-11-10-2101-target.json","w"),indent=1)
print("TARGET DONE")
