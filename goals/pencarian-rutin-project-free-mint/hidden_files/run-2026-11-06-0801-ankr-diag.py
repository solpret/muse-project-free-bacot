#!/usr/bin/env python3
"""Diagnostic: cross-check Ankr address-filtered Transfer counts vs the scan's own counts."""
import sys, json, time
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from ankr import ankr_post
TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO_TOPIC = "0x" + "00" * 32
def count_logs(addr, frm, to, topics):
    total = 0; token = None; pages = 0
    while True:
        params = {"blockchain": "bsc", "fromBlock": hex(frm), "toBlock": hex(to),
                  "pageSize": 1000, "decodeLogs": False, "address": addr, "topics": topics}
        if token: params["pageToken"] = token
        body = ankr_post("ankr_getLogs", params, timeout=30)
        result = body.get("result", {}) if isinstance(body, dict) else {}
        logs = result.get("logs", [])
        total += len(logs)
        token = result.get("nextPageToken"); pages += 1
        if not token or pages >= 15: break
        time.sleep(2.2)
    return total, pages
# Cross-check 1: scan window counts (scan found Cloudpuff 4, Tacotron 39 mints)
for name, addr in [("Cloudpuff", "0xe09131bBb48E653C5b2D64099324f14000d67De5"),
                   ("Tacotron", "0x05deBE4445232205AE7E79d02cb5DE5AA0641efF")]:
    c1, p1 = count_logs(addr, 131918215, 131919214, [TRANSFER, ZERO_TOPIC])
    print(f"{name} window Transfer-from-zero: {c1} (pages {p1})", flush=True)
    c2, p2 = count_logs(addr, 131899549, 131918589, [TRANSFER])
    print(f"{name} gap ALL Transfer: {c2} (pages {p2})", flush=True)
    c3, p3 = count_logs(addr, 131899549, 131918589, [TRANSFER, ZERO_TOPIC])
    print(f"{name} gap Transfer-from-zero: {c3} (pages {p3})", flush=True)
