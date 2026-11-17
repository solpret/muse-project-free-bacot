#!/usr/bin/env python3
"""Targeted retry for pending_check_2051: balances that failed + BITCAT pair + LUCKY777 reserves."""
import json, urllib.request
from eth_abi import encode, decode
from eth_utils import keccak

W = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
ROUTER = "0x10ED43C718714eb63d5aA57B78B54704E256024E"
FACTORY = "0xca143ce32fe78f1f7019d7d551a6402fc5350c73"
WBNB = "0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c"
RPCS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.defibit.io/",
        "https://bsc-dataseed1.ninicoin.io/"]

def sel(sig):
    return keccak(text=sig).hex()[:8]

def rpc_call(url, method, params):
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode()
    req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"})
    try:
        res = json.loads(urllib.request.urlopen(req, timeout=20).read())
        if res.get("error") or not res.get("result"):
            return None
        return res["result"]
    except Exception:
        return None

def call(to, data):
    for url in RPCS:
        r = rpc_call(url, "eth_call", [{"to": to, "data": data}, "latest"])
        if r is not None:
            return r
    return None

def u256(h):
    try:
        return int(h, 16) if h else 0
    except Exception:
        return 0

TARGETS = [
    ("POA", "0x21bc810818d9c9c767ba73c543f67a989fb5a543"),
    ("YYDS", "0xd23be069c3c3a7f631af52584a16a9e46bb41da1"),
    ("POSTAGE", "0x6C310EABEdFD4eEd6148bf2C07241FB45a52FB42"),
    ("MALTA", "0x728095Ab0BD71636Db5DA4E2A6d7f5cc73729fc0"),
    ("JINMA", "0xe4517E6718b24D5725956ac7A90686592a7b1539"),
    ("AMBR", "0x88B06f59BdB54039AEBf1d308d8B9181a90385c1"),
    ("CSAGENT", "0xeD290fA2e34233d0ee97eA95C2a34E770A9DA45D"),
]
out = {"retry": []}
for sym, tok in TARGETS:
    bal_h = call(tok, "0x" + sel("balanceOf(address)") + encode(["address"], [W]).hex())
    dec_h = call(tok, "0x" + sel("decimals()"))
    item = {"symbol": sym, "token": tok}
    if bal_h is None:
        item["status"] = "rpc_failed_balance_retry"
    else:
        bal = u256(bal_h); dec = u256(dec_h) if dec_h else 18
        item["balance_raw"] = str(bal); item["decimals"] = dec
        item["balance_human"] = bal / (10**dec) if dec < 40 else None
        item["status"] = "empty" if bal == 0 else "ok"
    out["retry"].append(item)

# BITCAT pair (recorded 0x8dD64bb9F614D58716eB0e343e1F794B2E7A04f4, main run got 0x0)
bitcat = "0x8708EE82fa34c58431532323530592ee3953e9d5"
pair_h = call(FACTORY, "0x" + sel("getPair(address,address)") + encode(["address", "address"], [bitcat, WBNB]).hex())
bit = {"symbol": "BITCAT", "pair_raw": pair_h}
if pair_h and u256(pair_h):
    pair = "0x" + pair_h[-40:]
    bit["pair_wbnb"] = pair
    res_h = call(pair, "0x" + sel("getReserves()"))
    if res_h:
        try:
            r0, r1, _ = decode(["uint112", "uint112", "uint32"], bytes.fromhex(res_h[2:]))
            bit["reserves"] = [str(r0), str(r1)]
        except Exception as ex:
            bit["reserves_error"] = str(ex)
    bit["status"] = "pair_empty" if bit.get("reserves") == ["0", "0"] else "pair_live"
else:
    bit["status"] = "no_pair"
out["retry"].append(bit)

# LUCKY777 reserves
lucky = "0x81afde1cddf0d277580b8e524361e0a7ea2983c6"
res_h = call(lucky, "0x" + sel("getReserves()"))
lk = {"symbol": "LUCKY777", "pair": lucky}
if res_h:
    try:
        r0, r1, _ = decode(["uint112", "uint112", "uint32"], bytes.fromhex(res_h[2:]))
        lk["reserves"] = [str(r0), str(r1)]
        lk["status"] = "pair_empty" if (r0 == 0 or r1 == 0) else "pair_live"
    except Exception as ex:
        lk["reserves_error"] = str(ex); lk["status"] = "reserves_error"
else:
    lk["status"] = "reserves_rpc_failed"
out["retry"].append(lk)
print(json.dumps(out, indent=1))
