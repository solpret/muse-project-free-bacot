#!/usr/bin/env python3
"""Run 0301 probe2: agent-shape views + cost views + token identity. Read-only."""
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
        if "(address)" in sig and ",uint256)" not in sig and sig.count("address")==1:
            data=sel(sig)+enc(USER); key=base+"_user"
        elif "(address,uint256)" in sig:
            data=sel(sig)+enc(USER)+"0000000000000000000000000000000000000000000000000000000000000001"; key=base+"_user_1"
        else:
            data=sel(sig); key=base
        calls.append({"jsonrpc":"2.0","id":i+1,"method":"eth_call","params":[{"to":addr,"data":data},"latest"]}); keys.append(key)
    for ep in EPS:
        try:
            res=post(ep,calls)
            if not isinstance(res,list) or len(res)!=len(calls): continue
            d={}
            for it,k in zip(res,keys):
                if isinstance(it,dict) and "error" in it: d[k]=None
                elif isinstance(it,dict):
                    r=it.get("result")
                    d[k]=r if (r and len(r)>66) else ti(r)
                else: d[k]=None
            return d
        except Exception: continue
    return None
AGENT=["agentRegistry()","REGISTRY()","agentId()","agentGate()","AGENT_REGISTRY()"]
COST=["costOf(address,uint256)","quote(address,uint256)","priceOf(address,uint256)","PRICE()","price()","getQuote(address,uint256)"]
out={}
for name,addr,views in [
    ("ACORE","0xf4bacf30fb8f69373f63d99c657f53dd7774af1d",AGENT+COST),
    ("SAKURA","0xF2705A84602369069782624279837A08bdbBf6D6",AGENT),
    ("LOWB","0x00487ED061C77A1dd5085ef3a2D593366f9C6B35",AGENT+COST+["PRICE(address)","totalFreeMinted()","freeMinted()"]),
    ("FEED88D7","0x88D7624Ecec5D327920C49F9Fe295885740Effe1",["name()","symbol()","decimals()","totalSupply()"]),
]:
    t=time.time(); v=batch(addr,views); out[name]=v
    print(name,v,f"({time.time()-t:.1f}s)",flush=True)
json.dump(out,open("run-2026-11-11-0301-probe2.json","w"),indent=1)
print("DONE")
