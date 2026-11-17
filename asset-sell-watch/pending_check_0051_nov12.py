#!/usr/bin/env python3
"""pending-coin-swap-watch run 2026-11-12 00:51 WIB. Read-only: balanceOf
(agent wallet 0xeb23), PCS V2 getPair, reserves, getAmountsOut, gas price,
plus sale-state spot checks (CSAGENT pair opened(), CHEEMSA tradingOpen())."""
import json, urllib.request
from eth_abi import encode, decode
from eth_utils import keccak

W = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
ROUTER = "0x10ED43C718714eb63d5aA57B78B54704E256024E"
FACTORY = "0xca143ce32fe78f1f7019d7d551a6402fc5350c73"
WBNB = "0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c"

def sel(sig):
    return keccak(text=sig).hex()[:8]

ENDPOINTS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.binance.org/",
             "https://bsc-dataseed2.binance.org/", "https://bsc-dataseed3.binance.org/",
             "https://bsc-dataseed4.binance.org/", "https://bsc.publicnode.com",
             "https://bsc.meowrpc.com"]

def rpc_batch(calls):
    batch = [{"jsonrpc": "2.0", "id": i + 1, "method": m, "params": p}
             for i, (m, p) in enumerate(calls)]
    last_err = None
    for url in ENDPOINTS:
        req = urllib.request.Request(url, data=json.dumps(batch).encode(),
                                     headers={"Content-Type": "application/json"})
        try:
            res = json.loads(urllib.request.urlopen(req, timeout=30).read())
            break
        except Exception as e:
            last_err = str(e); res = None
    if res is None:
        return [None] * len(calls), last_err
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

ENTRIES = [
    ("POA", "0x21bc810818d9c9c767ba73c543f67a989fb5a543", 18, 28000000000000000000000, None),
    ("BNBbaby", "0xd0079025a9bb66a7a1de991de2e4326faba35729", 18, None, None),
    ("PATCH", "0xBbA053567846842F95C060867a5C9eb6b3983c80", 18, None, None),
    ("QAGENT", "0x25e915EEE91411b0AC3273531dbaDc34e0EAA5eB", 18, None, None),
    ("YYDS", "0xd23be069c3c3a7f631af52584a16a9e46bb41da1", 18, None, "0xD15c928B7b777CaC7d613FE840C6eC3dE8e4EdDA"),
    ("币安加油", "0x397BF425926F521Ac5BEbe5062793BB224e3eF8f", 18, 50000000000000000000000000, "0xc939e2b49eea548c4539e45b4e355c2b2aa464d6"),
    ("PACTURE", "0x10b80088fDAf9363d83671BE66b64f231f9e92f6", 18, 10000000000000000000000000, None),
    ("ORBITA", "0x19b8d7613A6C2E4168a6a0Bb97ca0c842035d709", 18, 1000000000000000000000000, None),
    ("WW3", "0xf62628D99B28535ee593Ab5D6dFE7D914f5edca0", 18, 10000000000000000000000, None),
    ("POSTAGE", "0x6C310EABEdFD4eEd6148bf2C07241FB45a52FB42", 18, 10000000000000000000000, None),
    ("MALTA", "0x728095Ab0BD71636Db5DA4E2A6d7f5cc73729fc0", 18, 1000000000000000000000000, None),
    ("JINMA", "0xe4517E6718b24D5725956ac7A90686592a7b1539", 18, 50000000000000000000000000, "0xaa91fd1b1fc70888f5df17784720b752472e99da"),
    ("THYRK", "0x3b8747D067B2Ed8565330667128260C2a4954300", 18, 20000000000000000000, None),
    ("BITCAT", "0x8708EE82fa34c58431532323530592ee3953e9d5", 9, 37777777600000000000, "0x8dD64bb9F614D58716eB0e343e1F794B2E7A04f4"),
    ("LUCKY777", "0xc6D4ec8CB889aFBa9f251606001457644E260f7D", 18, 50000000000000000000000000, "0x81afde1cddf0d277580b8e524361e0a7ea2983c6"),
    ("WNO", "0x8C969a4CD49E4774908e667702C3d7C3ece164D0", 18, 1000000000000000000000000, None),
    ("AMBR", "0x88B06f59BdB54039AEBf1d308d8B9181a90385c1", 18, 10000000000000000000000, None),
    ("CSAGENT", "0xeD290fA2e34233d0ee97eA95C2a34E770A9DA45D", 18, 100000000000000000000000, "0x3020220Ca11BaE3F027C0DC8A3b8Bb73D5b55A00"),
    ("CHEEMSA", "0x00b4bdA5BBf83A72f1252CCEf361f107f5a728b2", 18, 5000000000000000000000000, None),
    ("NEB", "0xf08ac9c91dcfc5b74eae6c87e744cfefe0d32a68", 18, 1000000000000000000000, None),
]

