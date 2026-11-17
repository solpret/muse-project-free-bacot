#!/usr/bin/env python3
"""Retry read for 3 rpc-failed balances + JINMA reserves + 币安加油 pair.
Read-only. Uses fast_rpc batch_race."""
import sys, json
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import batch_race, call_many
from eth_abi import encode
from eth_utils import keccak

W = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
FACTORY = "0xca143ce32fe78f1f7019d7d551a6402fc5350c73"
WBNB = "0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c"
ROUTER = "0x10ED43C718714eb63d5aA57B78B54704E256024E"

def sel(sig):
    return keccak(text=sig).hex()[:8]

def enc(to, data):
    return {"to": to, "data": "0x" + data}

calls = []
labels = []
# balances
for sym, tok in [
    ("QAGENT", "0x25e915EEE91411b0AC3273531dbaDc34e0EAA5eB"),
    ("YYDS", "0xd23be069c3c3a7f631af52584a16a9e46bb41da1"),
    ("WW3", "0xf62628D99B28535ee593Ab5D6dFE7D914f5edca0"),
]:
    calls.append(("eth_call", [{"to": tok, "data": "0x" + sel("balanceOf(address)") + encode(["address"], [W]).hex()}, "latest"]))
    labels.append(f"balance_{sym}")
# 币安加油 pair
calls.append(("eth_call", [{"to": FACTORY, "data": "0x" + sel("getPair(address,address)") + encode(["address", "address"], ["0x397BF425926F521Ac5BEbe5062793BB224e3eF8f", WBNB]).hex()}, "latest"]))
labels.append("pair_BIANJIAYOU")
# JINMA pair reserves + token0/token1
JINMA_PAIR = "0xaa91fd1b1fc70888f5df17784720b752472e99da"
calls.append(("eth_call", [{"to": JINMA_PAIR, "data": "0x" + sel("getReserves()")}, "latest"]))
labels.append("reserves_JINMA")
calls.append(("eth_call", [{"to": JINMA_PAIR, "data": "0x" + sel("token0()")}, "latest"]))
labels.append("token0_JINMA")
calls.append(("eth_call", [{"to": JINMA_PAIR, "data": "0x" + sel("token1()")}, "latest"]))
labels.append("token1_JINMA")
# LUCKY777 token0 (was null)
calls.append(("eth_call", [{"to": "0x81afde1cddf0d277580b8e524361e0a7ea2983c6", "data": "0x" + sel("token0()")}, "latest"]))
labels.append("token0_LUCKY777")

try:
    res = batch_race(calls, timeout=10)
except Exception as e:
    res = call_many(calls)
out = {}
for lab, r in zip(labels, res):
    out[lab] = r
print(json.dumps(out, indent=1))
