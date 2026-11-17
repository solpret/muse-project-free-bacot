#!/usr/bin/env python3
"""Read-only run 43 tail + failed-wallet retry.
Reuses run42-sent.json (02:05 attempt, window blocks >131669961, mopup max
131684753) as the bulk sent pass, then:
 (a) retries the single failed wallet 0x13d1... over the FULL window
     (>131669961), up to 3 attempts;
 (b) fresh tail pass for all 55 wallets over blocks >131684753 up to now.
Merges into run43-sent.json. No preview/mint/sign/login/purchase."""
import json, sys, time, datetime
from pathlib import Path
sys.path.insert(0, str(Path.home() / "workspace/custom-connectors/custom.ankr/bin"))
import ankr as ankr_mod

HOME = Path.home()
jak = datetime.timezone(datetime.timedelta(hours=7))
OLD = json.load(open(HOME / "workspace/narrative-pulse/scan-runs/run42-sent.json"))
results = OLD["results"]
FULL_FROM = 131669961
TAIL_FROM = OLD["max_block"]  # 131684753
print(f"base: wallets={len(results)} ok={sum(1 for r in results.values() if r.get('ok'))} "
      f"total={sum(len(r.get('in_window', [])) for r in results.values() if r.get('ok'))} "
      f"tail_from={TAIL_FROM}", flush=True)

def fetch(w, from_block, max_attempts=3):
    """Return (in_window list, error or None). Pages newest-first until oldest <= from_block."""
    last_err = None
    for att in range(max_attempts):
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
                if oldest <= from_block:
                    break
                time.sleep(1.0)
            inw = []
            for t in txs:
                try:
                    bni = int(t.get("blockNumber"), 16)
                except Exception:
                    continue
                if bni <= from_block:
                    continue
                try:
                    ts = int(t.get("timestamp", "0"), 16)
                except Exception:
                    ts = 0
                inw.append({"hash": t.get("hash"), "block": bni, "to": t.get("to"),
                            "value": t.get("value"), "status": t.get("status"), "ts": ts,
                            "time_wib": datetime.datetime.fromtimestamp(ts, tz=jak).strftime("%Y-%m-%d %H:%M:%S WIB") if ts else None,
                            "input_prefix": (t.get("input") or "")[:10]})
            return inw, None
        except Exception as e:
            last_err = str(e)[:300]
            print(f"  {w[:10]} attempt {att+1} ERROR {last_err}", flush=True)
            time.sleep(5.0)
    return None, last_err

# (a) failed wallet, full window
failed_wallet = "0x13d1e9a96eba7906e1ede348c9bb604a03e46d02"
inw, err = fetch(failed_wallet, FULL_FROM)
if err is None:
    results[failed_wallet] = {"ok": True, "in_window": inw, "note": "run43 retry of run42-failed wallet, full window"}
    print(f"RETRY {failed_wallet[:10]} OK in_window={len(inw)}", flush=True)
else:
    print(f"RETRY {failed_wallet[:10]} STILL FAILED: {err} (leg unverified, NOT zero)", flush=True)

# (b) tail pass for all wallets
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
print(f"tail wallets={len(uniq)} tier={len(tier['wallets'])} feed={len(feed)}", flush=True)
tail_total, tail_failed = 0, []
max_block = TAIL_FROM
for i, w in enumerate(uniq):
    if w == failed_wallet:
        # already fetched full window above (covers tail too); do not double-count
        tail_total += 0
        continue
    inw, err = fetch(w, TAIL_FROM)
    if err is not None:
        tail_failed.append(w)
        print(f"[{i+1}/{len(uniq)}] {w[:10]} TAIL FAILED: {err} (tail unverified for this wallet, NOT zero)", flush=True)
        continue
    if inw:
        seen = {t["hash"] for t in results[w].get("in_window", [])} if results.get(w, {}).get("ok") else set()
        new = [t for t in inw if t["hash"] not in seen]
        if results.get(w, {}).get("ok"):
            results[w]["in_window"].extend(new)
        else:
            results[w] = {"ok": True, "in_window": new}
        tail_total += len(new)
        max_block = max(max_block, max(t["block"] for t in new))
        print(f"[{i+1}/{len(uniq)}] {w[:10]} tail_new={len(new)}", flush=True)
    time.sleep(1.5)
total = sum(len(r.get("in_window", [])) for r in results.values() if r.get("ok"))
still_failed = [w for w, r in results.items() if not r.get("ok")]
print(f"TAIL DONE tail_new={tail_total} total_in_window={total} max_block={max_block} "
      f"tail_failed={tail_failed} still_failed_overall={still_failed}", flush=True)
json.dump({"from_block": FULL_FROM, "tail_from": TAIL_FROM, "max_block": max_block,
           "results": results, "tail_failed": tail_failed, "still_failed": still_failed},
          open(HOME / "workspace/narrative-pulse/scan-runs/run43-sent.json", "w"), indent=1)
print("saved run43-sent.json", flush=True)
