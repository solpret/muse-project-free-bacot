#!/usr/bin/env python3
"""Check Boltbook-new 0x1595013d (BNB Genesis mint prompt, realsinaga.ai 2026-11-15T23:59Z).
Read-only: totalSupply, name/symbol, free views, Sourcify ABI, registry bytes."""
import json, subprocess, urllib.request
from Crypto.Hash import keccak
ADDR="0x1595013dfc8c6b3f4b172254bf09bdaf1421002b"
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS=["https://bsc-dataseed.binance.org/","https://bsc-dataseed1.bnbchain.org/"]
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64,"0")
def call(sig, args=[]):
    d=sel(sig)
    for a in args:
        d+= enc(a) if (isinstance(a,str) and a.startswith("0x") and len(a)==42) else format(int(a),"064x")
    payload={"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":ADDR,"data":d},"latest"]}
    for ep in EPS:
        try:
            r=subprocess.run(["curl","-sL","--max-time","30","-X","POST",ep,"-H","Content-Type: application/json","-d",json.dumps(payload)],capture_output=True,text=True,timeout=40)
            j=json.loads(r.stdout)
            if j.get("result") is not None: return j["result"]
        except Exception: continue
    return None
def tint(v):
    try: return int(v,16) if v and v!="0x" else None
    except Exception: return None
def tstr(v):
    try:
        b=bytes.fromhex(v[2:])
        ln=int.from_bytes(b[32:64],'big')
        return b[64:64+ln].decode(errors='ignore')
    except Exception: return None
out={}
for name,sig,args,fn in [
 ("totalSupply","totalSupply()",[],tint),("totalMinted","totalMinted()",[],tint),
 ("name","name()",[],tstr),("symbol","symbol()",[],tstr),
 ("MAX_SUPPLY","MAX_SUPPLY()",[],tint),("FREE_SUPPLY","FREE_SUPPLY()",[],tint),
 ("freeMinted","freeMinted()",[],tint),("freeClaimed","freeClaimed()",[],tint),
 ("mintOpen","mintOpen()",[],tint),("mintPrice","mintPrice()",[],tint),
 ("balanceOf_user","balanceOf(address)",[USER],tint),
 ("mintedBy_user","mintedBy(address)",[USER],tint),
 ("freeUsed_user","freeUsed(address)",[USER],tint),
 ("priceFor_user","priceFor(address)",[USER],tint),
]:
    out[name]=fn(call(sig,args))
print(json.dumps(out,indent=1))
# Sourcify ABI
try:
    req=urllib.request.Request(f"https://sourcify.dev/server/v2/contract/56/{ADDR}?fields=abi",headers={"User-Agent":"free-mint-search/0701"})
    with urllib.request.urlopen(req,timeout=20) as r: meta=json.loads(r.read().decode())
    abi=meta.get("abi",[])
    names=sorted({e["name"] for e in abi if e.get("type")=="function"})
    print("SOURCIFY verified, functions:", names)
    print("match:", meta.get("match"))
except Exception as e:
    print("SOURCIFY:", e)
# bytecode registry bytes
payload={"jsonrpc":"2.0","id":1,"method":"eth_getCode","params":[ADDR,"latest"]}
for ep in EPS:
    try:
        r=subprocess.run(["curl","-sL","--max-time","30","-X","POST",ep,"-H","Content-Type: application/json","-d",json.dumps(payload)],capture_output=True,text=True,timeout=40)
        code=json.loads(r.stdout).get("result","")
        print("bytecode len:", (len(code)-2)//2, "registry bytes present:", "60b9262456de011f7d15a54cdd8c48baaa8b022f" in code.lower())
        break
    except Exception as e: print("code err", e)
