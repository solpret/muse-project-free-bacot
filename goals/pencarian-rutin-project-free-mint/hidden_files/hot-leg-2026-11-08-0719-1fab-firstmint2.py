import sys, json
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from ankr import get_logs
from fast_rpc import batch
ADDR="0x1fab92b937572c79550aeee51cee77d3add20367"
TRANSFER="0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO="0x0000000000000000000000000000000000000000000000000000000000000000"
head=int(batch([("eth_blockNumber",[])], endpoint="https://bsc-dataseed1.bnbchain.org/", timeout=10)[0],16)
print("head",head, flush=True)
def logs(frm,to):
    d=get_logs(ADDR, frm, to, topics=[TRANSFER, ZERO])
    if "error" in d: raise RuntimeError(str(d["error"]))
    return d.get("result",{}).get("logs",[])
lo=131400000; first=None
while lo<head:
    hi=min(lo+99999, head)
    try:
        ls=logs(lo,hi)
    except Exception as e:
        print(f"window {lo}-{hi} ERROR {e}", flush=True); lo=hi+1; continue
    print(f"window {lo}-{hi}: {len(ls)} mint logs", flush=True)
    if ls:
        first=int(ls[0]["blockNumber"],16); break
    lo=hi+1
if first is None:
    print("NO MINT LOGS"); sys.exit(0)
# narrow within [lo, first] in 2000-block chunks
earliest=None; c=lo
while c<=first:
    h=min(c+1999, first)
    ls=logs(c,h)
    if ls:
        earliest=int(ls[0]["blockNumber"],16); break
    c=h+1
print("earliest mint block:", earliest)
if earliest:
    res=batch([("eth_getBlockByNumber",[hex(earliest), False])], endpoint="https://bsc-dataseed1.bnbchain.org/", timeout=10)
    ts=int(res[0]["timestamp"],16)
    from datetime import datetime, timezone, timedelta
    wib=timezone(timedelta(hours=7))
    print("earliest mint WIB:", datetime.fromtimestamp(ts,wib).strftime("%Y-%m-%d %H:%M:%S"))
    print("age hours:", round((datetime.now(wib).timestamp()-ts)/3600,2))
    json.dump({"head":head,"first_mint_block":earliest,"first_mint_ts":ts}, open("hot-leg-2026-11-08-0719-1fab-firstmint.json","w"), indent=1)
