#!/usr/bin/env python3
"""Free-probe run 0801: agentFreeUsed/paidMinted for the 4x 2000-cap items. Read-only."""
import json, subprocess, time
from Crypto.Hash import keccak
EPS=["https://bsc-dataseed.binance.org/","https://bsc-dataseed1.bnbchain.org/","https://bsc-dataseed2.bnbchain.org/"]
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def to_int(v):
    try: return int(v,16) if v not in (None,"0x") else None
    except Exception: return None
def post(ep,payload,timeout=25):
    out=subprocess.run(["curl","-sL","--max-time",str(timeout),"-X","POST",ep,"-H","Content-Type: application/json","-d",json.dumps(payload)],capture_output=True,text=True,timeout=timeout+5).stdout
    return json.loads(out)
ADDRS={"NIGHTFORGE":"0x0000000000000000000000000000000000000000"}
import json as j
snap=j.load(open("onchain-snapshot.json"))
for n in ("NIGHTFORGE","SOLDERCATS","REWINDCLUB","LCDSPRITE"):
    ADDRS[n]=snap["contracts"][n]["address"]
out={}
for name,addr in ADDRS.items():
    if addr=="0x0000000000000000000000000000000000000000": continue
    calls=[{"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":addr,"data":sel("agentFreeUsed()")},"latest"]},
           {"jsonrpc":"2.0","id":2,"method":"eth_call","params":[{"to":addr,"data":sel("paidMinted()")},"latest"]},
           {"jsonrpc":"2.0","id":3,"method":"eth_blockNumber","params":[]}]
    got=None
    for ep in EPS:
        try:
            r=post(ep,calls,timeout=25)
            if isinstance(r,list) and len(r)==3: got=r; break
        except Exception: continue
    if got:
        out[name]={"agentFreeUsed()":to_int(got[0].get("result")),"paidMinted()":to_int(got[1].get("result")),"block":int(got[2]["result"],16)}
        print(name, out[name], flush=True)
    else:
        out[name]={"agentFreeUsed()":None,"paidMinted()":None,"block":None}
        print(name, "FAIL", flush=True)
json.dump(out,open("run-2026-11-11-0801-freeprobe.json","w"),indent=1)
