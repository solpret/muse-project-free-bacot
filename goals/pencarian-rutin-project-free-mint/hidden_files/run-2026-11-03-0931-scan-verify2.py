#!/usr/bin/env python3
import json, sys
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from fast_rpc import _single
from ankr import ankr_post
from Crypto.Hash import keccak
EPS=["https://bsc-dataseed.binance.org/","https://bsc-dataseed1.bnbchain.org/"]
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64,"0")
def call(to,data):
    for ep in EPS:
        try:
            v=_single(ep,"eth_call",[{"to":to,"data":data},"latest"],8,retries=0); return v
        except Exception: pass
    return None
def iv(v):
    try: return int(v,16) if v else None
    except Exception: return None
SH="0xD0624b7cED1B822BCa6359302c375D8EF700a7fe"
for fn,arg in [("freeClaimed(address)",enc(USER)),("freeCount()",""),("mintedCount()",""),("mintStatus()",""),("totalSupply()",""),("mintedBy(address)",enc(USER))]:
    print("Shroomlets",fn,iv(call(SH,sel(fn)+arg)),flush=True)
TRANSFER="0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO="0x"+"00"*32
for n,a in [("SynthMinds","0x36E655717BA3fB01268b6069a88Cc5D4a982EA15"),("Shroomlets",SH)]:
    try:
        body=ankr_post("ankr_getLogs", {"blockchain":"bsc","fromBlock":hex(131350347),"toBlock":hex(131352346),"address":a,"pageSize":1000,"decodeLogs":False,"topics":[TRANSFER,ZERO]}, timeout=30)
        res=body.get("result",body) if isinstance(body,dict) else body
        logs=res.get("logs",[]) if isinstance(res,dict) else []
        print(n,"prewindow2 131350347-131352346 mints",len(logs),flush=True)
    except Exception as e: print(n,"prewindow2 ERROR",str(e)[:160],flush=True)
