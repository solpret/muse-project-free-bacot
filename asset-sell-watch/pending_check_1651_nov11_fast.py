#!/usr/bin/env python3
"""Fast threaded full pending-swap check run 16:51 Nov 11 — all 20 entries.
Publicnode primary, dataseed1 fallback, 12s timeouts, 5 threads, incremental
writes so a hang does not lose completed work. Read-only."""
import json, urllib.request, threading
from concurrent.futures import ThreadPoolExecutor
from eth_abi import encode, decode
from eth_utils import keccak

W = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
ROUTER = "0x10ED43C718714eb63d5aA57B78B54704E256024E"
FACTORY = "0xca143ce32fe78f1f7019d7d551a6402fc5350c73"
WBNB = "0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c"
URLS = ["https://bsc.publicnode.com/", "https://bsc-dataseed1.binance.org/"]
OUT = "/home/hatch/workspace/asset-sell-watch/pending_check_1651_nov11_stdout.json"
LOCK = threading.Lock()

def sel(sig):
    return keccak(text=sig).hex()[:8]

def call(to, data, timeout=12):
    last_err = None
    for url in URLS:
        body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                           "params": [{"to": to, "data": data}, "latest"]}).encode()
        req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"})
        try:
            res = json.loads(urllib.request.urlopen(req, timeout=timeout).read())
        except Exception as e:
            last_err = str(e); continue
        if isinstance(res, dict) and (res.get("error") or not res.get("result")):
            last_err = str(res.get("error")); continue
        return res.get("result"), url, None
    return None, None, last_err

def u256(h):
    try:
        return int(h, 16) if h else 0
    except Exception:
        return 0

def check(e, gas_est):
    tok = e["token"]; sym = e["symbol"]
    item = {"symbol": sym, "token": tok, "registered_amount_human": e.get("amount_human"),
            "amount_to_sell_raw": e.get("amount_to_sell_raw"), "reason_prev": e.get("reason")}
    bal_h, bal_ep, bal_err = call(tok, "0x" + sel("balanceOf(address)") + encode(["address"], [W]).hex())
    dec_h, _, _ = call(tok, "0x" + sel("decimals()"))
    if bal_h is None:
        item["status"] = "rpc_failed_balance"; item["balance_error"] = bal_err
        return item
    bal = u256(bal_h); dec = u256(dec_h) if dec_h else 18
    item["balance_raw"] = str(bal); item["balance_human"] = bal / (10**dec) if dec < 40 else None
    item["decimals"] = dec; item["balance_endpoint"] = bal_ep
    if bal == 0:
        item["status"] = "empty"; return item
    pair_h, pair_ep, _ = call(FACTORY, "0x" + sel("getPair(address,address)") + encode(["address", "address"], [tok, WBNB]).hex())
    pair = ("0x" + pair_h[-40:]) if pair_h and u256(pair_h) else None
    item["pair_wbnb"] = pair; item["pair_endpoint"] = pair_ep
    if not pair:
        item["status"] = "no_pair"; return item
    t0_h, _, _ = call(pair, "0x" + sel("token0()"))
    t1_h, _, _ = call(pair, "0x" + sel("token1()"))
    res_h, _, res_err = call(pair, "0x" + sel("getReserves()"))
    if res_h:
        try:
            r0, r1, _ = decode(["uint112", "uint112", "uint32"], bytes.fromhex(res_h[2:]))
            item["reserves"] = [str(r0), str(r1)]
            item["token0"] = ("0x" + t0_h[-40:]) if t0_h else None
            item["token1"] = ("0x" + t1_h[-40:]) if t1_h else None
            if r0 == 0 or r1 == 0:
                item["status"] = "pair_empty"; return item
        except Exception as ex:
            item["reserves_error"] = str(ex)
    else:
        item["reserves_error"] = res_err
    sell_amt = int(e["amount_to_sell_raw"]) if e.get("amount_to_sell_raw") else bal
    item["sell_amount_raw"] = str(sell_amt)
    q_h, q_ep, q_err = call(ROUTER, "0x" + sel("getAmountsOut(uint256,address[])") + encode(["uint256", "address[]"], [sell_amt, [tok, WBNB]]).hex())
    if q_h:
        try:
            outs = decode(["uint256[]"], bytes.fromhex(q_h[2:]))[0]
            item["quote_bnb"] = outs[1] / 1e18 if len(outs) == 2 else None
            item["quote_raw"] = str(outs[1]) if len(outs) == 2 else None
            item["quote_endpoint"] = q_ep
        except Exception as ex:
            item["quote_error"] = str(ex)
    else:
        item["quote_error"] = q_err
    if item.get("quote_bnb") is not None:
        q = item["quote_bnb"]
        item["quote_ge_2x_gas"] = (gas_est is not None and q >= 2 * gas_est)
        item["status"] = "executable_candidate" if item["quote_ge_2x_gas"] else "quote_dust"
    else:
        item["status"] = "no_quote"
    sc = e.get("sale_contract")
    if sc:
        lh, _, _ = call(sc, "0x" + sel("launched()"))
        item["sale_contract"] = sc; item["launched_raw"] = lh
        if lh is not None:
            try:
                item["launched"] = decode(["bool"], bytes.fromhex(lh[2:]))[0]
            except Exception:
                item["launched"] = None
    return item

def gas_price():
    for url in URLS:
        body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_gasPrice", "params": []}).encode()
        req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"})
        try:
            res = json.loads(urllib.request.urlopen(req, timeout=12).read())
            if res.get("result"):
                return u256(res["result"]), url
        except Exception:
            continue
    return None, None

def main():
    data = json.load(open("/home/hatch/workspace/asset-sell-watch/pending-swaps.json"))
    gp, gp_ep = gas_price()
    gas_est = (gp * 300000 / 1e18) if gp else None
    out = {"gas_price_wei": gp, "gas_price_gwei": (gp / 1e9 if gp else None),
           "gas_est_300k_bnb": gas_est, "gas_endpoint": gp_ep, "entries": []}
    json.dump(out, open(OUT, "w"), indent=1)
    print("gas:", gp, "gwei:", (gp / 1e9 if gp else None), "est300k:", gas_est, "ep:", gp_ep, flush=True)
    def work(e):
        item = check(e, gas_est)
        with LOCK:
            out["entries"].append(item)
            json.dump(out, open(OUT, "w"), indent=1)
        print(item["symbol"], "->", item.get("status"), "| bal:", item.get("balance_human"),
              "| pair:", item.get("pair_wbnb"), "| reserves:", item.get("reserves"),
              "| quote:", item.get("quote_bnb"), "| launched:", item.get("launched"), flush=True)
        return item
    with ThreadPoolExecutor(max_workers=5) as ex:
        list(ex.map(work, data["entries"]))
    print("DONE")

if __name__ == "__main__":
    main()
