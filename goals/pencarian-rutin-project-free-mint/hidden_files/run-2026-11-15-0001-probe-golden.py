#!/usr/bin/env python3
"""Probe GoldenAgents 0x4233... (sweep re-found run 0001; already age-excluded 11 Nov + gate-failed 14 Nov).
Fresh totalSupply/publicMinted/mintActive to confirm no new mint phase. Read-only."""
import json, subprocess
from Crypto.Hash import keccak
ADDR="0x4233c62919cc03168a361c547117c1553c375bfc"
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
calls=[]
for i,sig in enumerate(["totalSupply()","publicMinted()","mintActive()","mintedBy(address)","balanceOf(address)"]):
    data=sel(sig)
    if "address" in sig:
        data+="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"[2:].lower().rjust(64,"0")
    calls.append({"jsonrpc":"2.0","id":i+1,"method":"eth_call","params":[{"to":ADDR,"data":data},"latest"]})
for ep in ["https://bsc-dataseed.binance.org/","https://bsc-dataseed1.bnbchain.org/"]:
    try:
        out=subprocess.run(["curl","-sL","--max-time","60","-X","POST",ep,"-H","Content-Type: application/json","-d",json.dumps(calls)],capture_output=True,text=True,timeout=70).stdout
        res=json.loads(out)
        if isinstance(res,list) and len(res)==len(calls):
            vals=[]
            for r in res:
                v=r.get("result")
                vals.append(int(v,16) if v and v!="0x" and "error" not in r else None)
            print(json.dumps({"via":ep,"totalSupply":vals[0],"publicMinted":vals[1],"mintActive":vals[2],"mintedBy_user":vals[3],"balanceOf_user":vals[4]}))
            break
    except Exception as e:
        print("ep fail",ep,str(e)[:100])
