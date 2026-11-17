#!/usr/bin/env python3
"""Quick-check unknown Boltbook front-page addresses + binanceai pending claim. Read-only."""
import json, subprocess, urllib.request
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
EPS=["https://bsc-dataseed.binance.org/","https://bsc-dataseed1.bnbchain.org/","https://bsc-dataseed2.bnbchain.org/"]
def post(ep,payload,timeout=25):
    out=subprocess.run(["curl","-sL","--max-time",str(timeout),"-X","POST",ep,"-H","Content-Type: application/json","-d",json.dumps(payload)],capture_output=True,text=True,timeout=timeout+5).stdout
    return json.loads(out)
def code(addr):
    for ep in EPS:
        try:
            r=post(ep,{"jsonrpc":"2.0","id":1,"method":"eth_getCode","params":[addr,"latest"]},timeout=25)
            c=r.get("result")
            return ("0x" if c=="0x" else "code %d bytes"%(len(c)//2-1)) if c else None
        except Exception: continue
    return None
def abi_fns(addr):
    try:
        req=urllib.request.Request(f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi",headers={"User-Agent":"curl"})
        d=json.load(urllib.request.urlopen(req,timeout=20))
        abi=d.get("abi") or []
        return [e.get("name") for e in abi if e.get("type")=="function"]
    except Exception as e:
        return f"ERR {e}"
out={}
for a in ["0x8269Ea1629644219a88dbB053D34E8e877596B00","0xe0FeCB4A720d8F39531B3bC3f0Ebb865e10bE191","0x0759c26e1fbe339a7e4282f29b719f56e72f9a1b","0x7256f522e8867de57ea747eeaf83d604d08c47c2","0x05f23bfeb3115d6e1905d039f2c70e6928846956"]:
    fns=abi_fns(a)
    out[a]={"code":code(a),"fns":(fns if isinstance(fns,str) else len(fns)),"fn_list":(fns if isinstance(fns,list) else fns)}
    print(a, out[a]["code"], out[a]["fns"], flush=True)
json.dump(out,open(f"{BASE}/run-2026-11-11-0331-unknown.json","w"),indent=1)
