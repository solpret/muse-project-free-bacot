#!/usr/bin/env python3
"""Xeno Agent 0xc6a533... verification, run 1501. Read-only; static eth_call mint(1) value 0 (no tx)."""
import json, subprocess, urllib.request
from Crypto.Hash import keccak
ADDR="0xc6a533146b7de96f9c805c19777bafd93a41b594"
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS=["https://bsc-dataseed.binance.org/","https://bsc-dataseed1.bnbchain.org/","https://bsc-rpc.publicnode.com/"]
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def enc_addr(a): return a[2:].lower().rjust(64,"0")
def enc_u(n): return format(n,"064x")
def data(sig,args):
    d=sel(sig)
    for a in args:
        d+= enc_addr(a) if isinstance(a,str) and a.startswith("0x") and len(a)==42 else enc_u(int(a) if not isinstance(a,str) else int(a,16))
    return d
def to_int(v):
    try: return int(v,16) if v and v!="0x" else None
    except Exception: return v
def post(ep,payload,timeout=60):
    out=subprocess.run(["curl","-sL","--max-time",str(timeout),"-X","POST",ep,"-H","Content-Type: application/json","-d",json.dumps(payload)],capture_output=True,text=True,timeout=timeout+10).stdout
    return json.loads(out)
# Sourcify
try:
    req=urllib.request.Request(f"https://sourcify.dev/server/v2/contract/56/{ADDR}?fields=abi",headers={"User-Agent":"free-mint-search/1501"})
    with urllib.request.urlopen(req,timeout=20) as r: meta=json.loads(r.read().decode())
    abi=meta.get("abi",[])
    names=sorted({e["name"] for e in abi if e.get("type")=="function"})
    print("SOURCIFY: abi fns",len(names)); print(" ",names)
    print("  has freeMint:", "freeMint" in names, "| mint:", [n for n in names if n.lower().startswith('mint')], "| price/quote:", [n for n in names if 'price' in n.lower() or 'quote' in n.lower() or 'cost' in n.lower()])
    print("  free views:", [n for n in names if 'free' in n.lower()])
    print("  agent refs:", [n for n in names if 'agent' in n.lower() or 'registry' in n.lower()])
    print("  supply:", [n for n in names if 'supply' in n.lower() or 'cap' in n.lower() or 'max' in n.lower()])
except Exception as e:
    print("SOURCIFY ERROR:",type(e).__name__,str(e)[:200])
views=[("totalSupply","totalSupply()",[]),("totalMinted","totalMinted()",[]),("MAX_SUPPLY","MAX_SUPPLY()",[]),
("freeMinted","freeMinted()",[]),("freeClaimed","freeClaimed()",[]),("freeLeft","freeLeft()",[]),("freeSupply","freeSupply()",[]),
("mintOpen","mintOpen()",[]),("paused","paused()",[]),("price","price()",[]),("PRICE","PRICE()",[]),("mintPrice","mintPrice()",[]),
("owner","owner()",[]),("name","name()",[]),("symbol","symbol()",[]),
("balanceOf_user","balanceOf(address)",[USER]),("mintedBy_user","mintedBy(address)",[USER]),
("freeClaimed_user","freeClaimed(address)",[USER]),("freeMintedBy_user","freeMintedBy(address)",[USER]),
("priceFor_user_1","priceFor(address,uint256)",[USER,1]),("cost_user_1","cost(address,uint256)",[USER,1]),
("quote_user_1","quote(address,uint256)",[USER,1])]
calls=[]; meta=[]
for k,sig,args in views:
    calls.append({"jsonrpc":"2.0","id":len(calls)+1,"method":"eth_call","params":[{"to":ADDR,"data":data(sig,args)},"latest"]})
    meta.append(k)
for ep in EPS:
    try:
        res=post(ep,calls)
        if isinstance(res,list) and len(res)==len(calls):
            print("RPC via",ep)
            for it,k in zip(res,meta):
                if not isinstance(it,dict) or "error" in it or it.get("result") in (None,"0x"):
                    print(f"  {k}: None ({str(it.get('error'))[:80] if isinstance(it,dict) else '?'})")
                else:
                    print(f"  {k}: {to_int(it['result'][:66]) if len(it['result'])>=66 else it['result']}")
            break
    except Exception as e:
        print("ep fail",ep,str(e)[:80]); continue
# static call mint(1) value 0 from user
md=data("mint(uint256)",[1])
for ep in EPS:
    try:
        res=post(ep,{"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"from":USER,"to":ADDR,"data":md,"value":"0x0"},"latest"]})
        print("STATIC mint(1) value=0 via",ep,":",json.dumps(res)[:300]); break
    except Exception as e:
        print("static fail",ep,str(e)[:80]); continue
# block
for ep in EPS:
    try:
        r=post(ep,{"jsonrpc":"2.0","id":1,"method":"eth_blockNumber","params":[]})
        if r.get("result"): print("BLOCK:",int(r["result"],16)); break
    except Exception: continue
