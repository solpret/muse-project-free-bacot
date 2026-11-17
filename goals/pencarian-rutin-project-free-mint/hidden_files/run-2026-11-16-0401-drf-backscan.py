#!/usr/bin/env python3
"""DogeRageFi: timestamp of author-mint block + backward getLogs scan for earliest Transfer-from-zero.
Read-only. Public RPC, 200-block chunks, endpoint rotation, stops at first empty chunk (launch boundary)."""
import json, subprocess, time, datetime
ADDR="0x097ff90fce52f4f0e1f41d6f8c799db9cd67099f".lower()
EPS=["https://bsc-dataseed1.bnbchain.org/","https://bsc-dataseed.binance.org/","https://bsc-dataseed2.bnbchain.org/","https://bsc-rpc.publicnode.com/"]
TR="0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO="0x"+"00"*32
def post(ep, payload, timeout=60):
    r=subprocess.run(["curl","-sL","--max-time",str(timeout),"-X","POST",ep,"-H","Content-Type: application/json","-d",json.dumps(payload)],capture_output=True,text=True,timeout=timeout+10)
    return json.loads(r.stdout)
def rpc(method, params, timeout=60):
    for ep in EPS:
        try:
            j=post(ep,{"jsonrpc":"2.0","id":1,"method":method,"params":params},timeout)
            if isinstance(j,dict) and "result" in j and j["result"] is not None: return j["result"]
        except Exception: pass
    return None
def wib(ts): return (datetime.datetime.utcfromtimestamp(ts)+datetime.timedelta(hours=7)).strftime("%Y-%m-%d %H:%M:%S WIB")
head=int(rpc("eth_blockNumber",[]),16)
print("head:", head)
b=rpc("eth_getBlockByNumber",[hex(133803783), False])
ts=int(b["timestamp"],16)
print("author-mint block 133803783 time:", wib(ts), f"(unix {ts})")
# backward scan
earliest=None; empty_chunks=0; scanned=0
to=head
while to>head-8000 and empty_chunks<2:
    frm=max(to-199, head-8000)
    logs=rpc("eth_getLogs",[{"fromBlock":hex(frm),"toBlock":hex(to),"address":ADDR,"topics":[TR,ZERO]}])
    if logs is None:
        print(f"chunk {frm}-{to}: RPC FAIL, skip"); to=frm-1; time.sleep(2); continue
    scanned+=1
    print(f"chunk {frm}-{to}: {len(logs)} mints", flush=True)
    if logs:
        earliest=logs[0]
    else:
        empty_chunks+=1
    to=frm-1
    time.sleep(1)
if earliest:
    blk=int(earliest["blockNumber"],16)
    b2=rpc("eth_getBlockByNumber",[hex(blk), False])
    ts2=int(b2["timestamp"],16)
    print("EARLIEST mint in scanned window: block", blk, "time", wib(ts2), "tx", earliest.get("transactionHash"))
    print("NOTE: window scanned back to", head-8000, "; empty_chunks:", empty_chunks, "-> boundary found" if empty_chunks else "-> NO boundary in window, launch may be earlier")
else:
    print("no mints found in window (unexpected)")
print("chunks scanned:", scanned)
