#!/usr/bin/env python3
"""Retry read-only check for entries that failed RPC in pending_check_2151_nov11.
Uses alternate RPC endpoint bsc-dataseed1.bnbchain.org. No execution."""
import json, urllib.request
from eth_abi import encode, decode
from eth_utils import keccak

W = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
ROUTER = "0x10ED43C718714eb63d5aA57B78B54704E256024E"
FACTORY = "0xca143ce32fe78f1f7019d7d551a6402fc5350c73"
WBNB = "0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c"
URL = "https://bsc-dataseed1.bnbchain.org/"

def sel(sig):
    return keccak(text=sig).hex()[:8]

def rpc_batch(calls, url=URL):
    batch = [{"jsonrpc": "2.0", "id": i + 1, "method": m, "params": p}
             for i, (m, p) in enumerate(calls)]
    req = urllib.request.Request(url, data=json.dumps(batch).encode(),
                                 headers={"Content-Type": "application/json"})
    try:
        res = json.loads(urllib.request.urlopen(req, timeout=20).read())
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

TOKENS = [
    ("PATCH", "0xBbA053567846842F95C060867a5C9eb6b3983c80", None),
    ("QAGENT", "0x25e915EEE91411b0AC3273531dbaDc34e0EAA5eB", None),
    ("WW3", "0xf62628D99B28535ee593Ab5D6dFE7D914f5edca0", "10000000000000000000000"),
    ("BITCAT", "0x8708EE82fa34c58431532323530592ee3953e9d5", "37777777600000000000"),
    ("WNO", "0x8C969a4CD49E4774908e667702C3d7C3ece164D0", "1000000000000000000000000"),
    ("AMBR", "0x88B06f59BdB54039AEBf1d308d8B9181a90385c1", "10000000000000000000000"),
    ("CSAGENT", "0xeD290fA2e34233d0ee97eA95C2a34E770A9DA45D", "100000000000000000000000"),
    ("CHEEMSA", "0x00b4bdA5BBf83A72f1252CCEf361f107f5a728b2", "5000000000000000000000000"),
    # recheck pair for 币安加油 (pair read failed in main run, was pair_empty at 20:51)
    ("币安加油", "0x397BF425926F521Ac5BEbe5062793BB224e3eF8f", "50000000000000000000000000"),
]

def main():
    gp, gp_err = rpc_batch([("eth_gasPrice", [])])
    gas_price = u256(gp[0]) if gp and gp[0] else None
    gas_est = (gas_price * 300000 / 1e18) if gas_price else None
    out = {"rpc": URL, "gas_price_gwei": (gas_price / 1e9 if gas_price else None),
           "gas_est_300k_bnb": gas_est, "gas_err": gp_err, "entries": []}
    for sym, tok, sell_raw in TOKENS:
        item = {"symbol": sym, "token": tok}
        bal_h = call(tok, "0x" + sel("balanceOf(address)") + encode(["address"], [W]).hex())
        if bal_h is None:
            item["status"] = "rpc_failed_balance"; out["entries"].append(item); continue
        dec_h = call(tok, "0x" + sel("decimals()"))
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
        t0_h = call(pair, "0x" + sel("token0()"))
        if res_h:
            try:
                r0, r1, _ = decode(["uint112", "uint112", "uint32"], bytes.fromhex(res_h[2:]))
                item["reserves"] = [str(r0), str(r1)]
                item["token0"] = ("0x" + t0_h[-40:]) if t0_h else None
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
        if item.get("quote_bnb") is not None:
            item["quote_ge_2x_gas"] = (gas_est is not None and item["quote_bnb"] >= 2 * gas_est)
            item["status"] = "executable_candidate" if item["quote_ge_2x_gas"] else "quote_dust"
        else:
            item["status"] = "no_quote"
        out["entries"].append(item)
    print(json.dumps(out, indent=1))

if __name__ == "__main__":
    main()
