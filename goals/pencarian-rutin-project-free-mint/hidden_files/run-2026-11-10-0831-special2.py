#!/usr/bin/env python3
"""Run 0831 special2: binanceai track-B re-check + NOVA tokenURI + block timestamps. Read-only."""
import json, subprocess, urllib.request
from Crypto.Hash import keccak
EPS=["https://bsc-dataseed1.bnbchain.org/","https://bsc-dataseed2.bnbchain.org/","https://bsc-dataseed.binance.org/"]
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
BIN_MINT="0x46cb1D3efd4307506Cda7EbBa5a51be64746739E"
BIN_TOKEN="0x209173F09aFbCA053C0de9e9763f503e9fb54a3c"
NOVA="0x1b6E6F62528DE674C12BC2C04C159336d3DB049e"
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64,"0")
def toint(v):
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
        elif "(uint256)" in sig: data=sel(sig)+"0"*63+"1"; key=base+"_1"
        else: data=sel(sig); key=base
        calls.append({"jsonrpc":"2.0","id":i+1,"method":"eth_call","params":[{"to":addr,"data":data},"latest"]}); keys.append(key)
    for ep in EPS:
        try:
            res=post(ep,calls)
            if not isinstance(res,list) or len(res)!=len(calls): continue
            return {k:(None if (isinstance(it,dict) and "error" in it) else (toint(it.get("result")) if isinstance(it,dict) else None)) for it,k in zip(res,keys)}
        except Exception: continue
    return None
out={"block":None}
for ep in EPS:
    try:
        r=post(ep,{"jsonrpc":"2.0","id":1,"method":"eth_blockNumber","params":[]})
        out["block"]=int(r["result"],16); break
    except Exception: continue
out["binanceai_mint"]=batch(BIN_MINT,["launched()","failed()","isRefundPhase()","totalShares()","tokenClaimed(address)"])
out["binanceai_token_bal"]=batch(BIN_TOKEN,["balanceOf(address)"])

# block timestamps for interval (prev reread block 132673016 -> this run 132677349)
for b in (132684959, 132689899):
    for ep in EPS:
        try:
            body={"jsonrpc":"2.0","id":1,"method":"eth_getBlockByNumber","params":[hex(b),False]}
            res=post(ep,body)
            out[f"block_{b}_ts"]=int(res["result"]["timestamp"],16)
            break
        except Exception: continue
print(json.dumps(out, indent=1))
json.dump(out, open("run-2026-11-10-0831-special2.json","w"), indent=1)
