#!/usr/bin/env python3
"""Pre-flight run 2026-11-09 0931 WIB — one small Ankr ankr_getLogs call
(50 blocks, chain-wide Transfer topic), must succeed within <60s.
If it fails twice -> scan leg FAST-FAILS for this run (log + continue).
Read-only; writes run-2026-11-09-1301-preflight.json only.
"""
import json, sys, time
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from ankr import ankr_post

TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
FROM = 132536750
TO = 132536799
out = {"run": "2026-11-09-1301", "from": FROM, "to": TO, "attempts": []}
for i in (1, 2):
    t0 = time.time()
    try:
        res = ankr_post("ankr_getLogs", {
            "blockchain": "bsc",
            "fromBlock": str(FROM),
            "toBlock": str(TO),
            "topics": [TRANSFER],
            "pageSize": 1000,
        }, timeout=55)
        dt = time.time() - t0
        n = len(res.get("result", {}).get("logs", [])) if isinstance(res, dict) else -1
        out["attempts"].append({"n": i, "ok": True, "seconds": round(dt, 1), "logs": n})
        print(f"ATTEMPT {i}: OK {dt:.1f}s logs={n}", flush=True)
        out["preflight_ok"] = True
        break
    except Exception as e:
        dt = time.time() - t0
        out["attempts"].append({"n": i, "ok": False, "seconds": round(dt, 1), "error": str(e)[:300]})
        print(f"ATTEMPT {i}: FAIL {dt:.1f}s {str(e)[:200]}", flush=True)
        out["preflight_ok"] = False
json.dump(out, open("/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/run-2026-11-09-1301-preflight.json", "w"), indent=1)
print("PREFLIGHT", "OK" if out["preflight_ok"] else "FAIL")
