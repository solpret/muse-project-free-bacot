#!/usr/bin/env python3
"""Fresh reads for age-exclusion evidence, run 2026-11-14 16:31 WIB. Read-only."""
import json, subprocess, time
from Crypto.Hash import keccak
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS=["https://bsc-dataseed.binance.org/","https://bsc-dataseed1.bnbchain.org/","https://bsc-rpc.publicnode.com/"]
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
        d+=enc_addr(a) if isinstance(a,str) and a.startswith("0x") and len(a)==42 else enc_u(int(a))
    return d
def post(ep,payload,timeout=120):
    out=subprocess.run(["curl","-sL","--max-time",str(timeout),"-X","POST",ep,"-H","Content-Type: application/json","-d",json.dumps(payload)],capture_output=True,text=True,timeout=timeout+10).stdout
    return json.loads(out)
ITEMS={
 "LUMO":("0x1e340592665889735c1f871aa13d038fa58bd09e",[("totalSupply","totalSupply()",[]),("freeMinted","freeMinted()",[]),("FREE_SUPPLY","FREE_SUPPLY()",[]),("freeStart","freeStart()",[]),("freeEnd","freeEnd()",[]),("balanceOf_user","balanceOf(address)",[USER])]),
 "LuckyCatch":("0xD405C90079c594DA2456F5b37B4158A12f1382e5",[("totalSupply","totalSupply()",[]),("totalMinted","totalMinted()",[]),("agentFreeCount","agentFreeCount()",[]),("paidSold","paidSold()",[]),("mintOpen","mintOpen()",[]),("mintStart","mintStart()",[]),("agentFreeUsed_user","agentFreeUsed(address)",[USER]),("balanceOf_user","balanceOf(address)",[USER])]),
}
calls,meta=[],[]
for name,(addr,views) in ITEMS.items():
    for key,sig,args in views:
        calls.append({"jsonrpc":"2.0","id":len(calls)+1,"method":"eth_call","params":[{"to":addr,"data":build(sig,args)},"latest"]})
        meta.append((name,key))
calls.append({"jsonrpc":"2.0","id":len(calls)+1,"method":"eth_blockNumber","params":[]})
out={"reads":{},"block":None}
for ep in EPS:
    try:
        res=post(ep,calls)
        if not isinstance(res,list) or len(res)!=len(calls): continue
        ok=0
        for it,(name,key) in zip(res,meta):
            v=to_int(it.get("result")) if isinstance(it,dict) and "error" not in it else None
            out["reads"].setdefault(name,{})[key]=v
            if v is not None: ok+=1
        blk=to_int(res[-1].get("result")) if isinstance(res[-1],dict) else None
        out["block"]=blk
        if ok>=10: break
    except Exception as e:
        print("ep fail",ep,str(e)[:100],flush=True)
out["started_wib"]="2026-11-14T16:31+07:00"
json.dump(out,open(BASE+"run-2026-11-14-1631-agecheck.json","w"),indent=1)
print(json.dumps(out,indent=1))
