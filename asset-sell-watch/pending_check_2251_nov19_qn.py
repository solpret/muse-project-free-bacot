import json, sys, time
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.quicknode/bin")
import quicknode
from eth_utils import keccak

W = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
WBNB = "0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c"
FACT = "0xca143ce32fe78f1f7019d7d551a6402fc5350c73"
ROUT = "0x10ED43C718714eb63d5aA57B78B54704E256024E"

def pad(a): return a[2:].lower().rjust(64, '0')
def sel(s): return keccak(text=s).hex()[:8]

def rpc_batch(calls, timeout=60):
    """calls: list of (method, params). Returns list of per-item dicts (result or error).
    QuickNode free plan: 15 req/s — chunk to <=10 calls with 1.2s gaps."""
    import json as _json
    from quicknode import ProxyHTTPSConnection, HOST, dynamic_credential_entry
    entry = dynamic_credential_entry("custom.quicknode")
    surrogate = str(entry["surrogate"]).strip()
    path = f"/{surrogate}/"
    out = []
    CH = 10
    for s in range(0, len(calls), CH):
        chunk = calls[s:s + CH]
        payload = [{"jsonrpc": "2.0", "id": k + 1, "method": m, "params": p}
                   for k, (m, p) in enumerate(chunk)]
        body = _json.dumps(payload).encode()
        conn = ProxyHTTPSConnection(HOST, 443, timeout=timeout)
        try:
            conn.request("POST", path, body=body, headers={"Content-Type": "application/json"})
            resp = conn.getresponse()
            raw = resp.read()
            status = resp.status
        finally:
            conn.close()
        if status != 200:
            raise IOError(f"HTTP {status}: {raw[:200]}")
        data = _json.loads(raw.decode("utf-8"))
        if not isinstance(data, list) or len(data) != len(chunk):
            raise IOError(f"unexpected batch response: {str(data)[:200]}")
        out.extend(sorted(data, key=lambda it: it["id"]))
        if s + CH < len(calls):
            time.sleep(1.2)
    return out

entries = json.load(open("/home/hatch/workspace/asset-sell-watch/pending-swaps.json"))["entries"]
t0 = time.time()
out = {"run": "2026-11-19 22:51 WIB", "via": "quicknode", "elapsed_s": None,
       "gas_price_wei": None, "results": []}

# --- Batch A: gasPrice + balanceOf + getPair ---
calls = [("eth_gasPrice", [])]
for e in entries:
    calls.append(("eth_call", [{"to": e["token"], "data": "0x70a08231" + pad(W)}, "latest"]))
for e in entries:
    calls.append(("eth_call", [{"to": FACT, "data": "0xe6a43905" + pad(e["token"]) + pad(WBNB)}, "latest"]))
try:
    resA = rpc_batch(calls, timeout=90)
except Exception as ex:
    out["batchA_error"] = str(ex)
    print(json.dumps(out, indent=1))
    sys.exit(1)
n = len(entries)
if "error" in resA[0]:
    out["batchA_error"] = str(resA[0]["error"])
    print(json.dumps(out, indent=1))
    sys.exit(1)
out["gas_price_wei"] = int(resA[0]["result"], 16)
out["gas_price_gwei"] = int(resA[0]["result"], 16) / 1e9
balances = []
pairs = []
for i in range(n):
    it = resA[1 + i]
    balances.append(int(it["result"], 16) if "result" in it else None)
    if "result" not in it:
        out.setdefault("errors", []).append(f"balance {entries[i]['symbol']}: {it.get('error')}")
    it2 = resA[1 + n + i]
    if "result" in it2:
        pairs.append("0x" + it2["result"][-40:] if int(it2["result"], 16) != 0 else None)
    else:
        pairs.append(None)
        out.setdefault("errors", []).append(f"getPair {entries[i]['symbol']}: {it2.get('error')}")

rows = []
for i, e in enumerate(entries):
    rows.append({"symbol": e["symbol"], "token": e["token"],
                 "balance_raw": str(balances[i]) if balances[i] is not None else None,
                 "balance_human": (balances[i] / (10 ** e.get("decimals", 18))) if balances[i] is not None else None,
                 "pair_wbnb": pairs[i]})

# --- Batch B: getReserves ---
idx_pairs = [i for i in range(n) if pairs[i]]
if idx_pairs:
    callsB = [("eth_call", [{"to": pairs[i], "data": "0x0902f1ac"}, "latest"]) for i in idx_pairs]
    try:
        resB = rpc_batch(callsB, timeout=90)
        for j, i in enumerate(idx_pairs):
            it = resB[j]
            if "result" in it:
                r = it["result"]
                rows[i]["reserves"] = [str(int(r[2:66], 16)), str(int(r[66:130], 16))]
            else:
                rows[i]["reserves_error"] = str(it.get("error"))[:200]
    except Exception as ex:
        for i in idx_pairs:
            rows[i]["reserves_error"] = str(ex)[:200]

# --- Batch C: getAmountsOut ---
idx_q = [i for i in idx_pairs
         if rows[i].get("reserves") and int(rows[i]["reserves"][0]) > 0 and int(rows[i]["reserves"][1]) > 0]
if idx_q:
    callsC = []
    idx_q2 = []
    for i in idx_q:
        e = entries[i]
        sell = int(e["amount_to_sell_raw"]) if e.get("amount_to_sell_raw") else balances[i]
        if sell is None:
            rows[i]["quote_error"] = "saldo gagal dibaca (rate-limit) — quote dilewati run ini"
            continue
        idx_q2.append(i)
        rows[i]["sell_amount_raw"] = str(sell)
        data = ("0xd06ca61f" + format(sell, '064x')
                + "0000000000000000000000000000000000000000000000000000000000000040"
                + "0000000000000000000000000000000000000000000000000000000000000002"
                + pad(e["token"]) + pad(WBNB))
        callsC.append(("eth_call", [{"to": ROUT, "data": data}, "latest"]))
    try:
        resC = rpc_batch(callsC, timeout=90)
        for j, i in enumerate(idx_q2):
            it = resC[j]
            if "result" in it:
                q = it["result"]
                rows[i]["quote_raw"] = str(int(q[194:258], 16))
                rows[i]["quote_bnb"] = int(q[194:258], 16) / 1e18
            else:
                rows[i]["quote_error"] = str(it.get("error"))[:200]
    except Exception as ex:
        for i in idx_q2:
            rows[i]["quote_error"] = str(ex)[:200]

# --- Batch D: sale-state probes (revert = absent) ---
probes = ["launched()", "tradingOpen()", "isOpen()", "opened()", "phase()"]
callsD, metaD = [], []
for i, e in enumerate(entries):
    sc = e.get("sale_contract")
    if not sc:
        continue
    for f in probes:
        callsD.append(("eth_call", [{"to": sc, "data": "0x" + sel(f)}, "latest"]))
        metaD.append((i, f))
if callsD:
    try:
        resD = rpc_batch(callsD, timeout=120)
        for k, (i, f) in enumerate(metaD):
            it = resD[k]
            st = rows[i].setdefault("sale_state", {})
            st[f] = it["result"] if "result" in it else "revert/absent"
    except Exception as ex:
        for i, e in enumerate(entries):
            if e.get("sale_contract"):
                rows[i]["sale_state_error"] = str(ex)[:200]

out["results"] = rows
out["elapsed_s"] = round(time.time() - t0, 1)
print(json.dumps(out, indent=1))
