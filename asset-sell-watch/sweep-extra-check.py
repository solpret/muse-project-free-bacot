#!/usr/bin/env python3
"""Read-only sweep check for EXTRA wallet-held tokens not in pending-swaps.json
(Amber, MOTA, MWGL, STOCKMEMES, CAIBAO). Same logic as pending_check.py:
balance, decimals, getPair WBNB, reserves, getAmountsOut quote, quote >= 2x gas."""
import json, urllib.request
from eth_abi import encode, decode
from eth_utils import keccak

W = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
ROUTER = "0x10ED43C718714eb63d5aA57B78B54704E256024E"
FACTORY = "0xca143ce32fe78f1f7019d7d551a6402fc5350c73"
WBNB = "0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c"
TOKENS = [
    ("Amber", "0x4008a353d3476884DC8Cd8fBf314970C8409FB22"),
    ("MOTA", "0xfdd44c29af794249318930cebbf9cc3dfff9e4b1"),
    ("MWGL", "0x458ba0b810ff314b1d7d41a0f0f209706dcf949b"),
    ("STOCKMEMES", "0x8c36223b4f460521ca49d2ce43a1b60c8185ba80"),
    ("CAIBAO", "0x33d612C10b509aBD8723b7E0E11e1CFFB02f5a27"),
]

def sel(sig):
    return keccak(text=sig).hex()[:8]

def rpc_batch(calls):
    url = "https://bsc-dataseed.binance.org/"
    batch = [{"jsonrpc": "2.0", "id": i + 1, "method": m, "params": p}
             for i, (m, p) in enumerate(calls)]
    req = urllib.request.Request(url, data=json.dumps(batch).encode(),
                                 headers={"Content-Type": "application/json"})
    try:
        res = json.loads(urllib.request.urlopen(req, timeout=30).read())
    except Exception as e:
        return [None] * len(calls), str(e)
    out = []
    for r in res:
        if isinstance(r, dict) and (r.get("error") or not r.get("result")):
            out.append(None)
        elif isinstance(r, dict):
            out.append(r["result"])
        else:
            out.append(None)
    return out, None

def call(to, data):
    r, _ = rpc_batch([("eth_call", [{"to": to, "data": data}, "latest"])])
    return r[0]

def u256(h):
    try:
        return int(h, 16) if h else 0
    except Exception:
        return 0

def main():
    gp, _ = rpc_batch([("eth_gasPrice", [])])
    gas_price = u256(gp[0]) if gp and gp[0] else None
    gas_est_bnb = (gas_price * 300000 / 1e18) if gas_price else None
    out = {"gas_price_gwei": (gas_price / 1e9 if gas_price else None),
           "gas_est_300k_bnb": gas_est_bnb, "entries": []}
    for sym, tok in TOKENS:
        item = {"symbol": sym, "token": tok}
        bal_h = call(tok, "0x" + sel("balanceOf(address)") + encode(["address"], [W]).hex())
        dec_h = call(tok, "0x" + sel("decimals()"))
        if bal_h is None:
            item["status"] = "rpc_failed_balance"; out["entries"].append(item); continue
        bal = u256(bal_h); dec = u256(dec_h) if dec_h else 18
        item["balance_raw"] = str(bal); item["balance_human"] = bal / (10 ** dec) if dec < 40 else None
        item["decimals"] = dec
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
        q_h = call(ROUTER, "0x" + sel("getAmountsOut(uint256,address[])") + encode(["uint256", "address[]"], [bal, [tok, WBNB]]).hex())
        if q_h:
            try:
                outs = decode(["uint256[]"], bytes.fromhex(q_h[2:]))[0]
                item["quote_bnb"] = outs[1] / 1e18 if len(outs) == 2 else None
                item["quote_raw"] = str(outs[1]) if len(outs) == 2 else None
            except Exception as ex:
                item["quote_error"] = str(ex)
        if item.get("quote_bnb") is not None:
            q = item["quote_bnb"]
            item["quote_ge_2x_gas"] = (gas_est_bnb is not None and q >= 2 * gas_est_bnb)
            item["status"] = "executable_candidate" if item["quote_ge_2x_gas"] else "quote_dust"
        else:
            item["status"] = "no_quote"
        out["entries"].append(item)
    print(json.dumps(out, indent=1))

if __name__ == "__main__":
    main()
