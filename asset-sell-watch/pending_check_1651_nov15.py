#!/usr/bin/env python3
"""pending-coin-swap-watch run 2026-11-15 16:51 WIB. Read-only; prints JSON.
For each entry: balanceOf wallet, factory getPair(token,WBNB), getReserves,
router getAmountsOut(amount_to_sell or full balance). Plus fresh gasPrice."""
import json, urllib.request
from eth_abi import encode, decode
from eth_utils import keccak

W = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
ROUTER = "0x10ED43C718714eb63d5aA57B78B54704E256024E"
FACTORY = "0xca143ce32fe78f1f7019d7d551a6402fc5350c73"
WBNB = "0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c"
ENDPOINTS = ["https://bsc-dataseed1.binance.org/", "https://bsc-dataseed3.binance.org/",
             "https://bsc.publicnode.com", "https://bsc-dataseed2.binance.org/",
             "https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.defibit.io/"]

def sel(sig):
    return keccak(text=sig).hex()[:8]

def rpc(url, method, params):
    payload = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode()
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
    res = json.loads(urllib.request.urlopen(req, timeout=20).read())
    if res.get("error") or res.get("result") is None:
        return None
    return res["result"]

def call(to, data):
    for url in ENDPOINTS:
        try:
            r = rpc(url, "eth_call", [{"to": to, "data": data}, "latest"])
            if r is not None:
                return r, url
        except Exception:
            continue
    return None, None

def u256(h):
    try:
        return int(h, 16) if h else 0
    except Exception:
        return 0

ENTRIES = [
    ("POA", "0x21bc810818d9c9c767ba73c543f67a989fb5a543", "28000000000000000000000"),
    ("BNBbaby", "0xd0079025a9bb66a7a1de991de2e4326faba35729", None),
    ("PATCH", "0xBbA053567846842F95C060867a5C9eb6b3983c80", None),
    ("QAGENT", "0x25e915EEE91411b0AC3273531dbaDc34e0EAA5eB", None),
    ("YYDS", "0xd23be069c3c3a7f631af52584a16a9e46bb41da1", None),
    ("BIAJIAYOU", "0x397BF425926F521Ac5BEbe5062793BB224e3eF8f", "50000000000000000000000000"),
    ("PACTURE", "0x10b80088fDAf9363d83671BE66b64f231f9e92f6", "10000000000000000000000000"),
    ("ORBITA", "0x19b8d7613A6C2E4168a6a0Bb97ca0c842035d709", "1000000000000000000000000"),
    ("WW3", "0xf62628D99B28535ee593Ab5D6dFE7D914f5edca0", "90000000000000000000000"),
    ("POSTAGE", "0x6C310EABEdFD4eEd6148bf2C07241FB45a52FB42", "10000000000000000000000"),
    ("MALTA", "0x728095Ab0BD71636Db5DA4E2A6d7f5cc73729fc0", "1000000000000000000000000"),
    ("JINMA", "0xe4517E6718b24D5725956ac7A90686592a7b1539", "50000000000000000000000000"),
    ("THYRK", "0x3b8747D067B2Ed8565330667128260C2a4954300", "20000000000000000000"),
    ("LUCKY777", "0xc6D4ec8CB889aFBa9f251606001457644E260f7D", "50000000000000000000000000"),
    ("WNO", "0x8C969a4CD49E4774908e667702C3d7C3ece164D0", "1000000000000000000000000"),
    ("AMBR", "0x88B06f59BdB54039AEBf1d308d8B9181a90385c1", "10000000000000000000000"),
    ("CHEEMSA", "0x00b4bdA5BBf83A72f1252CCEf361f107f5a728b2", "5000000000000000000000000"),
    ("NEB", "0xf08ac9c91dcfc5b74eae6c87e744cfefe0d32a68", "1000000000000000000000"),
]

out = {"run": "pending-coin-swap-watch 2026-11-15 16:51 WIB", "entries": []}
# fresh gas price
gp = None
for url in ENDPOINTS:
    try:
        r = rpc(url, "eth_gasPrice", [])
        if r is not None:
            gp = u256(r); break
    except Exception:
        continue
out["gas_price_wei"] = gp
out["gas_estimate_bnb_300k"] = (gp * 300000 / 1e18) if gp else None

for sym, tok, amt in ENTRIES:
    item = {"symbol": sym, "token": tok}
    bal_h, url = call(tok, "0x" + sel("balanceOf(address)") + encode(["address"], [W]).hex())
    item["endpoint"] = url
    if bal_h is None:
        item["status"] = "rpc_failed_balance"; out["entries"].append(item); continue
    bal = u256(bal_h)
    item["balance_raw"] = str(bal); item["balance_human"] = bal / 1e18
    if bal == 0:
        item["status"] = "empty"; out["entries"].append(item); continue
    pair_h, _ = call(FACTORY, "0x" + sel("getPair(address,address)") + encode(["address", "address"], [tok, WBNB]).hex())
    pair = ("0x" + pair_h[-40:]) if pair_h and u256(pair_h) else None
    item["pair_wbnb"] = pair
    if not pair:
        item["status"] = "no_pair"; out["entries"].append(item); continue
    res_h, _ = call(pair, "0x" + sel("getReserves()"))
    if res_h:
        r0, r1, _ = decode(["uint112", "uint112", "uint32"], bytes.fromhex(res_h[2:]))
        item["reserves"] = [str(r0), str(r1)]
        if r0 == 0 or r1 == 0:
            item["status"] = "pair_empty"; out["entries"].append(item); continue
    else:
        item["status"] = "rpc_failed_reserves"; out["entries"].append(item); continue
    sell = int(amt) if amt else bal
    item["sell_raw"] = str(sell)
    q_h, _ = call(ROUTER, "0x" + sel("getAmountsOut(uint256,address[])") + encode(["uint256", "address[]"], [sell, [tok, WBNB]]).hex())
    if q_h:
        outs = decode(["uint256[]"], bytes.fromhex(q_h[2:]))[0]
        item["quote_bnb"] = outs[1] / 1e18 if len(outs) == 2 else None
        thr = 2 * out["gas_estimate_bnb_300k"] if out["gas_estimate_bnb_300k"] else 3e-05
        item["quote_ge_2x_gas"] = item["quote_bnb"] is not None and item["quote_bnb"] >= thr
        item["status"] = "executable_candidate" if item["quote_ge_2x_gas"] else "quote_dust"
    else:
        item["status"] = "no_quote"
    out["entries"].append(item)
print(json.dumps(out, indent=1))
