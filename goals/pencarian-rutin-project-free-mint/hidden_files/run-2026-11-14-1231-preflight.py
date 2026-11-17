#!/usr/bin/env python3
"""Ankr pre-flight run 2026-11-14 12:31 WIB: one small ankr_getLogs call (50 blocks), <60s.
Calls scan.ankr_logs directly (correct helper name). Read-only; fast-fail expected."""
import json, sys, time
t0 = time.time()
sys.path.insert(0, "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/")
import onchain_nft_scan as scan
TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
out = {"started_wib": "2026-11-14T12:31+07:00", "preflight": None, "elapsed_s": None}
try:
    logs, pages = scan.ankr_logs(133484000, 133484050, [TRANSFER])
    out["preflight"] = {"ok": True, "logs": len(logs), "pages": pages}
except Exception as e:
    out["preflight"] = {"ok": False, "error": str(e)[:300]}
out["elapsed_s"] = round(time.time() - t0, 1)
json.dump(out, open("/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/run-2026-11-14-1231-preflight.json", "w"), indent=1)
print(json.dumps(out, indent=1))
