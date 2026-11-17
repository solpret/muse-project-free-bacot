#!/usr/bin/env python3
"""Retry for pending-swap check 00:51 Nov 11 — only items whose first pass failed
on RPC (balance / getPair / reserves / quote). Tries 3 BSC RPC endpoints in turn.
Read-only."""
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
]

def sel(sig):
    return keccak(text=sig).hex()[:8]

def rpc_call(url, method, params, timeout=20):
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
    """eth_call trying endpoints in order; returns (result, endpoint_used, err)."""
    for url in ENDPOINTS:
        r, err = rpc_call(url, "eth_call", [{"to": to, "data": data}, "latest"])
        if r:
            return r, url, None
    return None, None, err

def u256(h):
    try:
        return int(h, 16) if h else 0
    except Exception:
        return 0

# items needing retry: (symbol, token, amount_to_sell_raw or None, need)
ITEMS = [
    ("POA", "0x21bc810818d9c9c767ba73c543f67a989fb5a543", "28000000000000000000000", ["balance", "pair", "reserves", "quote"]),
    ("PACTURE", "0x10b80088fDAf9363d83671BE66b64f231f9e92f6", "10000000000000000000000000", ["balance", "pair", "reserves", "quote"]),
    ("ORBITA", "0x19b8d7613A6C2E4168a6a0Bb97ca0c842035d709", "1000000000000000000000000", ["balance", "pair", "reserves", "quote"]),
    ("POSTAGE", "0x6C310EABEdFD4eEd6148bf2C07241FB45a52FB42", "10000000000000000000000", ["balance", "pair", "reserves", "quote"]),
    ("THYRK", "0x3b8747D067B2Ed8565330667128260C2a4954300", "20000000000000000000", ["balance", "pair", "reserves", "quote"]),
    ("WNO", "0x8C969a4CD49E4774908e667702C3d7C3ece164D0", "1000000000000000000000000", ["balance", "pair", "reserves", "quote"]),
    ("YYDS", "0xd23be069c3c3a7f631af52584a16a9e46bb41da1", "177600000000000", ["quote", "token0"]),
    ("BIAJIYOU", "0x397BF425926F521Ac5BEbe5062793BB224e3eF8f", "50000000000000000000000000", ["pair", "reserves", "quote"]),
    ("LUCKY777", "0xc6D4ec8CB889aFBa9f251606001457644E260f7D", "50000000000000000000000000", ["pair", "reserves", "quote"]),
    ("CSAGENT", "0xeD290fA2e34233d0ee97eA95C2a34E770A9DA45D", "100000000000000000000000", ["reserves", "quote"]),
]

out = {"entries": []}
for sym, tok, amt_raw, needs in ITEMS:
    item = {"symbol": sym, "token": tok}
    if "balance" in needs:
        bal_h, ep, err = call_any(tok, "0x" + sel("balanceOf(address)") + encode(["address"], [W]).hex())
        if bal_h is None:
            item["balance"] = None; item["balance_error"] = err
        else:
            bal = u256(bal_h)
            item["balance_raw"] = str(bal); item["balance_human"] = bal / 1e18
            item["balance_endpoint"] = ep
    if "pair" in needs or "reserves" in needs or "quote" in needs:
        pair_h, ep, err = call_any(FACTORY, "0x" + sel("getPair(address,address)") + encode(["address", "address"], [tok, WBNB]).hex())
        pair = ("0x" + pair_h[-40:]) if pair_h and u256(pair_h) else None
        item["pair_wbnb"] = pair; item["pair_endpoint"] = ep
        if pair:
            if "reserves" in needs:
                res_h, ep2, err2 = call_any(pair, "0x" + sel("getReserves()"))
                if res_h:
                    try:
                        r0, r1, _ = decode(["uint112", "uint112", "uint32"], bytes.fromhex(res_h[2:]))
                        item["reserves"] = [str(r0), str(r1)]
                    except Exception as ex:
                        item["reserves_error"] = str(ex)
                else:
                    item["reserves_error"] = err2
            if "token0" in needs:
                t0_h, ep3, _ = call_any(pair, "0x" + sel("token0()"))
                item["token0"] = ("0x" + t0_h[-40:]) if t0_h else None
            if "quote" in needs:
                sell = int(amt_raw) if amt_raw else (int(item["balance_raw"]) if item.get("balance_raw") else 0)
                if sell:
                    q_h, ep4, err4 = call_any(ROUTER, "0x" + sel("getAmountsOut(uint256,address[])") + encode(["uint256", "address[]"], [sell, [tok, WBNB]]).hex())
                    if q_h:
                        try:
                            outs = decode(["uint256[]"], bytes.fromhex(q_h[2:]))[0]
                            item["quote_bnb"] = outs[1] / 1e18 if len(outs) == 2 else None
                            item["quote_raw"] = str(outs[1]) if len(outs) == 2 else None
                        except Exception as ex:
                            item["quote_error"] = str(ex)
                    else:
                        item["quote_error"] = err4
    out["entries"].append(item)

print(json.dumps(out, indent=1))
