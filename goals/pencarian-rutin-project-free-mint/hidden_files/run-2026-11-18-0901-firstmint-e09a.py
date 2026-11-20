#!/usr/bin/env python3
"""First-mint Transfer check AlphaPulse Badge V1 0xE09A via bsc-dataseed eth_getLogs.
Chunked 20000 blocks, Transfer topic, from zero address. Read-only."""
import json, subprocess, time
ADDR="0xE09Ab25732b1e1FdA7ad4d551EEA0aAC65aD0711"
RPC="https://bsc-dataseed.binance.org/"
T0="0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO="0x0000000000000000000000000000000000000000000000000000000000000000"
def post(payload, timeout=30):
    r=subprocess.run(["curl","-s","-L","--max-time",str(timeout),RPC,"-H","Content-Type: application/json","-d",json.dumps(payload)],capture_output=True,timeout=timeout+5)
    return json.loads(r.stdout.decode())
head=int(post([{"jsonrpc":"2.0","id":1,"method":"eth_blockNumber","params":[]}])[0]["result"],16)
print("head:", head)
# search backwards from head in 20000-block chunks, earliest first-mint
LO=133900000  # ~15 Nov, safely before first-seen 17 Nov 13:29 (~13407xxxx)
first=None; total=0; minters=set(); chunks=0
frm=LO
while frm<=head:
    to=min(frm+19999, head)
    try:
        resp=post([{"jsonrpc":"2.0","id":1,"method":"eth_getLogs","params":[{"fromBlock":hex(frm),"toBlock":hex(to),"address":ADDR,"topics":[T0,ZERO]}]}])
        logs=resp[0].get("result",[]) if isinstance(resp,list) else resp.get("result",[])
        if logs:
            total+=len(logs)
            for lg in logs:
                b=int(lg["blockNumber"],16)
                if first is None or b<first[0]:
                    first=(b, lg["transactionHash"], lg.get("topics",[]))
                if len(lg.get("topics",[]))>2:
                    minters.add(lg["topics"][2])
        chunks+=1
    except Exception as e:
        print("chunk fail", frm, to, str(e)[:120]); break
    frm=to+1
    if first is not None and frm>first[0]+20000:
        break
print("chunks:", chunks, "mint logs found:", total, "distinct minters:", len(minters))
print("first mint:", first)
if first:
    blk=post([{"jsonrpc":"2.0","id":1,"method":"eth_getBlockByNumber","params":[hex(first[0]),False]}])
    ts=int(blk[0]["result"]["timestamp"],16)
    import datetime
    print("first mint block ts UTC:", datetime.datetime.utcfromtimestamp(ts).isoformat(), "| WIB:", datetime.datetime.utcfromtimestamp(ts+7*3600).isoformat())
json.dump({"head":head,"first_mint":first,"mint_logs":total,"distinct_minters":len(minters)}, open("run-2026-11-18-0901-firstmint-e09a.json","w"), indent=1)
