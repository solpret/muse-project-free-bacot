#!/usr/bin/env python3
"""Triage part 2 run 1601 — Agentite correct views + Motor owner check. Read-only."""
import json, subprocess, time
from concurrent.futures import ThreadPoolExecutor
from Crypto.Hash import keccak
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS=["https://bsc-dataseed1.bnbchain.org/","https://bsc-dataseed2.bnbchain.org/","https://bsc-dataseed.binance.org/"]
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64,"0")
def to_int(v):
    try: return int(v,16) if v not in (None,"0x") else None
    except Exception: return None
def post(ep,payload,timeout=25):
    out=subprocess.run(["curl","-sL","--max-time",str(timeout),"-X","POST",ep,"-H","Content-Type: application/json","-d",json.dumps(payload)],capture_output=True,text=True,timeout=timeout+5).stdout
    return json.loads(out)
def call_one(addr,sig):
    base=sig.split("(")[0]
    data=sel(sig)+(enc(USER) if "(address)" in sig else "")
    for ep in EPS:
        try:
            r=post(ep,{"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":addr,"data":data},"latest"]})
            if isinstance(r,dict) and "error" in r: return "REVERT"
            res=r.get("result")
            if res is None: continue
            if base in ("owner","admin","creator"):
                try: return "0x"+res[-40:]
                except Exception: return res
            return to_int(res)
        except Exception:
            continue
    return None
AG="0xA587F3Ef2BEc919255fCfFF36A6BdD82cf4D87e2"
X8="0x86F83E98437A1DcF0e4A62828f68C1D53B3c7AB5"
jobs=[("Agentite",AG,"totalMinted()"),("Agentite",AG,"hasFreeMinted(address)"),("Agentite",AG,"publicMinted()"),("Agentite",AG,"tokenGrade(uint256)"),("Motor",X8,"owner()"),("Motor",X8,"admin()")]
def run_job(j):
    name,addr,sig=j
    v=call_one(addr,sig)
    print(f"{name} {sig} = {v}",flush=True)
    return name,sig,v
out={}
with ThreadPoolExecutor(max_workers=4) as ex:
    for name,sig,v in ex.map(run_job,jobs):
        out.setdefault(name,{})[sig]=v
def block():
    for ep in EPS:
        try:
            r=post(ep,{"jsonrpc":"2.0","id":1,"method":"eth_blockNumber","params":[]})
            return int(r["result"],16)
        except Exception: continue
    return None
out["block"]=block()
print(json.dumps(out,indent=1))
json.dump(out,open("run-2026-11-09-1601-triage-new2.json","w"),indent=1)
