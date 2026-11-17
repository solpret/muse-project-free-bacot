#!/usr/bin/env python3
"""Triage-2 run 2301: disambiguate S1-hit free pool + 0x8b05 agent gating. Read-only."""
import json, subprocess
from Crypto.Hash import keccak
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
RPCS=["https://bsc-dataseed1.bnbchain.org/","https://bsc-dataseed2.bnbchain.org/","https://bsc-dataseed.binance.org/"]
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64,"0")
def post_rpc(ep,payload,timeout=25):
    out=subprocess.run(["curl","-sL","--max-time",str(timeout),"-X","POST",ep,"-H","Content-Type: application/json","-d",json.dumps(payload)],capture_output=True,text=True,timeout=timeout+5).stdout
    return json.loads(out)
def to_int(v):
    try:
        if v is None or v=="0x": return None
        return int(v,16)
    except Exception: return None
def batch(addr,views):
    calls,keys=[],[]
    for i,sig in enumerate(views):
        base=sig.split("(")[0]
        if "(address)" in sig:
            data=sel(sig)+enc(USER); key=base+"_user"
        else:
            data=sel(sig); key=base
        calls.append({"jsonrpc":"2.0","id":i+1,"method":"eth_call","params":[{"to":addr,"data":data},"latest"]})
        keys.append(key)
    for ep in RPCS:
        try:
            res=post_rpc(ep,calls)
            if not isinstance(res,list) or len(res)!=len(calls): continue
            return {k:(None if (isinstance(it,dict) and "error" in it) else (to_int(it.get("result")) if isinstance(it,dict) else None)) for it,k in zip(res,keys)}
        except Exception: continue
    return None
def call_raw(addr,data):
    for ep in RPCS:
        try:
            res=post_rpc(ep,{"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":addr,"data":data},"latest"]})
            if isinstance(res,dict) and "result" in res: return res["result"]
        except Exception: continue
    return None
out={}
A="0x5a52fe87c7F498653C596D856F1354E0a2895a07"
r=batch(A,["publicFreeRemaining()","totalPaidShares()","saleClockStart()","totalShares()","freeSharesRemaining()","launched()","pair()","token()"])
out["s1_hit2"]=r; print("S1-HIT2:",json.dumps(r))
# token() address -> name/symbol
tok=r.get("token")
if tok:
    ta="0x"+format(tok % (1<<160),"040x")
    print("S1 token addr:",ta)
    out["s1_hit2"]["token_addr"]=ta
    # name() as string
    raw=call_raw(ta, sel("name()"))
    print("token name raw:", raw)
C="0x8b059e611E5f16b4659f81698CDbcB3dcfcDFDF1"
r2=batch(C,["AGENT_ID()","freeRemaining()","priceFor(address)","freeClaimedBy(address)","freeStart()","dripStart()","creator()","FREE_PER_WALLET()","genesisHeld(address)"])
out["c8b05_2"]=r2; print("8B05-2:",json.dumps(r2))
ag=r2.get("AGENT_ID")
print("AGENT_ID() =", hex(ag) if isinstance(ag,int) else ag)
# name/symbol decode
for fn in ("name()","symbol()"):
    raw=call_raw(C, sel(fn))
    print(fn, "raw:", str(raw)[:200])
    if raw and len(raw)>130:
        try:
            b=bytes.fromhex(raw[2:])
            ln=int.from_bytes(b[64:96],"big")
            print("  decoded:", b[96:96+ln].decode(errors="replace"))
        except Exception as e: print("  decode err",e)
json.dump(out,open(f"{BASE}/run-2026-11-09-2301-triage2.json","w"),indent=1)
print("TRIAGE2 DONE")
