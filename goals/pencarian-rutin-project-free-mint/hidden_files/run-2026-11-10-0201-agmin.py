#!/usr/bin/env python3
"""Triage AGMIN 0x8670e99062ead2ce5402754aede769602fdf38b8 (Boltbook cyroo.ai post 02:0x WIB).
Read-only on-chain reads via curl dataseed (25s/call) + Sourcify ABI."""
import json, subprocess, time
from Crypto.Hash import keccak
ADDR="0x8670e99062ead2ce5402754aede769602fdf38b8"
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
def post(ep,payload,timeout=25):
    out=subprocess.run(["curl","-sL","--max-time",str(timeout),"-X","POST",ep,"-H","Content-Type: application/json","-d",json.dumps(payload)],capture_output=True,text=True,timeout=timeout+5).stdout
    return json.loads(out)
def call(addr,sig,arg=None):
    data=sel(sig)+(enc(arg) if arg else "")
    for ep in EPS:
        try:
            r=post(ep,{"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":addr,"data":data},"latest"]},timeout=25)
            if isinstance(r,dict) and "result" in r: return to_int(r["result"])
            if isinstance(r,dict) and "error" in r: return "ERR:"+str(r["error"].get("message",""))[:80]
        except Exception as e:
            continue
    return None
def call_raw(addr,sig,arg=None):
    data=sel(sig)+(enc(arg) if arg else "")
    for ep in EPS:
        try:
            r=post(ep,{"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":addr,"data":data},"latest"]},timeout=25)
            if isinstance(r,dict) and "result" in r: return r["result"]
            if isinstance(r,dict) and "error" in r: return "ERR:"+str(r["error"].get("message",""))[:80]
        except Exception:
            continue
    return None
views=["totalSupply()","totalMinted()","freeClaimed()","freeMinted()","FREE_SUPPLY()","MAX_SUPPLY()","mintOpen()","mintPrice()","PRICE()","price()","owner()","name()","symbol()","AGENT_ID()","agentRegistry()","AGENT_REGISTRY()","REGISTRY()","freeFor(address)","freeLeft()","freeUsed(address)","mintedBy(address)","freeClaimed(address)","balanceOf(address)","spotsLeft()","totalPaid()","quote(address,uint256)","quote(uint256)"]
out={}
for v in views:
    arg=USER if "(address)" in v else (1 if v=="quote(uint256)" else None)
    if v in ("quote(address,uint256)",): 
        # quote(address,uint256) needs 2 args: build manually
        data=sel(v)+enc(USER)+format(1,'064x')
        res=None
        for ep in EPS:
            try:
                r=post(ep,{"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":ADDR,"data":data},"latest"]},timeout=25)
                if isinstance(r,dict) and "result" in r: res=r["result"]; break
            except Exception: continue
        out[v]=res
        continue
    out[v]=call(ADDR,v,arg)
# name/symbol as strings
for v in ["name()","symbol()"]:
    raw=call_raw(ADDR,v)
    out[v+"_raw"]=str(raw)[:200] if raw else None
# block
blk=None
for ep in EPS:
    try:
        r=post(ep,{"jsonrpc":"2.0","id":1,"method":"eth_blockNumber","params":[]},timeout=25)
        blk=int(r["result"],16); break
    except Exception: continue
out["_block"]=blk
# Sourcify
try:
    r=subprocess.run(["curl","-sL","--max-time","30",f"https://sourcify.dev/server/v2/contracts/56/{ADDR}"],capture_output=True,text=True,timeout=35).stdout
    sj=json.loads(r)
    out["_sourcify_match"]=sj.get("match"); out["_sourcify_verifiedAt"]=sj.get("verifiedAt")
    abi=sj.get("abi") or (sj.get("stdJson") or {}).get("abi")
    if abi:
        fns=[f.get("name") for f in abi if isinstance(f,dict) and f.get("type")=="function"]
        out["_sourcify_fns"]=fns
        out["_sourcify_free_fns"]=[f for f in fns if "free" in f.lower() or "Free" in f]
        out["_sourcify_registry_fns"]=[f for f in fns if "agent" in f.lower() or "registry" in f.lower() or "Registry" in f]
except Exception as e:
    out["_sourcify_error"]=repr(e)[:200]
print(json.dumps(out,indent=1))
json.dump(out,open("run-2026-11-10-0201-agmin.json","w"),indent=1)
