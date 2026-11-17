#!/usr/bin/env python3
"""Targeted retry for JINMA/WNO/NEB balance+pair+quote (run 03:51 16 Nov 2026)."""
import json, urllib.request
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

def sel(s):
    return keccak(text=s).hex()[:8]

def batch(calls):
    b = [{"jsonrpc": "2.0", "id": i + 1, "method": m, "params": p}
         for i, (m, p) in enumerate(calls)]
    for url in URLS:
        try:
            req = urllib.request.Request(url, data=json.dumps(b).encode(),
                                         headers={"Content-Type": "application/json"})
            res = json.loads(urllib.request.urlopen(req, timeout=30).read())
            if isinstance(res, list) and any(isinstance(r, dict) and r.get("result") for r in res):
                return [r.get("result") if isinstance(r, dict) else None for r in res]
        except Exception:
            continue
    return [None] * len(calls)

def call(to, data):
    return batch([("eth_call", [{"to": to, "data": data}, "latest"])])[0]

def u(h):
    try:
        return int(h, 16) if h else 0
    except Exception:
        return 0

TOKENS = {
    "JINMA": ("0xe4517E6718b24D5725956ac7A90686592a7b1539", "50000000000000000000000000"),
    "WNO": ("0x8C969a4CD49E4774908e667702C3d7C3ece164D0", "1000000000000000000000000"),
    "NEB": ("0xf08ac9c91dcfc5b74eae6c87e744cfefe0d32a68", "1000000000000000000000"),
}

out = {}
for sym, (tok, sell_raw) in TOKENS.items():
    item = {"symbol": sym, "token": tok}
    bal_h = call(tok, "0x" + sel("balanceOf(address)") + encode(["address"], [W]).hex())
    if bal_h is None:
        item["status"] = "rpc_failed_balance"
        out[sym] = item
        continue
    bal = u(bal_h)
    item["balance_raw"] = str(bal)
    item["balance_human"] = bal / 1e18
    if bal == 0:
        item["status"] = "empty"
        out[sym] = item
        continue
    pair_h = call(FACTORY, "0x" + sel("getPair(address,address)") + encode(["address", "address"], [tok, WBNB]).hex())
    pair = ("0x" + pair_h[-40:]) if pair_h and u(pair_h) else None
    item["pair_wbnb"] = pair
    if not pair:
        item["status"] = "no_pair"
        out[sym] = item
        continue
    res_h = call(pair, "0x" + sel("getReserves()"))
    if res_h:
        r0, r1, _ = decode(["uint112", "uint112", "uint32"], bytes.fromhex(res_h[2:]))
        item["reserves"] = [str(r0), str(r1)]
        if r0 == 0 or r1 == 0:
            item["status"] = "pair_empty"
            out[sym] = item
            continue
    sell_amt = int(sell_raw)
    q_h = call(ROUTER, "0x" + sel("getAmountsOut(uint256,address[])") + encode(["uint256", "address[]"], [sell_amt, [tok, WBNB]]).hex())
    if q_h:
        outs = decode(["uint256[]"], bytes.fromhex(q_h[2:]))[0]
        item["quote_bnb"] = outs[1] / 1e18 if len(outs) == 2 else None
        item["quote_ge_2x_gas"] = item["quote_bnb"] is not None and item["quote_bnb"] >= 2 * 1.5e-05
        item["status"] = "executable_candidate" if item["quote_ge_2x_gas"] else "quote_dust"
    else:
        item["status"] = "no_quote"
    out[sym] = item

print(json.dumps(out, indent=1))
