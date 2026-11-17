#!/usr/bin/env python3
"""Batch read-only sale-contract state check (launched/pair) for pending swaps."""
import json, urllib.request
from eth_utils import keccak

def sel(sig):
    return keccak(text=sig).hex()[:8]

contracts = {
    "POA": "0x74d9b5477e7fa818298f927966452f2eb9c5fa5e",
    "BNBbaby": "0xbb7ed59ca41ea03cf20084a8c9de94244b7b2637",
    "PATCH": "0xCaFa8f3563E1ACd57abe24C42663BD1D103651C3",
    "QAGENT": "0xE3a4f3099a2136e0e66202A665815caB8FFA2704",
    "YYDS": "0x62AB0519dED1B70481021D31fa6BAcB7450b78F3",
}
calls = []
labels = []
for sym, sc in contracts.items():
    for fn in ["launched()", "pair()"]:
        calls.append({"jsonrpc": "2.0", "id": len(calls) + 1, "method": "eth_call",
                      "params": [{"to": sc, "data": "0x" + sel(fn)}, "latest"]})
        labels.append((sym, fn, sc))
batch = json.dumps(calls).encode()
req = urllib.request.Request("https://bsc-dataseed.binance.org/", data=batch,
                             headers={"Content-Type": "application/json"})
try:
    res = json.loads(urllib.request.urlopen(req, timeout=60).read())
except Exception as e:
    print(json.dumps({"error": str(e)})); raise SystemExit(0)
by_id = {r["id"]: r for r in res if isinstance(r, dict)}
for (sym, fn, sc), c in zip(labels, calls):
    r = by_id.get(c["id"], {})
    print(f"{sym} {fn} sale={sc} result={r.get('result')} error={r.get('error')}")
