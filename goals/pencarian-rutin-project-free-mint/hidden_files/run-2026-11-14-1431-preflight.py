#!/usr/bin/env python3
"""Ankr pre-flight run 2026-11-14 14:31 WIB: one small ankr_getLogs call (50 blocks), <60s.
Calls scan.ankr_logs directly. Read-only; fast-fail expected (401 outage since 9 Nov)."""
import json, sys, time, urllib.request
t0 = time.time()
sys.path.insert(0, "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/")
import onchain_nft_scan as scan
TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
out = {"started_wib": "2026-11-14T14:31+07:00", "preflight": None, "elapsed_s": None, "head": None}
try:
    req = urllib.request.Request("https://bsc-dataseed.binance.org/",
        data=json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}).encode(),
        headers={"Content-Type": "application/json"})
    head = int(json.load(urllib.request.urlopen(req, timeout=30))["result"], 16)
    out["head"] = head
    try:
        logs, pages = scan.ankr_logs(head - 50, head, [TRANSFER])
        out["preflight"] = {"ok": True, "logs": len(logs), "pages": pages}
    except Exception as e:
        out["preflight"] = {"ok": False, "error": str(e)[:300]}
except Exception as e:
    out["preflight"] = {"ok": False, "error": "head-fetch failed: " + str(e)[:200]}
out["elapsed_s"] = round(time.time() - t0, 1)
json.dump(out, open(BASE + "run-2026-11-14-1431-preflight.json", "w"), indent=1)
print(json.dumps(out, indent=1))
