#!/usr/bin/env python3
"""Targeted retry run 2026-11-13 12:51 WIB: getReserves for the 4 pairs whose
phase-2 batch failed (YYDS, BIJ, JINMA, LUCKY777), then getAmountsOut for any
pair with reserves > 0. Ankr excluded (401 auth since 2026-11-09)."""
import json, time, urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from eth_abi import encode, decode
from eth_utils import keccak

def sel(sig):
    return keccak(text=sig).hex()[:8]

WBNB = "0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c"
ROUTER = "0x10ED43C718714eb63d5aA57B78B54704E256024E"
PAIRS = {
    "YYDS": ("0xD15c928B7b777CaC7d613FE840C6eC3dE8e4EdDA", "0xd23be069c3c3a7f631af52584a16a9e46bb41da1", "177600000000000"),
    "BIJ": ("0xc939e2b49eea548c4539e45b4e355c2b2aa464d6", "0x397BF425926F521Ac5BEbe5062793BB224e3eF8f", "50000000000000000000000000"),
    "JINMA": ("0xaa91fd1b1fc70888f5df17784720b752472e99da", "0xe4517E6718b24D5725956ac7A90686592a7b1539", "50000000000000000000000000"),
    "LUCKY777": ("0x81afde1cddf0d277580b8e524361e0a7ea2983c6", "0xc6D4ec8CB889aFBa9f251606001457644E260f7D", "50000000000000000000000000"),
}
ENDPOINTS = ["https://bsc-dataseed1.binance.org/", "https://bsc-dataseed3.binance.org/",
             "https://bsc.publicnode.com", "https://bsc-rpc.publicnode.com",
             "https://bsc-dataseed.binance.org/", "https://bsc-dataseed2.binance.org/",
             "https://bsc-dataseed4.binance.org/"]

def _post_one(url, batch, timeout=20):
    req = urllib.request.Request(url, data=json.dumps(batch).encode(),
                                 headers={"Content-Type": "application/json"})
    res = json.loads(urllib.request.urlopen(req, timeout=timeout).read())
    if isinstance(res, dict):
        raise RuntimeError("endpoint error: " + str(res)[:200])
    return res

def rpc_batch(calls, timeout=20, attempts=4):
    out = [None] * len(calls)
    last_err = None
    for attempt in range(attempts):
        for start in range(0, len(calls), 10):
            chunk = calls[start:start + 10]
            batch = [{"jsonrpc": "2.0", "id": i + 1, "method": m, "params": p}
                     for i, (m, p) in enumerate(chunk)]
            res = None
            with ThreadPoolExecutor(max_workers=len(ENDPOINTS)) as ex:
                futs = {ex.submit(_post_one, url, batch, timeout): url for url in ENDPOINTS}
                for fut in as_completed(futs):
                    try:
                        res = fut.result()
                        break
                    except Exception as e:
                        last_err = str(e)
                for f in futs:
                    f.cancel()
            if res is None:
                continue
            by_id = {}
            for r in res:
                if isinstance(r, dict):
                    by_id[r.get("id")] = None if (r.get("error") or not r.get("result")) else r.get("result")
            for i in range(len(chunk)):
                if out[start + i] is None:
                    out[start + i] = by_id.get(i + 1)
        if all(v is not None for v in out):
            break
        time.sleep(3)
    return out, last_err

rcalls = [("eth_call", [{"to": p[0], "data": "0x" + sel("getReserves()")}, "latest"]) for p in PAIRS.values()]
rres, rerr = rpc_batch(rcalls)
out = {"run": "pending-coin-swap-watch targeted retry 2026-11-13 12:51 WIB", "phase2_error": rerr, "pairs": {}}
for (sym, (pair, tok, amt)), rh in zip(PAIRS.items(), rres):
    d = {"pair": pair}
    if rh:
        try:
            r0, r1, _ = decode(["uint112", "uint112", "uint32"], bytes.fromhex(rh[2:]))
            d["reserves"] = [str(r0), str(r1)]
            d["status"] = "pair_empty" if (r0 == 0 or r1 == 0) else "reserves_ok"
        except Exception as ex:
            d["reserves_error"] = str(ex)
    else:
        d["status"] = "rpc_failed_reserves"
    out["pairs"][sym] = d
need_q = [(sym, v) for sym, v in out["pairs"].items() if v.get("status") == "reserves_ok"]
if need_q:
    qcalls = [("eth_call", [{"to": ROUTER, "data": "0x" + sel("getAmountsOut(uint256,address[])") + encode(["uint256", "address[]"], [int(PAIRS[s][2]), [PAIRS[s][1], WBNB]]).hex()}, "latest"]) for s, _ in need_q]
    qres, qerr = rpc_batch(qcalls)
    out["phase3_error"] = qerr
    for (sym, _), qh in zip(need_q, qres):
        if qh:
            try:
                outs = decode(["uint256[]"], bytes.fromhex(qh[2:]))[0]
                out["pairs"][sym]["quote_bnb"] = outs[1] / 1e18 if len(outs) == 2 else None
            except Exception as ex:
                out["pairs"][sym]["quote_error"] = str(ex)
print(json.dumps(out, indent=1))
