#!/usr/bin/env python3
"""Leg 3 on-chain verification for new S1 sale-shape 0x12fb326c0037c3978a7cc08221e41dc81d26d060 (hot-leg 2026-11-07 1214, Skullbloom). Read-only."""
import json, sys, time
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _single as _fast_single
from Crypto.Hash import keccak

ADDR = "0x12fb326c0037c3978a7cc08221e41dc81d26d060"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/", "https://bsc-dataseed3.bnbchain.org/",
       "https://rpc.ankr.com/bsc"]

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def enc_uint(n): return format(n, "064x")

def raw(to, data):
    for ep in EPS:
        try:
            v = _fast_single(ep, "eth_call", [{"to": to, "data": data}, "latest"], 8, retries=0)
            if v is None or v == "0x":
                return None
            return v
        except Exception:
            continue
    return "transport-fail"

def call(sig, args=""):
    return raw(ADDR, sel(sig) + args)

def dec_str(hexv):
    if not hexv or hexv in ("transport-fail",):
        return hexv
    try:
        b = bytes.fromhex(hexv[2:])
        off = int.from_bytes(b[32:64], "big")
        ln = int.from_bytes(b[64:96], "big")
        return b[96:96+ln].decode("utf-8", "replace")
    except Exception as e:
        return f"decode-err {e}: {hexv[:120]}"

def dec_int(hexv):
    if hexv is None or hexv == "transport-fail":
        return hexv
    try:
        return int(hexv, 16)
    except Exception:
        return hexv

out = {}
out["block"] = None
blk = None
for ep in EPS:
    try:
        v = _fast_single(ep, "eth_blockNumber", [], 8, retries=0)
        if v:
            blk = int(v, 16); out["block"] = blk; out["block_via"] = ep; break
    except Exception:
        continue

for sig in ["name()", "symbol()", "totalSupply()", "FREE_SUPPLY()", "MAX_SUPPLY()",
            "freeClaimed()", "mintOpen()", "PRICE()", "FREE_PER_WALLET()", "MAX_PER_WALLET()",
            "AGENT_ID()", "agentIdRequired()"]:
    key = sig.split("(")[0]
    v = call(sig)
    out[key] = dec_int(v) if key not in ("name", "symbol") else dec_str(v)
for sig in ["freeLeft(address)", "freeUsed(address)", "mintedBy(address)", "balanceOf(address)"]:
    key = sig.split("(")[0] + "_user"
    out[key] = dec_int(call(sig, enc(USER)))
out["quote_user1"] = dec_int(call("quote(address,uint256)", enc(USER) + enc_uint(1)))
out["freeFor_user1"] = dec_int(call("freeFor(address,uint256)", enc(USER) + enc_uint(1)))
out["owner"] = call("owner()")
out["contractURI"] = dec_str(call("contractURI()"))
# tokenURI(1) for method (I)
out["tokenURI_1"] = dec_str(call("tokenURI(uint256)", enc_uint(1)))
out["ownerOf_7244"] = call("ownerOf(uint256)", enc_uint(7244))
print(json.dumps(out, indent=1))
json.dump(out, open("/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/leg3-12fb-1214.json", "w"), indent=1)
