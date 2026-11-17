#!/usr/bin/env python3
"""SEVEN fresh deep read for run 0231: age (mintOpensAt), free cap, slot, gate views. Read-only."""
import json, subprocess
from Crypto.Hash import keccak
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
SEVEN="0xFf65cf70a15fA0B06Bf8D8ED020Cf9F917C80f96"
EPS=["https://bsc-dataseed.binance.org/","https://bsc-dataseed1.bnbchain.org/","https://bsc-dataseed2.bnbchain.org/"]
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64,"0")
def to_int(v):
    try: return int(v,16) if v and v!="0x" else None
    except Exception: return None
def post_rpc(ep,payload,timeout=25):
    out=subprocess.run(["curl","-sL","--max-time",str(timeout),"-X","POST",ep,"-H","Content-Type: application/json","-d",json.dumps(payload)],capture_output=True,text=True,timeout=timeout+5).stdout
    return json.loads(out)
def raw_batch(addr,views,raw=False):
    calls,keys=[],[]
    for i,sig in enumerate(views):
        base=sig.split("(")[0]
        if "(address)" in sig: data=sel(sig)+enc(USER); key=base+"_user"
        else: data=sel(sig); key=base
        calls.append({"jsonrpc":"2.0","id":i+1,"method":"eth_call","params":[{"to":addr,"data":data},"latest"]})
        keys.append(key)
    for ep in EPS:
        try:
            res=post_rpc(ep,calls,timeout=25)
            if not isinstance(res,list) or len(res)!=len(calls): continue
            if raw:
                return {key:(it.get("result") if isinstance(it,dict) else None) for it,key in zip(res,keys)}
            return {key:(None if (isinstance(it,dict) and "error" in it) else (to_int(it.get("result")) if isinstance(it,dict) else None)) for it,key in zip(res,keys)}
        except Exception: continue
    return None
def get_block():
    for ep in EPS:
        try:
            r=post_rpc(ep,{"jsonrpc":"2.0","id":1,"method":"eth_blockNumber","params":[]},timeout=25)
            return int(r["result"],16)
        except Exception: continue
    return None
VIEWS=["mintOpensAt()","mintStart()","mintOpenedAt()","FREE_CAP()","FREE_SUPPLY()","freeSupply()","freeMinted()","totalMinted()","totalSupply()","mintOpen()","freeCountBy(address)","holdsAgentId(address)","balanceOf(address)","freeClaimed(address)","freeMintedBy(address)"]
out={"block":get_block(),"seven":raw_batch(SEVEN,VIEWS)}
out["seven_raw"]={k:raw_batch(SEVEN,[k+"()" if "(address)" not in k else k],raw=True) for k in ("contractURI","tokenURI")}
print(json.dumps(out,indent=1))
json.dump(out,open(BASE+"run-2026-11-12-0231-seven.json","w"),indent=1)
