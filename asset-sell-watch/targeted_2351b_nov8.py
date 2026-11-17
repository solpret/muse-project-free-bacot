#!/usr/bin/env python3
"""Follow-up for 23:51 run: launched()/phase() for ORBITA, WW3, JINCHAN sale contracts
skipped on the targeted-run deadline. Read-only, short timeouts."""
import json, time, urllib.request
from eth_abi import decode
from eth_utils import keccak
RPCS = ["https://bsc-dataseed1.binance.org/", "https://bsc.publicnode.com"]
def sel(sig): return keccak(text=sig).hex()[:8]
def call_one(rpc, to, data):
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                       "params": [{"to": to, "data": data}, "latest"]}).encode()
    req = urllib.request.Request(rpc, data=body, headers={"Content-Type": "application/json"})
    r = json.loads(urllib.request.urlopen(req, timeout=8).read())
    if r.get("error") or not r.get("result"): return None
    return r["result"]
def call(to, data):
    for rpc in RPCS:
        try:
            v = call_one(rpc, to, data)
            if v is not None: return v, rpc
        except Exception as e:
            continue
    return None, None
sales = {"ORBITA": "0x19b8d7613A6C2E4168a6a0Bb97ca0c842035d709",
         "WW3": "0x1Aa9797cC762b838388566Daa45A56b1709F4Bbe",
         "JINCHAN": "0xccc127D1A7Ef1e385757784a9878F7279BF3B19D"}
out = {"sale_contracts": {}}
for sym, sc in sales.items():
    e = {}
    lh, rpc = call(sc, "0x" + sel("launched()")); e["launched_raw"] = lh; e["launched_rpc"] = rpc
    if lh:
        try: e["launched"] = decode(["bool"], bytes.fromhex(lh[2:]))[0]
        except Exception: e["launched"] = None
    ph, rpc2 = call(sc, "0x" + sel("phase()")); e["phase_raw"] = ph; e["phase_rpc"] = rpc2
    if ph:
        try: e["phase"] = decode(["uint256"], bytes.fromhex(ph[2:]))[0]
        except Exception: e["phase"] = None
    out["sale_contracts"][sym] = e
print(json.dumps(out, indent=1))
