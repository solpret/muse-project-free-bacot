#!/usr/bin/env python3
"""Leg-3 probe for 0x5AEc (S1 pass, ERC-721 + free views + agentIdRegistry).
Single JSON-RPC batch, read-only. Writes run-2026-11-14-1009-5aec-leg3.json."""
import json, subprocess, time
from Crypto.Hash import keccak
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
ADDR = "0x5AEc03C90656743475810926B2B2bd443D5c26a4"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-rpc.publicnode.com/"]
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc_addr(a): return a[2:].lower().rjust(64, "0")
def build(sig, args):
    d = sel(sig)
    for a in args:
        d += enc_addr(a) if isinstance(a, str) and a.startswith("0x") and len(a)==42 else format(int(a), "064x")
    return d
VIEWS = [
 ("FREE_CAP","FREE_CAP()",[]),("MAX_SUPPLY","MAX_SUPPLY()",[]),
 ("MAX_PER_WALLET","MAX_PER_WALLET()",[]),("freeMinted","freeMinted()",[]),
 ("totalMinted","totalMinted()",[]),("mintOpen","mintOpen()",[]),
 ("mintOpensAt","mintOpensAt()",[]),("price","price()",[]),
 ("freeClaimed_user","freeClaimed(address)",[USER]),
 ("holdsAgentId_user","holdsAgentId(address)",[USER]),
 ("balanceOf_user","balanceOf(address)",[USER]),
 ("mintsBy_user","mintsBy(address)",[USER]),
 ("agentIdRegistry","agentIdRegistry()",[]),
 ("name","name()",[]),("symbol","symbol()",[]),
 ("owner","owner()",[]),("REWARD","REWARD()",[]),
 ("rewardPool","rewardPool()",[]),("nextTokenId","nextTokenId()",[]),
 ("tokenURI_1","tokenURI(uint256)",[1]),
]
def to_int(v):
    try: return int(v,16) if v and v!="0x" else None
    except Exception: return None
def decode_str(r):
    try:
        if not r or len(r)<130: return None
        ln=int(r[66:130],16)
        return bytes.fromhex(r[130:130+ln*2]).decode('utf-8','ignore')
    except Exception: return None
calls=[]
for i,(k,sig,args) in enumerate(VIEWS):
    calls.append({"jsonrpc":"2.0","id":i+1,"method":"eth_call","params":[{"to":ADDR,"data":build(sig,args)},"latest"]})
t0=time.time(); out={"started_wib":"2026-11-14T10:09+07:00","address":ADDR}
for ep in EPS:
    try:
        p=subprocess.run(["curl","-sL","--max-time","90","-X","POST",ep,"-H","Content-Type: application/json","-d",json.dumps(calls)],capture_output=True,text=True,timeout=100)
        res=json.loads(p.stdout)
        if not isinstance(res,list) or len(res)!=len(calls):
            print("bad shape via",ep,str(res)[:120],flush=True); continue
        vals={}
        for (k,sig,args),it in zip(VIEWS,res):
            r=it.get("result") if isinstance(it,dict) else None
            if not r or r=="0x" or "error" in it: vals[k]=None; continue
            if k in ("name","symbol","tokenURI_1"): vals[k]=decode_str(r)
            elif k=="agentIdRegistry" or k=="owner": vals[k]="0x"+r[-40:] if len(r)>=66 else r
            else: vals[k]=to_int(r[:66]) if len(r)>=66 else r
        out["views"]=vals; out["endpoint"]=ep; out["elapsed_s"]=round(time.time()-t0,1)
        print(json.dumps(vals,indent=1),flush=True)
        break
    except Exception as e:
        print("ep fail",ep,str(e)[:100],flush=True); continue
json.dump(out,open(BASE+"run-2026-11-14-1009-5aec-leg3.json","w"),indent=1)
print("DONE", out.get("elapsed_s"))
