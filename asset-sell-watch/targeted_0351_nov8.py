#!/usr/bin/env python3
"""Targeted retry for pending-coin-swap-watch 2026-11-08 03:51 WIB run.
Covers items with failed/incomplete reads in the main run (pending_check.py):
YYDS (balance null); BIA (getReserves + getAmountsOut returned nothing, pair
0xc939... was reserves 0/0 in prior runs - verify, not assume).
Rotating RPC endpoints. Read-only."""
import json, urllib.request
from eth_abi import encode, decode
from eth_utils import keccak

W = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
ROUTER = "0x10ED43C718714eb63d5aA57B78B54704E256024E"
FACTORY = "0xca143ce32fe78f1f7019d7d551a6402fc5350c73"
WBNB = "0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c"
RPCS = ["https://bsc-dataseed1.binance.org/", "https://bsc-dataseed2.binance.org/",
        "https://bsc-dataseed1.defibit.io/", "https://bsc-dataseed.binance.org/",
        "https://bsc.publicnode.com"]

def sel(sig): return keccak(text=sig).hex()[:8]
def call_one(rpc, to, data):
    body = json.dumps({"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":to,"data":data},"latest"]}).encode()
    req = urllib.request.Request(rpc, data=body, headers={"Content-Type":"application/json"})
    r = json.loads(urllib.request.urlopen(req, timeout=20).read())
    if r.get("error") or not r.get("result"): return None
    return r["result"]
def call(to, data):
    for rpc in RPCS:
        try:
            v = call_one(rpc, to, data)
            if v is not None: return v, rpc
        except Exception: continue
    return None, None
def u256(h): return int(h,16) if h else 0

out = {}
gp = None
for rpc in RPCS:
    try:
        body = json.dumps({"jsonrpc":"2.0","id":1,"method":"eth_gasPrice","params":[]}).encode()
        req = urllib.request.Request(rpc, data=body, headers={"Content-Type":"application/json"})
        r = json.loads(urllib.request.urlopen(req, timeout=20).read())
        if r.get("result"): gp = int(r["result"],16); out["gas_rpc"] = rpc; break
    except Exception: continue
out["gas_price_wei"] = gp
out["gas_price_gwei"] = gp/1e9 if gp else None
out["gas_est_300k_bnb"] = gp*300000/1e18 if gp else None

TOKENS = [
    ("YYDS", "0xd23be069c3c3a7f631af52584a16a9e46bb41da1", None,
     "0x62AB0519dED1B70481021D31fa6BAcB7450b78F3"),
    ("BIA", "0x397BF425926F521Ac5BEbe5062793BB224e3eF8f", "50000000000000000000000000",
     "0xC9b4d42ABe8966496aa68a736938Bf2D508F7a91"),
]
for sym, tok, sell_raw, sc in TOKENS:
    item = {}
    bal_h, rpc = call(tok, "0x"+sel("balanceOf(address)")+encode(["address"],[W]).hex())
    item["rpc"] = rpc
    if bal_h is None:
        item["status"] = "rpc_failed_balance"; out[sym] = item; continue
    bal = u256(bal_h)
    item["balance_raw"] = str(bal); item["balance_human"] = bal/1e18
    if bal == 0:
        item["status"] = "empty"; out[sym] = item; continue
    pair_h, prpc = call(FACTORY, "0x"+sel("getPair(address,address)")+encode(["address","address"],[tok,WBNB]).hex())
    item["pair_rpc"] = prpc
    pair = ("0x"+pair_h[-40:]) if pair_h and u256(pair_h) else None
    item["pair_wbnb"] = pair
    if not pair:
        item["status"] = "no_pair"; out[sym] = item; continue
    t0_h, _ = call(pair, "0x"+sel("token0()"))
    t1_h, _ = call(pair, "0x"+sel("token1()"))
    res_h, _ = call(pair, "0x"+sel("getReserves()"))
    if res_h:
        r0, r1, _ = decode(["uint112","uint112","uint32"], bytes.fromhex(res_h[2:]))
        item["reserves"] = [str(r0), str(r1)]
        item["token0"] = ("0x"+t0_h[-40:]) if t0_h else None
        item["token1"] = ("0x"+t1_h[-40:]) if t1_h else None
        if r0 == 0 or r1 == 0:
            item["status"] = "pair_empty"; out[sym] = item; continue
    else:
        item["reserves_error"] = "getReserves returned nothing on all RPCs"
    sell_amt = int(sell_raw) if sell_raw else bal
    item["sell_amount_raw"] = str(sell_amt)
    q_h, _ = call(ROUTER, "0x"+sel("getAmountsOut(uint256,address[])")+encode(["uint256","address[]"],[sell_amt,[tok,WBNB]]).hex())
    if q_h:
        outs = decode(["uint256[]"], bytes.fromhex(q_h[2:]))[0]
        item["quote_bnb"] = outs[1]/1e18 if len(outs)==2 else None
        item["quote_raw"] = str(outs[1]) if len(outs)==2 else None
    if item.get("quote_bnb") is not None:
        item["quote_ge_2x_gas"] = (gp is not None and item["quote_bnb"] >= 2*gp*300000/1e18)
        item["status"] = "executable_candidate" if item["quote_ge_2x_gas"] else "quote_dust"
    else:
        item["status"] = "no_quote"
    if sc:
        lh, _ = call(sc, "0x8091f3bf")  # launched() selector verified in earlier runs
        item["sale_contract"] = sc; item["launched_raw"] = lh
        if lh:
            try: item["launched"] = decode(["bool"], bytes.fromhex(lh[2:]))[0]
            except Exception: item["launched"] = None
    out[sym] = item

print(json.dumps(out, indent=1))
