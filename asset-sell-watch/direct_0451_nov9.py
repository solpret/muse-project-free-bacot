#!/usr/bin/env python3
"""Direct-endpoint retry for pending-coin-swap-watch 2026-11-09 04:51 WIB.
fast_rpc failed on all endpoints (breaker state + timeouts) but direct probes
show https://bsc-rpc.publicnode.com/ and https://bsc-dataseed1.bnbchain.org/
answering eth_blockNumber. Uses plain urllib, one endpoint at a time with
fallback, 45s timeout, single eth_calls. Read-only."""
import json, urllib.request
from eth_abi import encode, decode
from eth_utils import keccak

W = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
ROUTER = "0x10ED43C718714eb63d5aA57B78B54704E256024E"
FACTORY = "0xca143ce32fe78f1f7019d7d551a6402fc5350c73"
WBNB = "0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c"
ENDPOINTS = ["https://bsc-rpc.publicnode.com/",
             "https://bsc-dataseed1.bnbchain.org/",
             "https://bsc-dataseed2.bnbchain.org/",
             "https://bsc-dataseed4.bnbchain.org/"]

def sel(sig): return keccak(text=sig).hex()[:8]
def u256(h):
    try: return int(h, 16) if h else 0
    except Exception: return 0

def rpc(method, params):
    payload = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode()
    last_err = None
    for url in ENDPOINTS:
        try:
            req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
            res = json.loads(urllib.request.urlopen(req, timeout=45).read())
            if isinstance(res, dict) and res.get("result"):
                return res["result"]
            last_err = str(res)[:120]
        except Exception as e:
            last_err = str(e)[:120]
    return None

def call(to, data):
    return rpc("eth_call", [{"to": to, "data": data}, "latest"])

data = json.load(open("/home/hatch/workspace/asset-sell-watch/pending-swaps.json"))
gp_raw = rpc("eth_gasPrice", [])
gp = u256(gp_raw) if gp_raw else None
out = {"gas_price_wei": gp, "gas_price_gwei": (gp / 1e9 if gp else None),
       "gas_est_300k_bnb": (gp * 300000 / 1e18 if gp else None), "entries": []}
for e in data["entries"]:
    tok, sym = e["token"], e["symbol"]
    item = {"symbol": sym, "token": tok, "registered_amount_human": e.get("amount_human"),
            "amount_to_sell_raw": e.get("amount_to_sell_raw"), "reason_prev": e.get("reason")}
    bal_h = call(tok, "0x" + sel("balanceOf(address)") + encode(["address"], [W]).hex())
    if bal_h is None:
        item["status"] = "rpc_failed_balance"; out["entries"].append(item); continue
    bal = u256(bal_h)
    item["balance_raw"] = str(bal); item["balance_human"] = bal / 1e18
    if bal == 0:
        item["status"] = "empty"; out["entries"].append(item); continue
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
    if item.get("quote_bnb") is not None and gp:
        item["quote_ge_2x_gas"] = item["quote_bnb"] >= 2 * gp * 300000 / 1e18
        item["status"] = "executable_candidate" if item["quote_ge_2x_gas"] else "quote_dust"
    elif item.get("quote_bnb") is None:
        item["status"] = "no_quote"
    sc = e.get("sale_contract")
    if sc:
        lh = call(sc, "0x" + sel("launched()"))
        item["sale_contract"] = sc
        item["launched_raw"] = lh
        if lh is not None:
            try:
                item["launched"] = decode(["bool"], bytes.fromhex(lh[2:]))[0]
            except Exception:
                item["launched"] = None
    out["entries"].append(item)
    json.dump(out, open("/home/hatch/workspace/asset-sell-watch/direct_0451_nov9.json", "w"), indent=1, ensure_ascii=False)

print(json.dumps(out, indent=1, ensure_ascii=False))
