#!/usr/bin/env python3
"""Run 140 sent-pass retry for wallets that failed with Ankr 'Remote end closed
connection' (0xdb2d83f9, 0x3a39aa05, 0x92bc3297). Same window as run138-sent.py; merges
results into run140-sent.json. Read-only."""
import json, sys, time, datetime
from pathlib import Path
sys.path.insert(0, str(Path.home() / "workspace/custom-connectors/custom.ankr/bin"))
import ankr as ankr_mod

HOME = Path.home()
jak = datetime.timezone(datetime.timedelta(hours=7))
FROM_BLOCK = 132526590
WALLETS = ["0xdb2d83f907965fb05ac23b8d40d3a327fc9ea52b"]
SR = HOME / "workspace/narrative-pulse/scan-runs"
sent = json.load(open(SR / "run140-sent.json"))
max_block = sent["max_block"]
for w in WALLETS:
    try:
        txs, page_token = [], None
        while True:
            params = {"blockchain": "bsc", "address": w, "pageSize": 50}
            if page_token: params["pageToken"] = page_token
            data = ankr_mod.ankr_post("ankr_getTransactionsByAddress", params)
            res = data.get("result") or {}
            batch = res.get("transactions") or []
            txs.extend(batch)
            page_token = res.get("nextPageToken")
            if not batch or not page_token: break
            try: oldest = int(batch[-1].get("blockNumber", "0"), 16)
            except Exception: oldest = 0
            if oldest <= FROM_BLOCK: break
            time.sleep(1.0)
        inw = []
        for t in txs:
            try: bni = int(t.get("blockNumber"), 16)
            except Exception: continue
            if bni <= FROM_BLOCK: continue
            max_block = max(max_block, bni)
            try: ts = int(t.get("timestamp", "0"), 16)
            except Exception: ts = 0
            inw.append({"hash": t.get("hash"), "block": bni, "to": t.get("to"),
                        "value": t.get("value"), "status": t.get("status"), "ts": ts,
                        "time_wib": datetime.datetime.fromtimestamp(ts, tz=jak).strftime("%Y-%m-%d %H:%M:%S WIB") if ts else None,
                        "input_prefix": (t.get("input") or "")[:10]})
        sent["results"][w] = {"ok": True, "in_window": inw}
        print(f"RETRY OK {w[:10]} in_window={len(inw)}", flush=True)
    except Exception as e:
        sent["results"][w] = {"ok": False, "error": str(e)[:300]}
        print(f"RETRY FAIL {w[:10]} {e}", flush=True)
    time.sleep(1.5)
sent["max_block"] = max_block
total = sum(len(r.get("in_window", [])) for r in sent["results"].values() if r.get("ok"))
failed = [w for w, r in sent["results"].items() if not r.get("ok")]
print(f"RETRY DONE total_in_window={total} max_block={max_block} failed={len(failed)} {failed}", flush=True)
json.dump(sent, open(SR / "run140-sent.json", "w"), indent=1)
