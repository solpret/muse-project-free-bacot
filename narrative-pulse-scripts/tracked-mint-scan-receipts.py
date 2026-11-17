#!/usr/bin/env python3
"""Read-only: receipts for all 'other' (non-PCS, non-approve) in-window txs, batches of 6, ~4s gap.
Classify: mint if any log topic0 Transfer/TransferSingle with from == zero address and to == wallet."""
import json, sys, time
from pathlib import Path
from Crypto.Hash import keccak
sys.path.insert(0, str(Path.home() / "workspace/fast_exec"))
from fast_rpc import batch

def topic(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode()); return "0x" + k.hexdigest()
T_TRANSFER = topic("Transfer(address,address,uint256)")
T_SINGLE = topic("TransferSingle(address,address,address,uint256,uint256)")
T_BATCH = topic("TransferBatch(address,address,address,uint256[],uint256[])")
ZERO_PAD = "0x" + "0" * 64
print("topics", T_TRANSFER, T_SINGLE, T_BATCH, flush=True)

d = json.load(open("/tmp/tracked-scan-decoded.json"))
jobs = []
for w, txs in d.items():
    for t in txs:
        if t["kind"] == "other":
            jobs.append((w, t))
print(f"other txs: {len(jobs)}", flush=True)
out = {}
for i in range(0, len(jobs), 6):
    chunk = jobs[i:i+6]
    try:
        recs = batch([("eth_getTransactionReceipt", [t["hash"]]) for _, t in chunk])
    except Exception as e:
        print(f"batch {i} FAILED: {e}", flush=True)
        for w, t in chunk:
            out[t["hash"]] = {"wallet": w, "error": str(e)[:300]}
        time.sleep(4)
        continue
    for (w, t), r in zip(chunk, recs):
        if r is None:
            out[t["hash"]] = {"wallet": w, "to": t["to"], "selector": t["selector"],
                              "value": t["value"], "time_wib": t["time_wib"], "status": "receipt_null"}
            continue
        logs = r.get("logs") or []
        mint_logs, recv_logs = [], []
        for lg in logs:
            topics = lg.get("topics") or []
            if not topics:
                continue
            if topics[0] in (T_TRANSFER,):
                frm, to = topics[1], topics[2]
                if frm == ZERO_PAD:
                    mint_logs.append({"contract": lg.get("address"), "to": to, "data": lg.get("data")})
                if to and to.lower().endswith(w[2:].lower()):
                    recv_logs.append({"contract": lg.get("address"), "from": frm, "data": lg.get("data")})
            elif topics[0] in (T_SINGLE, T_BATCH):
                # topics: operator, from, to
                if len(topics) >= 4:
                    frm, to = topics[2], topics[3]
                    if frm == ZERO_PAD:
                        mint_logs.append({"contract": lg.get("address"), "to": to, "data": lg.get("data"), "batch": True})
                    if to and to.lower().endswith(w[2:].lower()):
                        recv_logs.append({"contract": lg.get("address"), "from": frm, "data": lg.get("data"), "batch": True})
        out[t["hash"]] = {"wallet": w, "to": t["to"], "selector": t["selector"],
                          "value": t["value"], "time_wib": t["time_wib"],
                          "receipt_status": r.get("status"), "n_logs": len(logs),
                          "mint_logs": mint_logs, "recv_logs": recv_logs}
    print(f"batch {i}-{i+len(chunk)-1} done", flush=True)
    time.sleep(4)
json.dump(out, open("/tmp/tracked-scan-receipts.json", "w"), indent=1)
n_mint = sum(1 for v in out.values() if v.get("mint_logs"))
print(f"saved. total={len(out)} with_mint_logs={n_mint}", flush=True)
