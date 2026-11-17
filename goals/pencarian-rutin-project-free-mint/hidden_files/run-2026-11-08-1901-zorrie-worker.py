#!/usr/bin/env python3
"""Zorrie first-mint parallel worker, run 1901. Read-only.
Usage: run-2026-11-08-1901-zorrie-worker.py LO HI OUTFILE
Scans [LO, HI] in 1000-block chunks via Ankr, collects Zorrie mints."""
import json, sys
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
sys.path.insert(0, "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files")
import onchain_nft_scan as scan

A = "0x47feee72353358a61618cE640265F9f406f88E47"
LO, HI, OUT = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
found = []
frm = HI - 999
while frm >= LO:
    to_b = min(frm + 999, HI)
    try:
        logs, _ = scan.ankr_logs(frm, to_b, [scan.TRANSFER, scan.ZERO_TOPIC])
    except Exception as e:
        print(f"chunk {frm}-{to_b} ERROR {e}", flush=True); break
    mine = [l for l in logs if l.get("address", "").lower() == A.lower()]
    for l in mine:
        found.append({"block": int(l["blockNumber"], 16), "tx": l.get("transactionHash"), "tokenId": int(l["topics"][3], 16) if len(l.get("topics", [])) >= 4 else None})
    print(f"chunk {frm}-{to_b}: {len(mine)} zorrie mints (total {len(found)})", flush=True)
    frm -= 1000
found.sort(key=lambda x: x["block"])
json.dump({"mints": found, "range": [LO, HI]}, open(OUT, "w"), indent=1)
print("DONE", OUT, len(found))
