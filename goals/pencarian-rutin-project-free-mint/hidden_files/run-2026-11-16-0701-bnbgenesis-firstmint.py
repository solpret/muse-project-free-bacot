#!/usr/bin/env python3
"""First-mint check for BNB Genesis 0x1595 via bsc-dataseed eth_getLogs (Ankr 401 dead).
Transfer(from=0x0) chunks of 2000 blocks back from head, max ~6 chunks (~2h). Read-only."""
import json, subprocess, time
ADDR="0x1595013dfc8c6b3f4b172254bf09bdaf1421002b"
ZERO="0x0000000000000000000000000000000000000000000000000000000000000000"
TRANSFER="0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
EP="https://bsc-dataseed.binance.org/"
def blocknum():
    p={"jsonrpc":"2.0","id":1,"method":"eth_blockNumber","params":[]}
    r=subprocess.run(["curl","-sL","--max-time","30","-X","POST",EP,"-H","Content-Type: application/json","-d",json.dumps(p)],capture_output=True,text=True,timeout=40)
    return int(json.loads(r.stdout)["result"],16)
def getlogs(frm,to):
    p={"jsonrpc":"2.0","id":1,"method":"eth_getLogs","params":[{"fromBlock":hex(frm),"toBlock":hex(to),"address":ADDR,"topics":[TRANSFER,ZERO]}]}
    r=subprocess.run(["curl","-sL","--max-time","60","-X","POST",EP,"-H","Content-Type: application/json","-d",json.dumps(p)],capture_output=True,text=True,timeout=70)
    j=json.loads(r.stdout)
    if "error" in j: return None, j["error"]
    return j.get("result",[]), None
def blocktime(b):
    p={"jsonrpc":"2.0","id":1,"method":"eth_getBlockByNumber","params":[hex(b),False]}
    r=subprocess.run(["curl","-sL","--max-time","30","-X","POST",EP,"-H","Content-Type: application/json","-d",json.dumps(p)],capture_output=True,text=True,timeout=40)
    j=json.loads(r.stdout)
    return int(j["result"]["timestamp"],16) if j.get("result") else None
head=blocknum(); print("head",head)
earliest=None
for i in range(6):
    to=head-i*2000; frm=to-1999
    logs,err=getlogs(frm,to)
    if err: print(f"chunk {frm}-{to}: ERROR {err}"); break
    print(f"chunk {frm}-{to}: {len(logs)} first-mint transfers")
    if logs:
        earliest=min(int(l["blockNumber"],16) for l in logs)
        print("  earliest in chunk:", earliest)
        # keep scanning older chunks to find the true first
print("earliest block found:", earliest)
if earliest:
    ts=blocktime(earliest)
    import datetime
    print("first mint block time UTC:", datetime.datetime.utcfromtimestamp(ts).isoformat()+"Z" if ts else None)
