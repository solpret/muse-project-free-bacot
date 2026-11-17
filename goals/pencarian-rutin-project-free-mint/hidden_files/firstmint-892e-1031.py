#!/usr/bin/env python3
"""Find first mint (Transfer from zero) for 0x892E... + block timestamps.
Read-only Ankr getLogs with address filter + fast_rpc block times."""
import json
import sys
import time

sys.path.insert(0, "/home/hatch/workspace/fast_exec")
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from fast_rpc import _single  # noqa: E402
from ankr import ankr_post  # noqa: E402

ADDR = "0x892E438425b3A41BC75b25C22Fd878b3fa2e308d"
TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO_TOPIC = "0x" + "00" * 32
EPS = ["https://bsc-dataseed.binance.org/",
       "https://bsc-dataseed1.bnbchain.org/"]


def rpc_call(method, params, timeout=10):
    last = None
    for ep in EPS:
        try:
            return _single(ep, method, params, timeout, retries=0)
        except Exception as e:  # noqa: BLE001
            last = e
    raise last


def block_time(blk):
    b = rpc_call("eth_getBlockByNumber", [hex(blk), False])
    return int(b["timestamp"], 16)


def main():
    # Search backwards from the scan-window first mint (132132467) in
    # 2000-block chunks to find the true first mint.
    to_block = 132132467
    from_block = 132120000
    first = None
    total_logs = 0
    while to_block >= from_block:
        chunk_from = max(from_block, to_block - 1999)
        params = {"blockchain": "bsc", "fromBlock": hex(chunk_from),
                  "toBlock": hex(to_block), "pageSize": 1000,
                  "decodeLogs": False, "address": ADDR,
                  "topics": [TRANSFER, ZERO_TOPIC]}
        body = ankr_post("ankr_getLogs", params, timeout=30)
        logs = body.get("result", {}).get("logs", []) if isinstance(body, dict) else []
        total_logs += len(logs)
        print(f"chunk {chunk_from}-{to_block}: {len(logs)} mint logs", flush=True)
        if logs:
            first = min(int(l["blockNumber"], 16) for l in logs)
            break
        to_block = chunk_from - 1
        time.sleep(1)
    if first is None:
        print("NO MINT FOUND back to", from_block, "- first mint may predate search or logs empty")
        first = 132132467
        print("FALLBACK first mint = scan-window first_block 132132467 (lower bound only)")
    ts = block_time(first)
    import datetime
    dt = datetime.datetime.fromtimestamp(ts, datetime.timezone(datetime.timedelta(hours=7)))
    now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=7)))
    age_h = (now - dt).total_seconds() / 3600
    print(json.dumps({"first_mint_block": first, "first_mint_wib": dt.strftime("%Y-%m-%d %H:%M:%S"),
                      "age_hours": round(age_h, 2), "logs_scanned": total_logs}))
    # also timestamp the scan-window first mint block for reference
    ts2 = block_time(132132467)
    dt2 = datetime.datetime.fromtimestamp(ts2, datetime.timezone(datetime.timedelta(hours=7)))
    print("scan-window first mint block 132132467 time WIB:", dt2.strftime("%Y-%m-%d %H:%M:%S"))


if __name__ == "__main__":
    main()
