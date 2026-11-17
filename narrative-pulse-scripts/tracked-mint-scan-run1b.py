#!/usr/bin/env python3
"""Read-only run 1 (module version): Ankr ankr_getTransactionsByAddress via module import (no 4000-char CLI truncation)."""
import json, sys, time, datetime
from pathlib import Path
sys.path.insert(0, str(Path.home() / "workspace/custom-connectors/custom.ankr/bin"))
import ankr as ankr_mod

TIER = Path.home() / "workspace/narrative-pulse/tier-ab-watch-state.json"
OUT = Path("/tmp/tracked-scan-run1b.json")
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
jak = datetime.timezone(datetime.timedelta(hours=7))
start = datetime.datetime(2026, 11, 3, 8, 5, tzinfo=jak)
start_ts = int(start.timestamp())
print(f"unique={len(uniq)} window_start_ts={start_ts}", flush=True)
results = {}
for i, w in enumerate(uniq):
    try:
        data = ankr_mod.ankr_post("ankr_getTransactionsByAddress",
                                  {"blockchain": "bsc", "address": w, "pageSize": 20})
        txs = (data.get("result") or {}).get("transactions") or []
        in_window = []
        for t in txs:
            try:
                ts = int(t.get("timestamp", "0"), 16) if isinstance(t.get("timestamp"), str) else int(t.get("timestamp", 0))
            except Exception:
                ts = 0
            try:
                bni = int(t.get("blockNumber"), 16) if isinstance(t.get("blockNumber"), str) else int(t.get("blockNumber") or 0)
            except Exception:
                bni = 0
            if ts >= start_ts:
                dt = datetime.datetime.fromtimestamp(ts, tz=jak).strftime("%Y-%m-%d %H:%M WIB")
                in_window.append({"hash": t.get("hash"), "block": bni, "to": t.get("to"),
                                  "value": t.get("value"), "status": t.get("status"),
                                  "ts": ts, "time_wib": dt,
                                  "input_prefix": (t.get("input") or "")[:10]})
        # newest/oldest returned for ordering check
        def _ts(t):
            try:
                return int(t.get("timestamp", "0"), 16)
            except Exception:
                return 0
        results[w] = {"ok": True, "n_returned": len(txs),
                      "first_ts": _ts(txs[0]) if txs else None,
                      "last_ts": _ts(txs[-1]) if txs else None,
                      "in_window": in_window}
        print(f"[{i+1}/{len(uniq)}] {w[:10]} returned={len(txs)} in_window={len(in_window)} first_ts={results[w]['first_ts']} last_ts={results[w]['last_ts']}", flush=True)
    except Exception as e:
        results[w] = {"ok": False, "error": str(e)[:400]}
        print(f"[{i+1}/{len(uniq)}] {w[:10]} ERROR {e}", flush=True)
    time.sleep(2.0)
json.dump({"window_start_ts": start_ts, "unique": uniq, "results": results}, open(OUT, "w"), indent=1)
print(f"saved {OUT}", flush=True)
