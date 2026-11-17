#!/usr/bin/env python3
"""Verify RIMEVAULT mint tx receipt + ownership + free counters. Read-only."""
import json, subprocess, time
from Crypto.Hash import keccak
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TX="0x7f3a84186785ac1ec9b414ddfff06a2a7a4029bf6bdfa8dcc4c0fab5517ecc2e"
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
ADDR="0xb1636010fb87f50574f76f6644b7cd306a6a4d1f"
EPS=["https://bsc-dataseed.binance.org/","https://bsc-dataseed1.bnbchain.org/","https://bsc-dataseed2.bnbchain.org/"]
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64,"0")
def post(ep,payload,timeout=25):
    out=subprocess.run(["curl","-sL","--max-time",str(timeout),"-X","POST",ep,"-H","Content-Type: application/json","-d",json.dumps(payload)],capture_output=True,text=True,timeout=timeout+5).stdout
    return json.loads(out)
receipt=None
for attempt in range(12):
    for ep in EPS:
        try:
            r=post(ep,{"jsonrpc":"2.0","id":1,"method":"eth_getTransactionReceipt","params":[TX]},timeout=25)
            if r.get("result"): receipt=r["result"]; break
        except Exception: continue
    if receipt: break
    print(f"attempt {attempt+1}: receipt not yet available, waiting 10s",flush=True)
    time.sleep(10)
print("RECEIPT:",json.dumps(receipt,indent=1) if receipt else "NONE after 12 attempts",flush=True)
if receipt:
    print("status:",receipt.get("status"),"| block:",int(receipt.get("blockNumber","0x0"),16),"| gasUsed:",int(receipt.get("gasUsed","0x0"),16),"| from:",receipt.get("from"),"| to:",receipt.get("to"),flush=True)
    # verify ownership + counters
    calls=[
      {"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":ADDR,"data":sel("ownerOf(uint256)")+"0"*60+"01fc"},"latest"]},
      {"jsonrpc":"2.0","id":2,"method":"eth_call","params":[{"to":ADDR,"data":sel("balanceOf(address)")+enc(USER)},"latest"]},
      {"jsonrpc":"2.0","id":3,"method":"eth_call","params":[{"to":ADDR,"data":sel("agentFreeUsed()")},"latest"]},
      {"jsonrpc":"2.0","id":4,"method":"eth_call","params":[{"to":ADDR,"data":sel("agentFreeByWallet(address)")+enc(USER)},"latest"]},
      {"jsonrpc":"2.0","id":5,"method":"eth_call","params":[{"to":ADDR,"data":sel("totalSupply()")},"latest"]},
      {"jsonrpc":"2.0","id":6,"method":"eth_blockNumber","params":[]},
    ]
    for ep in EPS:
        try:
            res=post(ep,calls,timeout=25)
            if isinstance(res,list) and len(res)==6:
                print("ownerOf(504):",res[0].get("result"),flush=True)
                print("balanceOf(user):",int(res[1]["result"],16) if res[1].get("result") else None,flush=True)
                print("agentFreeUsed:",int(res[2]["result"],16) if res[2].get("result") else None,flush=True)
                print("agentFreeByWallet(user):",int(res[3]["result"],16) if res[3].get("result") else None,flush=True)
                print("totalSupply:",int(res[4]["result"],16) if res[4].get("result") else None,flush=True)
                print("block:",int(res[5]["result"],16) if res[5].get("result") else None,flush=True)
                json.dump({"receipt":receipt,"verify":res},open(f"{BASE}/run-2026-11-11-0401-mycelix-verify.json","w"),indent=1)
                break
        except Exception as e:
            print("verify err",ep,e,flush=True)
