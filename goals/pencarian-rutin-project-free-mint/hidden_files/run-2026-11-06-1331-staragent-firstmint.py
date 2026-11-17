#!/usr/bin/env python3
"""StarAgent-7d39 first-mint probe via Ankr getLogs (address-filtered Transfer from zero).
Walks backwards in 50k-block ranges from firstSeenBlock 131641156; stops at first empty range.
Ankr via existing proxy env; NEVER set no_proxy."""
import sys, time, json
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from ankr import ankr_post

ADDR = "0x7d390e37Ed41A359f276D8764ca15432704B99b7"
TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO = "0x" + "00" * 32
OUT = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/run-2026-11-06-1331-staragent-firstmint.json"
t0 = time.time()
res = {"address": ADDR, "ranges": [], "earliest_block": None, "elapsed_s": None}
hi = 131641156  # firstSeenBlock (exclusive upper bound for probe)
for i in range(6):
    lo = hi - 50000
    if lo < 0: lo = 0
    try:
        body = ankr_post("ankr_getLogs", {
            "blockchain": "bsc", "address": ADDR, "fromBlock": hex(lo), "toBlock": hex(hi - 1),
            "pageSize": 1000, "decodeLogs": False,
            "topics": [TRANSFER, ZERO]}, timeout=60)
        logs = body.get("result", {}).get("logs", []) if isinstance(body, dict) else []
        blocks = sorted(int(l["blockNumber"], 16) for l in logs)
        print(f"range {lo}-{hi-1}: {len(logs)} mint logs, earliest {blocks[0] if blocks else None}, latest {blocks[-1] if blocks else None}", flush=True)
        res["ranges"].append({"from": lo, "to": hi - 1, "count": len(logs),
                              "earliest": blocks[0] if blocks else None,
                              "latest": blocks[-1] if blocks else None,
                              "capped": len(logs) >= 1000})
        if blocks:
            if res["earliest_block"] is None or blocks[0] < res["earliest_block"]:
                res["earliest_block"] = blocks[0]
        if not logs:
            print("EMPTY range - first mint is after", lo, flush=True)
            break
        hi = lo
        if len(logs) >= 1000:
            print("CAPPED at 1000 - earliest in range may not be true first mint", flush=True)
    except Exception as e:
        print("RANGE FAIL", lo, hi - 1, repr(e)[:200], flush=True)
        res["ranges"].append({"from": lo, "to": hi - 1, "error": repr(e)[:200]})
        break
    if time.time() - t0 > 240:
        print("TIME BUDGET EXCEEDED", flush=True); break
res["elapsed_s"] = round(time.time() - t0, 1)
json.dump(res, open(OUT, "w"), indent=1)
print("EARLIEST", res["earliest_block"], "elapsed", res["elapsed_s"], flush=True)
