#!/usr/bin/env python3
"""First-mint binary search for BRAINROT ZOO via address-filtered Ankr getLogs (existence probe). Read-only."""
import sys, json, time, datetime
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from ankr import ankr_post
from fast_rpc import _post as _fr_post
A = "0x3c7d328027ca0068e7cd8709d64d9161bc35de93"
TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO = "0x" + "00"*32
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/"]

def head():
    for ep in EPS:
        try:
            return int(_fr_post(ep, {"jsonrpc":"2.0","id":1,"method":"eth_blockNumber","params":[]}, timeout=8, retries=0)["result"], 16)
        except Exception: continue
    return None

def has_log(frm, to):
    params = {"blockchain":"bsc","address":A,"fromBlock":hex(frm),"toBlock":hex(to),
              "pageSize":1,"decodeLogs":False,"topics":[TRANSFER, ZERO]}
    body = ankr_post("ankr_getLogs", params, timeout=30)
    logs = body.get("result",{}).get("logs",[]) if isinstance(body,dict) else []
    return len(logs) > 0

def get_logs(frm, to):
    params = {"blockchain":"bsc","address":A,"fromBlock":hex(frm),"toBlock":hex(to),
              "pageSize":1000,"decodeLogs":False,"topics":[TRANSFER, ZERO]}
    body = ankr_post("ankr_getLogs", params, timeout=30)
    return body.get("result",{}).get("logs",[]) if isinstance(body,dict) else []

H = head()
print("head", H, flush=True)
lo, hi = 132200000, H  # ~23h window; if no log at all, extend backwards
if not has_log(lo, hi):
    print("NO mint logs in window 132200000-head; extending lo to 132000000", flush=True)
    lo = 132000000
    if not has_log(lo, hi):
        print("NO mint logs in 132000000-head either -> first mint older or Ankr issue", flush=True)
        sys.exit(0)
# binary search first block with a mint log: invariant has_log(lo,hi) true; find min block
a, b = lo, hi
while b - a > 1:
    m = (a + b)//2
    if has_log(lo, m):
        b = m
    else:
        a = m
    time.sleep(0.3)
print("first mint block (binary search):", b, flush=True)
logs = get_logs(max(b-500,0), b+499)
mine = [l for l in logs if l.get("address","").lower()==A.lower()]
print("logs in window:", len(mine), flush=True)
if mine:
    first = min(mine, key=lambda l: int(l.get("blockNumber","0x0"),16))
    fb = int(first.get("blockNumber","0x0"),16)
    print("first Transfer-from-zero block:", fb, "tx:", first.get("transactionHash"), flush=True)
    blk=None
    for ep in EPS:
        try:
            blk=_fr_post(ep, {"jsonrpc":"2.0","id":1,"method":"eth_getBlockByNumber","params":[hex(fb),False]}, timeout=10, retries=0)
            break
        except Exception: continue
    if blk and blk.get("result"):
        ts=int(blk["result"]["timestamp"],16)
        print("first mint time WIB:", datetime.datetime.fromtimestamp(ts, datetime.timezone(datetime.timedelta(hours=7))).isoformat(), flush=True)
    json.dump({"first_mint_block":fb,"tx":first.get("transactionHash"),"n_logs_window":len(mine)}, open("run-2026-11-08-1831-brainrot-firstmint.json","w"), indent=1)
