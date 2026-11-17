#!/usr/bin/env python3
"""MEMPL: verify block timestamps + first Minted event via Ankr."""
import json, sys, urllib.request
from datetime import datetime, timezone, timedelta
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from ankr import ankr_post
MEMPL = "0xd3bE54Ae65F837d0646709fFBc2A5eFB0b034846"
MINTED = "0xd8b419dcb55349414000518e58bc0ec29a3419a418cc9ab706cd9db1260cb2f4"
WIB = timezone(timedelta(hours=7))
def block_ts(n):
    req = urllib.request.Request("https://bsc-dataseed1.bnbchain.org",
        data=json.dumps({"jsonrpc":"2.0","id":1,"method":"eth_getBlockByNumber",
                         "params":[hex(n), False]}).encode(),
        headers={"Content-Type":"application/json"})
    with urllib.request.urlopen(req, timeout=10) as r:
        b = json.load(r)
    ts = int(b["result"]["timestamp"], 16)
    return ts, datetime.fromtimestamp(ts, WIB).isoformat(timespec="seconds")
out = {"run": "2026-11-07-0714-mempl-verify"}
for n in (132101141, 132102253, 132102859, 132104050):
    try:
        ts, dt = block_ts(n)
        out[f"block_{n}"] = {"ts": ts, "wib": dt}
        print(n, ts, dt)
    except Exception as e:
        out[f"block_{n}"] = {"error": str(e)}
        print(n, "ERR", e)
print("now:", datetime.now(WIB).isoformat(timespec="seconds"))
# Minted events via Ankr (all, window 132090000..latest)
try:
    body = ankr_post("ankr_getLogs", {
        "blockchain": "bsc", "address": [MEMPL],
        "fromBlock": hex(132090000), "toBlock": "latest",
        "topics": [MINTED], "pageSize": 1000, "decodeLogs": False})
    logs = body.get("result", {}).get("logs", []) if isinstance(body, dict) else []
    out["minted_n"] = len(logs)
    out["minted_nextPageToken"] = body.get("result", {}).get("nextPageToken") if isinstance(body, dict) else None
    if logs:
        logs_sorted = sorted(logs, key=lambda l: int(l.get("blockNumber", "0x0"), 16))
        first = logs_sorted[0]
        fb = int(first["blockNumber"], 16)
        ts, dt = block_ts(fb)
        out["minted_first"] = {"block": fb, "tx": first.get("transactionHash"), "ts": ts, "wib": dt,
                               "age_hours": round((datetime.now(WIB) - datetime.fromtimestamp(ts, WIB)).total_seconds()/3600, 2)}
        out["minted_last_block"] = int(logs_sorted[-1]["blockNumber"], 16)
        print("minted first:", out["minted_first"], "last block:", out["minted_last_block"], "n:", len(logs))
    else:
        out["minted_error"] = str(body)[:300]
        print("no minted logs:", str(body)[:300])
except Exception as e:
    out["minted_error"] = f"{type(e).__name__}: {e}"
    print("minted ERR:", e)
json.dump(out, open("/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/hot-leg-2026-11-07-0714-mempl-verify.json","w"), indent=1)
