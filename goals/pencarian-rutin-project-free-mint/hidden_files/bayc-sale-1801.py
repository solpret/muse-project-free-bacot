#!/usr/bin/env python3
"""Read-only check BAYC sale 0xA178Dd21FD274b25e92c4Ab4A58A8d0B6bdfAE6b (Boltbook guide 2026-11-04). Single-call batches (batch reverts whole batch on one revert)."""
import json, sys, time
from Crypto.Hash import keccak
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import batch
SALE = "0xA178Dd21FD274b25e92c4Ab4A58A8d0B6bdfAE6b"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed1.bnbchain.org/", "https://bsc.publicnode.com/", "https://bsc-dataseed2.bnbchain.org/"]
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
VIEWS = ["freeMinted()", "FREE_SHARES()", "freeSharesRemaining()", "totalShares()", "sharesSold()",
         "soldShares()", "totalMinted()", "started()", "isStarted()", "expired()", "startTime()",
         "endTime()", "saleStart()", "saleEnd()", "freeClaimed(address)", "balanceOf(address)",
         "token()", "freePrice()", "price()"]
out = {"sale": SALE, "block": None, "views": {}, "ts_wib": "2026-11-07 18:01 run leg3-1801"}
try:
    b = batch([("eth_blockNumber", [])], endpoint=EPS[0], timeout=8)
    out["block"] = int(b[0], 16)
except Exception as e:
    out["block_error"] = str(e)
for sig in VIEWS:
    base = sig.split("(")[0]
    data = sel(sig) + (enc(USER) if "(address)" in sig else "")
    key = base + ("_user" if "(address)" in sig else "")
    val = None
    for ep in EPS:
        try:
            r = batch([("eth_call", [{"to": SALE, "data": data}, "latest"])], endpoint=ep, timeout=8)
            v = r[0]
            val = int(v, 16) if isinstance(v, str) and v.startswith("0x") else v
            break
        except Exception:
            continue
    out["views"][key] = val
json.dump(out, open("bayc-sale-1801.json", "w"), indent=1)
print(json.dumps(out, indent=1))
