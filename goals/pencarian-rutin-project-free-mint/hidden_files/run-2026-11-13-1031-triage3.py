#!/usr/bin/env python3
"""Triage3 run 2026-11-13 10:31: Royal Rush Agents first-mint logs retry.
bsc-dataseed eth_getLogs, 100-block chunks over last 1500 blocks, 3 endpoints."""
import json, subprocess, time, datetime
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/", "https://bsc-dataseed3.bnbchain.org/"]
ADDR = "0x2e34d33256C920C33b2a03FEC132A2c74061d5D3"
def post_rpc(ep, payload, timeout=20):
    out = subprocess.run(["curl","-sL","--max-time",str(timeout),"-X","POST",ep,
        "-H","Content-Type: application/json","-d",json.dumps(payload)],
        capture_output=True, text=True, timeout=timeout+5).stdout
    return json.loads(out)
def main():
    t0=time.time(); out={"address":ADDR}
    head=None
    for ep in EPS:
        try:
            r=post_rpc(ep,{"jsonrpc":"2.0","id":1,"method":"eth_blockNumber","params":[]},timeout=15)
            head=int(r.get("result"),16); out["head"]=head; out["head_ep"]=ep; break
        except Exception as e:
            out.setdefault("head_errors",[]).append(str(e)[:80])
    if not head:
        out["first_mint"]=None; out["elapsed_s"]=round(time.time()-t0,1)
        print(json.dumps(out,indent=1)); json.dump(out,open(BASE+"run-2026-11-13-1031-triage3.json","w"),indent=1); return
    TRANSFER="0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
    ZERO="0x"+"00"*32
    logs=[]; out["log_chunks"]=[]
    for start in range(head-1499, head, 100):
        done=False
        for ep in EPS:
            p={"jsonrpc":"2.0","id":1,"method":"eth_getLogs","params":[{
                "fromBlock":hex(start),"toBlock":hex(min(start+99,head)),
                "address":ADDR,"topics":[TRANSFER,ZERO]}]}
            try:
                r=post_rpc(ep,p,timeout=20)
                res=r.get("result")
                if isinstance(res,list):
                    out["log_chunks"].append({"from":start,"to":min(start+99,head),"n":len(res),"ep":ep})
                    logs.extend(res); done=True; break
                else:
                    err=str(r)[:100]
            except Exception as e:
                err=str(e)[:100]
        if not done:
            out["log_chunks"].append({"from":start,"to":min(start+99,head),"error":err})
    if logs:
        logs.sort(key=lambda l:int(l["blockNumber"],16))
        first=logs[0]
        out["first_mint"]={"block":int(first["blockNumber"],16),"tx":first.get("transactionHash"),
                           "count_in_window":len(logs),
                           "distinct_minters":len({l["topics"][2] for l in logs if len(l.get("topics",[]))>2})}
        for ep in EPS:
            try:
                b=post_rpc(ep,{"jsonrpc":"2.0","id":1,"method":"eth_getBlockByNumber",
                    "params":[first["blockNumber"],False]},timeout=15)
                ts=int((b.get("result") or {}).get("timestamp","0x0"),16)
                out["first_mint"]["timestamp"]=ts
                out["first_mint"]["wib"]=datetime.datetime.fromtimestamp(ts,datetime.timezone(datetime.timedelta(hours=7))).strftime("%Y-%m-%d %H:%M:%S WIB")
                break
            except Exception as e:
                continue
    else:
        out["first_mint"]=None
    out["elapsed_s"]=round(time.time()-t0,1)
    print(json.dumps(out,indent=1))
    json.dump(out,open(BASE+"run-2026-11-13-1031-triage3.json","w"),indent=1)
if __name__=="__main__":
    main()
