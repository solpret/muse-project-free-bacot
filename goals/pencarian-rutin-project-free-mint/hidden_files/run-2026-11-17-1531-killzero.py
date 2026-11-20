#!/usr/bin/env python3
"""Fresh KillZero re-read for run 1531 (hot leg reported OPENED 15:21, FREE_SHARES=0)."""
import json, subprocess, sys
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from eth_hash.auto import keccak
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
KZ = "0x87ad9c1617ceb65f1b56f2ee06FE193F60aACF97"
def sel(sig): return keccak(sig.encode())[:4].hex()
def enc(a): return "0"*24 + a[2:].lower()
def curl_batch(calls, url, timeout=15):
    out=[]
    for i in range(0,len(calls),5):
        chunk=calls[i:i+5]
        payload=[{"jsonrpc":"2.0","id":j+1,"method":"eth_call","params":[{"to":t,"data":d},"latest"]} for j,(t,d) in enumerate(chunk)]
        r=subprocess.run(["curl","-s","--max-time",str(timeout),url,"-H","Content-Type: application/json","-d",json.dumps(payload)],capture_output=True,timeout=timeout+5)
        if r.returncode!=0 or not r.stdout: raise IOError(f"curl rc={r.returncode}")
        resp=json.loads(r.stdout.decode()); by={it["id"]:it for it in resp if isinstance(it,dict)}
        for j in range(len(chunk)):
            it=by.get(j+1,{})
            if "result" in it and it["result"] not in (None,"0x"):
                try: out.append(int(it["result"],16))
                except Exception: out.append(it["result"])
            else: out.append(None)
    return out
# quoteFor(address,uint256) returns (cost, tokensOut) tuple -> decode manually below
views=[("launched","launched()"),("launchedAt","launchedAt()"),("FREE_SHARES","FREE_SHARES()"),
       ("totalFreeClaimed","totalFreeClaimed()"),("totalMintCount","totalMintCount()"),
       ("freeClaimedById_user","freeClaimedById(address)")]
calls=[]; meta=[]
for label,sig in views:
    d="0x"+sel(sig)
    if "(address)" in sig: d+=enc(USER)
    calls.append((KZ,d)); meta.append(label)
# quoteFor(user,1): returns tuple; use raw call
qdata="0x"+sel("quoteFor(address,uint256)")+enc(USER)+"%064x"%1
calls.append((KZ,qdata)); meta.append("quoteFor_user_1_raw")
res=curl_batch(calls,"https://bsc-dataseed.binance.org/")
out={}
for label,val in zip(meta,res):
    if label=="quoteFor_user_1_raw":
        out[label]=val
    else:
        out[label]=val
# block
import urllib.request
payload=json.dumps([{"jsonrpc":"2.0","id":1,"method":"eth_blockNumber","params":[]}]).encode()
req=urllib.request.Request("https://bsc-dataseed.binance.org/",data=payload,headers={"Content-Type":"application/json"})
with urllib.request.urlopen(req,timeout=10) as r:
    out["block"]=int(json.loads(r.read().decode())[0]["result"],16)
print(json.dumps(out,indent=1))
json.dump(out,open("run-2026-11-17-1531-killzero.json","w"),indent=1)
