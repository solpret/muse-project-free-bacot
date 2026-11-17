#!/usr/bin/env python3
"""Retry for pending-swap check 2351 Nov 16: re-read only entries whose
balance read failed, plus LUCKY777 pair (returned 0x0 vs 0x81af... at 22:51)
and JINMA reserves/quote, using fallback RPC endpoints."""
import json, urllib.request, time
from eth_abi import encode, decode
from eth_utils import keccak

W = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
ROUTER = "0x10ED43C718714eb63d5aA57B78B54704E256024E"
FACTORY = "0xca143ce32fe78f1f7019d7d551a6402fc5350c73"
WBNB = "0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c"
ENDPOINTS = ["https://bsc-dataseed1.binance.org/",
             "https://bsc-dataseed2.binance.org/",
             "https://bsc-dataseed1.defibit.io/"]

def sel(sig):
    return keccak(text=sig).hex()[:8]

def rpc_batch(calls, url):
    batch = [{"jsonrpc": "2.0", "id": i + 1, "method": m, "params": p}
             for i, (m, p) in enumerate(calls)]
    req = urllib.request.Request(url, data=json.dumps(batch).encode(),
                                 headers={"Content-Type": "application/json"})
    res = json.loads(urllib.request.urlopen(req, timeout=30).read())
    out = []
    for r in res:
        if isinstance(r, dict) and (r.get("error") or not r.get("result")):
            out.append(None)
        elif isinstance(r, dict):
            out.append(r["result"])
        else:
            out.append(None)
    return out

def rpc_with_fallback(calls):
    last_err = None
    for url in ENDPOINTS:
        try:
            out = rpc_batch(calls, url)
            if any(o is not None for o in out):
                return out, url, None
            last_err = "all None from " + url
        except Exception as e:
            last_err = str(e) + " @ " + url
            time.sleep(1)
    return [None] * len(calls), None, last_err

def u256(h):
    try:
        return int(h, 16) if h else 0
    except Exception:
        return 0

def main():
    data = json.load(open("/home/hatch/workspace/asset-sell-watch/pending-swaps.json"))
    prev = json.load(open("/home/hatch/workspace/asset-sell-watch/pending_check_2351_nov16_stdout.json"))
    prev_by_sym = {e["symbol"]: e for e in prev["entries"]}
    retry_syms = {"BNBbaby", "PATCH", "YYDS", "币安加油", "ORBITA", "MALTA",
                  "THYRK", "WNO", "CHEEMSA", "NEB", "LUCKY777", "JINMA"}
    gp, url, gp_err = rpc_with_fallback([("eth_gasPrice", [])])
    gas_price = u256(gp[0]) if gp and gp[0] else None
    out = {"endpoint_used": url, "gas_price_wei": gas_price,
           "gas_price_gwei": (gas_price / 1e9 if gas_price else None),
           "gas_est_300k_bnb": (gas_price * 300000 / 1e18 if gas_price else None),
           "gas_err": gp_err, "entries": []}
    for e in data["entries"]:
        if e["symbol"] not in retry_syms:
            continue
        tok = e["token"]; sym = e["symbol"]
        item = {"symbol": sym, "token": tok, "prev_status": prev_by_sym[sym]["status"]}
        bal_h, = rpc_with_fallback([("eth_call", [{"to": tok, "data": "0x" + sel("balanceOf(address)") + encode(["address"], [W]).hex()}, "latest"])])[0:1] if False else (None,)
        # simple single-call path with fallback
        res, used, err = rpc_with_fallback([("eth_call", [{"to": tok, "data": "0x" + sel("balanceOf(address)") + encode(["address"], [W]).hex()}, "latest"])])
        bal_h = res[0]
        item["endpoint"] = used; item["err"] = err
        if bal_h is None:
            item["status"] = "rpc_failed_balance"; out["entries"].append(item); continue
        bal = u256(bal_h)
        item["balance_raw"] = str(bal); item["balance_human"] = bal / 1e18
        if bal == 0:
            item["status"] = "empty"; out["entries"].append(item); continue
        res, _, _ = rpc_with_fallback([("eth_call", [{"to": FACTORY, "data": "0x" + sel("getPair(address,address)") + encode(["address", "address"], [tok, WBNB]).hex()}, "latest"])])
        pair_h = res[0]
        pair = ("0x" + pair_h[-40:]) if pair_h and u256(pair_h) else None
        item["pair_wbnb"] = pair
        if not pair:
            item["status"] = "no_pair"; out["entries"].append(item); continue
        res, _, _ = rpc_with_fallback([("eth_call", [{"to": pair, "data": "0x" + sel("getReserves()")}, "latest"])])
        if res[0]:
            try:
                r0, r1, _ = decode(["uint112", "uint112", "uint32"], bytes.fromhex(res[0][2:]))
                item["reserves"] = [str(r0), str(r1)]
                if r0 == 0 or r1 == 0:
                    item["status"] = "pair_empty"; out["entries"].append(item); continue
            except Exception as ex:
                item["reserves_error"] = str(ex)
        sell_amt = int(e["amount_to_sell_raw"]) if e.get("amount_to_sell_raw") else bal
        item["sell_amount_raw"] = str(sell_amt)
        res, _, _ = rpc_with_fallback([("eth_call", [{"to": ROUTER, "data": "0x" + sel("getAmountsOut(uint256,address[])") + encode(["uint256", "address[]"], [sell_amt, [tok, WBNB]]).hex()}, "latest"])])
        if res[0]:
            try:
                outs = decode(["uint256[]"], bytes.fromhex(res[0][2:]))[0]
                item["quote_bnb"] = outs[1] / 1e18 if len(outs) == 2 else None
                item["quote_raw"] = str(outs[1]) if len(outs) == 2 else None
            except Exception as ex:
                item["quote_error"] = str(ex)
        if item.get("quote_bnb") is not None:
            q = item["quote_bnb"]
            ge = out["gas_est_300k_bnb"]
            item["quote_ge_2x_gas"] = (ge is not None and q >= 2 * ge)
            item["status"] = "executable_candidate" if item["quote_ge_2x_gas"] else "quote_dust"
        else:
            item["status"] = "no_quote"
        out["entries"].append(item)
    print(json.dumps(out, indent=1))

if __name__ == "__main__":
    main()
