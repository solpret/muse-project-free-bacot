#!/usr/bin/env python3
"""Resilient targeted retry for pending-coin-swap-watch 2026-11-09 18:51 WIB.
RPC egress severely degraded: all public BSC endpoints timing out at 8s race /
15s batch. Uses longer timeouts (race 30s, batch 45s) and per-call try/except
so partial results survive. Writes incremental JSON after every entry.
Read-only."""
import sys, json
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import race, call_many
from eth_abi import encode, decode
from eth_utils import keccak

W = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
ROUTER = "0x10ED43C718714eb63d5aA57B78B54704E256024E"
FACTORY = "0xca143ce32fe78f1f7019d7d551a6402fc5350c73"
WBNB = "0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c"
OUT = "/home/hatch/workspace/asset-sell-watch/targeted_1851_nov9.json"
RACE_T = 30
BATCH_T = 45

def sel(sig): return keccak(text=sig).hex()[:8]
def u256(h):
    try: return int(h, 16) if h else 0
    except Exception: return 0

def safe_call_many(calls):
    try:
        return call_many(calls, timeout=BATCH_T)
    except Exception as e:
        return [None] * len(calls)

def safe_race(method, params):
    try:
        return race(method, params, timeout=RACE_T)
    except Exception:
        return None

data = json.load(open("/home/hatch/workspace/asset-sell-watch/pending-swaps.json"))
out = {"entries": []}
gp_raw = safe_race("eth_gasPrice", [])
gp = u256(gp_raw) if gp_raw else None
out["gas_price_wei"] = gp
out["gas_price_gwei"] = gp / 1e9 if gp else None
out["gas_est_300k_bnb"] = gp * 300000 / 1e18 if gp else None
json.dump(out, open(OUT, "w"), indent=1, ensure_ascii=False)

calls = []
for e in data["entries"]:
    tok = e["token"]
    calls.append((tok, "0x" + sel("balanceOf(address)") + encode(["address"], [W]).hex()))
    calls.append((FACTORY, "0x" + sel("getPair(address,address)") + encode(["address", "address"], [tok, WBNB]).hex()))
res = safe_call_many(calls)

for i, e in enumerate(data["entries"]):
    sym, tok = e["symbol"], e["token"]
    item = {"symbol": sym, "token": tok, "registered_amount_human": e.get("amount_human"),
            "amount_to_sell_raw": e.get("amount_to_sell_raw"), "reason_prev": e.get("reason")}
    bal_h, pair_h = res[2*i], res[2*i+1]
    if bal_h is None:
        item["status"] = "rpc_failed_balance"; out["entries"].append(item)
        json.dump(out, open(OUT, "w"), indent=1, ensure_ascii=False); continue
    bal = u256(bal_h)
    item["balance_raw"] = str(bal); item["balance_human"] = bal / 1e18
    if bal == 0:
        item["status"] = "empty"; out["entries"].append(item)
        json.dump(out, open(OUT, "w"), indent=1, ensure_ascii=False); continue
    pair = ("0x" + pair_h[-40:]) if pair_h and u256(pair_h) else None
    item["pair_wbnb"] = pair
    if not pair:
        item["status"] = "no_pair"; out["entries"].append(item)
        json.dump(out, open(OUT, "w"), indent=1, ensure_ascii=False); continue
    r = safe_call_many([(pair, "0x" + sel("getReserves()"))])
    res_h = r[0]
    if res_h:
        try:
            r0, r1, _ = decode(["uint112", "uint112", "uint32"], bytes.fromhex(res_h[2:]))
            item["reserves"] = [str(r0), str(r1)]
            if r0 == 0 or r1 == 0:
                item["status"] = "pair_empty"; out["entries"].append(item)
                json.dump(out, open(OUT, "w"), indent=1, ensure_ascii=False); continue
        except Exception as ex:
            item["reserves_error"] = str(ex)
    sell_amt = int(e["amount_to_sell_raw"]) if e.get("amount_to_sell_raw") else bal
    item["sell_amount_raw"] = str(sell_amt)
    q = safe_call_many([(ROUTER, "0x" + sel("getAmountsOut(uint256,address[])") + encode(["uint256", "address[]"], [sell_amt, [tok, WBNB]]).hex())])
    if q[0]:
        try:
            outs = decode(["uint256[]"], bytes.fromhex(q[0][2:]))[0]
            item["quote_bnb"] = outs[1] / 1e18 if len(outs) == 2 else None
            item["quote_raw"] = str(outs[1]) if len(outs) == 2 else None
        except Exception as ex:
            item["quote_error"] = str(ex)
    if item.get("quote_bnb") is not None and gp:
        item["quote_ge_2x_gas"] = item["quote_bnb"] >= 2 * gp * 300000 / 1e18
        item["status"] = "executable_candidate" if item["quote_ge_2x_gas"] else "quote_dust"
    elif item.get("quote_bnb") is None:
        item["status"] = "no_quote"
    sc = e.get("sale_contract")
    if sc:
        lh = safe_call_many([(sc, "0x" + sel("launched()"))])[0]
        item["sale_contract"] = sc
        item["launched_raw"] = lh
        if lh is not None:
            try:
                item["launched"] = decode(["bool"], bytes.fromhex(lh[2:]))[0]
            except Exception:
                item["launched"] = None
    out["entries"].append(item)
    json.dump(out, open(OUT, "w"), indent=1, ensure_ascii=False)

print(json.dumps(out, indent=1, ensure_ascii=False))
