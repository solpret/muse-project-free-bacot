#!/usr/bin/env python3
"""Second targeted retry for pending-coin-swap-watch 2026-11-09 03:51 WIB run.
Uses fast_rpc (race + batch across many BSC endpoints) for the 5 entries whose
balance read failed in the main run (dataseed timeouts): POA, BNBbaby, YYDS,
币圈加油, JINCHAN. Read-only."""
import sys, json
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import race, call_many
from eth_abi import encode, decode
from eth_utils import keccak

W = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
ROUTER = "0x10ED43C718714eb63d5aA57B78B54704E256024E"
FACTORY = "0xca143ce32fe78f1f7019d7d551a6402fc5350c73"
WBNB = "0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c"

def sel(sig): return keccak(text=sig).hex()[:8]
def u256(h):
    try: return int(h, 16) if h else 0
    except Exception: return 0

TOKENS = [
    ("POA", "0x21bc810818d9c9c767ba73c543f67a989fb5a543", "28000000000000000000000"),
    ("BNBbaby", "0xd0079025a9bb66a7a1de991de2e4326faba35729", None),
    ("YYDS", "0xd23be069c3c3a7f631af52584a16a9e46bb41da1", None),
    ("\u5e01\u5b89\u52a0\u6cb9", "0x397BF425926F521Ac5BEbe5062793BB224e3eF8f", "50000000000000000000000000"),
    ("JINCHAN", "0xE2DFa6c6c7189a885bC0919527A303319f4EEffC", "50000000000000000000000"),
]

out = {}
gp = race("eth_gasPrice", [])
out["gas_price_wei"] = gp
out["gas_price_gwei"] = gp / 1e9 if gp else None
out["gas_est_300k_bnb"] = gp * 300000 / 1e18 if gp else None

calls = []
for sym, tok, _ in TOKENS:
    calls.append((tok, "0x" + sel("balanceOf(address)") + encode(["address"], [W]).hex()))
    calls.append((FACTORY, "0x" + sel("getPair(address,address)") + encode(["address", "address"], [tok, WBNB]).hex()))
res = call_many(calls)
out["entries"] = []
for i, (sym, tok, sell_raw) in enumerate(TOKENS):
    item = {"symbol": sym, "token": tok}
    bal_h, pair_h = res[2*i], res[2*i+1]
    if bal_h is None:
        item["status"] = "rpc_failed_balance"; out["entries"].append(item); continue
    bal = u256(bal_h)
    item["balance_raw"] = str(bal); item["balance_human"] = bal / 1e18
    if bal == 0:
        item["status"] = "empty"; out["entries"].append(item); continue
    pair = ("0x" + pair_h[-40:]) if pair_h and u256(pair_h) else None
    item["pair_wbnb"] = pair
    if not pair:
        item["status"] = "no_pair"; out["entries"].append(item); continue
    r = call_many([(pair, "0x" + sel("getReserves()"))])
    res_h = r[0]
    if res_h:
        r0, r1, _ = decode(["uint112", "uint112", "uint32"], bytes.fromhex(res_h[2:]))
        item["reserves"] = [str(r0), str(r1)]
        if r0 == 0 or r1 == 0:
            item["status"] = "pair_empty"; out["entries"].append(item); continue
    sell_amt = int(sell_raw) if sell_raw else bal
    item["sell_amount_raw"] = str(sell_amt)
    q = call_many([(ROUTER, "0x" + sel("getAmountsOut(uint256,address[])") + encode(["uint256", "address[]"], [sell_amt, [tok, WBNB]]).hex())])
    if q[0]:
        outs = decode(["uint256[]"], bytes.fromhex(q[0][2:]))[0]
        item["quote_bnb"] = outs[1] / 1e18 if len(outs) == 2 else None
        item["quote_raw"] = str(outs[1]) if len(outs) == 2 else None
    if item.get("quote_bnb") is not None and gp:
        item["quote_ge_2x_gas"] = item["quote_bnb"] >= 2 * gp * 300000 / 1e18
        item["status"] = "executable_candidate" if item["quote_ge_2x_gas"] else "quote_dust"
    elif item.get("quote_bnb") is None:
        item["status"] = "no_quote"
    out["entries"].append(item)

print(json.dumps(out, indent=1))
