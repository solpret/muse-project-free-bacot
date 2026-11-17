#!/usr/bin/env python3
"""0859 salvage: shape-check 1 new feed contract + RIG probe + leg4 re-read, hard-capped."""
import json, re, time, urllib.request, concurrent.futures
from Crypto.Hash import keccak
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
RPCS=["https://bsc-dataseed.bnbchain.org","https://bsc.nodereal.io/","https://bsc-dataseed1.binance.org/"]
REG="0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F"
NEW="0x7Fd63896472013696BB4658cCF3814FD2DDe80Da"
RIG="0xe657465f0EB4B55877246026BfAe4EC75ef2E160"
T0=time.time()
def fetch(url,timeout=12):
    req=urllib.request.Request(url,headers={"User-Agent":"hot-leg/1.0"})
    with urllib.request.urlopen(req,timeout=timeout) as r: return r.status,r.read()
def sel(sig):
    h=keccak.new(digest_bits=256); h.update(sig.encode()); return "0x"+h.hexdigest()[:8]
def post_rpc(ep,payload,timeout=10):
    req=urllib.request.Request(ep,data=json.dumps(payload).encode(),headers={"Content-Type":"application/json"})
    with urllib.request.urlopen(req,timeout=timeout) as r: return json.load(r)
def rpc_call(ep,to,data,frm=None,timeout=10):
    p={"to":to,"data":data}
    if frm: p["from"]=frm
    r=post_rpc(ep,{"jsonrpc":"2.0","id":1,"method":"eth_call","params":[p,"latest"]},timeout)
    return r.get("result")
# shape-check new contract
FREE_VIEWS={"freeSharesRemaining","freeClaimed","freeFor","freeLeft","freeUsed","freeAvailable","freeSharePoolExhausted","freeSharesClaimed","freeMinted","freeCardsRemaining"}
shape={}
try:
    st,body=fetch(f"https://sourcify.dev/server/v2/contract/56/{NEW}?fields=abi",timeout=12)
    meta=json.loads(body.decode()); abi=meta.get("abi",[])
    names={e["name"] for e in abi if e.get("type")=="function"}
    fns={}
    for e in abi:
        if e.get("type")=="function": fns.setdefault(e["name"],[]).append(e)
    has_mint=any(n.lower().startswith("mint") for n in names)
    has_quote=bool(names & {"quote","cost","getQuote","mintCost","price","getPrice"})
    fv=sorted(names & FREE_VIEWS)
    agent=bool(names & {"agentId","agentRegistry","registry","getAgentId","agentGate","AgentGate"})
    is_token=bool(names & {"name","symbol","decimals","totalSupply"})
    mintfree="mintFree" in fns and any(len(e.get("inputs",[]))==0 for e in fns["mintFree"])
    s1=has_mint and has_quote and bool(fv) and agent
    s2=(is_token and mintfree and bool(names & {"freeClaimed","freeMinted"}) and bool(names & {"FREE_SLOTS","FREE_SUPPLY"}) and agent)
    shape={"address":NEW,"S1":s1,"S2":s2,"has_mint":has_mint,"has_quote":has_quote,"free_views":fv,"agent_ref":agent,"is_token":is_token}
except Exception as e:
    shape={"address":NEW,"error":f"{type(e).__name__}:{str(e)[:100]}"}
print("SHAPE:",json.dumps(shape))
# pick working RPC fast
rpc=None; block=None
for ep in RPCS:
    try:
        bn=post_rpc(ep,{"jsonrpc":"2.0","id":1,"method":"eth_blockNumber","params":[]},timeout=8)
        block=int(bn["result"],16); rpc=ep; break
    except Exception: continue
print("RPC:",rpc,"block:",block)
def probe(to,sig,args=""):
    try:
        res=rpc_call(rpc,to,sel(sig)+args,timeout=8)
        if res and res!="0x":
            try: return int(res,16)
            except Exception: return res
        return None
    except Exception as e: return f"ERR:{type(e).__name__}"
