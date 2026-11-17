#!/usr/bin/env python3
"""Read-only pending-swap check run 2026-11-16 19:51 WIB (v2).
Few large urllib batches to https://bsc-rpc.publicnode.com/ with
progress prints. No audit, no preview, no execution."""
import sys, json, urllib.request
from eth_abi import encode, decode
from eth_utils import keccak

W = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
ROUTER = "0x10ED43C718714eb63d5aA57B78B54704E256024E"
FACTORY = "0xca143ce32fe78f1f7019d7d551a6402fc5350c73"
WBNB = "0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c"
URL = "https://bsc-dataseed.binance.org/"
CHUNK = 8

def sel(sig):
    return keccak(text=sig).hex()[:8]

def u256(h):
    try:
        return int(h, 16) if h else 0
    except Exception:
        return 0

def _batch_once(calls, start_id=1):
    payload = [{"jsonrpc": "2.0", "id": start_id + i, "method": m, "params": p}
               for i, (m, p) in enumerate(calls)]
    req = urllib.request.Request(URL, data=json.dumps(payload).encode(),
                                 headers={"Content-Type": "application/json"})
    raw = urllib.request.urlopen(req, timeout=25).read()
    res = json.loads(raw)
    out = [None] * len(calls)
    if isinstance(res, list):
        for r in res:
            if isinstance(r, dict) and r.get("id") is not None:
                idx = r["id"] - start_id
                if 0 <= idx < len(calls):
                    if r.get("error") or not r.get("result"):
                        out[idx] = None
                    else:
                        out[idx] = r["result"]
    return out

def batch(calls):
    """Chunked batches with retry on 429."""
    import time as _time
    out = []
    for s in range(0, len(calls), CHUNK):
        chunk = calls[s:s + CHUNK]
        got = None
        for attempt in range(4):
            try:
                got = _batch_once(chunk, start_id=1)
                break
            except Exception as e:
                print(f"[batch] chunk@{s} attempt {attempt+1} error: {e}", flush=True)
                _time.sleep(2 * (attempt + 1))
        out.extend(got if got is not None else [None] * len(chunk))
    return out

def ec(to, data):
    return ("eth_call", [{"to": to, "data": data}, "latest"])

