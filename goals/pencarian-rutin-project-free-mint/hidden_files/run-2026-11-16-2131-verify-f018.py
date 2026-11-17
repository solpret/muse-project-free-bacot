#!/usr/bin/env python3
"""Verify S1 hit 0xF0186519... run 2131. Read-only."""
import json, subprocess, urllib.request
from Crypto.Hash import keccak
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EP="https://bsc-dataseed.binance.org/"
ADDR="0xF0186519cff9830273Dc052451830308846D2813"
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def enc_addr(a): return a[2:].lower().rjust(64,"0")
def enc_u(n): return format(n,"064x")
def data(sig,args):
    d=sel(sig)
    for a in args:
        if isinstance(a,str) and a.startswith("0x") and len(a)==42: d+=enc_addr(a)
        elif isinstance(a,str) and a.startswith("0x"): d+=enc_u(int(a,16))
        else: d+=enc_u(int(a))
    return d
with urllib.request.urlopen(f"https://sourcify.dev/server/v2/contract/56/{ADDR}?fields=metadata,abi", timeout=45) as r:
    d=json.load(r)
abi=d.get("abi") or d.get("metadata",{}).get("output",{}).get("abi")
print("ABI fns:", [(f.get("name"), ",".join(i.get("type","") for i in f.get("inputs",[]))) for f in abi if f.get("type")=="function"])
print("match:", d.get("match"))
U=[USER]
views=[("name","name()",[]),("symbol","symbol()",[]),("decimals","decimals()",[]),
 ("totalSupply","totalSupply()",[]),("totalMinted","totalMinted()",[]),("freeMinted","freeMinted()",[]),
 ("freeClaimed","freeClaimed()",[]),("FREE_SUPPLY","FREE_SUPPLY()",[]),("FREE_SLOTS","FREE_SLOTS()",[]),
 ("freeLeft","freeLeft()",[]),("freeSupply","freeSupply()",[]),("MAX_SUPPLY","MAX_SUPPLY()",[]),
 ("mintOpen","mintOpen()",[]),("saleOpen","saleOpen()",[]),("launched","launched()",[]),
 ("paused","paused()",[]),("owner","owner()",[]),("agentRegistry","agentRegistry()",[]),
 ("mintedBy_user","mintedBy(address)",U),("balanceOf_user","balanceOf(address)",U),
 ("freeClaimed_user","freeClaimed(address)",U),("hasAgentId_user","hasAgentId(address)",U),
 ("quote_user_1","quote(address,uint256)",[USER,1]),("cost_user_1","cost(address,uint256)",[USER,1]),
 ("mintPriceFor_user_1","mintPriceFor(address,uint256)",[USER,1]),
 ("contractURI","contractURI()",[]),("tokenURI_0","tokenURI(uint256)",[0]),
 ("START_TIME","START_TIME()",[]),("saleStart","saleStart()",[]),("startTime","startTime()",[]),
 ("mintStart","mintStart()",[]),("FREE_AMOUNT","FREE_AMOUNT()",[]),("tokensPerShare","tokensPerShare()",[]),
 ("token","token()",[]),("saleToken","saleToken()",[]),("paymentToken","paymentToken()",[])]
res=[]
for ci in range(0, len(views), 12):
    chunk=views[ci:ci+12]
    calls=[{"jsonrpc":"2.0","id":i+1,"method":"eth_call","params":[{"to":ADDR,"data":data(sig,args)},"latest"]} for i,(k,sig,args) in enumerate(chunk)]
    out=subprocess.run(["curl","-sL","--max-time","120","-X","POST",EP,"-H","Content-Type: application/json","-d",json.dumps(calls)],capture_output=True,text=True,timeout=130).stdout
    res += json.loads(out)
def ti(v):
    try: return int(v,16) if v and v!="0x" else None
    except Exception: return None
outd={}
for (k,sig,args),r in zip(views,res):
    v=r.get("result")
    if v is None or v=="0x": outd[k]=None; continue
    if k in ("name","symbol"):
        try:
            raw=bytes.fromhex(v[2:]); ln=int.from_bytes(raw[64:96],'big'); outd[k]=raw[96:96+ln].decode(errors='replace')
        except Exception: outd[k]="decode-fail"
    elif k in ("contractURI","tokenURI_0"):
        try:
            raw=bytes.fromhex(v[2:]); ln=int.from_bytes(raw[64:96],'big'); outd[k]=raw[96:96+ln].decode(errors='replace')[:500]
        except Exception: outd[k]=v[:200]
    else: outd[k]=ti(v)
print(json.dumps(outd, indent=1))
json.dump({"address":ADDR,"abi_fns":[f.get("name") for f in abi if f.get("type")=="function"],"views":outd}, open(BASE+"run-2026-11-16-2131-verify-f018.json","w"), indent=1)
print("DONE")
