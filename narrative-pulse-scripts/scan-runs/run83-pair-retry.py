#!/usr/bin/env python3
"""Run 83 follow-up: retry pair token0()/token1() reads for the a6e6 and 887c
PCS pairs, which were UNREADABLE in run 82 (fast_rpc 'all endpoints failed').
Read-only eth_call. No preview/mint/sign/login."""
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
        return f"ERROR:{e}"
    if not isinstance(r, str) or r.startswith("ERROR"):
        return f"unreadable({str(r)[:80]})"
    try:
        return "0x" + r[-40:]
    except Exception:
        return f"raw:{r[:80]}"

PAIRS = {
    "0xa6e6df413cb8e876c6f85bfc788478109c577777": "0x9fac925655fa4985ab4fe2fe9e0ca8ae323cc9da",
    "0x887cf69e1d86ac9bad48f44347c56052128b7777": "0xa9fa6efb21c252b7d4ab81d19a07ee4ecf6d2c97",
}
out = {}
for token, pair in PAIRS.items():
    t0 = read_addr(pair, "token0()")
    t1 = read_addr(pair, "token1()")
    print(token, "pair", pair, "token0", t0, "token1", t1, flush=True)
    out[token] = {"pair": pair, "token0": t0, "token1": t1}
json.dump(out, open(Path.home() / "workspace/narrative-pulse/scan-runs/run83-pair-retry.json", "w"), indent=1)
print("saved run83-pair-retry.json", flush=True)
