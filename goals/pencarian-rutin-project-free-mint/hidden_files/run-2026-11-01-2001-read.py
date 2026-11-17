#!/usr/bin/env python3
"""Free-mint-search run 2026-11-01 ~20:01 WIB: HIVE Agents re-read (route 1).
Selectors computed with keccak256 (pycryptodome) from function signatures
named in the 2026-11-01 evening deep sweep. REVERT = view absent, not zero.
Read-only: no preview/mint/signing."""
import json, sys, time
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _single
from Crypto.Hash import keccak

def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode()); return "0x" + k.hexdigest()[:8]

def enc_addr(a):
    return "0x" + a[2:].lower().rjust(64, "0")
def enc_uint(n):
    return "0x" + format(n, "064x")

HIVE = "0x1458b0C132Fb51BDC65B1Ca7a3BE484BCd9A2f77"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/", "https://bsc-dataseed3.bnbchain.org/"]

calls = {
    "totalSupply()": sel("totalSupply()"),
    "START_TIME()": sel("START_TIME()"),
    "FREE_SUPPLY()": sel("FREE_SUPPLY()"),
    "FREE_PER_WALLET()": sel("FREE_PER_WALLET()"),
    "totalPaid()": sel("totalPaid()"),
    "freeMintedBy(address)": sel("freeMintedBy(address)") + enc_addr(USER)[2:],
    "balanceOf(address)": sel("balanceOf(address)") + enc_addr(USER)[2:],
    "quote(uint256)": sel("quote(uint256)") + enc_uint(1)[2:],
    "currentPrice()": sel("currentPrice()"),
    "name()": sel("name()"),
    "symbol()": sel("symbol()"),
}
print("selectors:", {k: v[:10] for k, v in calls.items()})
t0 = time.time()
out = {}
for name, data in calls.items():
    val = None; err = None
    for ep in EPS:
        try:
            r = _single(ep, "eth_call", [{"to": HIVE, "data": data}, "latest"], 8, retries=0)
            val = r; break
        except Exception as e:
            err = f"{type(e).__name__}: {str(e)[:160]}"
    out[name] = {"raw": val, "error": err if val is None else None}
    if val and name not in ("name()", "symbol()"):
        try: out[name]["int"] = int(val, 16)
        except Exception: pass
block = None
for ep in EPS:
    try:
        block = int(_single(ep, "eth_blockNumber", [], 8, retries=0), 16); break
    except Exception as e:
        block = f"error: {e}"
print(json.dumps({"block": block, "read_seconds": round(time.time()-t0, 2), "results": out}, indent=1))
