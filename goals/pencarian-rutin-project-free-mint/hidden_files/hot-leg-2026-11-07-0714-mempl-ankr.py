#!/usr/bin/env python3
"""MEMPL first-mint via Ankr ankr_getLogs (registered custom.ankr connector).
Transfer-from-zero for the MEMPL token contract, window 132090000..latest."""
import json, sys
from datetime import datetime, timezone, timedelta
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from ankr import ankr_post
MEMPL = "0xd3bE54Ae65F837d0646709fFBc2A5eFB0b034846"
TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO = "0x" + "0"*64
WIB = timezone(timedelta(hours=7))
out = {"run": "2026-11-07-0714-mempl-ankr"}
try:
    body = ankr_post("ankr_getLogs", {
        "blockchain": "bsc", "address": [MEMPL],
        "fromBlock": hex(132090000), "toBlock": "latest",
        "topics": [TRANSFER, ZERO], "pageSize": 1000, "decodeLogs": False})
    logs = body.get("result", {}).get("logs", []) if isinstance(body, dict) else []
    out["n_logs"] = len(logs)
    out["nextPageToken"] = body.get("result", {}).get("nextPageToken") if isinstance(body, dict) else None
    if logs:
        first = min(logs, key=lambda l: int(l.get("blockNumber", "0x0"), 16))
        out["first_block"] = int(first["blockNumber"], 16)
        out["first_tx"] = first.get("transactionHash")
        # block timestamp via dataseed eth_getBlockByNumber
        import urllib.request
        req = urllib.request.Request("https://bsc-dataseed1.bnbchain.org",
            data=json.dumps({"jsonrpc":"2.0","id":1,"method":"eth_getBlockByNumber",
                             "params":[first["blockNumber"], False]}).encode(),
            headers={"Content-Type":"application/json"})
        with urllib.request.urlopen(req, timeout=10) as r:
            b = json.load(r)
        ts = int(b["result"]["timestamp"], 16)
        dt = datetime.fromtimestamp(ts, WIB)
        out["first_time_wib"] = dt.isoformat(timespec="seconds")
        age_h = (datetime.now(WIB) - dt).total_seconds()/3600
        out["age_hours"] = round(age_h, 2)
        out["age_le_48h"] = age_h <= 48
        out["last_block"] = int(max(logs, key=lambda l: int(l.get("blockNumber","0x0"),16))["blockNumber"], 16)
    else:
        out["error"] = f"no logs; raw={str(body)[:300]}"
except Exception as e:
    out["error"] = f"{type(e).__name__}: {e}"
print(json.dumps(out, indent=1))
json.dump(out, open("/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/hot-leg-2026-11-07-0714-mempl-ankr.json","w"), indent=1)
