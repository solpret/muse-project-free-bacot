#!/usr/bin/env python3
"""Hot-leg 1809 leg3 extra: probe new S1-pass NFT 0xcdA4A0EF (Monoliths) on-chain,
read-only. NFT early-lead detection stays with the main job; this only enriches
the hot-leg record (pool/slot/age state). No preview, no mint."""
import json, sys, time, urllib.request
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import batch
from Crypto.Hash import keccak
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
TAG = "hot-leg-2026-11-08-1844"
ADDR = "0xcdA4A0EF9C0a626b2450168fd8F90f62C51A569b"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EP = "https://bsc-dataseed1.bnbchain.org/"
t0 = time.time()
def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode()); return "0x"+k.hexdigest()[:8]
def enc_addr(a): return a[2:].lower().rjust(64, "0")
def to_int(v):
    try: return int(v, 16)
    except Exception: return None
def call(sig, arg=""):
    data = sel(sig)
    if arg == "USER": data += enc_addr(USER)
    elif arg == "U1": data += format(1, "064x")
    try:
        r = batch([("eth_call", [{"to": ADDR, "data": data}, "latest"])], endpoint=EP, timeout=30)
        return to_int(r[0])
    except Exception as ex:
        return f"ERR {str(ex)[:100]}"
out = {}
for name, sig, arg in [
    ("totalMinted", "totalMinted()", ""),
    ("totalSupply", "totalSupply()", ""),
    ("mintActive", "mintActive()", ""),
    ("publicRemaining", "publicRemaining()", ""),
    ("freeUsed_user", "freeUsed(address)", "USER"),
    ("mintedCount_user", "mintedCount(address)", "USER"),
    ("balanceOf_user", "balanceOf(address)", "USER"),
    ("mintCost", "mintCost()", ""),
    ("price", "price()", ""),
    ("mintedAt_1", "mintedAt(uint256)", "U1"),
]:
    out[name] = call(sig, arg)
try:
    blk = int(batch([("eth_blockNumber", [])], endpoint=EP, timeout=30)[0], 16)
except Exception:
    blk = None
out["block"] = blk
ts = out.get("mintedAt_1")
if isinstance(ts, int) and ts > 0:
    out["first_mint_wib"] = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(ts + 7*3600))
json.dump(out, open(BASE+TAG+"-leg3-cdA4.json","w"), indent=1)
# enrich the hot-leg-seen record with the probe (read-only state, no promotion)
seen = json.load(open(BASE+"hot-leg-seen.json"))
note = seen.get(ADDR, {}).get("note", "")
extra = (f" | Leg3 block {blk}: totalMinted={out['totalMinted']} totalSupply={out['totalSupply']} "
         f"mintActive={out['mintActive']} publicRemaining={out['publicRemaining']} "
         f"freeUsed(user)={out['freeUsed_user']} mintedCount(user)={out['mintedCount_user']} "
         f"balanceOf(user)={out['balanceOf_user']} mintCost={out['mintCost']} price={out['price']} "
         f"mintedAt(1)={out['mintedAt_1']}" + (f" ({out['first_mint_wib']} WIB)" if out.get("first_mint_wib") else ""))
if ADDR in seen:
    seen[ADDR]["note"] = note + extra
    json.dump(seen, open(BASE+"hot-leg-seen.json","w"), indent=1)
out["elapsed_sec"] = round(time.time()-t0, 1)
print(json.dumps(out, indent=1))
