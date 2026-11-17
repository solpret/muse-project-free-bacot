#!/usr/bin/env python3
"""REWINDCLUB own-market state. Read-only."""
import json, subprocess
from Crypto.Hash import keccak
MK="0xfb414d2288536f35eea77ba996effddb85e07574"
EPS=["https://bsc-dataseed.binance.org/","https://bsc-dataseed1.bnbchain.org/"]
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def to_int(v):
    try: return int(v,16) if v not in (None,"0x") else None
    except Exception: return None
def post(ep,payload,timeout=25):
    out=subprocess.run(["curl","-sL","--max-time",str(timeout),"-X","POST",ep,"-H","Content-Type: application/json","-d",json.dumps(payload)],capture_output=True,text=True,timeout=timeout+5).stdout
    return json.loads(out)
def batch(addr, views):
    calls=[{"jsonrpc":"2.0","id":i+1,"method":"eth_call","params":[{"to":addr,"data":sel(sig)},"latest"]} for i,(sig,) in enumerate(views)]
    for ep in EPS:
        try:
            r=post(ep,calls,timeout=25)
            if isinstance(r,list) and len(r)==len(calls):
                return [it.get("result") if isinstance(it,dict) and "error" not in it else None for it in r]
        except Exception: continue
    return [None]*len(views)
r=batch(MK,[("listedCount()",),("FEE_BPS()",),("NFT()",)])
print("listedCount:",to_int(r[0]),"| FEE_BPS:",to_int(r[1]),"| NFT:",("0x"+r[2][-40:]) if r[2] else None,flush=True)
json.dump({"listedCount":to_int(r[0]),"FEE_BPS":to_int(r[1]),"NFT":("0x"+r[2][-40:]) if r[2] else None},open("run-2026-11-11-0831-rewind-market.json","w"),indent=1)
