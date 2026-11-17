#!/usr/bin/env python3
"""Lean targeted retry for pending-coin-swap-watch 2026-11-08 10:51 WIB.
Single RPC (dataseed1), 10s timeout. ORBITA balance + pair/quote if >0;
launched()/phase() for all 9 sale contracts (reverts return fast as errors).
Read-only."""
import json, urllib.request
from eth_abi import encode, decode
from eth_utils import keccak

W = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
ROUTER = "0x10ED43C718714eb63d5aA57B78B54704E256024E"
FACTORY = "0xca143ce32fe78f1f7019d7d551a6402fc5350c73"
WBNB = "0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c"
RPC = "https://bsc-dataseed1.binance.org/"

def sel(sig): return keccak(text=sig).hex()[:8]
def call(to, data):
    body = json.dumps({"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":to,"data":data},"latest"]}).encode()
    req = urllib.request.Request(RPC, data=body, headers={"Content-Type":"application/json"})
    try:
        r = json.loads(urllib.request.urlopen(req, timeout=10).read())
    except Exception as e:
        return None, str(e)
    if r.get("error") or not r.get("result"): return None, "error_or_empty"
    return r["result"], None
def u256(h): return int(h,16) if h else 0

out = {}
gp = None
try:
    body = json.dumps({"jsonrpc":"2.0","id":1,"method":"eth_gasPrice","params":[]}).encode()
    req = urllib.request.Request(RPC, data=body, headers={"Content-Type":"application/json"})
    r = json.loads(urllib.request.urlopen(req, timeout=10).read())
    if r.get("result"): gp = int(r["result"],16)
except Exception: pass
out["gas_price_gwei"] = gp/1e9 if gp else None
out["gas_2x_threshold_bnb"] = 2*gp*300000/1e18 if gp else None

tok = "0x19b8d7613A6C2E4168a6a0Bb97ca0c842035d709"
item = {}
bal_h, err = call(tok, "0x"+sel("balanceOf(address)")+encode(["address"],[W]).hex())
if bal_h is None:
    item["status"] = "rpc_failed_balance"; item["error"] = err
else:
    bal = u256(bal_h)
    item["balance_raw"] = str(bal); item["balance_human"] = bal/1e18
    if bal == 0:
        item["status"] = "empty"
    else:
        pair_h, _ = call(FACTORY, "0x"+sel("getPair(address,address)")+encode(["address","address"],[tok,WBNB]).hex())
        pair = ("0x"+pair_h[-40:]) if pair_h and u256(pair_h) else None
        item["pair_wbnb"] = pair
        if not pair:
            item["status"] = "no_pair"
        else:
            res_h, _ = call(pair, "0x"+sel("getReserves()"))
            if res_h:
                r0, r1, _ = decode(["uint112","uint112","uint32"], bytes.fromhex(res_h[2:]))
                item["reserves"] = [str(r0), str(r1)]
                if r0 == 0 or r1 == 0:
                    item["status"] = "pair_empty"
                else:
                    q_h, _ = call(ROUTER, "0x"+sel("getAmountsOut(uint256,address[])")+encode(["uint256","address[]"],[1000000000000000000000000,[tok,WBNB]]).hex())
                    if q_h:
                        outs = decode(["uint256[]"], bytes.fromhex(q_h[2:]))[0]
                        item["quote_bnb"] = outs[1]/1e18 if len(outs)==2 else None
                        item["quote_ge_2x_gas"] = (gp is not None and item["quote_bnb"] is not None and item["quote_bnb"] >= 2*gp*300000/1e18)
                        item["status"] = "executable_candidate" if item["quote_ge_2x_gas"] else "quote_dust"
                    else:
                        item["status"] = "no_quote"
            else:
                item["status"] = "reserves_failed"
out["ORBITA"] = item

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
    entry = {}
    lh, _ = call(sc, "0x"+sel("launched()"))
    entry["launched_raw"] = lh
    if lh:
        try: entry["launched"] = decode(["bool"], bytes.fromhex(lh[2:]))[0]
        except Exception: entry["launched"] = None
    ph, _ = call(sc, "0x"+sel("phase()"))
    entry["phase_raw"] = ph
    if ph:
        try: entry["phase"] = decode(["uint256"], bytes.fromhex(ph[2:]))[0]
        except Exception: entry["phase"] = None
    sc_out[sym] = entry
out["sale_contracts"] = sc_out
print(json.dumps(out, indent=1))
