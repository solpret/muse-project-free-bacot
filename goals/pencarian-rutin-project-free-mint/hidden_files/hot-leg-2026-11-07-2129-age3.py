#!/usr/bin/env python3
"""AgentBook first-mint: publicnode eth_getLogs over last 3000 blocks; save logs."""
import sys, json, time, datetime, urllib.request
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _single
ADDR = "0xeecacbe6eac6d6f2a38e8daa9049c7aa08ad43b0"
TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO = "0x0000000000000000000000000000000000000000000000000000000000000000"
WIB = datetime.timezone(datetime.timedelta(hours=7))
head = None
for ep in ["https://bsc.publicnode.com/", "https://bsc-dataseed2.bnbchain.org/"]:
    try:
        head = int(_single(ep, "eth_blockNumber", [], 15, retries=0), 16)
        print("head via", ep, ":", head); break
    except Exception as e:
        print("head err", ep, e)
if head is None:
    head = 132217859
    print("head fallback:", head)
def logs(ep, frm, to):
    payload = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_getLogs",
        "params": [{"fromBlock": hex(frm), "toBlock": hex(to), "address": ADDR,
                    "topics": [TRANSFER, ZERO]}]}).encode()
    req = urllib.request.Request(ep, data=payload, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=25) as r:
        return json.load(r)["result"]
frm = head - 3000
all_logs = None
for ep in ["https://bsc.publicnode.com/", "https://bsc-dataseed2.bnbchain.org/"]:
    try:
        all_logs = logs(ep, frm, head)
        print("logs via", ep, ":", len(all_logs)); break
    except Exception as e:
        print("getLogs err", ep, str(e)[:120])
if all_logs:
    json.dump(all_logs, open("hot-leg-2026-11-07-2129-agentbook-mintlogs.json", "w"))
    first = min(all_logs, key=lambda l: int(l["blockNumber"], 16))
    blk = int(first["blockNumber"], 16)
    print("first_mint_block_in_window:", blk, "window_start:", frm, "inside_window:", blk > frm)
    for ep in ["https://bsc.publicnode.com/", "https://bsc-dataseed2.bnbchain.org/"]:
        try:
            b = _single(ep, "eth_getBlockByNumber", [hex(blk), False], 15, retries=0)
            ts = int(b["timestamp"], 16)
            print("first_mint_wib:", datetime.datetime.fromtimestamp(ts, WIB).isoformat())
            print("age_minutes:", round((time.time() - ts) / 60, 1))
            break
        except Exception as e:
            print("block ts err", ep, e)
else:
    print("NO logs retrieved")
