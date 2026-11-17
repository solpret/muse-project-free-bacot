#!/usr/bin/env python3
import json, urllib.request
from eth_abi import encode, decode
from eth_utils import keccak
W = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
ROUTER = "0x10ED43C718714eb63d5aA57B78B54704E256024E"
FACTORY = "0xca143ce32fe78f1f7019d7d551a6402fc5350c73"
WBNB = "0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c"
ENDPOINTS = ["https://bsc-dataseed1.defibit.io/", "https://bsc-dataseed1.ninicoin.io/",
             "https://bsc-dataseed.bnbchain.org/", "https://rpc.ankr.com/bsc", "https://bsc-dataseed.binance.org/"]
def sel(sig): return keccak(text=sig).hex()[:8]
def rpc(url, calls):
    batch = [{"jsonrpc": "2.0", "id": i+1, "method": m, "params": p} for i, (m, p) in enumerate(calls)]
    req = urllib.request.Request(url, data=json.dumps(batch).encode(), headers={"Content-Type": "application/json"})
    try: res = json.loads(urllib.request.urlopen(req, timeout=20).read())
    except Exception as e: return [None]*len(calls), str(e)
    out = []
    for r in res:
        if isinstance(r, dict) and (r.get("error") or not r.get("result")): out.append(None)
        elif isinstance(r, dict): out.append(r["result"])
        else: out.append(None)
    return out, None
def call_multi(to, data):
    for url in ENDPOINTS:
        r, _ = rpc(url, [("eth_call", [{"to": to, "data": data}, "latest"])])
        if r[0]: return r[0], url
    return None, None
def u256(h):
    try: return int(h, 16) if h else 0
    except Exception: return 0
out = {}
# 币安加油 balance retry
tok = "0x397BF425926F521Ac5BEbe5062793BB224e3eF8f"
bal_h, url = call_multi(tok, "0x" + sel("balanceOf(address)") + encode(["address"], [W]).hex())
item = {"symbol": "币安加油", "rpc_url": url}
if bal_h is None:
    item["status"] = "rpc_failed_balance"
else:
    bal = u256(bal_h); item["balance_raw"] = str(bal); item["balance_human"] = bal/1e18
    pair_h, _ = call_multi(FACTORY, "0x" + sel("getPair(address,address)") + encode(["address","address"], [tok, WBNB]).hex())
    pair = ("0x" + pair_h[-40:]) if pair_h and u256(pair_h) else None
    item["pair_wbnb"] = pair; item["status"] = "no_pair" if not pair else "pair_exists"
out["币安加油"] = item
# YYDS quote: sell full balance 177600000000000
yyds = "0xd23be069c3c3a7f631af52584a16a9e46bb41da1"
q_h, qurl = call_multi(ROUTER, "0x" + sel("getAmountsOut(uint256,address[])") + encode(["uint256","address[]"], [177600000000000, [yyds, WBNB]]).hex())
qitem = {"symbol": "YYDS", "rpc_url": qurl}
if q_h:
    try:
        outs = decode(["uint256[]"], bytes.fromhex(q_h[2:]))[0]
        qitem["quote_raw"] = str(outs[1]); qitem["quote_bnb"] = outs[1]/1e18
    except Exception as ex: qitem["quote_error"] = str(ex)
else:
    qitem["status"] = "no_quote"
# fresh gas price
gp, gpurl = call_multi(None, None) if False else (None, None)
for url in ENDPOINTS:
    r, _ = rpc(url, [("eth_gasPrice", [])])
    if r[0]:
        gp = u256(r[0]); qitem["gas_price_gwei"] = gp/1e9; qitem["gas_est_300k_bnb"] = gp*300000/1e18; qitem["gas_rpc"] = url
        break
out["YYDS_quote"] = qitem
print(json.dumps(out, indent=1, ensure_ascii=False))
