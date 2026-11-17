#!/usr/bin/env python3
"""Retry read-only pending-swap check (run 2026-11-16 02:51 WIB) using fast_rpc batch_race.
Covers: balances that failed, gas price, YYDS quote, and recorded-pair verification
for 币安加油 / JINMA / LUCKY777 (earlier run said no_pair, contradicting recorded pairs —
suspected 403 flakiness). Read-only, no audit/preview/execution."""
import sys, json
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import batch_race, race
from eth_abi import encode, decode
from eth_utils import keccak

W = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
ROUTER = "0x10ED43C718714eb63d5aA57B78B54704E256024E"
FACTORY = "0xca143ce32fe78f1f7019d7d551a6402fc5350c73"
WBNB = "0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c"

def sel(sig):
    return keccak(text=sig).hex()[:8]

def call(to, data):
    return ("eth_call", [{"to": to, "data": data}, "latest"])

def u256(h):
    try:
        return int(h, 16) if h else 0
    except Exception:
        return 0

TOK = {
 "BNBbaby": "0xd0079025a9bb66a7a1de991de2e4326faba35729",
 "WW3": "0xf62628D99B28535ee593Ab5D6dFE7D914f5edca0",
 "LUCKY777": "0xc6D4ec8CB889aFBa9f251606001457644E260f7D",
 "YYDS": "0xd23be069c3c3a7f631af52584a16a9e46bb41da1",
 "币安加油": "0x397BF425926F521Ac5BEbe5062793BB224e3eF8f",
 "JINMA": "0xe4517E6718b24D5725956ac7A90686592a7b1539",
 "CHEEMSA": "0x00b4bdA5BBf83A72f1252CCEf361f107f5a728b2",
}
RECORDED_PAIR = {
 "币安加油": "0xc939e2b49eea548c4539e45b4e355c2b2aa464d6",
 "JINMA": "0xaa91fd1b1fc70888f5df17784720b752472e99da",
 "LUCKY777": "0x81afde1cddf0d277580b8e524361e0a7ea2983c6",
 "YYDS": "0xd15c928b7b777cac7d613fe840c6ec3de8e4edda",
}

calls = []
labels = []
# gas price
calls.append(("eth_gasPrice", [])); labels.append("gasPrice")
# balances
for sym, tok in TOK.items():
    calls.append(call(tok, "0x" + sel("balanceOf(address)") + encode(["address"], [W]).hex()))
    labels.append(f"bal:{sym}")
# getPair for the recorded-pair tokens + YYDS
for sym in ["币安加油", "JINMA", "LUCKY777", "YYDS"]:
    tok = TOK[sym]
    calls.append(call(FACTORY, "0x" + sel("getPair(address,address)") + encode(["address", "address"], [tok, WBNB]).hex()))
    labels.append(f"pair:{sym}")
# YYDS quote for full balance (0.0001776 = 177600000000000 raw)
calls.append(call(ROUTER, "0x" + sel("getAmountsOut(uint256,address[])") + encode(["uint256", "address[]"], [177600000000000, [TOK["YYDS"], WBNB]]).hex()))
labels.append("quote:YYDS")
# CHEEMSA tradingOpen + launched
calls.append(call(TOK["CHEEMSA"], "0x" + sel("tradingOpen()"))); labels.append("cheemsa:tradingOpen")
calls.append(call(TOK["CHEEMSA"], "0x" + sel("launched()"))); labels.append("cheemsa:launched")
# reserves for recorded pairs
for sym, pair in RECORDED_PAIR.items():
    calls.append(call(pair, "0x" + sel("getReserves()"))); labels.append(f"reserves:{sym}")

res = batch_race(calls, timeout=15)
out = {}
for lab, r in zip(labels, res):
    out[lab] = r
    if isinstance(r, str) and r.startswith("0x"):
        try:
            out[lab + "_u256"] = u256(r)
        except Exception:
            pass
print(json.dumps(out, indent=1))

# human summary
gp = out.get("gasPrice")
if gp and isinstance(gp, str) and gp.startswith("0x"):
    gwei = u256(gp) / 1e9
    print(f"\nGAS: {gwei:.3f} gwei -> 300k gas est = {u256(gp)*300000/1e18:.8f} BNB ; 2x = {u256(gp)*600000/1e18:.8f} BNB")
else:
    print("\nGAS: FAILED", gp)
for sym in TOK:
    b = out.get(f"bal:{sym}")
    print(f"BAL {sym}: {u256(b)/1e18 if b and isinstance(b,str) and b.startswith('0x') else b}")
for sym in ["币安加油", "JINMA", "LUCKY777", "YYDS"]:
    p = out.get(f"pair:{sym}")
    print(f"PAIR {sym}: {p} (recorded {RECORDED_PAIR[sym]})")
    r = out.get(f"reserves:{sym}")
    if r and isinstance(r, str) and r.startswith("0x"):
        try:
            r0, r1, _ = decode(["uint112", "uint112", "uint32"], bytes.fromhex(r[2:]))
            print(f"  reserves: {r0} / {r1}")
        except Exception as e:
            print("  reserves decode err", e)
    else:
        print("  reserves:", r)
q = out.get("quote:YYDS")
if q and isinstance(q, str) and q.startswith("0x"):
    try:
        outs = decode(["uint256[]"], bytes.fromhex(q[2:]))[0]
        print(f"QUOTE YYDS: {outs[1]/1e18:.10f} BNB raw={outs[1]}")
    except Exception as e:
        print("QUOTE YYDS decode err", e)
else:
    print("QUOTE YYDS:", q)
print("CHEEMSA tradingOpen:", out.get("cheemsa:tradingOpen"), "launched:", out.get("cheemsa:launched"))
