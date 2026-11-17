#!/usr/bin/env python3
"""Fixed-decoder name reads for 3 new feed contracts + agentFreeUsed REWINDCLUB/NIGHTFORGE. Read-only."""
import json, subprocess
from Crypto.Hash import keccak
EPS=["https://bsc-dataseed.binance.org/","https://bsc-dataseed1.bnbchain.org/"]
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64,"0")
def to_int(v):
    try: return int(v,16) if v not in (None,"0x") else None
    except Exception: return None
def dec_str(v):
    try:
        if not v or v=="0x": return None
        b=bytes.fromhex(v[2:])
        off=int.from_bytes(b[0:32],"big"); ln=int.from_bytes(b[off:off+32],"big")
        return b[off+32:off+32+ln].decode(errors="replace")
    except Exception: return None
def post(ep,payload,timeout=25):
    out=subprocess.run(["curl","-sL","--max-time",str(timeout),"-X","POST",ep,"-H","Content-Type: application/json","-d",json.dumps(payload)],capture_output=True,text=True,timeout=timeout+5).stdout
    return json.loads(out)
def batch(addr, views):
    calls=[]
    for i,(sig,arg) in enumerate(views):
        data=sel(sig)+(enc(arg) if arg is not None else "")
        calls.append({"jsonrpc":"2.0","id":i+1,"method":"eth_call","params":[{"to":addr,"data":data},"latest"]})
    for ep in EPS:
        try:
            r=post(ep,calls,timeout=25)
            if isinstance(r,list) and len(r)==len(calls):
                return [it.get("result") if isinstance(it,dict) and "error" not in it else None for it in r]
        except Exception: continue
    return [None]*len(views)
out={}
for key,addr in [("FEED-4676","0x467696af8c2206B977B24081445104632dc1D459"),
                 ("FEED-08E3","0x08E3e40829718913fb627c818Cb334B1E3d5B699"),
                 ("FEED-0BF3","0x0BF38aFe23070C79f693DBDA4ce1866Ff11C4bF7")]:
    r=batch(addr,[("name()",None),("symbol()",None),("owner()",None)])
    out[key]={"name":dec_str(r[0]),"symbol":dec_str(r[1]),"owner":("0x"+r[2][-40:]) if r[2] else None}
    print(key,out[key],flush=True)
for key,addr in [("REWINDCLUB","0x39b451abbd53365e2277084cb60f9a2c5ad6e698"),
                 ("NIGHTFORGE","0x22f43ba09fd4beb9417d4484c60370354b220186")]:
    r=batch(addr,[("agentFreeUsed()",None),("paidMinted()",None),("totalSupply()",None)])
    out[key]={"agentFreeUsed":to_int(r[0]),"paidMinted":to_int(r[1]),"totalSupply":to_int(r[2])}
    print(key,out[key],flush=True)
json.dump(out,open("run-2026-11-11-0831-names.json","w"),indent=1)
