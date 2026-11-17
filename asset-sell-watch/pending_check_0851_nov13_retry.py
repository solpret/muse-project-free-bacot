#!/usr/bin/env python3
"""Retry phase 2/3 for pending-coin-swap-watch run 2026-11-13 08:51 WIB.
Phase 2 (getReserves for 5 known pairs) failed for all 5 in the main run;
retry with fresh raced batches. If a pair has reserves > 0, run getAmountsOut."""
import json, time, urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from eth_abi import encode, decode
from eth_utils import keccak

ROUTER = "0x10ED43C718714eb63d5aA57B78B54704E256024E"
WBNB = "0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c"

def sel(sig):
    return keccak(text=sig).hex()[:8]

ENDPOINTS = ["https://bsc-dataseed1.binance.org/", "https://bsc-dataseed3.binance.org/",
             "https://bsc.publicnode.com", "https://bsc-rpc.publicnode.com",
             "https://bsc-dataseed.binance.org/", "https://bsc-dataseed2.binance.org/",
             "https://bsc-dataseed4.binance.org/"]

def _post_one(url, batch, timeout=15):
    req = urllib.request.Request(url, data=json.dumps(batch).encode(),
                                 headers={"Content-Type": "application/json"})
    res = json.loads(urllib.request.urlopen(req, timeout=timeout).read())
    if isinstance(res, dict):
        raise RuntimeError("endpoint error: " + str(res)[:200])
    return res

def rpc_batch(calls, timeout=15):
    out = [None] * len(calls)
    last_err = None
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
            out[start + i] = by_id.get(i + 1)
    return out, last_err

PAIRS = {
    "YYDS": ("0xD15c928B7b777CaC7d613FE840C6eC3dE8e4EdDA", "0xd23be069c3c3a7f631af52584a16a9e46bb41da1", None),
    "币安加油": ("0xc939e2b49eea548c4539e45b4e355c2b2aa464d6", "0x397BF425926F521Ac5BEbe5062793BB224e3eF8f", "50000000000000000000000000"),
    "JINMA": ("0xaa91fd1b1fc70888f5df17784720b752472e99da", "0xe4517E6718b24D5725956ac7A90686592a7b1539", "50000000000000000000000000"),
    "BITCAT": ("0x8dD64bb9F614D58716eB0e343e1F794B2E7A04f4", "0x8708EE82fa34c58431532323530592ee3953e9d5", "37777777600000000000"),
    "LUCKY777": ("0x81afde1cddf0d277580b8e524361e0a7ea2983c6", "0xc6D4ec8CB889aFBa9f251606001457644E260f7D", "50000000000000000000000000"),
}

def main():
    out = {"run": "pending-coin-swap-watch 2026-11-13 08:51 WIB RETRY phase2/3"}
    res = None; err = None
    for attempt in range(3):
        rcalls = [("eth_call", [{"to": p, "data": "0x" + sel("getReserves()")}, "latest"]) for p, _, _ in PAIRS.values()]
        res, err = rpc_batch(rcalls)
        if any(r is not None for r in res):
            break
        time.sleep(3)
    out["phase2_error"] = err
    quotes = {}
    for (sym, (pair, tok, amt)), rh in zip(PAIRS.items(), res):
        item = {"pair": pair}
        if rh:
            try:
                r0, r1, _ = decode(["uint112", "uint112", "uint32"], bytes.fromhex(rh[2:]))
                item["reserves"] = [str(r0), str(r1)]
                item["status"] = "pair_empty" if (r0 == 0 or r1 == 0) else "reserves_ok"
            except Exception as ex:
                item["reserves_error"] = str(ex)
        else:
            item["status"] = "rpc_failed_reserves"
        out[sym] = item
    need_q = [sym for sym, it in out.items() if isinstance(it, dict) and it.get("status") == "reserves_ok"]
    if need_q:
        qcalls = []
        for sym in need_q:
            pair, tok, amt = PAIRS[sym]
            a = int(amt) if amt else 177600000000000
            qcalls.append(("eth_call", [{"to": ROUTER, "data": "0x" + sel("getAmountsOut(uint256,address[])") + encode(["uint256", "address[]"], [a, [tok, WBNB]]).hex()}, "latest"]))
        qres, qerr = rpc_batch(qcalls)
        out["phase3_error"] = qerr
        for sym, qh in zip(need_q, qres):
            if qh:
                try:
                    outs = decode(["uint256[]"], bytes.fromhex(qh[2:]))[0]
                    out[sym]["quote_bnb"] = outs[1] / 1e18 if len(outs) == 2 else None
                except Exception as ex:
                    out[sym]["quote_error"] = str(ex)
            q = out[sym].get("quote_bnb")
            if q is not None:
                out[sym]["quote_ge_2x_gas"] = q >= 0.00003
                out[sym]["status"] = "executable_candidate" if q >= 0.00003 else "quote_dust"
            else:
                out[sym]["status"] = "no_quote"
    print(json.dumps(out, indent=1))

if __name__ == "__main__":
    main()
