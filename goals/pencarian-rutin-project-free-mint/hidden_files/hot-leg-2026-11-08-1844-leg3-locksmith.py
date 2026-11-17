#!/usr/bin/env python3
"""Hot-leg 1514 leg3 follow-up: LOCKSMITH first mint (0->1) seen in leg4 re-read.
Verify first-mint time (age corroboration) + user slot still open. Read-only."""
import json, sys, time
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import batch
from Crypto.Hash import keccak
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
TAG = "hot-leg-2026-11-08-1844"
ADDR = "0x05e8738290be6639fD0f7236ebF444E5466D3164"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EP = "https://bsc-dataseed1.bnbchain.org/"
t0 = time.time()
def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode()); return "0x"+k.hexdigest()[:8]
def enc_addr(a): return a[2:].lower().rjust(64, "0")
def enc_u(n): return format(n, "064x")
def to_int(v):
    try: return int(v, 16)
    except Exception: return None
def call(sig, arg=""):
    data = sel(sig)
    if arg == "USER": data += enc_addr(USER)
    elif arg == "U1": data += enc_u(1)
    try:
        r = batch([("eth_call", [{"to": ADDR, "data": data}, "latest"])], endpoint=EP, timeout=30)
        return to_int(r[0])
    except Exception as ex:
        return f"ERR {ex}"
out = {}
for name, sig, arg in [
    ("mintedAt_1", "mintedAt(uint256)", "U1"),
    ("totalMinted", "totalMinted()", ""),
    ("freeMintedTotal", "freeMintedTotal()", ""),
    ("FREE_CAP", "FREE_CAP()", ""),
    ("mintActive", "mintActive()", ""),
    ("freeMinted_user", "freeMinted(address)", "USER"),
    ("mintedCount_user", "mintedCount(address)", "USER"),
    ("balanceOf_user", "balanceOf(address)", "USER"),
    ("quote_tier0_free", "quote(uint256,uint256)", ""),
]:
    if name == "quote_tier0_free":
        data = sel(sig) + enc_u(0) + enc_u(1)
        try:
            r = batch([("eth_call", [{"to": ADDR, "data": data}, "latest"])], endpoint=EP, timeout=30)
            out[name] = to_int(r[0])
        except Exception as ex:
            out[name] = f"ERR {ex}"
        continue
    out[name] = call(sig, arg)
try:
    blk = int(batch([("eth_blockNumber", [])], endpoint=EP, timeout=30)[0], 16)
except Exception as ex:
    blk = None
out["block"] = blk
# mintedAt(1) is a unix timestamp if the view returns one; convert to WIB
ts = out.get("mintedAt_1")
if isinstance(ts, int) and ts > 0:
    out["first_mint_wib"] = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(ts + 7*3600))
json.dump(out, open(BASE+TAG+"-leg3-locksmith.json","w"), indent=1)
out["elapsed_sec"] = round(time.time()-t0, 1)
print(json.dumps(out, indent=1))
