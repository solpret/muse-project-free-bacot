#!/usr/bin/env python3
"""Independent first-mint check for the 2 age-sweep REMOVE candidates (thin margin ~0.6h)."""
import json, sys, time
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from ankr import ankr_post
from fast_rpc import batch
from datetime import datetime, timezone, timedelta
TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO = "0x" + "00" * 32
WIB = timezone(timedelta(hours=7))
ITEMS = {
    "Agent Coffee": "0x53A3D78FF23d9c9cb14Ae8B2fd168A44391b2010",
    "Driftnauts": "0x6a926234D3767F2EEb3DB12c1B4C9e2912C5589b",
}
out = {}
for name, addr in ITEMS.items():
    first = None; total = 0; token = None; pages = 0; err = None
    try:
        while True:
            params = {"blockchain": "bsc", "address": addr.lower(), "fromBlock": hex(131000000),
                      "toBlock": hex(132170000), "pageSize": 1000, "decodeLogs": False,
                      "topics": [TRANSFER, ZERO]}
            if token: params["pageToken"] = token
            body = ankr_post("ankr_getLogs", params, timeout=60)
            res = body.get("result", {}) if isinstance(body, dict) else {}
            logs = res.get("logs", []); pages += 1; total += len(logs)
            for lg in logs:
                blk = int(lg.get("blockNumber", "0x0"), 16)
                if first is None or blk < first["block"]:
                    first = {"block": blk, "tx": lg.get("transactionHash")}
            token = res.get("nextPageToken")
            if not token or pages >= 10: break
            time.sleep(1)
    except Exception as e:
        err = f"{type(e).__name__}:{e}"[:150]
    row = {"address": addr, "logs_from_zero": total, "pages": pages, "error": err, "first": first}
    if first:
        try:
            b = batch([("eth_getBlockByNumber", [hex(first["block"]), False])],
                      endpoint="https://bsc-dataseed1.bnbchain.org/", timeout=15)[0]
            ts = int(b["timestamp"], 16)
            dt = datetime.fromtimestamp(ts, tz=WIB)
            row["firstMintWib"] = dt.strftime("%Y-%m-%d %H:%M:%S")
            row["ageHours"] = round((datetime.now(WIB) - dt).total_seconds() / 3600, 1)
        except Exception as e:
            row["timestamp_error"] = f"{type(e).__name__}:{e}"[:150]
    out[name] = row
    print(name, json.dumps(row), flush=True)
json.dump(out, open("/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/run-2026-11-07-1431-ageverify.json", "w"), indent=1)
print("DONE")
