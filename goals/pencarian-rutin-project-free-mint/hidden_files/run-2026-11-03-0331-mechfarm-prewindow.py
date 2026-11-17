import sys, json, datetime
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from ankr import ankr_post
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _single
ZERO = "0x0000000000000000000000000000000000000000"
TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
def topic_addr(a): return "0x000000000000000000000000" + a[2:].lower()
def wib(ts): return datetime.datetime.fromtimestamp(ts, datetime.timezone(datetime.timedelta(hours=7))).isoformat()
addr="0xde536232c09ea778b6cb8409328362F7e9182bc9"
out={}
earliest=None; total=0; chunks=[]
frm=131280000
while frm<=131306576:
    to=min(frm+1999,131306576)
    try:
        body=ankr_post("ankr_getLogs",{"blockchain":"bsc","fromBlock":hex(frm),"toBlock":hex(to),"address":[addr],"topics":[[TRANSFER,topic_addr(ZERO)]],"pageSize":100},timeout=60)
        r=body.get("result",body); logs=r.get("logs",[]) if isinstance(r,dict) else []
    except Exception as e:
        chunks.append((frm,to,f"ERR {e}")); frm=to+1; continue
    chunks.append((frm,to,len(logs))); total+=len(logs)
    for l in logs:
        b=int(l["blockNumber"],16)
        if earliest is None or b<earliest[0]: earliest=(b,l["transactionHash"])
    frm=to+1
ts=None
if earliest:
    blk=_single("https://bsc-dataseed.binance.org/","eth_getBlockByNumber",[hex(earliest[0]),False],8,retries=0)
    ts=wib(int(blk["timestamp"],16))
out={"prewindow_logs":total,"earliest_block":earliest[0] if earliest else None,"earliest_tx":earliest[1] if earliest else None,"earliest_wib":ts,"chunks":chunks}
print(out)
json.dump(out, open("/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/run-2026-11-03-0331-mechfarm-prewindow.json","w"), indent=1)
