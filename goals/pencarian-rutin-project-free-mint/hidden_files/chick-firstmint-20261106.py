#!/usr/bin/env python3
"""Find whether BNB Chick (0xA948...) had ANY mint before the 48h cutoff.

Checks mint Transfers (Transfer from zero address) via Ankr ankr_getLogs
in [131240000, 131586707] (deployment era -> 48h before 2026-11-06 14:42 WIB).
If any log exists there, true first mint is >48h old and the track-C age leg fails.
Read-only. Writes chick-firstmint-20261106.json."""
import json
import os
import sys
import time

sys.path.insert(0, "/home/hatch/workspace/fast_exec")
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from ankr import ankr_post  # noqa: E402
from fast_rpc import _single  # noqa: E402

BASE = os.path.dirname(os.path.abspath(__file__))
SALE = "0xA9481429169C883c7FD5f5EAdFD08737ad688337"
TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO_TOPIC = "0x" + "00" * 32
FROM_BLOCK = 131240000
TO_BLOCK = 131586707  # 48h before 2026-11-06 14:42 WIB
EPS = [
    "https://bsc-dataseed1.defibit.io/",
    "https://bsc.publicnode.com/",
    "https://bsc-dataseed1.bnbchain.org/",
]


def block_ts(n):
    for ep in EPS:
        try:
            b = _single(ep, "eth_getBlockByNumber", [hex(n), False], 8, retries=0)
            if isinstance(b, dict) and b.get("timestamp"):
                return int(b["timestamp"], 16)
        except Exception:
            continue
    return None


def main():
    params = {
        "blockchain": "bsc",
        "fromBlock": hex(FROM_BLOCK),
        "toBlock": hex(TO_BLOCK),
        "address": SALE,
        "topics": [TRANSFER, ZERO_TOPIC],
        "pageSize": 1000,
        "decodeLogs": False,
    }
    logs = []
    page_token = None
    pages = 0
    while True:
        p = dict(params)
        if page_token:
            p["pageToken"] = page_token
        try:
            body = ankr_post("ankr_getLogs", p, timeout=30)
        except Exception as e:  # noqa: BLE001
            print(f"ankr error page {pages}: {e}")
            break
        result = body.get("result", {}) if isinstance(body, dict) else {}
        batch = result.get("logs", [])
        logs.extend(batch)
        page_token = result.get("nextPageToken")
        pages += 1
        if not page_token or pages >= 10:
            break
        time.sleep(2.2)
    blocks = sorted({int(l["blockNumber"], 16) for l in logs if l.get("blockNumber")})
    out = {
        "range": [FROM_BLOCK, TO_BLOCK],
        "mint_logs_in_range": len(logs),
        "distinct_blocks": len(blocks),
        "earliest_mint_block": blocks[0] if blocks else None,
        "latest_mint_block_in_range": blocks[-1] if blocks else None,
        "pages": pages,
    }
    if blocks:
        ts = block_ts(blocks[0])
        out["earliest_mint_ts"] = ts
        if ts:
            out["earliest_mint_wib"] = time.strftime(
                "%Y-%m-%d %H:%M:%S", time.gmtime(ts + 7 * 3600))
            out["age_hours_at_20261106_1442"] = round((1793950975 - ts) / 3600, 2)
    with open(os.path.join(BASE, "chick-firstmint-20261106.json"), "w") as f:
        json.dump(out, f, indent=1)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
