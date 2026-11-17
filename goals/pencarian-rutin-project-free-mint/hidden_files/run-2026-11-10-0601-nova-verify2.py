#!/usr/bin/env python3
"""NOVA verify v2 — curl batch transport (25s), run 2026-11-10 06:01 WIB. Read-only."""
import json, subprocess, time
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
VIEWS=["name()","symbol()","totalSupply()","MAX_SUPPLY()","FREE_SUPPLY()","FREE_PER_WALLET()",
 "MAX_PER_WALLET()","mintOpen()","freeClaimed()","freeMinted()","freeLeft()","balanceOf(address)",
 "freeClaimed(address)","mintedBy(address)","owner()","AGENT_ID_REGISTRY()","agentRegistry()",
 "AGENT_REGISTRY()","price()","priceFor(address)","quote(uint256)","spotsLeft()","totalMinted()",
 "mintPrice()","START_TIME()","startTime()","mintStart()","saleStart()","launchTime()","startAt()",
 "startedAt()","endTime()","freeFor(address)","freeUsed(address)","holdsAgentId(address)"]
calls=[]; keys=[]
for i,sig in enumerate(VIEWS):
    base=sig.split("(")[0]
    if "(address)" in sig: data=sel(sig)+enc(USER); key=base+"_user"
    elif "(uint256)" in sig: data=sel(sig)+"0"*63+"1"; key=base+"_1"
    else: data=sel(sig); key=base
    calls.append({"jsonrpc":"2.0","id":i+1,"method":"eth_call","params":[{"to":NOVA,"data":data},"latest"]}); keys.append(key)
out={"contract":NOVA,"block":None,"views":{}}
for ep in EPS:
    try:
        r=post(ep,{"jsonrpc":"2.0","id":1,"method":"eth_blockNumber","params":[]})
        out["block"]=int(r["result"],16); break
    except Exception: continue
for ep in EPS:
    try:
        res=post(ep,calls)
        if not isinstance(res,list) or len(res)!=len(calls): continue
        for item,key in zip(res,keys):
            out["views"][key]=None if (isinstance(item,dict) and "error" in item) else (toint(item.get("result")) if isinstance(item,dict) else None)
        break
    except Exception as e:
        out["batch_error_"+ep]=repr(e)
# string views raw
for fn in ["contractURI()","baseURI()","name()","symbol()"]:
    for ep in EPS:
        try:
            res=post(ep,[{"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":NOVA,"data":sel(fn)},"latest"]}])
            v=res[0].get("result") if isinstance(res,list) else None
            out.setdefault("raw",{})[fn]=v[:300] if v else None
            break
        except Exception: continue
# eth_getCode registry bytes
for ep in EPS:
    try:
        res=post(ep,{"jsonrpc":"2.0","id":1,"method":"eth_getCode","params":[NOVA,"latest"]})
        code=res.get("result","")
        out["code_len"]=(len(code)-2)//2 if code.startswith("0x") else 0
        out["code_registry"]="60b9262456de011f7d15a54cdd8c48baa8b022f" in code.lower()
        break
    except Exception: continue
print(json.dumps(out, indent=1))
json.dump(out, open("run-2026-11-10-0601-nova-verify2.json","w"), indent=1)
