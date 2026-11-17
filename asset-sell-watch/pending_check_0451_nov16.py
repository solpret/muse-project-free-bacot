#!/usr/bin/env python3
"""Read-only pending-swap check run 2026-11-16 04:51 WIB.
Main wallet, PCS V2 only. Multi-endpoint fallback. No audit/preview/execution."""
import sys, json, urllib.request
from eth_abi import encode, decode
from eth_utils import keccak

W = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
ROUTER = "0x10ED43C718714eb63d5aA57B78B54704E256024E"
FACTORY = "0xca143ce32fe78f1f7019d7d551a6402fc5350c73"
WBNB = "0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c"
URLS = ["https://bsc-dataseed-public.bnbchain.org/",
        "https://bsc-dataseed1.binance.org/",
        "https://bsc-dataseed3.binance.org/",
        "https://bsc-dataseed.binance.org/",
        "https://bsc-dataseed1.defibit.io/",
        "https://bsc-dataseed2.ninicoin.io/"]

def sel(sig):
    return keccak(text=sig).hex()[:8]

def rpc_batch(calls):
    batch = [{"jsonrpc": "2.0", "id": i + 1, "method": m, "params": p}
             for i, (m, p) in enumerate(calls)]
    for url in URLS:
        try:
            req = urllib.request.Request(url, data=json.dumps(batch).encode(),
                                         headers={"Content-Type": "application/json"})
            res = json.loads(urllib.request.urlopen(req, timeout=30).read())
        except Exception:
            continue
        if isinstance(res, list) and any(isinstance(r, dict) and r.get("result") for r in res):
            out = []
            for r in res:
                if isinstance(r, dict) and (r.get("error") or not r.get("result")):
                    out.append(None)
                elif isinstance(r, dict):
                    out.append(r["result"])
                else:
                    out.append(None)
            return out, None
    return [None] * len(calls), "all endpoints failed"

def call(to, data):
    r, _ = rpc_batch([("eth_call", [{"to": to, "data": data}, "latest"])])
    return r[0]

def u256(h):
    try:
        return int(h, 16) if h else 0
    except Exception:
        return 0

def main():
    data = json.load(open("/home/hatch/workspace/asset-sell-watch/pending-swaps.json"))
    gp, gp_err = rpc_batch([("eth_gasPrice", [])])
    gas_price = u256(gp[0]) if gp and gp[0] else None
    gas_est_bnb = (gas_price * 300000 / 1e18) if gas_price else None
    out = {"gas_price_wei": gas_price, "gas_price_gwei": (gas_price/1e9 if gas_price else None),
           "gas_est_300k_bnb": gas_est_bnb, "gas_err": gp_err, "entries": []}
    for e in data["entries"]:
        tok = e["token"]; sym = e["symbol"]
        item = {"symbol": sym, "token": tok, "registered_amount_human": e.get("amount_human"),
                "amount_to_sell_raw": e.get("amount_to_sell_raw"), "reason_prev": e.get("reason")}
        bal_h = call(tok, "0x" + sel("balanceOf(address)") + encode(["address"], [W]).hex())
        dec_h = call(tok, "0x" + sel("decimals()"))
        if bal_h is None:
            item["status"] = "rpc_failed_balance"; out["entries"].append(item); continue
        bal = u256(bal_h); dec = u256(dec_h) if dec_h else 18
        item["balance_raw"] = str(bal); item["balance_human"] = bal / (10**dec) if dec < 40 else None
        item["decimals"] = dec
        if bal == 0:
            item["status"] = "empty"; out["entries"].append(item); continue
        pair_h = call(FACTORY, "0x" + sel("getPair(address,address)") + encode(["address", "address"], [tok, WBNB]).hex())
        pair = ("0x" + pair_h[-40:]) if pair_h and u256(pair_h) else None
        item["pair_wbnb"] = pair
        if not pair:
            item["status"] = "no_pair"; out["entries"].append(item); continue
        t0_h = call(pair, "0x" + sel("token0()"))
        t1_h = call(pair, "0x" + sel("token1()"))
        res_h = call(pair, "0x" + sel("getReserves()"))
        if res_h:
            try:
                r0, r1, _ = decode(["uint112", "uint112", "uint32"], bytes.fromhex(res_h[2:]))
                item["reserves"] = [str(r0), str(r1)]
                item["token0"] = ("0x" + t0_h[-40:]) if t0_h else None
                item["token1"] = ("0x" + t1_h[-40:]) if t1_h else None
                if r0 == 0 or r1 == 0:
                    item["status"] = "pair_empty"; out["entries"].append(item); continue
            except Exception as ex:
                item["reserves_error"] = str(ex)
        sell_amt = int(e["amount_to_sell_raw"]) if e.get("amount_to_sell_raw") else bal
        item["sell_amount_raw"] = str(sell_amt)
        q_h = call(ROUTER, "0x" + sel("getAmountsOut(uint256,address[])") + encode(["uint256", "address[]"], [sell_amt, [tok, WBNB]]).hex())
        if q_h:
            try:
                outs = decode(["uint256[]"], bytes.fromhex(q_h[2:]))[0]
                item["quote_bnb"] = outs[1] / 1e18 if len(outs) == 2 else None
                item["quote_raw"] = str(outs[1]) if len(outs) == 2 else None
            except Exception as ex:
                item["quote_error"] = str(ex)
        if item.get("quote_bnb") is not None:
            q = item["quote_bnb"]
            item["quote_ge_2x_gas"] = (gas_est_bnb is not None and q >= 2 * gas_est_bnb)
            item["status"] = "executable_candidate" if item["quote_ge_2x_gas"] else "quote_dust"
        else:
            item["status"] = "no_quote"
        out["entries"].append(item)
    print(json.dumps(out, indent=1))

if __name__ == "__main__":
    main()
