#!/usr/bin/env python3
"""Free-mint-search run 2026-11-01 ~18:31 WIB: totalSupply reads via Binance dataseeds only."""
import json, sys, time
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _single
SNAP = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/onchain-snapshot.json"
snap = json.load(open(SNAP))
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/", "https://bsc-dataseed2.bnbchain.org/", "https://bsc-dataseed3.bnbchain.org/"]
SEL = "0x18160ddd"
t0 = time.time()
out = {}
for name, c in snap["contracts"].items():
    val = None; err = None
    for ep in EPS:
        try:
            r = _single(ep, "eth_call", [{"to": c["address"], "data": SEL}, "latest"], 8, retries=0)
            val = int(r, 16) if isinstance(r, str) and r.startswith("0x") else None
            break
        except Exception as e:
            err = f"{ep}: {type(e).__name__}: {str(e)[:120]}"
    out[name] = {"address": c["address"], "totalSupply": val, "previousTotalSupply": c.get("totalSupply"), "error": err if val is None else None}
block = None
for ep in EPS:
    try:
        block = _single(ep, "eth_blockNumber", [], 8, retries=0)
        break
    except Exception as e:
        block = f"error: {e}"
print(json.dumps({"prev_timestamp_wib": snap["timestamp_wib"], "block": block, "read_seconds": round(time.time()-t0, 2), "results": out}, indent=1))
