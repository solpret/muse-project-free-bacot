#!/usr/bin/env python3
"""Age sweep run 0831: live-verify the 4 early-leads queued by run 0801
(Alchemister, BotWar Arena Test, ONI-d576, KIJIN) + pull prev rates for movers.
Read-only batch eth_call via bsc-dataseed."""
import json, subprocess, time
from eth_hash.auto import keccak
HF="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
RPC_URL="https://bsc-dataseed.binance.org/"
def sel(sig): return keccak(sig.encode())[:4].hex()
def enc_addr(a): return "0"*24+a[2:].lower()
def encode(sig, arg):
    d="0x"+sel(sig)
    if arg=="user": d+=enc_addr("0xeb237F6f9FB4e826739F0954e9768914F28b2c2E")
    return d
def curl_json(url, payload, timeout=25):
    r=subprocess.run(["curl","-s","-L","--max-time",str(timeout),url,"-H","Content-Type: application/json","-d",json.dumps(payload)],capture_output=True,timeout=timeout+5)
    return json.loads(r.stdout.decode())
def rpc_batch(calls, timeout=25):
    payload=[{"jsonrpc":"2.0","id":i+1,"method":"eth_call","params":[{"to":to,"data":data},"latest"]} for i,(to,data) in enumerate(calls)]
    resp=curl_json(RPC_URL,payload,timeout=timeout)
    by_id={it["id"]:it for it in resp if isinstance(it,dict)}
    res=[]
    for i in range(len(calls)):
        it=by_id.get(i+1,{})
        if "result" in it and it["result"] not in (None,"0x"):
            try: res.append(int(it["result"],16))
            except Exception: res.append(it["result"])
        elif "error" in it: res.append(f"err:{it['error']}")
        else: res.append(None)
    return res
PLAN=[
 ("Alchemister","0x69037Db8C6f237eCd9aB4B364D65C6dD05825dCb",["totalSupply()","MAX_SUPPLY()","maxSupply()","mintOpen()","freeMinted()","freeClaimed()","freeLeft()"]),
 ("BotWar Arena Test","0x25eCD3B84D8F9D76eb38AA9C6fb10581aE30Dc48",["totalSupply()","totalMinted()","MAX_SUPPLY()","mintOpen()"]),
 ("ONI-d576","0xd576F638b5eF8906C13CE9Ca534113DdBd0a9038",["totalMinted()","totalSupply()","freeMinted()","FREE_POOL()","MAX_SUPPLY()","mintOpen()"]),
 ("KIJIN","0x625188954784D2f8c542FE8206050fF540Ae3B20",["totalMinted()","totalSupply()","freeMinted()","freeRemaining()","MAX_SUPPLY()","mintOpen()"]),
]
calls,meta=[],[]
for name,addr,sigs in PLAN:
    for sig in sigs:
        calls.append((addr,encode(sig,None))); meta.append((name,addr,sig))
res=rpc_batch(calls)
out={"reads":{},"block":None}
for (name,addr,sig),val in zip(meta,res):
    out["reads"].setdefault(name,{"address":addr,"views":{}})[ "views"][sig]=val
try:
    blk=curl_json(RPC_URL,[{"jsonrpc":"2.0","id":1,"method":"eth_blockNumber","params":[]}])
    out["block"]=int(blk[0]["result"],16)
except Exception as e:
    out["block"]=f"error: {e}"
json.dump(out,open(f"{HF}/run-2026-11-18-0831-agesweep.json","w"),indent=1)
print(json.dumps(out,indent=1))
