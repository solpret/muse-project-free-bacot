#!/usr/bin/env python3
"""Lean targeted retry for pending-coin-swap-watch 2026-11-08 11:51 WIB run.
Covers: fresh gasPrice, BIA pair+reserves (main run read pair null vs
0xc939... + 0/0 last run), PACTURE balanceOf (rpc_failed_balance in main
run), launched()/phase() batch for all 9 sale contracts. Read-only.
Hard per-call timeout 8s, max 2 RPCs per call, global deadline 110s."""
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

# BIA pair + reserves
bia = "0x397BF425926F521Ac5BEbe5062793BB224e3eF8f"
item = {}
pair_h, prpc = call(FACTORY, "0x" + sel("getPair(address,address)") + encode(["address", "address"], [bia, WBNB]).hex())
item["pair_rpc"] = prpc
pair = ("0x" + pair_h[-40:]) if pair_h and u256(pair_h) else None
item["pair_wbnb"] = pair
if pair:
    res_h, _ = call(pair, "0x" + sel("getReserves()"))
    if res_h:
        try:
            r0, r1, _ = decode(["uint112", "uint112", "uint32"], bytes.fromhex(res_h[2:]))
            item["reserves"] = [str(r0), str(r1)]
            item["status"] = "pair_empty" if (r0 == 0 or r1 == 0) else "has_liquidity"
        except Exception as ex:
            item["reserves_error"] = str(ex)
    else:
        item["status"] = "reserves_failed"
else:
    item["status"] = "no_pair"
out["BIA"] = item

# PACTURE balance + pair
pac = "0x10b80088fDAf9363d83671BE66b64f231f9e92f6"
pitem = {}
bal_h, brpc = call(pac, "0x" + sel("balanceOf(address)") + encode(["address"], [W]).hex())
pitem["rpc"] = brpc
if bal_h is None:
    pitem["status"] = "rpc_failed_balance"
else:
    bal = u256(bal_h)
    pitem["balance_raw"] = str(bal)
    pitem["balance_human"] = bal / 1e18
    if bal == 0:
        pitem["status"] = "empty"
    else:
        pair_h, prpc = call(FACTORY, "0x" + sel("getPair(address,address)") + encode(["address", "address"], [pac, WBNB]).hex())
        pair = ("0x" + pair_h[-40:]) if pair_h and u256(pair_h) else None
        pitem["pair_wbnb"] = pair
        pitem["status"] = "no_pair" if not pair else "has_pair"
out["PACTURE"] = pitem

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
