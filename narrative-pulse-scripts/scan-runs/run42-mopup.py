#!/usr/bin/env python3
"""Read-only run 42 mop-up: retry only the 5 wallets that failed the retry
sent pass, up to 3 attempts each with 10s between attempts. Updates
run42-sent.json in place. No preview/mint/sign/login."""
import json, sys, time, datetime
from pathlib import Path
sys.path.insert(0, str(Path.home() / "workspace/custom-connectors/custom.ankr/bin"))
import ankr as ankr_mod

HOME = Path.home()
jak = datetime.timezone(datetime.timedelta(hours=7))
FROM_BLOCK = 131669961
SENT = HOME / "workspace/narrative-pulse/scan-runs/run42-sent.json"
data = json.load(open(SENT))
results = data["results"]
max_block = data["max_block"]
failed = [w for w, r in results.items() if not r.get("ok")]
print(f"mopup targets={failed}", flush=True)
for w in failed:
    got = None
    for attempt in range(1, 4):
        try:
            txs, page_token = [], None
            while True:
                params = {"blockchain": "bsc", "address": w, "pageSize": 50}
                if page_token:
                    params["pageToken"] = page_token
                res = (ankr_mod.ankr_post("ankr_getTransactionsByAddress", params).get("result") or {})
                batch = res.get("transactions") or []
                txs.extend(batch)
                page_token = res.get("nextPageToken")
                if not batch or not page_token:
                    break
                try:
                    oldest = int(batch[-1].get("blockNumber", "0"), 16)
                except Exception:
                    oldest = 0
                if oldest <= FROM_BLOCK:
                    break
                time.sleep(1.0)
            got = txs
            break
        except Exception as e:
            print(f"  {w[:10]} mopup attempt {attempt} ERROR {str(e)[:200]}", flush=True)
            time.sleep(10.0)
    if got is None:
        print(f"  {w[:10]} MOPUP FAILED", flush=True)
        continue
    inw = []
    for t in got:
        try:
            bni = int(t.get("blockNumber"), 16)
        except Exception:
            continue
        if bni <= FROM_BLOCK:
            continue
        max_block = max(max_block, bni)
        try:
            ts = int(t.get("timestamp", "0"), 16)
        except Exception:
            ts = 0
        inw.append({"hash": t.get("hash"), "block": bni, "to": t.get("to"),
                    "value": t.get("value"), "status": t.get("status"), "ts": ts,
                    "time_wib": datetime.datetime.fromtimestamp(ts, tz=jak).strftime("%Y-%m-%d %H:%M:%S WIB") if ts else None,
                    "input_prefix": (t.get("input") or "")[:10]})
    results[w] = {"ok": True, "in_window": inw, "attempts": "mopup"}
    print(f"  {w[:10]} MOPUP OK in_window={len(inw)}", flush=True)
    time.sleep(3.0)
data["max_block"] = max_block
data["results"] = results
json.dump(data, open(SENT, "w"), indent=1)
still = [w for w, r in results.items() if not r.get("ok")]
tot = sum(len(r.get("in_window", [])) for r in results.values() if r.get("ok"))
print(f"MOPUP_DONE max_block={max_block} total_inw={tot} still_failed={still}", flush=True)
