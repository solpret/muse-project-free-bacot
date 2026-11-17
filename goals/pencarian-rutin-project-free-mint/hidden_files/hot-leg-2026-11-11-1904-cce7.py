#!/usr/bin/env python3
"""1904 follow-up: leg3 verify new S1 0xcce7... + Stampooor targeted retry. Read-only, no preview/mint."""
import json, urllib.request, subprocess, time
from Crypto.Hash import keccak
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
AGENTID=107187496765866644729837695198686237165740365523485558112864918211974996443404
EPS=["https://bsc.nodereal.io/","https://bsc-dataseed.binance.org/","https://bsc.publicnode.com"]
def sel(sig):
    k=keccak.new(digest_bits=256); k.update(sig.encode()); return "0x"+k.hexdigest()[:8]
def enc_addr(a): return a.lower().replace("0x","").rjust(64,"0")
def enc_u(n): return "%064x"%n
def call(addr,sig,args="",timeout=15):
    data=sel(sig)+args
    body=json.dumps({"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":addr,"data":data},"latest"]}).encode()
    errs=[]
    for ep in EPS:
        try:
            req=urllib.request.Request(ep,data=body,headers={"Content-Type":"application/json"})
            with urllib.request.urlopen(req,timeout=timeout) as r: j=json.loads(r.read().decode())
            if "error" in j: return {"error":str(j["error"])[:150]}
            raw=j["result"]
            if raw in (None,"0x"): return {"error":"empty-return"}
            return raw
        except Exception as e: errs.append(f"{ep.split('/')[2]}:{type(e).__name__}")
    return {"error":"all-endpoints-failed: "+",".join(errs)}
def dec(raw):
    if isinstance(raw,dict): return raw
    try:
        h=raw[2:]
        # single uint256
        if len(h)>=64: return int(h[:64],16)
        return raw
    except Exception: return raw
def dec_str(raw):
    # try decode string return (offset,len,bytes)
    if isinstance(raw,dict): return raw
    try:
        h=raw[2:]
        off=int(h[:64],16)*2; ln=int(h[64:128],16)
        return bytes.fromhex(h[off+64:off+64+ln*2]).decode(errors="replace")
    except Exception: return raw
def block():
    body=json.dumps({"jsonrpc":"2.0","id":1,"method":"eth_blockNumber","params":[]}).encode()
    for ep in EPS:
        try:
            req=urllib.request.Request(ep,data=body,headers={"Content-Type":"application/json"})
            with urllib.request.urlopen(req,timeout=10) as r: return int(json.loads(r.read().decode())["result"],16)
        except Exception: continue
    return None
blk=block()
print("BLOCK",blk)
# --- fetch ABI for cce7 ---
out=subprocess.run(["curl","-s","-m","20","https://sourcify.dev/server/v2/contract/56/0xcce7e755D343912AA0dBBc617FEA9bb193Efb32a?fields=abi,metadata"],capture_output=True,timeout=30)
doc=json.loads(out.stdout.decode(errors="replace"))
abi=doc.get("abi",[])
json.dump(doc,open(BASE+"hot-leg-2026-11-11-1904-cce7-abi.json","w"),indent=1)
fns={}
for e in abi:
    if e.get("type")=="function": fns.setdefault(e["name"],[]).append(e)
print("FNS",sorted(fns.keys()))
meta=doc.get("metadata",{})
print("META_KEYS",list(meta.keys()) if isinstance(meta,dict) else type(meta))
# name/symbol
res={}
C="0xcce7e755D343912AA0dBBc617FEA9bb193Efb32a"
U=enc_addr(USER)
for name,sig,args,decoder in [
 ("name","name()", "",dec_str),("symbol","symbol()","",dec_str),
 ("totalSupply","totalSupply()","",dec),("freeMinted","freeMinted()","",dec),
 ("freeClaimed_total","freeClaimed()","",dec),("FREE_SUPPLY","FREE_SUPPLY()","",dec),
 ("FREE_SLOTS","FREE_SLOTS()","",dec),("freeSupply","freeSupply()","",dec),
 ("mintOpen","mintOpen()","",dec),("opened","opened()","",dec),
 ("mintStart","mintStart()","",dec),("startTime","startTime()","",dec),
 ("freeAvailable_user","freeAvailable(address)",U,dec),
 ("freeClaimed_user","freeClaimed(address)",U,dec),
 ("freeUsed_user","freeUsed(address)",U,dec),
 ("balanceOf_user","balanceOf(address)",U,dec),
 ("REGISTRY","REGISTRY()","",dec_str),
 ("contractURI","contractURI()","",dec_str),
]:
    if name.split("_")[0] not in fns and name not in ("freeClaimed_total",):
        # still try if fn exists under exact name
        base=name.split("_")[0]
        if base not in fns: 
            res[name]={"skipped":"no such fn in ABI"}
            continue
    raw=call(C,sig,args)
    res[name]=decoder(raw) if not isinstance(raw,dict) else raw
print(json.dumps(res,indent=1,default=str))
# quote(user,1) if quote exists with (address,uint256)
if "quote" in fns:
    print("QUOTE_RAW",call(C,"quote(address,uint256)",U+enc_u(1)))
# Stampooor retry
S="0x467696af8c2206B977B24081445104632dc1D459"
st={}
for name,sig,args in [("freeMinted","freeMinted()",""),("totalMinted","totalMinted()",""),("FREE_SUPPLY","FREE_SUPPLY()",""),("mintOpen","mintOpen()",""),("freeAvailable_user","freeAvailable(address)",U),("balanceOf_user","balanceOf(address)",U)]:
    st[name]=dec(call(S,sig,args))
print("STAMPOOOR",json.dumps(st,default=str))
json.dump({"block":blk,"cce7":res,"stampooor":st,"fns":sorted(fns.keys())},open(BASE+"hot-leg-2026-11-11-1904-cce7.json","w"),indent=1,default=str)
