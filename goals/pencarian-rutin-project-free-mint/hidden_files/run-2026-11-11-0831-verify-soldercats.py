#!/usr/bin/env python3
"""Verify SOLDERCATS mint tx receipt + post-mint state. Read-only."""
import json, subprocess, time
from Crypto.Hash import keccak
TX="0x94f1f51a13bcf6fec68eb79b42941daab049568de728530332640234c03bed70"
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
SC="0x3D972EBbF7488f21b95250B867e2406c723C9DDC"
EPS=["https://bsc-dataseed.binance.org/","https://bsc-dataseed1.bnbchain.org/","https://bsc-dataseed2.bnbchain.org/"]
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64,"0")
def to_int(v):
    try: return int(v,16) if v not in (None,"0x") else None
    except Exception: return None
def post(ep,payload,timeout=25):
    out=subprocess.run(["curl","-sL","--max-time",str(timeout),"-X","POST",ep,"-H","Content-Type: application/json","-d",json.dumps(payload)],capture_output=True,text=True,timeout=timeout+5).stdout
    return json.loads(out)
receipt=None
for i in range(24):
    for ep in EPS:
        try:
            r=post(ep,{"jsonrpc":"2.0","id":1,"method":"eth_getTransactionReceipt","params":[TX]},timeout=25)
            if r.get("result"): receipt=r["result"]; break
        except Exception: continue
    if receipt: break
    print(f"poll {i}: no receipt yet",flush=True); time.sleep(5)
print("RECEIPT:",json.dumps(receipt),flush=True)
out={"tx":TX,"receipt":receipt}
if receipt:
    blk=int(receipt["blockNumber"],16); gas=int(receipt["gasUsed"],16)
    print("block",blk,"status",int(receipt["status"],16),"gasUsed",gas,flush=True)
    # post-mint state: ownerOf(504), balanceOf, agentFreeUsed, agentFreeByWallet, totalSupply
    tid="00000000000000000000000000000000000000000000000000000000000001f8"
    calls=[
     {"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":SC,"data":sel("ownerOf(uint256)")+tid},"latest"]},
     {"jsonrpc":"2.0","id":2,"method":"eth_call","params":[{"to":SC,"data":sel("balanceOf(address)")+enc(USER)},"latest"]},
     {"jsonrpc":"2.0","id":3,"method":"eth_call","params":[{"to":SC,"data":sel("agentFreeUsed()")},"latest"]},
     {"jsonrpc":"2.0","id":4,"method":"eth_call","params":[{"to":SC,"data":sel("agentFreeByWallet(address)")+enc(USER)},"latest"]},
     {"jsonrpc":"2.0","id":5,"method":"eth_call","params":[{"to":SC,"data":sel("totalSupply()")},"latest"]},
     {"jsonrpc":"2.0","id":6,"method":"eth_call","params":[{"to":SC,"data":sel("claimable(address)")+enc(USER)},"latest"]},
     {"jsonrpc":"2.0","id":7,"method":"eth_blockNumber","params":[]},
    ]
    for ep in EPS:
        try:
            r=post(ep,calls,timeout=25)
            if isinstance(r,list) and len(r)==7:
                out["post"]={"ownerOf_504":("0x"+r[0].get("result","")[-40:]) if r[0].get("result") else None,
                  "balanceOf_user":to_int(r[1].get("result")),"agentFreeUsed":to_int(r[2].get("result")),
                  "agentFreeByWallet_user":to_int(r[3].get("result")),"totalSupply":to_int(r[4].get("result")),
                  "claimable_user":r[5].get("result"),"block":int(r[6]["result"],16)}
                print("POST:",json.dumps(out["post"]),flush=True); break
        except Exception as e: print(ep,"err",e,flush=True)
json.dump(out,open("run-2026-11-11-0831-verify-soldercats.json","w"),indent=1)
