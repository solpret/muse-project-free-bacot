#!/usr/bin/env python3
"""Read-only run 114 (2026-11-08 11:05 WIB): sent-tx pass via Ankr module + receipt
check via fast_rpc + inbound leg via Ankr getLogs address-filtered per known contract.
No preview/mint/sign/login/purchase."""
import json, sys, time, datetime
from pathlib import Path
from Crypto.Hash import keccak
sys.path.insert(0, str(Path.home() / "workspace/custom-connectors/custom.ankr/bin"))
sys.path.insert(0, str(Path.home() / "workspace/fast_exec"))
import ankr as ankr_mod
import fast_rpc

HOME = Path.home()
jak = datetime.timezone(datetime.timedelta(hours=7))
FROM_BLOCK = 132318096
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
state = json.load(open(HOME / "workspace/narrative-pulse/tracked-wallet-mint-scan-state.json"))
known_tx = set()
for f in state.get("reported_findings", []):
    for m in f.get("mints", []):
        if m.get("tx"): known_tx.add(m["tx"].lower())
print(f"wallets={len(uniq)} tier={len(tier['wallets'])} feed={len(feed)} from_block={FROM_BLOCK} known_tx={len(known_tx)}", flush=True)

results = {}
max_block = FROM_BLOCK
for i, w in enumerate(uniq):
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
        results[w] = {"ok": True, "in_window": inw}
        if inw: print(f"[{i+1}/{len(uniq)}] {w[:10]} in_window={len(inw)} blocks={inw[0]['block']}-{inw[-1]['block']}", flush=True)
    except Exception as e:
        results[w] = {"ok": False, "error": str(e)[:300]}
        print(f"[{i+1}/{len(uniq)}] {w[:10]} ERROR {e}", flush=True)
    time.sleep(1.5)
total_inw = sum(len(r.get("in_window", [])) for r in results.values() if r.get("ok"))
failed_wallets = [w for w, r in results.items() if not r.get("ok")]
print(f"SENT PASS DONE total_in_window={total_inw} max_block={max_block} failed={len(failed_wallets)}", flush=True)
json.dump({"from_block": FROM_BLOCK, "max_block": max_block, "results": results}, open("/home/hatch/workspace/narrative-pulse/scan-runs/run114-sent.json", "w"), indent=1)


