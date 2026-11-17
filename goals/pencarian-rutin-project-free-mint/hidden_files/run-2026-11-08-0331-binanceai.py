#!/usr/bin/env python3
"""Run 0331: Track-B binanceai re-check only (adapted from run 2201 coracle-binanceai.py).
Read-only except own output file run-2026-11-08-0331-binanceai.json.
Binanceai MINT 0x46cb1D3efd4307506Cda7EbBa5a51be64746739E,
TOKEN 0x209173F09aFbCA053C0de9e9763f503e9fb54a3c,
pair 0x903ACC22B9BABCD427bfb9AF2C27a27a5aC7c698.
"""
import json, sys, time, urllib.request, urllib.error
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _single as _fast_single
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/", "https://bsc-dataseed3.bnbchain.org/",
       "https://rpc.ankr.com/bsc"]
DEADLINE = time.time() + 150
t0 = time.time()

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def enc_uint(n): return format(n, "064x")
def raw(to, data):
    if time.time() > DEADLINE:
        return "deadline"
    for ep in EPS:
        if time.time() > DEADLINE:
            return "deadline"
        try:
            v = _fast_single(ep, "eth_call", [{"to": to, "data": data}, "latest"], 8, retries=0)
            if v is None or v == "0x":
                return None
            try:
                return int(v, 16)
            except Exception:
                return v
        except Exception:
            continue
    return None
def call(to, sig, args=""): return raw(to, sel(sig) + args)
def decode_str(v):
    if not isinstance(v, str) or not v.startswith("0x") or len(v) < 138:
        return None
    try:
        b = bytes.fromhex(v[2:])
        off = int.from_bytes(b[32:64], "big")
        ln = int.from_bytes(b[off:off+32], "big")
        return b[off+32:off+32+ln].decode("utf-8", "replace")
    except Exception:
        return None

blk = None
for ep in EPS:
    try:
        v = _fast_single(ep, "eth_blockNumber", [], 8, retries=0)
        if v:
            blk = int(v, 16); break
    except Exception:
        continue
print("head block:", blk, flush=True)

# ---- Track-B binanceai ----
M = "0x46cb1D3efd4307506Cda7EbBa5a51be64746739E"
T = "0x209173F09aFbCA053C0de9e9763f503e9fb54a3c"
P = "0x903ACC22B9BABCD427bfb9AF2C27a27a5aC7c698"
b = {"block": blk, "mint": M, "token": T, "pair": P}
for sig, key in [("launched()", "launched"), ("failed()", "failed"),
                 ("isRefundPhase()", "isRefundPhase"), ("totalShares()", "totalShares"),
                 ("totalSupply()", "totalSupply_mint"),
                 ("claimOpen()", "claimOpen"), ("claimsOpen()", "claimsOpen")]:
    b[key] = call(M, sig)
for sig, key in [("tokenClaimed(address)", "tokenClaimed_user"),
                 ("claimed(address)", "claimed_user"),
                 ("shares(address)", "shares_user")]:
    b[key] = call(M, sig, enc(USER))
b["token_balance_user"] = call(T, "balanceOf(address)", enc(USER))
b["token_totalSupply"] = call(T, "totalSupply()")
b["pair_token0"] = call(P, "token0()")
b["pair_token1"] = call(P, "token1()")
res = call(P, "getReserves()")
b["pair_getReserves_raw"] = res if not isinstance(res, int) else None
# getReserves returns tuple; raw() int-parses only single words, so decode manually
if b["pair_getReserves_raw"] is None:
    try:
        v = None
        for ep in EPS:
            try:
                v = _fast_single(ep, "eth_call", [{"to": P, "data": sel("getReserves()")}, "latest"], 8, retries=0)
                if v and v != "0x":
                    break
            except Exception:
                continue
        if v and len(v) >= 194:
            bb = bytes.fromhex(v[2:])
            b["pair_reserve0"] = int.from_bytes(bb[0:32], "big")
            b["pair_reserve1"] = int.from_bytes(bb[32:64], "big")
    except Exception as e:
        b["pair_reserves_error"] = str(e)
b["duration_s"] = round(time.time() - t0, 1)
json.dump(b, open(f"{BASE}/run-2026-11-08-0331-binanceai.json", "w"), indent=1)
print("Binanceai:", json.dumps(b), flush=True)
