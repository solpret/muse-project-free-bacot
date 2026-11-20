#!/usr/bin/env python3
"""pending_check_0951_nov18_curl.py — fresh read via curl (transport proven OK).
Sequential curl eth_calls with endpoint fallback; small delay between calls to
avoid dataseed 429s. Same output shape as pending_check_0151_nov18.py.
Sale probes reduced to phase()+launched() (all 5 probes reverted for every
entry in the 01:51 run — functions absent; a phase change would still show
via phase()/launched())."""
import json, subprocess, time
from eth_utils import keccak

W = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
WBNB = "0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c"
FACT = "0xca143ce32fe78f1f7019d7d551a6402fc5350c73"
ROUT = "0x10ED43C718714eb63d5aA57B78B54704E256024E"
EPS = ["https://bsc-dataseed.binance.org", "https://bsc-dataseed1.bnbchain.org",
       "https://bsc-dataseed2.bnbchain.org", "https://bsc-dataseed1.defibit.io"]

def pad(a): return a[2:].lower().rjust(64, '0')
def sel(s): return keccak(text=s).hex()[:8]

def rpc(method, params):
    payload = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params})
    last = None
    for ep in EPS:
        try:
            r = subprocess.run(["curl", "-s", "-m", "12", "-X", "POST", ep,
                                "-H", "Content-Type: application/json",
                                "--data", payload],
                               capture_output=True, text=True, timeout=15)
            j = json.loads(r.stdout)
            if "error" in j:
                last = f"RPC:{j['error']}"
                continue
            time.sleep(0.15)
            return j["result"], ep
        except Exception as e:
            last = f"{type(e).__name__}:{e}"
            continue
    raise Exception(last or "all endpoints failed")

def eth_call(to, data):
    return rpc("eth_call", [{"to": to, "data": data}, "latest"])

entries = json.load(open("/home/hatch/workspace/asset-sell-watch/pending-swaps.json"))["entries"]
out = []
gas = None
try:
    g, _ = rpc("eth_gasPrice", [])
    gas = int(g, 16)
except Exception as e:
    out.append({"gas_error": str(e)})

for e in entries:
    tok = e["token"]; sym = e["symbol"]
    amt = int(e["amount_to_sell_raw"]) if e.get("amount_to_sell_raw") else None
    row = {"symbol": sym, "token": tok}
    try:
        b, ep = eth_call(tok, "0x70a08231" + pad(W))
        bal = int(b, 16)
        row["balance_raw"] = str(bal)
        row["balance_human"] = bal / (10 ** e.get("decimals", 18))
        row["balance_ep"] = ep
    except Exception as ex:
        row["balance_error"] = str(ex)[:200]
        out.append(row); continue
    try:
        p, ep = eth_call(FACT, "0xe6a43905" + pad(tok) + pad(WBNB))
        pair_addr = "0x" + p[-40:]
        row["pair_wbnb"] = pair_addr if int(p, 16) != 0 else None
        row["pair_ep"] = ep
    except Exception as ex:
        row["pair_error"] = str(ex)[:200]
        out.append(row); continue
    if row["pair_wbnb"]:
        try:
            res, _ = eth_call(row["pair_wbnb"], "0x0902f1ac")
            r0 = int(res[2:66], 16); r1 = int(res[66:130], 16)
            row["reserves"] = [str(r0), str(r1)]
        except Exception as ex:
            row["reserves_error"] = str(ex)[:200]
        sell = amt if amt is not None else bal
        if sell > 0 and row.get("reserves") and int(row["reserves"][0]) > 0 and int(row["reserves"][1]) > 0:
            data = ("0xd06ca61f" + format(sell, '064x')
                    + "0000000000000000000000000000000000000000000000000000000000000040"
                    + "0000000000000000000000000000000000000000000000000000000000000002"
                    + pad(tok) + pad(WBNB))
            try:
                q, _ = eth_call(ROUT, data)
                row["quote_raw"] = str(int(q[194:258], 16))
                row["quote_bnb"] = int(q[194:258], 16) / 1e18
            except Exception as ex:
                row["quote_error"] = str(ex)[:200]
    sc = e.get("sale_contract")
    if sc:
        st = {}
        for fname in ["phase()", "launched()"]:
            try:
                r, _ = eth_call(sc, "0x" + sel(fname))
                st[fname] = r
            except Exception as ex:
                st[fname] = "ERR:" + str(ex)[:80]
        row["sale_state"] = st
    out.append(row)

print(json.dumps({"gas_price_wei": gas, "gas_price_gwei": (gas / 1e9 if gas else None),
                  "results": out}, indent=1))
