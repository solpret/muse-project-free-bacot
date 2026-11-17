#!/usr/bin/env python3
"""WNO mint verification: receipt + balances + free flags (read-only)."""
import json, subprocess, time
from Crypto.Hash import keccak
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
WNO="0x8C969a4CD49E4774908e667702C3d7C3ece164D0"
TX="0xbcaf2ff53785ae3c595d7ccfc9e817404822d9957e91f5ea647b6c7c807712a3"
EPS=["https://bsc-dataseed.binance.org/","https://bsc-dataseed1.bnbchain.org/","https://bsc-dataseed2.bnbchain.org/","https://bsc.nodereal.io/"]
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64,"0")
def rpc(method,params,timeout=25):
    payload={"jsonrpc":"2.0","id":1,"method":method,"params":params}
    for ep in EPS:
        try:
            out=subprocess.run(["curl","-sL","--max-time",str(timeout),"-X","POST",ep,"-H","Content-Type: application/json","-d",json.dumps(payload)],capture_output=True,text=True,timeout=timeout+5).stdout
            r=json.loads(out)
            if "result" in r and r["result"] is not None: return r["result"]
        except Exception: continue
    return None
receipt=None
for i in range(12):
    receipt=rpc("eth_getTransactionReceipt",[TX])
    if receipt: break
    print(f"poll {i}: no receipt yet",flush=True); time.sleep(10)
print("RECEIPT:", json.dumps(receipt)[:800] if receipt else None, flush=True)
def call(data):
    return rpc("eth_call",[{"to":WNO,"data":data},"latest"])
def to_int(v):
    try: return int(v,16) if v and v!="0x" else None
    except Exception: return None
out={}
out["balanceOf_user"]=to_int(call(sel("balanceOf(address)")+enc(USER)))
out["sharesOf_user"]=to_int(call(sel("sharesOf(address)")+enc(USER)))
out["freeUsed_user"]=to_int(call(sel("freeUsed(address)")+enc(USER)))
out["totalFreeShares"]=to_int(call(sel("totalFreeShares()")))
out["totalShares"]=to_int(call(sel("totalShares()")))
print(json.dumps(out,indent=1),flush=True)
json.dump({"tx":TX,"receipt":receipt,"checks":out},open("/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/run-2026-11-10-1431-wno-receipt.json","w"),indent=1)
print("DONE")
