#!/usr/bin/env python3
"""Hot-leg 1559 retry2: first retry chunk-1 (24 calls) returned all-null while
chunk-2 worked - suspected batch transport failure, not contract state.
Re-run only the two contracts that matter: 0xd621 shape-check + NEW5893 re-read,
19 calls in one chunk."""
import json, subprocess, time
from eth_hash.auto import keccak
HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
USER_PAD = USER[2:].lower().rjust(64, "0")
def sel(sig): return "0x" + keccak(sig.encode()).hex()[:8]
D="0xd621fe1c3af088ed5f7f4f776ad48daa24b35c67"
N="0x5893199322A5300775912ebD236d8f1fEFC700Db"
calls=[]; keys=[]
def add(addr,fn,uarg=False):
    data=sel(fn+("(address)" if uarg else "()"))+(USER_PAD if uarg else "")
    calls.append({"jsonrpc":"2.0","id":len(calls),"method":"eth_call","params":[{"to":addr,"data":data},"latest"]})
    keys.append((addr,fn+("_user" if uarg else "")))
for fn in ["mintFree","mint","quote","name","symbol","decimals","freeMinted","FREE_SLOTS","registry","AGENT_REGISTRY","agentGate","agentRegistry","freeClaimed"]:
    add(D,fn, uarg=(fn=="freeClaimed"))
for fn in ["freeMinted","FREE_SUPPLY","saleOpen","mintOpen","totalSupply"]:
    add(N,fn)
add(N,"freeClaimed",True)
body=json.dumps(calls)
p=subprocess.run(["curl","-sS","-m","25","-A","Mozilla/5.0","-H","Content-Type: application/json","-d",body,"https://bsc-dataseed.binance.org/"],capture_output=True,text=True,timeout=30)
res={}; raw=p.stdout if p.returncode==0 else ""
try:
    resp=json.loads(raw); items=resp if isinstance(resp,list) else [resp]
    by={it.get("id"):it for it in items if isinstance(it,dict)}
    for c in calls:
        it=by.get(c["id"],{}); r=it.get("result")
        a,fn=keys[c["id"]]
        v=None
        if r and r!="0x":
            try: v=int(r[-64:],16)
            except Exception: v=r
        res.setdefault(a,{})[fn]={"v":v,"err":it.get("error")}
except Exception as e:
    res={"parse_error":str(e),"raw_head":raw[:300],"curl_rc":p.returncode}
out={"run":"hot-leg 1559 retry2","reads":res}
json.dump(out,open(f"{HF}/hot-leg-2026-11-13-1559-retry2.json","w"),indent=1)
print(json.dumps(out,indent=1))
