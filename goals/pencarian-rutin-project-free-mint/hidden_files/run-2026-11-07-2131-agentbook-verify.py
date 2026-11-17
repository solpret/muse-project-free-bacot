#!/usr/bin/env python3
"""Parent verify AgentBook 0xEECaCBE6eAC6D6F2a38e8daA9049C7AA08aD43b0 — run 2131.
ABI from hot-leg 2129 sourcify-shape (exact_match, 44 fns). Single calls only
(fast_rpc.batch whole-batch revert quirk)."""
import json, sys
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import batch
from Crypto.Hash import keccak
ADDR = "0xEECaCBE6eAC6D6F2a38e8daA9049C7AA08aD43b0"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
REG = "0x60b9262456de011f7d15a54cdd8c48baaa8b022f"
EPS = ["https://bsc-dataseed1.bnbchain.org/", "https://bsc.publicnode.com/", "https://bsc-dataseed2.bnbchain.org/"]
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def enc_uint(n): return ("%064x" % n)
def to_int(v):
    try: return int(v, 16)
    except Exception: return None
def dec_str(v):
    try:
        b = bytes.fromhex(v[2:]); ln = int.from_bytes(b[32:64], "big")
        return b[64:64+ln].decode(errors="replace")
    except Exception: return None
def single(data, ep):
    r = batch([("eth_call", [{"to": ADDR, "data": data}, "latest"])], endpoint=ep, timeout=10)
    return r[0]
out = {"address": ADDR}
ep = EPS[0]
try:
    out["block"] = int(batch([("eth_blockNumber", [])], endpoint=ep, timeout=10)[0], 16)
except Exception:
    ep = EPS[1]
    out["block"] = int(batch([("eth_blockNumber", [])], endpoint=ep, timeout=10)[0], 16)
for sig in ["name()", "symbol()", "totalSupply()", "FREE_QUOTA()", "MAX_SUPPLY()",
            "MAX_PER_WALLET()", "PAID_PRICE()", "paidPrice()", "mintOpen()",
            "remainingFree()", "soldOut()", "agentGateOn()", "REGISTRY()",
            "contractURI()", "mintNonce()"]:
    base = sig.split("(")[0]
    try:
        v = single(sel(sig), ep)
        if base in ("name", "symbol", "contractURI"):
            out[base] = dec_str(v)
        elif base == "REGISTRY":
            out[base] = ("0x" + v[2:][-40:]) if v and len(v) >= 42 else None
        else:
            out[base] = to_int(v)
    except Exception as e:
        out[base] = None; out[base + "_err"] = str(e)[:120]
for sig, key in [("balanceOf(address)", "balanceOf_user"),
                 ("freeUsed(address)", "freeUsed_user"),
                 ("freeClaimed(address)", "freeClaimed_user"),
                 ("freeFor(address)", "freeFor_user"),
                 ("mintedBy(address)", "mintedBy_user")]:
    try:
        out[key] = to_int(single(sel(sig) + enc(USER), ep))
    except Exception as e:
        out[key] = None; out[key + "_err"] = str(e)[:120]
# costOf(address,uint256) for 1 mint
try:
    out["costOf_user_1"] = to_int(single(sel("costOf(address,uint256)") + enc(USER) + enc_uint(1), ep))
except Exception as e:
    out["costOf_user_1"] = None; out["costOf_user_1_err"] = str(e)[:120]
out["registry_match"] = (out.get("REGISTRY") is not None and out["REGISTRY"].lower() == REG.lower())
print(json.dumps(out, indent=1))
json.dump(out, open("run-2026-11-07-2131-agentbook-verify.json", "w"), indent=1)
