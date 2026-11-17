#!/usr/bin/env python3
"""Triage retry LEGBEE + WISPAGENT, batched eth_call like reread script. Read-only."""
import json, subprocess
from Crypto.Hash import keccak
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS=["https://bsc-dataseed.binance.org/","https://bsc-dataseed1.bnbchain.org/","https://bsc-dataseed2.bnbchain.org/","https://bsc-rpc.publicnode.com/"]
REG="60b9262456de011f7d15a54cdd8c48baaa8b022f"
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
def post(ep,payload,timeout=150):
    out=subprocess.run(["curl","-sL","--max-time",str(timeout),"-X","POST",ep,"-H","Content-Type: application/json","-d",json.dumps(payload)],capture_output=True,text=True,timeout=timeout+10).stdout
    return json.loads(out)
def to_int(v):
    try: return int(v,16) if v and v!="0x" else None
    except Exception: return None
def dec_str(v):
    if not v or len(v)<130: return None
    try:
        b=bytes.fromhex(v[2:]); ln=int.from_bytes(b[64:96],'big')
        return b[96:96+ln].decode('utf-8',errors='ignore')
    except Exception: return None
VIEWS=["totalSupply()","totalMinted()","mintOpen()","mintActive()","MAX_SUPPLY()","FREE_SUPPLY()","FREE_CAP()","FREE_MAX()","freeMinted()","freeClaimed()","freeSupply()","freeLeft()","freeRemaining()","owner()","AGENT_ID()","agentRegistry()","name()","symbol()","paused()","mintPrice()","price()","totalClaimed()","claimedCount()"]
UV=[("priceFor(address,uint256)",[USER,1]),("quote(address,uint256)",[USER,1]),("costFor(address,uint256)",[USER,1]),("freeClaimed(address)",[USER]),("mintedBy(address)",[USER]),("balanceOf(address)",[USER]),("canFreeMint(address)",[USER]),("hasAgentId(address)",[USER]),("mintedAt(uint256)",[1]),("mintedAt(uint256)",[2])]
out={}
for name,addr in [("LEGBEE","0x44a6e69a0b41ee345fa67afee68b0cc90a6ca149"),("WISPAGENT","0x84629f583e7eafba8f5f336b6943e8f23f8ae7bb")]:
    calls=[]; meta=[]
    for sig in VIEWS:
        calls.append({"jsonrpc":"2.0","id":len(calls)+1,"method":"eth_call","params":[{"to":addr,"data":data(sig,[])},"latest"]}); meta.append(sig.split("(")[0])
    for sig,args in UV:
        calls.append({"jsonrpc":"2.0","id":len(calls)+1,"method":"eth_call","params":[{"to":addr,"data":data(sig,args)},"latest"]}); meta.append(sig.split("(")[0]+"_user")
    calls.append({"jsonrpc":"2.0","id":len(calls)+1,"method":"eth_getCode","params":[addr,"latest"]}); meta.append("CODE")
    calls.append({"jsonrpc":"2.0","id":len(calls)+1,"method":"eth_blockNumber","params":[]}); meta.append("BLOCK")
    d={"address":addr}; done=False
    for ep in EPS:
        try:
            res=post(ep,calls)
            if not isinstance(res,list) or len(res)!=len(calls):
                print(name,"ep",ep,"bad shape",str(res)[:100]); continue
            for it,key in zip(res,meta):
                if key=="CODE":
                    code=it.get("result") if isinstance(it,dict) else None
                    d["code_len"]=len(code)//2-1 if code else None
                    d["registry_bytes_in_code"]=(REG in code.lower()) if code else None
                elif key=="BLOCK":
                    d["block"]=to_int(it.get("result")) if isinstance(it,dict) else None
                elif not isinstance(it,dict) or "error" in it or it.get("result") in (None,"0x"):
                    d[key]=None
                else:
                    r=it["result"]
                    d[key]=dec_str(r) if key in ("name","symbol") else (to_int(r[:66]) if len(r)>=66 else r)
            print(name,"OK via",ep); done=True; break
        except Exception as e:
            print(name,"ep",ep,"exc",str(e)[:100]); continue
    d["batch_ok"]=done
    out[name]=d
    print(json.dumps(d,indent=1))
json.dump(out,open("run-2026-11-16-0001-triage2.json","w"),indent=1)
