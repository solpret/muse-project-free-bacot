#!/usr/bin/env python3
"""Pre-flight for free-mint-search run 2026-11-12-1531: one small ankr_getLogs
call (single 50-block chunk) via the Ankr module (never CLI). Exit 0 on
success, 1 on failure. Prints elapsed time and log count."""
import json
import sys
import time

sys.path.insert(0, "/home/hatch/workspace/fast_exec")
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from fast_rpc import _single  # noqa: E402
from ankr import ankr_post  # noqa: E402

TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO_TOPIC = "0x" + "00" * 32
EPS = ["https://bsc-dataseed.binance.org/",
       "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/",
       "https://bsc-dataseed3.bnbchain.org/"]


def rpc_call(method, params, timeout=8):
    last = None
    for ep in EPS:
        try:
            return _single(ep, method, params, timeout, retries=0)
        except Exception as e:  # noqa: BLE001
            last = e
    raise last


def main():
    t0 = time.time()
    latest = int(rpc_call("eth_blockNumber", []), 16)
    to_block = latest
    from_block = latest - 49
    params = {"blockchain": "bsc", "fromBlock": hex(from_block),
              "toBlock": hex(to_block), "pageSize": 1000,
              "decodeLogs": False, "topics": [TRANSFER, ZERO_TOPIC]}
    body = ankr_post("ankr_getLogs", params, timeout=30)
    result = body.get("result", {}) if isinstance(body, dict) else {}
    logs = result.get("logs", [])
    elapsed = time.time() - t0
    print(json.dumps({"preflight": "OK", "head": latest,
                      "chunk": [from_block, to_block],
                      "logs_returned": len(logs),
                      "elapsed_s": round(elapsed, 2)}), flush=True)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:  # noqa: BLE001
        print(json.dumps({"preflight": "FAIL", "error": str(e)}), flush=True)
        sys.exit(1)
