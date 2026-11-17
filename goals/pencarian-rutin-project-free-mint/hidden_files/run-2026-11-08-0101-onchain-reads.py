#!/usr/bin/env python3
"""Read-only on-chain verification, run 0101 discovery leg.
LEAN batch (totalSupply) first, then per-view batches, single-call fallback.
Writes ONLY run-2026-11-08-0101-onchain-reads.json (own file)."""
import sys, json
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from eth_hash.auto import keccak
from fast_rpc import call_many, race

def sel(sig):
    return "0x" + keccak(sig.encode()).hex()[:8]

CONTRACTS = {
 "Agent Goats": "0x0e9e0a3b46dc0d36a1ab64f553dd8a0693e6aaa6",
 "BRAINROT ZOO": "0x3c7d328027ca0068e7cd8709d64d9161bc35de93",
 "Driftnauts": "0x6a926234d3767f2eeb3db12c1b4c9e2912c5589b",
 "REWARD": "0xcfe5e4925a76a3aa11afa79e04c6fad3611cee40",
 "Gacha Gang": "0x7182f4230cbd53294366a344d13ddd041c4e734c",
 "Ticker Pets": "0x31975837d5c68eea0b66b5fd27de3506c2f109ba",
 "Odyssey": "0xdfd073ad4b1ce3778b5b44f61dec8e07640777df",
}
VIEWS = ["totalSupply()", "freeClaimed()", "freeLeft()", "FREE_SUPPLY()", "MAX_SUPPLY()", "mintOpen()"]

def decode(hexres):
    if not hexres or hexres == "0x":
        return None
    try:
        return int(hexres, 16)
    except Exception:
        return f"raw:{hexres[:80]}"

out = {"block": None, "reads": {}}
try:
    out["block"] = race("eth_blockNumber", [])
except Exception as e:
    out["block_error"] = str(e)
print("head block:", out["block"], flush=True)

# LEAN batch: totalSupply for all
calls = [(addr, sel("totalSupply()")) for addr in CONTRACTS.values()]
try:
    res = call_many(calls)
    for (name, addr), r in zip(CONTRACTS.items(), res):
        out["reads"].setdefault(name, {})["totalSupply"] = decode(r)
    print("LEAN totalSupply OK", flush=True)
except Exception as e:
    print("LEAN batch failed:", e, flush=True)
    out["lean_error"] = str(e)

# Per-view batches for remaining views; single-call fallback on failure
for view in VIEWS[1:]:
    calls = [(addr, sel(view)) for addr in CONTRACTS.values()]
    try:
        res = call_many(calls)
        for (name, addr), r in zip(CONTRACTS.items(), res):
            out["reads"].setdefault(name, {})[view] = decode(r)
        print(f"view {view} batch OK", flush=True)
    except Exception as e:
        print(f"view {view} batch FAILED ({e}) -> singles", flush=True)
        for name, addr in CONTRACTS.items():
            try:
                r = race("eth_call", [{"to": addr, "data": sel(view)}, "latest"])
                out["reads"].setdefault(name, {})[view] = decode(r)
            except Exception as e2:
                out["reads"].setdefault(name, {})[view] = f"ERR:{e2}"[:80]
        print(f"view {view} singles done", flush=True)

json.dump(out, open("run-2026-11-08-0101-onchain-reads.json", "w"), indent=1)
for name, vals in out["reads"].items():
    print(name, vals, flush=True)
print("DONE", flush=True)
