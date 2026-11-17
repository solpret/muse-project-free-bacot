#!/usr/bin/env python3
"""Parent fresh verification for run 2026-11-07 0201: Jager Agent Pass + FUGUI sets.
Read-only eth_call via fast_rpc. No signing, no preview, no mint."""
import json, sys
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _single
from eth_hash.auto import keccak

MAIN = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/"]
OUT = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/run-2026-11-07-0201-verify.json"

def sel(sig):
    return "0x" + keccak(sig.encode()).hex()[:8]

def enc_addr(a):
    return a.lower().replace("0x", "").rjust(64, "0")

def call(addr, sig, args=""):
    data = sel(sig) + args
    for ep in EPS:
        try:
            r = _single(ep, "eth_call", [{"to": addr, "data": data}, "latest"], 10, retries=0)
            if isinstance(r, str) and r.startswith("0x"):
                return r
        except Exception:
            continue
    return None

def u(r):
    if r is None:
        return None
    try:
        return int(r, 16)
    except Exception:
        return r

def b(r):
    if r is None:
        return None
    return int(r, 16) != 0

def block():
    for ep in EPS:
        try:
            r = _single(ep, "eth_blockNumber", [], 10, retries=0)
            if isinstance(r, str):
                return int(r, 16)
        except Exception:
            continue
    return None

res = {"run": "2026-11-07-0201", "block": block()}

# Jager Agent Pass
J = "0x951f705feB9dCc95D58b445BE58b869724E50707"
res["jager"] = {
    "address": J,
    "totalMinted": u(call(J, "totalMinted()")),
    "MAX_SUPPLY": u(call(J, "MAX_SUPPLY()")),
    "freeMinted": u(call(J, "freeMinted()")),
    "balanceOf_user": u(call(J, "balanceOf(address)", enc_addr(MAIN))),
    "owner": call(J, "owner()"),
}

# FUGUI sets
for label, sale in [("set1", "0x4d6bbbc3129beb54450427dc12011f178c7fb630"),
                    ("set2", "0xa0b30b8ff77826e2288a28d2c560ecf3476828f6")]:
    res["fugui_" + label] = {
        "sale": sale,
        "FREE_SHARES": u(call(sale, "FREE_SHARES()")),
        "freeMinted": u(call(sale, "freeMinted()")),
        "totalMinted": u(call(sale, "totalMinted()")),
        "paidMinted": u(call(sale, "paidMinted()")),
        "finalized": b(call(sale, "finalized()")),
        "freeClaimed_user": b(call(sale, "freeClaimed(address)", enc_addr(MAIN))),
        "hasAgentId_user": b(call(sale, "hasAgentId(address)", enc_addr(MAIN))),
    }

with open(OUT, "w") as f:
    json.dump(res, f, indent=1)
print(json.dumps(res, indent=1))
