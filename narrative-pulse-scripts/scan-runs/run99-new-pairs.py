#!/usr/bin/env python3
"""Run 99 new-pair reads (read-only): token0/token1 for the four new rotation pairs."""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path.home() / "workspace/fast_exec"))
import fast_rpc
from Crypto.Hash import keccak
def sel4(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode()); return "0x" + k.hexdigest()[:8]
def read_addr(addr, sig):
    try:
        r = fast_rpc.race("eth_call", [{"to": addr, "data": sel4(sig)}, "latest"])
    except Exception as e:
        return f"fast_rpc ERROR:{e}"[:120]
    if not isinstance(r, str):
        return f"raw:{r}"
    try:
        return "0x" + r[-40:]
    except Exception:
        return f"raw:{r[:80]}"
PAIRS = {
 "db49 0x41cbb4910fd4959f651d7bff8d8b5ed5cd355dfc": "0x41cbb4910fd4959f651d7bff8d8b5ed5cd355dfc",
 "ff66 0x2d3e053bada0378299010fde9f59209985760bab": "0x2d3e053bada0378299010fde9f59209985760bab",
 "6b12 0x43d85c9fa81bc019701431460d1b3459b057af6d": "0x43d85c9fa81bc019701431460d1b3459b057af6d",
 "50e4 0x26b53042e668d52056e4449abcd238cf01e3a155": "0x26b53042e668d52056e4449abcd238cf01e3a155",
}
out = {}
for label, pair in PAIRS.items():
    t0 = read_addr(pair, "token0()")
    t1 = read_addr(pair, "token1()")
    out[label] = {"token0": t0, "token1": t1}
    print(label, "token0", t0, "token1", t1, flush=True)
json.dump(out, open("/home/hatch/workspace/narrative-pulse/scan-runs/run99-new-pairs.json", "w"), indent=1)
print("saved run99-new-pairs.json")
