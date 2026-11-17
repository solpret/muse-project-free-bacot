#!/usr/bin/env python3
"""Leg 3 on-chain fast check for S1 sale 0xDDc2352d... (track-C shape)."""
import json, subprocess
from Crypto.Hash import keccak
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EP="https://bsc.nodereal.io/"
ADDR="0xDDc2352d1ceC10b42e05A297232f5328902C6c2C"
def sel(sig):
    k=keccak.new(digest_bits=256); k.update(sig.encode()); return "0x"+k.hexdigest()[:8]
def enc_addr(a): return a.lower().replace("0x","").rjust(64,"0")
def enc_uint(n): return format(n,"064x")
CALLS=[("name","name()","str"),("symbol","symbol()","str"),("decimals","decimals()","uint"),
 ("TOTAL_SUPPLY","TOTAL_SUPPLY()","uint"),("FREE_SHARES","FREE_SHARES()","uint"),
 ("PAID_SHARES","PAID_SHARES()","uint"),("TOTAL_SHARES","TOTAL_SHARES()","uint"),
 ("freeClaimed","freeClaimed()","uint"),("freeClaimedBy_user","freeClaimedBy(address)","bool"),
 ("remainingShares","remainingShares()","uint"),("sharesSold","sharesSold()","uint"),
 ("soldOut","soldOut()","bool"),("launch","launch()","bool"),
 ("startTime","startTime()","uint"),("deadline","deadline()","uint"),
 ("launchBlock","launchBlock()","uint"),("mintCost1","mintCost(uint256)","uint"),
 ("owner","owner()","addr"),("registry","registry()","addr"),
 ("TOKENS_PER_SHARE","TOKENS_PER_SHARE()","uint"),("totalSupply","totalSupply()","uint"),
 ("tradingOpen","tradingOpen()","bool"),("raised","raised()","uint")]
jobs=[]
for name,sig,kind in CALLS:
    if sig.endswith("(address)"): data=sel(sig)+enc_addr(USER)
    elif sig.endswith("(uint256)"): data=sel(sig)+enc_uint(1)
    else: data=sel(sig)
    jobs.append((name,data,kind))
payload=json.dumps([{"jsonrpc":"2.0","id":j,"method":"eth_call","params":[{"to":ADDR,"data":d},"latest"]} for j,(_,d,_) in enumerate(jobs)])
pr=None
for _try in range(3):
    pr=subprocess.run(["curl","-s","--max-time","30","-X","POST",EP,"-H","Content-Type: application/json","--data",payload],capture_output=True,text=True)
    if pr.stdout.strip(): break
    import time as _t; _t.sleep(2)
if not pr.stdout.strip():
    raise SystemExit("RPC batch returned empty after 3 tries")
resps=json.loads(pr.stdout)
if isinstance(resps,dict): resps=[resps]
out={}
for (name,_,kind),r in zip(jobs,resps):
    raw=r.get("result") if isinstance(r,dict) else None
    v=None
    if isinstance(raw,str) and raw.startswith("0x"):
        try:
            if kind=="uint": v=int(raw,16)
            elif kind=="bool": v=int(raw,16)!=0
            elif kind=="addr": v="0x"+raw[-40:]
            elif kind=="str":
                # abi string: offset(32B) + len(32B) + data
                ln=int(raw[66:130],16); v=bytes.fromhex(raw[130:130+ln*2]).decode("utf-8","ignore")
        except Exception as e: v=f"DECODE-ERR {e}"
    else:
        v=f"RPC-ERR {r}"
    out[name]=v
# block number
pb=subprocess.run(["curl","-s","--max-time","15","-X","POST",EP,"-H","Content-Type: application/json","--data",'{"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}'],capture_output=True,text=True)
try: block=int(json.loads(pb.stdout)["result"],16)
except Exception: block=None
json.dump({"block":block,"values":out}, open(BASE+"hot-leg-2026-11-11-0859-ddc2.json","w"), indent=1)
print("block:",block); print(json.dumps(out,indent=1))
