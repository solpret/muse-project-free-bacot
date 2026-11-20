#!/usr/bin/env python3
"""pending_check_0951_nov18_fast.py — fresh read of pending-swaps via fast_rpc batch+race.
Same output shape as pending_check_0151_nov18.py, but batched (1 round trip per
group) because the sequential urllib version stalled >6 min on egress flapping.
Read-only: balanceOf, factory getPair, getReserves, getAmountsOut, gasPrice,
plus best-effort sale-contract state probes (revert = function absent)."""
import json, sys
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from eth_utils import keccak
import fast_rpc

W = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
WBNB = "0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c"
FACT = "0xca143ce32fe78f1f7019d7d551a6402fc5350c73"
ROUT = "0x10ED43C718714eb63d5aA57B78B54704E256024E"

def pad(a): return a[2:].lower().rjust(64, '0')
def sel(s): return keccak(text=s).hex()[:8]

def batch_tolerant(calls, timeout=15, chunk=6):
    """calls = list of (method, params). Returns list of ('ok', result) or ('err', msg)
    per item. Chunked small batches (dataseeds 429 large batches), sequential,
    one endpoint at a time via fast_rpc.batch (walks healthy endpoints)."""
    import time
    out_all = []
    for i in range(0, len(calls), chunk):
        sub = calls[i:i + chunk]
        try:
            res = fast_rpc.batch(sub, timeout=timeout)
            out_all.extend(("ok", r) for r in res)
        except Exception:
            # fall back: race each call individually
            for m, p in sub:
                try:
                    out_all.append(("ok", fast_rpc.race(m, p, timeout=timeout)))
                except Exception as e:
                    out_all.append(("err", f"{type(e).__name__}: {str(e)[:100]}"))
        time.sleep(0.3)
    return out_all

def eth_call_item(to, data):
    return ("eth_call", [{"to": to, "data": data}, "latest"])

entries = json.load(open("/home/hatch/workspace/asset-sell-watch/pending-swaps.json"))["entries"]
out = []
gas = None

# Batch A: gasPrice + balanceOf + getPair for all entries
calls = [("eth_gasPrice", [])]
for e in entries:
    calls.append(eth_call_item(e["token"], "0x70a08231" + pad(W)))
for e in entries:
    calls.append(eth_call_item(FACT, "0xe6a43905" + pad(e["token"]) + pad(WBNB)))
resA = batch_tolerant(calls)
g = resA[0]
if g[0] == "ok":
    gas = int(g[1], 16)

n = len(entries)
for i, e in enumerate(entries):
    tok = e["token"]; sym = e["symbol"]
    amt = int(e["amount_to_sell_raw"]) if e.get("amount_to_sell_raw") else None
    row = {"symbol": sym, "token": tok}
    b = resA[1 + i]
    if b[0] == "ok":
        bal = int(b[1], 16)
        row["balance_raw"] = str(bal)
        row["balance_human"] = bal / (10 ** e.get("decimals", 18))
    else:
        row["balance_error"] = b[1]
        out.append(row); continue
    p = resA[1 + n + i]
    if p[0] == "ok":
        pair_addr = "0x" + p[1][-40:]
        row["pair_wbnb"] = pair_addr if int(p[1], 16) != 0 else None
    else:
        row["pair_error"] = p[1]
        out.append(row); continue
    out.append(row)

# Batch B: getReserves for pairs found
pair_idx = [(i, out[i]["pair_wbnb"]) for i in range(n) if out[i].get("pair_wbnb")]
if pair_idx:
    resB = batch_tolerant([eth_call_item(p, "0x0902f1ac") for _, p in pair_idx])
    for k, (i, p) in enumerate(pair_idx):
        r = resB[k]
        if r[0] == "ok":
            out[i]["reserves"] = [str(int(r[1][2:66], 16)), str(int(r[1][66:130], 16))]
        else:
            out[i]["reserves_error"] = r[1]

# Batch C: getAmountsOut for pairs with both reserves > 0
q_idx = []
for i in range(n):
    row = out[i]
    if row.get("reserves") and int(row["reserves"][0]) > 0 and int(row["reserves"][1]) > 0:
        sell = int(entries[i]["amount_to_sell_raw"]) if entries[i].get("amount_to_sell_raw") else int(row["balance_raw"])
        if sell > 0:
            data = ("0xd06ca61f" + format(sell, '064x')
                    + "0000000000000000000000000000000000000000000000000000000000000040"
                    + "0000000000000000000000000000000000000000000000000000000000000002"
                    + pad(entries[i]["token"]) + pad(WBNB))
            q_idx.append((i, data))
if q_idx:
    resC = batch_tolerant([eth_call_item(ROUT, d) for _, d in q_idx])
    for k, (i, _) in enumerate(q_idx):
        r = resC[k]
        if r[0] == "ok":
            out[i]["quote_raw"] = str(int(r[1][194:258], 16))
            out[i]["quote_bnb"] = int(r[1][194:258], 16) / 1e18
        else:
            out[i]["quote_error"] = r[1]

# Batch D: sale-contract state probes (best effort)
probe_fns = ["launched()", "tradingOpen()", "isOpen()", "opened()", "phase()"]
sc_idx = []
for i, e in enumerate(entries):
    if e.get("sale_contract"):
        for f in probe_fns:
            sc_idx.append((i, e["sale_contract"], f))
if sc_idx:
    resD = batch_tolerant([eth_call_item(sc, "0x" + sel(f)) for _, sc, f in sc_idx])
    for k, (i, sc, f) in enumerate(sc_idx):
        st = out[i].setdefault("sale_state", {})
        r = resD[k]
        st[f] = r[1] if r[0] == "ok" else "ERR:" + r[1][:80]

print(json.dumps({"gas_price_wei": gas, "gas_price_gwei": (gas / 1e9 if gas else None),
                  "results": out}, indent=1))
