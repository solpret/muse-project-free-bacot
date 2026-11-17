#!/usr/bin/env python3
"""Grove watch retry run 2026-11-14 05:01 WIB (read-only).
Sequential read failed all endpoints (TimeoutError). Retry with batch_race
+ call_many (pattern of run 04:31 WIB, which succeeded via publicnode)."""
import json, sys
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import batch_race, call_many
from eth_hash.auto import keccak

GROVE = "0x8b710e45D38fD55E2D198d2295c0a0D24EBfd64c"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"

def sel(sig):
    return "0x" + keccak(sig.encode()).hex()[:8]

calls = [
    {"to": GROVE, "data": sel("freeOpen()")},
    {"to": GROVE, "data": sel("freeClaimed(address)") + "000000000000000000000000" + USER[2:].lower()},
]
try:
    res = batch_race(calls, timeout=10)
    mode = "batch_race"
except Exception as e:
    res = call_many(calls)
    mode = "call_many-fallback"

def dec_bool(out):
    if not isinstance(out, str) or not out.startswith("0x"):
        return None
    try:
        return bool(int(out[2:66], 16))
    except Exception:
        return None

out = {"mode": mode, "raw": res,
       "freeOpen": dec_bool(res[0]) if isinstance(res, list) and len(res) > 0 else None,
       "freeClaimed_user": dec_bool(res[1]) if isinstance(res, list) and len(res) > 1 else None}
print(json.dumps(out, indent=2))
