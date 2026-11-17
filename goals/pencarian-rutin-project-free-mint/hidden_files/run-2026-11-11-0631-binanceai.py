#!/usr/bin/env python3
"""Track-B binanceai.fun re-check run 0401. Read-only."""
import json, subprocess
from Crypto.Hash import keccak
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
MINT="0x46cb1D3efd4307506Cda7EbBa5a51be64746739E"
TOKEN="0x209173F09aFbCA053C0de9e9763f503e9fb54a3c"
EPS=["https://bsc-dataseed.binance.org/","https://bsc-dataseed1.bnbchain.org/"]
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64,"0")
def to_int(v):
    try: return int(v,16) if v not in (None,"0x") else None
    except Exception: return None
def post(ep,payload,timeout=25):
    out=subprocess.run(["curl","-sL","--max-time",str(timeout),"-X","POST",ep,"-H","Content-Type: application/json","-d",json.dumps(payload)],capture_output=True,text=True,timeout=timeout+5).stdout
    return json.loads(out)
calls=[
 {"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":MINT,"data":sel("launched()")},"latest"]},
 {"jsonrpc":"2.0","id":2,"method":"eth_call","params":[{"to":MINT,"data":sel("tokenClaimed(address)")+enc(USER)},"latest"]},
 {"jsonrpc":"2.0","id":3,"method":"eth_call","params":[{"to":TOKEN,"data":sel("balanceOf(address)")+enc(USER)},"latest"]},
 {"jsonrpc":"2.0","id":4,"method":"eth_blockNumber","params":[]},
]
for ep in EPS:
    try:
        r=post(ep,calls,timeout=25)
        if isinstance(r,list) and len(r)==4:
            print("launched:",to_int(r[0].get("result")),"| tokenClaimed(user):",to_int(r[1].get("result")),"| TOKEN balanceOf(user):",to_int(r[2].get("result")),"| block:",int(r[3]["result"],16),flush=True)
            json.dump({"launched":to_int(r[0].get("result")),"tokenClaimed_user":to_int(r[1].get("result")),"token_balance_user":to_int(r[2].get("result")),"block":int(r[3]["result"],16)},open("run-2026-11-11-0631-binanceai.json","w"),indent=1)
            break
    except Exception as e: print(ep,"err",e,flush=True)
