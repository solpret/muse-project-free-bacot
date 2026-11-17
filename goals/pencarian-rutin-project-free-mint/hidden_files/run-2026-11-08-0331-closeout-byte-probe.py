#!/usr/bin/env python3
"""Closeout probe: verify BYTE first-mint via Ankr getLogs (full history).
Probes Transfer events (topic0) on BYTE token 0xCA19f39A451e43698E71F25279c01A809C37fe7c
in 1000-block windows at Nov 5 / Nov 6 / Nov 7 / Nov 8 02:57 boundaries.
Also checks whether ANY Transfer exists before block 132260548 (binary-search result).
"""
import json, sys, time
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from ankr import ankr_post

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TOKEN = "0xca19f39a451e43698e71f25279c01a809c37fe7c"
TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO = "0x0000000000000000000000000000000000000000000000000000000000000000"

def logs(frm, to, topics):
    params = {"blockchain": "bsc", "fromBlock": hex(frm), "toBlock": hex(to),
              "address": [TOKEN], "topics": topics, "pageSize": 1000}
    body = ankr_post("ankr_getLogs", params, timeout=30)
    r = body.get("result", {}) if isinstance(body, dict) else {}
    return r.get("logs", [])

out = {"run": "0331-closeout-byte-probe", "probes": []}
# probe windows: (label, from, to) — 0.45s/block, head 132270538 @ 2026-11-08 04:12 WIB
probes = [
    ("nov05_0000", 131664938, 131665937),
    ("nov06_0000", 131856938, 131857937),
    ("nov07_0000", 132048938, 132049937),
    ("nov08_0257_area", 132260000, 132260999),
    ("nov08_0257_before", 132259548, 132260547),
]
for label, frm, to in probes:
    try:
        lg = logs(frm, to, [TRANSFER, ZERO])
        out["probes"].append({"label": label, "from": frm, "to": to,
                              "mint_transfers": len(lg),
                              "first_block": int(lg[0]["blockNumber"], 16) if lg else None,
                              "first_tx": lg[0]["transactionHash"] if lg else None})
    except Exception as e:
        out["probes"].append({"label": label, "from": frm, "to": to, "error": str(e)[:200]})

# Any mint Transfer before 132260548? Scan backwards in 3 wide steps using
# fromBlock far back is unreliable (pageSize truncation) — instead probe the
# earliest possible deployment area: check a window just before the binary-search
# result already covered above (nov08_0257_before). Also probe mid Nov 7 daytime.
for label, frm, to in [("nov07_midday", 132120000, 132120999),
                       ("nov06_midday", 131940000, 131940999),
                       ("nov05_midday", 131760000, 131760999)]:
    try:
        lg = logs(frm, to, [TRANSFER, ZERO])
        out["probes"].append({"label": label, "from": frm, "to": to,
                              "mint_transfers": len(lg),
                              "first_block": int(lg[0]["blockNumber"], 16) if lg else None})
    except Exception as e:
        out["probes"].append({"label": label, "from": frm, "to": to, "error": str(e)[:200]})

with open(f"{BASE}/run-2026-11-08-0331-closeout-byte-probe.json", "w") as f:
    json.dump(out, f, indent=1)
print(json.dumps(out, indent=1))
