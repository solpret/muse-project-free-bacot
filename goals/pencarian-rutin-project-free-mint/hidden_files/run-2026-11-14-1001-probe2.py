#!/usr/bin/env python3
"""Run 1001 probe retry: small chunks (<=16 calls), bsc-dataseed first."""
import json, subprocess, time
from Crypto.Hash import keccak
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS=["https://bsc-dataseed.binance.org/","https://bsc-dataseed1.bnbchain.org/","https://bsc-dataseed2.bnbchain.org/","https://bsc-rpc.publicnode.com/"]
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
CHUNKS=[
 ("LumenFindings-a", LUMEN, [("totalSpecimens","totalSpecimens()",[]),("genesisOpen","genesisOpen()",[])]+[(f"specimensInExperiment_{i}","specimensInExperiment(uint256)",[i]) for i in range(8)]),
 ("LumenFindings-b", LUMEN, [(f"specimensInExperiment_{i}","specimensInExperiment(uint256)",[i]) for i in range(8,16)]+[(f"isSealed_{i}","isSealed(uint256)",[i]) for i in range(16)]),
 ("Zephyra", ZEPH, [("totalMinted","totalMinted()",[]),("MAX_SUPPLY","MAX_SUPPLY()",[]),("mintOpen","mintOpen()",[]),("priceFor_user_1","priceFor(address)",[USER]),("mintedBy_user","mintedBy(address)",[USER]),("hasAgentId_user","hasAgentId(address)",[USER]),("MAX_PER_WALLET","MAX_PER_WALLET()",[])]),
 ("B77D-free", B77D, [("freeMinted","freeMinted()",[]),("freeClaimed","freeClaimed()",[]),("freeSupply","freeSupply()",[]),("FREE_SUPPLY","FREE_SUPPLY()",[]),("freeRemaining","freeRemaining()",[]),("priceFor_user","priceFor(address)",[USER]),("totalSupply","totalSupply()",[]),("totalMinted","totalMinted()",[])]),
]
out={}
for cname, addr, views in CHUNKS:
    calls=[{"jsonrpc":"2.0","id":i+1,"method":"eth_call","params":[{"to":addr,"data":build(s,a)},"latest"]} for i,(k,s,a) in enumerate(views)]
    done=False
    for ep in EPS:
        try:
            res=post(ep,calls,timeout=150)
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
    if not done:
        out[cname]=None; print(cname,"FAIL all endpoints",flush=True)
    time.sleep(5)
out["elapsed_s"]=round(time.time()-t0,1)
json.dump(out,open(BASE+"run-2026-11-14-1001-probe.json","w"),indent=1)
print(json.dumps(out,indent=1))
