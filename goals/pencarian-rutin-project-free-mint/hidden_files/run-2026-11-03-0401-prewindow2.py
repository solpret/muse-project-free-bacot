#!/usr/bin/env python3
import sys, json, datetime
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from ankr import ankr_post
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _single
ZERO="0x0000000000000000000000000000000000000000"
TRANSFER="0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
def ta(a): return "0x000000000000000000000000"+a[2:].lower()
def wib(ts): return datetime.datetime.fromtimestamp(ts, datetime.timezone(datetime.timedelta(hours=7))).isoformat()
targets={"Dronagent":"0x307157fb80A63bD4C845f44f5a55Dd90127D8C50","Zephyr Agent":"0xE41b54504aa171D92E01384aE3aB3007E170Aa70"}
head=int(_single("https://bsc-dataseed.binance.org/","eth_blockNumber",[],8,retries=0),16)
print("HEAD", head)
out={"head":head}
for name,addr in targets.items():
    earliest=None; total=0; chunks=[]; frm=131290000
    while frm<=head:
        to=min(frm+1999,head)
        try:
            body=ankr_post("ankr_getLogs",{"blockchain":"bsc","fromBlock":hex(frm),"toBlock":hex(to),"address":[addr],"topics":[TRANSFER,ta(ZERO)],"pageSize":100},timeout=60)
            logs=body.get("result",body).get("logs",[])
        except Exception as e:
            chunks.append((frm,to,f"ERR {type(e).__name__} {str(e)[:80]}")); frm=to+1; continue
        logs=[l for l in logs if len(l.get("topics",[]))>1 and l["topics"][1].lower()==ta(ZERO)]
        chunks.append((frm,to,len(logs))); total+=len(logs)
        for l in logs:
            b=int(l["blockNumber"],16)
            if earliest is None or b<earliest[0]: earliest=(b,l["transactionHash"])
        frm=to+1
    ts=None
    if earliest:
        blk=_single("https://bsc-dataseed.binance.org/","eth_getBlockByNumber",[hex(earliest[0]),False],8,retries=0)
        ts=wib(int(blk["timestamp"],16))
    out[name]={"from_zero_logs":total,"earliest_block":earliest[0] if earliest else None,"earliest_tx":earliest[1] if earliest else None,"earliest_wib":ts,"chunks":chunks}
    print(name, "from-zero:", total, "earliest:", earliest, ts)
json.dump(out, open("/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/run-2026-11-03-0401-prewindow2.json","w"), indent=1)
