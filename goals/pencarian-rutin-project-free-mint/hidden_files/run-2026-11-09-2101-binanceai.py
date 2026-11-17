#!/usr/bin/env python3
"""Track-B binanceai.fun probe run 2101. Read-only."""
import json, urllib.request
from Crypto.Hash import keccak
RPCS=["https://bsc-dataseed1.bnbchain.org","https://bsc-dataseed2.bnbchain.org","https://bsc-dataseed.binance.org"]
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
MINT="0x46cb1D3efd4307506Cda7EbBa5a51be64746739E"
TOKEN="0x209173F09aFbCA053C0de9e9763f503e9fb54a3c"
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64,"0")
def rpc(method,params):
    for u in RPCS:
        try:
            body=json.dumps({"jsonrpc":"2.0","id":1,"method":method,"params":params}).encode()
            req=urllib.request.Request(u,data=body,headers={"Content-Type":"application/json"})
            with urllib.request.urlopen(req,timeout=15) as r: out=json.load(r)
            if "error" in out: continue
            return out["result"]
        except Exception: continue
    return None
def call(addr,sig,args=""):
    v=rpc("eth_call",[{"to":addr,"data":sel(sig)+args},"latest"])
    if v is None or v=="0x": return None
    try: return int(v,16)
    except Exception: return v
blk=rpc("eth_blockNumber",[])
out={"block":int(blk,16) if blk else None,
 "launched":call(MINT,"launched()"),"failed":call(MINT,"failed()"),
 "isRefundPhase":call(MINT,"isRefundPhase()"),"totalShares":call(MINT,"totalShares()"),
 "tokenClaimed_user":call(MINT,"tokenClaimed(address)",enc(USER)),
 "tokenBalance_user":call(TOKEN,"balanceOf(address)",enc(USER))}
print(json.dumps(out,indent=1))
json.dump(out,open("run-2026-11-09-2101-binanceai.json","w"),indent=1)
