#!/usr/bin/env python3
"""Third attempt 22:51 run — fast_rpc batch_race for phase 1 (gas + balances + getPair)."""
import json, sys
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import batch_race
from eth_abi import encode
from eth_utils import keccak

W = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
FACTORY = "0xca143ce32fe78f1f7019d7d551a6402fc5350c73"
WBNB = "0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c"
def sel(sig): return keccak(text=sig).hex()[:8]

with open("/home/hatch/workspace/asset-sell-watch/pending-swaps.json") as f:
    ENTRIES = json.load(f)["entries"]

calls = [("eth_gasPrice", [])]
for e in ENTRIES:
    calls.append(("eth_call", [{"to": e["token"], "data": "0x" + sel("balanceOf(address)") + encode(["address"], [W]).hex()}, "latest"]))
for e in ENTRIES:
    calls.append(("eth_call", [{"to": FACTORY, "data": "0x" + sel("getPair(address,address)") + encode(["address", "address"], [e["token"], WBNB]).hex()}, "latest"]))
res = batch_race(calls, timeout=10)
def u256(h):
    try: return int(h, 16) if h else 0
    except Exception: return 0
gas = u256(res[0]) if res and res[0] else None
n = len(ENTRIES)
out = {"run": "pending-coin-swap-watch 2026-11-13 22:51 WIB (attempt 3, fast_rpc batch_race)",
       "wallet": W, "gas_price_gwei": gas/1e9 if gas else None,
       "gas_est_300k_bnb": gas*300000/1e18 if gas else None, "entries": []}
for i, e in enumerate(ENTRIES):
    item = {"symbol": e["symbol"], "token": e["token"]}
    bal_h, pair_h = res[1+i], res[1+n+i]
    if bal_h is None:
        item["status"] = "rpc_failed_balance"; out["entries"].append(item); continue
    bal = u256(bal_h)
    item["balance_raw"] = str(bal); item["balance_human"] = bal / 10**e.get("decimals", 18)
    if bal == 0:
        item["status"] = "empty"; out["entries"].append(item); continue
    pair = ("0x" + pair_h[-40:]) if pair_h and u256(pair_h) else None
    item["pair_wbnb"] = pair
    item["status"] = "no_pair" if not pair else "pair_found"
    out["entries"].append(item)
print(json.dumps(out, indent=1))
