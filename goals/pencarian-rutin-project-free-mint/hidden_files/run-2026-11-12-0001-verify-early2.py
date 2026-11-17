#!/usr/bin/env python3
"""Verify 2 new early-shape contracts from feed shape-check run 0001:
0x79b0 (S1 pass, NFT) and 0xE1a4 (early_shape, NFT). Free pool, user slot,
launch-time views, name/symbol, ABI fn list. Read-only; no preview/mint."""
import json, subprocess
from Crypto.Hash import keccak
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS=["https://bsc-dataseed.binance.org/","https://bsc-dataseed1.bnbchain.org/","https://bsc-dataseed2.bnbchain.org/"]
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64,"0")
def enc_u(n): return hex(n)[2:].rjust(64,"0")
def to_int(v):
    try: return int(v,16) if v and v!="0x" else None
    except Exception: return None
def post(ep,payload,timeout=25):
    out=subprocess.run(["curl","-sL","--max-time",str(timeout),"-X","POST",ep,"-H","Content-Type: application/json","-d",json.dumps(payload)],capture_output=True,text=True,timeout=timeout+5).stdout
    return json.loads(out)
def call(addr,data,timeout=25):
    for ep in EPS:
        try:
            r=post(ep,{"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":addr,"data":data},"latest"]},timeout)
            if isinstance(r,dict) and "result" in r: return r["result"]
        except Exception: continue
    return None
def batch(addr,views):
    calls,keys=[],[]
    for i,sig in enumerate(views):
        base=sig.split("(")[0]
        if "(address)" in sig: data,key=sel(sig)+enc(USER),base+"_user"
        else: data,key=sel(sig),base
        calls.append({"jsonrpc":"2.0","id":i+1,"method":"eth_call","params":[{"to":addr,"data":data},"latest"]})
        keys.append(key)
    for ep in EPS:
        try:
            res=post(ep,calls)
            if not isinstance(res,list) or len(res)!=len(calls): continue
            return {k:(None if isinstance(it,dict) and "error" in it else (to_int(it.get("result")) if isinstance(it,dict) else None)) for it,k in zip(res,keys)}
        except Exception: continue
    return None
VIEWS=["totalSupply()","totalMinted()","freeClaimed()","freeMinted()","FREE_SUPPLY()","freeLeft()","MAX_SUPPLY()","mintOpen()","balanceOf(address)","freeClaimed(address)","freeUsed(address)","mintedBy(address)","mintStart()","saleStart()","saleEnd()","mintOpenedAt()","mintOpensAt()","freePoolSize()","totalFreeCount()","paidMinted()","PRICE()","price()","freeSharesRemaining()","freeRemaining()","owner()","FREE_CAP()","FREE_PER_WALLET()","MAX_PER_WALLET()","freeCountBy(address)","freeMintedBy(address)","holdsAgentId(address)","isAgent(address)","freeAvailable(address)","agentIdRegistry()"]
TARGETS={"0x79b0":"0x79b0CE8b39c3Ed230487172751612b4F631398Bc",
         "0xE1a4":"0xE1a4fFb104e5BF2b7aA5aD77969D43B56FCEE91A"}
out={}
for name,addr in TARGETS.items():
    d={"address":addr}
    try:
        r=subprocess.run(["curl","-sL","--max-time","60",f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi"],capture_output=True,text=True,timeout=65)
        meta=json.loads(r.stdout)
        fns=[(f.get("name"),",".join(i.get("type","") for i in f.get("inputs",[]))) for f in meta.get("abi",[]) if f.get("type")=="function"]
        d["fns"]=fns
        d["name_fns"]=[f for f in fns if f[0] in ("name","symbol","decimals","quote","mint","mintFree","freeMint","freeSharesRemaining","freeRemaining","agentIdRegistry","agentRegistry","registry")]
    except Exception as e:
        d["abi_error"]=str(e)[:120]
    got=batch(addr,VIEWS)
    d.update(got or {"_batch_fail":True})
    for sig,data in (("quote(uint256)",sel("quote(uint256)")+enc_u(1)),
                     ("quote(address,uint256)",sel("quote(address,uint256)")+enc(USER)+enc_u(1))):
        d[sig]=call(addr,data)
    for fn in ("name()","symbol()"):
        raw=call(addr,sel(fn))
        if raw and len(raw)>130:
            try:
                ln=int(raw[130:194],16)
                d[fn]=bytes.fromhex(raw[194:194+ln*2]).decode(errors="replace")
            except Exception: d[fn]=raw[:66]
        else: d[fn]=raw
    out[name]=d
    print(name,json.dumps(d)[:1800],flush=True)
json.dump(out,open(BASE+"run-2026-11-12-0001-verify-early2.json","w"),indent=1)
print("VERIFY-EARLY2 DONE")
