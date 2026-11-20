#!/usr/bin/env python3
"""Validate getLogs + probe E09A event types. Read-only."""
import json, subprocess
RPC="https://bsc-dataseed.binance.org/"
E09A="0xE09Ab25732b1e1FdA7ad4d551EEA0aAC65aD0711"
HIVE="0x1458b0C132Fb51BDC65B1Ca7a3BE484BCd9A2f77"
T_TRANSFER="0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
T_SINGLE="0xc3d58168c5ae7397731d9e3f770f7aa13d7d5e5d5d7d5d5d5d5d5d5d5d5d5d5d5"
# correct TransferSingle topic:
T_SINGLE="0xc3d58168c5ae7397731d9e3f770f7aa13d7d5e5d5d5d5d5d5d5d5d5d5d5d5d5"
def post(payload, timeout=30):
    r=subprocess.run(["curl","-s","-L","--max-time",str(timeout),RPC,"-H","Content-Type: application/json","-d",json.dumps(payload)],capture_output=True,timeout=timeout+5)
    return json.loads(r.stdout.decode())
head=int(post([{"jsonrpc":"2.0","id":1,"method":"eth_blockNumber","params":[]}])[0]["result"],16)
print("head:", head)
def logs(addr, topics, frm, to):
    resp=post([{"jsonrpc":"2.0","id":1,"method":"eth_getLogs","params":[{"fromBlock":hex(frm),"toBlock":hex(to),"address":addr,"topics":topics}]}])
    res=resp[0].get("result") if isinstance(resp,list) else resp.get("result")
    return res if isinstance(res,list) else {"error": res}
# control: HIVE Transfer last 20000 blocks
h=logs(HIVE,[T_TRANSFER],head-19999,head)
print("HIVE Transfer last 20k:", len(h) if isinstance(h,list) else h)
# E09A: any Transfer last 100k blocks
e=logs(E09A,[T_TRANSFER],head-99999,head)
print("E09A Transfer last 100k:", len(e) if isinstance(e,list) else e)
# E09A: all events last 100k (no topics filter)
e2=logs(E09A,[],head-99999,head)
print("E09A ALL events last 100k:", len(e2) if isinstance(e2,list) else e2)
if isinstance(e2,list) and e2:
    from collections import Counter
    print("topics0:", Counter([l["topics"][0] for l in e2 if l.get("topics")]))
    print("first log block:", int(e2[0]["blockNumber"],16), "tx:", e2[0]["transactionHash"])
    print("last log block:", int(e2[-1]["blockNumber"],16))
# code existence at older blocks
for blk in (133900000, 134000000, 134100000, 134150000, 134200000):
    c=post([{"jsonrpc":"2.0","id":1,"method":"eth_getCode","params":[E09A,hex(blk)]}])
    code=c[0].get("result","")
    print(f"code at {blk}:", "present(%d)"%len(code) if code and code!="0x" else "absent")
