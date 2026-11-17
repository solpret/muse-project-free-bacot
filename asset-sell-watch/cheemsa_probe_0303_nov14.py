#!/usr/bin/env python3
"""Probe tambahan CHEEMSA 2026-11-14 ~03:03 WIB: apakah sale mencapai soft cap /
masuk fase refund? mintDeadline() terverifikasi 1794564000 = 2026-11-13 17:00 WIB
(sudah lewat), tradingOpen()=0, pair 0x0. Coba selector jumlah terjual/cap/refund."""
import json, time, urllib.request
from eth_utils import keccak

def sel(sig):
    return keccak(text=sig).hex()[:8]

ADDR = "0x00b4bdA5BBf83A72f1252CCEf361f107f5a728b2"
SIGS = ["sharesSold()", "totalSold()", "soldShares()", "freeSharesRemaining()",
        "paidSharesSold()", "totalShares()", "mintedShares()", "sharesClaimed()",
        "totalMinted()", "softCapShares()", "capReached()", "refundEnabled()",
        "refundsEnabled()", "isRefunding()", "saleEnded()", "ended()",
        "totalSupply()", "freeSharesTotal()", "paidSharesTotal()", "maxShares()"]
ENDPOINTS = ["https://bsc-dataseed2.binance.org/",
             "https://bsc-dataseed3.binance.org/",
             "https://bsc-dataseed4.binance.org/",
             "https://bsc-dataseed1.binance.org/"]

def post(url, batch, timeout=45):
    req = urllib.request.Request(url, data=json.dumps(batch).encode(),
                                 headers={"Content-Type": "application/json"})
    res = json.loads(urllib.request.urlopen(req, timeout=timeout).read())
    if isinstance(res, dict):
        raise RuntimeError("endpoint error: " + str(res)[:200])
    return res

out = {}
for start in range(0, len(SIGS), 5):
    chunk = SIGS[start:start + 5]
    batch = [{"jsonrpc": "2.0", "id": i + 1, "method": "eth_call",
              "params": [{"to": ADDR, "data": "0x" + sel(s)}, "latest"]}
             for i, s in enumerate(chunk)]
    res = None
    for url in ENDPOINTS:
        try:
            res = post(url, batch)
            break
        except Exception:
            continue
    if res is None:
        for s in chunk:
            out[s] = None
        time.sleep(2)
        continue
    by_id = {}
    for r in res:
        if isinstance(r, dict):
            by_id[r.get("id")] = None if (r.get("error") or not r.get("result")) else r.get("result")
    for i, s in enumerate(chunk):
        h = by_id.get(i + 1)
        out[s] = (int(h, 16) if h else None)
    time.sleep(2)
print(json.dumps(out, indent=1))
