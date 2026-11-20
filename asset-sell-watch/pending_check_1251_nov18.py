#!/usr/bin/env python3
"""pending_check_1251_nov18.py — run 12:51 WIB 2026-11-18.
Stage 1: balanceOf + getPair + gasPrice in ONE JSON-RPC batch (AGENTS.md:
batch, bukan sekuensial). Stage 2: getReserves batch utk pair yg ada.
Stage 3: getAmountsOut batch utk pair dgn cadangan > 0.
Stage 4: sale-state probe batch (launched/tradingOpen/isOpen/opened/phase)
utk setiap sale_contract. curl, timeout 20s, retry antar endpoint."""
import json, subprocess, time

W = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
WBNB = "0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c"
FACT = "0xca143ce32fe78f1f7019d7d551a6402fc5350c73"
ROUT = "0x10ED43C718714eb63d5aA57B78B54704E256024E"
EPS = ["https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed.binance.org/",
       "https://bsc-dataseed1.defibit.io/"]

def pad(a):
    return a[2:].lower().rjust(64, '0')

def _post_batch(payload, ep):
    proc = subprocess.run(["curl", "-s", "-m", "20", "-H", "Content-Type: application/json",
                           "-d", payload, ep], capture_output=True, text=True, timeout=25)
    return json.loads(proc.stdout)

def _single(call):
    k, m, p = call
    payload = json.dumps({"jsonrpc": "2.0", "id": 1, "method": m, "params": p})
    for ep in EPS:
        try:
            j = _post_batch(payload, ep)
            if isinstance(j, dict) and "error" in j:
                raise Exception(str(j["error"]))
            return j.get("result")
        except Exception:
            time.sleep(1)
    raise Exception("all_endpoints_failed_single")

def batch(calls, chunk=5):
    """Chunked batches (dataseed rate-limits large eth_call batches with
    -32005). A chunk that fails as a whole is retried call-by-call."""
    out = {}
    for start in range(0, len(calls), chunk):
        part = calls[start:start + chunk]
        payload = json.dumps([{"jsonrpc": "2.0", "id": i + 1, "method": m, "params": p}
                              for i, (k, m, p) in enumerate(part)])
        resp = None
        for ep in EPS:
            try:
                r = _post_batch(payload, ep)
                if isinstance(r, list) and len(r) == len(part):
                    resp = r
                    break
                if isinstance(r, dict) and "error" in r:
                    raise Exception(str(r["error"]))
                raise Exception("short_batch_response len=%s" % (len(r) if isinstance(r, list) else type(r).__name__))
            except Exception:
                time.sleep(1)
        if resp is None:
            for k, m, p in part:
                try:
                    out[k] = _single((k, m, p))
                except Exception as e:
                    out[k] = {"_error": str(e)[:200]}
            continue
        for i, (k, m, p) in enumerate(part):
            r = resp[i]
            if isinstance(r, dict) and "error" in r:
                out[k] = {"_error": str(r["error"])[:200]}
            else:
                out[k] = r.get("result") if isinstance(r, dict) else r
    return out

def sel(sig):
    from eth_utils import keccak
    return keccak(text=sig).hex()[:8]

entries = json.load(open("/home/hatch/workspace/asset-sell-watch/pending-swaps.json"))["entries"]
t0 = time.time()

# ---- Stage 1: balances + pairs + gas ----
calls = [("gas", "eth_gasPrice", [])]
for e in entries:
    calls.append((e["symbol"] + "|bal", "eth_call",
                  [{"to": e["token"], "data": "0x70a08231" + pad(W)}, "latest"]))
    calls.append((e["symbol"] + "|pair", "eth_call",
                  [{"to": FACT, "data": "0xe6a43905" + pad(e["token"]) + pad(WBNB)}, "latest"]))
r1 = batch(calls)
gas = None
try:
    gas = int(r1["gas"], 16)
except Exception:
    pass

