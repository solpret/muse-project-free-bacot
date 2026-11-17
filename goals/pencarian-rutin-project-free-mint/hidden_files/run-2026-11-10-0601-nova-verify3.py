#!/usr/bin/env python3
"""NOVA verify v3 — small batches (8), curl transport. Read-only."""
import json, subprocess
from Crypto.Hash import keccak
NOVA="0x1b6E6F62528DE674C12BC2C04C159336d3DB049e"
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS=["https://bsc-dataseed1.bnbchain.org/","https://bsc-dataseed2.bnbchain.org/","https://bsc-dataseed.binance.org/"]
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64,"0")
def toint(v):
    try: return int(v,16) if v not in (None,"0x") else None
    except Exception: return None
def post(ep,payload,timeout=25):
    out=subprocess.run(["curl","-sL","--max-time",str(timeout),"-X","POST",ep,"-H","Content-Type: application/json","-d",json.dumps(payload)],capture_output=True,text=True,timeout=timeout+5).stdout
    return json.loads(out)
VIEWS=["totalSupply()","MAX_SUPPLY()","FREE_SUPPLY()","FREE_PER_WALLET()","MAX_PER_WALLET()",
 "mintOpen()","freeClaimed()","freeMinted()","freeLeft()","balanceOf(address)","freeClaimed(address)",
 "mintedBy(address)","owner()","AGENT_ID_REGISTRY()","agentRegistry()","AGENT_REGISTRY()","price()",
 "priceFor(address)","quote(uint256)","spotsLeft()","totalMinted()","mintPrice()","START_TIME()",
 "startTime()","mintStart()","saleStart()","launchTime()","startAt()","startedAt()","endTime()",
 "freeFor(address)","freeUsed(address)","holdsAgentId(address)"]
out={"contract":NOVA,"block":None,"views":{}}
for ep in EPS:
    try:
        r=post(ep,{"jsonrpc":"2.0","id":1,"method":"eth_blockNumber","params":[]})
        out["block"]=int(r["result"],16); break
    except Exception: continue
for chunk_start in range(0,len(VIEWS),8):
    chunk=VIEWS[chunk_start:chunk_start+8]
    calls=[]; keys=[]
    for i,sig in enumerate(chunk):
        base=sig.split("(")[0]
        if "(address)" in sig: data=sel(sig)+enc(USER); key=base+"_user"
        elif "(uint256)" in sig: data=sel(sig)+"0"*63+"1"; key=base+"_1"
        else: data=sel(sig); key=base
        calls.append({"jsonrpc":"2.0","id":i+1,"method":"eth_call","params":[{"to":NOVA,"data":data},"latest"]}); keys.append(key)
    done=False
    for ep in EPS:
        try:
            res=post(ep,calls)
            if not isinstance(res,list) or len(res)!=len(calls): continue
            for item,key in zip(res,keys):
                out["views"][key]=None if (isinstance(item,dict) and "error" in item) else (toint(item.get("result")) if isinstance(item,dict) else None)
            done=True; break
        except Exception: continue
    print("chunk",chunk_start,"done" if done else "FAILED", flush=True)
print(json.dumps(out, indent=1))
json.dump(out, open("run-2026-11-10-0601-nova-verify3.json","w"), indent=1)
