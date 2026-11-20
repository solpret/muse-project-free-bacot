#!/usr/bin/env python3
"""Batch probe sale-state selectors for pending-swap sale contracts (re-check per 06:51 note)."""
import json, subprocess
from eth_utils import keccak

EPS = ["https://bsc-dataseed1.bnbchain.org/", "https://bsc-dataseed.binance.org/"]
entries = json.load(open("/home/hatch/workspace/asset-sell-watch/pending-swaps.json"))["entries"]
sels = {}
for sig in ["launched()", "isOpen()", "phase()", "opened()", "saleEnds()", "saleEnd()", "tradingOpen()", "refundAt()", "saleState()"]:
    sels[sig] = "0x" + keccak(text=sig).hex()[:8]

calls = []
idx = 0
meta = []
for e in entries:
    for sig, sel in sels.items():
        calls.append({"jsonrpc": "2.0", "id": idx, "method": "eth_call",
                      "params": [{"to": e["sale_contract"], "data": sel}, "latest"]})
        meta.append((e["symbol"], e["sale_contract"], sig))
        idx += 1
payload = json.dumps(calls)
out = {}
for ep in EPS:
    try:
        p = subprocess.run(["curl", "-s", "-m", "30", "-H", "Content-Type: application/json",
                            "-d", payload, ep], capture_output=True, text=True, timeout=40)
        res = json.loads(p.stdout)
        if isinstance(res, list) and res:
            out = res; break
    except Exception as ex:
        print("ep fail", ep, ex)
for r, (sym, sc, sig) in zip(out, meta):
    v = r.get("result")
    if v and "error" not in r:
        try:
            iv = int(v, 16)
            print(f"{sym} {sc} {sig} -> {iv} (raw {v[:66]})")
        except Exception:
            print(f"{sym} {sc} {sig} -> {v[:66]}")
print("done", len(out), "responses")
