#!/usr/bin/env python3
"""Probe run 0901: Stampooor user slot (correct sigs) + 0x7Eb9 name/quote/MAX. Read-only."""
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
fa=call(ST, sel("freeAvailable(address)")+enc(USER))
fu=call(ST, sel("freeUsed(address)")+enc(USER))
fm=call(ST, sel("freeMinted()"))
print("STAMPOOOR freeAvailable(user)=",to_int(fa),"freeUsed(user)=",to_int(fu),"freeMinted=",to_int(fm),flush=True)
out["Stampooor_slot"]={"freeAvailable_user":to_int(fa),"freeUsed_user":to_int(fu),"freeMinted":to_int(fm)}
A7="0x7Eb92041aa3037e39baA88154F279e3D9F85c593"
nm=call(A7, sel("name()"))
sy=call(A7, sel("symbol()"))
mx=call(A7, sel("MAX_SUPPLY()"))
tm=call(A7, sel("totalMinted()"))
mb=call(A7, sel("mintedBy(address)")+enc(USER))
def dec_str(res):
    try:
        b=bytes.fromhex(res[2:])
        ln=int.from_bytes(b[32:64],'big')
        return b[64:64+ln].decode(errors='ignore')
    except Exception: return None
print("0x7Eb9 name=",dec_str(nm),"symbol=",dec_str(sy),"MAX_SUPPLY=",to_int(mx),"totalMinted=",to_int(tm),"mintedBy(user)=",to_int(mb),flush=True)
out["0x7Eb9"]={"name":dec_str(nm),"symbol":dec_str(sy),"MAX_SUPPLY":to_int(mx),"totalMinted":to_int(tm),"mintedBy_user":to_int(mb)}
# quote: try quote(uint256) and quote(address,uint256)
q1=call(A7, sel("quote(uint256)")+enc_u(1))
print("0x7Eb9 quote(1)=",to_int(q1),flush=True)
out["0x7Eb9"]["quote_1"]=to_int(q1)
json.dump(out,open("run-2026-11-11-0901-probe-slot-7eb9.json","w"),indent=1)
print("DONE block",out["block"],flush=True)
