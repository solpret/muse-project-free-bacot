#!/usr/bin/env python3
"""Probe BITCAT sale contract 0x577874415214780b37EB8966c41563954b76A8B8
for phase/state view functions (TwoTargetSale template candidates).
Read-only eth_call probes, raced across public BSC endpoints."""
import json, urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from eth_utils import keccak

SALE = "0x577874415214780b37EB8966c41563954b76A8B8"
ENDPOINTS = ["https://bsc-dataseed1.binance.org/", "https://bsc-dataseed3.binance.org/",
             "https://bsc.publicnode.com", "https://bsc-rpc.publicnode.com",
             "https://bsc-dataseed.binance.org/", "https://bsc-dataseed2.binance.org/",
             "https://bsc-dataseed4.binance.org/"]

def sel(sig):
    return "0x" + keccak(text=sig).hex()[:8]

def post_one(url, batch, timeout=12):
    req = urllib.request.Request(url, data=json.dumps(batch).encode(),
                                 headers={"Content-Type": "application/json"})
    res = json.loads(urllib.request.urlopen(req, timeout=timeout).read())
    if isinstance(res, dict):
        raise RuntimeError("endpoint error: " + str(res)[:200])
    return res

def rpc_batch(calls, timeout=12):
    batch = [{"jsonrpc": "2.0", "id": i + 1, "method": m, "params": p}
             for i, (m, p) in enumerate(calls)]
    with ThreadPoolExecutor(max_workers=len(ENDPOINTS)) as ex:
        futs = {ex.submit(post_one, url, batch, timeout): url for url in ENDPOINTS}
        for fut in as_completed(futs):
            try:
                res = fut.result()
                return res
            except Exception:
                continue
    return None

SIGS = ["phase()", "opened()", "saleEnd()", "refundAt()", "saleEnds()",
        "launched()", "poolOpened()", "isOpen()", "state()", "status()",
        "getPhase()", "endTime()", "saleEndTime()", "refundEnabled()",
        "totalSharesSold()", "sharesSold()", "paidSharesSold()",
        "freeSharesClaimed()", "softCapReached()"]
calls = [("eth_call", [{"to": SALE, "data": sel(s)}, "latest"]) for s in SIGS]
res = rpc_batch(calls)
out = {"contract": SALE, "probes": {}}
if res:
    for s, r in zip(SIGS, res):
        if isinstance(r, dict) and r.get("result"):
            try:
                v = int(r["result"], 16)
                out["probes"][s] = {"raw": r["result"], "uint": v}
            except Exception:
                out["probes"][s] = {"raw": r["result"]}
        elif isinstance(r, dict) and r.get("error"):
            out["probes"][s] = {"error": str(r["error"])[:120]}
        else:
            out["probes"][s] = {"empty": True}
else:
    out["error"] = "all endpoints failed"
print(json.dumps(out, indent=1))
