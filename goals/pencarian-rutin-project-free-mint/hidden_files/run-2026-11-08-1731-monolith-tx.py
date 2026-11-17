#!/usr/bin/env python3
"""Check MONOLITH mint tx values (free vs paid) via Ankr getLogs in-window + tx lookup. Read-only."""
import sys, json
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
sys.path.insert(0, "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files")
from fast_rpc import batch
import onchain_nft_scan as scan

M = "0xcdA4A0EF9C0a626b2450168fd8F90f62C51A569b".lower()
logs = []
for frm in range(132377160, 132377462, 50):
    to = min(frm + 49, 132377461)
    l, _ = scan.ankr_logs(frm, to, [scan.TRANSFER, scan.ZERO_TOPIC])
    logs.extend([x for x in l if x.get("address", "").lower() == M])
print(f"MONOLITH Transfer-from-zero logs in 132377160-132377461: {len(logs)}")
txs = sorted({l["transactionHash"] for l in logs})
print("distinct mint txs:", len(txs))
vals = []
for h in txs:
    try:
        tx = batch([("eth_getTransactionByHash", [h])], endpoint="https://bsc-dataseed.binance.org/", timeout=15)[0]
        v = int(tx["value"], 16) if tx else None
        vals.append({"tx": h, "from": tx["from"] if tx else None, "value_wei": v, "value_bnb": v / 1e18 if v is not None else None, "block": int(tx["blockNumber"], 16) if tx else None})
    except Exception as e:
        vals.append({"tx": h, "error": str(e)[:80]})
for v in vals:
    print(" ", v)
json.dump({"logs": len(logs), "txs": vals}, open("run-2026-11-08-1731-monolith-tx.json", "w"), indent=1)
print("WROTE monolith-tx.json")
