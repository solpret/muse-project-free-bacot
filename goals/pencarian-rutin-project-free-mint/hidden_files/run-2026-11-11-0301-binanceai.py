#!/usr/bin/env python3
"""Run 0301 track-B binanceai check. Read-only."""
import json, subprocess
from Crypto.Hash import keccak
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS=["https://bsc-dataseed.binance.org/","https://bsc-dataseed1.bnbchain.org/","https://bsc-dataseed2.bnbchain.org/","https://bsc.nodereal.io/"]
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64,"0")
def ti(v):
    try: return int(v,16) if v not in (None,"0x") else None
    except Exception: return None
def post(ep,payload,timeout=25):
    out=subprocess.run(["curl","-sL","--max-time",str(timeout),"-X","POST",ep,"-H","Content-Type: application/json","-d",json.dumps(payload)],capture_output=True,text=True,timeout=timeout+5).stdout
    return json.loads(out)
def call(addr,sig):
    for ep in EPS:
        try:
            data=sel(sig)+enc(USER) if "(address)" in sig else sel(sig)
            r=post(ep,{"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":addr,"data":data},"latest"]})
            if isinstance(r,dict) and "error" not in r: return ti(r.get("result"))
        except Exception: continue
    return None
MINT="0x46cb1D3efd4307506Cda7EbBa5a51be64746739E"
TOKEN="0x209173F09aFbCA053C0de9e9763f503e9fb54a3c"
print("launched()=",call(MINT,"launched()"))
print("tokenClaimed(user)=",call(MINT,"tokenClaimed(address)"))
print("token balanceOf(user)=",call(TOKEN,"balanceOf(address)"))
print("DONE")
