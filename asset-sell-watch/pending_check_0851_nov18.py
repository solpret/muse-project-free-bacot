#!/usr/bin/env python3
"""pending_check_0851_nov18.py — stage 1 only: balanceOf + getPair.
Sale-state probes skipped this run (uniformly absent/reverted in the
05:51 run 1h ago; re-check next run). curl, 8s timeout, 1 retry."""
import json, subprocess, time
from eth_utils import keccak

W = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
WBNB = "0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c"
FACT = "0xca143ce32fe78f1f7019d7d551a6402fc5350c73"
ROUT = "0x10ED43C718714eb63d5aA57B78B54704E256024E"
EPS = ["https://bsc-dataseed1.bnbchain.org/", "https://bsc-dataseed.binance.org/"]

def pad(a): return a[2:].lower().rjust(64, '0')

def eth_call(to, data):
    payload = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                          "params": [{"to": to, "data": data}, "latest"]})
    last = None
    for ep in EPS:
        for attempt in range(2):
            try:
                p = subprocess.run(["curl", "-s", "-m", "8", "-H", "Content-Type: application/json",
                                    "-d", payload, ep], capture_output=True, text=True, timeout=12)
                j = json.loads(p.stdout)
                if "error" in j:
                    raise Exception(str(j["error"]))
                return j["result"]
            except Exception as e:
                last = e
                time.sleep(1)
    raise last

def gas_price():
    payload = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_gasPrice", "params": []})
    for ep in EPS:
        try:
            p = subprocess.run(["curl", "-s", "-m", "8", "-H", "Content-Type: application/json",
                                "-d", payload, ep], capture_output=True, text=True, timeout=12)
            return int(json.loads(p.stdout)["result"], 16)
        except Exception:
            continue
    return None

entries = json.load(open("/home/hatch/workspace/asset-sell-watch/pending-swaps.json"))["entries"]
t0 = time.time()
gas = gas_price()
rows = []
for e in entries:
    tok = e["token"]; sym = e["symbol"]
    row = {"symbol": sym, "token": tok}
    try:
        bal = int(eth_call(tok, "0x70a08231" + pad(W)), 16)
        row["balance_raw"] = str(bal); row["balance_human"] = bal / (10 ** e.get("decimals", 18))
    except Exception as ex:
        row["balance_error"] = str(ex)[:200]; rows.append(row); continue
    try:
        pair = eth_call(FACT, "0xe6a43905" + pad(tok) + pad(WBNB))
        row["pair_wbnb"] = ("0x" + pair[-40:]) if int(pair, 16) != 0 else None
    except Exception as ex:
        row["pair_error"] = str(ex)[:200]; rows.append(row); continue
    if row["pair_wbnb"]:
        try:
            res = eth_call(row["pair_wbnb"], "0x0902f1ac")
            r0 = int(res[2:66], 16); r1 = int(res[66:130], 16)
            row["reserves"] = [str(r0), str(r1)]
        except Exception as ex:
            row["reserves_error"] = str(ex)[:200]
        sell = int(e["amount_to_sell_raw"]) if e.get("amount_to_sell_raw") else bal
        if sell > 0 and row.get("reserves") and int(row["reserves"][0]) > 0 and int(row["reserves"][1]) > 0:
            data = ("0xd06ca61f" + format(sell, '064x')
                    + "0000000000000000000000000000000000000000000000000000000000000040"
                    + "0000000000000000000000000000000000000000000000000000000000000002"
                    + pad(tok) + pad(WBNB))
            try:
                q = eth_call(ROUT, data)
                row["quote_raw"] = str(int(q[194:258], 16)); row["quote_bnb"] = int(q[194:258], 16) / 1e18
            except Exception as ex:
                row["quote_error"] = str(ex)[:200]
    rows.append(row)

print(json.dumps({"gas_price_wei": gas, "gas_price_gwei": (gas/1e9 if gas else None),
                  "elapsed_s": round(time.time()-t0, 1), "results": rows}, indent=1))
