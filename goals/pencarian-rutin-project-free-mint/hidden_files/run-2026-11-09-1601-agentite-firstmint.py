#!/usr/bin/env python3
"""Agentite first-mint getLogs attempt run 1601 — contract-scoped Transfer logs.
Read-only. Tries dataseed then publicnode, one window each."""
import json, subprocess
AG="0xA587F3Ef2BEc919255fCfFF36A6BdD82cf4D87e2"
TR="0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
def h(n): return hex(n)
EPS=["https://bsc-dataseed1.bnbchain.org/","https://bsc.publicnode.com","https://bsc-dataseed2.bnbchain.org/"]
out={"contract":AG,"attempts":[]}
for ep in EPS:
    try:
        p={"jsonrpc":"2.0","id":1,"method":"eth_getLogs","params":[{"fromBlock":h(132555000),"toBlock":h(132560000),"address":AG,"topics":[TR]}]}
        r=subprocess.run(["curl","-sL","--max-time","30","-X","POST",ep,"-H","Content-Type: application/json","-d",json.dumps(p)],capture_output=True,text=True,timeout=35)
        d=json.loads(r.stdout)
        if isinstance(d,dict) and "error" in d:
            out["attempts"].append({"ep":ep,"ok":False,"error":str(d["error"])[:200]})
            print(ep,"ERROR",str(d["error"])[:150],flush=True)
            continue
        logs=d.get("result",[])
        out["attempts"].append({"ep":ep,"ok":True,"n_logs":len(logs)})
        print(ep,"OK logs=",len(logs),flush=True)
        if logs:
            first=logs[0]
            out["first_mint"]={"block":int(first["blockNumber"],16),"tx":first["transactionHash"],"logIndex":int(first["logIndex"],16)}
            out["n_mints_in_window"]=len(logs)
            break
        out["first_mint"]=None
        break
    except Exception as e:
        out["attempts"].append({"ep":ep,"ok":False,"error":str(e)[:200]})
        print(ep,"EXC",str(e)[:150],flush=True)
print(json.dumps(out,indent=1))
json.dump(out,open("run-2026-11-09-1601-agentite-firstmint.json","w"),indent=1)
