#!/usr/bin/env python3
"""Grove watch run 2026-11-14 04:01 WIB (read-only).
Batch: batch_race dulu, fallback call_many (pola run 02:01/03:01 WIB)."""
import json, sys, time
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import batch_race, call_many, race
from eth_hash.auto import keccak

GROVE = "0x8b710e45D38fD55E2D198d2295c0a0D24EBfd64c"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"

def sel(sig):
    return "0x" + keccak(sig.encode()).hex()[:8]

calls = [
    (GROVE, sel("freeOpen()")),
    (GROVE, sel("freeClaimed(address)") + "000000000000000000000000" + USER[2:].lower()),
]
out = {"attempt": "batch", "t0": time.strftime("%H:%M:%S")}
t_start = time.time()
res = None
try:
    res = batch_race(calls, timeout=10)
    out["path"] = "batch_race"
except Exception as e:
    out["batch_race_error"] = f"{type(e).__name__}: {str(e)[:200]}"
    try:
        res = call_many(calls)
        out["path"] = "call_many"
    except Exception as e2:
        out["call_many_error"] = f"{type(e2).__name__}: {str(e2)[:200]}"
out["elapsed_s"] = round(time.time() - t_start, 1)

def dec_bool(v):
    if not isinstance(v, str) or not v.startswith("0x"):
        return None
    try:
        return bool(int(v[2:66], 16))
    except Exception:
        return None

if res is not None:
    out["freeOpen_raw"] = res[0]
    out["freeOpen"] = dec_bool(res[0])
    out["freeClaimed_raw"] = res[1]
    out["freeClaimed_user"] = dec_bool(res[1])
try:
    blk = race("eth_blockNumber", [], timeout=8)
    out["block"] = int(blk, 16) if isinstance(blk, str) else blk
except Exception as e:
    out["block_error"] = f"{type(e).__name__}: {str(e)[:120]}"
print(json.dumps(out, indent=2))