def main():
    data = json.load(open("/home/hatch/workspace/asset-sell-watch/pending-swaps.json"))
    entries = data["entries"]
    out = {"run": "2026-11-16 19:51 WIB", "endpoint": URL, "entries": []}
    gp = batch([("eth_gasPrice", [])])[0]
    gas_price = u256(gp) if gp else None
    out["gas_price_wei"] = gas_price
    out["gas_price_gwei"] = (gas_price / 1e9) if gas_price else None
    out["gas_est_300k_bnb"] = (gas_price * 300000 / 1e18) if gas_price else None
    print(f"[stage] gasPrice={gas_price}", flush=True)

    calls = []
    for e in entries:
        tok = e["token"]
        calls.append(ec(tok, "0x" + sel("balanceOf(address)") + encode(["address"], [W]).hex()))
        calls.append(ec(tok, "0x" + sel("decimals()")))
    res = batch(calls)
    print(f"[stage] balances done ({len(calls)} calls)", flush=True)
    bals, decs = {}, {}
    for i, e in enumerate(entries):
        bals[e["symbol"]] = u256(res[2*i]) if res[2*i] else None
        decs[e["symbol"]] = u256(res[2*i+1]) if res[2*i+1] else 18

    calls, idx = [], []
    for i, e in enumerate(entries):
        if bals[e["symbol"]] and bals[e["symbol"]] > 0:
            calls.append(ec(FACTORY, "0x" + sel("getPair(address,address)") + encode(["address", "address"], [e["token"], WBNB]).hex()))
            idx.append(i)
    pres = batch(calls) if calls else []
    print(f"[stage] pairs done ({len(calls)} calls)", flush=True)
    pairs = {}
    for j, i in enumerate(idx):
        h = pres[j]
        pairs[entries[i]["symbol"]] = ("0x" + h[-40:]) if h and u256(h) else None

    calls, idx = [], []
    for i, e in enumerate(entries):
        p = pairs.get(e["symbol"])
        if p:
            calls.append(ec(p, "0x" + sel("token0()")))
            calls.append(ec(p, "0x" + sel("token1()")))
            calls.append(ec(p, "0x" + sel("getReserves()")))
            idx.append(i)
    rres = batch(calls) if calls else []
    print(f"[stage] reserves done ({len(calls)} calls)", flush=True)
    reserves = {}
    for k, i in enumerate(idx):
        sym = entries[i]["symbol"]
        t0h, t1h, rh = rres[3*k], rres[3*k+1], rres[3*k+2]
        r = {"token0": ("0x" + t0h[-40:]) if t0h else None,
             "token1": ("0x" + t1h[-40:]) if t1h else None, "reserves": None}
        if rh:
            try:
                r0, r1, _ = decode(["uint112", "uint112", "uint32"], bytes.fromhex(rh[2:]))
                r["reserves"] = [str(r0), str(r1)]
            except Exception as ex:
                r["reserves_error"] = str(ex)
        reserves[sym] = r

    calls, idx = [], []
    for i, e in enumerate(entries):
        sym = e["symbol"]
        p = pairs.get(sym)
        rv = reserves.get(sym, {})
        if p and rv.get("reserves") and int(rv["reserves"][0]) > 0 and int(rv["reserves"][1]) > 0:
            sell = int(e["amount_to_sell_raw"]) if e.get("amount_to_sell_raw") else bals[sym]
            calls.append(ec(ROUTER, "0x" + sel("getAmountsOut(uint256,address[])") + encode(["uint256", "address[]"], [sell, [e["token"], WBNB]]).hex()))
            idx.append((i, sell))
    qres = batch(calls) if calls else []
    print(f"[stage] quotes done ({len(calls)} calls)", flush=True)
    quotes = {}
    for k, (i, sell) in enumerate(idx):
        h = qres[k]
        if h:
            try:
                outs = decode(["uint256[]"], bytes.fromhex(h[2:]))[0]
                quotes[entries[i]["symbol"]] = {"quote_raw": str(outs[1]), "quote_bnb": outs[1] / 1e18, "sell_amount_raw": str(sell)}
            except Exception as ex:
                quotes[entries[i]["symbol"]] = {"quote_error": str(ex)}

    calls, idx = [], []
    for i, e in enumerate(entries):
        sc = e.get("sale_contract")
        if sc:
            calls.append(ec(sc, "0x" + sel("launched()")))
            idx.append(i)
    lres = batch(calls) if calls else []
    print(f"[stage] launched done ({len(calls)} calls)", flush=True)
    launched = {}
    for k, i in enumerate(idx):
        h = lres[k]
        if h:
            try:
                launched[entries[i]["symbol"]] = decode(["bool"], bytes.fromhex(h[2:]))[0]
            except Exception:
                launched[entries[i]["symbol"]] = None
        else:
            launched[entries[i]["symbol"]] = None

    for i, e in enumerate(entries):
        sym = e["symbol"]
        item = {"symbol": sym, "token": e["token"], "registered_amount_human": e.get("amount_human"),
                "amount_to_sell_raw": e.get("amount_to_sell_raw"), "reason_prev": e.get("reason"),
                "balance_raw": (str(bals[sym]) if bals[sym] is not None else None),
                "balance_human": (bals[sym] / (10**decs[sym]) if bals[sym] is not None else None),
                "decimals": decs[sym], "pair_wbnb": pairs.get(sym),
                "sale_contract": e.get("sale_contract"), "launched": launched.get(sym)}
        if bals[sym] is None:
            item["status"] = "rpc_failed_balance"
        elif bals[sym] == 0:
            item["status"] = "empty"
        elif not pairs.get(sym):
            item["status"] = "no_pair"
        else:
            rv = reserves.get(sym, {})
            item.update(rv)
            if rv.get("reserves") and (int(rv["reserves"][0]) == 0 or int(rv["reserves"][1]) == 0):
                item["status"] = "pair_empty"
            elif sym in quotes:
                q = quotes[sym]
                item.update(q)
                if "quote_bnb" in q:
                    ge = out["gas_est_300k_bnb"]
                    item["quote_ge_2x_gas"] = (ge is not None and q["quote_bnb"] >= 2 * ge)
                    item["status"] = "executable_candidate" if item["quote_ge_2x_gas"] else "quote_dust"
                else:
                    item["status"] = "no_quote"
            else:
                item["status"] = "no_quote"
        out["entries"].append(item)
    json.dump(out, open("/home/hatch/workspace/asset-sell-watch/pending_check_1951_nov16_stdout.json", "w"), indent=1, ensure_ascii=False)
    print(json.dumps({e["symbol"]: e["status"] for e in out["entries"]}, ensure_ascii=False), flush=True)

if __name__ == "__main__":
    main()
