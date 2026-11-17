#!/usr/bin/env python3
"""Probe bead62 (new Boltbook) + ORYN sale (hot-leg flag) — read-only."""
import json, subprocess, time
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
        elif sig.endswith("()") and base in ("balanceOf","freeClaimed","hasFreeClaimed","hasAgentId"):
            data=sel(sig)+enc(USER); key=base+"_user"
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
def raw_str(addr,sig):
    # string-returning view: decode utf8 from result
    for ep in EPS:
        try:
            res=post(ep,[{"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":addr,"data":sel(sig)},"latest"]}],timeout=25)
            r=res[0].get("result") if isinstance(res,list) else None
            if r and len(r)>130:
                b=bytes.fromhex(r[2:])
                ln=int.from_bytes(b[64:96],"big")
                return b[96:96+ln].decode(errors="replace")
            return None
        except Exception: continue
    return None
def raw_addr(addr,sig):
    d=raw(addr,[sig])
    if d is None: return None
    v=d.get(sig.split("(")[0])
    if v is None: return None
    return "0x"+format(v,"040x")

out={}
B="0xbead62a6c6b9a43ece68645f2328e0ebd015dbf2"
out["bead62"]=raw(B,["totalSupply()","totalMinted()","MAX_SUPPLY()","PRICE()","freeAvailable()","freeUsed()","mintOpen()","isWorking()","owner()","balanceOf(address)","freeClaimed(address)"])
out["bead62_name"]=raw_str(B,"name()")
out["bead62_symbol"]=raw_str(B,"symbol()")
out["bead62_agentRegistry"]=raw_addr(B,"agentIdRegistry()")
out["bead62_contractURI"]=raw_str(B,"contractURI()")
O="0x96135a41FA155752dc7154CDcaA480f2fBEC1493"
out["oryn"]=raw(O,["FREE_POOL()","freePoolRemaining()","freePoolPaidOut()","currentFreeRound()","freeClaimsThisRound()","CLAIMS_PER_FREE_ROUND()","LOT_PRICE()","totalLotsSold()","liquidityOpened()","paused()","owner()","hasAgentId(address)","hasFreeClaimed(address)"])
out["oryn_token"]=raw_addr(O,"token()")
out["oryn_identity"]=raw_addr(O,"identityContract()")
out["oryn_freeRound1"]=None
# freeRound(uint256) returns tuple; call directly
try:
    data=sel("freeRound(uint256)")+"0"*63+"1"
    for ep in EPS:
        try:
            res=post(ep,[{"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":O,"data":data},"latest"]}],timeout=25)
            r=res[0].get("result") if isinstance(res,list) else None
            if r and len(r)>2:
                b=bytes.fromhex(r[2:])
                out["oryn_freeRound1"]=[int.from_bytes(b[i:i+32],"big") for i in range(0,len(b),32)]
                break
        except Exception: continue
except Exception as e:
    out["oryn_freeRound1_err"]=str(e)
tok=out["oryn_token"]
if tok:
    out["oryn_token_name"]=raw_str(tok,"name()")
    out["oryn_token_symbol"]=raw_str(tok,"symbol()")
    out["oryn_token_totalSupply"]=raw(tok,["totalSupply()","decimals()"])
print(json.dumps(out,indent=1))
json.dump(out,open(f"{BASE}/run-2026-11-11-0331-probe.json","w"),indent=1)
