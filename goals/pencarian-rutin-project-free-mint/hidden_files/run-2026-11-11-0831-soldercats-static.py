#!/usr/bin/env python3
"""Static eth_call test: SOLDERCATS mint(1) value 0 from agent wallet + walletInfo. Read-only."""
import json, subprocess
from Crypto.Hash import keccak
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
SC="0x3D972EBbF7488f21b95250B867e2406c723C9DDC"
EPS=["https://bsc-dataseed.binance.org/","https://bsc-dataseed1.bnbchain.org/","https://bsc-dataseed2.bnbchain.org/"]
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64,"0")
def post(ep,payload,timeout=25):
    out=subprocess.run(["curl","-sL","--max-time",str(timeout),"-X","POST",ep,"-H","Content-Type: application/json","-d",json.dumps(payload)],capture_output=True,text=True,timeout=timeout+5).stdout
    return json.loads(out)
# mint(1) data
mint_data = sel("mint(uint256)") + "0000000000000000000000000000000000000000000000000000000000000001"
calls=[
 {"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"from":USER,"to":SC,"data":mint_data,"value":"0x0"},"latest"]},
 {"jsonrpc":"2.0","id":2,"method":"eth_call","params":[{"to":SC,"data":sel("walletInfo(address)")+enc(USER)},"latest"]},
 {"jsonrpc":"2.0","id":3,"method":"eth_call","params":[{"to":SC,"data":sel("claimable(address)")+enc(USER)},"latest"]},
 {"jsonrpc":"2.0","id":4,"method":"eth_blockNumber","params":[]},
]
for ep in EPS:
    try:
        r=post(ep,calls,timeout=25)
        if isinstance(r,list) and len(r)==4:
            print("mint(1) value0 from agent:", json.dumps(r[0]),flush=True)
            print("walletInfo(user):", r[1].get("result"),flush=True)
            print("claimable(user):", r[2].get("result"),flush=True)
            print("block:", int(r[3]["result"],16),flush=True)
            json.dump({"mint1_static":r[0],"walletInfo":r[1].get("result"),"claimable":r[2].get("result"),"block":int(r[3]["result"],16)},open("run-2026-11-11-0831-soldercats-static.json","w"),indent=1)
            break
    except Exception as e: print(ep,"err",e,flush=True)
