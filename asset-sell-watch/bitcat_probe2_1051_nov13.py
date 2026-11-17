#!/usr/bin/env python3
"""Round 2 probe of BITCAT sale contract for explicit phase/deadline views."""
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
    out = [None] * len(calls)
    for start in range(0, len(calls), 10):
        chunk = calls[start:start + 10]
        batch = [{"jsonrpc": "2.0", "id": i + 1, "method": m, "params": p}
                 for i, (m, p) in enumerate(chunk)]
        res = None
        with ThreadPoolExecutor(max_workers=len(ENDPOINTS)) as ex:
            futs = {ex.submit(post_one, url, batch, timeout): url for url in ENDPOINTS}
            for fut in as_completed(futs):
                try:
                    r = fut.result()
                    if isinstance(r, list) and len(r) == len(chunk):
                        res = r
                        break
                except Exception:
                    continue
            for f in futs:
                f.cancel()
        if res is None:
            continue
        for i, r in enumerate(res):
            out[start + i] = r
    return out

SIGS = ["saleActive()", "saleEnded()", "ended()", "isSaleActive()", "isEnded()",
        "deadline()", "saleDeadline()", "endTimestamp()", "refundsEnabled()",
        "refundable()", "canRefund()", "poolLaunched()", "liquidityAdded()",
        "lpAdded()", "graduated()", "soldOut()", "totalSold()", "mintStart()",
        "startTime()", "start()", "saleStart()", "token()", "agentToken()",
        "isRefundPhase()", "currentPhase()", "salePhase()", "closesAt()",
        "saleClose()", "refundOpen()", "refundsOpen()", "isRefundable()",
        "hasEnded()", "saleOver()", "isClosed()", "closed()", "failed()",
        "isFailed()", "refundPhase()", "getState()", "saleState()",
        "freeShares()", "totalFreeShares()", "maxShares()", "totalShares()",
        "shares()", "paidShares()", "pricePerShare()", "sharePrice()",
        "owner()", "admin()", "treasury()", "pair()", "lpPair()",
        "wbnbPair()", "liquidityPair()", "tokenAddress()"]
calls = [("eth_call", [{"to": SALE, "data": sel(s)}, "latest"]) for s in SIGS]
res = rpc_batch(calls)
out = {"contract": SALE, "probes": {}}
if res:
    for s, r in zip(SIGS, res):
        if isinstance(r, dict) and r.get("result"):
            try:
                v = int(r["result"], 16)
                out["probes"][s] = {"raw": r["result"][:66], "uint": v}
            except Exception:
                out["probes"][s] = {"raw": r["result"][:130]}
        elif isinstance(r, dict) and r.get("error"):
            out["probes"][s] = {"error": "revert"}
        else:
            out["probes"][s] = {"empty": True}
else:
    out["error"] = "all endpoints failed"
print(json.dumps(out, indent=1))
