#!/usr/bin/env python3
"""pending-coin-swap-watch run 2026-11-10 09:51 WIB.
Fresh read-only check for all 13 entries in pending-swaps.json:
 balanceOf agent wallet, factory getPair(token,WBNB), pair reserves,
 router getAmountsOut for the registered sell amount, fresh gasPrice.
Never treats a failed RPC read as zero; tries multiple BSC RPCs."""
import json, urllib.request
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
    out = {"run": "pending-coin-swap-watch 2026-11-10 09:51 WIB",
           "wallet": W, "entries": []}
    gp, err, pend = call_any([("eth_gasPrice", [])])
    gas_wei = u256(gp[0]) if gp[0] else None
    out["gas_price_wei"] = gas_wei
    out["gas_price_gwei"] = gas_wei / 1e9 if gas_wei else None
    out["gas_est_300k_bnb"] = (gas_wei * 300000 / 1e18) if gas_wei else None
    out["gas_2x_threshold_bnb"] = (2 * out["gas_est_300k_bnb"]) if out["gas_est_300k_bnb"] else None
    if pend:
        out["gas_err"] = err

    with open("/home/hatch/workspace/asset-sell-watch/pending-swaps.json") as f:
        data = json.load(f)

    for e in data["entries"]:
        sym = e["symbol"]
        tok = e["token"]
        item = {"symbol": sym}
        bal_h = call(tok, "0x" + sel("balanceOf(address)") + encode(["address"], [W]).hex())
        if bal_h is None:
            item["status"] = "rpc_failed_balance"
            out["entries"].append(item)
            continue
        bal = u256(bal_h)
        item["balance_raw"] = str(bal)
        item["balance_human"] = bal / 1e18
        if bal == 0:
            item["status"] = "empty_balance"
            out["entries"].append(item)
            continue
        pair_h = call(FACTORY, "0x" + sel("getPair(address,address)") + encode(["address", "address"], [tok, WBNB]).hex())
        pair = ("0x" + pair_h[-40:]) if pair_h and u256(pair_h) else None
        item["pair_wbnb"] = pair
        if not pair:
            item["status"] = "no_pair"
            out["entries"].append(item)
            continue
        res_h = call(pair, "0x" + sel("getReserves()"))
        reserves = None
        if res_h:
            try:
                r0, r1, _ = decode(["uint112", "uint112", "uint32"], bytes.fromhex(res_h[2:]))
                reserves = [str(r0), str(r1)]
                item["reserves"] = reserves
                if r0 == 0 or r1 == 0:
                    item["status"] = "pair_empty"
                    out["entries"].append(item)
                    continue
            except Exception as ex:
                item["reserves_error"] = str(ex)
        else:
            item["reserves_error"] = "rpc_failed"
        # quote for registered sell amount (or fresh full balance if null)
        amt = int(e["amount_to_sell_raw"]) if e.get("amount_to_sell_raw") else bal
        item["sell_amount_raw"] = str(amt)
        q_h = call(ROUTER, "0x" + sel("getAmountsOut(uint256,address[])") + encode(["uint256", "address[]"], [amt, [tok, WBNB]]).hex())
        if q_h:
            try:
                outs = decode(["uint256[]"], bytes.fromhex(q_h[2:]))[0]
                if len(outs) == 2:
                    item["quote_bnb"] = outs[1] / 1e18
                    item["quote_raw"] = str(outs[1])
            except Exception as ex:
                item["quote_error"] = str(ex)
        if item.get("quote_bnb") is not None and out["gas_2x_threshold_bnb"] is not None:
            item["quote_ge_2x_gas"] = item["quote_bnb"] >= out["gas_2x_threshold_bnb"]
            item["status"] = "executable_candidate" if item["quote_ge_2x_gas"] else "quote_dust"
        elif item.get("quote_bnb") is None:
            item["status"] = "no_quote"
        out["entries"].append(item)

    print(json.dumps(out, indent=1))

if __name__ == "__main__":
    main()
