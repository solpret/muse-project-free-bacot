#!/usr/bin/env python3
"""Pending-swap check run 2026-11-17 22:51 WIB — read-only, batched via fast_rpc.
Reads fresh: balanceOf, decimals, factory getPair(token,WBNB), token0/getReserves,
getAmountsOut(sell amount), gasPrice, sale launched()/tradingOpen() best effort."""
import sys, json
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import batch_race, call_many
from eth_abi import encode, decode
from eth_utils import keccak

W = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
ROUTER = "0x10ED43C718714eb63d5aA57B78B54704E256024E"
FACTORY = "0xca143ce32fe78f1f7019d7d551a6402fc5350c73"
WBNB = "0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c"

def sel(sig):
    return keccak(text=sig).hex()[:8]

def u256(h):
    try:
        return int(h, 16) if h else 0
    except Exception:
        return 0

def ec(to, data):
    return ("eth_call", [{"to": to, "data": data}, "latest"])

data = json.load(open("/home/hatch/workspace/asset-sell-watch/pending-swaps.json"))
entries = data["entries"]

# ---- batch 1: gasPrice + balanceOf + decimals + getPair for all ----
calls = [("eth_gasPrice", [])]
for e in entries:
    tok = e["token"]
    calls.append(ec(tok, "0x" + sel("balanceOf(address)") + encode(["address"], [W]).hex()))
    calls.append(ec(tok, "0x" + sel("decimals()")))
    calls.append(ec(FACTORY, "0x" + sel("getPair(address,address)") + encode(["address", "address"], [tok, WBNB]).hex()))
try:
    res1, err1 = batch_race(calls, timeout=15)
except Exception as ex:
    res1, err1 = call_many(calls, timeout=20)
gas_price = u256(res1[0]) if res1 and res1[0] else None
gas_est_bnb = (gas_price * 300000 / 1e18) if gas_price else None

out = {"run": "2026-11-17 22:51 WIB", "gas_price_wei": gas_price,
       "gas_price_gwei": (gas_price / 1e9 if gas_price else None),
       "gas_est_300k_bnb": gas_est_bnb, "batch1_err": err1, "entries": []}

items = []
for i, e in enumerate(entries):
    tok = e["token"]; sym = e["symbol"]
    item = {"symbol": sym, "token": tok, "registered_amount_human": e.get("amount_human"),
            "amount_to_sell_raw": e.get("amount_to_sell_raw"), "reason_prev": e.get("reason")}
    bal_h, dec_h, pair_h = res1[1 + i*3], res1[2 + i*3], res1[3 + i*3]
    if bal_h is None:
        item["status"] = "rpc_failed_balance"; items.append(item); continue
    bal = u256(bal_h); dec = u256(dec_h) if dec_h else 18
    item["balance_raw"] = str(bal); item["balance_human"] = bal / (10**dec) if dec < 40 else None
    item["decimals"] = dec
    if bal == 0:
        item["status"] = "empty"; items.append(item); continue
    pair = ("0x" + pair_h[-40:]) if pair_h and u256(pair_h) else None
    item["pair_wbnb"] = pair
    if not pair:
        item["status"] = "no_pair"; items.append(item); continue
    items.append(item)

# ---- batch 2: token0 + getReserves for existing pairs; launched()/tradingOpen() for sale contracts ----
calls2, idx2 = [], []
for it in items:
    if it.get("pair_wbnb"):
        idx2.append(("tok0", it)); calls2.append(ec(it["pair_wbnb"], "0x" + sel("token0()")))
        idx2.append(("res", it)); calls2.append(ec(it["pair_wbnb"], "0x" + sel("getReserves()")))
for e in entries:
    sc = e.get("sale_contract")
    if sc:
        idx2.append(("launched", e["symbol"])); calls2.append(ec(sc, "0x" + sel("launched()")))
        idx2.append(("tradingOpen", e["symbol"])); calls2.append(ec(sc, "0x" + sel("tradingOpen()")))
try:
    res2, err2 = batch_race(calls2, timeout=15) if calls2 else ([], None)
except Exception as ex:
    res2, err2 = call_many(calls2, timeout=20) if calls2 else ([], None)
out["batch2_err"] = err2
launched_map = {}
for (kind, ref), rh in zip(idx2, res2):
    if kind == "tok0":
        ref["token0"] = ("0x" + rh[-40:]) if rh else None
    elif kind == "res":
        if rh:
            try:
                r0, r1, _ = decode(["uint112", "uint112", "uint32"], bytes.fromhex(rh[2:]))
                ref["reserves"] = [str(r0), str(r1)]
            except Exception as ex:
                ref["reserves_error"] = str(ex)
        else:
            ref["reserves_error"] = "null"
    elif kind == "launched":
        launched_map.setdefault(ref, {})["launched_raw"] = rh
        if rh is not None:
            try:
                launched_map[ref]["launched"] = decode(["bool"], bytes.fromhex(rh[2:]))[0]
            except Exception:
                launched_map[ref]["launched"] = None
    elif kind == "tradingOpen":
        launched_map.setdefault(ref, {})["tradingOpen_raw"] = rh
        if rh is not None:
            try:
                launched_map[ref]["tradingOpen"] = decode(["bool"], bytes.fromhex(rh[2:]))[0]
            except Exception:
                launched_map[ref]["tradingOpen"] = None

# ---- batch 3: getAmountsOut for pairs with reserves > 0 ----
calls3, idx3 = [], []
for it in items:
    res = it.get("reserves")
    if res and int(res[0]) > 0 and int(res[1]) > 0:
        bal = int(it["balance_raw"])
        sell_amt = int(it["amount_to_sell_raw"]) if it.get("amount_to_sell_raw") else bal
        it["sell_amount_raw"] = str(sell_amt)
        idx3.append(it)
        calls3.append(ec(ROUTER, "0x" + sel("getAmountsOut(uint256,address[])") + encode(["uint256", "address[]"], [sell_amt, [it["token"], WBNB]]).hex()))
    elif res:
        it["status"] = "pair_empty"
try:
    res3, err3 = batch_race(calls3, timeout=15) if calls3 else ([], None)
except Exception as ex:
    res3, err3 = call_many(calls3, timeout=20) if calls3 else ([], None)
out["batch3_err"] = err3
for it, qh in zip(idx3, res3):
    if qh:
        try:
            outs = decode(["uint256[]"], bytes.fromhex(qh[2:]))[0]
            it["quote_bnb"] = outs[1] / 1e18 if len(outs) == 2 else None
            it["quote_raw"] = str(outs[1]) if len(outs) == 2 else None
        except Exception as ex:
            it["quote_error"] = str(ex)
    if it.get("quote_bnb") is not None:
        q = it["quote_bnb"]
        it["quote_ge_2x_gas"] = (gas_est_bnb is not None and q >= 2 * gas_est_bnb)
        it["status"] = "executable_candidate" if it["quote_ge_2x_gas"] else "quote_dust"
    else:
        it["status"] = "no_quote"

for it in items:
    lm = launched_map.get(it["symbol"])
    if lm:
        it.update(lm)
out["entries"] = items
print(json.dumps(out, indent=1))
json.dump(out, open("/home/hatch/workspace/asset-sell-watch/run-2026-11-17-2251.json", "w"), indent=1)
