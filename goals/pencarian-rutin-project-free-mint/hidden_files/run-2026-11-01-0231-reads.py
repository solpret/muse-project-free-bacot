#!/usr/bin/env python3
import json, sys, time
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import call_many, race
snap_path = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/onchain-snapshot.json"
snap = json.load(open(snap_path))
contracts = snap["contracts"]
names = [k for k in contracts if k != "Agent Periodic Lab"]
calls = [(contracts[n]["address"], "0x18160ddd") for n in names]
results = {}
try:
    vals = call_many(calls)
    for n, v in zip(names, vals):
        try:
            results[n] = int(v, 16) if isinstance(v, str) else v
        except Exception as e:
            results[n] = f"ERROR decode {v!r}: {e}"
except Exception as e:
    print("call_many failed:", e)
    for n, (to, data) in zip(names, calls):
        try:
            v = race("eth_call", [{"to": to, "data": data}, "latest"])
            results[n] = int(v, 16)
        except Exception as e2:
            results[n] = f"ERROR {type(e2).__name__}: {e2}"
try:
    blk = race("eth_blockNumber", [])
    block = int(blk, 16)
except Exception as e:
    block = f"ERROR {e}"
print(json.dumps({"block": block, "results": results}, indent=1))
