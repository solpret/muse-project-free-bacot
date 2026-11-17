#!/usr/bin/env python3
"""Scan pre-flight for free-mint-search run 2026-11-14 01:01 WIB.
One small ankr_getLogs call (50 blocks); must succeed in <60s or scan leg fast-fails."""
import sys, time, json
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from ankr import ankr_post
t0 = time.time()
# current head via public dataseed (Ankr eth_blockNumber is known-flaky)
import subprocess
def head():
    for ep in ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/"]:
        try:
            out = subprocess.run(["curl", "-sL", "--max-time", "15", "-X", "POST", ep,
                "-H", "Content-Type: application/json",
                "-d", json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []})],
                capture_output=True, text=True, timeout=20).stdout
            r = json.loads(out)
            if r.get("result"): return int(r["result"], 16)
        except Exception:
            continue
    return None
h = head()
print("head:", h, "elapsed:", round(time.time() - t0, 1), flush=True)
if h is None:
    print("PREFLIGHT_FAIL: no head", flush=True); sys.exit(2)
ZERO_TOPIC = "0x" + "0" * 64
TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
params = {"blockchain": "bsc", "fromBlock": hex(h - 50), "toBlock": hex(h),
          "topics": [TRANSFER, ZERO_TOPIC], "pageSize": 10}
try:
    body = ankr_post("ankr_getLogs", params, timeout=45)
    print("PREFLIGHT_OK elapsed:", round(time.time() - t0, 1), "logs:", len(body.get("logs", [])) if isinstance(body, dict) else body, flush=True)
except Exception as e:
    print("PREFLIGHT_FAIL elapsed:", round(time.time() - t0, 1), "error:", str(e)[:300], flush=True)
    sys.exit(2)
