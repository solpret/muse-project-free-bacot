#!/usr/bin/env python3
"""Run 86 pair retry (4th attempt): token0/token1 for a6e6/887c pairs.
Read-only. No preview/mint/sign/login."""
import json, sys, time
from pathlib import Path
sys.path.insert(0, str(Path.home() / "workspace/fast_exec"))
sys.path.insert(0, str(Path.home() / "workspace/custom-connectors/custom.ankr/bin"))
import fast_rpc
import ankr as ankr_mod

PAIRS = {
 "0xa6e6": "0x9fac925655fa4985ab4fe2fe9e0ca8ae323cc9da",
 "0x887c": "0xa9fa6efb21c252b7d4ab81d19a07ee4ecf6d2c97",
}
out = {"pairs": {}}
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
json.dump(out, open("/home/hatch/workspace/narrative-pulse/scan-runs/run86-pair-retry.json", "w"), indent=1)
print("saved run86-pair-retry.json", flush=True)
