#!/usr/bin/env python3
"""Read-only run 131 sent-pass retry: only the 9 wallets that failed in the
main pass (Ankr 'Remote end closed connection' / timeouts). Up to 2 attempts
per wallet with a pause between. Merges recovered results into
run131-sent.json. No preview/mint/sign/login."""
import json, sys, time, datetime
from pathlib import Path
sys.path.insert(0, str(Path.home() / "workspace/custom-connectors/custom.ankr/bin"))
import ankr as ankr_mod

HOME = Path.home()
SR = HOME / "workspace/narrative-pulse/scan-runs"
jak = datetime.timezone(datetime.timedelta(hours=7))
FROM_BLOCK = 132456149
sent = json.load(open(SR / "run131-sent.json"))
failed = [w for w, r in sent["results"].items() if not r.get("ok")]
print(f"retry wallets={len(failed)} from_block={FROM_BLOCK}", flush=True)
recovered = {}
for i, w in enumerate(failed):
    ok = False
    for attempt in (1, 2):
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
                try: ts = int(t.get("timestamp", "0"), 16)
                except Exception: ts = 0
                inw.append({"hash": t.get("hash"), "block": bni, "to": t.get("to"),
                            "value": t.get("value"), "status": t.get("status"), "ts": ts,
                            "time_wib": datetime.datetime.fromtimestamp(ts, tz=jak).strftime("%Y-%m-%d %H:%M:%S WIB") if ts else None,
                            "input_prefix": (t.get("input") or "")[:10]})
            recovered[w] = {"ok": True, "in_window": inw, "recovered_via_retry": True}
            print(f"[{i+1}/{len(failed)}] {w[:10]} RECOVERED attempt={attempt} in_window={len(inw)}", flush=True)
            ok = True
            break
        except Exception as e:
            print(f"[{i+1}/{len(failed)}] {w[:10]} attempt={attempt} ERROR {e}", flush=True)
            time.sleep(10)
    if not ok:
        recovered[w] = {"ok": False, "error": "retry failed both attempts"}
    time.sleep(1.5)
n_rec = sum(1 for r in recovered.values() if r.get("ok"))
tot = sum(len(r.get("in_window", [])) for r in recovered.values() if r.get("ok"))
new_max = sent["max_block"]
for r in recovered.values():
    if r.get("ok"):
        for t in r["in_window"]:
            new_max = max(new_max, t["block"])
for w, r in recovered.items():
    sent["results"][w] = r
sent["max_block"] = new_max
sent["sent_retry"] = {"recovered": n_rec, "failed_still": len(failed) - n_rec,
                      "recovered_in_window": tot}
json.dump(sent, open(SR / "run131-sent.json", "w"), indent=1)
print(f"SENT RETRY DONE recovered={n_rec}/{len(failed)} recovered_in_window={tot} new_max_block={new_max}", flush=True)
