#!/usr/bin/env python3
"""Zephyra follow-up: priceFor(user,1) + historical totalMinted bracket. Read-only."""
import json, subprocess
from Crypto.Hash import keccak
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
ADDR="0x00a9791be6317d6e3a6c60f75a706c870d882048"
EPS=["https://bsc-dataseed.binance.org/","https://bsc-dataseed1.bnbchain.org/","https://bsc-dataseed2.bnbchain.org/","https://bsc-rpc.publicnode.com/"]
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
# priceFor(user,1) + priceFor(user,2) + priceFor(user,3)
calls=[]
labels=[]
for q in (1,2,3):
    calls.append({"jsonrpc":"2.0","id":len(calls)+1,"method":"eth_call","params":[{"to":ADDR,"data":build("priceFor(address,uint256)",[USER,q])},"latest"]})
    labels.append(f"priceFor_user_{q}")
# historical totalMinted at estimated blocks (1h ~ 5200 blocks; anchor blk 133465241 @ 09:36 WIB 14 Nov)
hist=[("2026-11-12 16:00 WIB",133249000),("2026-11-13 00:00 WIB",133290000),("2026-11-13 12:00 WIB",133353000),("2026-11-14 00:00 WIB",133415000),("2026-11-14 06:00 WIB",133446000),("2026-11-14 09:00 WIB",133462000)]
for lbl,blk in hist:
    calls.append({"jsonrpc":"2.0","id":len(calls)+1,"method":"eth_call","params":[{"to":ADDR,"data":build("totalMinted()",[])},hex(blk)]})
    labels.append(f"totalMinted@{lbl}(blk {blk})")
out={}
for ep in EPS:
    try:
        r=subprocess.run(["curl","-sL","--max-time","120","-X","POST",ep,"-H","Content-Type: application/json","-d",json.dumps(calls)],capture_output=True,text=True,timeout=130)
        res=json.loads(r.stdout)
        if not isinstance(res,list) or len(res)!=len(calls): print("bad shape",ep,str(res)[:150]); continue
        for lbl,it in zip(labels,res):
            if not isinstance(it,dict) or "error" in it or it.get("result") in (None,"0x"):
                out[lbl]=("ERR", str(it.get("error",{}).get("message","empty"))[:120] if isinstance(it,dict) else "bad")
            else:
                out[lbl]=to_int(it["result"][:66])
        print("OK via",ep); break
    except Exception as e: print("ep fail",ep,str(e)[:120])
print(json.dumps(out,indent=1))
json.dump(out,open(BASE+"run-2026-11-14-0931-zephyra2.json","w"),indent=1)
