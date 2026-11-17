#!/usr/bin/env python3
"""Lean targeted check for pending-coin-swap-watch 2026-11-08 17:51 WIB run.
Main run (pending_check.py, bsc-dataseed.binance.org) succeeded cleanly:
all 9 balances verified fresh, gasPrice 0.05 gwei, no RPC failures.
Only YYDS reached launched() (null); no_pair / pair_empty entries skipped
the sale-contract state read. This script reads launched()/phase() for all
9 sale contracts to detect a refund/failed phase (body step 4).
Read-only. Hard per-call timeout 8s, max 2 RPCs per call, global deadline 110s."""
import json, time, urllib.request
from eth_abi import encode, decode
from eth_utils import keccak

DEADLINE = time.time() + 110
RPCS = ["https://bsc-dataseed1.binance.org/", "https://bsc.publicnode.com"]

def sel(sig):
    return keccak(text=sig).hex()[:8]

def call_one(rpc, to, data):
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                       "params": [{"to": to, "data": data}, "latest"]}).encode()
    req = urllib.request.Request(rpc, data=body, headers={"Content-Type": "application/json"})
    r = json.loads(urllib.request.urlopen(req, timeout=8).read())
    if r.get("error") or not r.get("result"):
        return None
    return r["result"]

def call(to, data):
    for rpc in RPCS[:2]:
        if time.time() > DEADLINE:
            return None, None
        try:
            v = call_one(rpc, to, data)
            if v is not None:
                return v, rpc
        except Exception:
            continue
    return None, None

sales = {
    "POA": "0x74d9b5477e7fa818298f927966452f2eb9c5fa5e",
    "BNBbaby": "0xbb7ed59ca41ea03cf20084a8c9de94244b7b2637",
    "PATCH": "0xCaFa8f3563E1ACd57abe24C42663BD1D103651C3",
    "QAGENT": "0xE3a4f3099a2136e0e66202A665815caB8FFA2704",
    "YYDS": "0x62AB0519dED1B70481021D31fa6BAcB7450b78F3",
    "BIA": "0xC9b4d42ABe8966496aa68a736938Bf2D508F7a91",
    "PACTURE": "0x95AF9fe16fE5c1741b5E3F1b3b045a8c2470eca9",
    "ORBITA": "0x19b8d7613A6C2E4168a6a0Bb97ca0c842035d709",
    "WW3": "0x1Aa9797cC762b838388566Daa45A56b1709F4Bbe",
}
out = {"sale_contracts": {}}
for sym, sc in sales.items():
    if time.time() > DEADLINE:
        out["sale_contracts"][sym] = {"status": "skipped_deadline"}
        continue
    entry = {}
    lh, _ = call(sc, "0x" + sel("launched()"))
    entry["launched_raw"] = lh
    if lh:
        try:
            entry["launched"] = decode(["bool"], bytes.fromhex(lh[2:]))[0]
        except Exception:
            entry["launched"] = None
    ph, _ = call(sc, "0x" + sel("phase()"))
    entry["phase_raw"] = ph
    if ph:
        try:
            entry["phase"] = decode(["uint256"], bytes.fromhex(ph[2:]))[0]
        except Exception:
            entry["phase"] = None
    out["sale_contracts"][sym] = entry
print(json.dumps(out, indent=1))
