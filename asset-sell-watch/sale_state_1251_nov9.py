#!/usr/bin/env python3
"""Read-only sale-contract state check for pending-coin-swap-watch 2026-11-09 12:51 WIB.
Per-call race with try/except so a revert on one selector never kills the rest."""
import sys, json
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import race
from eth_abi import decode
from eth_utils import keccak

def sel(sig): return keccak(text=sig).hex()[:8]
data = json.load(open("/home/hatch/workspace/asset-sell-watch/pending-swaps.json"))
out = {}
for e in data["entries"]:
    sc = e.get("sale_contract")
    if not sc: continue
    item = {}
    for fn, types in [("launched()", ["bool"]), ("phase()", ["uint8"]), ("pair()", ["address"])]:
        try:
            r = race("eth_call", [{"to": sc, "data": "0x" + sel(fn)}, "latest"], timeout=30)
        except Exception as ex:
            r = None; item[fn] = {"error": str(ex)}
        if r is not None:
            try:
                item[fn] = decode(types, bytes.fromhex(r[2:]))[0]
            except Exception:
                item[fn] = {"raw": r}
        elif fn not in item:
            item[fn] = None
    out[e["symbol"]] = item
print(json.dumps(out, indent=1, ensure_ascii=False, default=str))
json.dump(out, open("/home/hatch/workspace/asset-sell-watch/sale_state_1251_nov9.json", "w"), indent=1, ensure_ascii=False, default=str)
