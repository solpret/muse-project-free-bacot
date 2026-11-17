#!/usr/bin/env python3
"""RWD (REWARD-cfe5) free-pool re-check, run 0331. Read-only.
RWD 0xcfE5E4925A76A3AA11aFA79e04c6fad3611cee40 is excluded-same-owner-discarded
in snapshot `excluded` (NOT in contracts/track_c) — record only, never report/promote/preview/mint.
Hot-leg 0319: freeMinted 125/200, user slot open.
"""
import json, sys, time
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import batch
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
RWD = "0xcfE5E4925A76A3AA11aFA79e04c6fad3611cee40"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed1.bnbchain.org/", "https://bsc.publicnode.com/",
       "https://bsc-dataseed2.bnbchain.org/"]

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def to_int(v):
    try: return int(v, 16)
    except Exception: return None

t0 = time.time()
blk = None
for ep in EPS:
    try:
        b = batch([("eth_blockNumber", [])], endpoint=ep, timeout=8)
        blk = int(b[0], 16); break
    except Exception:
        continue
views = ["totalSupply()", "totalMinted()", "freeClaimed()", "freeMinted()",
         "FREE_SUPPLY()", "MAX_SUPPLY()", "mintOpen()", "balanceOf(address)",
         "freeClaimed(address)"]
calls, keys = [], []
for sig in views:
    base = sig.split("(")[0]
    if "(address)" in sig:
        data = sel(sig) + enc(USER); key = base + "_user"
    else:
        data = sel(sig); key = base
    calls.append(("eth_call", [{"to": RWD, "data": data}, "latest"]))
    keys.append(key)
got = None
for ep in EPS:
    try:
        res = batch(calls, endpoint=ep, timeout=8)
        got = {k: to_int(v) for k, v in zip(keys, res)}
        break
    except Exception:
        continue
out = {"block": blk, "address": RWD, "name": "REWARD (RWD)",
       "snapshot_status": "excluded-same-owner-discarded-2026-11-07",
       "hotleg_0319": {"freeMinted": 125, "freeCap": 200, "userSlotOpen": True},
       "reads": got, "duration_s": round(time.time() - t0, 1)}
print(json.dumps(out, indent=1))
json.dump(out, open(f"{BASE}/run-2026-11-08-0331-rwd-check.json", "w"), indent=1)
