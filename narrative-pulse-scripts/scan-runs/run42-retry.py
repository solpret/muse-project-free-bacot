#!/usr/bin/env python3
"""Read-only run 42 retry: sent-tx pass via Ankr module, per-wallet retries
(up to 4 attempts per wallet, 5s between) because Ankr egress flapped during
the first attempt (wallets 22+ timed out). No preview/mint/sign/login."""
import json, sys, time, datetime
from pathlib import Path
sys.path.insert(0, str(Path.home() / "workspace/custom-connectors/custom.ankr/bin"))
import ankr as ankr_mod

HOME = Path.home()
jak = datetime.timezone(datetime.timedelta(hours=7))
FROM_BLOCK = 131669961
OUT = HOME / "workspace/narrative-pulse/scan-runs/run42-sent.json"
tier = json.load(open(HOME / "workspace/narrative-pulse/tier-ab-watch-state.json"))
feed = ["0x8e966a9f17beab1ea50039434c2a14ad9e09b8d6",
        "0x2325f175975abdbcde555c79cc8e63381d28551b",
        "0xbf004bff64725914ee36d03b87d6965b0ced4903",
        "0x6ba79dcc05a1056e19bf1021db4fca7be18b49e7",
        "0x892200223bdfb11d2506c5ab1cae9222ce253acc",
        "0xda91cefe240175e6fab56271110427a4195ab71f"]
uniq = []
for w in list(tier["wallets"].keys()) + feed:
    if w.lower() not in uniq:
        uniq.append(w.lower())
user = {"0xeb237f6f9fb4e826739f0954e9768914f28b2c2e", "0xcf3c6fc1bf670a8d3f03436395286f86dbee7418"}
uniq = [w for w in uniq if w not in user]
print(f"wallets={len(uniq)} tier={len(tier['wallets'])} feed={len(feed)} from_block={FROM_BLOCK}", flush=True)

def fetch_wallet(w):
    """Returns (txs, error). Retries whole fetch up to 4 times."""
    last_err = None
    for attempt in range(1, 5):
        try:
            txs, page_token = [], None
            while True:
                params = {"blockchain": "bsc", "address": w, "pageSize": 50}
                if page_token:
                    params["pageToken"] = page_token
                data = ankr_mod.ankr_post("ankr_getTransactionsByAddress", params)
                res = data.get("result") or {}
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
            return txs, None, attempt
        except Exception as e:
            last_err = str(e)[:300]
            print(f"  {w[:10]} attempt {attempt} ERROR {last_err}", flush=True)
            time.sleep(5.0)
    return None, last_err, 4

results = {}
max_block = FROM_BLOCK
for i, w in enumerate(uniq):
    txs, err, attempts = fetch_wallet(w)
    if err is not None:
        results[w] = {"ok": False, "error": err, "attempts": attempts}
        print(f"[{i+1}/{len(uniq)}] {w[:10]} FAILED after {attempts} attempts", flush=True)
    else:
        inw = []
        for t in txs:
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
        results[w] = {"ok": True, "in_window": inw, "attempts": attempts}
        if inw:
            print(f"[{i+1}/{len(uniq)}] {w[:10]} in_window={len(inw)} blocks={inw[0]['block']}-{inw[-1]['block']} attempts={attempts}", flush=True)
    time.sleep(1.5)
total_inw = sum(len(r.get("in_window", [])) for r in results.values() if r.get("ok"))
failed_wallets = [w for w, r in results.items() if not r.get("ok")]
print(f"SENT PASS DONE total_in_window={total_inw} max_block={max_block} failed={len(failed_wallets)}", flush=True)
json.dump({"from_block": FROM_BLOCK, "max_block": max_block, "results": results}, open(OUT, "w"), indent=1)
print(f"RETRY_SENT_SUMMARY wallets_ok={sum(1 for r in results.values() if r.get('ok'))}/{len(uniq)} total={total_inw} max_block={max_block} failed_wallets={failed_wallets}", flush=True)
