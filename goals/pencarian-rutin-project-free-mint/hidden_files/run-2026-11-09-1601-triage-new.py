#!/usr/bin/env python3
"""Triage NEW discovery items run 1601 — Agentite + 0x86F8. Read-only, curl dataseed,
single-call batches (revert-safe). Writes run-2026-11-09-1601-triage-new.json."""
import json, subprocess, time
from concurrent.futures import ThreadPoolExecutor
from Crypto.Hash import keccak
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
REG="60b9262456de011f7d15a54cdd8c48baaa8b022f"
EPS=["https://bsc-dataseed1.bnbchain.org/","https://bsc-dataseed2.bnbchain.org/","https://bsc-dataseed.binance.org/"]
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64,"0")
def dec_str(v):
    try:
        b=bytes.fromhex(v[2:])
        if len(b)<64: return None
        ln=int.from_bytes(b[32:64],"big")
        raw=b[64:64+ln]
        return raw.decode("utf-8","replace")
    except Exception: return None
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
            if base in ("name","symbol","contractURI"):
                s=dec_str(res)
                return s if s is not None else res
            if base in ("agentRegistry","REGISTRY","TOKEN","owner"):
                try: return "0x"+res[-40:]
                except Exception: return res
            if base=="freeLeft":
                try:
                    b=bytes.fromhex(res[2:])
                    return [int.from_bytes(b[i:i+32],"big") for i in (0,32)]
                except Exception: return res
            return to_int(res)
        except Exception:
            continue
    return None
def code_has_registry(addr):
    for ep in EPS:
        try:
            r=post(ep,{"jsonrpc":"2.0","id":1,"method":"eth_getCode","params":[addr,"latest"]})
            c=r.get("result","")
            return {"has_registry_bytes": REG in c.lower(), "code_len": (len(c)-2)//2 if c.startswith("0x") else None}
        except Exception:
            continue
    return {"has_registry_bytes": None, "code_len": None}
def block():
    for ep in EPS:
        try:
            r=post(ep,{"jsonrpc":"2.0","id":1,"method":"eth_blockNumber","params":[]})
            return int(r["result"],16)
        except Exception: continue
    return None
AG="0xA587F3Ef2BEc919255fCfFF36A6BdD82cf4D87e2"
X8="0x86F83E98437A1DcF0e4A62828f68C1D53B3c7AB5"
AG_VIEWS=["totalSupply()","name()","symbol()","owner()","freeClaimed()","freeMinted()","freeLeft()","FREE_SUPPLY()","MAX_SUPPLY()","mintOpen()","mintStart()","mintEnd()","agentRegistry()","hasAgentId(address)","freeClaimed(address)","balanceOf(address)","contractURI()"]
X8_VIEWS=["name()","symbol()","totalSupply()","REGISTRY()","AGENT_FREE_CAP()","X_FREE_CAP()","freeLeft()","mintStart()","mintEnd()","mintOpen()","paidMinted()","freeUsedByWallet(address)","agentFreeUsed(address)","TOKEN()","contractURI()","MAX_SUPPLY()","PRICE()","claimable(address)"]
out={"block":block(),"run":"2026-11-09-1601"}
jobs=[]
for sig in AG_VIEWS: jobs.append(("Agentite",AG,sig))
for sig in X8_VIEWS: jobs.append(("0x86F8",X8,sig))
def run_job(j):
    name,addr,sig=j
    t=time.time()
    v=call_one(addr,sig)
    print(f"{name} {sig} = {str(v)[:120]} ({time.time()-t:.1f}s)",flush=True)
    return name,sig,v
res={}
with ThreadPoolExecutor(max_workers=4) as ex:
    for name,sig,v in ex.map(run_job,jobs):
        res.setdefault(name,{})[sig]=v
out["reads"]=res
out["Agentite_code"]=code_has_registry(AG)
out["0x86F8_code"]=code_has_registry(X8)
print(json.dumps(out,indent=1))
json.dump(out,open("run-2026-11-09-1601-triage-new.json","w"),indent=1)
