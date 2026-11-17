#!/usr/bin/env python3
"""Verify AGCLUB (sweep finding run 0401) on-chain, then add watchlist-only.
Read-only except snapshot add. No preview/mint."""
import json, subprocess, time
from Crypto.Hash import keccak
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
ADDR = "0x67270bb351515abf3089ca5420456897363f5e75"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/"]
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc_addr(a): return a[2:].lower().rjust(64, "0")
def enc_u(n): return format(n, "064x")
def post_rpc(ep, payload, timeout=60):
    out = subprocess.run(["curl","-sL","--max-time",str(timeout),"-X","POST",ep,
        "-H","Content-Type: application/json","-d",json.dumps(payload)],
        capture_output=True, text=True, timeout=timeout+10).stdout
    return json.loads(out)
def to_int(v):
    try: return int(v,16) if v and v!="0x" else None
    except Exception: return None
views = [("totalSupply","totalSupply()",[]),("freeMinted","freeMinted()",[]),
         ("FREE_SUPPLY","FREE_SUPPLY()",[]),("MAX_SUPPLY","MAX_SUPPLY()",[]),
         ("mintOpen","mintOpen()",[]),("totalMinted","totalMinted()",[]),
         ("freeClaimed_user","freeClaimed(address)",[USER]),
         ("balanceOf_user","balanceOf(address)",[USER])]
calls=[]
for name,sig,args in views:
    d=sel(sig)
    for a in args:
        d += enc_addr(a) if isinstance(a,str) and a.startswith("0x") and len(a)==42 else enc_u(int(a))
    calls.append({"jsonrpc":"2.0","id":len(calls)+1,"method":"eth_call",
                  "params":[{"to":ADDR,"data":d},"latest"]})
res=None; head=None
for ep in EPS:
    try:
        r=post_rpc(ep,{"jsonrpc":"2.0","id":1,"method":"eth_blockNumber","params":[]},30)
        head=int(r["result"],16)
        res=post_rpc(ep,calls,90)
        break
    except Exception as e:
        print("ep fail",ep,str(e)[:80]); continue
out={"address":ADDR,"block":head,"views":{}}
if res:
    for (name,_,_),item in zip(views,res):
        out["views"][name]=to_int(item.get("result")) if isinstance(item,dict) else None
print(json.dumps(out,indent=1))
json.dump(out,open(BASE+"run-2026-11-15-0401-agclub.json","w"),indent=1)
