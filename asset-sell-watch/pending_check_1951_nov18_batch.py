import json, sys, time
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
import fast_rpc
from eth_utils import keccak

W = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
WBNB = "0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c"
FACT = "0xca143ce32fe78f1f7019d7d551a6402fc5350c73"
ROUT = "0x10ED43C718714eb63d5aA57B78B54704E256024E"

def pad(a): return a[2:].lower().rjust(64, '0')
def sel(s): return keccak(text=s).hex()[:8]

entries = json.load(open("/home/hatch/workspace/asset-sell-watch/pending-swaps.json"))["entries"]
t0 = time.time()
out = {"run": "2026-11-18 19:51 WIB", "elapsed_s": None, "gas_price_wei": None, "results": []}

# --- Batch A: gasPrice + balanceOf + getPair for all entries ---
calls = [("eth_gasPrice", [])]
for e in entries:
    calls.append(("eth_call", [{"to": e["token"], "data": "0x70a08231" + pad(W)}, "latest"]))
for e in entries:
    calls.append(("eth_call", [{"to": FACT, "data": "0xe6a43905" + pad(e["token"]) + pad(WBNB)}, "latest"]))
try:
    resA = fast_rpc.batch_race(calls, timeout=30)
    out["gas_price_wei"] = int(resA[0], 16)
    out["gas_price_gwei"] = int(resA[0], 16) / 1e9
except Exception as ex:
    out["batchA_error"] = str(ex)
    print(json.dumps(out, indent=1))
    sys.exit(1)

n = len(entries)
balances = [int(resA[1 + i], 16) for i in range(n)]
pairs = []
for i in range(n):
    p = resA[1 + n + i]
    pairs.append("0x" + p[-40:] if int(p, 16) != 0 else None)

rows = []
for i, e in enumerate(entries):
    rows.append({"symbol": e["symbol"], "token": e["token"], "balance_raw": str(balances[i]),
                 "balance_human": balances[i] / (10 ** e.get("decimals", 18)),
                 "pair_wbnb": pairs[i]})

# --- Batch B: getReserves for existing pairs ---
idx_pairs = [i for i in range(n) if pairs[i]]
if idx_pairs:
    callsB = [("eth_call", [{"to": pairs[i], "data": "0x0902f1ac"}, "latest"]) for i in idx_pairs]
    try:
        resB = fast_rpc.batch_race(callsB, timeout=30)
        for j, i in enumerate(idx_pairs):
            r = resB[j]
            rows[i]["reserves"] = [str(int(r[2:66], 16)), str(int(r[66:130], 16))]
    except Exception as ex:
        for i in idx_pairs:
            rows[i]["reserves_error"] = str(ex)[:200]

# --- Batch C: getAmountsOut for pairs with reserves > 0 ---
idx_q = []
for i in idx_pairs:
    rv = rows[i].get("reserves")
    if rv and int(rv[0]) > 0 and int(rv[1]) > 0:
        idx_q.append(i)
if idx_q:
    callsC = []
    for i in idx_q:
        e = entries[i]
        sell = int(e["amount_to_sell_raw"]) if e.get("amount_to_sell_raw") else balances[i]
        rows[i]["sell_amount_raw"] = str(sell)
        data = ("0xd06ca61f" + format(sell, '064x')
                + "0000000000000000000000000000000000000000000000000000000000000040"
                + "0000000000000000000000000000000000000000000000000000000000000002"
                + pad(e["token"]) + pad(WBNB))
        callsC.append(("eth_call", [{"to": ROUT, "data": data}, "latest"]))
    try:
        resC = fast_rpc.batch_race(callsC, timeout=30)
        for j, i in enumerate(idx_q):
            q = resC[j]
            rows[i]["quote_raw"] = str(int(q[194:258], 16))
            rows[i]["quote_bnb"] = int(q[194:258], 16) / 1e18
    except Exception as ex:
        for i in idx_q:
            rows[i]["quote_error"] = str(ex)[:200]

# --- Batch D: sale-state probes, per-item error tolerant (revert = function absent) ---
probes = ["launched()", "tradingOpen()", "isOpen()", "opened()", "phase()"]
callsD = []
metaD = []
for i, e in enumerate(entries):
    sc = e.get("sale_contract")
    if not sc:
        continue
    for f in probes:
        callsD.append(("eth_call", [{"to": sc, "data": "0x" + sel(f)}, "latest"]))
        metaD.append((i, f))
if callsD:
    payload = [{"jsonrpc": "2.0", "id": k + 1, "method": m, "params": p} for k, (m, p) in enumerate(callsD)]
    eps = fast_rpc.healthy_endpoints()
    done = False
    for ep in eps:
        try:
            resp = fast_rpc._post(ep, payload, 30)
            if isinstance(resp, list) and len(resp) == len(callsD):
                by_id = {it["id"]: it for it in resp}
                for k, (i, f) in enumerate(metaD):
                    it = by_id[k + 1]
                    st = rows[i].setdefault("sale_state", {})
                    if "error" in it:
                        st[f] = "revert/absent"
                    else:
                        st[f] = it["result"]
                done = True
                break
        except Exception:
            continue
    if not done:
        for i, e in enumerate(entries):
            if e.get("sale_contract"):
                rows[i]["sale_state_error"] = "probe batch failed on all endpoints"

out["results"] = rows
out["elapsed_s"] = round(time.time() - t0, 1)
print(json.dumps(out, indent=1))
