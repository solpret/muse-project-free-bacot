#!/usr/bin/env python3
"""Pumpkinfarm 0x77e3... age bracket, hot-leg 2026-11-08 06:19 WIB.
Calibrate BSC block time from dataseed block timestamps (Ankr returns fake
timestamps - never use Ankr for block time), then sample totalSupply() at
historical blocks to bracket first mint. Read-only."""
import sys, json, time
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import batch
from Crypto.Hash import keccak

ADDR = "0x77e38295603a06654a6ed3ed0849e6aa50749963"
EPS = ["https://bsc-dataseed1.bnbchain.org/", "https://bsc.publicnode.com/",
       "https://bsc-dataseed2.bnbchain.org/", "https://bsc-dataseed.binance.org/"]
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]

def block_ts(blk):
    for ep in EPS:
        try:
            r = batch([("eth_getBlockByNumber", [hex(blk), False])], endpoint=ep, timeout=10)
            b = r[0]
            if isinstance(b, dict) and b.get("timestamp"):
                return int(b["timestamp"], 16)
        except Exception:
            continue
    return None

def total_supply_at(blk):
    for ep in EPS:
        try:
            r = batch([("eth_call", [{"to": ADDR, "data": sel("totalSupply()")}, hex(blk)])],
                      endpoint=ep, timeout=10)
            v = r[0]
            if v is None:
                return None
            return int(v, 16)
        except Exception:
            continue
    return None

out = {}
head = int(batch([("eth_blockNumber", [])], endpoint=EPS[0], timeout=8)[0], 16)
out["head"] = head
t_head = block_ts(head)
t_old = block_ts(head - 20000)
out["calibration"] = {"head_ts": t_head, "head_minus_20000_ts": t_old}
if t_head and t_old:
    rate = (t_head - t_old) / 20000.0
    out["calibration"]["sec_per_block"] = round(rate, 4)
    blocks_48h = int(48 * 3600 / rate)
else:
    rate = 3.0
    blocks_48h = 57600
    out["calibration"]["note"] = "timestamp read failed; assuming 3.0 s/block"
out["blocks_48h"] = blocks_48h

# sample totalSupply at age brackets (hours ago, computed from measured rate)
samples = {}
for hours in (48, 24, 12, 6, 3, 1):
    blk = head - int(hours * 3600 / rate)
    samples[f"minus_{hours}h_block_{blk}"] = total_supply_at(blk)
out["totalSupply_samples"] = samples
ts48 = samples.get(f"minus_48h_block_{head - int(48 * 3600 / rate)}")
if ts48 is None:
    out["age_verdict"] = "UNVERIFIED - totalSupply at 48h-ago block unreadable"
elif ts48 > 0:
    out["age_verdict"] = "AGE-EXCLUDED - totalSupply already >0 48h ago (first mint older than 48h)"
else:
    out["age_verdict"] = "AGE-OK - totalSupply was 0 48h ago (first mint within 48h); bracket below"
    # binary-search first block with totalSupply>0 between 48h-ago and head
    lo = head - int(48 * 3600 / rate)
    hi = head
    for _ in range(18):
        mid = (lo + hi) // 2
        v = total_supply_at(mid)
        if v is None:
            break
        if v > 0:
            hi = mid
        else:
            lo = mid
        if hi - lo <= 1:
            break
    out["first_mint_block_bracket"] = {"lo_zero_supply": lo, "hi_positive_supply": hi}
    ts = block_ts(hi)
    out["first_mint_block_ts"] = ts
    if ts:
        from datetime import datetime, timezone, timedelta
        out["first_mint_wib"] = datetime.fromtimestamp(ts, timezone(timedelta(hours=7))).strftime("%Y-%m-%d %H:%M:%S WIB")

json.dump(out, open(f"{BASE}/hot-leg-2026-11-08-0619-pumpkin-age.json", "w"), indent=1)
print(json.dumps(out, indent=1))
