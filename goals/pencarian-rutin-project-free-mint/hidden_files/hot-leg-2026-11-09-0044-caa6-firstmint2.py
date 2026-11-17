import json, sys
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from ankr import get_logs
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import batch
ADDR="0xcaa6554463a98f9afc966175694cd81ac7c41b41"
TRANSFER="0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO="0x0000000000000000000000000000000000000000000000000000000000000000"
out={}
try:
    res=get_logs(ADDR, 131000000, 132000000, topics=[TRANSFER, ZERO])
    logs=res.get("result",{}).get("logs",[])
    out["window"]=[131000000,132000000]
    out["n_mint_logs"]=len(logs)
    out["nextPageToken"]=res.get("result",{}).get("nextPageToken")
    if logs:
        blocks=sorted(int(l["blockNumber"],16) for l in logs)
        out["earliest_mint_block"]=blocks[0]
        out["latest_mint_block"]=blocks[-1]
        out["first5"]=blocks[:5]
    json.dump(res, open("hot-leg-2026-11-09-0044-caa6-mintlogs-early.json","w"))
except Exception as e:
    out["error"]=f"{type(e).__name__}: {e}"
# timestamp of earliest mint block via dataseed (real timestamp, NOT Ankr)
eb=out.get("earliest_mint_block")
if eb:
    for ep in ["https://bsc-dataseed1.bnbchain.org/","https://bsc.publicnode.com/"]:
        try:
            r=batch([("eth_getBlockByNumber",[hex(eb), False])], endpoint=ep, timeout=10)
            ts=int(r[0]["timestamp"],16)
            from datetime import datetime, timezone, timedelta
            WIB=timezone(timedelta(hours=7))
            dt=datetime.fromtimestamp(ts, WIB)
            out["earliest_mint_time_wib"]=dt.strftime("%Y-%m-%d %H:%M:%S WIB")
            out["earliest_mint_unix"]=ts
            out["timestamp_source"]=ep
            break
        except Exception as e:
            out.setdefault("timestamp_errors",[]).append(f"{ep}: {e}")
print(json.dumps(out,indent=1))
