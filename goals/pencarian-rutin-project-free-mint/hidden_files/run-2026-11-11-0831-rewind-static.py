#!/usr/bin/env python3
"""Static eth_call: REWINDCLUB mint(1) value 0 from agent wallet. Read-only."""
import json, subprocess
from Crypto.Hash import keccak
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
RC="0x39b451abbd53365e2277084cb60f9a2c5ad6e698"
EPS=["https://bsc-dataseed.binance.org/","https://bsc-dataseed1.bnbchain.org/"]
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def post(ep,payload,timeout=25):
    out=subprocess.run(["curl","-sL","--max-time",str(timeout),"-X","POST",ep,"-H","Content-Type: application/json","-d",json.dumps(payload)],capture_output=True,text=True,timeout=timeout+5).stdout
    return json.loads(out)
mint_data = sel("mint(uint256)") + "0000000000000000000000000000000000000000000000000000000000000001"
calls=[{"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"from":USER,"to":RC,"data":mint_data,"value":"0x0"},"latest"]},
       {"jsonrpc":"2.0","id":2,"method":"eth_blockNumber","params":[]}]
for ep in EPS:
    try:
        r=post(ep,calls,timeout=25)
        if isinstance(r,list) and len(r)==2:
            print("mint(1) value0 from agent:", json.dumps(r[0]), "| block:", int(r[1]["result"],16),flush=True)
            json.dump({"mint1_static":r[0],"block":int(r[1]["result"],16)},open("run-2026-11-11-0831-rewind-static.json","w"),indent=1)
            break
    except Exception as e: print(ep,"err",e,flush=True)
