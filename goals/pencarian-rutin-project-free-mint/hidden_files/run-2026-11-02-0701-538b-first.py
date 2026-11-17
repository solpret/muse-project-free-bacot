import json, sys
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from ankr import ankr_post
from fast_rpc import _single
C="0x538Bd9f178eEf2CFB564d2FAD1D5B0702d8B3818"
ZERO="0x"+"0"*64
TOPIC="0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
# walk backwards in 2000-block chunks from window start
hi=131140010; found=None; total=0
while hi>131110000 and found is None:
    lo=max(hi-1999,131110000)
    params={"blockchain":"bsc","fromBlock":hex(lo),"toBlock":hex(hi),"topics":[TOPIC,ZERO,None],"address":[C],"pageSize":1000}
    body=ankr_post("ankr_getLogs", params, timeout=30)
    logs=(body.get("result") or {}).get("logs") or []
    total+=len(logs)
    if logs:
        logs.sort(key=lambda l:int(l["blockNumber"],16))
        found=logs[0]
    hi=lo-1
print("logs_in_searched_range", total)
if found:
    b=int(found["blockNumber"],16); print("first_in_range_block", b)
    blk=_single("https://bsc-dataseed.binance.org/","eth_getBlockByNumber",[hex(b),False],8,retries=0)
    ts=int(blk["timestamp"],16); print("first_block_timestamp", ts)
    import datetime; print("first_wib", datetime.datetime.fromtimestamp(ts, datetime.timezone(datetime.timedelta(hours=7))).isoformat())
    json.dump({"first_block":b,"timestamp":ts}, open("/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/run-2026-11-02-0701-538b-first.json","w"))
else:
    print("no claim Transfer found back to 131110000; first claim predates that bound")
