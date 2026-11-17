#!/usr/bin/env python3
"""Check getApproved(502) on REWINDCLUB + isApprovedForAll. Read-only."""
import json, subprocess
from Crypto.Hash import keccak
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
RC="0x39b451abbd53365e2277084cb60f9a2c5ad6e698"
MK="0xfb414d2288536f35eea77ba996effddb85e07574"
EPS=["https://bsc-dataseed.binance.org/","https://bsc-dataseed1.bnbchain.org/"]
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64,"0")
def post(ep,payload,timeout=25):
    out=subprocess.run(["curl","-sL","--max-time",str(timeout),"-X","POST",ep,"-H","Content-Type: application/json","-d",json.dumps(payload)],capture_output=True,text=True,timeout=timeout+5).stdout
    return json.loads(out)
tid="00000000000000000000000000000000000000000000000000000000000001f6"
calls=[
 {"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":RC,"data":sel("getApproved(uint256)")+tid},"latest"]},
 {"jsonrpc":"2.0","id":2,"method":"eth_call","params":[{"to":RC,"data":sel("isApprovedForAll(address,address)")+enc(USER)+enc(MK)},"latest"]},
 {"jsonrpc":"2.0","id":3,"method":"eth_blockNumber","params":[]}]
for ep in EPS:
    try:
        r=post(ep,calls,timeout=25)
        if isinstance(r,list) and len(r)==3:
            print("getApproved(502):",("0x"+r[0].get("result","")[-40:]) if r[0].get("result") else None,"| isApprovedForAll:",r[1].get("result"),"| block:",int(r[2]["result"],16),flush=True)
            json.dump({"getApproved_502":("0x"+r[0].get("result","")[-40:]) if r[0].get("result") else None,"isApprovedForAll":r[1].get("result"),"block":int(r[2]["result"],16)},open("run-2026-11-11-0831-rewind-approve-check.json","w"),indent=1)
            break
    except Exception as e: print(ep,"err",e,flush=True)
