#!/usr/bin/env python3
"""Read-only pending-swap check run 2026-11-16 19:51 WIB.
Uses fast_rpc.batch_race (multi-endpoint) for robustness.
No audit, no preview, no execution. Prints JSON summary."""
import sys, json
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from eth_abi import encode, decode
from eth_utils import keccak
import fast_rpc

W = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
ROUTER = "0x10ED43C718714eb63d5aA57B78B54704E256024E"
FACTORY = "0xca143ce32fe78f1f7019d7d551a6402fc5350c73"
WBNB = "0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c"

def sel(sig):
    return keccak(text=sig).hex()[:8]

def u256(h):
    try:
        return int(h, 16) if h else 0
    except Exception:
        return 0

def call_many(calls):
    """calls: list of (to, data) -> list of hex results or None per item."""
    try:
        return fast_rpc.call_many(calls)
    except Exception as e:
        return [None] * len(calls)

def main():
    data = json.load(open("/home/hatch/workspace/asset-sell-watch/pending-swaps.json"))
    entries = data["entries"]
    out = {"run": "2026-11-16 19:51 WIB", "entries": []}
    # gas price
    try:
        gp = fast_rpc.race("eth_gasPrice", [])
        gas_price = u256(gp)
    except Exception as e:
        gas_price = None
        out["gas_err"] = str(e)
    out["gas_price_wei"] = gas_price
    out["gas_price_gwei"] = (gas_price / 1e9) if gas_price else None
    out["gas_est_300k_bnb"] = (gas_price * 300000 / 1e18) if gas_price else None

    # batch 1: balanceOf + decimals for all
    calls = []
    for e in entries:
        tok = e["token"]
        calls.append((tok, "0x" + sel("balanceOf(address)") + encode(["address"], [W]).hex()))
        calls.append((tok, "0x" + sel("decimals()")))
    res = call_many(calls)
    bals, decs = {}, {}
    for i, e in enumerate(entries):
        bals[e["symbol"]] = u256(res[2*i]) if res[2*i] else None
        decs[e["symbol"]] = u256(res[2*i+1]) if res[2*i+1] else 18

    # batch 2: getPair for entries with balance > 0
    pair_calls, pair_idx = [], []
    for i, e in enumerate(entries):
        if bals[e["symbol"]] and bals[e["symbol"]] > 0:
            pair_calls.append((FACTORY, "0x" + sel("getPair(address,address)") + encode(["address", "address"], [e["token"], WBNB]).hex()))
            pair_idx.append(i)
    pair_res = call_many(pair_calls) if pair_calls else []
    pairs = {}
    for j, i in enumerate(pair_idx):
        h = pair_res[j]
        pairs[entries[i]["symbol"]] = ("0x" + h[-40:]) if h and u256(h) else None

    # batch 3: token0/token1/getReserves for pairs found
    res_calls, res_idx = [], []
    for i, e in enumerate(entries):
        p = pairs.get(e["symbol"])
        if p:
            res_calls.append((p, "0x" + sel("token0()")))
            res_calls.append((p, "0x" + sel("token1()")))
            res_calls.append((p, "0x" + sel("getReserves()")))
            res_idx.append(i)
    res_res = call_many(res_calls) if res_calls else []
    reserves = {}
    for k, i in enumerate(res_idx):
        sym = entries[i]["symbol"]
        t0h, t1h, rh = res_res[3*k], res_res[3*k+1], res_res[3*k+2]
        r = {"token0": ("0x" + t0h[-40:]) if t0h else None,
             "token1": ("0x" + t1h[-40:]) if t1h else None,
             "reserves": None}
        if rh:
            try:
                r0, r1, _ = decode(["uint112", "uint112", "uint32"], bytes.fromhex(rh[2:]))
                r["reserves"] = [str(r0), str(r1)]
            except Exception as ex:
                r["reserves_error"] = str(ex)
        reserves[sym] = r

    # batch 4: quotes for pairs with both reserves > 0
    q_calls, q_idx = [], []
    for i, e in enumerate(entries):
        sym = e["symbol"]
        p = pairs.get(sym)
        rv = reserves.get(sym, {})
        if p and rv.get("reserves") and int(rv["reserves"][0]) > 0 and int(rv["reserves"][1]) > 0:
            sell = int(e["amount_to_sell_raw"]) if e.get("amount_to_sell_raw") else bals[sym]
            q_calls.append((ROUTER, "0x" + sel("getAmountsOut(uint256,address[])") + encode(["uint256", "address[]"], [sell, [e["token"], WBNB]]).hex()))
            q_idx.append((i, sell))
    q_res = call_many(q_calls) if q_calls else []
    quotes = {}
    for k, (i, sell) in enumerate(q_idx):
        h = q_res[k]
        if h:
            try:
                outs = decode(["uint256[]"], bytes.fromhex(h[2:]))[0]
                quotes[entries[i]["symbol"]] = {"quote_raw": str(outs[1]), "quote_bnb": outs[1] / 1e18, "sell_amount_raw": str(sell)}
            except Exception as ex:
                quotes[entries[i]["symbol"]] = {"quote_error": str(ex)}

    # batch 5: launched() on sale contracts (best effort)
    l_calls, l_idx = [], []
    for i, e in enumerate(entries):
        sc = e.get("sale_contract")
        if sc:
            l_calls.append((sc, "0x" + sel("launched()")))
            l_idx.append(i)
    l_res = call_many(l_calls) if l_calls else []
    launched = {}
    for k, i in enumerate(l_idx):
        h = l_res[k]
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
                "sale_contract": e.get("sale_contract"),
                "launched": launched.get(sym)}
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
    print(json.dumps(out, indent=1, ensure_ascii=False))

if __name__ == "__main__":
    main()
