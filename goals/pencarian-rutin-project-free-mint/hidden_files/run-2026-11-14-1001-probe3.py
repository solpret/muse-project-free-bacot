#!/usr/bin/env python3
"""Run 1001 probe3: Lumen exp10 window + B77D pool structure. Read-only."""
import json, subprocess, time
from Crypto.Hash import keccak
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS=["https://bsc-dataseed.binance.org/","https://bsc-dataseed1.bnbchain.org/","https://bsc-dataseed2.bnbchain.org/"]
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
def post(ep,payload,timeout=120):
    o=subprocess.run(["curl","-sL","--max-time",str(timeout),"-X","POST",ep,"-H","Content-Type: application/json","-d",json.dumps(payload)],capture_output=True,text=True,timeout=timeout+10).stdout
    return json.loads(o)
LUMEN="0x4158B701EaA30E8FaDBaA526F70780A38318c1C4"
B77D="0xB77D3495d3ed4427dA78c9D0f7Cb76C21c23D9fe"
CHUNKS=[
 ("Lumen-exp10", LUMEN, [("experimentStart_10","experimentStart(uint256)",[10]),("experimentEnd_10","experimentEnd(uint256)",[10]),("experimentStart_0","experimentStart(uint256)",[0]),("experimentEnd_0","experimentEnd(uint256)",[0]),("priceFor_user","priceFor(address)",[USER])]),
 ("B77D-pools", B77D, [("MAX_SUPPLY","MAX_SUPPLY()",[]),("STANDARD_POOL_SIZE","STANDARD_POOL_SIZE()",[]),("LEGENDARY_POOL_SIZE","LEGENDARY_POOL_SIZE()",[]),("standardMinted","standardMinted()",[]),("legendaryMinted","legendaryMinted()",[]),("freeCount_user","freeCount(address)",[USER]),("freePerWallet","freePerWallet()",[]),("freeAgentGate","freeAgentGate()",[]),("mintOpen","mintOpen()",[])]),
]
out={}
for cname, addr, views in CHUNKS:
    calls=[{"jsonrpc":"2.0","id":i+1,"method":"eth_call","params":[{"to":addr,"data":build(s,a)},"latest"]} for i,(k,s,a) in enumerate(views)]
    done=False
    for ep in EPS:
        try:
            res=post(ep,calls,timeout=120)
            if not isinstance(res,list) or len(res)!=len(calls):
                print(cname,"ep",ep,"bad shape",str(res)[:100],flush=True); continue
            d={}
            for it,(k,s,a) in zip(res,views):
                if not isinstance(it,dict) or "error" in it or it.get("result") in (None,"0x"):
                    d[k]=None
                else:
                    r=it["result"]; d[k]= to_int(r[:66]) if len(r)>=66 else r
            out[cname]=d; print(cname,"OK via",ep,f"({time.time()-t0:.0f}s)",flush=True); done=True; break
        except Exception as e:
            print(cname,"ep",ep,"exc",str(e)[:80],flush=True); continue
    if not done: out[cname]=None; print(cname,"FAIL",flush=True)
    time.sleep(5)
out["elapsed_s"]=round(time.time()-t0,1)
json.dump(out,open(BASE+"run-2026-11-14-1001-probe.json","w"),indent=1)
print(json.dumps(out,indent=1))
