#!/usr/bin/env python3
"""Run 106 sent-pass same-run retry for the single failed wallet
0x81c3d1b4c9433bd5e52544ca96b19cfa9eb5de36 (Ankr 'Remote end closed').
Patches run106-sent.json in place; updates max_block if the retry finds later txs."""
import json, sys, time, datetime
from pathlib import Path
sys.path.insert(0, str(Path.home() / "workspace/custom-connectors/custom.ankr/bin"))
import ankr as ankr_mod

HOME = Path.home()
jak = datetime.timezone(datetime.timedelta(hours=7))
FROM_BLOCK = 132260250
W = "0x81c3d1b4c9433bd5e52544ca96b19cfa9eb5de36"
sent = json.load(open(HOME / "workspace/narrative-pulse/scan-runs/run106-sent.json"))
ok = False
for attempt in range(3):
    try:
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
        inw = []
        for t in txs:
            try: bni = int(t.get("blockNumber"), 16)
            except Exception: continue
            if bni <= FROM_BLOCK: continue
            try: ts = int(t.get("timestamp", "0"), 16)
            except Exception: ts = 0
            inw.append({"hash": t.get("hash"), "block": bni, "to": t.get("to"),
                        "value": t.get("value"), "status": t.get("status"), "ts": ts,
                        "time_wib": datetime.datetime.fromtimestamp(ts, tz=jak).strftime("%Y-%m-%d %H:%M:%S WIB") if ts else None,
                        "input_prefix": (t.get("input") or "")[:10]})
        sent["results"][W] = {"ok": True, "in_window": inw}
        if inw:
            sent["max_block"] = max(sent["max_block"], max(t["block"] for t in inw))
        print(f"RETRY OK attempt={attempt+1} in_window={len(inw)} max_block={sent['max_block']}", flush=True)
        ok = True
        break
    except Exception as e:
        print(f"RETRY attempt={attempt+1} ERROR {e}", flush=True)
        time.sleep(5)
if not ok:
    print("RETRY FAILED all 3 attempts - wallet stays failed; retry run 107", flush=True)
json.dump(sent, open(HOME / "workspace/narrative-pulse/scan-runs/run106-sent.json", "w"), indent=1)
print("saved run106-sent.json")
