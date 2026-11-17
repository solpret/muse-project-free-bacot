#!/usr/bin/env python3
"""Hot-leg 1559 retry: (a) deeper shape-check on probe-possible-sale
0xd621fe1c3af088ed5f7f4f776ad48daa24b35c67 (freeClaimed+FREE_SUPPLY+mintOpen,
no registry hit in probe) - check mintFree/quote/name/symbol/registry variants;
(b) re-read NEW5893, 2e34, binanceai, OLIVER whose views returned null in main run."""
import json, subprocess, time
from eth_hash.auto import keccak
HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
USER_PAD = USER[2:].lower().rjust(64, "0")
def sel(sig): return "0x" + keccak(sig.encode()).hex()[:8]
def curl(url, data=None, timeout=25):
    cmd = ["curl","-sS","-m",str(timeout),"-A","Mozilla/5.0"]
    if data is not None: cmd += ["-H","Content-Type: application/json","-d",data]
    cmd.append(url)
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout+5)
        return p.stdout if p.returncode==0 and p.stdout else None
    except Exception: return None
def rpc_chunked(calls, timeout=25):
    out=[]
    for i in range(0,len(calls),24):
        chunk=calls[i:i+24]
        body=curl("https://bsc-dataseed.binance.org/", data=json.dumps(chunk), timeout=timeout)
        if not body:
            out+=[(c["id"],None,"fetch-failed") for c in chunk]; continue
        try:
            resp=json.loads(body); items=resp if isinstance(resp,list) else [resp]
            by={it.get("id"):it for it in items if isinstance(it,dict)}
            for c in chunk:
                it=by.get(c["id"],{}); out.append((c["id"],it.get("result"),it.get("error")))
        except Exception as e:
            out+=[(c["id"],None,f"parse-failed: {e}") for c in chunk]
    return out
D="0xd621fe1c3af088ed5f7f4f776ad48daa24b35c67"
N="0x5893199322A5300775912ebD236d8f1fEFC700Db"
T="0x2e34d33256C920C33b2a03FEC132A2c74061d5D3"
B="0x46cb1D3efd4307506Cda7EbBa5a51be64746739E"
O="0xad86e4d52e55709d1bda08f922853d4b109e0810"
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
for fn in ["freeMinted","freeRemaining","FREE_MAX","mintOpen"]:
    add(T,fn)
add(B,"launched"); add(B,"claimable",True)
for fn in ["freeMinted","FREE_MAX","freeRemaining","mintOpen"]:
    add(O,fn)
res={}
for cid,r,err in rpc_chunked(calls):
    a,fn=keys[cid]
    v=None
    if r and r!="0x":
        try: v=int(r[-64:],16)
        except Exception:
            try: v=r
            except Exception: v=None
    res.setdefault(a,{})[fn]=v
out={"run":"hot-leg 1559 retry","started_wib":time.strftime("%Y-%m-%dT%H:%M:%S+07:00",time.gmtime(time.time()+7*3600)),"reads":res}
json.dump(out,open(f"{HF}/hot-leg-2026-11-13-1559-retry.json","w"),indent=1)
print(json.dumps(out,indent=1))
