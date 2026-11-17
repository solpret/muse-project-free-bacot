#!/usr/bin/env python3
"""Track-B pending re-check 2026-11-01 ~20:31 WIB: binanceai.fun.
Read-only. REVERT = view absent, not zero. Selectors keccak-computed."""
import json, sys
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _single
from Crypto.Hash import keccak

def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode()); return "0x" + k.hexdigest()[:8]

def enc_addr(a):
    return "0x" + a[2:].lower().rjust(64, "0")

MINT = "0x46cb1D3efd4307506Cda7EbBa5a51be64746739E"
TOKEN = "0x209173F09aFbCA053C0de9e9763f503e9fb54a3c"
PAIR = "0x903ACC22B9BABCD427bfb9AF2C27a27a5aC7c698"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/", "https://bsc-dataseed3.bnbchain.org/"]

def call(to, data):
    for ep in EPS:
        try:
            return _single(ep, "eth_call", [{"to": to, "data": data}, "latest"], 8, retries=0), None
        except Exception as e:
            err = f"{type(e).__name__}: {str(e)[:160]}"
    return None, err

def as_int(v):
    try: return int(v, 16)
    except Exception: return None

calls = {
    "MINT.launched()": (MINT, sel("launched()")),
    "MINT.tokenClaimed(address)": (MINT, sel("tokenClaimed(address)") + enc_addr(USER)[2:]),
    "MINT.totalShares()": (MINT, sel("totalShares()")),
    "MINT.sharesMinted()": (MINT, sel("sharesMinted()")),
    "MINT.isRefundPhase()": (MINT, sel("isRefundPhase()")),
    "MINT.failed()": (MINT, sel("failed()")),
    "MINT.FREE_SHARES()": (MINT, sel("FREE_SHARES()")),
    "TOKEN.balanceOf(MINT)": (TOKEN, sel("balanceOf(address)") + enc_addr(MINT)[2:]),
    "TOKEN.balanceOf(USER)": (TOKEN, sel("balanceOf(address)") + enc_addr(USER)[2:]),
    "PAIR.getReserves()": (PAIR, sel("getReserves()")),
    "PAIR.token0()": (PAIR, sel("token0()")),
    "PAIR.token1()": (PAIR, sel("token1()")),
}
out = {}
for name, (to, data) in calls.items():
    val, err = call(to, data)
    out[name] = {"raw": val, "int": as_int(val) if val else None, "error": err if val is None else None}
block = None
for ep in EPS:
    try:
        block = int(_single(ep, "eth_blockNumber", [], 8, retries=0), 16); break
    except Exception as e:
        block = f"error: {e}"
print(json.dumps({"block": block, "results": out}, indent=1))
