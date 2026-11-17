#!/usr/bin/env python3
"""Wait approve receipt + re-check floor + preview list(502, 0.005 BNB)."""
import json, subprocess, time
TX="0x4687139e265cb0abfd512242cc6d438a0923334a5036c0067d4aa5e10f5a2bc6"
EPS=["https://bsc-dataseed.binance.org/","https://bsc-dataseed1.bnbchain.org/"]
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
    print(f"poll {i}",flush=True); time.sleep(5)
print("APPROVE RECEIPT block",int(receipt["blockNumber"],16),"status",int(receipt["status"],16),"gasUsed",int(receipt["gasUsed"],16),"gasPrice",receipt.get("effectiveGasPrice"),flush=True)
json.dump({"receipt":receipt},open("run-2026-11-11-0831-verify-approve.json","w"),indent=1)
