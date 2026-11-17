#!/usr/bin/env python3
"""Run 0101: single-call free-view check for the 1 velocity passer (MORPHA).
Adapted from run 0001 script: 0001 passers BOT-UNIT + bridge-0x6eee are NOT passers this run
(BOT-UNIT +2 ratio collapse; bridge supply DECREASED), so they are NOT re-checked here; AgentVOLT (round 1) is the only real passer (Ink Koi already claimed by user; bridge artifacts excluded).
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
 "0xe0DEB1A792EeBD9cbA7Fd74B70A283Bfa2630771": ["totalSupply()", "freeMints()", "freeMinted()", "freeClaimed()", "FREE_SUPPLY()", "FREE_CAP()", "MAX_SUPPLY()", "mintOpen()", "paused()", "freeLeft()", "freeSupply()", "totalMinted()", "name()", "symbol()"],
}
ADDR_VIEWS = {
 "0xe0DEB1A792EeBD9cbA7Fd74B70A283Bfa2630771": ["freeClaims(address)", "freeClaimed(address)", "freeMintedBy(address)", "balanceOf(address)", "mintedBy(address)", "canFreeMint(address)", "claimedFree(address)"],
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
json.dump(out, open("run-2026-11-08-0101-passer-free.json", "w"), indent=1)
