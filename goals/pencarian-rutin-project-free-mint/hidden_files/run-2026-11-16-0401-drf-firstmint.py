#!/usr/bin/env python3
"""DogeRageFi first-mint verification (run 0401). Read-only.
1) Verify author tx receipt 0x6a3cab48... 2) Binary-search creation block via eth_getCode.
3) eth_getLogs Transfer-from-zero in small chunks around creation block -> first mint block + timestamp."""
import json, subprocess, time
ADDR="0x097ff90fce52f4f0e1f41d6f8c799db9cd67099f".lower()
TX="0x6a3cab48e4e59002a153e8a336486159f0dfebe4a948770f0981c8ee700261a6"
EPS=["https://bsc-dataseed1.bnbchain.org/","https://bsc-dataseed.binance.org/","https://bsc-dataseed2.bnbchain.org/","https://bsc-rpc.publicnode.com/"]
def post(ep, payload, timeout=90):
    r=subprocess.run(["curl","-sL","--max-time",str(timeout),"-X","POST",ep,"-H","Content-Type: application/json","-d",json.dumps(payload)],capture_output=True,text=True,timeout=timeout+10)
    return json.loads(r.stdout)
def rpc(method, params, timeout=90):
    for ep in EPS:
        try:
            j=post(ep,{"jsonrpc":"2.0","id":1,"method":method,"params":params},timeout)
            if isinstance(j,dict) and "result" in j and j["result"] is not None: return j["result"], ep
            if isinstance(j,dict) and "error" in j: print(" ",ep,method,"err",str(j["error"])[:100])
        except Exception as e: print(" ",ep,"exc",str(e)[:80])
    return None, None
# 1) receipt
rc,_=rpc("eth_getTransactionReceipt",[TX])
print("receipt:", json.dumps(rc)[:600] if rc else "FAIL")
if rc:
    print("status:", rc.get("status"), "block:", int(rc.get("blockNumber"),16), "logs:", len(rc.get("logs",[])))
    for lg in rc.get("logs",[])[:3]:
        print(" log topics:", lg.get("topics"), "data:", lg.get("data"))
# 2) head + creation binary search
head,_=rpc("eth_blockNumber",[])
head=int(head,16); print("head:", head)
def has_code(blk):
    r,_=rpc("eth_getCode",[ADDR, hex(blk)])
    return r not in (None,"0x")
lo, hi = head-300000, head  # assume created within last ~300k blocks (~37h); narrow down
# quick check: code at lo?
print("code at head-300000:", has_code(lo))
# binary search first block with code
a,b=lo,head
while b-a>1:
    m=(a+b)//2
    if has_code(m): b=m
    else: a=m
    time.sleep(0.3)
print("creation block ~:", b, " (first block with code)")
# 3) getLogs Transfer from zero around creation block, chunks of 200
ZERO="0x"+"00"*32
TR="0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
first=None
frm=b
while frm<=min(b+2000, head) and first is None:
    to=min(frm+199, head)
    logs,_=rpc("eth_getLogs",[{"fromBlock":hex(frm),"toBlock":hex(to),"address":ADDR,"topics":[TR,ZERO]}])
    if logs is None:
        print(f"getLogs {frm}-{to}: FAIL"); frm=to+1; continue
    print(f"getLogs {frm}-{to}: {len(logs)} transfer-from-zero")
    if logs:
        first=logs[0]; break
    frm=to+1
if first:
    blk=int(first["blockNumber"],16)
    print("first mint block:", blk, "tx:", first.get("transactionHash"))
    binfo,_=rpc("eth_getBlockByNumber",[hex(blk), False])
    ts=int(binfo["timestamp"],16)
    import datetime
    print("first mint time UTC:", datetime.datetime.utcfromtimestamp(ts).isoformat()+"Z",
          "| WIB:", (datetime.datetime.utcfromtimestamp(ts)+datetime.timedelta(hours=7)).isoformat())
    print("first mint value:", int(first["data"],16)/1e18, "DRF")
else:
    print("NO first-mint Transfer found in searched range")
