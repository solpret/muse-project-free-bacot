#!/usr/bin/env python3
"""Grove retry run 0731 — single-call batches (race degraded)."""
import sys, json, time
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import batch
from Crypto.Hash import keccak
EPS = ["https://bsc-dataseed1.bnbchain.org/", "https://bsc.publicnode.com/",
       "https://bsc-dataseed2.bnbchain.org/", "https://bsc-dataseed3.bnbchain.org/"]
GROVE = "0x8b710e45D38fD55E2D198d2295c0a0D24EBfd64c"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def single(data):
    for ep in EPS:
        try:
            res = batch([("eth_call", [{"to": GROVE, "data": data}, "latest"])], endpoint=ep, timeout=10)
            return int(res[0], 16)
        except Exception:
            continue
    return None
t0 = time.time()
block = None
for ep in EPS:
    try:
        block = int(batch([("eth_blockNumber", [])], endpoint=ep, timeout=10)[0], 16); break
    except Exception: continue
fo = single(sel("freeOpen()"))
fc = single(sel("freeClaimed(address)") + enc(USER))
out = {"block": block, "freeOpen": fo, "freeClaimed_user": (bool(fc) if fc is not None else None), "elapsed_s": round(time.time()-t0, 2), "retry": True}
print(json.dumps(out, indent=1)); json.dump(out, open("run-2026-11-08-0731-grove-check.json", "w"), indent=1)
