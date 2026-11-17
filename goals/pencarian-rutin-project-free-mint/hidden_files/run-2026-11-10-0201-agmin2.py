#!/usr/bin/env python3
"""AGMIN re-triage (fixed): batch eth_call for extra views + Sourcify + contractURI. Saves after each step."""
import json, subprocess, time
from Crypto.Hash import keccak
ADDR="0x8670e99062ead2ce5402754aede769602fdf38b8"
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS=["https://bsc-dataseed1.bnbchain.org/","https://bsc-dataseed2.bnbchain.org/","https://bsc-dataseed.binance.org/"]
OUT="run-2026-11-10-0201-agmin.json"
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
def save(d):
    json.dump(d,open(OUT,"w"),indent=1)
out={}
VIEWS=["owner()","freeFor(address)","freeLeft()","freeUsed(address)","mintedBy(address)","spotsLeft()","totalPaid()","mintOpen()","totalSupply()","freeClaimed()","freeMinted()","FREE_SUPPLY()","MAX_SUPPLY()"]
calls=[]; keys=[]
for i,sig in enumerate(VIEWS):
    base=sig.split("(")[0]
    if "(address)" in sig:
        data=sel(sig)+enc(USER); key=base+"_user"
    else:
        data=sel(sig); key=base
    calls.append({"jsonrpc":"2.0","id":i+1,"method":"eth_call","params":[{"to":ADDR,"data":data},"latest"]})
    keys.append(key)
# quote(address,1): append raw
calls.append({"jsonrpc":"2.0","id":len(calls)+1,"method":"eth_call","params":[{"to":ADDR,"data":sel("quote(address,uint256)")+enc(USER)+format(1,'064x')},"latest"]})
keys.append("quote_user_1_raw")
got=None
for ep in EPS:
    try:
        r=post(ep,calls,timeout=25)
        if isinstance(r,list) and len(r)==len(calls):
            got=r; print("BATCH OK via",ep,flush=True); break
    except Exception as e:
        print("batch fail",ep,repr(e)[:100],flush=True)
if got:
    for item,key in zip(got,keys):
        if isinstance(item,dict) and "error" in item:
            out[key]="ERR:"+str(item["error"].get("message",""))[:60]
        elif isinstance(item,dict):
            out[key]=item.get("result")
        else:
            out[key]=None
    # decode ints where sensible
    for k in list(out):
        if k!="quote_user_1_raw" and isinstance(out[k],str) and out[k].startswith("0x"):
            out[k+"_int"]=to_int(out[k])
    save(out); print("saved batch",flush=True)
# contractURI raw
for ep in EPS:
    try:
        r=post(ep,{"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":ADDR,"data":sel("contractURI()")},"latest"]},timeout=25)
        if isinstance(r,dict) and "result" in r:
            out["contractURI_raw"]=str(r["result"])[:400]; break
    except Exception: continue
save(out); print("saved contractURI",flush=True)
# Sourcify
try:
    r=subprocess.run(["curl","-sL","--max-time","30",f"https://sourcify.dev/server/v2/contracts/56/{ADDR}"],capture_output=True,text=True,timeout=35).stdout
    sj=json.loads(r)
    out["_sourcify_match"]=sj.get("match"); out["_sourcify_verifiedAt"]=sj.get("verifiedAt")
    abi=sj.get("abi") or (sj.get("stdJson") or {}).get("abi")
    if abi:
        fns=[f.get("name") for f in abi if isinstance(f,dict) and f.get("type")=="function"]
        out["_sourcify_fns"]=fns
        out["_sourcify_free_fns"]=[f for f in fns if "free" in f.lower()]
        out["_sourcify_registry_fns"]=[f for f in fns if "agent" in f.lower() or "registry" in f.lower()]
    save(out); print("saved sourcify",flush=True)
except Exception as e:
    out["_sourcify_error"]=repr(e)[:150]; save(out)
print(json.dumps(out,indent=1))
