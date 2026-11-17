#!/usr/bin/env python3
"""Run 1631 triage: Skunk Hollow 0x88E4b613... + PAWG recheck if needed. Read-only."""
import json, subprocess, time, urllib.request
from Crypto.Hash import keccak
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
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
def post_rpc(ep,payload,timeout=25):
    out=subprocess.run(["curl","-sL","--max-time",str(timeout),"-X","POST",ep,"-H","Content-Type: application/json","-d",json.dumps(payload)],capture_output=True,text=True,timeout=timeout+5).stdout
    return json.loads(out)
def raw_batch(addr,views):
    calls,keys=[],[]
    for i,sig in enumerate(views):
        base=sig.split("(")[0]
        if "(address)" in sig: data=sel(sig)+enc(USER); key=base+"_user"
        else: data=sel(sig); key=base
        calls.append({"jsonrpc":"2.0","id":i+1,"method":"eth_call","params":[{"to":addr,"data":data},"latest"]}); keys.append(key)
    for ep in EPS:
        try:
            res=post_rpc(ep,calls)
            if not isinstance(res,list) or len(res)!=len(calls): continue
            return {key:(None if (isinstance(it,dict) and "error" in it) else (to_int(it.get("result")) if isinstance(it,dict) else None)) for it,key in zip(res,keys)}
        except Exception: continue
    return None
def get_code(addr):
    for ep in EPS:
        try:
            r=post_rpc(ep,{"jsonrpc":"2.0","id":1,"method":"eth_getCode","params":[addr,"latest"]},timeout=25)
            if isinstance(r,dict) and r.get("result"): return r["result"]
        except Exception: continue
    return None
def get_block():
    for ep in EPS:
        try:
            r=post_rpc(ep,{"jsonrpc":"2.0","id":1,"method":"eth_blockNumber","params":[]},timeout=25)
            return int(r["result"],16)
        except Exception: continue
    return None
REG="60b9262456de011f7d15a54CdD8c48bAaa8B022F".lower()
VIEWS=["totalSupply()","freeSkunksClaimed()","paidSkunksSold()","FREE_SUPPLY()","MAX_SUPPLY()","mintStart()","mintEnd()","windowEnd()","endTime()","mintOpen()","balanceOf(address)","freeClaimedBy(address)","freeClaimed(address)","owner()"]
addr="0x88E4b613609af6C479F11D78e5a696d84B78993B"
code=get_code(addr)
got=raw_batch(addr,VIEWS)
out={"block":get_block(),"address":addr,"reads":got,"code_len":len(code) if code else None,"registry_bytes":(REG in code.lower()) if code else None}
print(json.dumps(out,indent=1), flush=True)
# Sourcify metadata for site pointers
try:
    req=urllib.request.Request(f"https://sourcify.dev/server/v2/contract/56/{addr}",headers={"User-Agent":"Mozilla/5.0"})
    with urllib.request.urlopen(req,timeout=20) as r: data=json.load(r)
    std=data.get("stdJson",{})
    print("SOURCIFY match:", data.get("match"), "creation:", data.get("creationMatch"), "runtime:", data.get("runtimeMatch"), flush=True)
    meta=data.get("metadata") or {}
    srcs=(std.get("sources") or {})
    print("SOURCIFY sources:", list(srcs.keys())[:10], flush=True)
    out["sourcify"]={"match":data.get("match"),"sources":list(srcs.keys())}
except Exception as e:
    print("SOURCIFY ERR", e, flush=True); out["sourcify"]={"error":str(e)}
with open(f"{BASE}/run-2026-11-09-1631-triage-skunk.json","w") as f: json.dump(out,f,indent=1)
print("SKUNK TRIAGE DONE", flush=True)
