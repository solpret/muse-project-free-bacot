#!/usr/bin/env python3
"""Targeted retry: YYDS balanceOf + getPair + reserves + quote, run 1551."""
import json, sys
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import call_many
from eth_abi import encode
from eth_utils import keccak

W = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
TOK = "0xd23be069c3c3a7f631af52584a16a9e46bb41da1"
FACTORY = "0xca143ce32fe78f1f7019d7d551a6402fc5350c73"
WBNB = "0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c"
ROUTER = "0x10ED43C718714eb63d5aA57B78B54704E256024E"
def sel(s): return keccak(text=s).hex()[:8]
calls = [
    {"to": TOK, "data": "0x" + sel("balanceOf(address)") + encode(["address"], [W]).hex()},
    {"to": FACTORY, "data": "0x" + sel("getPair(address,address)") + encode(["address","address"], [TOK, WBNB]).hex()},
]
res = call_many(calls, timeout=15)
print(json.dumps({"calls": res}, indent=1))
