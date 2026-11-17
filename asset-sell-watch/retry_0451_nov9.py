#!/usr/bin/env python3
"""Focused retry for pending-coin-swap-watch 2026-11-09 04:51 WIB.
Direct run verified POA + BNBbaby fresh; 8 balances failed (RPC flaky mid-run).
Retries only the 8 failed tokens, 2 endpoints (publicnode, dataseed1), 20s each.
For tokens with a known live pair (YYDS, 币安加油) also re-reads reserves+quote.
Read-only."""
import json, urllib.request
from eth_abi import encode, decode
from eth_utils import keccak

W = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
ROUTER = "0x10ED43C718714eb63d5aA57B78B54704E256024E"
FACTORY = "0xca143ce32fe78f1f7019d7d551a6402fc5350c73"
WBNB = "0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c"
ENDPOINTS = ["https://bsc-rpc.publicnode.com/", "https://bsc-dataseed1.bnbchain.org/"]

def sel(sig): return keccak(text=sig).hex()[:8]
def u256(h):
    try: return int(h, 16) if h else 0
    except Exception: return 0

def rpc(method, params, timeout=20):
    payload = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode()
    for url in ENDPOINTS:
        try:
            req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
            res = json.loads(urllib.request.urlopen(req, timeout=timeout).read())
            if isinstance(res, dict) and res.get("result"):
                return res["result"]
        except Exception:
            continue
    return None

def call(to, data):
    return rpc("eth_call", [{"to": to, "data": data}, "latest"])

TOKENS = [
    ("PATCH", "0xBbA053567846842F95C060867a5C9eb6b3983c80", None, None),
    ("QAGENT", "0x25e915EEE91411b0AC3273531dbaDc34e0EAA5eB", None, None),
    ("YYDS", "0xd23be069c3c3a7f631af52584a16a9e46bb41da1", None, "0xD15c928B7b777CaC7d613FE840C6eC3dE8e4EdDA"),
    ("\u5e01\u5b89\u52a0\u6cb9", "0x397BF425926F521Ac5BEbe5062793BB224e3eF8f", "50000000000000000000000000", "0xc939e2b49eea548c4539e45b4e355c2b2aa464d6"),
    ("PACTURE", "0x10b80088fDAf9363d83671BE66b64f231f9e92f6", "10000000000000000000000000", None),
    ("ORBITA", "0x19b8d7613A6C2E4168a6a0Bb97ca0c842035d709", "1000000000000000000000000", None),
    ("WW3", "0xf62628D99B28535ee593Ab5D6dFE7D914f5edca0", "10000000000000000000000", None),
    ("JINCHAN", "0xE2DFa6c6c7189a885bC0919527A303319f4EEffC", "50000000000000000000000", None),
]
gp_raw = rpc("eth_gasPrice", [])
gp = u256(gp_raw) if gp_raw else None
out = {"gas_price_wei": gp, "gas_price_gwei": (gp / 1e9 if gp else None),
       "gas_est_300k_bnb": (gp * 300000 / 1e18 if gp else None), "entries": []}
for sym, tok, sell_raw, known_pair in TOKENS:
    item = {"symbol": sym, "token": tok}
    bal_h = call(tok, "0x" + sel("balanceOf(address)") + encode(["address"], [W]).hex())
    if bal_h is None:
        item["status"] = "rpc_failed_balance"; out["entries"].append(item); continue
    bal = u256(bal_h)
    item["balance_raw"] = str(bal); item["balance_human"] = bal / 1e18
    if bal == 0:
        item["status"] = "empty"; out["entries"].append(item); continue
    pair = known_pair
    if not pair:
        pair_h = call(FACTORY, "0x" + sel("getPair(address,address)") + encode(["address", "address"], [tok, WBNB]).hex())
        pair = ("0x" + pair_h[-40:]) if pair_h and u256(pair_h) else None
    item["pair_wbnb"] = pair
    if not pair:
        item["status"] = "no_pair"; out["entries"].append(item); continue
    res_h = call(pair, "0x" + sel("getReserves()"))
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
    q_h = call(ROUTER, "0x" + sel("getAmountsOut(uint256,address[])") + encode(["uint256", "address[]"], [sell_amt, [tok, WBNB]]).hex())
    if q_h:
        try:
            outs = decode(["uint256[]"], bytes.fromhex(q_h[2:]))[0]
            item["quote_bnb"] = outs[1] / 1e18 if len(outs) == 2 else None
            item["quote_raw"] = str(outs[1]) if len(outs) == 2 else None
        except Exception as ex:
            item["quote_error"] = str(ex)
    if item.get("quote_bnb") is not None and gp:
        item["quote_ge_2x_gas"] = item["quote_bnb"] >= 2 * gp * 300000 / 1e18
        item["status"] = "executable_candidate" if item["quote_ge_2x_gas"] else "quote_dust"
    elif item.get("quote_bnb") is None:
        item["status"] = "no_quote"
    out["entries"].append(item)
    json.dump(out, open("/home/hatch/workspace/asset-sell-watch/retry_0451_nov9.json", "w"), indent=1, ensure_ascii=False)

print(json.dumps(out, indent=1, ensure_ascii=False))
