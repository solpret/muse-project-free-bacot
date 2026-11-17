#!/usr/bin/env python3
"""Probe POA 0x4D0923060D6f657dF4C2567b629e1C3ab8DBc5F5 — read-only, no preview/mint."""
import json, subprocess, time
from Crypto.Hash import keccak
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
ADDR="0x4D0923060D6f657dF4C2567b629e1C3ab8DBc5F5"
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EP="https://bsc-dataseed.binance.org/"
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def enc_addr(a): return a[2:].lower().rjust(64,"0")
def enc_u(n): return format(n,"064x")
def data(sig,args):
    d=sel(sig)
    for a in args:
        d+=enc_addr(a) if isinstance(a,str) and a.startswith("0x") else enc_u(int(a))
    return d
def call(to,d,tag="latest"):
    p={"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":to,"data":d},tag]}
    out=subprocess.run(["curl","-sL","--max-time","30","-X","POST",EP,"-H","Content-Type: application/json","-d",json.dumps(p)],capture_output=True,text=True,timeout=40).stdout
    r=json.loads(out)
    if "result" not in r: return None
    v=r["result"]
    try: return int(v,16)
    except Exception: return v
VIEWS=[("totalSupply","totalSupply()",[]),("saleActive","saleActive()",[]),
 ("FREE_LIMIT","FREE_LIMIT()",[]),("MAX_FREE_PER_WALLET","MAX_FREE_PER_WALLET()",[]),
 ("MAX_PAID_PER_WALLET","MAX_PAID_PER_WALLET()",[]),("MAX_SUPPLY","MAX_SUPPLY()",[]),
 ("PRICE","PRICE()",[]),("registry","registry()",[]),
 ("costFor_user_1","costFor(address,uint256)",[USER,1]),
 ("freeMintedBy_user","freeMintedBy(address)",[USER]),
 ("paidMintedBy_user","paidMintedBy(address)",[USER]),
 ("hasAgentId_user","hasAgentId(address)",[USER]),
 ("balanceOf_user","balanceOf(address)",[USER]),
 ("splitFor_1","splitFor(uint256)",[1]),
 ("owner","owner()",[])]
res={}
for name,sig,args in VIEWS:
    res[name]=call(ADDR,data(sig,args))
    print(name,"=",res[name])
# head block
p={"jsonrpc":"2.0","id":1,"method":"eth_blockNumber","params":[]}
out=subprocess.run(["curl","-sL","--max-time","30","-X","POST",EP,"-H","Content-Type: application/json","-d",json.dumps(p)],capture_output=True,text=True,timeout=40).stdout
head=int(json.loads(out)["result"],16)
res["head"]=head
print("head =",head)
json.dump(res,open(BASE+"run-2026-11-15-0031-probe-poa.json","w"),indent=1)
