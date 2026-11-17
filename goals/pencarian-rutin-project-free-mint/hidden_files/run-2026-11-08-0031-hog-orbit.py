#!/usr/bin/env python3
"""Run 0031: HOG ORBIT fresh on-chain re-read + gate-evidence pack (priority flag, hot-leg 0024).
Single-call reads (batch fails whole-batch on a reverting view). Read-only; writes
run-2026-11-08-0031-hog-orbit.json. NO preview, NO mint, NO sim of mint (parent decides).
Contract: 0x7bc0b487febcbb1caa781148bf05a8cd72d02ec5 (HOG ORBIT, HOG, ERC721, MAX_SUPPLY 1500).
"""
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
def enc_int(n): return ("%064x" % n)
def to_int(v):
    try: return int(v, 16)
    except Exception: return None
def call(addr, data, ep):
    r = batch([("eth_call", [{"to": addr, "data": data}, "latest"])], endpoint=ep, timeout=10)
    return r[0]
ep = EPS[0]
out = {"contract": ADDR, "name": "HOG ORBIT"}
try:
    out["block"] = int(batch([("eth_blockNumber", [])], endpoint=ep, timeout=10)[0], 16)
except Exception:
    ep = EPS[1]
    out["block"] = int(batch([("eth_blockNumber", [])], endpoint=ep, timeout=10)[0], 16)
print("BLOCK", out["block"], "ep", ep, flush=True)
noarg = ["totalSupply()", "freeLeft()", "FREE_SUPPLY()", "MAX_SUPPLY()", "mintOpen()",
         "price()", "bogo()", "owner()", "agentIds()", "treasury()", "totalMinted()"]
for sig in noarg:
    try:
        v = call(ADDR, sel(sig), ep)
        out[sig.split("(")[0]] = to_int(v)
        if sig in ("owner()", "agentIds()", "treasury()") and v:
            out[sig.split("(")[0] + "_hex"] = "0x" + v[-40:] if len(v) >= 42 else v
    except Exception as e:
        out[sig.split("(")[0]] = None
        out[sig.split("(")[0] + "_err"] = str(e)[:120]
# two-arg views: freeOf(wallet,qty), costOf(wallet,qty)
for sig, qty in [("freeOf(address,uint256)", 1), ("costOf(address,uint256)", 1)]:
    try:
        data = sel(sig) + enc(USER) + enc_int(qty)
        out[sig.split("(")[0] + "_user_1"] = to_int(call(ADDR, data, ep))
    except Exception as e:
        out[sig.split("(")[0] + "_user_1"] = None
        out[sig.split("(")[0] + "_user_1_err"] = str(e)[:120]
# one-arg user views
for sig in ["mintedBy(address)", "mintsLeft(address)", "balanceOf(address)", "agentTokenIdOf(address)"]:
    try:
        out[sig.split("(")[0] + "_user"] = to_int(call(ADDR, sel(sig) + enc(USER), ep))
    except Exception as e:
        out[sig.split("(")[0] + "_user"] = None
        out[sig.split("(")[0] + "_user_err"] = str(e)[:120]
# tokenURI(1) raw (string return, keep raw hex)
try:
    raw = call(ADDR, sel("tokenURI(uint256)") + enc_int(1), ep)
    out["tokenURI_1_raw"] = raw[:200] if raw else raw
    # try utf8 decode of the abi-encoded string payload
    try:
        b = bytes.fromhex(raw[2:])
        # abi string: offset(32) + len(32) + data
        ln = int.from_bytes(b[32:64], "big")
        out["tokenURI_1"] = b[64:64+ln].decode("utf-8", "replace")
    except Exception as e:
        out["tokenURI_1_decode_err"] = str(e)[:100]
except Exception as e:
    out["tokenURI_1_raw"] = None
    out["tokenURI_1_err"] = str(e)[:120]
# contractURI() does not exist in ABI (verified by grep) - record as absent, do not call
out["contractURI_exists_in_abi"] = False
print(json.dumps(out, indent=1))
json.dump(out, open("run-2026-11-08-0031-hog-orbit.json", "w"), indent=1)
