#!/usr/bin/env python3
"""DogeRageFi backscan pass 2: from author-mint block 133803783 downward, 200-block chunks,
retry failed chunks once on another endpoint, stop after 4 CONSECUTIVE empty chunks."""
import json, subprocess, time, datetime
ADDR="0x097ff90fce52f4f0e1f41d6f8c799db9cd67099f".lower()
EPS=["https://bsc-dataseed1.bnbchain.org/","https://bsc-dataseed.binance.org/","https://bsc-dataseed2.bnbchain.org/","https://bsc-rpc.publicnode.com/"]
TR="0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO="0x"+"00"*32
def post(ep, payload, timeout=60):
    r=subprocess.run(["curl","-sL","--max-time",str(timeout),"-X","POST",ep,"-H","Content-Type: application/json","-d",json.dumps(payload)],capture_output=True,text=True,timeout=timeout+10)
    return json.loads(r.stdout)
def getlogs(frm,to):
    for ep in EPS:
        try:
            j=post(ep,{"jsonrpc":"2.0","id":1,"method":"eth_getLogs","params":[{"fromBlock":hex(frm),"toBlock":hex(to),"address":ADDR,"topics":[TR,ZERO]}]})
            if isinstance(j,dict) and isinstance(j.get("result"),list): return j["result"]
        except Exception: pass
        time.sleep(1)
    return None
def block_ts(blk):
    for ep in EPS:
        try:
            j=post(ep,{"jsonrpc":"2.0","id":1,"method":"eth_getBlockByNumber","params":[hex(blk),False]})
            if isinstance(j,dict) and j.get("result"): return int(j["result"]["timestamp"],16)
        except Exception: pass
    return None
def wib(ts): return (datetime.datetime.utcfromtimestamp(ts)+datetime.timedelta(hours=7)).strftime("%Y-%m-%d %H:%M:%S WIB")
START=133803783; LIMIT=START-12000
to=START; consec_empty=0; earliest=None; total=0; chunks=0; failed=0
while to>LIMIT and consec_empty<4:
    frm=max(to-199, LIMIT)
    logs=getlogs(frm,to)
    chunks+=1
    if logs is None:
        print(f"chunk {frm}-{to}: FAIL (all endpoints)"); failed+=1; to=frm-1; time.sleep(2); continue
    total+=len(logs)
    print(f"chunk {frm}-{to}: {len(logs)} mints", flush=True)
    if logs:
        earliest=logs[0]; consec_empty=0
    else:
        consec_empty+=1
    to=frm-1
    time.sleep(1)
print("chunks:",chunks,"failed:",failed,"total mints in window:",total)
if earliest:
    blk=int(earliest["blockNumber"],16); ts=block_ts(blk)
    print("EARLIEST mint found: block",blk,"time",wib(ts) if ts else "?","tx",earliest.get("transactionHash"))
    print("consec_empty at stop:",consec_empty,"-> boundary", "FOUND" if consec_empty>=4 else "NOT found in window")
else:
    print("no mints found?!")
