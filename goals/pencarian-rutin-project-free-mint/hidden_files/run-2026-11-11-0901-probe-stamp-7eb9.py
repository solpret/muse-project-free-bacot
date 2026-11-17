#!/usr/bin/env python3
"""Probe run 0901: Stampooor user slot + 0x7Eb9 AGENT_ID/totalMinted. Read-only."""
import json, subprocess
from Crypto.Hash import keccak
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS=["https://bsc-dataseed.binance.org/","https://bsc-dataseed1.bnbchain.org/"]
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64,"0")
def enc_u(n): return hex(n)[2:].rjust(64,"0")
def to_int(v):
    try: return int(v,16) if v not in (None,"0x") else None
    except Exception: return None
def post(ep,payload,timeout=25):
    out=subprocess.run(["curl","-sL","--max-time",str(timeout),"-X","POST",ep,"-H","Content-Type: application/json","-d",json.dumps(payload)],capture_output=True,text=True,timeout=timeout+5).stdout
    return json.loads(out)
def call(addr,data):
    for ep in EPS:
        try:
            r=post(ep,{"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":addr,"data":data},"latest"]},timeout=25)
            if isinstance(r,dict) and "result" in r: return r["result"]
        except Exception: continue
    return None
def block():
    for ep in EPS:
        try:
            r=post(ep,{"jsonrpc":"2.0","id":1,"method":"eth_blockNumber","params":[]},timeout=25)
            return int(r["result"],16)
        except Exception: continue
    return None
out={"block":block()}
ST="0x467696af8c2206B977B24081445104632dc1D459"
# quote(uint256 1) + freeAvailable() + freeMinted() + totalMinted()
q=call(ST, sel("quote(uint256)")+enc_u(1))
fa=call(ST, sel("freeAvailable()"))
fm=call(ST, sel("freeMinted()"))
tm=call(ST, sel("totalMinted()"))
ms=call(ST, sel("mintStart()"))
print("STAMPOOOR quote(1)=",to_int(q),"freeAvailable=",to_int(fa),"freeMinted=",to_int(fm),"totalMinted=",to_int(tm),"mintStart=",to_int(ms),flush=True)
out["Stampooor"]={"quote_1":to_int(q),"freeAvailable":to_int(fa),"freeMinted":to_int(fm),"totalMinted":to_int(tm),"mintStart":to_int(ms)}
A7="0x7Eb92041aa3037e39baA88154F279e3D9F85c593"
ag=call(A7, sel("AGENT_ID()"))
tm7=call(A7, sel("totalMinted()"))
nm=call(A7, sel("name()"))
print("0x7Eb9 AGENT_ID raw=",ag," totalMinted=",to_int(tm7),flush=True)
out["0x7Eb9"]={"AGENT_ID_raw":ag,"totalMinted":to_int(tm7)}
if ag and len(ag)>=42:
    print("0x7Eb9 AGENT_ID addr=0x"+ag[-40:],flush=True)
    out["0x7Eb9"]["AGENT_ID_addr"]="0x"+ag[-40:]
json.dump(out,open("run-2026-11-11-0901-probe-stamp-7eb9.json","w"),indent=1)
print("DONE block",out["block"],flush=True)
