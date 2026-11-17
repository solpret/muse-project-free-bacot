#!/usr/bin/env python3
"""Run 0001: single-call free-view check for the 2 velocity passers (BOT-UNIT real-count; bridge-0x6eee raw-unit artifact).
The reread LEAN batch fails whole-batch on a reverting no-arg freeClaimed(),
so free views may be readable individually. Read-only; writes -passer-free.json."""
import json, sys
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import batch
from Crypto.Hash import keccak
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed1.bnbchain.org/", "https://bsc.publicnode.com/", "https://bsc-dataseed2.bnbchain.org/"]
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def to_int(v):
    try: return int(v, 16)
    except Exception: return None
def single(addr, sig, ep, arg=None):
    data = sel(sig) + (enc(arg) if arg else "")
    r = batch([("eth_call", [{"to": addr, "data": data}, "latest"])], endpoint=ep, timeout=10)
    return r[0]
PASSERS = {
 "0x1482fba999E7C1da9764C5e874d18a832881E3d6": ["totalSupply()", "freeMints()", "freeMinted()", "freeClaimed()", "FREE_SUPPLY()", "FREE_CAP()", "MAX_SUPPLY()", "mintOpen()", "paused()", "freeLeft()", "freeSupply()", "totalMinted()"],
 "0x6eee003e2aebe75be551ac509eb485cc25e404fb": ["totalSupply()", "freeMinted()", "freeClaimed()", "FREE_SUPPLY()", "MAX_SUPPLY()", "mintOpen()", "totalMinted()"],
}
ADDR_VIEWS = {
 "0x1482fba999E7C1da9764C5e874d18a832881E3d6": ["freeClaims(address)", "freeClaimed(address)", "freeMintedBy(address)", "balanceOf(address)"],
 "0x6eee003e2aebe75be551ac509eb485cc25e404fb": ["freeClaimed(address)", "balanceOf(address)"],
}
out = {}
ep = EPS[0]
try:
    out["block"] = int(batch([("eth_blockNumber", [])], endpoint=ep, timeout=10)[0], 16)
except Exception:
    ep = EPS[1]
    out["block"] = int(batch([("eth_blockNumber", [])], endpoint=ep, timeout=10)[0], 16)
for addr, sigs in PASSERS.items():
    d = {}
    for sig in sigs:
        try: d[sig.split("(")[0]] = to_int(single(addr, sig, ep))
        except Exception as e: d[sig.split("(")[0]] = None; d[sig.split("(")[0]+"_err"] = str(e)[:100]
    for sig in ADDR_VIEWS.get(addr, []):
        try: d[sig.split("(")[0]+"_user"] = to_int(single(addr, sig, ep, USER))
        except Exception as e: d[sig.split("(")[0]+"_user"] = None; d[sig.split("(")[0]+"_user_err"] = str(e)[:100]
    out[addr] = d
    print(addr, json.dumps(d))
json.dump(out, open("run-2026-11-08-0001-passer-free.json", "w"), indent=1)
