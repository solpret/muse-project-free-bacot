#!/usr/bin/env python3
"""Oliver age check via historical eth_call (no getLogs needed).
Reads totalSupply at a historical block to bound the first mint.
Read-only. Contract: Oliver Agents 0xad86e4d52e55709d1bda08f922853d4b109e0810
"""
import sys, time, json
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import race

OLIVER = "0xad86e4d52e55709d1bda08f922853d4b109e0810"
TS = "0x18160ddd"  # totalSupply()
FM = "0xd10a1a2b"  # freeMinted()

def blk_ts(b):
    r = race("eth_getBlockByNumber", [hex(b), False], timeout=10)
    return int(r["timestamp"], 16)

def call_at(data, b):
    r = race("eth_call", [{"to": OLIVER, "data": data}, hex(b)], timeout=10)
    return int(r, 16)

t0 = time.time()
tip = race("eth_blockNumber", [], timeout=10)
tip = int(tip, 16)
print("tip", tip, "elapsed", round(time.time()-t0, 1))
ts_tip = blk_ts(tip)
ts_old = blk_ts(tip - 10000)
spb = (ts_tip - ts_old) / 10000.0
print("tip_ts", ts_tip, "ts_tip-10000", ts_old, "sec/block", round(spb, 3))
now = int(time.time())
print("now_utc", now, "tip lag s", now - ts_tip)
blocks_24h = int(86400 / spb)
b24 = tip - blocks_24h
ts_b24 = blk_ts(b24)
print("block24h_ago", b24, "its_ts", ts_b24, "age_h", round((now - ts_b24)/3600, 2))
fm24 = call_at(FM, b24)
ts24 = call_at(TS, b24)
print("freeMinted@block24h", fm24, "totalSupply@block24h", ts24)
print("freeMinted@tip", call_at(FM, tip), "totalSupply@tip", call_at(TS, tip))
if fm24 == 0 and ts24 == 0:
    print("VERDICT: AGE VERIFIED <24h — first mint after block", b24)
else:
    print("VERDICT: AGE FAILS — mints already existed 24h ago (freeMinted was", fm24, ")")
print("total", json.dumps({"tip": tip, "sec_per_block": spb, "block24": b24, "ts_block24": ts_b24, "ts_tip": ts_tip, "freeMinted_block24": fm24, "totalSupply_block24": ts24}))
