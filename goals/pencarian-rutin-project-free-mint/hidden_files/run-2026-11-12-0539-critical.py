#!/usr/bin/env python3
"""Run 0539 critical single-call fresh reads (no batches): Stampooor slot,
SEVEN, Eco, WFPASS. Sequential single eth_calls to dodge batch rate limits."""
import json, subprocess, time
from Crypto.Hash import keccak
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS=["https://bsc-dataseed.binance.org/","https://bsc-dataseed1.bnbchain.org/","https://bsc.publicnode.com","https://binance.llamarpc.com","https://rpc.ankr.com/bsc"]
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64,"0")
def to_int(v):
    try: return int(v,16) if v and v!="0x" else None
    except Exception: return None
def call(to,sig,args=()):
    data=sel(sig)
    for a in args: data+=enc(a)
    payload={"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":to,"data":data},"latest"]}
    for ep in EPS:
        try:
            r=subprocess.run(["curl","-sL","--max-time","20","-X","POST",ep,"-H","Content-Type: application/json","-d",json.dumps(payload)],capture_output=True,text=True,timeout=25)
            res=json.loads(r.stdout)
            if isinstance(res,dict) and "result" in res:
                return to_int(res["result"]), ep.split("//")[1].split("/")[0]
            if isinstance(res,dict) and "error" in res:
                continue
        except Exception:
            continue
        time.sleep(0.3)
    return None, None
def block():
    for ep in EPS:
        try:
            r=subprocess.run(["curl","-sL","--max-time","20","-X","POST",ep,"-H","Content-Type: application/json","-d",json.dumps({"jsonrpc":"2.0","id":1,"method":"eth_blockNumber","params":[]})],capture_output=True,text=True,timeout=25)
            res=json.loads(r.stdout)
            if "result" in res: return int(res["result"],16)
        except Exception: continue
    return None
out={"block":block(),"time_wib":time.strftime("%H:%M",time.gmtime(time.time()+7*3600))}
def rd(name,addr,views):
    d={"address":addr}
    for sig,args in views:
        v,ep=call(addr,sig,args)
        d[sig.split("(")[0]+("_user" if args else "")]=v
        print(name,sig,"=",v,"via",ep,flush=True)
        time.sleep(0.4)
    out[name]=d
rd("Stampooor","0x467696af8c2206B977B24081445104632dc1D459",
   [("freeMinted()",()),("FREE_SUPPLY()",()),("mintOpen()",()),("balanceOf(address)",(USER,)),("freeAvailable(address)",(USER,))])
rd("SEVEN","0xFf65cf70a15fA0B06Bf8D8ED020Cf9F917C80f96",
   [("freeMinted()",()),("FREE_CAP()",()),("mintOpen()",()),("freeCountBy(address)",(USER,))])
rd("Eco","0xd31b168F7b6f3dB39BEd89433124595aaa91cfF3",
   [("freeWalletCount()",()),("FREE_WALLETS()",()),("freeMinted()",()),("totalMinted()",()),("mintOpen()",()),("freeCountBy(address)",(USER,))])
rd("WFPASS","0xD52A86AC936c4C3d46aF0d49e8D44F3C698BEe7C",
   [("mintOpen()",()),("saleStart()",()),("totalMinted()",())])
print(json.dumps(out,indent=1))
json.dump(out,open(BASE+"run-2026-11-12-0539-critical.json","w"),indent=1)
