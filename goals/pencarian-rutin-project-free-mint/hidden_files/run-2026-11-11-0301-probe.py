#!/usr/bin/env python3
"""Run 0301 probes: ACORE, SAKURA, MOODENG, LOWB, 0x88D7624E. Read-only."""
import json, subprocess, time
from Crypto.Hash import keccak
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS=["https://bsc-dataseed.binance.org/","https://bsc-dataseed1.bnbchain.org/","https://bsc-dataseed2.bnbchain.org/"]
REG="60b9262456de011f7d15a54cdd8c48baa8b022f"
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64,"0")
def ti(v):
    try: return int(v,16) if v not in (None,"0x") else None
    except Exception: return None
def post(ep,payload,timeout=25):
    out=subprocess.run(["curl","-sL","--max-time",str(timeout),"-X","POST",ep,"-H","Content-Type: application/json","-d",json.dumps(payload)],capture_output=True,text=True,timeout=timeout+5).stdout
    return json.loads(out)
def call(ep,addr,data,timeout=25):
    r=post(ep,{"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":addr,"data":data},"latest"]},timeout)
    if isinstance(r,dict) and "error" in r: return None
    return ti(r.get("result")) if isinstance(r,dict) else None
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
def code(addr):
    for ep in EPS:
        try:
            r=post(ep,{"jsonrpc":"2.0","id":1,"method":"eth_getCode","params":[addr,"latest"]},timeout=25)
            c=(r.get("result") or "").lower()
            return {"len":len(c),"registry_bytes":REG in c}
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
VIEWS_NFT=["totalSupply()","freeClaimed()","freeMinted()","FREE_SUPPLY()","MAX_SUPPLY()","freeLeft()","mintOpen()","mintStart()","balanceOf(address)","freeClaimed(address)","contractURI()"]
print("BLOCK",out["block"],flush=True)
for name,addr in [("ACORE","0xf4bacf30fb8f69373f63d99c657f53dd7774af1d"),
                  ("SAKURA","0xF2705A84602369069782624279837A08bdbBf6D6")]:
    t=time.time(); v=batch(addr,VIEWS_NFT); c=code(addr)
    out[name]={"address":addr,"views":v,"code":c}
    print(name,v,"code:",c,f"({time.time()-t:.1f}s)",flush=True)
# MOODENG sale: freeMinted + paid + totalMinted + freeClaimed(user)
VIEWS_MOOD=["freeMinted()","totalMinted()","paidMinted()","FREE_SHARES()","TOTAL_SHARES()","freeClaimed(address)","mintedBy(address)"]
t=time.time(); out["MOODENG"]={"address":"0xbb45668788a08ceceea6b1a0d0f25c1b667e1668","views":batch("0xbb45668788a08ceceea6b1a0d0f25c1b667e1668",VIEWS_MOOD),"code":code("0xbb45668788a08ceceea6b1a0d0f25c1b667e1668")}
print("MOODENG",out["MOODENG"],f"({time.time()-t:.1f}s)",flush=True)
# LOWB sale
VIEWS_LOW=["opened()","totalFreeMinted()","totalMinted()","freeSharesRemaining()","sharesOf(address)","freeClaimed(address)"]
t=time.time(); out["LOWB"]={"address":"0x00487ED061C77A1dd5085ef3a2D593366f9C6B35","views":batch("0x00487ED061C77A1dd5085ef3a2D593366f9C6B35",VIEWS_LOW),"code":code("0x00487ED061C77A1dd5085ef3a2D593366f9C6B35")}
print("LOWB",out["LOWB"],f"({time.time()-t:.1f}s)",flush=True)
# 0x88D7624E new feed
t=time.time(); out["FEED88D7"]={"address":"0x88D7624Ecec5D327920C49F9Fe295885740Effe1","views":batch("0x88D7624Ecec5D327920C49F9Fe295885740Effe1",["totalSupply()","freeClaimed()","freeMinted()","mintOpen()","mintStart()"]),"code":code("0x88D7624Ecec5D327920C49F9Fe295885740Effe1")}
print("FEED88D7",out["FEED88D7"],f"({time.time()-t:.1f}s)",flush=True)
json.dump(out,open("run-2026-11-11-0301-probe.json","w"),indent=1)
print("DONE")
