#!/usr/bin/env python3
"""Run 101 read-only metadata: name/symbol/totalSupply/decimals for the two new
machine-token rotations + a sample of the 25 contracts deployed in-window."""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path.home() / "workspace/fast_exec"))
import fast_rpc
from Crypto.Hash import keccak
def sel4(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode()); return "0x" + k.hexdigest()[:8]
def call(addr, sig):
    try:
        r = fast_rpc.race("eth_call", [{"to": addr, "data": sel4(sig)}, "latest"])
    except Exception as e:
        return f"ERROR:{e}"[:120]
    if not isinstance(r, str): return f"raw:{r}"
    return r
def dec_str(h):
    try:
        if not isinstance(h, str) or len(h) < 130: return f"raw:{h}"[:120]
        ln = int(h[66:130], 16)
        b = bytes.fromhex(h[130:130+ln*2])
        return b.decode("utf-8", "replace")
    except Exception as e:
        return f"decode-err:{e}"
def dec_u(h):
    try: return int(h, 16)
    except Exception: return f"raw:{h}"[:80]
ADDRS = {
 "rot-4727": "0x4727e091d34665249bfbdc1575c7180d19527777",
 "rot-1e9c": "0x1e9c6d463a096320df3ad60754344b2735a37777",
}
out = {}
for label, a in ADDRS.items():
    name = dec_str(call(a, "name()"))
    sym = dec_str(call(a, "symbol()"))
    ts = dec_u(call(a, "totalSupply()"))
    dec = dec_u(call(a, "decimals()"))
    out[label] = {"address": a, "name": name, "symbol": sym, "totalSupply": ts, "decimals": dec}
    print(label, a, "| name:", name, "| symbol:", sym, "| totalSupply:", ts, "| decimals:", dec, flush=True)
json.dump(out, open("/home/hatch/workspace/narrative-pulse/scan-runs/run101-token-meta.json", "w"), indent=1)
print("saved run101-token-meta.json")
