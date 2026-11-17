#!/usr/bin/env python3
"""pending-coin-swap-watch run 2026-11-11 ~22:51 WIB. Read-only.
Reads ~/workspace/asset-sell-watch/pending-swaps.json fresh, checks every entry:
balanceOf agent wallet, factory getPair(token,WBNB), reserves, getAmountsOut,
gas price, and sale-contract state (launched()/opened()/tradingOpen() best-effort).
Falls back across RPC endpoints per call; never treats an RPC failure as zero."""
import json, urllib.request
from eth_abi import encode, decode
from eth_utils import keccak

W = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
ROUTER = "0x10ED43C718714eb63d5aA57B78B54704E256024E"
FACTORY = "0xca143ce32fe78f1f7019d7d551a6402fc5350c73"
WBNB = "0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c"
ENDPOINTS = [
    "https://bsc-dataseed1.bnbchain.org/",
    "https://bsc-dataseed.binance.org/",
    "https://bsc.publicnode.com/",
]

def sel(sig):
    return keccak(text=sig).hex()[:8]

def rpc_call(url, method, params, timeout=15):
    req = urllib.request.Request(url, data=json.dumps(
        {"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode(),
        headers={"Content-Type": "application/json"})
    try:
        res = json.loads(urllib.request.urlopen(req, timeout=timeout).read())
    except Exception as e:
        return None, str(e)
    if isinstance(res, dict) and res.get("error"):
        return None, str(res["error"])
    if isinstance(res, dict) and res.get("result") is not None:
        return res["result"], None
    return None, "empty result"

def eth_call(to, data):
    last_err = None
    for url in ENDPOINTS:
        r, err = rpc_call(url, "eth_call", [{"to": to, "data": data}, "latest"])
        if r is not None:
            return r, None
        last_err = err
    return None, last_err

def u256(h):
    try:
        return int(h, 16) if h else 0
    except Exception:
        return 0

def main():
    with open("/home/hatch/workspace/asset-sell-watch/pending-swaps.json") as f:
        data = json.load(f)
    gp = None
    gp_err = None
    for url in ENDPOINTS:
        r, err = rpc_call(url, "eth_gasPrice", [])
        if r is not None:
            gp = u256(r); break
        gp_err = err
    gas_est = (gp * 300000 / 1e18) if gp else None
    out = {"gas_price_gwei": (gp / 1e9 if gp else None),
           "gas_est_300k_bnb": gas_est, "gas_err": gp_err, "entries": []}
    for e in data["entries"]:
        sym = e["symbol"]; tok = e["token"]
        item = {"symbol": sym, "token": tok, "reason_prev": e.get("reason"),
                "amount_to_sell_raw": e.get("amount_to_sell_raw")}
        bal_h, bal_err = eth_call(tok, "0x" + sel("balanceOf(address)") + encode(["address"], [W]).hex())
        if bal_h is None:
            item["status"] = "rpc_failed_balance"; item["error"] = bal_err
            out["entries"].append(item); continue
        dec_h, _ = eth_call(tok, "0x" + sel("decimals()"))
        bal = u256(bal_h); dec = u256(dec_h) if dec_h else 18
        item["balance_raw"] = str(bal); item["balance_human"] = bal / (10 ** dec) if dec < 40 else None
        item["decimals"] = dec
        if bal == 0:
            item["status"] = "empty"; out["entries"].append(item); continue
        pair_h, pair_err = eth_call(FACTORY, "0x" + sel("getPair(address,address)") + encode(["address", "address"], [tok, WBNB]).hex())
        pair = ("0x" + pair_h[-40:]) if pair_h and u256(pair_h) else None
        item["pair_wbnb"] = pair
        if pair_err and not pair:
            item["pair_error"] = pair_err
        if not pair:
            item["status"] = "no_pair"; out["entries"].append(item); continue
        res_h, res_err = eth_call(pair, "0x" + sel("getReserves()"))
        if res_h:
            try:
                r0, r1, _ = decode(["uint112", "uint112", "uint32"], bytes.fromhex(res_h[2:]))
                item["reserves"] = [str(r0), str(r1)]
                t0_h, _ = eth_call(pair, "0x" + sel("token0()"))
                item["token0"] = ("0x" + t0_h[-40:]) if t0_h else None
                if r0 == 0 or r1 == 0:
                    item["status"] = "pair_empty"; out["entries"].append(item); continue
            except Exception as ex:
                item["reserves_error"] = str(ex)
                out["entries"].append(item); continue
        else:
            item["status"] = "rpc_failed_reserves"; item["error"] = res_err
            out["entries"].append(item); continue
        sell_amt = int(e["amount_to_sell_raw"]) if e.get("amount_to_sell_raw") else bal
        item["sell_amount_raw"] = str(sell_amt)
        q_h, q_err = eth_call(ROUTER, "0x" + sel("getAmountsOut(uint256,address[])") + encode(["uint256", "address[]"], [sell_amt, [tok, WBNB]]).hex())
        if q_h:
            try:
                outs = decode(["uint256[]"], bytes.fromhex(q_h[2:]))[0]
                item["quote_bnb"] = outs[1] / 1e18 if len(outs) == 2 else None
                item["quote_raw"] = str(outs[1]) if len(outs) == 2 else None
            except Exception as ex:
                item["quote_error"] = str(ex)
        else:
            item["quote_error"] = q_err
        if item.get("quote_bnb") is not None:
            item["quote_ge_2x_gas"] = (gas_est is not None and item["quote_bnb"] >= 2 * gas_est)
            item["status"] = "executable_candidate" if item["quote_ge_2x_gas"] else "quote_dust"
        else:
            item["status"] = "no_quote"
        # sale-contract state, best effort
        sc = e.get("sale_contract")
        if sc and sc.lower() != tok.lower():
            st = {}
            for fn in ("launched()", "opened()", "tradingOpen()"):
                h, _ = eth_call(sc, "0x" + sel(fn))
                if h:
                    try:
                        st[fn] = decode(["bool"], bytes.fromhex(h[2:]))[0]
                    except Exception:
                        try:
                            st[fn] = u256(h)
                        except Exception:
                            st[fn] = h
            if st:
                item["sale_state"] = st
        out["entries"].append(item)
    print(json.dumps(out, indent=1))

if __name__ == "__main__":
    main()
