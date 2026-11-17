#!/usr/bin/env python3
"""Run 98 read-only metadata retry: symbol() for da79/43bc (timed out in pass 1),
plus second-pass name()/symbol() confirmation for all four new rotations."""
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
ADDRS = {
 "rot-da79": "0xda79bd2e54f46492ac5c44bb7d20da46a2ae7777",
 "rot-2120": "0x21209278656222412f365716863bfb5110637777",
 "rot-43bc": "0x43bcaac4a4aa9711c2846d37fd78879435087777",
 "rot-41cc": "0x41cc11074f16292f311ecac7d6702bb39b157777",
}
out = {}
for label, a in ADDRS.items():
    name = dec_str(call(a, "name()"))
    sym = dec_str(call(a, "symbol()"))
    out[label] = {"address": a, "name": name, "symbol": sym}
    print(label, a, "| name:", name, "| symbol:", sym, flush=True)
json.dump(out, open("/home/hatch/workspace/narrative-pulse/scan-runs/run98-token-meta2.json", "w"), indent=1)
print("saved run98-token-meta2.json")
