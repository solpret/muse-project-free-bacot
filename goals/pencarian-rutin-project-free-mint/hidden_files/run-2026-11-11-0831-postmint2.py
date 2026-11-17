#!/usr/bin/env python3
"""Post-mint checks SOLDERCATS #504 (fixed string decoder) + own-market live state. Read-only."""
import json, subprocess, urllib.request
from Crypto.Hash import keccak
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
SC="0x3D972EBbF7488f21b95250B867e2406c723C9DDC"
MK="0xd35592aeccb54a9e528bf4b1a6fcfd4de9367bc9"
EPS=["https://bsc-dataseed.binance.org/","https://bsc-dataseed1.bnbchain.org/"]
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64,"0")
def to_int(v):
    try: return int(v,16) if v not in (None,"0x") else None
    except Exception: return None
def dec_str(v):
    try:
        if not v or v=="0x": return None
        b=bytes.fromhex(v[2:])
        off=int.from_bytes(b[0:32],"big")
        ln=int.from_bytes(b[off:off+32],"big")
        return b[off+32:off+32+ln].decode(errors="replace")
    except Exception: return None
def post(ep,payload,timeout=25):
    out=subprocess.run(["curl","-sL","--max-time",str(timeout),"-X","POST",ep,"-H","Content-Type: application/json","-d",json.dumps(payload)],capture_output=True,text=True,timeout=timeout+5).stdout
    return json.loads(out)
def batch(addr, views):
    calls=[]
    for i,(sig,arg) in enumerate(views):
        data=sel(sig)+(enc(arg) if arg is not None else "")
        calls.append({"jsonrpc":"2.0","id":i+1,"method":"eth_call","params":[{"to":addr,"data":data},"latest"]})
    for ep in EPS:
        try:
            r=post(ep,calls,timeout=25)
            if isinstance(r,list) and len(r)==len(calls):
                return [it.get("result") if isinstance(it,dict) and "error" not in it else None for it in r]
        except Exception: continue
    return [None]*len(views)
out={}
tid="00000000000000000000000000000000000000000000000000000000000001f8"
r=batch(SC,[("tokenURI(uint256)",tid),("isRevealed()",None),("revealedCount()",None)])
out["tokenURI"]=dec_str(r[0]); out["isRevealed"]=to_int(r[1]); out["revealedCount"]=to_int(r[2])
print("tokenURI:",out["tokenURI"],"| isRevealed:",out["isRevealed"],"| revealedCount:",out["revealedCount"],flush=True)
uri=out["tokenURI"] or ""
meta=None
if uri.startswith("http"):
    try:
        req=urllib.request.Request(uri,headers={"User-Agent":"free-bacot/1.0"})
        with urllib.request.urlopen(req,timeout=20) as resp: meta=json.loads(resp.read().decode())
        print("META:",json.dumps(meta)[:2000],flush=True)
    except Exception as e: print("META ERR",e,flush=True)
elif uri:
    # relative path: try site base
    for base in ["https://soldercats.pages.dev/meta/","https://soldercats.pages.dev/"]:
        try:
            req=urllib.request.Request(base+uri,headers={"User-Agent":"free-bacot/1.0"})
            with urllib.request.urlopen(req,timeout=20) as resp: meta=json.loads(resp.read().decode())
            print("META via",base+uri,":",json.dumps(meta)[:2000],flush=True); break
        except Exception as e: print("META ERR",base+uri,e,flush=True)
out["metadata"]=meta
# market: listedCount, FEE_BPS, feeOf(504), listings(504), listingsPage(0,10)
r=batch(MK,[("listedCount()",None),("FEE_BPS()",None),("NFT()",None)])
out["market_listedCount"]=to_int(r[0]); out["market_FEE_BPS"]=to_int(r[1])
out["market_NFT"]=("0x"+r[2][-40:]) if r[2] else None
print("MARKET listedCount:",out["market_listedCount"],"FEE_BPS:",out["market_FEE_BPS"],"NFT:",out["market_NFT"],flush=True)
# listings(uint256) returns struct - raw hex
r=batch(MK,[("listings(uint256)",tid),("feeOf(uint256)",tid)])
out["market_listings_504_raw"]=r[0]; out["market_feeOf_504_raw"]=r[1]
print("listings(504) raw:",r[0],flush=True)
print("feeOf(504) raw:",r[1],flush=True)
r=batch(MK,[("listingsPage(uint256,uint256)","0"),("listingsPage(uint256,uint256)","10")])
# listingsPage likely takes (offset,limit) as two uints; encode manually below if needed
print("listingsPage raw attempt:",r,flush=True)
json.dump(out,open("run-2026-11-11-0831-postmint2.json","w"),indent=1)
