#!/usr/bin/env python3
"""Run 0301 UFO probe. Read-only."""
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
def batch(addr,views):
    calls=[];keys=[]
    for i,sig in enumerate(views):
        base=sig.split("(")[0]
        if "(address)" in sig and sig.count("address")==1 and ",uint256)" not in sig:
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
                    r=it.get("result"); d[k]=r if (r and len(r)>66) else ti(r)
                else: d[k]=None
            return d
        except Exception: continue
    return None
ADDR="0xE4059eA596392AcA14100af6CDC9481c330E2728"
VIEWS=["totalSupply()","freeMinted()","freeClaimed()","freeSharesRemaining()","freeRemaining()","freeClaimed(address)","mintedBy(address)","quote(address,uint256)","costOf(address,uint256)","agentRegistry()","REGISTRY()","mintOpen()","opened()","launched()","deadline()","startTime()","TOTAL_SHARES()","FREE_SHARES()","sharesOf(address)"]
t=time.time(); v=batch(ADDR,VIEWS)
code=None
for ep in EPS:
    try:
        r=post(ep,{"jsonrpc":"2.0","id":1,"method":"eth_getCode","params":[ADDR,"latest"]},timeout=25)
        c=(r.get("result") or "").lower(); code={"len":len(c),"registry_bytes":REG in c}; break
    except Exception: continue
print("UFO",v,"code:",code,f"({time.time()-t:.1f}s)",flush=True)
json.dump({"address":ADDR,"views":v,"code":code},open("run-2026-11-11-0301-ufo.json","w"),indent=1)
# Sourcify correct endpoint
import urllib.request
try:
    req=urllib.request.Request("https://sourcify.dev/server/v2/contract/56/"+ADDR,headers={"User-Agent":"curl"})
    d=json.load(urllib.request.urlopen(req,timeout=25))
    print("SOURCIFY match:",d.get("match"),"verifiedAt:",d.get("verifiedAt"))
except Exception as e:
    print("SOURCIFY ERR",e)
print("DONE")
