#!/usr/bin/env python3
"""Hot-leg 0619 leg-4: batched re-read of 0614 baseline items + THYRK/SAKURA probes. Read-only."""
import json, subprocess, time
from Crypto.Hash import keccak
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
RPCS = ["https://bsc.nodereal.io/", "https://bsc-dataseed1.binance.org/"]
T0 = time.time()
def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode())
    return "0x" + k.hexdigest()[:8]
def enc_addr(a): return a.lower().replace("0x","").rjust(64,"0")
def enc_uint(n): return format(n,"064x")
def calldata(field):
    if field in ("address",): return None
    if field.endswith("_user1"):
        return sel(f"{field[:-6]}(address,uint256)") + enc_addr(USER) + enc_uint(1)
    if field.endswith("_user"):
        return sel(f"{field[:-5]}(address)") + enc_addr(USER)
    return sel(f"{field}()")
def post(ep, payload):
    p = subprocess.run(["curl","-s","--max-time","30","-X","POST",ep,"-H","Content-Type: application/json","--data",payload],capture_output=True,text=True)
    try: return json.loads(p.stdout)
    except Exception: return {"_err": p.stdout[:200]+p.stderr[:200]}
def blocknum():
    for ep in RPCS:
        try:
            r = post(ep, '{"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}')
            return int(r["result"],16), ep
        except Exception: continue
    return None, None
prev = json.load(open(BASE+"hot-leg-2026-11-10-0614-reread.json"))
items = prev["items"]
jobs=[]
for name,entry in items.items():
    for field in entry:
        d=calldata(field)
        if d: jobs.append((name,field,entry["address"],d))
# THYRK + SAKURA probes
extra = {
 "THYRK": ("0x4D90fFC3075FB8897EDFf6d7c6269c906664a20e", ["totalSupply","freeMinted","mintActive","freeUsed_user","priceFor_user1"]),
 "SAKURA": ("0xF2705A84602369069782624279837A08bdbBf6D6", ["totalSupply","freeMinted"]),
}
for name,(addr,fields) in extra.items():
    for f in fields:
        d=calldata(f)
        if d: jobs.append((name,f,addr,d))
block, ep = blocknum()
print("block:", block, "rpc:", ep, "calls:", len(jobs))
results={}; failed=[]
for i in range(0,len(jobs),25):
    chunk=jobs[i:i+25]
    payload=json.dumps([{"jsonrpc":"2.0","id":j,"method":"eth_call","params":[{"to":to,"data":data},"latest"]} for j,(_,_,to,data) in enumerate(chunk)])
    resp=post(ep or RPCS[0], payload)
    if isinstance(resp,dict):
        if "_err" in resp:
            for (n,f,_,_) in chunk: results[(n,f)]=None; failed.append((n,f))
            continue
        resp=[resp]
    for j,item in enumerate(resp):
        n,f,_,_=chunk[j]
        if isinstance(item,dict) and "result" in item and isinstance(item["result"],str):
            try: results[(n,f)]=int(item["result"],16)
            except Exception: results[(n,f)]=None; failed.append((n,f))
        else:
            results[(n,f)]=None; failed.append((n,f))
reread={"block":block,"items":{},"duration_sec":round(time.time()-T0,1)}
rf=[]
for name,entry in items.items():
    row={"address":entry["address"]}
    for field in entry:
        if field=="address": continue
        v=results.get((name,field))
        if v is None: row[field]=entry.get(field); rf.append((name,field))
        else: row[field]=v
    reread["items"][name]=row
probes={}
for name,(addr,fields) in extra.items():
    probes[name]={"address":addr}
    for f in fields:
        probes[name][f]=results.get((name,f))
reread["probes"]=probes
reread["read_failed"]=[{"item":n,"field":f} for n,f in rf]
diffs=[]
for name,row in reread["items"].items():
    base=items.get(name,{})
    for field,val in row.items():
        if field=="address": continue
        bv=base.get(field)
        if bv is not None and val is not None and val!=bv:
            diffs.append({"item":name,"field":field,"was":bv,"now":val})
reread["diffs"]=diffs
json.dump(reread, open(BASE+"hot-leg-2026-11-10-0619-reread.json","w"), indent=1)
print("diffs:", json.dumps(diffs))
print("probes:", json.dumps(probes))
print("read_failed:", len(rf), rf[:20])
print("duration:", round(time.time()-T0,1))
