#!/usr/bin/env python3
"""Fresh pre-execution probe run 0401: agentFreeUsed/freeLeft/slot/owner/PAYEE/PRICE for RIMEVAULT + MYCELIX (+ NIGHTFORGE agentFreeUsed). Read-only."""
import json, subprocess, time
from Crypto.Hash import keccak
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS=["https://bsc-dataseed.binance.org/","https://bsc-dataseed1.bnbchain.org/","https://bsc-dataseed2.bnbchain.org/"]
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
def raw_batch(addr,views):
    calls,keys=[],[]
    for i,sig in enumerate(views):
        base=sig.split("(")[0]
        if "(address)" in sig: data=sel(sig)+enc(USER); key=base+"_user"
        else: data=sel(sig); key=base
        calls.append({"jsonrpc":"2.0","id":i+1,"method":"eth_call","params":[{"to":addr,"data":data},"latest"]})
        keys.append(key)
    for ep in EPS:
        try:
            res=post(ep,calls,timeout=25)
            if not isinstance(res,list) or len(res)!=len(calls): continue
            outd={}
            for item,key in zip(res,keys):
                if isinstance(item,dict) and "error" in item: outd[key]=None
                elif isinstance(item,dict):
                    r=item.get("result")
                    outd[key]=r  # raw hex kept; ints decoded below
                else: outd[key]=None
            return outd
        except Exception: continue
    return None
VIEWS=["agentFreeUsed()","freeLeft()","agentFreeByWallet(address)","balanceOf(address)","mintOpen()","mintStart()","mintEnd()","PRICE()","paidMinted()","totalSupply()","REGISTRY()","PAYEE()","owner()","status()","AGENT_FREE_CAP()","MAX_SUPPLY()"]
TARGETS={"RIMEVAULT":"0x96e879c79b1191a0954022c7483c44b2ee522ba1","MYCELIX":"0xb1636010fb87f50574f76f6644b7cd306a6a4d1f","NIGHTFORGE":"0x22f43ba09fd4beb9417d4484c60370354b220186"}
out={"block":None,"probe":{},"started_wib":"2026-11-11 04:01 WIB"}
for ep in EPS:
    try:
        r=post(ep,{"jsonrpc":"2.0","id":1,"method":"eth_blockNumber","params":[]},timeout=25)
        out["block"]=int(r["result"],16); break
    except Exception: continue
print("BLOCK",out["block"],flush=True)
for name,addr in TARGETS.items():
    got=raw_batch(addr,VIEWS)
    d={"address":addr}
    if got is None:
        d["_batch_fail"]=True
    else:
        for k,v in got.items():
            if k in ("REGISTRY_user","PAYEE_user","owner_user"): continue
            if k in ("REGISTRY","PAYEE","owner"):
                d[k]=v  # raw 32-byte hex (address in last 20 bytes)
            else:
                d[k]=to_int(v)
    out["probe"][name]=d
    print(name,json.dumps(d),flush=True)
json.dump(out,open(f"{BASE}/run-2026-11-11-0401-probe.json","w"),indent=1)
print("PROBE DONE",flush=True)
