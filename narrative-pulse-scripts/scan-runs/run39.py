#!/usr/bin/env python3
"""Read-only run 39 (2026-11-04 21:05 WIB): sent-tx pass via Ankr module + receipt
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
FROM_BLOCK = 131646484
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
json.dump({"from_block": FROM_BLOCK, "max_block": max_block, "results": results}, open("/home/hatch/workspace/narrative-pulse/scan-runs/run39-sent.json", "w"), indent=1)

def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode()); return "0x" + k.hexdigest()[:8]
APPROVE = sel("approve(address,uint256)")
cands = []
for w, r in results.items():
    if not r.get("ok"): continue
    for t in r["in_window"]:
        if t["input_prefix"] == APPROVE: continue
        cands.append((w, t))
print(f"receipt candidates={len(cands)} (all non-approve in-window txs)", flush=True)
receipts = {}
for j in range(0, len(cands), 6):
    chunk = cands[j:j+6]
    calls = [("eth_getTransactionReceipt", [t["hash"]]) for _, t in chunk]
    try:
        res = fast_rpc.batch(calls)
    except Exception as e:
        print(f"receipt batch {j} batch ERROR {e}; falling back to race per tx", flush=True)
        res = []
        for _, t in chunk:
            try: res.append(fast_rpc.race("eth_getTransactionReceipt", [t["hash"]]))
            except Exception as e2: res.append(None); print(f"  race {t['hash'][:12]} ERROR {e2}", flush=True)
    for (w, t), r in zip(chunk, res if isinstance(res, list) else []):
        receipts[t["hash"]] = r
    time.sleep(4.0)
# parse mint logs
def topic(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode()); return "0x" + k.hexdigest()
T_TRANSFER = topic("Transfer(address,address,uint256)")
T_SINGLE = topic("TransferSingle(address,address,address,uint256,uint256)")
T_BATCH = topic("TransferBatch(address,address,address,uint256[],uint256[])")
ZERO_PAD = "0x" + "0" * 64
parsed = {}
for w, t in cands:
    r = receipts.get(t["hash"])
    if r is None:
        parsed[t["hash"]] = {"wallet": w, "to": t["to"], "selector": t["input_prefix"], "value": t["value"], "time_wib": t["time_wib"], "status": "receipt_null"}
        continue
    logs = r.get("logs") or []
    mint_logs = []
    for lg in logs:
        topics = lg.get("topics") or []
        if not topics: continue
        if topics[0] == T_TRANSFER and len(topics) >= 3 and topics[1] == ZERO_PAD:
            mint_logs.append({"contract": lg.get("address"), "to_topic": topics[2], "data": lg.get("data")})
        elif topics[0] in (T_SINGLE, T_BATCH) and len(topics) >= 4 and topics[2] == ZERO_PAD:
            mint_logs.append({"contract": lg.get("address"), "to_topic": topics[3], "data": lg.get("data"), "batch": True})
    parsed[t["hash"]] = {"wallet": w, "to": t["to"], "selector": t["input_prefix"], "value": t["value"], "time_wib": t["time_wib"],
                         "receipt_status": r.get("status"), "n_logs": len(logs), "mint_logs": mint_logs}
json.dump(parsed, open("/home/hatch/workspace/narrative-pulse/scan-runs/run39-receipts.json", "w"), indent=1)
n_mint = sum(1 for v in parsed.values() if v.get("mint_logs"))
print(f"RECEIPTS DONE total={len(parsed)} with_mint_logs={n_mint}", flush=True)
for h, v in parsed.items():
    if v.get("mint_logs"):
        print(f"MINT {h} wallet={v['wallet'][:10]} to={v['to']} sel={v['selector']} val={v['value']} time={v['time_wib']} logs={v['mint_logs']}", flush=True)
print(f"RUN39_SENT_SUMMARY wallets_ok={sum(1 for r in results.values() if r.get('ok'))}/{len(uniq)} total={total_inw} max_block={max_block} failed_wallets={failed_wallets}")
