#!/usr/bin/env python3
"""Age-exclusion fresh reads, Ghostling + Voltoad — single-call batches only
(fast_rpc.batch reverts whole batch if one view reverts)."""
import sys, json, time
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import batch
from Crypto.Hash import keccak
EPS = ["https://bsc-dataseed1.bnbchain.org/", "https://bsc.publicnode.com/",
       "https://bsc-dataseed2.bnbchain.org/", "https://bsc-dataseed3.bnbchain.org/"]
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def to_int(v):
    try: return int(v, 16)
    except Exception: return None
def single(addr, sig):
    for ep in EPS:
        try:
            res = batch([("eth_call", [{"to": addr, "data": sel(sig)}, "latest"])], endpoint=ep, timeout=10)
            return to_int(res[0])
        except Exception:
            continue
    return None
out = {}
for name, addr in [("Ghostling", "0x6a4847cb5f658943222fbd23d2520049f824789d"),
                   ("Voltoad", "0xbc95e0a5bb1305958ba3263c6e9943b7a2554757")]:
    d = {}
    for sig in ["totalSupply()", "freeClaimed()", "FREE_SUPPLY()", "MAX_SUPPLY()", "mintOpen()"]:
        d[sig.split("(")[0]] = single(addr, sig)
        time.sleep(0.3)
    print(name, d, flush=True)
    out[name] = {"address": addr, "views": d}
try:
    b = batch([("eth_blockNumber", [])], endpoint=EPS[0], timeout=10)
    out["block"] = int(b[0], 16)
except Exception as e:
    out["block"] = None
    print("block fail", e, flush=True)
print("block", out["block"], flush=True)
json.dump(out, open("run-2026-11-08-0731-age-verify.json", "w"), indent=1)
