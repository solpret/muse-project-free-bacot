#!/usr/bin/env python3
"""Probe Skywe Legion + 05f23bfe game contract. Read-only."""
import json, subprocess
from Crypto.Hash import keccak
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS=["https://bsc-dataseed.binance.org/","https://bsc-dataseed1.bnbchain.org/","https://bsc-dataseed2.bnbchain.org/"]
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64,"0")
def to_int(v):
    try:
        if v is None or v=="0x": return None
        return int(v,16)
    except Exception: return None
def post(ep,payload,timeout=25):
    out=subprocess.run(["curl","-sL","--max-time",str(timeout),"-X","POST",ep,"-H","Content-Type: application/json","-d",json.dumps(payload)],capture_output=True,text=True,timeout=timeout+5).stdout
    return json.loads(out)
def raw(addr,views):
    calls,keys=[],[]
    for i,sig in enumerate(views):
        base=sig.split("(")[0]
        if "(address)" in sig: data=sel(sig)+enc(USER); key=base+"_user"
        else: data=sel(sig); key=base
        calls.append({"jsonrpc":"2.0","id":i+1,"method":"eth_call","params":[{"to":addr,"data":data},"latest"]})
        keys.append(key)
    for ep in EPS:
        try:
            res=post(ep,calls,timeout=25)
            if not isinstance(res,list) or len(res)!=len(calls): continue
            return {key:(None if (isinstance(it,dict) and "error" in it) else (to_int(it.get("result")) if isinstance(it,dict) else None)) for it,key in zip(res,keys)}
        except Exception: continue
    return None
def raw_addr(addr,sig):
    d=raw(addr,[sig])
    if d is None: return None
    v=d.get(sig.split("(")[0])
    return ("0x"+format(v,"040x")) if v is not None else None
def raw_str(addr,sig):
    for ep in EPS:
        try:
            res=post(ep,[{"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":addr,"data":sel(sig)},"latest"]}],timeout=25)
            r=res[0].get("result") if isinstance(res,list) else None
            if r and len(r)>130:
                b=bytes.fromhex(r[2:])
                ln=int.from_bytes(b[32:64],"big")
                return b[64:64+ln].decode(errors="replace")
        except Exception: continue
    return None
out={}
L="0x7256f522e8867de57ea747eeaf83d604d08c47c2"
out["skywe"]=raw(L,["totalMinted()","maxSupply()","mintOpen()","maxPerWallet()","paidPrice()","mintedBy(address)","owner()"])
out["skywe_name"]=raw_str(L,"name()")
out["skywe_symbol"]=raw_str(L,"symbol()")
out["skywe_registry"]=raw_addr(L,"REGISTRY()")
# costOf(address,uint256)
data=sel("costOf(address,uint256)")+enc(USER)+"0"*63+"1"
for ep in EPS:
    try:
        res=post(ep,[{"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":L,"data":data},"latest"]}],timeout=25)
        r=res[0].get("result") if isinstance(res,list) else None
        out["skywe_costOf_user_1"]=to_int(r)
        break
    except Exception: continue
G="0x05f23bfeb3115d6e1905d039f2c70e6928846956"
out["game"]=raw(G,["FREE_QUOTA()","freeClaimed()","freeUsed()","totalBoarded()","gameStart()","gameEnd()","sealedFlag()","owner()"])
out["game_name"]=raw_str(G,"name()")
out["game_symbol"]=raw_str(G,"symbol()")
out["game_registry"]=raw_addr(G,"registry()")
out["game_freeClaimed_user"]=raw(G,["freeClaimed(address)"]).get("freeClaimed_user") if raw(G,["freeClaimed(address)"]) else None
print(json.dumps(out,indent=1))
json.dump(out,open(f"{BASE}/run-2026-11-11-0331-probe3.json","w"),indent=1)
