#!/usr/bin/env python3
"""Run 0101: ONES 0xD878B2e224B9F077323d46309EC1dba979857B6E first-seen EARLY-lead verification.
Single-call reads (LEAN batch fails whole-batch on a reverting view). Read-only."""
import json, sys
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import batch
from Crypto.Hash import keccak
ADDR = "0xD878B2e224B9F077323d46309EC1dba979857B6E"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed1.bnbchain.org/", "https://bsc.publicnode.com/", "https://bsc-dataseed2.bnbchain.org/"]
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def to_int(v):
    try: return int(v, 16)
    except Exception: return None
def dec_str(v):
    try:
        b = bytes.fromhex(v[2:]); ln = int.from_bytes(b[32:64], "big")
        return b[64:64+ln].decode(errors="replace")
    except Exception: return None
def single(sig, ep, arg=None, raw=False):
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
NOARG = ["totalSupply()", "totalMinted()", "nextTokenId()", "FREE_CAP()", "MAX_SUPPLY()", "MAX_PER_WALLET()", "PRICE()", "mintOpen()", "mintOpensAt()", "freeMinted()", "freeClaimed()", "owner()", "treasury()", "agentIdRegistry()", "contractURI()"]
for sig in NOARG:
    try:
        v = single(sig, ep)
        out[sig.split("(")[0]] = dec_str(v) if sig in ("contractURI()",) else to_int(v)
        if out[sig.split("(")[0]] is None and sig == "contractURI()":
            out["contractURI_raw"] = v[:200] if isinstance(v, str) else v
    except Exception as e:
        out[sig.split("(")[0]] = None; out[sig.split("(")[0]+"_err"] = str(e)[:100]
for sig in ["freeClaimed(address)", "mintsBy(address)", "balanceOf(address)", "holdsAgentId(address)"]:
    try:
        out[sig.split("(")[0]+"_user"] = to_int(single(sig, ep, USER))
    except Exception as e:
        out[sig.split("(")[0]+"_user"] = None; out[sig.split("(")[0]+"_user_err"] = str(e)[:100]
# tokenURI(1) for method I
try:
    import struct
    data = sel("tokenURI(uint256)") + format(1, "064x")
    r = batch([("eth_call", [{"to": ADDR, "data": data}, "latest"])], endpoint=ep, timeout=10)
    out["tokenURI_1"] = dec_str(r[0])
except Exception as e:
    out["tokenURI_1"] = None; out["tokenURI_1_err"] = str(e)[:100]
print(json.dumps(out, indent=1))
json.dump(out, open("run-2026-11-08-0101-ones-verify.json", "w"), indent=1)
