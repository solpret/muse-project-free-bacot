#!/usr/bin/env python3
"""Second targeted retry, pending-coin-swap-watch 2026-11-08 12:51 WIB.
Covers: fresh gasPrice (failed in main + targeted runs), BIA reserves direct
on known pair 0xc939e2b49eea548c4539e45b4e355c2b2aa464d6 (getPair null both
runs), launched()/phase() for the 6 sale contracts skipped by deadline.
Read-only. Hard per-call timeout 8s, global deadline 100s."""
import json, time, urllib.request
from eth_abi import encode, decode
from eth_utils import keccak

DEADLINE = time.time() + 100
RPCS = ["https://bsc-dataseed1.binance.org/", "https://bsc.publicnode.com",
        "https://bsc-dataseed.binance.org/"]

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
    for rpc in RPCS:
        if time.time() > DEADLINE:
            return None, None
        try:
            v = call_one(rpc, to, data)
            if v is not None:
                return v, rpc
        except Exception:
            continue
    return None, None

out = {}
gp = None
for rpc in RPCS:
    try:
        body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_gasPrice", "params": []}).encode()
        req = urllib.request.Request(rpc, data=body, headers={"Content-Type": "application/json"})
        r = json.loads(urllib.request.urlopen(req, timeout=8).read())
        if r.get("result"):
            gp = int(r["result"], 16)
            out["gas_rpc"] = rpc
            break
    except Exception:
        continue
out["gas_price_gwei"] = gp / 1e9 if gp else None
out["gas_est_300k_bnb"] = gp * 300000 / 1e18 if gp else None
out["gas_2x_threshold_bnb"] = 2 * gp * 300000 / 1e18 if gp else None

bia_pair = "0xc939e2b49eea548c4539e45b4e355c2b2aa464d6"
res_h, rrpc = call(bia_pair, "0x" + sel("getReserves()"))
bia = {"reserves_rpc": rrpc}
if res_h:
    try:
        r0, r1, _ = decode(["uint112", "uint112", "uint32"], bytes.fromhex(res_h[2:]))
        bia["reserves"] = [str(r0), str(r1)]
        bia["status"] = "pair_empty" if (r0 == 0 or r1 == 0) else "has_liquidity"
    except Exception as ex:
        bia["reserves_error"] = str(ex)
else:
    bia["status"] = "reserves_failed"
out["BIA"] = bia

sales = {
    "QAGENT": "0xE3a4f3099a2136e0e66202A665815caB8FFA2704",
    "YYDS": "0x62AB0519dED1B70481021D31fa6BAcB7450b78F3",
    "BIA": "0xC9b4d42ABe8966496aa68a736938Bf2D508F7a91",
    "PACTURE": "0x95AF9fe16fE5c1741b5E3F1b3b045a8c2470eca9",
    "ORBITA": "0x19b8d7613A6C2E4168a6a0Bb97ca0c842035d709",
    "WW3": "0x1Aa9797cC762b838388566Daa45A56b1709F4Bbe",
}
sc_out = {}
for sym, sc in sales.items():
    if time.time() > DEADLINE:
        sc_out[sym] = {"status": "skipped_deadline"}
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
    sc_out[sym] = entry
out["sale_contracts"] = sc_out
print(json.dumps(out, indent=1))
