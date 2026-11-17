#!/usr/bin/env python3
"""Triage LEGBEE + WISPAGENT via SINGLE eth_call/eth_getCode (batch path degraded). Read-only."""
import json, subprocess, time
from Crypto.Hash import keccak
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EP="https://bsc-dataseed.binance.org/"
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
def rpc(method,params,timeout=30):
    for attempt in range(3):
        try:
            out=subprocess.run(["curl","-sL","--max-time",str(timeout),"-X","POST",EP,"-H","Content-Type: application/json","-d",json.dumps({"jsonrpc":"2.0","id":1,"method":method,"params":params})],capture_output=True,text=True,timeout=timeout+10).stdout
            j=json.loads(out)
            if isinstance(j,dict) and "result" in j: return j["result"]
            if isinstance(j,dict) and "error" in j: return {"error":j["error"]}
        except Exception as e:
            time.sleep(2); continue
    return None
def to_int(v):
    try: return int(v,16) if v and v!="0x" else None
    except Exception: return None
def dec_str(v):
    if not v or len(v)<130: return None
    try:
        b=bytes.fromhex(v[2:]); ln=int.from_bytes(b[64:96],'big')
        return b[96:96+ln].decode('utf-8',errors='ignore')
    except Exception: return None
VIEWS=["totalSupply()","totalMinted()","mintOpen()","mintActive()","MAX_SUPPLY()","FREE_SUPPLY()","FREE_CAP()","FREE_MAX()","freeMinted()","freeClaimed()","freeSupply()","freeLeft()","freeRemaining()","owner()","AGENT_ID()","agentRegistry()","name()","symbol()","mintPrice()","mintStart()","startTime()","mintStartTime()","launchTime()"]
UV=[("priceFor(address,uint256)",[USER,1]),("quote(address,uint256)",[USER,1]),("costFor(address,uint256)",[USER,1]),("freeClaimed(address)",[USER]),("mintedBy(address)",[USER]),("balanceOf(address)",[USER]),("canFreeMint(address)",[USER]),("hasAgentId(address)",[USER]),("mintedAt(uint256)",[1])]
out={"block":to_int(rpc("eth_blockNumber",[]))}
for name,addr in [("LEGBEE","0x44a6e69a0b41ee345fa67afee68b0cc90a6ca149"),("WISPAGENT","0x84629f583e7eafba8f5f336b6943e8f23f8ae7bb")]:
    d={"address":addr}
    code=rpc("eth_getCode",[addr,"latest"])
    if isinstance(code,str):
        d["code_len"]=len(code)//2-1
        d["registry_bytes_in_code"]=REG in code.lower()
        # selectors present (first 4 bytes after 0x6080... dispatcher): list function selectors from code
        import re
        sels=sorted(set(re.findall(r'63([0-9a-f]{8})',code.lower())))
        d["selectors"]=sels
    else:
        d["code_error"]=str(code)[:200]
    for sig in VIEWS:
        key=sig.split("(")[0]
        r=rpc("eth_call",[{"to":addr,"data":data(sig,[])},"latest"])
        if isinstance(r,str) and r not in (None,"0x"):
            d[key]=dec_str(r) if key in ("name","symbol") else (to_int(r[:66]) if len(r)>=66 else r)
        else: d[key]=None
    for sig,args in UV:
        key=sig.split("(")[0]+"_user"
        r=rpc("eth_call",[{"to":addr,"data":data(sig,args)},"latest"])
        if isinstance(r,str) and r not in (None,"0x"):
            d[key]=to_int(r[:66]) if len(r)>=66 else r
        else: d[key]=None
    out[name]=d
    print(json.dumps(d,indent=1),flush=True)
json.dump(out,open("run-2026-11-16-0001-triage3.json","w"),indent=1)
