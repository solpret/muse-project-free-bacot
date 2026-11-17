#!/usr/bin/env python3
"""Free-mint-search run 2026-11-01 ~11:01 WIB: raced single totalSupply reads, per-contract errors isolated."""
import json, sys, time
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import race

SNAP = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/onchain-snapshot.json"
with open(SNAP) as f:
    snap = json.load(f)
prev_ts = snap["timestamp_wib"]
contracts = snap["contracts"]
SEL = "0x18160ddd"
t0 = time.time()
out = {}
for name, c in contracts.items():
    try:
        r = race("eth_call", [{"to": c["address"], "data": SEL}, "latest"])
        val = int(r, 16) if isinstance(r, str) and r.startswith("0x") else None
        out[name] = {"address": c["address"], "totalSupply": val,
                     "previousTotalSupply": c.get("totalSupply")}
        if val is None:
            out[name]["error"] = f"non-hex result {r}"
    except Exception as e:
        out[name] = {"address": c["address"], "totalSupply": None,
                     "previousTotalSupply": c.get("totalSupply"), "error": str(e)[:200]}
try:
    block = race("eth_blockNumber", [])
except Exception as e:
    block = f"error: {e}"
print(json.dumps({"prev_timestamp_wib": prev_ts, "block": block,
                  "read_seconds": round(time.time() - t0, 2), "results": out}, indent=1))
