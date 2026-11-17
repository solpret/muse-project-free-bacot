#!/usr/bin/env python3
"""Diagnose list(502, 0.005) revert: static call + approval + floor re-read. Read-only."""
import json, subprocess
from Crypto.Hash import keccak
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
RC="0x39b451abbd53365e2277084cb60f9a2c5ad6e698"
MK="0xfb414d2288536f35eea77ba996effddb85e07574"
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
tid="00000000000000000000000000000000000000000000000000000000000001f6"
price="0000000000000000000000000000000000000000000000000000000011c37937e08000"
list_data=sel("list(uint256,uint256)")+tid+price
calls=[
 {"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"from":USER,"to":MK,"data":list_data,"value":"0x0"},"latest"]},
 {"jsonrpc":"2.0","id":2,"method":"eth_call","params":[{"to":RC,"data":sel("getApproved(uint256)")+tid},"latest"]},
 {"jsonrpc":"2.0","id":3,"method":"eth_call","params":[{"to":MK,"data":sel("listings(uint256)")+tid},"latest"]},
 {"jsonrpc":"2.0","id":4,"method":"eth_call","params":[{"to":MK,"data":sel("listedCount()")},"latest"]},
 {"jsonrpc":"2.0","id":5,"method":"eth_call","params":[{"to":MK,"data":sel("isValid(uint256)")+tid},"latest"]},
 {"jsonrpc":"2.0","id":6,"method":"eth_blockNumber","params":[]},
]
for ep in EPS:
    try:
        r=post(ep,calls,timeout=25)
        if isinstance(r,list) and len(r)==6:
            print("static list(502,0.005):", json.dumps(r[0]),flush=True)
            print("getApproved(502):",("0x"+r[1].get("result","")[-40:]) if r[1].get("result") else None,flush=True)
            print("listings(502) raw:",r[2].get("result"),flush=True)
            print("listedCount:",to_int(r[3].get("result")),"| isValid(502):",to_int(r[4].get("result")),"| block:",int(r[5]["result"],16),flush=True)
            json.dump({"static_list":r[0],"getApproved":r[1].get("result"),"listings502":r[2].get("result"),"listedCount":to_int(r[3].get("result")),"isValid502":to_int(r[4].get("result")),"block":int(r[5]["result"],16)},open("run-2026-11-11-0831-list-diag.json","w"),indent=1)
            break
    except Exception as e: print(ep,"err",e,flush=True)
