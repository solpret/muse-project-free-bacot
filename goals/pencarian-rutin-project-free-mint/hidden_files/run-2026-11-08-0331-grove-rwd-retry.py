#!/usr/bin/env python3
"""Retry Grove + RWD single-call reads, run 0331 (race()/batch() timed out on all endpoints).
Read-only; writes run-2026-11-08-0331-grove-check.json and run-2026-11-08-0331-rwd-check.json.
"""
import json, sys, time
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _single as _fast_single
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/", "https://bsc-dataseed3.bnbchain.org/",
       "https://bsc.publicnode.com/"]
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
GROVE = "0x8b710e45D38fD55E2D198d2295c0a0D24EBfd64c"
RWD = "0xcfE5E4925A76A3AA11aFA79e04c6fad3611cee40"

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def call(to, sig, args=""):
    for ep in EPS:
        try:
            v = _fast_single(ep, "eth_call", [{"to": to, "data": sel(sig) + args}, "latest"], 8, retries=0)
            if v is None or v == "0x":
                return None
            return int(v, 16)
        except Exception:
            continue
    return None

t0 = time.time()
blk = None
for ep in EPS:
    try:
        v = _fast_single(ep, "eth_blockNumber", [], 8, retries=0)
        if v:
            blk = int(v, 16); break
    except Exception:
        continue
print("head block:", blk, flush=True)

g = {"block": blk, "freeOpen": call(GROVE, "freeOpen()"),
     "freeClaimed_user": call(GROVE, "freeClaimed(address)", enc(USER)),
     "elapsed_s": round(time.time() - t0, 2)}
if g["freeClaimed_user"] is not None:
    g["freeClaimed_user"] = bool(g["freeClaimed_user"])
print("GROVE:", json.dumps(g), flush=True)
json.dump(g, open(f"{BASE}/run-2026-11-08-0331-grove-check.json", "w"), indent=1)

t1 = time.time()
views = ["totalSupply()", "totalMinted()", "freeClaimed()", "freeMinted()",
         "FREE_SUPPLY()", "MAX_SUPPLY()", "mintOpen()", "balanceOf(address)",
         "freeClaimed(address)"]
reads = {}
for sig in views:
    base = sig.split("(")[0]
    key = base + "_user" if "(address)" in sig else base
    reads[key] = call(RWD, sig, enc(USER) if "(address)" in sig else "")
r = {"block": blk, "address": RWD, "name": "REWARD (RWD)",
     "snapshot_status": "excluded-same-owner-discarded-2026-11-07",
     "hotleg_0319": {"freeMinted": 125, "freeCap": 200, "userSlotOpen": True},
     "reads": reads, "duration_s": round(time.time() - t1, 1)}
print("RWD:", json.dumps(r), flush=True)
json.dump(r, open(f"{BASE}/run-2026-11-08-0331-rwd-check.json", "w"), indent=1)
