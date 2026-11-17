#!/usr/bin/env python3
"""Fresh reads for Ghostling + Voltoad age-exclusion evidence, run 0731.
Read-only. Uses fast_rpc batch on pinned endpoints (race is degraded)."""
import sys, json, time
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import batch
from Crypto.Hash import keccak
EPS = ["https://bsc-dataseed1.bnbchain.org/", "https://bsc.publicnode.com/",
       "https://bsc-dataseed2.bnbchain.org/"]
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def to_int(v):
    try: return int(v, 16)
    except Exception: return None
def views(addr, sigs):
    calls = [("eth_call", [{"to": addr, "data": sel(s)}, "latest"]) for s in sigs]
    for ep in EPS:
        try:
            res = batch(calls, endpoint=ep, timeout=10)
            return {s.split("(")[0]: to_int(v) for s, v in zip(sigs, res)}
        except Exception as e:
            print("  ep fail", ep, e, flush=True)
    return None
SIGS = ["totalSupply()", "freeClaimed()", "freeMinted()", "FREE_SUPPLY()", "MAX_SUPPLY()", "mintOpen()"]
out = {}
for name, addr in [("Ghostling", "0x6a4847cb5f658943222fbd23d2520049f824789d"),
                   ("Voltoad", "0xbc95e0a5bb1305958ba3263c6e9943b7a2554757")]:
    print(name, addr, flush=True)
    d = views(addr, SIGS)
    print(" ", d, flush=True)
    out[name] = {"address": addr, "views": d}
try:
    b = batch([("eth_blockNumber", [])], endpoint=EPS[0], timeout=10)
    out["block"] = int(b[0], 16)
    print("block", out["block"], flush=True)
except Exception as e:
    print("block fail", e, flush=True)
json.dump(out, open("run-2026-11-08-0731-age-verify.json", "w"), indent=1)
