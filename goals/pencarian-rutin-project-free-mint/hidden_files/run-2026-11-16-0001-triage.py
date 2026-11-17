#!/usr/bin/env python3
"""Triage LEGBEE + WISPAGENT for run 2026-11-16 00:01 WIB. Read-only."""
import json, subprocess, urllib.request
from Crypto.Hash import keccak
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS=["https://bsc-dataseed.binance.org/","https://bsc-dataseed1.bnbchain.org/","https://bsc-rpc.publicnode.com/"]
REG="0x60b9262456de011f7d15a54cdd8c48baaa8b022f"
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def enc_addr(a): return a[2:].lower().rjust(64,"0")
def enc_u(n): return format(n,"064x")
def data(sig,args):
    d=sel(sig)
    for a in args:
        if isinstance(a,str) and a.startswith("0x") and len(a)==42: d+=enc_addr(a)
        else: d+=enc_u(int(a))
    return d
def post(ep,payload,timeout=60):
    out=subprocess.run(["curl","-sL","--max-time",str(timeout),"-X","POST",ep,"-H","Content-Type: application/json","-d",json.dumps(payload)],capture_output=True,text=True,timeout=timeout+10).stdout
    return json.loads(out)
def call(addr,sig,args=[]):
    calls=[{"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":addr,"data":data(sig,args)},"latest"]}]
    for ep in EPS:
        try:
            r=post(ep,calls)
            if isinstance(r,dict) and "result" in r and r["result"] not in (None,"0x"):
                return r["result"]
        except Exception: pass
    return None
def to_int(v):
    try: return int(v,16) if v and v!="0x" else None
    except Exception: return None
def dec_str(v):
    if not v or len(v)<130: return None
    try:
        b=bytes.fromhex(v[2:])
        ln=int.from_bytes(b[64:96],'big')
        return b[96:96+ln].decode('utf-8',errors='ignore')
    except Exception: return None
def get_code(addr):
    for ep in EPS:
        try:
            r=post(ep,[{"jsonrpc":"2.0","id":1,"method":"eth_getCode","params":[addr,"latest"]}])
            if isinstance(r,dict) and r.get("result"): return r["result"]
        except Exception: pass
    return None
def block():
    for ep in EPS:
        try:
            r=post(ep,[{"jsonrpc":"2.0","id":1,"method":"eth_blockNumber","params":[]}])
            if isinstance(r,dict) and r.get("result"): return int(r["result"],16)
        except Exception: pass
    return None
def sourcify(addr):
    for base in ("https://sourcify.dev/server/v2/contracts/56/",):
        try:
            req=urllib.request.Request(base+addr,headers={"User-Agent":"Mozilla/5.0"})
            with urllib.request.urlopen(req,timeout=30) as resp:
                return json.loads(resp.read().decode())
        except Exception as e:
            return {"error":str(e)}
    return {}
VIEWS=["totalSupply()","totalMinted()","mintOpen()","mintActive()","MAX_SUPPLY()","FREE_SUPPLY()","FREE_CAP()","FREE_MAX()","freeMinted()","freeClaimed()","freeSupply()","freeLeft()","freeRemaining()","owner()","AGENT_ID()","agentRegistry()","name()","symbol()"]
USER_VIEWS=[("priceFor(address,uint256)",[USER,1]),("quote(address,uint256)",[USER,1]),("costFor(address,uint256)",[USER,1]),("freeClaimed(address)",[USER]),("mintedBy(address)",[USER]),("freeMintedBy(address)",[USER]),("balanceOf(address)",[USER]),("canFreeMint(address)",[USER]),("isEligible(address)",[USER]),("hasAgentId(address)",[USER])]
out={"block":block()}
for name,addr in [("LEGBEE","0x44a6e69a0b41ee345fa67afee68b0cc90a6ca149"),("WISPAGENT","0x84629f583e7eafba8f5f336b6943e8f23f8ae7bb")]:
    d={"address":addr}
    sf=sourcify(addr)
    if isinstance(sf,dict) and sf.get("stdJson"):
        try:
            abi=sf["stdJson"].get("output",{}).get("abi",[])
            fns=[f.get("name") for f in abi if f.get("type")=="function"]
            d["sourcify"]="verified"; d["verifiedAt"]=sf.get("verifiedAt"); d["functions"]=fns
            d["registry_in_abi"]=any("agent" in (f or "").lower() for f in fns)
        except Exception as e: d["sourcify"]="verified-parse-error "+str(e)
    else:
        d["sourcify"]=str(sf)[:200]
    code=get_code(addr)
    d["code_len"]=len(code)//2-1 if code else None
    d["registry_bytes_in_code"]= (REG[2:].lower() in code.lower()) if code else None
    for sig in VIEWS:
        key=sig.split("(")[0]
        r=call(addr,sig)
        if r is None: d[key]=None
        elif key in ("name","symbol"): d[key]=dec_str(r)
        else: d[key]=to_int(r[:66]) if len(r)>=66 else r
    for sig,args in USER_VIEWS:
        key=sig.split("(")[0]+"_user"
        r=call(addr,sig,args)
        d[key]=to_int(r[:66]) if (r and len(r)>=66) else r
    out[name]=d
    print(json.dumps(d,indent=1))
json.dump(out,open("run-2026-11-16-0001-triage.json","w"),indent=1)
