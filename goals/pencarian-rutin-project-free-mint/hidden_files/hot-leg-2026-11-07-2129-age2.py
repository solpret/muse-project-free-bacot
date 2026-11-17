#!/usr/bin/env python3
"""AgentBook first-mint via dataseed eth_getLogs (fast), timestamp via dataseed."""
import sys, json, time, datetime, urllib.request
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _single
ADDR = "0xeecacbe6eac6d6f2a38e8daa9049c7aa08ad43b0"
TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO = "0x0000000000000000000000000000000000000000000000000000000000000000"
WIB = datetime.timezone(datetime.timedelta(hours=7))
head = int(_single("https://bsc-dataseed1.bnbchain.org/", "eth_blockNumber", [], 8, retries=0), 16)
print("head:", head)
def logs(ep, frm, to):
    payload = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_getLogs",
        "params": [{"fromBlock": hex(frm), "toBlock": hex(to), "address": ADDR,
                    "topics": [TRANSFER, ZERO]}]}).encode()
    req = urllib.request.Request(ep, data=payload, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.load(r)["result"]
# newest 3000 blocks first; if earliest log is at the window start, extend backwards
frm = head - 3000
all_logs = []
try:
    all_logs = logs("https://bsc-dataseed1.bnbchain.org/", frm, head)
    print("logs in last 3000 blocks:", len(all_logs))
except Exception as e:
    print("dataseed1 getLogs err:", e)
    try:
        all_logs = logs("https://bsc.publicnode.com/", frm, head)
        print("publicnode logs in last 3000 blocks:", len(all_logs))
    except Exception as e2:
        print("publicnode getLogs err:", e2)
if all_logs:
    first = min(all_logs, key=lambda l: int(l["blockNumber"], 16))
    blk = int(first["blockNumber"], 16)
    print("first_mint_block_in_window:", blk, "tx:", first.get("transactionHash"))
    print("window_start_block:", frm, "-> first mint inside window:", blk > frm)
    b = _single("https://bsc-dataseed1.bnbchain.org/", "eth_getBlockByNumber", [hex(blk), False], 10, retries=0)
    ts = int(b["timestamp"], 16)
    print("first_mint_wib:", datetime.datetime.fromtimestamp(ts, WIB).isoformat())
    print("age_minutes:", round((time.time() - ts) / 60, 1))
