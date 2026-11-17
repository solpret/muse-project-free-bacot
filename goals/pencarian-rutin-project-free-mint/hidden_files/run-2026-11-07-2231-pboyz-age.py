#!/usr/bin/env python3
"""PBOYZ first-mint block via binary search on totalSupply() at historical
blocks. Read-only. Timestamps from dataseed (NOT Ankr - fake timestamps)."""
import json, sys, time
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _single as _fast_single
from Crypto.Hash import keccak
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/", "https://bsc-dataseed3.bnbchain.org/"]
PBOYZ = "0xafb50403c0838d5b45f8748138ba33a70e23b8cf"
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
TS = sel("totalSupply()")
def call_at(block_hex):
    for ep in EPS:
        try:
            v = _fast_single(ep, "eth_call", [{"to": PBOYZ, "data": TS}, block_hex], 8, retries=0)
            if v is None: return None
            return int(v, 16)
        except Exception: continue
    return "ERR"
def block_ts(block_hex):
    for ep in EPS:
        try:
            b = _fast_single(ep, "eth_getBlockByNumber", [block_hex, False], 8, retries=0)
            if isinstance(b, dict) and b.get("timestamp"):
                return int(b["timestamp"], 16)
        except Exception: continue
    return None
head = None
for ep in EPS:
    try:
        v = _fast_single(ep, "eth_blockNumber", [], 8, retries=0)
        if v: head = int(v, 16); break
    except Exception: continue
print("head:", head, flush=True)
lo, hi = 131200000, head
print("totalSupply@lo:", call_at(hex(lo)), "totalSupply@hi:", call_at(hex(hi)), flush=True)
n = 0
while hi - lo > 1 and n < 30:
    mid = (lo + hi) // 2
    v = call_at(hex(mid))
    if v == "ERR" or v is None:
        print("call failed at", mid, flush=True); time.sleep(2); continue
    if v == 0: lo = mid
    else: hi = mid
    n += 1
    print(f"iter {n}: lo={lo} hi={hi} mid={mid} supply={v}", flush=True)
ts = block_ts(hex(hi))
import datetime
print("first-mint block:", hi, "timestamp:", ts,
      datetime.datetime.fromtimestamp(ts, datetime.timezone.utc).isoformat() if ts else None, flush=True)
json.dump({"run": "2231", "contract": PBOYZ, "firstMintBlock": hi,
           "firstMintTs": ts,
           "firstMintUtc": datetime.datetime.fromtimestamp(ts, datetime.timezone.utc).isoformat() if ts else None,
           "head": head, "iterations": n},
          open(f"{BASE}/run-2026-11-07-2231-pboyz-age.json", "w"), indent=1)
print("DONE", flush=True)
