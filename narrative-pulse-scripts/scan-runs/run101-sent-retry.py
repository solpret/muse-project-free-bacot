#!/usr/bin/env python3
"""Run 101 sent-pass single-wallet retry (read-only): wallet 0x5b4beded failed
first attempt with Ankr 'Remote end closed connection'. Merge into run101-sent.json."""
import json, sys, time, datetime
from pathlib import Path
sys.path.insert(0, str(Path.home() / "workspace/custom-connectors/custom.ankr/bin"))
import ankr as ankr_mod
HOME = Path.home()
jak = datetime.timezone(datetime.timedelta(hours=7))
FROM_BLOCK = 132192617
W = "0x5b4beded36c1ea380abe8c6a6a0c4408f38e5024"
txs, page_token = [], None
while True:
    params = {"blockchain": "bsc", "address": W, "pageSize": 50}
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
inw, max_block = [], FROM_BLOCK
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
print(f"retry wallet {W[:10]} in_window={len(inw)} max_block={max_block}", flush=True)
s = json.load(open("/home/hatch/workspace/narrative-pulse/scan-runs/run101-sent.json"))
s["results"][W] = {"ok": True, "in_window": inw}
s["max_block"] = max(s["max_block"], max_block)
json.dump(s, open("/home/hatch/workspace/narrative-pulse/scan-runs/run101-sent.json", "w"), indent=1)
print("merged; total_in_window now", sum(len(r.get("in_window", [])) for r in s["results"].values() if r.get("ok")))
