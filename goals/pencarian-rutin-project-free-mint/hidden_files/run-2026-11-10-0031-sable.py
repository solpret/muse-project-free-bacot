#!/usr/bin/env python3
"""Sable Agent 0x23d35617 probe — read-only, curl transport."""
import json, subprocess
from Crypto.Hash import keccak
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
ADDR="0x23d356173ff227d5bf6d622f4a8907f208871d76"
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
VIEWS=["totalSupply()","totalMinted()","freeClaimed()","freeMinted()","paidMinted()",
 "FREE_SUPPLY()","MAX_SUPPLY()","mintOpen()","mintStart()","START_TIME()","startTime()",
 "MINT_START()","freePerWallet()","FREE_PER_WALLET()","mintPrice()","PRICE()","owner()",
 "agentId()","balanceOf(address)","freeClaimed(address)","freeMintedBy(address)","name()","symbol()"]
def post(ep,payload,timeout=25):
    out=subprocess.run(["curl","-sL","--max-time",str(timeout),"-X","POST",ep,"-H","Content-Type: application/json","-d",json.dumps(payload)],capture_output=True,text=True,timeout=timeout+5).stdout
    return json.loads(out)
calls=[];keys=[]
for i,sig in enumerate(VIEWS):
    base=sig.split("(")[0]
    if "(address)" in sig:
        data=sel(sig)+enc(USER); key=base+"_user"
    else:
        data=sel(sig); key=base
    calls.append({"jsonrpc":"2.0","id":i+1,"method":"eth_call","params":[{"to":ADDR,"data":data},"latest"]})
    keys.append(key)
blk=None
for ep in EPS:
    try:
        r=post(ep,{"jsonrpc":"2.0","id":1,"method":"eth_blockNumber","params":[]})
        blk=int(r["result"],16); break
    except Exception: continue
out={"block":blk}
for ep in EPS:
    try:
        res=post(ep,calls)
        if not isinstance(res,list) or len(res)!=len(calls): continue
        for item,key in zip(res,keys):
            out[key]=None if (isinstance(item,dict) and "error" in item) else (to_int(item.get("result")) if isinstance(item,dict) else None)
        break
    except Exception: continue
print(json.dumps(out,indent=1))
json.dump(out,open(f"{BASE}/run-2026-11-10-0031-sable.json","w"),indent=1)