rows = []
for e in entries:
    sym = e["symbol"]
    row = {"symbol": sym, "token": e["token"]}
    b = r1.get(sym + "|bal")
    if isinstance(b, dict):
        row["balance_error"] = b["_error"]; rows.append(row); continue
    try:
        bal = int(b, 16)
    except Exception as ex:
        row["balance_error"] = str(ex)[:200]; rows.append(row); continue
    row["balance_raw"] = str(bal)
    row["balance_human"] = bal / (10 ** e.get("decimals", 18))
    p = r1.get(sym + "|pair")
    if isinstance(p, dict):
        row["pair_error"] = p["_error"]; rows.append(row); continue
    try:
        row["pair_wbnb"] = ("0x" + p[-40:]) if int(p, 16) != 0 else None
    except Exception as ex:
        row["pair_error"] = str(ex)[:200]; rows.append(row); continue
    rows.append(row)

# ---- Stage 2: reserves for existing pairs ----
calls2 = []
for row in rows:
    if row.get("pair_wbnb"):
        calls2.append((row["symbol"] + "|res", "eth_call",
                       [{"to": row["pair_wbnb"], "data": "0x0902f1ac"}, "latest"]))
r2 = batch(calls2) if calls2 else {}
for row in rows:
    if row.get("pair_wbnb"):
        res = r2.get(row["symbol"] + "|res")
        if isinstance(res, dict):
            row["reserves_error"] = res["_error"]
        else:
            try:
                row["reserves"] = [str(int(res[2:66], 16)), str(int(res[66:130], 16))]
            except Exception as ex:
                row["reserves_error"] = str(ex)[:200]

# ---- Stage 3: quotes for pairs with both reserves > 0 ----
calls3 = []
for row, e in zip(rows, entries):
    if row.get("reserves") and int(row["reserves"][0]) > 0 and int(row["reserves"][1]) > 0:
        sell = int(e["amount_to_sell_raw"]) if e.get("amount_to_sell_raw") else int(row["balance_raw"])
        if sell > 0:
            data = ("0xd06ca61f" + format(sell, '064x')
                    + "0000000000000000000000000000000000000000000000000000000000000040"
                    + "0000000000000000000000000000000000000000000000000000000000000002"
                    + pad(e["token"]) + pad(WBNB))
            calls3.append((row["symbol"] + "|quote", "eth_call",
                           [{"to": ROUT, "data": data}, "latest"]))
            row["_sell_raw"] = str(sell)
r3 = batch(calls3) if calls3 else {}
for row in rows:
    q = r3.get(row["symbol"] + "|quote")
    if q is None:
        continue
    if isinstance(q, dict):
        row["quote_error"] = q["_error"]
    else:
        try:
            row["quote_raw"] = str(int(q[194:258], 16))
            row["quote_bnb"] = int(q[194:258], 16) / 1e18
        except Exception as ex:
            row["quote_error"] = str(ex)[:200]
    row.pop("_sell_raw", None)

# ---- Stage 4: sale-state probes ----
calls4 = []
for e in entries:
    sc = e.get("sale_contract")
    if not sc:
        continue
    for fname in ["launched()", "tradingOpen()", "isOpen()", "opened()", "phase()"]:
        calls4.append((e["symbol"] + "|" + fname, "eth_call",
                       [{"to": sc, "data": "0x" + sel(fname)}, "latest"]))
r4 = batch(calls4) if calls4 else {}
sale_state = {}
for e in entries:
    sc = e.get("sale_contract")
    if not sc:
        continue
    st = {}
    for fname in ["launched()", "tradingOpen()", "isOpen()", "opened()", "phase()"]:
        v = r4.get(e["symbol"] + "|" + fname)
        if isinstance(v, dict):
            st[fname] = "ERR:" + v["_error"][:120]
        else:
            st[fname] = v
    sale_state[e["symbol"]] = st

print(json.dumps({"gas_price_wei": gas, "gas_price_gwei": (gas / 1e9 if gas else None),
                  "gas_2x_300k_bnb": (gas * 300000 * 2 / 1e18 if gas else None),
                  "elapsed_s": round(time.time() - t0, 1),
                  "results": rows, "sale_state": sale_state}, indent=1))
