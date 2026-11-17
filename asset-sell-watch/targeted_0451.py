#!/usr/bin/env python3
"""Targeted retry for pending-coin-swap-watch 2026-11-07 04:51 WIB run.
Covers items that failed in the main run: gasPrice, 币安加油 balance/pair/
reserves, KAGENT launched(), PACTURE sale-contract launched() (best effort),
YYDS quote re-check with fresh gas. Rotating RPC endpoints, 20s timeout."""
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

# 币安加油: balance + pair + reserves
b = {}
tok = "0x397BF425926F521Ac5BEbe5062793BB224e3eF8f"
bal_h, rpc = call(tok, "0x"+sel("balanceOf(address)")+encode(["address"],[W]).hex())
b["rpc"] = rpc
if bal_h is None:
    b["status"] = "rpc_failed_balance"
else:
    bal = u256(bal_h)
    b["balance_raw"] = str(bal); b["balance_human"] = bal/1e18
    if bal == 0:
        b["status"] = "empty"
    else:
        pair_h, _ = call(FACTORY, "0x"+sel("getPair(address,address)")+encode(["address","address"],[tok,WBNB]).hex())
        pair = ("0x"+pair_h[-40:]) if pair_h and u256(pair_h) else None
        b["pair_wbnb"] = pair
        if not pair:
            b["status"] = "no_pair"
        else:
            t0_h, _ = call(pair, "0x"+sel("token0()"))
            t1_h, _ = call(pair, "0x"+sel("token1()"))
            res_h, _ = call(pair, "0x"+sel("getReserves()"))
            if res_h:
                r0, r1, _ = decode(["uint112","uint112","uint32"], bytes.fromhex(res_h[2:]))
                b["reserves"] = [str(r0), str(r1)]
                b["token0"] = ("0x"+t0_h[-40:]) if t0_h else None
                b["token1"] = ("0x"+t1_h[-40:]) if t1_h else None
                if r0 == 0 or r1 == 0:
                    b["status"] = "pair_empty"
                else:
                    sell_amt = 50000000000000000000000000
                    q_h, _ = call(ROUTER, "0x"+sel("getAmountsOut(uint256,address[])")+encode(["uint256","address[]"],[sell_amt,[tok,WBNB]]).hex())
                    if q_h:
                        outs = decode(["uint256[]"], bytes.fromhex(q_h[2:]))[0]
                        b["quote_bnb"] = outs[1]/1e18 if len(outs)==2 else None
                        b["quote_raw"] = str(outs[1]) if len(outs)==2 else None
                        if b.get("quote_bnb") is not None:
                            b["quote_ge_2x_gas"] = (gp is not None and b["quote_bnb"] >= 2*gp*300000/1e18)
                            b["status"] = "executable_candidate" if b["quote_ge_2x_gas"] else "quote_dust"
                        else:
                            b["status"] = "no_quote"
                    else:
                        b["status"] = "no_quote"
out["币安加油"] = b

# KAGENT launched()
k = {}
lh, rpc = call("0xb34105002B19EF0ce43B59011fE848df5c8B174f", "0x"+sel("launched()"))
k["rpc"] = rpc; k["launched_raw"] = lh
if lh:
    try: k["launched"] = decode(["bool"], bytes.fromhex(lh[2:]))[0]
    except Exception: k["launched"] = None
out["KAGENT_launched"] = k

# PACTURE sale contract launched() — best effort
p = {}
lh, rpc = call("0x95AF9fe16fE5c1741b5E3F1b3b045a8c2470eca9", "0x"+sel("launched()"))
p["rpc"] = rpc; p["launched_raw"] = lh
if lh:
    try: p["launched"] = decode(["bool"], bytes.fromhex(lh[2:]))[0]
    except Exception: p["launched"] = None
out["PACTURE_launched"] = p

# YYDS quote re-check with fresh gas
y = {}
yyds_tok = "0xd23be069c3c3a7f631af52584a16a9e46bb41da1"
q_h, rpc = call(ROUTER, "0x"+sel("getAmountsOut(uint256,address[])")+encode(["uint256","address[]"],[177600000000000,[yyds_tok,WBNB]]).hex())
y["rpc"] = rpc
if q_h:
    outs = decode(["uint256[]"], bytes.fromhex(q_h[2:]))[0]
    y["quote_bnb"] = outs[1]/1e18 if len(outs)==2 else None
    y["quote_raw"] = str(outs[1]) if len(outs)==2 else None
    if y.get("quote_bnb") is not None:
        y["quote_ge_2x_gas"] = (gp is not None and y["quote_bnb"] >= 2*gp*300000/1e18)
        y["status"] = "executable_candidate" if y["quote_ge_2x_gas"] else "quote_dust"
    else:
        y["status"] = "no_quote"
else:
    y["status"] = "no_quote"
out["YYDS"] = y
print(json.dumps(out, indent=1))
