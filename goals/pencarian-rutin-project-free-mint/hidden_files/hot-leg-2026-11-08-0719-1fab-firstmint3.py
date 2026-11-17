import sys, json, time
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from ankr import get_logs
from fast_rpc import batch
ADDR="0x1fab92b937572c79550aeee51cee77d3add20367"
TRANSFER="0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO="0x0000000000000000000000000000000000000000000000000000000000000000"
def has_mint(lo, hi, tries=3):
    for t in range(tries):
        try:
            d=get_logs(ADDR, lo, hi, topics=[TRANSFER, ZERO])
            if "error" in d: raise RuntimeError(str(d["error"]))
            ls=d.get("result",{}).get("logs",[])
            return len(ls)>0, len(ls)
        except Exception as e:
            print(f"  retry {t+1} [{lo}-{hi}] {type(e).__name__}", flush=True)
            time.sleep(2)
    raise RuntimeError(f"has_mint failed [{lo}-{hi}]")
def first_log_block(lo, hi):
    d=get_logs(ADDR, lo, hi, topics=[TRANSFER, ZERO])
    ls=d.get("result",{}).get("logs",[])
    return int(ls[0]["blockNumber"],16) if ls else None
head=int(batch([("eth_blockNumber",[])], endpoint="https://bsc-dataseed1.bnbchain.org/", timeout=10)[0],16)
print("head",head, flush=True)
LO=131300000
# binary search: smallest B in [LO, head] such that a mint exists in [LO, B]
a,b=LO,head
# ensure there is a mint in [LO, head] at all (known true from earlier 1000-log window)
while a<b:
    mid=(a+b)//2
    ok,n=has_mint(LO,mid)
    print(f"has_mint [{LO}-{mid}] = {ok} ({n} logs)", flush=True)
    if ok: b=mid
    else: a=mid+1
print("first mint block (binary search):", a)
# confirm: first log in [a, a+2000]
fb=first_log_block(a, min(a+2000, head))
print("first log block confirmed:", fb)
res=batch([("eth_getBlockByNumber",[hex(fb), False])], endpoint="https://bsc-dataseed1.bnbchain.org/", timeout=10)
ts=int(res[0]["timestamp"],16)
from datetime import datetime, timezone, timedelta
wib=timezone(timedelta(hours=7))
print("first mint WIB:", datetime.fromtimestamp(ts,wib).strftime("%Y-%m-%d %H:%M:%S"))
print("age hours:", round((datetime.now(wib).timestamp()-ts)/3600,2))
json.dump({"head":head,"first_mint_block":fb,"first_mint_ts":ts}, open("hot-leg-2026-11-08-0719-1fab-firstmint.json","w"), indent=1)
