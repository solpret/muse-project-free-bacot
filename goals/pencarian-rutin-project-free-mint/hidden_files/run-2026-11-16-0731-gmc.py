#!/usr/bin/env python3
"""Golden Miner deep read run 0731 (read-only)."""
import json, subprocess
from Crypto.Hash import keccak
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EP="https://bsc-dataseed.binance.org/"
ADDR="0x088708f79A71b82C14e1864FB0c63E53Cbf94243"
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def enc_addr(a): return a[2:].lower().rjust(64,"0")
def enc_u(n): return format(n,"064x")
def data(sig,args):
    d=sel(sig)
    for a in args:
        if isinstance(a,str) and a.startswith("0x") and len(a)==42: d+=enc_addr(a)
        else: d+=enc_u(int(a))
    return d
def rpc(p,timeout=60):
    out=subprocess.run(["curl","-sL","--max-time",str(timeout),"-X","POST",EP,"-H","Content-Type: application/json","-d",json.dumps(p)],capture_output=True,text=True,timeout=timeout+10).stdout
    return json.loads(out)
U=[USER]
calls=[("FREE_POOL","FREE_POOL()",[]),("FREE_PER_ID","FREE_PER_ID()",[]),("freeRemaining","freeRemaining()",[]),
("freeOf_user","freeOf(address)",U),("freeAllowanceOf_user","freeAllowanceOf(address)",U),
("quote_user_1","quote(address,uint256)",[USER,1]),("quote_user_5","quote(address,uint256)",[USER,5]),
("mintStart","mintStart()",[]),("mintEnd","mintEnd()",[]),("saleActive","saleActive()",[]),("saleEnded","saleEnded()",[]),
("gate","gate()",[]),("mintCountByWallet_user","mintCountByWallet(address)",U),
("freeMintCountById_user","freeMintCountById(address)",U),
("tokenURI_1","tokenURI(uint256)",[1]),("tokenURI_0","tokenURI(uint256)",[0]),
("remaining","remaining()",[]),("totalDrawn","totalDrawn()",[])]
payload=[{"jsonrpc":"2.0","id":i,"method":"eth_call","params":[{"to":ADDR,"data":data(s,a)},"latest"]} for i,(n,s,a) in enumerate(calls)]
r=rpc(payload)
def di(h):
    try: return int(h,16) if h and h!="0x" else None
    except Exception: return None
def ds(h):
    try:
        if not h or len(h)<138: return None
        ln=int(h[66:130],16)
        return bytes.fromhex(h[130:130+ln*2]).decode("utf-8","replace")
    except Exception: return None
out={}
for i,(n,s,a) in enumerate(calls):
    res=r[i].get("result") if isinstance(r,list) else None
    out[n]=ds(res) if n.startswith("tokenURI") else di(res)
    print(n,"=",out[n])
import datetime
for k in ("mintStart","mintEnd"):
    if out.get(k): print(k,"->",datetime.datetime.fromtimestamp(out[k],datetime.timezone(datetime.timedelta(hours=7))).isoformat())
json.dump(out,open(BASE+"run-2026-11-16-0731-gmc.json","w"),indent=1)
