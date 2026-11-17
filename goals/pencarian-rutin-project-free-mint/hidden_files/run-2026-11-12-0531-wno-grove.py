#!/usr/bin/env python3
"""Run 0531 ad-hoc: WNO fresh free-pool read (track-C gate-failed 2026-11-10;
age check: sale open no later than Colony post 2026-11-10 10:56 WIB) +
Grove phase-2 freeOpen/freeClaimed(user). Read-only."""
import json, subprocess
from Crypto.Hash import keccak
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS=["https://bsc-dataseed.binance.org/","https://bsc-dataseed1.bnbchain.org/","https://bsc-dataseed2.bnbchain.org/"]
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64,"0")
def enc_u(n): return ("%064x"%n)
def to_int(v):
    try: return int(v,16) if v and v!="0x" else None
    except Exception: return None
def post_rpc(ep,payload,timeout=25):
    o=subprocess.run(["curl","-sL","--max-time",str(timeout),"-X","POST",ep,"-H","Content-Type: application/json","-d",json.dumps(payload)],capture_output=True,text=True,timeout=timeout+5).stdout
    return json.loads(o)
def raw_batch(addr,views):
    calls,keys=[],[]
    for i,(sig,args) in enumerate(views):
        base=sig.split("(")[0]
        data=sel(sig)
        for a in args:
            data+= enc(a) if isinstance(a,str) and a.startswith("0x") else enc_u(a)
        calls.append({"jsonrpc":"2.0","id":i+1,"method":"eth_call","params":[{"to":addr,"data":data},"latest"]})
        keys.append(base)
    for ep in EPS:
        try:
            res=post_rpc(ep,calls,timeout=25)
            if not isinstance(res,list) or len(res)!=len(calls): continue
            return {key:(None if (isinstance(it,dict) and "error" in it) else (to_int(it.get("result")) if isinstance(it,dict) else None)) for it,key in zip(res,keys)}
        except Exception: continue
    return None
def get_block():
    for ep in EPS:
        try:
            r=post_rpc(ep,{"jsonrpc":"2.0","id":1,"method":"eth_blockNumber","params":[]},timeout=25)
            return int(r["result"],16)
        except Exception: continue
    return None
blk=get_block()
wno=raw_batch("0x8C969a4CD49E4774908e667702C3d7C3ece164D0",
  [("totalSupply()",[]),("freeRemaining()",[]),("freeSharesRemaining()",[]),("freeClaimed()",[]),
   ("freeLeft()",[]),("freeClaimed(address)",[USER]),("quote(address,uint256)",[USER,1]),
   ("totalShares()",[]),("MAX_SHARES()",[])])
grove=raw_batch("0x8b710e45D38fD55E2D198d2295c0a0D24EBfd64c",
  [("freeOpen()",[]),("freeClaimed(address)",[USER])])
out={"block":blk,"WNO":wno,"Grove":grove}
print(json.dumps(out,indent=1))
json.dump(out,open(BASE+"run-2026-11-12-0531-wno-grove.json","w"),indent=1)
