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
 "rot-8b19": "0x8b19cdca84f9e57cbb2946f1c8d27be25ef87777",
 "rot-d826": "0xd826883c65bd3b760ee1b0720c8c31cc2b177777",
 "rot-07b2": "0x07b225cecc3733f71fd613dbf80a275dfd5a7777",
 "rot-4263": "0x42637d6471cd50286a0801060d88e05007197777",
 "refl-d2c1": "0xd2c1cad9a374947b17f49d69fff7f278d7255555",
 "refl-0e22": "0x0e2272d0e5e9ea71ff458c8a2f73bc837c844734",
}
out = {}
for label, a in ADDRS.items():
    name = dec_str(call(a, "name()"))
    sym = dec_str(call(a, "symbol()"))
    ts = dec_u(call(a, "totalSupply()"))
    dec = dec_u(call(a, "decimals()"))
    out[label] = {"address": a, "name": name, "symbol": sym, "totalSupply": ts, "decimals": dec}
    print(label, a, "| name:", name, "| symbol:", sym, "| totalSupply:", ts, "| decimals:", dec, flush=True)
json.dump(out, open("/home/hatch/workspace/narrative-pulse/scan-runs/run102-token-meta.json", "w"), indent=1)
print("saved run102-token-meta.json")
