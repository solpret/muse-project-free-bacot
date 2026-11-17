#!/usr/bin/env python3
"""Quick on-chain read: Lumen Wraiths (Boltbook ranjha.ai lead, run 2026-11-01 20:31).
Read-only. REVERT = view absent, not zero."""
import json, sys
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _single
from Crypto.Hash import keccak

def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode()); return "0x" + k.hexdigest()[:8]

LUMEN = "0xaDC5BB4E4F4D14B8F8f0172D77E6dbDbd8EdC6f2"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/", "https://bsc-dataseed3.bnbchain.org/"]
names = ["totalSupply()", "totalMinted()", "FREE_CAP()", "FREE_PER_WALLET()",
         "freeMinted()", "freeClaimed()", "MAX_SUPPLY()", "PRICE()", "name()", "symbol()"]
out = {}
for name in names:
    val, err = None, None
    for ep in EPS:
        try:
            val = _single(ep, "eth_call", [{"to": LUMEN, "data": sel(name)}, "latest"], 8, retries=0); break
        except Exception as e:
            err = f"{type(e).__name__}: {str(e)[:120]}"
    try: iv = int(val, 16) if val else None
    except Exception: iv = None
    out[name] = {"raw": val, "int": iv, "error": err if val is None else None}
block = None
for ep in EPS:
    try:
        block = int(_single(ep, "eth_blockNumber", [], 8, retries=0), 16); break
    except Exception as e:
        block = f"error: {e}"
print(json.dumps({"block": block, "contract": LUMEN, "results": out}, indent=1))
