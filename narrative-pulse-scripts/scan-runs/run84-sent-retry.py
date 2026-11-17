#!/usr/bin/env python3
"""Run 84 sent-pass retry: the 8 wallets that failed the main sent pass
(Ankr urlopen timeout burst). Same window FROM_BLOCK=132031247, same Ankr
module method. Merges into run84-sent.json. Read-only."""
import json, sys, time, datetime
from pathlib import Path
sys.path.insert(0, str(Path.home() / "workspace/custom-connectors/custom.ankr/bin"))
import ankr as ankr_mod

HOME = Path.home()
jak = datetime.timezone(datetime.timedelta(hours=7))
FROM_BLOCK = 132031247
SENT_PATH = HOME / "workspace/narrative-pulse/scan-runs/run84-sent.json"
sent = json.load(open(SENT_PATH))
failed = [w for w, r in sent["results"].items() if not r.get("ok")]
print(f"retrying {len(failed)} wallets from_block={FROM_BLOCK}", flush=True)
max_block = sent["max_block"]
for i, w in enumerate(failed):
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
        sent["results"][w] = {"ok": True, "in_window": inw, "retried": True}
        print(f"[{i+1}/{len(failed)}] {w[:10]} OK in_window={len(inw)}", flush=True)
    except Exception as e:
        sent["results"][w] = {"ok": False, "error": str(e)[:300], "retried": True}
        print(f"[{i+1}/{len(failed)}] {w[:10]} STILL FAILED {e}", flush=True)
    time.sleep(1.5)
sent["max_block"] = max_block
still = [w for w, r in sent["results"].items() if not r.get("ok")]
tot = sum(len(r.get("in_window", [])) for r in sent["results"].values() if r.get("ok"))
print(f"SENT RETRY DONE total_in_window={tot} max_block={max_block} still_failed={len(still)} {still}", flush=True)
json.dump(sent, open(SENT_PATH, "w"), indent=1)
print("saved run84-sent.json", flush=True)
