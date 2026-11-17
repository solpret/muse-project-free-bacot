#!/usr/bin/env python3
"""Ankr pre-flight run 2026-11-14 06:31 WIB: one small ankr_getLogs call, <60s.
Uses the Ankr module path from onchain_nft_scan.py if importable; else direct
JSON-RPC to the Ankr endpoint from env/proxy. Read-only; fast-fail expected."""
import json, os, subprocess, time, sys
t0 = time.time()
# Reuse the scan script's Ankr call helper if present
sys.path.insert(0, "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/")
try:
    import onchain_nft_scan as scan
    fn = getattr(scan, "ankr_getLogs", None) or getattr(scan, "ankr_get_logs", None)
    print("scan module fns:", [n for n in dir(scan) if "ankr" in n.lower() or "getLogs" in n], flush=True)
except Exception as e:
    print("scan import failed:", e, flush=True)
    fn = None
TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
out = {"started_wib": "2026-11-14T06:31+07:00", "preflight": None, "elapsed_s": None}
if fn:
    try:
        r = fn(133438600, 133438650, timeout=55)
        out["preflight"] = {"ok": True, "logs": len(r) if isinstance(r, list) else str(type(r))}
    except Exception as e:
        out["preflight"] = {"ok": False, "error": str(e)[:300]}
else:
    out["preflight"] = {"ok": False, "error": "no ankr helper found in scan module"}
out["elapsed_s"] = round(time.time() - t0, 1)
json.dump(out, open("/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/run-2026-11-14-0631-preflight.json", "w"), indent=1)
print(json.dumps(out, indent=1))
