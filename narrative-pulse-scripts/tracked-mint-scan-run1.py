#!/usr/bin/env python3
"""Read-only first run: tracked-wallet-mint-scan-hourly, 2026-11-03 09:05 WIB.
Sent txs in last hour via Ankr ankr_getTransactionsByAddress (module path, not CLI truncation).
No preview/mint/sign/login. Failures recorded as unverified, never zero."""
import json, subprocess, sys, time, datetime
from pathlib import Path

TIER = Path.home() / "workspace/narrative-pulse/tier-ab-watch-state.json"
OUT = Path("/tmp/tracked-scan-run1.json")
tier = json.load(open(TIER))
wallets = list(tier["wallets"].keys())
feed = ["0x8e966a9f17beab1ea50039434c2a14ad9e09b8d6",
        "0x2325f175975abdbcde555c79cc8e63381d28551b",
        "0xbf004bff64725914ee36d03b87d6965b0ced4903"]
uniq = []
for w in wallets + feed:
    wl = w.lower()
    if wl not in uniq:
        uniq.append(wl)
print(f"tier_ab={len(wallets)} feed={len(feed)} unique={len(uniq)}", flush=True)

# Window: 1 hour before scheduled run 09:05 WIB 2026-11-03
jak = datetime.timezone(datetime.timedelta(hours=7))
start = datetime.datetime(2026, 11, 3, 8, 5, tzinfo=jak)
start_ts = int(start.timestamp())
print(f"window_start_wib={start} ts={start_ts}", flush=True)

results = {}
for i, w in enumerate(uniq):
    params = json.dumps({"blockchain": "bsc", "address": w, "pageSize": 20})
    try:
        r = subprocess.run(
            [sys.executable, str(Path.home() / "workspace/custom-connectors/custom.ankr/bin/ankr.py"),
             "raw", "ankr_getTransactionsByAddress", params],
            capture_output=True, text=True, timeout=60)
        data = json.loads(r.stdout)
        txs = (data.get("result") or {}).get("transactions") or []
        in_window = []
        latest = None
        for t in txs:
            try:
                ts = int(t.get("timestamp", "0"), 16) if isinstance(t.get("timestamp"), str) else int(t.get("timestamp", 0))
            except Exception:
                ts = 0
            bn = t.get("blockNumber")
            try:
                bni = int(bn, 16) if isinstance(bn, str) else int(bn or 0)
            except Exception:
                bni = 0
            if latest is None:
                latest = {"hash": t.get("hash"), "block": bni, "ts": ts}
            if ts >= start_ts:
                dt = datetime.datetime.fromtimestamp(ts, tz=jak).strftime("%Y-%m-%d %H:%M WIB")
                in_window.append({"hash": t.get("hash"), "block": bni, "to": t.get("to"),
                                  "value": t.get("value"), "status": t.get("status"),
                                  "ts": ts, "time_wib": dt,
                                  "input_prefix": (t.get("input") or "")[:10]})
        results[w] = {"ok": True, "n_returned": len(txs), "latest": latest, "in_window": in_window}
        print(f"[{i+1}/{len(uniq)}] {w[:10]} returned={len(txs)} in_window={len(in_window)} latest_block={latest['block'] if latest else None}", flush=True)
    except Exception as e:
        results[w] = {"ok": False, "error": str(e)[:300]}
        print(f"[{i+1}/{len(uniq)}] {w[:10]} ERROR {e}", flush=True)
    time.sleep(2.0)  # stay under Ankr 30/min
json.dump({"window_start_ts": start_ts, "window_start_wib": str(start),
           "unique": uniq, "results": results}, open(OUT, "w"), indent=1)
print(f"saved {OUT}", flush=True)
