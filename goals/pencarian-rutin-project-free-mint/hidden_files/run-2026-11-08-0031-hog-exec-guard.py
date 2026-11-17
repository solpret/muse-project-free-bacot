#!/usr/bin/env python3
"""Run 0031 execution-time fresh guard for HOG ORBIT strong-lead direct mint.
Re-reads freeLeft/costOf/mintOpen/totalSupply/balanceOf fresh. Read-only."""
import json, sys
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import batch
from Crypto.Hash import keccak
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
ADDR = "0x7bc0b487febcbb1caa781148bf05a8cd72d02ec5"
EPS = ["https://bsc-dataseed1.bnbchain.org/", "https://bsc.publicnode.com/", "https://bsc-dataseed2.bnbchain.org/"]
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def enc_int(n): return "%064x" % n
def to_int(v):
    try: return int(v, 16)
    except Exception: return None
def call(addr, data, ep):
    return batch([("eth_call", [{"to": addr, "data": data}, "latest"])], endpoint=ep, timeout=10)[0]
out = {"contract": ADDR}
ep = EPS[0]
try:
    out["block"] = int(batch([("eth_blockNumber", [])], endpoint=ep, timeout=10)[0], 16)
except Exception:
    ep = EPS[1]
    out["block"] = int(batch([("eth_blockNumber", [])], endpoint=ep, timeout=10)[0], 16)
for sig in ["totalSupply()", "freeLeft()", "MAX_SUPPLY()", "mintOpen()"]:
    try: out[sig.split("(")[0]] = to_int(call(ADDR, sel(sig), ep))
    except Exception as e: out[sig.split("(")[0]] = None; out[sig.split("(")[0]+"_err"] = str(e)[:100]
for sig, qty in [("freeOf(address,uint256)", 1), ("costOf(address,uint256)", 1)]:
    try: out[sig.split("(")[0]+"_user_1"] = to_int(call(ADDR, sel(sig)+enc(USER)+enc_int(qty), ep))
    except Exception as e: out[sig.split("(")[0]+"_user_1"] = None
for sig in ["mintedBy(address)", "balanceOf(address)"]:
    try: out[sig.split("(")[0]+"_user"] = to_int(call(ADDR, sel(sig)+enc(USER), ep))
    except Exception as e: out[sig.split("(")[0]+"_user"] = None
print(json.dumps(out, indent=1))
json.dump(out, open("run-2026-11-08-0031-hog-exec-guard.json", "w"), indent=1)
