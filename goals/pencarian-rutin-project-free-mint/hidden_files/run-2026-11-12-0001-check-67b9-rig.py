#!/usr/bin/env python3
"""Check Boltbook-new 0x67b955d6 (code? Sourcify?) + RigForge re-check (lean).
Read-only; writes run-2026-11-12-0001-check-67b9-rig.json."""
import json, subprocess, time
from Crypto.Hash import keccak
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS=["https://bsc-dataseed.binance.org/","https://bsc-dataseed1.bnbchain.org/"]
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64,"0")
def post(ep,payload,timeout=20):
    out=subprocess.run(["curl","-sL","--max-time",str(timeout),"-X","POST",ep,"-H","Content-Type: application/json","-d",json.dumps(payload)],capture_output=True,text=True,timeout=timeout+5).stdout
    return json.loads(out)
def rpc(method,params):
    for ep in EPS:
        try:
            r=post(ep,{"jsonrpc":"2.0","id":1,"method":method,"params":params},timeout=20)
            if "result" in r: return r["result"]
        except Exception: continue
    return None
def to_int(v):
    try: return int(v,16) if v and v!="0x" else None
    except Exception: return None
out={}
addr="0x67b955d6155ac3957dfa61c3855590dcbf2b64f8"
code=rpc("eth_getCode",[addr,"latest"])
out["67b9_code_len"]=len(code)-2 if code else None
out["67b9_is_contract"]=bool(code and code!="0x")
print("67b9 code len:",out["67b9_code_len"],"is_contract:",out["67b9_is_contract"],flush=True)
if out["67b9_is_contract"]:
    try:
        r=subprocess.run(["curl","-sL","--max-time","60",f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi"],capture_output=True,text=True,timeout=65)
        meta=json.loads(r.stdout)
        fns=[f.get("name") for f in meta.get("abi",[]) if f.get("type")=="function"]
        out["67b9_fns"]=fns
        out["67b9_fn_count"]=len(fns)
        print("67b9 fns:",fns,flush=True)
    except Exception as e:
        out["67b9_abi_error"]=str(e)[:120]; print("67b9 ABI ERR",e,flush=True)
RIG="0xa1cc0d7c0534f824f2cf6eeb865a8fede96c8f7d"
rig={}
for name,sig in (("openedAt","openedAt()"),("freeSharesLeft","freeSharesLeft()"),("freeClaimed","freeClaimed()")):
    raw=rpc("eth_call",[{"to":RIG,"data":sel(sig)},"latest"])
    rig[name]=to_int(raw)
raw=rpc("eth_call",[{"to":RIG,"data":sel("freeBooked(address)")+enc(USER)},"latest"])
rig["freeBooked_user"]=to_int(raw)
out["rigforge"]=rig
print("RIGFORGE:",rig,flush=True)
json.dump(out,open(BASE+"run-2026-11-12-0001-check-67b9-rig.json","w"),indent=1)
print("CHECK DONE")
