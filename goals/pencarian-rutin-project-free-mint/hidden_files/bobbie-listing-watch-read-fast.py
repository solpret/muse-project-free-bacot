#!/usr/bin/env python3
"""BOBBIE listing watch — fresh on-chain reads via fast_rpc batch (read-only)."""
import json, sys, time
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import batch_race, call_many
from eth_hash.auto import keccak

NFT = "0x3BF121dC4c5a1Ba567F3eE801d0e447601726207"
MARKET = "0xfA239D919Db60E1b497E9E8CA26CA79689a180AF"
AGENT = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
TOKEN = 4023

def sel(sig):
    return "0x" + keccak(sig.encode()).hex()[:8]

def enc_uint(n):
    return n.to_bytes(32, "big").hex()

calls = [
    (NFT, sel("saleFinalized()")),
    (NFT, sel("cancelled()")),
    (NFT, sel("ownerOf(uint256)") + enc_uint(TOKEN)),
    (MARKET, sel("paused()")),
    (MARKET, sel("listings(uint256)") + enc_uint(TOKEN)),
]
names = ["saleFinalized", "cancelled", "ownerOf4023", "marketPaused", "listings4023"]

t0 = time.time()
res = None
method = None
try:
    res = batch_race(calls, timeout=10)
    method = "batch_race"
except Exception as e:
    print(f"batch_race failed: {e}", flush=True)
try:
    if res is None:
        res = call_many(calls)
        method = "call_many fallback"
except Exception as e:
    print(f"call_many failed: {e}", flush=True)
    raise SystemExit("ALL read paths failed")

out = {"method": method, "elapsed_s": round(time.time() - t0, 1)}
for name, r in zip(names, res):
    out[name] = r
# block number
try:
    from fast_rpc import race
    out["block_number"] = int(race("eth_blockNumber", []), 16)
except Exception as e:
    out["block_number"] = None
    out["block_error"] = str(e)
print(json.dumps(out, indent=2))
