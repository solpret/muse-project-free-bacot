#!/usr/bin/env python3
"""Run 0901: Ankr-based first-mint verification for Crack 0xAeA1433dBD9e7edE0914d996C2Dad692E6e01e09.
Range [131900000, 131921703] (hot-leg 0833 read block). Address-filtered
ankr_getLogs Transfer-from-zero, paging pageSize 1000. Also fetches the
block timestamp of the earliest mint block (dataseed eth_getBlockByNumber)
to compute launch age. Limitation: mints before 131900000 (~05:51 WIB)
are outside the range; deployment is bounded below by Sourcify verifiedAt
2026-11-06T01:33:01Z (08:33 WIB), so first mint is expected inside range.
Ankr via existing proxy env; NEVER set no_proxy for rpc.ankr.com."""
import sys, json, time, urllib.request
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from ankr import ankr_post
from fast_rpc import _single

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TS = "2026-11-06-0901"
TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO_TOPIC = "0x" + "00" * 32
ADDR = "0xAeA1433dBD9e7edE0914d996C2Dad692E6e01e09"
FROM, TO = 131900000, 131921703

def earlier_mints(addr, frm, to):
    total = 0; earliest = None; latest = None; token = None; pages = 0
    while True:
        params = {"blockchain": "bsc", "fromBlock": hex(frm), "toBlock": hex(to),
                  "pageSize": 1000, "decodeLogs": False, "address": addr,
                  "topics": [TRANSFER, ZERO_TOPIC]}
        if token: params["pageToken"] = token
        body = ankr_post("ankr_getLogs", params, timeout=30)
        result = body.get("result", {}) if isinstance(body, dict) else {}
        logs = result.get("logs", [])
        for lg in logs:
            total += 1
            b = int(lg.get("blockNumber", "0x0"), 16)
            earliest = b if earliest is None else min(earliest, b)
            latest = b if latest is None else max(latest, b)
        token = result.get("nextPageToken")
        pages += 1
        if not token or pages >= 15: break
        time.sleep(2.2)
    return total, earliest, latest, pages

t0 = time.time()
total, earliest, latest, pages = earlier_mints(ADDR, FROM, TO)
print("CRACK first-mint: total", total, "earliest", earliest, "latest", latest, "pages", pages, "elapsed %.1fs" % (time.time()-t0), flush=True)
ts = None
if earliest:
    for ep in ["https://bsc-dataseed1.bnbchain.org", "https://bsc.publicnode.com"]:
        try:
            blk = _single(ep, "eth_getBlockByNumber", [hex(earliest), False], 8, retries=0)
            ts = int(blk["timestamp"], 16)
            print("earliest block ts", ts, time.strftime("%Y-%m-%d %H:%M:%S WIB", time.gmtime(ts + 7*3600)), flush=True)
            break
        except Exception as e:
            print("block ts fail", ep, repr(e), flush=True)
out = {"address": ADDR, "range": [FROM, TO], "total_mints_in_range": total,
       "earliest_block": earliest, "latest_block": latest, "pages": pages,
       "earliest_block_timestamp": ts, "elapsed_s": round(time.time()-t0, 1)}
json.dump(out, open(f"{BASE}/run-{TS}-crack-firstmint.json", "w"), indent=1)
print(json.dumps(out), flush=True)
