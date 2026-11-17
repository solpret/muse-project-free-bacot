"""First-mint verification for Mechfarm 0x1fab92... via Ankr eth_getLogs (Transfer from zero).
Chunked scan from ~deploy era, then narrow. Timestamps via dataseed (Ankr timestamps are fake)."""
import json, urllib.request, sys
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import batch
ADDR="0x1fab92b937572c79550aeee51cee77d3add20367"
TRANSFER="0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO="0x0000000000000000000000000000000000000000000000000000000000000000"
ANKR="https://rpc.ankr.com/bsc"
def ankr_logs(frm, to):
    body={"jsonrpc":"2.0","id":1,"method":"eth_getLogs","params":[{"fromBlock":hex(frm),"toBlock":hex(to),"address":ADDR,"topics":[TRANSFER,ZERO]}]}
    req=urllib.request.Request(ANKR, data=json.dumps(body).encode(), headers={"Content-Type":"application/json"})
    with urllib.request.urlopen(req, timeout=20) as r:
        d=json.load(r)
    if "error" in d: raise RuntimeError(str(d["error"]))
    return d.get("result",[])
def block_ts(bn):
    # dataseed via fast_rpc
    res=batch([("eth_getBlockByNumber",[hex(bn), False])], endpoint="https://bsc-dataseed1.bnbchain.org/", timeout=10)
    return int(res[0]["timestamp"],16)
head=int(batch([("eth_blockNumber",[])], endpoint="https://bsc-dataseed1.bnbchain.org/", timeout=10)[0],16)
print("head",head)
# chunked scan upward from 131400000 (approx Nov 3 10:10 UTC verify time)
lo=131400000; first=None; step=100000
while lo<head:
    hi=min(lo+step-1, head)
    try:
        logs=ankr_logs(lo,hi)
    except Exception as e:
        print(f"window {lo}-{hi} ERROR {e}"); lo=hi+1; continue
    print(f"window {lo}-{hi}: {len(logs)} mint logs")
    if logs:
        first=int(logs[0]["blockNumber"],16); break
    lo=hi+1
if first is None:
    print("NO MINT LOGS FOUND in scanned range"); sys.exit(0)
# narrow: binary search earliest block with a mint in [lo, first]
a,b=lo,first
while a<b:
    mid=(a+b)//2
    logs=ankr_logs(mid,first)
    if logs: b=int(logs[0]["blockNumber"],16) if int(logs[0]["blockNumber"],16)<b else mid
    else: a=mid+1
    if b<=a: break
# simpler: scan the window in 5000-block chunks to pin first block
print("first mint approx block:", first)
# verify by scanning [lo, first] in 2000-block chunks for the earliest log
earliest=None
c=lo
while c<=first:
    h=min(c+1999, first)
    logs=ankr_logs(c,h)
    if logs:
        earliest=int(logs[0]["blockNumber"],16); break
    c=h+1
print("earliest mint block:", earliest)
if earliest:
    ts=block_ts(earliest)
    from datetime import datetime, timezone, timedelta
    wib=timezone(timedelta(hours=7))
    print("earliest mint time WIB:", datetime.fromtimestamp(ts,wib).strftime("%Y-%m-%d %H:%M:%S"))
    print("age hours:", round((datetime.now(wib).timestamp()-ts)/3600,2))
json.dump({"head":head,"first_mint_block":earliest}, open("hot-leg-2026-11-08-0719-1fab-firstmint.json","w"), indent=1)
