#!/usr/bin/env python3
"""Run 1631 triage: Flare Agent + PAWG verify + 6 new Sourcify shape-checks. Read-only."""
import json, subprocess, time, urllib.request
from Crypto.Hash import keccak
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS=["https://bsc-dataseed1.bnbchain.org/","https://bsc-dataseed2.bnbchain.org/","https://bsc-dataseed.binance.org/"]
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64,"0")
def to_int(v):
    try:
        if v is None or v=="0x": return None
        return int(v,16)
    except Exception: return None
def post_rpc(ep,payload,timeout=25):
    out=subprocess.run(["curl","-sL","--max-time",str(timeout),"-X","POST",ep,"-H","Content-Type: application/json","-d",json.dumps(payload)],capture_output=True,text=True,timeout=timeout+5).stdout
    return json.loads(out)
def raw_batch(addr,views):
    calls,keys=[],[]
    for i,sig in enumerate(views):
        base=sig.split("(")[0]
        if "(address)" in sig: data=sel(sig)+enc(USER); key=base+"_user"
        else: data=sel(sig); key=base
        calls.append({"jsonrpc":"2.0","id":i+1,"method":"eth_call","params":[{"to":addr,"data":data},"latest"]}); keys.append(key)
    for ep in EPS:
        try:
            res=post_rpc(ep,calls)
            if not isinstance(res,list) or len(res)!=len(calls): continue
            return {key:(None if (isinstance(it,dict) and "error" in it) else (to_int(it.get("result")) if isinstance(it,dict) else None)) for it,key in zip(res,keys)}
        except Exception: continue
    return None
def get_code(addr):
    for ep in EPS:
        try:
            r=post_rpc(ep,{"jsonrpc":"2.0","id":1,"method":"eth_getCode","params":[addr,"latest"]},timeout=25)
            if isinstance(r,dict) and r.get("result"): return r["result"]
        except Exception: continue
    return None
def get_block():
    for ep in EPS:
        try:
            r=post_rpc(ep,{"jsonrpc":"2.0","id":1,"method":"eth_blockNumber","params":[]},timeout=25)
            return int(r["result"],16)
        except Exception: continue
    return None
REG="60b9262456de011f7d15a54cdd8c48baaa8b022f"
VIEWS=["name()","symbol()","totalSupply()","totalMinted()","freeClaimed()","freeMinted()","FREE_SUPPLY()","MAX_SUPPLY()","mintStart()","mintEnd()","mintOpen()","balanceOf(address)","freeClaimed(address)"]
out={"block":get_block(),"triage":{}}
for label,addr in [("Flare Agent","0xe2deb47514bbfd19550866c8820bce04e8a8d416"),("PAWG","0x587C303982187Ec578dF309d27670327b13202F8")]:
    t=time.time(); got=raw_batch(addr,VIEWS); code=get_code(addr)
    d={"address":addr,"reads":got,"code_len":len(code) if code else None,"registry_bytes":(REG in code.lower()) if code else None,"elapsed_s":round(time.time()-t,1)}
    out["triage"][label]=d
    print(label, json.dumps(d), flush=True)
# Sourcify shape-check for 6 new
NEW=["0xb79BA612aBe9BB82e727AB394b2c094C6507d76d","0x57cf26c69fC9171937BA47164a3F8F451FD85B20","0xCc844748C64b9b8e45aC4504553C9757c7CDB7E0","0x448f01b6366b333e3e8046645c35181FFF51De5b","0x9ecEb8B0081b9df25fF271bF24735d6Dea671D78","0x391D7b854b6152a201A3D83Ec2B83b4FC141C03C"]
FREE_VIEWS=["freeSharesRemaining","freeClaimed","freeFor","freeLeft","freeUsed","freeAvailable","freeSharePoolExhausted","freeSharesClaimed","freeMinted","freeSupply"]
for addr in NEW:
    try:
        req=urllib.request.Request(f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi",headers={"User-Agent":"Mozilla/5.0"})
        with urllib.request.urlopen(req,timeout=20) as r: data=json.load(r)
        abi=data.get("abi") or []
        fns={f.get("name") for f in abi if f.get("type")=="function"}
        mint=bool(fns & {"mint","mintFree","freeMint","claimFree","mintShares","claim"})
        quote=bool(fns & {"quote","getQuote","cost","price","mintPrice","getPrice"})
        free=[f for f in FREE_VIEWS if f in fns]
        agent=bool(fns & {"agentRegistry","REGISTRY","agentId","hasAgentId","AgentGate"}) or ("0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F" in json.dumps(data))
        token=bool(fns & {"name","symbol","decimals","totalSupply"})
        s1=mint and quote and bool(free) and agent
        s2=token and bool(fns & {"mintFree","freeMint"}) and bool(free) and agent
        out["triage"][addr]={"sourcify_abi":True,"fns":sorted(fns),"S1":s1,"S2":s2,"mint":mint,"quote":quote,"free":free,"agent":agent,"token":token}
    except Exception as e:
        out["triage"][addr]={"sourcify_abi":False,"error":str(e)}
    print(addr, json.dumps(out["triage"][addr]), flush=True)
with open(f"{BASE}/run-2026-11-09-1631-triage-new.json","w") as f: json.dump(out,f,indent=1)
print("TRIAGE DONE block", out["block"], flush=True)
