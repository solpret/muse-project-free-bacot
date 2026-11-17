#!/usr/bin/env python3
"""Run 63 detail 2: verify 0xbff868... is the CORLA/WBNB PCS pair; name/symbol
of 3 created contracts; sum BNB values of the 27 wallets' swaps. Read-only."""
import json, sys, time
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
import fast_rpc
from eth_abi import decode as abi_decode, encode as abi_encode
from Crypto.Hash import keccak

def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode()); return "0x" + k.hexdigest()[:8]

def call(to, data):
    for _ in range(3):
        try:
            return fast_rpc.race("eth_call", [{"to": to, "data": data}, "latest"])
        except Exception as e:
            print("call retry", e, flush=True); time.sleep(3)
    return None

FACTORY = "0xca143ce32fe78f1f7019d7d551a6402fc5350c"
WBNB = "0xbb4cdb9cbdb36b01bd1cbebf2de08d9173bc095c"
TOK = "0x4a9c499574ea003846e81522d59aa4c27ca47777"
# getPair(address,address)
data = sel("getPair(address,address)") + abi_encode(["address", "address"], [TOK, WBNB]).hex()
r = call(FACTORY, data)
pair = ("0x" + r[-40:]) if r else None
print("factory getPair(CORLA,WBNB) =", pair, flush=True)
print("sample Transfer from was 0xbff868d924c19f3b9cd7309f5be7c2dcc48ba839 -> match:", (pair or "").lower() == "0xbff868d924c19f3b9cd7309f5be7c2dcc48ba839", flush=True)
if pair:
    for fn in ["token0()", "token1()"]:
        rr = call(pair, sel(fn))
        print(fn, ("0x" + rr[-40:]) if rr else None, flush=True)

created = json.load(open("/home/hatch/workspace/narrative-pulse/scan-runs/run63-created.json"))
for h, c in created[:3]:
    if not c:
        continue
    for fn in ["name()", "symbol()"]:
        rr = call(c, sel(fn))
        try:
            print(c[:12], fn, abi_decode(["string"], bytes.fromhex(rr[2:]))[0] if rr else None, flush=True)
        except Exception as e:
            print(c[:12], fn, "decode ERR", (rr or "")[:80], flush=True)

# sum BNB values of the 27 wallets' in-window txs
sent = json.load(open("/home/hatch/workspace/narrative-pulse/scan-runs/run63-sent.json"))
paid = json.load(open("/home/hatch/workspace/narrative-pulse/scan-runs/run63-paid.json"))
recv = set(paid[TOK])
tot = 0; n_nonzero = 0
for w, rr in sent["results"].items():
    if w in recv:
        for t in rr["in_window"]:
            v = int(t["value"], 16)
            if v:
                tot += v; n_nonzero += 1
print("27 wallets: nonzero-value txs =", n_nonzero, "total BNB value =", tot / 1e18, flush=True)
print("DONE", flush=True)
