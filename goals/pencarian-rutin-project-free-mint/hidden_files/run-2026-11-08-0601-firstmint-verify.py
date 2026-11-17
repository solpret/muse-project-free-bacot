#!/usr/bin/env python3
"""Verify first-mint blocks for Ghostling/Voltoad with chunked <=1000-block
probes over [48h-boundary+1000, first_mint_block-1]. Any hit => first mint
is EARLIER than the binary-search answer. Read-only."""
import sys, json
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from ankr import ankr_post
ZERO = "0x" + "00"*32
TOPIC = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
def count_mints(addr, lo, hi):
    body = ankr_post("ankr_getLogs", {"blockchain": "bsc", "fromBlock": hex(lo),
        "toBlock": hex(hi), "pageSize": 1000, "decodeLogs": False,
        "address": addr, "topics": [TOPIC, ZERO]}, timeout=30)
    logs = body.get("result", {}).get("logs", [])
    return len(logs)
out = {}
for name, (addr, fb) in {
  "Ghostling": ("0x6a4847cb5f658943222fbd23d2520049f824789d", 131912632),
  "Voltoad": ("0xbc95e0a5bb1305958ba3263c6e9943b7a2554757", 131912458),
}.items():
    lo, hi = 131907767, fb - 1
    total = 0; chunks = []
    c = lo
    while c <= hi:
        ce = min(c + 999, hi)
        n = count_mints(addr, c, ce)
        chunks.append((c, ce, n)); total += n
        print(f"{name} [{c},{ce}] = {n}", flush=True)
        c = ce + 1
    out[name] = {"window": [lo, hi], "total_mints_before_claimed_first": total, "chunks": chunks,
                 "confirmed_first_mint_block": fb if total == 0 else "EARLIER - first mint < claimed block"}
    print(name, "TOTAL before claimed first:", total, flush=True)
json.dump(out, open("run-2026-11-08-0601-firstmint-verify.json", "w"), indent=1)
print("DONE")
