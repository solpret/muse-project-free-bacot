#!/usr/bin/env python3
import sys, json, datetime
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from ankr import ankr_post
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _single
ZERO = "0x0000000000000000000000000000000000000000"
TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
def topic_addr(a): return "0x000000000000000000000000" + a[2:].lower()
for name, addr in [("Opera Agent", "0x32ddd7d98bB711976cCfE19548Df52D0cdeC197c"),
                   ("Silk Agent", "0xF888787f39dD5a5adCEC1b0d9833cF40a655c60e")]:
    logs_all = []
    frm = 131260000
    body = ankr_post("ankr_getLogs", {"blockchain": "bsc", "fromBlock": hex(frm), "toBlock": hex(131287525),
                     "address": [addr], "topics": [[TRANSFER, topic_addr(ZERO)]], "pageSize": 100}, timeout=60)
    # topics format: ankr expects topics array; try alternative if empty
    r = body.get("result", body)
    logs = r.get("logs", []) if isinstance(r, dict) else []
    print(name, "pre-window from-zero logs (131260000-131287525):", len(logs))
    if logs:
        first = min(logs, key=lambda l: int(l["blockNumber"], 16))
        blk = int(first["blockNumber"], 16)
        print("  earliest pre-window:", blk, first["transactionHash"])
        for ep in ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/"]:
            try:
                b = _single(ep, "eth_getBlockByNumber", [hex(blk), False], 8, retries=0)
                ts = int(b["timestamp"], 16)
                print("  WIB:", datetime.datetime.fromtimestamp(ts, datetime.timezone(datetime.timedelta(hours=7))).isoformat())
                break
            except Exception as e: print("  block err", str(e)[:100])
    json.dump(logs, open(f"/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/run-2026-11-03-0131-prewindow-{name.replace(' ','').lower()}.json", "w"), indent=1)