def main():
    gp, _ = rpc_batch([("eth_gasPrice", [])])
    gas_price = u256(gp[0]) if gp and gp[0] else None
    gas_est = (gas_price * 300000 / 1e18) if gas_price else None
    out = {"run": "2026-11-12 00:51 WIB", "gas_price_gwei": (gas_price/1e9 if gas_price else None),
           "gas_est_300k_bnb": gas_est, "entries": []}
    for sym, tok, dec, amt, pair_known in ENTRIES:
        item = {"symbol": sym, "token": tok}
        bal_h = call(tok, "0x" + sel("balanceOf(address)") + encode(["address"], [W]).hex())
        if bal_h is None:
            item["status"] = "rpc_failed_balance"; out["entries"].append(item); continue
        bal = u256(bal_h)
        item["balance_raw"] = str(bal); item["balance_human"] = bal / (10**dec)
        if bal == 0:
            item["status"] = "empty"; out["entries"].append(item); continue
        pair_h = call(FACTORY, "0x" + sel("getPair(address,address)") + encode(["address", "address"], [tok, WBNB]).hex())
        pair = ("0x" + pair_h[-40:]) if pair_h and u256(pair_h) else None
        if not pair:
            pair = pair_known
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
        else:
            item["status"] = "rpc_failed_reserves"; out["entries"].append(item); continue
        sell_amt = amt if amt is not None else bal
        item["sell_amount_raw"] = str(sell_amt)
        q_h = call(ROUTER, "0x" + sel("getAmountsOut(uint256,address[])") + encode(["uint256", "address[]"], [sell_amt, [tok, WBNB]]).hex())
        if q_h:
            try:
                outs = decode(["uint256[]"], bytes.fromhex(q_h[2:]))[0]
                item["quote_bnb"] = outs[1] / 1e18 if len(outs) == 2 else None
            except Exception as ex:
                item["quote_error"] = str(ex)
        if item.get("quote_bnb") is not None:
            q = item["quote_bnb"]
            item["quote_ge_2x_gas"] = (gas_est is not None and q >= 2 * gas_est)
            item["status"] = "executable_candidate" if item["quote_ge_2x_gas"] else "quote_dust"
        else:
            item["status"] = "no_quote"
        out["entries"].append(item)
    # Sale-state spot checks (best effort; failed read = null, NOT treated as false)
    sale_checks = {}
    try:
        h = call("0x3020220Ca11BaE3F027C0DC8A3b8Bb73D5b55A00", "0x" + sel("opened()"))
        sale_checks["CSAGENT_pair_opened"] = (u256(h) != 0) if h else None
    except Exception as e:
        sale_checks["CSAGENT_opened_error"] = str(e)
    try:
        h = call("0x00b4bdA5BBf83A72f1252CCEf361f107f5a728b2", "0x" + sel("tradingOpen()"))
        sale_checks["CHEEMSA_tradingOpen"] = (u256(h) != 0) if h else None
    except Exception as e:
        sale_checks["CHEEMSA_tradingOpen_error"] = str(e)
    out["sale_state_checks"] = sale_checks
    print(json.dumps(out, indent=1))

if __name__ == "__main__":
    main()
