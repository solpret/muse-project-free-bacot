#!/usr/bin/env python3
"""Targeted retry for pending_check_2351_nov10: 4 entries with rpc_failed_balance
(POA, PATCH, YYDS, PACTURE) + 3 entries whose pair read flipped to null vs 22:51 run
(BIJIA? no - BIANJIAYOU token, JINMA, LUCKY777). Read-only. Prints JSON."""
import sys, json, urllib.request
from eth_abi import encode, decode
from eth_utils import keccak

W = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
ROUTER = "0x10ED43C718714eb63d5aA57B78B54704E256024E"
FACTORY = "0xca143ce32fe78f1f7019d7d551a6402fc5350c73"
WBNB = "0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c"
URLS = ["https://bsc-dataseed.binance.org/",
        "https://bsc-dataseed1.defibit.io/",
        "https://bsc-dataseed1.ninicoin.io/"]

def sel(sig):
    return keccak(text=sig).hex()[:8]

def rpc_call(url, method, params):
    payload = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode()
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
    try:
        res = json.loads(urllib.request.urlopen(req, timeout=30).read())
        if res.get("error") or not res.get("result"):
            return None, str(res.get("error"))
        return res["result"], None
    except Exception as e:
        return None, str(e)

def call_multi(to, data):
    for url in URLS:
        r, err = rpc_call(url, "eth_call", [{"to": to, "data": data}, "latest"])
        if r is not None:
            return r, url, None
    return None, None, "all_rpcs_failed"

def u256(h):
    try:
        return int(h, 16) if h else 0
    except Exception:
        return 0

TARGETS = [
    ("POA", "0x21bc810818d9c9c767ba73c543f67a989fb5a543", "28000000000000000000000"),
    ("PATCH", "0xBbA053567846842F95C060867a5C9eb6b3983c80", None),
    ("YYDS", "0xd23be069c3c3a7f631af52584a16a9e46bb41da1", None),
    ("PACTURE", "0x10b80088fDAf9363d83671BE66b64f231f9e92f6", "10000000000000000000000000"),
    ("BIANJIAYOU", "0x397BF425926F521Ac5BEbe5062793BB224e3eF8f", "50000000000000000000000000"),
    ("JINMA", "0xe4517E6718b24D5725956ac7A90686592a7b1539", "50000000000000000000000000"),
    ("LUCKY777", "0xc6D4ec8CB889aFBa9f251606001457644E260f7D", "50000000000000000000000000"),
]

def main():
    gp, url, _ = call_multi("0x0000000000000000000000000000000000000000", "0x")  # placeholder no-op
    # gas price via eth_gasPrice on first working URL
    gas_price = None
    for u in URLS:
        r, err = rpc_call(u, "eth_gasPrice", [])
        if r:
            gas_price = u256(r)
            break
    gas_est = (gas_price * 300000 / 1e18) if gas_price else None
    out = {"gas_price_wei": gas_price, "gas_est_300k_bnb": gas_est, "entries": []}
    for sym, tok, sell_raw in TARGETS:
        item = {"symbol": sym, "token": tok}
        bal_h, burl, berr = call_multi(tok, "0x" + sel("balanceOf(address)") + encode(["address"], [W]).hex())
        if bal_h is None:
            item["status"] = "rpc_failed_balance"; item["rpc_error"] = berr
            out["entries"].append(item); continue
        bal = u256(bal_h)
        dec_h, _, _ = call_multi(tok, "0x" + sel("decimals()"))
        dec = u256(dec_h) if dec_h else 18
        item["balance_raw"] = str(bal); item["balance_human"] = bal / (10**dec); item["decimals"] = dec
        if bal == 0:
            item["status"] = "empty"; out["entries"].append(item); continue
        pair_h, _, _ = call_multi(FACTORY, "0x" + sel("getPair(address,address)") + encode(["address", "address"], [tok, WBNB]).hex())
        pair = ("0x" + pair_h[-40:]) if pair_h and u256(pair_h) else None
        item["pair_wbnb"] = pair
        if not pair:
            item["status"] = "no_pair"; out["entries"].append(item); continue
        res_h, _, _ = call_multi(pair, "0x" + sel("getReserves()"))
        if res_h:
            try:
                r0, r1, _ = decode(["uint112", "uint112", "uint32"], bytes.fromhex(res_h[2:]))
                item["reserves"] = [str(r0), str(r1)]
                if r0 == 0 or r1 == 0:
                    item["status"] = "pair_empty"; out["entries"].append(item); continue
            except Exception as ex:
                item["reserves_error"] = str(ex)
        sell_amt = int(sell_raw) if sell_raw else bal
        item["sell_amount_raw"] = str(sell_amt)
        q_h, _, _ = call_multi(ROUTER, "0x" + sel("getAmountsOut(uint256,address[])") + encode(["uint256", "address[]"], [sell_amt, [tok, WBNB]]).hex())
        if q_h:
            try:
                outs = decode(["uint256[]"], bytes.fromhex(q_h[2:]))[0]
                item["quote_bnb"] = outs[1] / 1e18 if len(outs) == 2 else None
                item["quote_raw"] = str(outs[1]) if len(outs) == 2 else None
            except Exception as ex:
                item["quote_error"] = str(ex)
        if item.get("quote_bnb") is not None:
            q = item["quote_bnb"]
            item["quote_ge_2x_gas"] = (gas_est is not None and q >= 2 * gas_est)
            item["status"] = "executable_candidate" if item["quote_ge_2x_gas"] else "quote_dust"
        else:
            item["status"] = "no_quote"
        out["entries"].append(item)
    print(json.dumps(out, indent=1))

if __name__ == "__main__":
    main()
