import json, sys, datetime
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from ankr import ankr_post
TRANSFER="0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO="0x"+"00"*32
HEAD=131773324
def any_mint(addr, lo, hi):
    """True if any 4-topic Transfer-from-zero log for addr in [lo,hi]."""
    params={"blockchain":"bsc","fromBlock":hex(lo),"toBlock":hex(hi),"pageSize":1000,"decodeLogs":False,"topics":[TRANSFER,ZERO],"address":addr}
    body=ankr_post("ankr_getLogs", params, timeout=30)
    logs=(body.get("result",{}) or {}).get("logs",[]) if isinstance(body,dict) else []
    for lg in logs:
        if len(lg.get("topics",[]))==4:
            return int(lg["blockNumber"],16)
    return None
def first_mint(addr, lo, hi):
    # binary search for earliest mint block in [lo,hi]; assumes at least one exists
    if any_mint(addr, lo, hi) is None:
        return None
    while lo < hi:
        mid=(lo+hi)//2
        if any_mint(addr, lo, mid) is not None:
            hi=mid
        else:
            lo=mid+1
    return lo
import urllib.request
RPCS=["https://bsc-dataseed1.bnbchain.org","https://bsc-dataseed2.bnbchain.org"]
def block_ts(n):
    for rpc in RPCS:
        try:
            body=json.dumps({"jsonrpc":"2.0","id":1,"method":"eth_getBlockByNumber","params":[hex(n),False]}).encode()
            req=urllib.request.Request(rpc,data=body,headers={"Content-Type":"application/json"})
            with urllib.request.urlopen(req,timeout=15) as r: out=json.load(r)
            return int(out["result"]["timestamp"],16)
        except Exception: continue
    return None
res={}
for name,addr,lo in [
    ("Robogent","0x5eA7E757dfc4654f7478841BD30175bd7F186e24",131375631),
    ("Jolly","0xdc11764a5664e333c8d303eb465e89a1caadb85b",131060000),
]:
    b=first_mint(addr,lo,HEAD)
    ts=block_ts(b) if b else None
    wib=datetime.datetime.fromtimestamp(ts, datetime.timezone(datetime.timedelta(hours=7))).isoformat() if ts else None
    res[name]={"firstMintBlock":b,"ts":ts,"wib":wib}
    print(name,res[name])
json.dump(res,open("/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/run-2026-11-05-1401-firstmint.json","w"),indent=1)
