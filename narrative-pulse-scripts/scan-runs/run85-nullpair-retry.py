#!/usr/bin/env python3
"""Run 85 quick retries: 3 null receipts from run 84 + pair token0/token1 for a6e6/887c.
Read-only. No preview/mint/sign/login."""
import json, sys, time
from pathlib import Path
sys.path.insert(0, str(Path.home() / "workspace/fast_exec"))
sys.path.insert(0, str(Path.home() / "workspace/custom-connectors/custom.ankr/bin"))
import fast_rpc
import ankr as ankr_mod

NULL_TXS = [
 "0x3c13e8651ae7eaeffe7f5117d924ea240dcb7528bea6b0a7d8cd80293818f42c",
 "0x98dc3c0d8388e144f1e2ad55068cfb274b4e35d9766acbee6d8151d62541d8a5",
 "0xcef045848f25c492fe62cf7e9e50aeb1c493372e19b65a9c3dcc2907fb28a204",
]
PAIRS = {
 "0xa6e6": "0x9fac925655fa4985ab4fe2fe9e0ca8ae323cc9da",
 "0x887c": "0xa9fa6efb21c252b7d4ab81d19a07ee4ecf6d2c97",
}
out = {"null_receipts": {}, "pairs": {}}
for h in NULL_TXS:
    try:
        r = fast_rpc.race("eth_getTransactionReceipt", [h])
    except Exception as e:
        r = {"error": str(e)[:200]}
    out["null_receipts"][h] = r
    if isinstance(r, dict) and r.get("status"):
        nlogs = len(r.get("logs") or [])
        print(f"{h[:12]} status={r['status']} logs={nlogs} contractAddress={r.get('contractAddress')}", flush=True)
    else:
        print(f"{h[:12]} STILL NULL/ERROR: {str(r)[:150]}", flush=True)
    time.sleep(1)

def sel(sig):
    from Crypto.Hash import keccak
    k = keccak.new(digest_bits=256); k.update(sig.encode()); return "0x" + k.hexdigest()[:8]
T0, T1 = sel("token0()"), sel("token1()")
for label, pair in PAIRS.items():
    res = {}
    for fn, name in ((T0, "token0"), (T1, "token1")):
        v = None
        try:
            v = fast_rpc.race("eth_call", [{"to": pair, "data": fn}, "latest"])
        except Exception as e:
            v = {"fast_rpc_error": str(e)[:150]}
        if not v or (isinstance(v, dict) and v.get("fast_rpc_error")):
            try:
                d = ankr_mod.ankr_post("eth_call", [{"to": pair, "data": fn}, "latest"])
                v = (d.get("result") if isinstance(d, dict) else d)
            except Exception as e:
                v = {"ankr_error": str(e)[:150]}
        res[name] = v
        print(f"{label} pair {pair[:10]} {name} = {str(v)[:120]}", flush=True)
        time.sleep(1)
    out["pairs"][label] = {"pair": pair, **res}
json.dump(out, open("/home/hatch/workspace/narrative-pulse/scan-runs/run85-nullpair-retry.json", "w"), indent=1)
print("saved run85-nullpair-retry.json", flush=True)
