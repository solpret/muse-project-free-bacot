#!/usr/bin/env python3
"""Grove watch read (read-only). Reads freeOpen() + freeClaimed(agent wallet)
+ current block for Agent Grove 0x8b710e45D38fD55E2D198d2295c0a0D24EBfd64c."""
import json, sys
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _single
from eth_hash.auto import keccak

GROVE = "0x8b710e45D38fD55E2D198d2295c0a0D24EBfd64c"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/", "https://bsc-dataseed3.bnbchain.org/",
       "https://bsc-dataseed4.bnbchain.org/", "https://bsc-rpc.publicnode.com/"]

def sel(sig):
    return "0x" + keccak(sig.encode()).hex()[:8]

def call(addr, data, timeout=8):
    last = None
    for ep in EPS:
        try:
            r = _single(ep, "eth_call", [{"to": addr, "data": data}, "latest"], timeout, retries=0)
            if isinstance(r, str) and r.startswith("0x"):
                return r, ep
            last = r
        except Exception as e:
            last = e
    return {"_error": f"{type(last).__name__}: {str(last)[:150]}"}, None

def block():
    last = None
    for ep in EPS:
        try:
            r = _single(ep, "eth_blockNumber", [], 8, retries=0)
            if isinstance(r, str) and r.startswith("0x"):
                return int(r, 16), ep
            last = r
        except Exception as e:
            last = e
    return None, None

def dec_bool(out):
    if not isinstance(out, str) or not out.startswith("0x"):
        return None
    try:
        return bool(int(out[2:66], 16))
    except Exception:
        return None

out = {}
blk, bep = block()
out["block"] = blk
out["block_endpoint"] = bep
d1 = sel("freeOpen()")
r1, ep1 = call(GROVE, d1)
out["freeOpen_raw"] = r1 if not isinstance(r1, dict) else r1
out["freeOpen"] = dec_bool(r1) if isinstance(r1, str) else None
out["freeOpen_endpoint"] = ep1
d2 = sel("freeClaimed(address)") + "000000000000000000000000" + USER[2:].lower()
r2, ep2 = call(GROVE, d2)
out["freeClaimed_raw"] = r2 if not isinstance(r2, dict) else r2
out["freeClaimed_user"] = dec_bool(r2) if isinstance(r2, str) else None
out["freeClaimed_endpoint"] = ep2
print(json.dumps(out, indent=2))
