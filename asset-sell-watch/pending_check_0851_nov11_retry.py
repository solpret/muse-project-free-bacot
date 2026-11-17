#!/usr/bin/env python3
"""Retry for pending-swap-watch run 08:51 Nov 11 — re-check only the 11
entries whose balanceOf read failed (Connection refused mid-run, VM restart).
Read-only. Merges results into pending_check_0851_nov11_stdout.json."""
import json, urllib.request
from eth_abi import encode, decode
from eth_utils import keccak

W = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
ROUTER = "0x10ED43C718714eb63d5aA57B78B54704E256024E"
FACTORY = "0xca143ce32fe78f1f7019d7d551a6402fc5350c73"
WBNB = "0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c"
ENDPOINTS = [
    "https://bsc-dataseed1.binance.org/",
    "https://bsc-dataseed.binance.org/",
    "https://bsc.publicnode.com/",
    "https://rpc.ankr.com/bsc",
]

def sel(sig):
    return keccak(text=sig).hex()[:8]

def rpc_call(url, method, params, timeout=25):
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode()
    req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"})
    try:
        res = json.loads(urllib.request.urlopen(req, timeout=timeout).read())
    except Exception as e:
        return None, str(e)
    if isinstance(res, dict) and (res.get("error") or not res.get("result")):
        return None, str(res.get("error"))
    return res.get("result"), None

def call_any(to, data):
    last_err = None
    for url in ENDPOINTS:
        r, err = rpc_call(url, "eth_call", [{"to": to, "data": data}, "latest"])
        if r:
            return r, url, None
        last_err = err
    return None, None, last_err

def u256(h):
    try:
        return int(h, 16) if h else 0
    except Exception:
        return 0

def main():
    path = "/home/hatch/workspace/asset-sell-watch/pending_check_0851_nov11_stdout.json"
    out = json.load(open(path))
    data = json.load(open("/home/hatch/workspace/asset-sell-watch/pending-swaps.json"))
    by_sym = {e["symbol"]: e for e in data["entries"]}
    gas_est = out.get("gas_est_300k_bnb")
    retry_syms = ["POSTAGE", "MALTA", "JINMA", "THYRK", "BITCAT", "LUCKY777",
                  "WNO", "AMBR", "CSAGENT", "CHEEMSA", "NEB"]
    for idx, e in enumerate(out["entries"]):
        if e["symbol"] not in retry_syms:
            continue
        src = by_sym[e["symbol"]]
        tok = src["token"]
        item = {"symbol": e["symbol"], "token": tok,
                "registered_amount_human": src.get("amount_human"),
                "amount_to_sell_raw": src.get("amount_to_sell_raw"),
                "reason_prev": src.get("reason"), "retry": True}
        bal_h, bal_ep, bal_err = call_any(tok, "0x" + sel("balanceOf(address)") + encode(["address"], [W]).hex())
        dec_h, _, _ = call_any(tok, "0x" + sel("decimals()"))
        if bal_h is None:
            item["status"] = "rpc_failed_balance"; item["balance_error"] = bal_err
            out["entries"][idx] = item; continue
        bal = u256(bal_h); dec = u256(dec_h) if dec_h else 18
        item["balance_raw"] = str(bal); item["balance_human"] = bal / (10**dec) if dec < 40 else None
        item["decimals"] = dec; item["balance_endpoint"] = bal_ep
        if bal == 0:
            item["status"] = "empty"; out["entries"][idx] = item; continue
        pair_h, pair_ep, _ = call_any(FACTORY, "0x" + sel("getPair(address,address)") + encode(["address", "address"], [tok, WBNB]).hex())
        pair = ("0x" + pair_h[-40:]) if pair_h and u256(pair_h) else None
        item["pair_wbnb"] = pair; item["pair_endpoint"] = pair_ep
        if not pair:
            item["status"] = "no_pair"; out["entries"][idx] = item; continue
        t0_h, _, _ = call_any(pair, "0x" + sel("token0()"))
        res_h, _, res_err = call_any(pair, "0x" + sel("getReserves()"))
        if res_h:
            try:
                r0, r1, _ = decode(["uint112", "uint112", "uint32"], bytes.fromhex(res_h[2:]))
                item["reserves"] = [str(r0), str(r1)]
                item["token0"] = ("0x" + t0_h[-40:]) if t0_h else None
                if r0 == 0 or r1 == 0:
                    item["status"] = "pair_empty"; out["entries"][idx] = item; continue
            except Exception as ex:
                item["reserves_error"] = str(ex)
        else:
            item["reserves_error"] = res_err
        sell_amt = int(src["amount_to_sell_raw"]) if src.get("amount_to_sell_raw") else bal
        item["sell_amount_raw"] = str(sell_amt)
        q_h, q_ep, q_err = call_any(ROUTER, "0x" + sel("getAmountsOut(uint256,address[])") + encode(["uint256", "address[]"], [sell_amt, [tok, WBNB]]).hex())
        if q_h:
            try:
                outs = decode(["uint256[]"], bytes.fromhex(q_h[2:]))[0]
                item["quote_bnb"] = outs[1] / 1e18 if len(outs) == 2 else None
                item["quote_raw"] = str(outs[1]) if len(outs) == 2 else None
                item["quote_endpoint"] = q_ep
            except Exception as ex:
                item["quote_error"] = str(ex)
        else:
            item["quote_error"] = q_err
        if item.get("quote_bnb") is not None:
            q = item["quote_bnb"]
            item["quote_ge_2x_gas"] = (gas_est is not None and q >= 2 * gas_est)
            item["status"] = "executable_candidate" if item["quote_ge_2x_gas"] else "quote_dust"
        else:
            item["status"] = "no_quote"
        sc = src.get("sale_contract")
        if sc:
            lh, _, _ = call_any(sc, "0x" + sel("launched()"))
            item["sale_contract"] = sc
            item["launched_raw"] = lh
            if lh is not None:
                try:
                    item["launched"] = decode(["bool"], bytes.fromhex(lh[2:]))[0]
                except Exception:
                    item["launched"] = None
        out["entries"][idx] = item
    json.dump(out, open(path, "w"), indent=1)
    print(json.dumps(out, indent=1))

if __name__ == "__main__":
    main()
