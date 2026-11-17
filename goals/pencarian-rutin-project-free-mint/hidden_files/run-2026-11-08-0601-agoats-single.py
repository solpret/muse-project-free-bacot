#!/usr/bin/env python3
"""Agent Goats single-call reads (batch reverts on this contract - one call
per batch so a revert only kills that view). Read-only."""
import json, sys, time
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import batch
from Crypto.Hash import keccak
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
ADDR = "0x0e9e0a3b46dc0d36a1ab64f553dd8a0693e6aaa6"
EPS = ["https://bsc-dataseed1.bnbchain.org/", "https://bsc.publicnode.com/",
       "https://bsc-dataseed2.bnbchain.org/"]
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def to_int(v):
    try: return int(v, 16)
    except Exception: return None
def single(data):
    for ep in EPS:
        try:
            r = batch([("eth_call", [{"to": ADDR, "data": data}, "latest"])], endpoint=ep, timeout=10)
            return r[0]
        except Exception:
            continue
    return None
VIEWS = {"totalSupply": "totalSupply()", "totalMinted": "totalMinted()",
         "freeClaimed": "freeClaimed()", "freeMinted": "freeMinted()",
         "FREE_SUPPLY": "FREE_SUPPLY()", "MAX_SUPPLY": "MAX_SUPPLY()",
         "mintOpen": "mintOpen()", "owner": "owner()",
         "balanceOf_user": "balanceOf(address)",
         "quote_user1": "quote(address,uint256)",
         "freeLeft_user": "freeLeft(address)", "freeUsed_user": "freeUsed(address)",
         "mintedBy_user": "mintedBy(address)", "freeFor_user1": "freeFor(address,uint256)"}
out = {"address": ADDR}
for key, sig in VIEWS.items():
    if "(address)" in sig and "uint256" not in sig:
        data = sel(sig) + enc(USER)
    elif sig == "quote(address,uint256)":
        data = sel(sig) + enc(USER) + "1".rjust(64, "0")
    elif sig == "freeFor(address,uint256)":
        data = sel(sig) + enc(USER) + "1".rjust(64, "0")
    else:
        data = sel(sig)
    v = single(data)
    if key == "owner":
        out[key] = ("0x" + v[-40:]) if isinstance(v, str) and len(v) >= 42 else v
    else:
        out[key] = to_int(v) if isinstance(v, str) and v.startswith("0x") else v
    print(key, "=", out[key], flush=True)
    time.sleep(0.5)
try:
    out["block"] = int(batch([("eth_blockNumber", [])], endpoint=EPS[0], timeout=8)[0], 16)
except Exception as e:
    out["block"] = f"ERR:{e}"
json.dump(out, open("run-2026-11-08-0601-agoats-single.json", "w"), indent=1)
print("DONE block", out.get("block"))
