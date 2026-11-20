#!/usr/bin/env python3
"""Pending-swap check run 2026-11-17 21:51 WIB — sequential single-call curl (read-only).
Batch eth_call is rate-limited right now on binance dataseed
("method eth_call in batch triggered rate limit", -32005) and publicnode
is 429; single eth_call works on 5 endpoints (verified live). Sequential
curl, one call at a time, rotating endpoints, 20s cap each — same pattern
as pending_check_0851_nov11_retry_curl.py. Same reads as
pending_check_1951_nov17.py."""
import json, subprocess, itertools
from eth_abi import encode, decode
from eth_utils import keccak

W = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
ROUTER = "0x10ED43C718714eb63d5aA57B78B54704E256024E"
FACTORY = "0xca143ce32fe78f1f7019d7d551a6402fc5350c73"
WBNB = "0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c"
URLS = itertools.cycle([
    "https://bsc-dataseed.binance.org/",
    "https://bsc-dataseed1.bnbchain.org/",
    "https://bsc-dataseed2.bnbchain.org/",
    "https://bsc.drpc.org/",
    "https://bsc.nodereal.io/",
])
OUT = "/home/hatch/workspace/asset-sell-watch/run-2026-11-17-2151.json"

def sel(sig):
    return keccak(text=sig).hex()[:8]

def u256(h):
    try:
        return int(h, 16) if h else 0
    except Exception:
        return 0

def call(method, params, timeout=20):
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params})
    for _ in range(3):
        url = next(URLS)
        try:
            p = subprocess.run(["curl", "-s", "-m", str(timeout), "-X", "POST",
                                "-H", "Content-Type: application/json",
                                "-d", body, url],
                               capture_output=True, text=True, timeout=timeout + 5)
            res = json.loads(p.stdout)
        except Exception as e:
            continue
        if isinstance(res, dict) and res.get("error"):
            continue
        if isinstance(res, dict) and res.get("result") is not None:
            return res["result"], url
    return None, None

def ec(to, data):
    return ("eth_call", [{"to": to, "data": data}, "latest"])

data = json.load(open("/home/hatch/workspace/asset-sell-watch/pending-swaps.json"))
entries = data["entries"]

gp, gp_url = call("eth_gasPrice", [])
gas_price = u256(gp) if gp else None
gas_est_bnb = (gas_price * 300000 / 1e18) if gas_price else None
out = {"run": "2026-11-17 21:51 WIB", "method": "curl_sequential_single",
       "gas_price_wei": gas_price, "gas_price_gwei": (gas_price / 1e9 if gas_price else None),
       "gas_est_300k_bnb": gas_est_bnb, "gas_url": gp_url, "entries": []}

items = []
for e in entries:
    tok = e["token"]; sym = e["symbol"]
    item = {"symbol": sym, "token": tok, "registered_amount_human": e.get("amount_human"),
            "amount_to_sell_raw": e.get("amount_to_sell_raw"), "reason_prev": e.get("reason")}
    bal_h, _ = call(*ec(tok, "0x" + sel("balanceOf(address)") + encode(["address"], [W]).hex()))
    dec_h, _ = call(*ec(tok, "0x" + sel("decimals()")))
    pair_h, _ = call(*ec(FACTORY, "0x" + sel("getPair(address,address)") + encode(["address", "address"], [tok, WBNB]).hex()))
    if bal_h is None:
        item["status"] = "rpc_failed_balance"; items.append(item)
        print(sym, "-> rpc_failed_balance", flush=True); continue
    bal = u256(bal_h); dec = u256(dec_h) if dec_h else 18
    item["balance_raw"] = str(bal); item["balance_human"] = bal / (10**dec) if dec < 40 else None
    item["decimals"] = dec
    if bal == 0:
        item["status"] = "empty"; items.append(item)
        print(sym, "-> empty", flush=True); continue
    pair = ("0x" + pair_h[-40:]) if pair_h and u256(pair_h) else None
    item["pair_wbnb"] = pair
    if not pair:
        item["status"] = "no_pair"; items.append(item)
        print(sym, "-> no_pair bal", item["balance_human"], flush=True); continue
    t0_h, _ = call(*ec(pair, "0x" + sel("token0()")))
    res_h, _ = call(*ec(pair, "0x" + sel("getReserves()")))
    item["token0"] = ("0x" + t0_h[-40:]) if t0_h else None
    if res_h:
        try:
            r0, r1, _ = decode(["uint112", "uint112", "uint32"], bytes.fromhex(res_h[2:]))
            item["reserves"] = [str(r0), str(r1)]
        except Exception as ex:
            item["reserves_error"] = str(ex)
    else:
        item["reserves_error"] = "null"
    res = item.get("reserves")
    if res and int(res[0]) > 0 and int(res[1]) > 0:
        sell_amt = int(item["amount_to_sell_raw"]) if item.get("amount_to_sell_raw") else bal
        item["sell_amount_raw"] = str(sell_amt)
        q_h, _ = call(*ec(ROUTER, "0x" + sel("getAmountsOut(uint256,address[])") + encode(["uint256", "address[]"], [sell_amt, [tok, WBNB]]).hex()))
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
    elif res:
        item["status"] = "pair_empty"
    items.append(item)
    print(sym, "->", item["status"], "| bal:", item.get("balance_human"),
          "| pair:", pair, "| res:", item.get("reserves"), "| quote:", item.get("quote_bnb"), flush=True)

# sale state probes (best effort, like previous runs)
for e in entries:
    sc = e.get("sale_contract")
    if not sc:
        continue
    sym = e["symbol"]
    lh, _ = call(*ec(sc, "0x" + sel("launched()")))
    th, _ = call(*ec(sc, "0x" + sel("tradingOpen()")))
    for it in items:
        if it["symbol"] == sym:
            it["sale_contract"] = sc
            it["launched_raw"] = lh
            it["tradingOpen_raw"] = th
            if lh is not None:
                try: it["launched"] = decode(["bool"], bytes.fromhex(lh[2:]))[0]
                except Exception: it["launched"] = None
            if th is not None:
                try: it["tradingOpen"] = decode(["bool"], bytes.fromhex(th[2:]))[0]
                except Exception: it["tradingOpen"] = None

out["entries"] = items
out["gas_2x_bnb"] = (2 * gas_est_bnb) if gas_est_bnb else None
out["entries_checked"] = len(items)
out["no_pair"] = [i["symbol"] for i in items if i["status"] == "no_pair"]
out["pair_empty"] = [i["symbol"] for i in items if i["status"] == "pair_empty"]
out["quote_dust"] = [i["symbol"] for i in items if i["status"] == "quote_dust"]
out["removed"] = []
out["sold"] = []
out["new_blocks"] = []
json.dump(out, open(OUT, "w"), indent=1)
print("DONE ->", OUT)
