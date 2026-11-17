#!/usr/bin/env python3
"""Run 2131: track-B binanceai re-check (read-only)."""
import json, sys
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import batch
from Crypto.Hash import keccak
MINT="0x46cb1D3efd4307506Cda7EbBa5a51be64746739E"
TOKEN="0x209173F09aFbCA053C0de9e9763f503e9fb54a3c"
PAIR="0x903ACC22B9BABCD427bfb9AF2C27a27a5aC7c698"
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS=["https://bsc-dataseed1.bnbchain.org/","https://bsc.publicnode.com/"]
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64,"0")
def to_int(v):
    try: return int(v,16)
    except Exception: return None
def single(ep,addr,sig,arg=None):
    data=sel(sig)+(enc(arg) if arg else "")
    return batch([("eth_call",[{"to":addr,"data":data},"latest"])],endpoint=ep,timeout=12)[0]
ep=EPS[0]
out={}
try: out["block"]=int(batch([("eth_blockNumber",[])],endpoint=ep,timeout=10)[0],16)
except Exception:
    ep=EPS[1]; out["block"]=int(batch([("eth_blockNumber",[])],endpoint=ep,timeout=10)[0],16)
out["endpoint"]=ep
for sig in ["launched()","failed()","isRefundPhase()","totalShares()","totalSupply()"]:
    try: out[sig.split("(")[0]]=to_int(single(ep,MINT,sig))
    except Exception as e: out[sig.split("(")[0]]=None; out[sig.split("(")[0]+"_err"]=str(e)[:100]
for sig,key in [("tokenClaimed(address)","tokenClaimed_user")]:
    try: out[key]=to_int(single(ep,MINT,sig,USER))
    except Exception as e: out[key]=None; out[key+"_err"]=str(e)[:100]
try: out["tokenBalance_user"]=to_int(single(ep,TOKEN,"balanceOf(address)",USER))
except Exception as e: out["tokenBalance_user"]=None; out["tokenBalance_user_err"]=str(e)[:100]
try:
    r0=to_int(single(ep,PAIR,"getReserves()"))  # returns tuple; to_int fails -> None, fine
    out["pair_reserves_raw"]=single(ep,PAIR,"getReserves()")
except Exception as e: out["pair_reserves_raw"]=None; out["pair_err"]=str(e)[:100]
print(json.dumps(out,indent=1))
json.dump(out,open("run-2026-11-07-2131-binanceai.json","w"),indent=1)
