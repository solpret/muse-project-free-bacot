#!/usr/bin/env python3
"""Retry for pending-swap entries whose balanceOf failed in the 18:51 run.
Uses alternate public BSC RPC endpoints. Read-only."""
import sys, json, time, urllib.request
from eth_abi import encode, decode
from eth_utils import keccak

W = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
ROUTER = "0x10ED43C718714eb63d5aA57B78B54704E256024E"
FACTORY = "0xca143ce32fe78f1f7019d7d551a6402fc5350c73"
WBNB = "0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c"
ENDPOINTS = [
    "https://bsc-dataseed1.defibit.io/",
    "https://bsc-dataseed.binance.org/",
    "https://rpc.ankr.com/bsc",
    "https://bsc-dataseed1.ninicoin.io/",
]

def sel(sig):
    return keccak(text=sig).hex()[:8]

def rpc_batch(url, calls):
    batch = [{"jsonrpc": "2.0", "id": i + 1, "method": m, "params": p}
             for i, (m, p) in enumerate(calls)]
    req = urllib.request.Request(url, data=json.dumps(batch).encode(),
                                 headers={"Content-Type": "application/json"})
    try:
        res = json.loads(urllib.request.urlopen(req, timeout=30).read())
    except Exception as e:
        return [None] * len(calls), str(e)
    out = []
    for r in res:
        if isinstance(r, dict) and (r.get("error") or not r.get("result")):
            out.append(None)
        elif isinstance(r, dict):
            out.append(r["result"])
        else:
            out.append(None)
    return out, None

def call_multi(to, data):
    for url in ENDPOINTS:
        r, _ = rpc_batch(url, [("eth_call", [{"to": to, "data": data}, "latest"])])
        if r[0]:
            return r[0], url
    return None, None

def u256(h):
    try:
        return int(h, 16) if h else 0
    except Exception:
        return 0

def main():
    data = json.load(open("/home/hatch/workspace/asset-sell-watch/pending-swaps.json"))
    prev = json.load(open("/home/hatch/workspace/asset-sell-watch/pending_check_1851_nov16_stdout.json"))
    failed = [e["symbol"] for e in prev["entries"] if e["status"] == "rpc_failed_balance"]
    # gas price fresh (any endpoint)
    gas_price = None
    for url in ENDPOINTS:
        gp, _ = rpc_batch(url, [("eth_gasPrice", [])])
        if gp and gp[0]:
            gas_price = u256(gp[0]); break
    gas_est = (gas_price * 300000 / 1e18) if gas_price else None
    out = {"gas_price_wei": gas_price, "gas_est_300k_bnb": gas_est,
           "retried_symbols": failed, "entries": []}
    by_sym = {e["symbol"]: e for e in data["entries"]}
    for sym in failed:
        e = by_sym[sym]; tok = e["token"]
        item = {"symbol": sym, "token": tok}
        bal_h, ep = call_multi(tok, "0x" + sel("balanceOf(address)") + encode(["address"], [W]).hex())
        if bal_h is None:
            item["status"] = "rpc_failed_balance_retry"; out["entries"].append(item); continue
        item["rpc_endpoint"] = ep
        dec_h, _ = call_multi(tok, "0x" + sel("decimals()"))
        bal = u256(bal_h); dec = u256(dec_h) if dec_h else 18
        item["balance_raw"] = str(bal); item["balance_human"] = bal / (10**dec)
        if bal == 0:
            item["status"] = "empty"; out["entries"].append(item); continue
        pair_h, _ = call_multi(FACTORY, "0x" + sel("getPair(address,address)") + encode(["address", "address"], [tok, WBNB]).hex())
        pair = ("0x" + pair_h[-40:]) if pair_h and u256(pair_h) else None
        item["pair_wbnb"] = pair
        if not pair:
            item["status"] = "no_pair"; out["entries"].append(item); continue
        res_h, _ = call_multi(pair, "0x" + sel("getReserves()"))
        if res_h:
            r0, r1, _ = decode(["uint112", "uint112", "uint32"], bytes.fromhex(res_h[2:]))
            item["reserves"] = [str(r0), str(r1)]
            if r0 == 0 or r1 == 0:
                item["status"] = "pair_empty"; out["entries"].append(item); continue
        sell_amt = int(e["amount_to_sell_raw"]) if e.get("amount_to_sell_raw") else bal
        item["sell_amount_raw"] = str(sell_amt)
        q_h, _ = call_multi(ROUTER, "0x" + sel("getAmountsOut(uint256,address[])") + encode(["uint256", "address[]"], [sell_amt, [tok, WBNB]]).hex())
        if q_h:
            outs = decode(["uint256[]"], bytes.fromhex(q_h[2:]))[0]
            item["quote_bnb"] = outs[1] / 1e18 if len(outs) == 2 else None
        if item.get("quote_bnb") is not None:
            item["quote_ge_2x_gas"] = (gas_est is not None and item["quote_bnb"] >= 2 * gas_est)
            item["status"] = "executable_candidate" if item["quote_ge_2x_gas"] else "quote_dust"
        else:
            item["status"] = "no_quote"
        out["entries"].append(item)
    print(json.dumps(out, indent=1, ensure_ascii=False))

if __name__ == "__main__":
    main()
