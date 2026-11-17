#!/usr/bin/env python3
"""Post-mint checks SOLDERCATS #504: tokenURI/rarity + own-market state. Read-only."""
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
def post(ep,payload,timeout=25):
    out=subprocess.run(["curl","-sL","--max-time",str(timeout),"-X","POST",ep,"-H","Content-Type: application/json","-d",json.dumps(payload)],capture_output=True,text=True,timeout=timeout+5).stdout
    return json.loads(out)
def dec_str(v):
    try:
        if not v or v=="0x": return None
        b=bytes.fromhex(v[2:])
        ln=int.from_bytes(b[64:96],"big")
        return b[96:96+ln].decode(errors="replace")
    except Exception: return None
out={}
tid="00000000000000000000000000000000000000000000000000000000000001f8"
calls=[{"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":SC,"data":sel("tokenURI(uint256)")+tid},"latest"]},
       {"jsonrpc":"2.0","id":2,"method":"eth_call","params":[{"to":SC,"data":sel("isRevealed()")},"latest"]},
       {"jsonrpc":"2.0","id":3,"method":"eth_blockNumber","params":[]}]
for ep in EPS:
    try:
        r=post(ep,calls,timeout=25)
        if isinstance(r,list) and len(r)==3:
            out["tokenURI"]=dec_str(r[0].get("result")); out["isRevealed"]=to_int(r[1].get("result")); out["block"]=int(r[2]["result"],16)
            break
    except Exception: continue
print("tokenURI:",out.get("tokenURI"),"| isRevealed:",out.get("isRevealed"),"| block:",out.get("block"),flush=True)
# fetch metadata
uri=out.get("tokenURI") or ""
meta=None
if uri.startswith("http"):
    try:
        req=urllib.request.Request(uri,headers={"User-Agent":"free-bacot/1.0"})
        with urllib.request.urlopen(req,timeout=20) as resp: meta=json.loads(resp.read().decode())
        print("META:",json.dumps(meta)[:1500],flush=True)
    except Exception as e: print("META ERR",e,flush=True)
out["metadata"]=meta
# market contract: Sourcify ABI + views
try:
    req=urllib.request.Request(f"https://sourcify.dev/server/v2/contract/56/{MK}?fields=abi",headers={"User-Agent":"free-bacot/1.0"})
    with urllib.request.urlopen(req,timeout=20) as resp: mabi=json.loads(resp.read().decode()).get("abi",[])
    mfns=sorted({e['name'] for e in mabi if e.get('type')=='function'})
    print("MARKET fns:",mfns,flush=True)
    out["market_fns"]=mfns
    json.dump(mabi,open("abi-0831-soldercats-market.json","w"))
except Exception as e:
    print("MARKET ABI ERR",e,flush=True); out["market_fns"]=None
json.dump(out,open("run-2026-11-11-0831-postmint.json","w"),indent=1)
