#!/usr/bin/env python3
"""2301 age check: first-mint block via totalSupply binary search + block timestamps.
Read-only."""
import json, sys, time
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _single as _fast_single
from Crypto.Hash import keccak
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/", "https://bsc-dataseed3.bnbchain.org/"]
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def ts_call(ep, method, params):
    for _ in range(2):
        try:
            v = _fast_single(ep, method, params, 10, retries=0)
            if v is not None: return v
        except Exception: continue
    return None
def total_supply_at(addr, block):
    data = sel("totalSupply()")
    for ep in EPS:
        try:
            v = _fast_single(ep, "eth_call", [{"to": addr, "data": data}, hex(block)], 10, retries=0)
            if v not in (None, "0x"): return int(v, 16)
        except Exception: continue
    return None
def block_ts(block):
    for ep in EPS:
        try:
            b = _fast_single(ep, "eth_getBlockByNumber", [hex(block), False], 10, retries=0)
            if b and b.get("timestamp"): return int(b["timestamp"], 16)
        except Exception: continue
    return None
def first_mint_block(addr, lo, hi):
    # invariant: totalSupply(lo)==0 (or unknown->assume), totalSupply(hi)>0
    if total_supply_at(addr, lo) not in (0, None):
        return lo, "lo-not-zero"
    while hi - lo > 1:
        mid = (lo + hi) // 2
        s = total_supply_at(addr, mid)
        if s is None: return None, f"call-failed@{mid}"
        if s > 0: hi = mid
        else: lo = mid
    return hi, "ok"
out = {"run": "2301", "checks": {}}
head = None
for ep in EPS:
    try:
        v = _fast_single(ep, "eth_blockNumber", [], 8, retries=0)
        if v: head = int(v, 16); break
    except Exception: continue
print("head:", head, "head_ts:", block_ts(head), flush=True)
for name, addr, lo in [("HELM", "0xe0df49c281b8584f03ed21beac0e5002ec4a0599", 132170000),
                       ("HOG", "0x7bc0b487febcbb1caa781148bf05a8cd72d02ec5", 132190000)]:
    fb, status = first_mint_block(addr, lo, head)
    ts = block_ts(fb) if fb else None
    row = {"first_mint_block": fb, "status": status, "first_mint_ts": ts,
           "head": head, "head_ts": block_ts(head)}
    if ts and row["head_ts"]:
        row["age_hours"] = (row["head_ts"] - ts) / 3600
    out["checks"][name] = row
    print(name, row, flush=True)
json.dump(out, open(f"{BASE}/run-2026-11-07-2301-age.json", "w"), indent=1)
print("DONE", flush=True)
