#!/usr/bin/env python3
"""Run 1001 probe: LumenFindings experiments 0..15 + Zephyra state + B77D extra free views.
Read-only; writes run-2026-11-14-1001-probe.json."""
import json, subprocess, time
from Crypto.Hash import keccak
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS=["https://bsc-dataseed.binance.org/","https://bsc-dataseed1.bnbchain.org/","https://bsc-rpc.publicnode.com/"]
t0=time.time()
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def enc_addr(a): return a[2:].lower().rjust(64,"0")
def enc_u(n): return format(n,"064x")
def to_int(v):
    try: return int(v,16) if v and v!="0x" else None
    except Exception: return None
def build(sig,args):
    d=sel(sig)
    for a in args:
        d+= enc_addr(a) if isinstance(a,str) and a.startswith("0x") and len(a)==42 else enc_u(int(a))
    return d
def post(ep,payload,timeout=150):
    o=subprocess.run(["curl","-sL","--max-time",str(timeout),"-X","POST",ep,"-H","Content-Type: application/json","-d",json.dumps(payload)],capture_output=True,text=True,timeout=timeout+10).stdout
    return json.loads(o)
LUMEN="0x4158B701EaA30E8FaDBaA526F70780A38318c1C4"
ZEPH="0x00a9791be6317d6e3a6c60f75a706c870d882048"
B77D="0xB77D3495d3ed4427dA78c9D0f7Cb76C21c23D9fe"
calls=[]; meta=[]
def add(name,key,addr,sig,args):
    calls.append({"jsonrpc":"2.0","id":len(calls)+1,"method":"eth_call","params":[{"to":addr,"data":build(sig,args)},"latest"]})
    meta.append((name,key))
add("LumenFindings","totalSpecimens",LUMEN,"totalSpecimens()",[])
add("LumenFindings","currentExperiment",LUMEN,"currentExperiment()",[])
add("LumenFindings","genesisOpen",LUMEN,"genesisOpen()",[])
for i in range(16):
    add("LumenFindings",f"specimensInExperiment_{i}",LUMEN,"specimensInExperiment(uint256)",[i])
    add("LumenFindings",f"isSealed_{i}",LUMEN,"isSealed(uint256)",[i])
add("Zephyra","totalMinted",ZEPH,"totalMinted()",[])
add("Zephyra","MAX_SUPPLY",ZEPH,"MAX_SUPPLY()",[])
add("Zephyra","mintOpen",ZEPH,"mintOpen()",[])
add("Zephyra","priceFor_user_1",ZEPH,"priceFor(address)",[USER])
add("Zephyra","mintedBy_user",ZEPH,"mintedBy(address)",[USER])
add("Zephyra","hasAgentId_user",ZEPH,"hasAgentId(address)",[USER])
add("Zephyra","MAX_PER_WALLET",ZEPH,"MAX_PER_WALLET()",[])
add("B77D","freeMinted",B77D,"freeMinted()",[])
add("B77D","freeClaimed",B77D,"freeClaimed()",[])
add("B77D","freeSupply",B77D,"freeSupply()",[])
add("B77D","FREE_SUPPLY",B77D,"FREE_SUPPLY()",[])
add("B77D","freeRemaining",B77D,"freeRemaining()",[])
add("B77D","priceFor_user",B77D,"priceFor(address)",[USER])
add("B77D","totalSupply",B77D,"totalSupply()",[])
out={}
for ep in EPS:
    try:
        res=post(ep,calls,timeout=150)
        if not isinstance(res,list) or len(res)!=len(calls):
            print("ep",ep,"bad shape",str(res)[:120],flush=True); continue
        for it,(name,key) in zip(res,meta):
            if not isinstance(it,dict) or "error" in it or it.get("result") in (None,"0x"):
                out.setdefault(name,{})[key]=None
            else:
                r=it["result"]; out.setdefault(name,{})[key]= to_int(r[:66]) if len(r)>=66 else r
        print("OK via",ep,f"({time.time()-t0:.0f}s)",flush=True); break
    except Exception as e:
        print("ep",ep,"exc",str(e)[:100],flush=True); continue
out["elapsed_s"]=round(time.time()-t0,1)
json.dump(out,open(BASE+"run-2026-11-14-1001-probe.json","w"),indent=1)
print(json.dumps(out,indent=1))
