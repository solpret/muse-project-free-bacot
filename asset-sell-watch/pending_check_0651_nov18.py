#!/usr/bin/env python3
"""pending_check_0651_nov18.py — batched version (fast_rpc batch_race).
Same reads as the sequential script: balanceOf, getPair(WBNB), reserves,
getAmountsOut, sale-state probes. One JSON-RPC batch per stage, raced."""
import json, sys, time
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import batch_race, call_many, race
from eth_utils import keccak

W = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
WBNB = "0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c"
FACT = "0xca143ce32fe78f1f7019d7d551a6402fc5350c73"
ROUT = "0x10ED43C718714eb63d5aA57B78B54704E256024E"

def pad(a): return a[2:].lower().rjust(64, '0')
def sel(s): return keccak(text=s).hex()[:8]

def do_batch(calls, timeout=12):
    """calls: list of (to, data). Returns list of raw hex results (or None on error)."""
    try:
        return batch_race(calls, timeout=timeout)
    except Exception:
        return call_many(calls)

entries = json.load(open("/home/hatch/workspace/asset-sell-watch/pending-swaps.json"))["entries"]
out = []
t0 = time.time()

# Stage 0: gas price
gas = None
try:
    gas = int(race("eth_gasPrice", []), 16)
except Exception as e:
    out.append({"gas_error": str(e)[:200]})

# Stage 1: balanceOf + getPair for all entries in ONE batch (36 calls)
calls = []
for e in entries:
    calls.append((e["token"], "0x70a08231" + pad(W)))
    calls.append((FACT, "0xe6a43905" + pad(e["token"]) + pad(WBNB)))
res1 = do_batch(calls)
if res1 is None or len(res1) != len(calls):
    print(json.dumps({"error": "stage1 batch failed", "results": res1}, indent=1))
    sys.exit(1)

rows = []
for i, e in enumerate(entries):
    tok = e["token"]; sym = e["symbol"]
    row = {"symbol": sym, "token": tok}
    bal_raw, pair_raw = res1[2*i], res1[2*i+1]
    try:
        bal = int(bal_raw, 16)
        row["balance_raw"] = str(bal); row["balance_human"] = bal / (10 ** e.get("decimals", 18))
    except Exception:
        row["balance_error"] = str(bal_raw)[:200]
    try:
        row["pair_wbnb"] = ("0x" + pair_raw[-40:]) if int(pair_raw, 16) != 0 else None
    except Exception:
        row["pair_error"] = str(pair_raw)[:200]
    rows.append(row)

# Stage 2: reserves for pairs that exist
pair_idx = [i for i, r in enumerate(rows) if r.get("pair_wbnb")]
if pair_idx:
    rcalls = [(rows[i]["pair_wbnb"], "0x0902f1ac") for i in pair_idx]
    rres = do_batch(rcalls)
    for k, i in enumerate(pair_idx):
        try:
            rr = rres[k]
            r0 = int(rr[2:66], 16); r1 = int(rr[66:130], 16)
            rows[i]["reserves"] = [str(r0), str(r1)]
        except Exception:
            rows[i]["reserves_error"] = str(rres[k])[:200] if rres and k < len(rres) else "no result"

# Stage 3: getAmountsOut for pairs with both reserves > 0
q_idx = []
for i in pair_idx:
    r = rows[i]
    if r.get("reserves") and int(r["reserves"][0]) > 0 and int(r["reserves"][1]) > 0:
        q_idx.append(i)
if q_idx:
    qcalls = []
    for i in q_idx:
        e = entries[i]; tok = e["token"]
        sell = int(e["amount_to_sell_raw"]) if e.get("amount_to_sell_raw") else int(rows[i]["balance_raw"])
        data = ("0xd06ca61f" + format(sell, '064x')
                + "0000000000000000000000000000000000000000000000000000000000000040"
                + "0000000000000000000000000000000000000000000000000000000000000002"
                + pad(tok) + pad(WBNB))
        qcalls.append((ROUT, data))
    qres = do_batch(qcalls)
    for k, i in enumerate(q_idx):
        try:
            q = qres[k]
            rows[i]["quote_raw"] = str(int(q[194:258], 16))
            rows[i]["quote_bnb"] = int(q[194:258], 16) / 1e18
        except Exception:
            rows[i]["quote_error"] = str(qres[k])[:200] if qres and k < len(qres) else "no result"

# Stage 4: sale-state probes (5 selectors x 18 contracts = 90 calls, one batch)
scalls, smap = [], []
for i, e in enumerate(entries):
    sc = e.get("sale_contract")
    if sc:
        for fname in ["launched()", "tradingOpen()", "isOpen()", "opened()", "phase()"]:
            scalls.append((sc, "0x" + sel(fname)))
            smap.append((i, fname))
if scalls:
    sres = do_batch(scalls)
    for k, (i, fname) in enumerate(smap):
        rows[i].setdefault("sale_state", {})[fname] = sres[k] if k < len(sres) else "no result"

print(json.dumps({"gas_price_wei": gas, "gas_price_gwei": (gas/1e9 if gas else None),
                  "elapsed_s": round(time.time()-t0, 1), "results": rows}, indent=1))
