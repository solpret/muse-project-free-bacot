#!/usr/bin/env python3
import json, urllib.request, time
from Crypto.Hash import keccak
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
RPCS=["https://bsc-dataseed1.bnbchain.org","https://bsc.publicnode.com","https://bsc-dataseed2.bnbchain.org"]
DL=time.time()+45
FIVE={
 "UTAMN":"0xC7c08925D1953CBE943D1893f61d8F6EEcEe163C",
 "BNCBN":"0xBB7c5c37aE8DEF9a92C53da4Ba66D8F379E71378",
 "RYNK":"0x5a55C53AE5198139f25573bc8056b189f70acf1D",
 "IEDUS":"0xB9C4915d8F3fC9270eac0dF4de9c3b0734550C1e",
 "MTERG":"0x30aD58557aa5f3616A70275aD55b315c82AC3e5B",
}
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64,"0")
def call(addr,sig,args=""):
    data=sel(sig)+args
    for rpc in RPCS:
        if time.time()>DL: return "deadline"
        try:
            body=json.dumps({"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":addr,"data":data},"latest"]}).encode()
            req=urllib.request.Request(rpc,data=body,headers={"Content-Type":"application/json"})
            with urllib.request.urlopen(req,timeout=5) as r: out=json.load(r)
            if "error" in out: continue
            v=out["result"]
            if not v or v=="0x": return None
            return v
        except Exception: continue
    return None
def uint(v):
    if v is None or v=="deadline": return v
    try: return int(v,16)
    except Exception: return v
def dec_str(v):
    if not v or v=="deadline": return v
    try:
        b=bytes.fromhex(v[2:]); ln=int.from_bytes(b[32:64],"big"); return b[64:64+ln].decode()
    except Exception: return v
out={}
for name,addr in FIVE.items():
    d={"address":addr}
    for _n,sig,args,conv in [
        ("name","name()","",dec_str),("symbol","symbol()","",dec_str),
        ("decimals","decimals()","",uint),("totalSupply","totalSupply()","",uint),
        ("freeRemaining","freeRemaining()","",uint),
        ("balanceOf_user","balanceOf(address)",enc(USER),uint),
    ]:
        d[sig.split("(")[0]+("_user" if "address" in sig else "")]=conv(call(addr,sig,args))
    out[name]=d; print(name,d,flush=True)
json.dump(out,open(f"{BASE}/run-2026-11-06-0954-five-erc20-probe.json","w"),indent=1)
print("DONE")
