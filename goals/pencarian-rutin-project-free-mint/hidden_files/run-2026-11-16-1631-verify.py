#!/usr/bin/env python3
"""Re-read Volta Gent + Punch Card for run 1631. Read-only."""
import json, subprocess, time
from Crypto.Hash import keccak
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed.binance.org/","https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/","https://bsc-rpc.publicnode.com/"]
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def enc_addr(a): return a[2:].lower().rjust(64,"0")
def enc_u(n): return format(n,"064x")
def build(sig,args):
    d=sel(sig)
    for a in args:
        if isinstance(a,str) and a.startswith("0x") and len(a)==42: d+=enc_addr(a)
        elif isinstance(a,str) and a.startswith("0x"): d+=enc_u(int(a,16))
        else: d+=enc_u(int(a))
    return d
def to_int(v):
    try: return int(v,16) if v and v!="0x" else None
    except Exception: return None
def call(ep,to,data,timeout=60):
    out=subprocess.run(["curl","-sL","--max-time",str(timeout),"-X","POST",ep,
        "-H","Content-Type: application/json","-d",
        json.dumps({"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":to,"data":data},"latest"]})],
        capture_output=True,text=True,timeout=timeout+10).stdout
    try: return json.loads(out).get("result")
    except Exception: return None
def read(to, views):
    res={}
    for name,sig,args in views:
        val=None
        for ep in EPS:
            r=call(ep,to,build(sig,args))
            if r is not None:
                val=to_int(r); break
        res[name]=val
    return res
U=[USER]
ITEMS={
 "VoltaGent":("0x2703a2be75e0c470d83573badc6a1b1b86d1871e",[
   ("totalMinted","totalMinted()",[]),("AGENT_LIMIT","AGENT_LIMIT()",[]),
   ("agentPhaseActive","agentPhaseActive()",[]),("mintOpen","mintOpen()",[]),
   ("agentMintedByWallet_user","agentMintedByWallet(address)",U),
   ("balanceOf_user","balanceOf(address)",U),("MAX_SUPPLY","MAX_SUPPLY()",[])]),
 "PunchCard":("0x1d4ef0587dd3ff3875a141d4711c60bca40587c4",[
   ("totalSupply","totalSupply()",[]),("totalMinted","totalMinted()",[]),
   ("freeMinted","freeMinted()",[]),("paidMinted","paidMinted()",[]),
   ("MAX_SUPPLY","MAX_SUPPLY()",[]),("remaining","remaining()",[]),
   ("mintOpen","mintOpen()",[]),("mintPriceFor_user_1","mintPriceFor(address,uint256)",U+[1]),
   ("mintedCount_user","mintedCount(address)",U),("balanceOf_user","balanceOf(address)",U)]),
}
out={"block":None,"reads":{}}
for ep in EPS:
    try:
        o=subprocess.run(["curl","-sL","--max-time","30","-X","POST",ep,"-H","Content-Type: application/json",
            "-d",json.dumps({"jsonrpc":"2.0","id":1,"method":"eth_blockNumber","params":[]})],
            capture_output=True,text=True,timeout=40).stdout
        out["block"]=int(json.loads(o)["result"],16); break
    except Exception: pass
t0=time.time()
for k,(to,views) in ITEMS.items():
    out["reads"][k]={"address":to,"views":read(to,views)}
out["elapsed_s"]=round(time.time()-t0,1)
json.dump(out,open("run-2026-11-16-1631-verify.json","w"),indent=1)
print(json.dumps(out,indent=1))