rig={}
if rpc:
    u="000000000000000000000000"+USER[2:].lower()
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as ex:
        futs={
         "totalSupply":ex.submit(probe,RIG,"totalSupply()"),
         "freeMinted":ex.submit(probe,RIG,"freeMinted()"),
         "FREE_SUPPLY":ex.submit(probe,RIG,"FREE_SUPPLY()"),
         "freeClaimed_user":ex.submit(probe,RIG,"freeClaimed(address)",u),
         "balanceOf_user":ex.submit(probe,RIG,"balanceOf(address)",u),
         "owner":ex.submit(probe,RIG,"owner()"),
         "mintOpen":ex.submit(probe,RIG,"mintOpen()"),
        }
        for k,f in futs.items():
            try: rig[k]=f.result(timeout=12)
            except Exception as e: rig[k]=f"ERR:{type(e).__name__}"
    if isinstance(rig.get("owner"),int): rig["owner_addr"]="0x"+format(rig["owner"],"040x")
    rig["block"]=block
print("RIG:",json.dumps(rig))
# leg4 re-read
def calldata(field):
    if field.endswith("_user1"):
        return sel(f"{field[:-6]}(address,uint256)")+"000000000000000000000000"+USER[2:].lower()+format(1,"064x")
    if field.endswith("_user"):
        return sel(f"{field[:-5]}(address)")+"000000000000000000000000"+USER[2:].lower()
    return sel(f"{field}()")
prev=json.load(open(BASE+"hot-leg-run-2026-11-10-0854-leg4.json"))
prev_items=prev.get("leg4",{}); prev_probes=prev.get("probes",{})
extra={"THYRK":("0x4D90fFC3075FB8897EDFf6d7c6269c906664a20e",["totalSupply","freeMinted","mintActive","freeUsed_user","priceFor_user1"]),
       "SAKURA":("0xF2705A84602369069782624279837A08bdbBf6D6",["totalSupply","freeMinted"])}
jobs=[]
for name,entry in prev_items.items():
    addr=entry.get("address")
    if not addr: continue
    for field in entry:
        if field=="address": continue
        jobs.append(("item",name,field,addr,calldata(field)))
for name,(addr,fields) in extra.items():
    for f in fields: jobs.append(("probe",name,f,addr,calldata(f)))
def call_one(job):
    kind,n,f,to,data=job
    try:
        r=post_rpc(rpc,{"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":to,"data":data},"latest"]},timeout=8)
        res=r.get("result")
        if res and res!="0x":
            try: return (kind,n,f,int(res,16))
            except Exception: return (kind,n,f,None)
        return (kind,n,f,None)
    except Exception:
        return (kind,n,f,None)
results={}; failed=[]
if rpc:
    with concurrent.futures.ThreadPoolExecutor(max_workers=16) as ex:
        futs={ex.submit(call_one,j):j for j in jobs}
        for fut in concurrent.futures.as_completed(futs,timeout=90):
            kind,n,f,v=fut.result()
            if v is None: failed.append((kind,n,f))
            else: results[(kind,n,f)]=v
leg4_items={}; diffs=[]
for name,entry in prev_items.items():
    row={"address":entry.get("address")}
    for field in entry:
        if field=="address": continue
        v=results.get(("item",name,field))
        row[field]=entry.get(field) if v is None else v
        bv=entry.get(field)
        if isinstance(v,int) and isinstance(bv,int) and v!=bv: diffs.append({"item":name,"field":field,"was":bv,"now":v})
    leg4_items[name]=row
probes={}
for name,(addr,fields) in extra.items():
    probes[name]={"address":addr}
    for f in fields:
        v=results.get(("probe",name,f))
        probes[name][f]=v
        pv=prev_probes.get(name,{}).get(f)
        if isinstance(v,int) and isinstance(pv,int) and v!=pv: diffs.append({"item":name,"field":f,"was":pv,"now":v})
out={"run":"2026-11-10 08:59 WIB (salvage after 280s overrun)","block":block,"shape_new":shape,"rig":rig,
     "leg4":leg4_items,"probes":probes,"diffs":diffs,"read_failed":[[k,n,f] for (k,n,f) in failed],
     "elapsed_s":round(time.time()-T0,1)}
json.dump(out,open(BASE+"hot-leg-run-2026-11-10-0859-salvage.json","w"),indent=1)
print("DIFFS:",json.dumps(diffs))
print("FAILED:",len(failed),failed[:20])
print("ELAPSED:",round(time.time()-T0,1))
