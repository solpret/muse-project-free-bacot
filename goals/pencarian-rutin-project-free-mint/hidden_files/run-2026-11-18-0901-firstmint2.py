#!/usr/bin/env python3
"""First-mint check E09A via SINGLE (non-batch) eth_getLogs, bsc-dataseed + dataseed1.
Read-only."""
import json, subprocess, time, datetime
E09A="0xE09Ab25732b1e1FdA7ad4d551EEA0aAC65aD0711"
T0="0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO="0x0000000000000000000000000000000000000000000000000000000000000000"
EPS=["https://bsc-dataseed.binance.org/","https://bsc-dataseed1.bnbchain.org/","https://bsc-dataseed2.bnbchain.org/"]
def single(ep, method, params, timeout=30):
    payload={"jsonrpc":"2.0","id":1,"method":method,"params":params}
    r=subprocess.run(["curl","-s","-L","--max-time",str(timeout),ep,"-H","Content-Type: application/json","-d",json.dumps(payload)],capture_output=True,timeout=timeout+5)
    return json.loads(r.stdout.decode())
head=None
for ep in EPS:
    try:
        res=single(ep,"eth_blockNumber",[])
        head=int(res["result"],16); print("head via",ep,":",head); break
    except Exception as e:
        print("head fail",ep,str(e)[:100])
if head is None: raise SystemExit("no head")
# search backwards in 5000-block chunks from head, single calls, stop at first hit
first=None; total=0; minters=set(); tried=0; errs=0
frm=head-4999
while frm>head-400000 and first is None:
    to=min(frm+4999,head)
    ok=False
    for ep in EPS:
        try:
            res=single(ep,"eth_getLogs",[{"fromBlock":hex(frm),"toBlock":hex(to),"address":E09A,"topics":[T0,ZERO]}])
            if "result" in res and isinstance(res["result"],list):
                logs=res["result"]; ok=True; break
            else:
                print("chunk",frm,"-",to,"err via",ep,":",str(res.get("error"))[:100])
        except Exception as e:
            print("chunk exc",frm,ep,str(e)[:100])
    if not ok:
        errs+=1
        if errs>=3: print("too many chunk errors, abort"); break
        frm=to+1; continue
    tried+=1
    if logs:
        total+=len(logs)
        for lg in logs:
            b=int(lg["blockNumber"],16)
            if first is None or b<first[0]: first=(b,lg["transactionHash"])
            if len(lg.get("topics",[]))>2: minters.add(lg["topics"][2])
        print("chunk",frm,"-",to,"logs:",len(logs),"first so far:",first)
    frm=to+1
    time.sleep(0.3)
print("chunks ok:",tried,"errors:",errs,"mint logs:",total,"minters:",len(minters))
print("FIRST MINT:",first)
if first:
    for ep in EPS:
        try:
            res=single(ep,"eth_getBlockByNumber",[hex(first[0]),False])
            ts=int(res["result"]["timestamp"],16)
            print("first mint UTC:",datetime.datetime.utcfromtimestamp(ts).isoformat(),"| WIB:",datetime.datetime.utcfromtimestamp(ts+7*3600).isoformat())
            break
        except Exception as e:
            print("block ts fail",ep,str(e)[:80])
json.dump({"head":head,"first_mint":first,"mint_logs":total,"distinct_minters":len(minters),"chunks_ok":tried},open("run-2026-11-18-0901-firstmint2.json","w"),indent=1)
