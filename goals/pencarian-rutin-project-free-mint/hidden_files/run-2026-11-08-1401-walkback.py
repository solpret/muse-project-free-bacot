import sys, time, json, datetime
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from ankr import ankr_post
from fast_rpc import _post
TRANSFER="0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO="0x"+"00"*32
def block_ts(blk):
    for ep in ['https://bsc-dataseed2.bnbchain.org/','https://bsc-dataseed1.bnbchain.org/']:
        try:
            b=_post(ep, {'jsonrpc':'2.0','id':1,'method':'eth_getBlockByNumber','params':[hex(blk),False]}, timeout=10, retries=0)
            return int(b['result']['timestamp'],16)
        except Exception: continue
    return None
out={}
for addr in ['0x9831577F7Ee2257e9B0b5C9809eD53B00e6975b8','0xf89CEdb1Bbc3C11a4941e543Ecf9f890788567f0']:
    res=ankr_post("ankr_getLogs", {"blockchain":"bsc","address":addr,"fromBlock":hex(131000000),"toBlock":"latest","topics":[TRANSFER],"pageSize":1000}, timeout=55)
    logs=res.get("result",{}).get("logs",[]) if isinstance(res,dict) else []
    mints=[l for l in logs if l.get("topics",[None,None])[1]==ZERO]
    mints.sort(key=lambda l: int(l["blockNumber"],16))
    first=mints[0] if mints else None
    fb=int(first["blockNumber"],16) if first else None
    ts=block_ts(fb) if fb else None
    wib=datetime.datetime.fromtimestamp(ts, datetime.timezone(datetime.timedelta(hours=7))).strftime("%Y-%m-%d %H:%M:%S WIB") if ts else None
    out[addr]={"logs_total":len(logs),"mints_from_zero":len(mints),"first_block":fb,"first_wib":wib,"truncated_risk":len(logs)>=1000}
    print(addr, json.dumps(out[addr]), flush=True)
json.dump(out, open('run-2026-11-08-1401-walkback2.json','w'), indent=1)
