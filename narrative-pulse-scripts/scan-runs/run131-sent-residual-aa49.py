#!/usr/bin/env python3
"""Read-only run 131 residual: re-read sent txs for 0xaa49e7fec503664a39598645c7a3fbfa0374380d
for the run-130 window 132445937-132456148 (failed main pass + 2 retry attempts in run 130).
Output merges into run131-sent-residual-aa49.json; parent merges into run130-sent.json.
No preview/mint/sign/login."""
import json, sys, time, datetime
from pathlib import Path
sys.path.insert(0, str(Path.home() / "workspace/custom-connectors/custom.ankr/bin"))
import ankr as ankr_mod

HOME = Path.home()
SR = HOME / "workspace/narrative-pulse/scan-runs"
jak = datetime.timezone(datetime.timedelta(hours=7))
WALLET = "0xaa49e7fec503664a39598645c7a3fbfa0374380d"
FROM_BLOCK = 132445937
TO_BLOCK = 132456148
ok = False
for attempt in (1, 2, 3):
    try:
        txs, page_token = [], None
        while True:
            params = {"blockchain": "bsc", "address": WALLET, "pageSize": 50}
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
            if bni <= FROM_BLOCK or bni > TO_BLOCK: continue
            try: ts = int(t.get("timestamp", "0"), 16)
            except Exception: ts = 0
            inw.append({"hash": t.get("hash"), "block": bni, "to": t.get("to"),
                        "value": t.get("value"), "status": t.get("status"), "ts": ts,
                        "time_wib": datetime.datetime.fromtimestamp(ts, tz=jak).strftime("%Y-%m-%d %H:%M:%S WIB") if ts else None,
                        "input_prefix": (t.get("input") or "")[:10]})
        json.dump({"wallet": WALLET, "from_block": FROM_BLOCK, "to_block": TO_BLOCK,
                   "ok": True, "attempt": attempt, "in_window": inw},
                  open(SR / "run131-sent-residual-aa49.json", "w"), indent=1)
        print(f"RESIDUAL SENT DONE wallet={WALLET[:10]} attempt={attempt} in_window={len(inw)}", flush=True)
        for t in inw:
            print(f"  {t['hash'][:12]} block={t['block']} to={t['to']} sel={t['input_prefix']} val={t['value']} time={t['time_wib']}", flush=True)
        ok = True
        break
    except Exception as e:
        print(f"attempt={attempt} ERROR {e}", flush=True)
        time.sleep(10)
if not ok:
    json.dump({"wallet": WALLET, "from_block": FROM_BLOCK, "to_block": TO_BLOCK,
               "ok": False, "error": "all 3 attempts failed", "in_window": []},
              open(SR / "run131-sent-residual-aa49.json", "w"), indent=1)
    print("RESIDUAL SENT FAILED all 3 attempts - window STILL UNVERIFIED, carry to run 132", flush=True)
