#!/usr/bin/env python3
"""Probe 6 new Sourcify contracts from run 1101 feed (0x8af3 free+mint no-agent;
5x 37-fn template mint+quote+agent no-free-view). Generic NFT views only, read-only."""
import json, subprocess, time
from Crypto.Hash import keccak
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/"]
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def post_rpc(ep, payload, timeout=20):
    out = subprocess.run(["curl","-sL","--max-time",str(timeout),"-X","POST",ep,
        "-H","Content-Type: application/json","-d",json.dumps(payload)],
        capture_output=True, text=True, timeout=timeout+5).stdout
    return json.loads(out)
def words(hexv):
    try:
        b = bytes.fromhex(hexv[2:])
        return [int.from_bytes(b[i:i+32],"big") for i in range(0,len(b),32)]
    except Exception: return None
VIEWS = [("totalSupply","totalSupply()"),("totalMinted","totalMinted()"),
 ("freeMinted","freeMinted()"),("FREE_POOL","FREE_POOL()"),("FREE_SUPPLY","FREE_SUPPLY()"),
 ("FREE_MAX","FREE_MAX()"),("MAX_SUPPLY","MAX_SUPPLY()"),("mintOpen","mintOpen()"),
 ("mintPrice","mintPrice()"),("paidMinted","paidMinted()"),("name","name()"),("symbol","symbol()"),
 ("decimals","decimals()"),("agentIdRegistry","agentIdRegistry()"),("registry","registry()")]
TARGETS = ["0x8af3C54A08cF7E0Bff2b74343bC7c268FAac7F7e","0x13de553dE4154644eDEC85F5d723E6AF4A6e7703",
 "0xaBd0450a893F5800C4c2E54595650FC29325CC12","0x16DA14B5062f2313Bc4291D73a1DbCc132Acf9cc",
 "0x749501DEEe864C403EDd84E41808Aea408567270","0x01A5d8E7Ce9D19DC7Ca557d5d88146A34a16264D"]
def read_one(addr):
    calls=[{"jsonrpc":"2.0","id":i+1,"method":"eth_call","params":[{"to":addr,"data":sel(sig)},"latest"]} for i,(k,sig) in enumerate(VIEWS)]
    for ep in EPS:
        try:
            r = post_rpc(ep, calls)
            if not isinstance(r, list) or len(r)!=len(calls): continue
            res={}
            for it,(k,sig) in zip(r,VIEWS):
                if not isinstance(it,dict) or "error" in it or not it.get("result") or it["result"]=="0x":
                    res[k]=None; continue
                w=words(it["result"])
                if k in ("name","symbol"):
                    try:
                        b=bytes.fromhex(it["result"][2:])
                        ln=int.from_bytes(b[32:64],"big")
                        res[k]=b[64:64+ln].decode(errors="replace") if 0<ln<=64 else (w[0] if w else None)
                    except Exception: res[k]=w[0] if w else None
                else:
                    res[k]=w[0] if w is not None and len(w)==1 else w
            return res
        except Exception: continue
    return {"error":"all-endpoints-failed"}
out={}
for a in TARGETS: out[a]=read_one(a)
print(json.dumps(out, indent=1))
json.dump(out, open("run-2026-11-13-1101-probe.json","w"), indent=1)
