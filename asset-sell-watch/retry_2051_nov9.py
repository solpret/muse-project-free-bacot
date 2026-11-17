#!/usr/bin/env python3
"""Targeted retry for pending-coin-swap-watch 2026-11-09 20:51 run.
Re-reads only the items that failed in the first pass:
 gasPrice, balances+pairs for POA, 币安加油, PACTURE, WW3, and YYDS pair+reserves+quote.
Tries multiple BSC RPC endpoints; never treats a failed read as zero."""
import json, urllib.request, time
from eth_abi import encode, decode
from eth_utils import keccak

W = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
ROUTER = "0x10ED43C718714eb63d5aA57B78B54704E256024E"
FACTORY = "0xca143ce32fe78f1f7019d7d551a6402fc5350c73"
WBNB = "0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c"
RPCS = [
    "https://bsc-dataseed.binance.org/",
    "https://bsc-dataseed1.binance.org/",
    "https://bsc-dataseed2.binance.org/",
    "https://bsc-dataseed1.defibit.io/",
]

def sel(sig):
    return keccak(text=sig).hex()[:8]

def rpc_batch(calls, url):
    batch = [{"jsonrpc": "2.0", "id": i + 1, "method": m, "params": p}
             for i, (m, p) in enumerate(calls)]
    req = urllib.request.Request(url, data=json.dumps(batch).encode(),
                                 headers={"Content-Type": "application/json"})
    res = json.loads(urllib.request.urlopen(req, timeout=30).read())
    out = []
    for r in res:
        if isinstance(r, dict) and (r.get("error") or not r.get("result")):
            out.append(None)
        elif isinstance(r, dict):
            out.append(r["result"])
        else:
            out.append(None)
    return out

def call_any(calls):
    """calls: list of (method, params). Returns list of results, trying RPCs in order."""
    results = [None] * len(calls)
    pending = list(range(len(calls)))
    last_err = None
    for url in RPCS:
        if not pending:
            break
        try:
            got = rpc_batch([calls[i] for i in pending], url)
        except Exception as e:
            last_err = str(e)
            continue
        for j, idx in enumerate(pending):
            if got[j] is not None:
                results[idx] = got[j]
        pending = [i for i in pending if results[i] is None]
    return results, last_err, pending

def u256(h):
    try:
        return int(h, 16) if h else 0
    except Exception:
        return 0

def call(to, data):
    r, _, _ = call_any([("eth_call", [{"to": to, "data": data}, "latest"])])
    return r[0]

def main():
    out = {"run": "pending-coin-swap-watch 2026-11-09 20:51 WIB retry", "entries": {}}
    gp, err, pend = call_any([("eth_gasPrice", [])])
    out["gas_price_wei"] = u256(gp[0]) if gp[0] else None
    out["gas_price_gwei"] = out["gas_price_wei"] / 1e9 if out["gas_price_wei"] else None
    out["gas_est_300k_bnb"] = (out["gas_price_wei"] * 300000 / 1e18) if out["gas_price_wei"] else None
    out["gas_err"] = err if pend else None

    targets = {
        "POA": "0x21bc810818d9c9c767ba73c543f67a989fb5a543",
        "币安加油": "0x397BF425926F521Ac5BEbe5062793BB224e3eF8f",
        "PACTURE": "0x10b80088fDAf9363d83671BE66b64f231f9e92f6",
        "WW3": "0xf62628D99B28535ee593Ab5D6dFE7D914f5edca0",
        "YYDS": "0xd23be069c3c3a7f631af52584a16a9e46bb41da1",
    }
    for sym, tok in targets.items():
        item = {"token": tok}
        bal_h = call(tok, "0x" + sel("balanceOf(address)") + encode(["address"], [W]).hex())
        if bal_h is None:
            item["status"] = "rpc_failed_balance"
            out["entries"][sym] = item
            continue
        bal = u256(bal_h)
        item["balance_raw"] = str(bal)
        item["balance_human"] = bal / 1e18
        if bal == 0:
            item["status"] = "empty"
            out["entries"][sym] = item
            continue
        pair_h = call(FACTORY, "0x" + sel("getPair(address,address)") + encode(["address", "address"], [tok, WBNB]).hex())
        pair = ("0x" + pair_h[-40:]) if pair_h and u256(pair_h) else None
        item["pair_wbnb"] = pair
        if not pair:
            item["status"] = "no_pair"
            out["entries"][sym] = item
            continue
        res_h = call(pair, "0x" + sel("getReserves()"))
        if res_h:
            try:
                r0, r1, _ = decode(["uint112", "uint112", "uint32"], bytes.fromhex(res_h[2:]))
                item["reserves"] = [str(r0), str(r1)]
                if r0 == 0 or r1 == 0:
                    item["status"] = "pair_empty"
                    out["entries"][sym] = item
                    continue
            except Exception as ex:
                item["reserves_error"] = str(ex)
        # quote for the registered sell amount
        amounts = {"POA": 28000000000000000000000, "币安加油": 50000000000000000000000000,
                   "PACTURE": 10000000000000000000000000, "WW3": 10000000000000000000000,
                   "YYDS": 177600000000000}
        q_h = call(ROUTER, "0x" + sel("getAmountsOut(uint256,address[])") + encode(["uint256", "address[]"], [amounts[sym], [tok, WBNB]]).hex())
        if q_h:
            try:
                outs = decode(["uint256[]"], bytes.fromhex(q_h[2:]))[0]
                item["quote_bnb"] = outs[1] / 1e18 if len(outs) == 2 else None
                item["quote_raw"] = str(outs[1]) if len(outs) == 2 else None
            except Exception as ex:
                item["quote_error"] = str(ex)
        if item.get("quote_bnb") is not None:
            q = item["quote_bnb"]
            item["quote_ge_2x_gas"] = (out["gas_est_300k_bnb"] is not None and q >= 2 * out["gas_est_300k_bnb"])
            item["status"] = "executable_candidate" if item["quote_ge_2x_gas"] else "quote_dust"
        else:
            item["status"] = "no_quote"
        out["entries"][sym] = item
    print(json.dumps(out, indent=1))

if __name__ == "__main__":
    main()
