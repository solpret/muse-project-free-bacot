#!/usr/bin/env python3
"""Age verification for 2 new discovery items run 1431 (PIXEL PETS, Skynet).
Read-only. Ankr getLogs address-filtered for first Transfer-from-zero;
block timestamp via fast_rpc (Ankr timestamps are fake 'now')."""
import json, sys, time
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from ankr import ankr_post
from fast_rpc import batch

TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO = "0x" + "00" * 32
ITEMS = {
    "PIXEL PETS": "0x85188BC437eCB8677b072529Fc80AC602A7a1465",
    "Skynet": "0x4364991B28184727CAce1ac659e53cc497a940F7",
}
HEAD = 132167467
FROM = 129500000  # ~Oct 24, safely before Oct 26 post
out = {}
for name, addr in ITEMS.items():
    t0 = time.time()
    first = None; total = 0; err = None; pages = 0
    token = None
    try:
        while True:
            params = {"blockchain": "bsc", "address": addr.lower(),
                      "fromBlock": hex(FROM), "toBlock": hex(HEAD),
                      "pageSize": 1000, "decodeLogs": False,
                      "topics": [TRANSFER, ZERO]}
            if token:
                params["pageToken"] = token
            body = ankr_post("ankr_getLogs", params, timeout=60)
            res = body.get("result", {}) if isinstance(body, dict) else {}
            logs = res.get("logs", [])
            pages += 1
            total += len(logs)
            for lg in logs:
                blk = int(lg.get("blockNumber", "0x0"), 16)
                if first is None or blk < first["block"]:
                    first = {"block": blk, "tx": lg.get("transactionHash")}
            token = res.get("nextPageToken")
            if not token or pages >= 10:
                break
            time.sleep(1)
    except Exception as e:
        err = f"{type(e).__name__}:{e}"[:200]
    row = {"address": addr, "logs_from_zero": total, "pages": pages, "error": err, "first": first}
    if first:
        try:
            b = batch([("eth_getBlockByNumber", [hex(first["block"]), False])],
                      endpoint="https://bsc-dataseed1.bnbchain.org/", timeout=15)[0]
            ts = int(b["timestamp"], 16)
            from datetime import datetime, timezone, timedelta
            wib = timezone(timedelta(hours=7))
            dt = datetime.fromtimestamp(ts, tz=wib)
            row["firstMintWib"] = dt.strftime("%Y-%m-%d %H:%M:%S")
            row["ageHours"] = round((datetime.now(wib) - dt).total_seconds() / 3600, 1)
        except Exception as e:
            row["timestamp_error"] = f"{type(e).__name__}:{e}"[:150]
    row["elapsed_s"] = round(time.time() - t0, 1)
    out[name] = row
    print(name, json.dumps(row), flush=True)
json.dump(out, open("/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/run-2026-11-07-1431-newitems-age.json", "w"), indent=1)
print("DONE")
