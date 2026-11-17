#!/usr/bin/env python3
"""REWINDCLUB fresh strong-lead legs: agentFreeUsed, slot, owner, mintOpen. Read-only."""
import json, subprocess
from Crypto.Hash import keccak
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
RC="0x39b451abbd53365e2277084cb60f9a2c5ad6e698"
EPS=["https://bsc-dataseed.binance.org/","https://bsc-dataseed1.bnbchain.org/"]
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64,"0")
def to_int(v):
    try: return int(v,16) if v not in (None,"0x") else None
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
r=batch(RC,[("agentFreeUsed()",None),("paidMinted()",None),("agentFreeByWallet(address)",USER),("balanceOf(address)",USER),("mintOpen()",None),("mintStart()",None),("totalSupply()",None),("owner()",None),("REGISTRY()",None)])
out={"agentFreeUsed":to_int(r[0]),"paidMinted":to_int(r[1]),"agentFreeByWallet_user":to_int(r[2]),
 "balanceOf_user":to_int(r[3]),"mintOpen":to_int(r[4]),"mintStart":to_int(r[5]),"totalSupply":to_int(r[6]),
 "owner":("0x"+r[7][-40:]) if r[7] else None,"REGISTRY":("0x"+r[8][-40:]) if r[8] else None}
print(json.dumps(out),flush=True)
json.dump(out,open("run-2026-11-11-0831-rewind.json","w"),indent=1)
