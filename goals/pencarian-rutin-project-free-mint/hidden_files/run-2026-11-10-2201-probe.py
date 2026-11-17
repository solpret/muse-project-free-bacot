#!/usr/bin/env python3
"""Run 2201 targeted probes: BYTEBLOOM + SOLDERCATS + NIGHTFORGE slot/free/age. Read-only."""
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
def words(h):
    if h is None: return None
    b=bytes.fromhex(h[2:])
    return [int.from_bytes(b[i:i+32],"big") for i in range(0,len(b),32)]
def probe(addr, views):
    out={}
    for v in views:
        if v.endswith("(address)"): r=call(addr,v,enc(USER))
        elif v=="quote(address,uint256)": r=call(addr,v,enc(USER)+enc_uint(1))
        elif v=="walletInfo(address)": r=call(addr,v,enc(USER))
        else: r=call(addr,v)
        w=words(r)
        out[v]= w[0] if w and len(w)==1 else w
    return out
VIEWS=["totalSupply()","totalMinted()","freeMinted()","freeClaimed()","FREE_SUPPLY()","MAX_SUPPLY()","AGENT_FREE_CAP()","agentFreeUsed()","agentFreeByWallet(address)","mintOpen()","mintStart()","saleStart()","freeLeft()","balanceOf(address)","freeClaimed(address)","mintPrice()","PRICE()","quote(address,uint256)","walletInfo(address)","contractURI()"]
TARGETS=[("BYTEBLOOM","0x74bbDAD7c027C56bE30A7fEaC6F7371B95f1c32B"),
         ("SOLDERCATS","0x3D972EBbF7488f21b95250B867e2406c723C9DDC"),
         ("NIGHTFORGE","0x22f43ba09fd4beb9417d4484c60370354b220186")]
res={}
for label,addr in TARGETS:
    t=time.time(); d=probe(addr,VIEWS); d["_secs"]=round(time.time()-t,1)
    res[label]=d
    print(label, json.dumps(d), flush=True)
json.dump(res, open("run-2026-11-10-2201-probe.json","w"), indent=1)
print("PROBE DONE")
