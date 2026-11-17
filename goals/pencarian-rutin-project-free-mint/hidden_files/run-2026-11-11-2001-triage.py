#!/usr/bin/env python3
"""Triage run 2001: Boltbook-new 0xe10a... + feed ABI-fetch errors 0x62dC/0x3a84.
Read-only; writes run-2026-11-11-2001-triage.json. No preview/mint."""
import json, subprocess, urllib.request, time
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
REG="60b9262456de011f7d15a54cdd8c48baaa8b022f"
FREE=["freeSharesRemaining","freeClaimed","freeFor","freeLeft","freeUsed","freeAvailable","freeSharePoolExhausted","freeSharesClaimed","freeMinted","freeCardsRemaining","freeSupply","FREE_SUPPLY"]
def get(url,timeout=25):
    req=urllib.request.Request(url,headers={"User-Agent":"free-bacot/1.0"})
    with urllib.request.urlopen(req,timeout=timeout) as r: return r.read().decode(errors="replace")
def eth_call(addr,data):
    payload={"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":addr,"data":data},"latest"]}
    for ep in ["https://bsc-dataseed.binance.org/","https://bsc-dataseed1.bnbchain.org/"]:
        try:
            out=subprocess.run(["curl","-sL","--max-time","25","-X","POST",ep,"-H","Content-Type: application/json","-d",json.dumps(payload)],capture_output=True,text=True,timeout=30).stdout
            j=json.loads(out)
            if "result" in j: return j["result"]
        except Exception as e: pass
    return None
from Crypto.Hash import keccak
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
out={}
for addr in ["0xe10a2432d9c4bcde9e896c0a0beaf36d674e946c","0x62dC2216079671561b1CFF0564dEa23A6e01C275","0x3a84F41c71ba67CD62493B12448C175B0aD2F741"]:
    d={"address":addr}
    try:
        meta=json.loads(get(f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi,sources"))
        abi=meta.get("abi",[])
        fns=[f.get("name") for f in abi if isinstance(f,dict) and f.get("type")=="function"]
        d["verified"]=True; d["fn_count"]=len(fns)
        d["has_mint"]=any("mint" in (f or "").lower() for f in fns)
        d["free_views"]=[f for f in fns if f in FREE]
        src=json.dumps(meta.get("sources",{}))
        d["agent_ref"]=REG in src.lower()
        d["name"]=next((f for f in []),None)
        d["early_shape"]=bool(d["agent_ref"] or d["free_views"])
    except Exception as e:
        d["verified"]=None; d["error"]=f"{type(e).__name__}: {str(e)[:120]}"
    ts=eth_call(addr, sel("totalSupply()"))
    d["totalSupply"]=int(ts,16) if ts and ts!="0x" else None
    print(addr, d, flush=True)
    out[addr]=d
json.dump(out, open(BASE+"run-2026-11-11-2001-triage.json","w"), indent=1)
print("TRIAGE DONE")
