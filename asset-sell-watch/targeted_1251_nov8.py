#!/usr/bin/env python3
"""Lean targeted retry for pending-coin-swap-watch 2026-11-08 12:51 WIB run.
Main run (pending_check.py, bsc-dataseed.binance.org) glitches:
- gasPrice failed (RemoteDisconnected)
- balanceOf failed: BNBbaby, QAGENT, BIA, WW3
- YYDS getPair returned null (last run: pair 0xd15c... + reserves + quote
  0.0000110612 BNB) -> re-read pair + reserves + quote
- BIA pair read null in main run -> re-read pair + reserves (known pair
  0xc939e2b49eea548c4539e45b4e355c2b2aa464d6, 0/0 last run)
- launched()/phase() batch for all 9 sale contracts.
Read-only. Hard per-call timeout 8s, max 2 RPCs per call, global deadline 110s."""
import json, time, urllib.request
from eth_abi import encode, decode
from eth_utils import keccak

DEADLINE = time.time() + 110
W = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
ROUTER = "0x10ED43C718714eb63d5aA57B78B54704E256024E"
FACTORY = "0xca143ce32fe78f1f7019d7d551a6402fc5350c73"
WBNB = "0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c"
RPCS = ["https://bsc-dataseed1.binance.org/", "https://bsc.publicnode.com",
        "https://bsc-dataseed.binance.org/"]

def sel(sig):
    return keccak(text=sig).hex()[:8]

def call_one(rpc, to, data):
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                       "params": [{"to": to, "data": data}, "latest"]}).encode()
    req = urllib.request.Request(rpc, data=body, headers={"Content-Type": "application/json"})
    r = json.loads(urllib.request.urlopen(req, timeout=8).read())
    if r.get("error") or not r.get("result"):
        return None
    return r["result"]

def call(to, data):
    for rpc in RPCS[:2]:
        if time.time() > DEADLINE:
            return None, None
        try:
            v = call_one(rpc, to, data)
            if v is not None:
                return v, rpc
        except Exception:
            continue
    return None, None

def u256(h):
    try:
        return int(h, 16) if h else 0
    except Exception:
        return 0

out = {}
# gas price
gp = None
for rpc in RPCS[:2]:
    try:
        body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_gasPrice", "params": []}).encode()
        req = urllib.request.Request(rpc, data=body, headers={"Content-Type": "application/json"})
        r = json.loads(urllib.request.urlopen(req, timeout=8).read())
        if r.get("result"):
            gp = int(r["result"], 16)
            out["gas_rpc"] = rpc
            break
    except Exception:
        continue
out["gas_price_gwei"] = gp / 1e9 if gp else None
out["gas_est_300k_bnb"] = gp * 300000 / 1e18 if gp else None
out["gas_2x_threshold_bnb"] = 2 * gp * 300000 / 1e18 if gp else None

def balance(tok):
    bal_h, brpc = call(tok, "0x" + sel("balanceOf(address)") + encode(["address"], [W]).hex())
    if bal_h is None:
        return {"status": "rpc_failed_balance", "rpc": brpc}
    bal = u256(bal_h)
    return {"balance_raw": str(bal), "balance_human": bal / 1e18, "status": "empty" if bal == 0 else "has_balance", "rpc": brpc}

def pair_info(tok, sell_amt=None):
    item = {}
    pair_h, prpc = call(FACTORY, "0x" + sel("getPair(address,address)") + encode(["address", "address"], [tok, WBNB]).hex())
    item["pair_rpc"] = prpc
    pair = ("0x" + pair_h[-40:]) if pair_h and u256(pair_h) else None
    item["pair_wbnb"] = pair
    if not pair:
        item["status"] = "no_pair"
        return item
    res_h, _ = call(pair, "0x" + sel("getReserves()"))
    if res_h:
        try:
            r0, r1, _ = decode(["uint112", "uint112", "uint32"], bytes.fromhex(res_h[2:]))
            item["reserves"] = [str(r0), str(r1)]
            if r0 == 0 or r1 == 0:
                item["status"] = "pair_empty"
                return item
        except Exception as ex:
            item["reserves_error"] = str(ex)
            item["status"] = "reserves_failed"
            return item
    else:
        item["status"] = "reserves_failed"
        return item
    if sell_amt:
        q_h, _ = call(ROUTER, "0x" + sel("getAmountsOut(uint256,address[])") + encode(["uint256", "address[]"], [sell_amt, [tok, WBNB]]).hex())
        if q_h:
            try:
                outs = decode(["uint256[]"], bytes.fromhex(q_h[2:]))[0]
                item["quote_bnb"] = outs[1] / 1e18 if len(outs) == 2 else None
                item["quote_raw"] = str(outs[1]) if len(outs) == 2 else None
            except Exception as ex:
                item["quote_error"] = str(ex)
    item["status"] = "has_liquidity"
    return item

