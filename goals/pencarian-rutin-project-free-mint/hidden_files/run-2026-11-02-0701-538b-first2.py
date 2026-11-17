import json, sys
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from ankr import ankr_post
C="0x538Bd9f178eEf2CFB564d2FAD1D5B0702d8B3818"
ZERO="0x"+"0"*64
TOPIC="0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
def logs_chunk(lo,hi):
    out=[]; token=None
    for _ in range(10):
        params={"blockchain":"bsc","fromBlock":hex(lo),"toBlock":hex(hi),"topics":[TOPIC,ZERO,None],"address":[C],"pageSize":1000}
        if token: params["pageToken"]=token
        body=ankr_post("ankr_getLogs", params, timeout=30)
        res=body.get("result") or {}
        out+=res.get("logs") or []
        token=res.get("nextPageToken")
        if not token: break
    return out
hi=131109999; found=None; total=0; earliest=None
while hi>131079999:
    lo=max(hi-1999,131080000)
    logs=logs_chunk(lo,hi); total+=len(logs)
    if logs:
        logs.sort(key=lambda l:int(l["blockNumber"],16))
        if earliest is None or int(logs[0]["blockNumber"],16)<earliest: earliest=int(logs[0]["blockNumber"],16)
    hi=lo-1
print("extra_range_logs", total, "earliest_in_extra", earliest)
