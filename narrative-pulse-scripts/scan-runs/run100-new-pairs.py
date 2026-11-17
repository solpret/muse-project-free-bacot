#!/usr/bin/env python3
"""Run 100 new-pair reads (read-only): token0/token1 for the four new rotation pairs."""
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
 "6f31 0xc9299379d122a1a84d45fdf1ee87dd0ce1a5e3e8": "0xc9299379d122a1a84d45fdf1ee87dd0ce1a5e3e8",
 "0d7e 0x98fe67c6aeb645e6c9aa41c1fd79898261e7fde7": "0x98fe67c6aeb645e6c9aa41c1fd79898261e7fde7",
}
out = {}
for label, pair in PAIRS.items():
    t0 = read_addr(pair, "token0()")
    t1 = read_addr(pair, "token1()")
    out[label] = {"token0": t0, "token1": t1}
    print(label, "token0", t0, "token1", t1, flush=True)
json.dump(out, open("/home/hatch/workspace/narrative-pulse/scan-runs/run100-new-pairs.json", "w"), indent=1)
print("saved run100-new-pairs.json")
