#!/usr/bin/env python3
"""Resolve HokiPanda true first mint: earliest Transfer-from-zero to the
contract. Pre-window chunk 132300401-132301400 had 3 mints; fetch them,
take earliest block, timestamp via dataseed (never Ankr)."""
import sys, json, datetime
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from fast_rpc import batch
from ankr import ankr_post
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
ADDR = "0x4b61A7767dA68f18266907b2Eb7C9A1EE3d24517"
TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO_TOPIC = "0x" + "00" * 32
EPS = ["https://bsc-dataseed1.bnbchain.org/", "https://bsc.publicnode.com/",
       "https://bsc-dataseed2.bnbchain.org/", "https://bsc-dataseed3.bnbchain.org/"]
body = ankr_post("ankr_getLogs", {"blockchain": "bsc", "fromBlock": hex(132300401),
    "toBlock": hex(132301400), "pageSize": 1000, "decodeLogs": False,
    "topics": [TRANSFER, ZERO_TOPIC], "address": [ADDR.lower()]}, timeout=30)
logs = body.get("result", {}).get("logs", [])
print(f"pre-window mints 132300401-132301400: {len(logs)}")
rows = []
for lg in logs:
    blk = int(lg["blockNumber"], 16)
    rows.append({"block": blk, "tx": lg.get("transactionHash"),
                 "to": "0x" + lg["topics"][2][-40:], "tokenId": int(lg["topics"][3], 16)})
rows.sort(key=lambda r: r["block"])
for r in rows: print(r)
first = rows[0]["block"]
ts = None
for ep in EPS:
    try:
        res = batch([("eth_getBlockByNumber", [hex(first), False])], endpoint=ep, timeout=10)
        ts = int(res[0]["timestamp"], 16); break
    except Exception: continue
wib = datetime.datetime.fromtimestamp(ts, datetime.timezone(datetime.timedelta(hours=7))).strftime("%Y-%m-%d %H:%M:%S") if ts else None
print(f"TRUE FIRST MINT block={first} ts={ts} WIB={wib}")
json.dump({"first_mint_block": first, "first_mint_timestamp_utc": ts,
           "first_mint_wib": wib, "pre_window_mints": rows},
          open(f"{BASE}/run-2026-11-08-0801-firstmint.json", "w"), indent=1)
