#!/usr/bin/env python3
"""Pre-flight for run 0801 scan (amendment 2026-11-06 ~07:49): one small
ankr_getLogs call (single 50-block chunk) must succeed in <60s.
Ankr MUST go through the existing proxy env; NEVER set no_proxy for rpc.ankr.com."""
import sys, time, json
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from fast_rpc import _single
from ankr import ankr_post

t0 = time.time()
latest = int(_single("https://bsc-dataseed1.bnbchain.org", "eth_blockNumber", [], 8, retries=0), 16)
print("head", latest, flush=True)
to_b = latest
from_b = latest - 49
body = ankr_post("ankr_getLogs", {
    "blockchain": "bsc", "fromBlock": hex(from_b), "toBlock": hex(to_b),
    "pageSize": 1000, "decodeLogs": False,
    "topics": ["0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef",
               "0x" + "00" * 32]}, timeout=30)
logs = body.get("result", {}).get("logs", []) if isinstance(body, dict) else []
print("PREFLIGHT OK blocks", from_b, "-", to_b, "logs", len(logs),
      "elapsed %.1fs" % (time.time() - t0), flush=True)
print(json.dumps({"head": latest, "from": from_b, "to": to_b, "logs": len(logs),
                  "elapsed": round(time.time() - t0, 1)}))
