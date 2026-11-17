#!/usr/bin/env python3
"""Agent Goats minimal retry (no freeUsed/freeLeft — they revert). Read-only."""
import json, sys, time
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import batch
from Crypto.Hash import keccak
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed1.bnbchain.org/", "https://bsc.publicnode.com/",
       "https://bsc-dataseed2.bnbchain.org/"]
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def to_int(v):
    try: return int(v, 16)
    except Exception: return None
ADDR = "0x0e9e0a3b46dc0d36a1ab64f553dd8a0693e6aaa6"
VIEWS = ["totalSupply()", "freeClaimed()", "FREE_SUPPLY()", "MAX_SUPPLY()",
         "mintOpen()", "owner()", "balanceOf(address)"]
calls, keys = [], []
for sig in VIEWS:
    base = sig.split("(")[0]
    if "(address)" in sig:
        calls.append(("eth_call", [{"to": ADDR, "data": sel(sig) + enc(USER)}, "latest"])); keys.append(base + "_user")
    else:
        calls.append(("eth_call", [{"to": ADDR, "data": sel(sig)}, "latest"])); keys.append(base)
calls.append(("eth_call", [{"to": ADDR, "data": sel("quote(address,uint256)") + enc(USER) + "1".rjust(64, "0")}, "latest"])); keys.append("quote_user1")
for ep in EPS:
    try:
        res = batch(calls, endpoint=ep, timeout=15)
        d = {"_ep": ep}
        for k, v in zip(keys, res):
            d[k] = ("0x" + v[-40:]) if k == "owner" and isinstance(v, str) and len(v) >= 42 else to_int(v)
        d["address"] = ADDR
        try: d["block"] = int(batch([("eth_blockNumber", [])], endpoint=ep, timeout=8)[0], 16)
        except Exception: pass
        print(d); json.dump(d, open("run-2026-11-08-0601-agoats-min.json", "w"), indent=1); break
    except Exception as e:
        print(f"via {ep} failed: {str(e)[:120]}", flush=True); time.sleep(2)
