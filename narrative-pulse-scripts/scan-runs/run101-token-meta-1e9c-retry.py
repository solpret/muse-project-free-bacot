#!/usr/bin/env python3
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path.home() / "workspace/fast_exec"))
import fast_rpc
from Crypto.Hash import keccak
def sel4(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode()); return "0x" + k.hexdigest()[:8]
def call(addr, sig):
    try:
        return fast_rpc.race("eth_call", [{"to": addr, "data": sel4(sig)}, "latest"])
    except Exception as e:
        return f"ERROR:{e}"[:150]
def dec_str(h):
    try:
        if not isinstance(h, str) or len(h) < 130: return f"raw:{h}"[:120]
        ln = int(h[66:130], 16)
        return bytes.fromhex(h[130:130+ln*2]).decode("utf-8", "replace")
    except Exception as e:
        return f"decode-err:{e}"
def dec_u(h):
    try: return int(h, 16)
    except Exception: return f"raw:{h}"[:80]
A = "0x1e9c6d463a096320df3ad60754344b2735a37777"
out = {"address": A, "name": dec_str(call(A, "name()")), "symbol": dec_str(call(A, "symbol()")),
       "totalSupply": dec_u(call(A, "totalSupply()")), "decimals": dec_u(call(A, "decimals()"))}
print(out)
meta = json.load(open("/home/hatch/workspace/narrative-pulse/scan-runs/run101-token-meta.json"))
meta["rot-1e9c"] = out
json.dump(meta, open("/home/hatch/workspace/narrative-pulse/scan-runs/run101-token-meta.json", "w"), indent=1)
print("updated run101-token-meta.json")
