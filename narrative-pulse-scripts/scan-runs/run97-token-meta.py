#!/usr/bin/env python3
"""Run 97 read-only metadata: name/symbol/totalSupply/decimals for the two new
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
 "rot-c90a": "0xc90a6cf8d74cf3540eaca3ce63ea7ae4e1ec7777",
 "rot-e3a8": "0xe3a8e1ca392b316c42d780c3cf15202f80f37777",
 "dep-0eb7": "0x0eb71fdecf71ceafb1bfadd83ec9ce2589fb76a9",
 "dep-2be8": "0x2be815d0f51cc0691ea5d716563f22154bfd5c4a",
 "dep-7543": "0x7543e5ced4865b548c882bd20253ab4cfa17f735",
 "dep-eb94": "0xeb94304ddca442ab0d9de1476d88d649f446c046",
 "dep-505f": "0x505f926bc27351f4b7ea0d8f0c5a1f833d9da007",
 "dep-97bd-1": "0x900027cf859124d1e3b88e375ef48d0c5e291e96",
}
out = {}
for label, a in ADDRS.items():
    name = dec_str(call(a, "name()"))
    sym = dec_str(call(a, "symbol()"))
    ts = dec_u(call(a, "totalSupply()"))
    dec = dec_u(call(a, "decimals()"))
    out[label] = {"address": a, "name": name, "symbol": sym, "totalSupply": ts, "decimals": dec}
    print(label, a, "| name:", name, "| symbol:", sym, "| totalSupply:", ts, "| decimals:", dec, flush=True)
json.dump(out, open("/home/hatch/workspace/narrative-pulse/scan-runs/run97-token-meta.json", "w"), indent=1)
print("saved run97-token-meta.json")
