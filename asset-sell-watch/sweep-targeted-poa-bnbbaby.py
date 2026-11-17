#!/usr/bin/env python3
"""Targeted re-check: POA + BNBbaby pair + quote (pending_check.py output was
truncated at the head; these two entries need confirmation). Read-only."""
import json, urllib.request
from eth_abi import encode, decode
from eth_utils import keccak

W = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
ROUTER = "0x10ED43C718714eb63d5aA57B78B54704E256024E"
FACTORY = "0xca143ce32fe78f1f7019d7d551a6402fc5350c73"
WBNB = "0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c"
TOKENS = [
    ("POA", "0x21bc810818d9c9c767ba73c543f67a989fb5a543", "28000000000000000000000"),
    ("BNBbaby", "0xd0079025a9bb66a7a1de991de2e4326faba35729", None),
]

def sel(sig):
    return keccak(text=sig).hex()[:8]

def call(to, data):
    payload = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                          "params": [{"to": to, "data": data}, "latest"]}).encode()
    last = None
    for ep in ["https://bsc-dataseed.binance.org", "https://bsc-dataseed1.bnbchain.org",
               "https://bsc-dataseed2.bnbchain.org"]:
        try:
            req = urllib.request.Request(ep, data=payload, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=12) as r:
                res = json.loads(r.read().decode())
            if res.get("result"):
                return res["result"]
            last = res
        except Exception as e:
            last = str(e)
    return None

def u256(h):
    try:
        return int(h, 16) if h else 0
    except Exception:
        return 0

out = {"entries": []}
for sym, tok, sell_raw in TOKENS:
    item = {"symbol": sym, "token": tok}
    bal_h = call(tok, "0x" + sel("balanceOf(address)") + encode(["address"], [W]).hex())
    bal = u256(bal_h) if bal_h else 0
    item["balance_raw"] = str(bal)
    pair_h = call(FACTORY, "0x" + sel("getPair(address,address)") + encode(["address", "address"], [tok, WBNB]).hex())
    pair = ("0x" + pair_h[-40:]) if pair_h and u256(pair_h) else None
    item["pair_wbnb"] = pair
    if not pair:
        item["status"] = "no_pair"
        out["entries"].append(item)
        continue
    res_h = call(pair, "0x" + sel("getReserves()"))
    if res_h:
        r0, r1, _ = decode(["uint112", "uint112", "uint32"], bytes.fromhex(res_h[2:]))
        item["reserves"] = [str(r0), str(r1)]
        if r0 == 0 or r1 == 0:
            item["status"] = "pair_empty"
            out["entries"].append(item)
            continue
    amt = int(sell_raw) if sell_raw else bal
    q_h = call(ROUTER, "0x" + sel("getAmountsOut(uint256,address[])") + encode(["uint256", "address[]"], [amt, [tok, WBNB]]).hex())
    if q_h:
        outs = decode(["uint256[]"], bytes.fromhex(q_h[2:]))[0]
        item["quote_bnb"] = outs[1] / 1e18 if len(outs) == 2 else None
        item["status"] = "executable_candidate" if (item["quote_bnb"] or 0) >= 0.00003 else "quote_dust"
    else:
        item["status"] = "no_quote"
    out["entries"].append(item)
print(json.dumps(out, indent=1))
