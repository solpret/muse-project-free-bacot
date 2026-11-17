#!/usr/bin/env python3
"""Parent verify King's Game — LEAN batch (no revert-prone no-arg freeClaimed), single calls for risky views."""
import json, sys
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import batch
from Crypto.Hash import keccak
ADDR = "0x9eA27f3F0919DaF6a4401CFd09563162d395061D"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
REG = "0x60b9262456de011f7d15a54cdd8c48baaa8b022f"
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
def single(sig, ep, addr_arg=None):
    data = sel(sig) + (enc(addr_arg) if addr_arg else "")
    r = batch([("eth_call", [{"to": ADDR, "data": data}, "latest"])], endpoint=ep, timeout=10)
    return r[0]
out = {"address": ADDR}
ep = EPS[0]
try:
    out["block"] = int(batch([("eth_blockNumber", [])], endpoint=ep, timeout=10)[0], 16)
except Exception:
    ep = EPS[1]
    out["block"] = int(batch([("eth_blockNumber", [])], endpoint=ep, timeout=10)[0], 16)
for sig in ["name()", "symbol()", "totalSupply()", "totalMinted()", "freeMinted()",
            "FREE_SUPPLY()", "MAX_SUPPLY()", "mintOpen()", "agentRegistry()", "contractURI()"]:
    base = sig.split("(")[0]
    try:
        v = single(sig, ep)
        out[base] = dec_str(v) if base in ("name", "symbol", "contractURI") else to_int(v)
    except Exception as e:
        out[base] = None; out[base+"_err"] = str(e)[:120]
for sig, key in [("balanceOf(address)", "balanceOf_user"), ("freeClaimed(address)", "freeClaimed_user")]:
    try:
        out[key] = to_int(single(sig, ep, USER))
    except Exception as e:
        out[key] = None; out[key+"_err"] = str(e)[:120]
try:
    out["freeClaimed_noarg"] = to_int(single("freeClaimed()", ep))
except Exception as e:
    out["freeClaimed_noarg"] = None; out["freeClaimed_noarg_err"] = str(e)[:120]
out["registry_match"] = (out.get("agentRegistry") is not None and out.get("agentRegistry") == int(REG, 16))
print(json.dumps(out, indent=1))
json.dump(out, open("run-2026-11-07-2201-kgame-retry.json", "w"), indent=1)
