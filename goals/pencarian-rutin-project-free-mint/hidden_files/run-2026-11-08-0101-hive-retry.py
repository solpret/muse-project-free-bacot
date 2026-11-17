#!/usr/bin/env python3
"""Run 0101: HIVE Agents single-call retry (reread LEAN row may be None on RPC degradation)."""
import json, sys, time
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import batch
from Crypto.Hash import keccak
ADDR = "0x1458b0C132Fb51BDC65B1Ca7a3BE484BCd9A2f77"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed1.bnbchain.org/", "https://bsc.publicnode.com/", "https://bsc-dataseed2.bnbchain.org/"]
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def to_int(v):
    try: return int(v, 16)
    except Exception: return None
def single(sig, ep, arg=None):
    data = sel(sig) + (enc(arg) if arg else "")
    r = batch([("eth_call", [{"to": ADDR, "data": data}, "latest"])], endpoint=ep, timeout=10)
    return r[0]
out = {"address": ADDR}
ep = EPS[0]
try:
    out["block"] = int(batch([("eth_blockNumber", [])], endpoint=ep, timeout=10)[0], 16)
except Exception:
    ep = EPS[1]
    out["block"] = int(batch([("eth_blockNumber", [])], endpoint=ep, timeout=10)[0], 16)
for sig in ["totalSupply()", "MAX_SUPPLY()", "freeLeft()", "mintOpen()"]:
    try: out[sig.split("(")[0]] = to_int(single(sig, ep))
    except Exception as e: out[sig.split("(")[0]] = None; out[sig.split("(")[0]+"_err"] = str(e)[:80]
try: out["balanceOf_user"] = to_int(single("balanceOf(address)", ep, USER))
except Exception as e: out["balanceOf_user"] = None
print(json.dumps(out))
json.dump(out, open("run-2026-11-08-0101-hive-retry.json", "w"), indent=1)
