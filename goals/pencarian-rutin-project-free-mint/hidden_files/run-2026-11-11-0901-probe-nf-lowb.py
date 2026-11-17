#!/usr/bin/env python3
"""Probe run 0901: NIGHTFORGE strong-lead legs + LOWB opened/free state. Read-only."""
import json, subprocess, urllib.request, time
from Crypto.Hash import keccak
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS=["https://bsc-dataseed.binance.org/","https://bsc-dataseed1.bnbchain.org/","https://bsc-dataseed2.bnbchain.org/"]
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64,"0")
def to_int(v):
    try: return int(v,16) if v not in (None,"0x") else None
    except Exception: return None
def post(ep,payload,timeout=25):
    out=subprocess.run(["curl","-sL","--max-time",str(timeout),"-X","POST",ep,"-H","Content-Type: application/json","-d",json.dumps(payload)],capture_output=True,text=True,timeout=timeout+5).stdout
    return json.loads(out)
def batch(addr, views):
    calls=[]; keys=[]
    for i,sig in enumerate(views):
        base=sig.split("(")[0]
        if "(address)" in sig: data=sel(sig)+enc(USER); key=base+"_user"
        else: data=sel(sig); key=base
        calls.append({"jsonrpc":"2.0","id":i+1,"method":"eth_call","params":[{"to":addr,"data":data},"latest"]}); keys.append(key)
    for ep in EPS:
        try:
            r=post(ep,calls,timeout=25)
            if isinstance(r,list) and len(r)==len(calls):
                return {k:(None if (isinstance(it,dict) and "error" in it) else (to_int(it.get("result")) if isinstance(it,dict) else None)) for it,k in zip(r,keys)}
        except Exception: continue
    return None
def block():
    for ep in EPS:
        try:
            r=post(ep,{"jsonrpc":"2.0","id":1,"method":"eth_blockNumber","params":[]},timeout=25)
            return int(r["result"],16)
        except Exception: continue
    return None
out={"block":block(),"started_wib":"2026-11-11 09:01 WIB"}
NF="0x22f43ba09fd4beb9417d4484c60370354b220186"
nf=batch(NF,["totalSupply()","agentFreeUsed()","paidMinted()","freeLeft()","AGENT_FREE_CAP()","mintStart()","mintEnd()","mintOpen()","agentFreeByWallet(address)","balanceOf(address)"])
out["NIGHTFORGE"]=nf
print("NIGHTFORGE",json.dumps(nf),flush=True)
# LOWB ABI first
LOWB="0x00487ED061C77A1dd5085ef3a2D593366f9C6B35"
try:
    req=urllib.request.Request(f"https://sourcify.dev/server/v2/contract/56/{LOWB}?fields=abi",headers={"User-Agent":"free-bacot/1.0"})
    with urllib.request.urlopen(req,timeout=20) as r: meta=json.loads(r.read().decode())
    abi=meta.get("abi",[])
    fns=sorted(set(e["name"] for e in abi if e.get("type")=="function"))
    print("LOWB fns",fns,flush=True)
    json.dump(abi,open("abi-0901-lowb.json","w"))
    views=[s for s in ["opened()","totalFreeMinted()","totalMinted()","totalPaidMinted()","FREE_SHARES()","MAX_SHARES()","freeClaimed(address)","mintStart()","MINT_DEADLINE()"] if s.split("(")[0] in fns]
    lb=batch(LOWB,views)
    out["LOWB"]=lb; out["LOWB_views"]=views
    print("LOWB",json.dumps(lb),flush=True)
except Exception as ex:
    print("LOWB ABI FAIL",repr(ex),flush=True)
    out["LOWB_error"]=repr(ex)
json.dump(out,open("run-2026-11-11-0901-probe-nf-lowb.json","w"),indent=1)
print("DONE block",out["block"],flush=True)
