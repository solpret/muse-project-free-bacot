#!/usr/bin/env python3
"""Run 2031 probes: MSTRACK 0xa37b + Lanternfield 0x9aab slot/owner. Read-only."""
import json, subprocess, time
from Crypto.Hash import keccak
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS=["https://bsc-dataseed.binance.org/","https://bsc-dataseed1.bnbchain.org/","https://bsc-dataseed2.bnbchain.org/"]
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64,"0")
def enc_uint(n): return format(n,"064x")
def post(ep,payload,timeout=25):
    out=subprocess.run(["curl","-sL","--max-time",str(timeout),"-X","POST",ep,"-H","Content-Type: application/json","-d",json.dumps(payload)],capture_output=True,text=True,timeout=timeout+5).stdout
    return json.loads(out)
def call(addr,sig,args=""):
    data=sel(sig)+args
    for ep in EPS:
        try:
            r=post(ep,{"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":addr,"data":data},"latest"]},timeout=25)
            res=r.get("result")
            if res is None or res=="0x": return None
            return res
        except Exception: continue
    return None
def as_int(h):
    if h is None: return None
    try: return int(h,16)
    except Exception: return h
def as_addr(h):
    if h is None: return None
    try: return "0x"+h[-40:]
    except Exception: return h
def as_str(h):
    if h is None: return None
    try:
        b=bytes.fromhex(h[2:])
        ln=int.from_bytes(b[32:64],"big")
        return b[64:64+ln].decode(errors="ignore")
    except Exception: return h
def probe(addr, views):
    out={}
    for v in views:
        if v.endswith("(address)"):
            r=call(addr,v,enc(USER))
        elif v=="quote(address,uint256)":
            r=call(addr,v,enc(USER)+enc_uint(1))
        elif v=="costOfMint(address,uint256)":
            r=call(addr,v,enc(USER)+enc_uint(1))
        elif v=="freeRemainingFor(address)":
            r=call(addr,v,enc(USER))
        else:
            r=call(addr,v)
        out[v]=r
    return out
VIEWS=["name()","symbol()","totalSupply()","totalMinted()","freeMinted()","freeClaimed()","FREE_SUPPLY()","MAX_SUPPLY()","mintOpen()","saleOpen()","mintStart()","saleStart()","owner()","agentRegistry()","REGISTRY()","registry()","freeLeft()","freeRemaining()","balanceOf(address)","freeClaimed(address)","freeMintedBy(address)","canFreeMint(address)","freeAvailable(address)","hasAgentId(address)","quote(address,uint256)","costOfMint(address,uint256)","freeRemainingFor(address)","mintPrice()","PRICE()"]
res={}
for label,addr in [("MSTRACK","0xa37b3ff7a1cabf77256a4b246eba1652011e4569"),("Lanternfield","0x9aab6e84096A780F9400CdD4E230FaA41B4545f2")]:
    t=time.time(); raw=probe(addr,VIEWS)
    d={}
    for k,v in raw.items():
        if k in ("name()","symbol()"): d[k]=as_str(v)
        elif k in ("owner()","agentRegistry()","REGISTRY()","registry()"): d[k]=as_addr(v)
        else: d[k]=as_int(v)
    d["_secs"]=round(time.time()-t,1)
    res[label]=d
    print(label, json.dumps(d), flush=True)
json.dump(res, open("run-2026-11-10-2031-probe.json","w"), indent=1)
print("PROBE DONE")
