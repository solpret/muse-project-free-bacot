#!/usr/bin/env python3
"""Run 0131: agentFreeUsed/agentFreeByWallet/paidMinted fresh for 6 priority NFT contracts. Read-only."""
import json, subprocess, time
from Crypto.Hash import keccak
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS=["https://bsc-dataseed.binance.org/","https://bsc-dataseed1.bnbchain.org/","https://bsc-dataseed2.bnbchain.org/"]
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64,"0")
def ti(v):
    try: return int(v,16) if v not in (None,"0x") else None
    except Exception: return None
def post(ep,payload,timeout=25):
    out=subprocess.run(["curl","-sL","--max-time",str(timeout),"-X","POST",ep,"-H","Content-Type: application/json","-d",json.dumps(payload)],capture_output=True,text=True,timeout=timeout+5).stdout
    return json.loads(out)
def batch(addr,views):
    calls=[];keys=[]
    for i,sig in enumerate(views):
        base=sig.split("(")[0]
        if "(address)" in sig: data=sel(sig)+enc(USER); key=base+"_user"
        else: data=sel(sig); key=base
        calls.append({"jsonrpc":"2.0","id":i+1,"method":"eth_call","params":[{"to":addr,"data":data},"latest"]}); keys.append(key)
    for ep in EPS:
        try:
            res=post(ep,calls)
            if not isinstance(res,list) or len(res)!=len(calls): continue
            return {k:(None if isinstance(it,dict) and "error" in it else ti(it.get("result")) if isinstance(it,dict) else None) for it,k in zip(res,keys)}
        except Exception: continue
    return None
VIEWS=["agentFreeUsed()","agentFreeByWallet(address)","paidMinted()","mintOpen()","totalSupply()","mintStart()"]
ADDRS={
 "REWINDCLUB":"0x39b451abbd53365e2277084cb60f9a2c5ad6e698",
 "LCDSPRITE":"0xf341806c87b1ae196e67cea3c0dad75021f1ed92",
 "RIMEVAULT":"0x96e879c79b1191a0954022c7483c44b2ee522ba1",
 "MYCELIX":"0xb1636010fb87f50574f76f6644b7cd306a6a4d1f",
 "NIGHTFORGE":"0x22f43ba09fd4beb9417d4484c60370354b220186",
 "SOLDERCATS":"0x3D972EBbF7488f21b95250B867e2406c723C9DDC",
}
out={}
for name,addr in ADDRS.items():
    t=time.time(); out[name]={"address":addr,"views":batch(addr,VIEWS)}
    print(name, out[name]["views"], f"({time.time()-t:.1f}s)", flush=True)
json.dump(out,open("run-2026-11-11-0201-free.json","w"),indent=1)
print("DONE")