# Failed balances
out["BNBbaby"] = balance("0xd0079025a9bb66a7a1de991de2e4326faba35729")
out["QAGENT"] = balance("0x25e915EEE91411b0AC3273531dbaDc34e0EAA5eB")
out["BIA"] = balance("0x397BF425926F521Ac5BEbe5062793BB224e3eF8f")
out["WW3"] = balance("0xf62628D99B28535ee593Ab5D6dFE7D914f5edca0")
# Pair re-reads
for sym, item in (("BNBbaby", out["BNBbaby"]), ("QAGENT", out["QAGENT"]),
                  ("BIA", out["BIA"]), ("WW3", out["WW3"])):
    if item.get("status") == "has_balance":
        tok = {"BNBbaby": "0xd0079025a9bb66a7a1de991de2e4326faba35729",
               "QAGENT": "0x25e915EEE91411b0AC3273531dbaDc34e0EAA5eB",
               "BIA": "0x397BF425926F521Ac5BEbe5062793BB224e3eF8f",
               "WW3": "0xf62628D99B28535ee593Ab5D6dFE7D914f5edca0"}[sym]
        item.update(pair_info(tok))
# YYDS: pair + reserves + quote (full balance 177600000000000)
yyds = "0xd23be069c3c3a7f631af52584a16a9e46bb41da1"
out["YYDS"] = pair_info(yyds, sell_amt=177600000000000)
if out["YYDS"].get("quote_bnb") is not None and out.get("gas_2x_threshold_bnb") is not None:
    out["YYDS"]["quote_ge_2x_gas"] = out["YYDS"]["quote_bnb"] >= out["gas_2x_threshold_bnb"]

# launched()/phase() batch for all 9 sale contracts
sales = {
    "POA": "0x74d9b5477e7fa818298f927966452f2eb9c5fa5e",
    "BNBbaby": "0xbb7ed59ca41ea03cf20084a8c9de94244b7b2637",
    "PATCH": "0xCaFa8f3563E1ACd57abe24C42663BD1D103651C3",
    "QAGENT": "0xE3a4f3099a2136e0e66202A665815caB8FFA2704",
    "YYDS": "0x62AB0519dED1B70481021D31fa6BAcB7450b78F3",
    "BIA": "0xC9b4d42ABe8966496aa68a736938Bf2D508F7a91",
    "PACTURE": "0x95AF9fe16fE5c1741b5E3F1b3b045a8c2470eca9",
    "ORBITA": "0x19b8d7613A6C2E4168a6a0Bb97ca0c842035d709",
    "WW3": "0x1Aa9797cC762b838388566Daa45A56b1709F4Bbe",
}
sc_out = {}
for sym, sc in sales.items():
    if time.time() > DEADLINE:
        sc_out[sym] = {"status": "skipped_deadline"}
        continue
    entry = {}
    lh, _ = call(sc, "0x" + sel("launched()"))
    entry["launched_raw"] = lh
    if lh:
        try:
            entry["launched"] = decode(["bool"], bytes.fromhex(lh[2:]))[0]
        except Exception:
            entry["launched"] = None
    ph, _ = call(sc, "0x" + sel("phase()"))
    entry["phase_raw"] = ph
    if ph:
        try:
            entry["phase"] = decode(["uint256"], bytes.fromhex(ph[2:]))[0]
        except Exception:
            entry["phase"] = None
    sc_out[sym] = entry
out["sale_contracts"] = sc_out
print(json.dumps(out, indent=1))
