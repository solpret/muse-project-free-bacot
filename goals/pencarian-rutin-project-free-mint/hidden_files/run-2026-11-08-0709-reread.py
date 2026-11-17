#!/usr/bin/env python3
"""Hot-leg run 2026-11-08 07:09 WIB: focused re-read (read-only) + Caishen shape-check.
Reuses fast_rpc.batch (single-call batches to avoid whole-batch revert quirk).
Never writes snapshot/main seen files; writes only run-2026-11-08-0709-reread.json + hot-leg-seen.json update (this job's own file, handled by caller script? No - this script updates seen for Caishen only via separate step).
"""
import json, sys, time, os
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import batch
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TS = "2026-11-08-0709"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed1.bnbchain.org/", "https://bsc.publicnode.com/",
       "https://bsc-dataseed2.bnbchain.org/"]
REGISTRY = "60b9262456de011f7d15a54cdd8c48baaa8b022f"

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def enc_u(n): return format(n, "064x")
def to_int(v):
    try: return int(v, 16)
    except Exception: return None

def call_one(ep, addr, data, timeout=8):
    try:
        r = batch([("eth_call", [{"to": addr, "data": data}, "latest"])], endpoint=ep, timeout=timeout)
        return to_int(r[0])
    except Exception:
        return None

def call_view(addr, sig, arg=None):
    data = sel(sig)
    if arg == "user":
        data += enc(USER)
    elif isinstance(arg, int):
        data += enc_u(arg)
    elif isinstance(arg, tuple):  # (user, uint)
        data += enc(USER) + enc_u(arg[1])
    for ep in EPS:
        v = call_one(ep, addr, data)
        if v is not None:
            return v
    return None

def get_code(addr):
    for ep in EPS:
        try:
            r = batch([("eth_getCode", [addr, "latest"])], endpoint=ep, timeout=8)
            return r[0]
        except Exception:
            continue
    return None

def get_block():
    for ep in EPS:
        try:
            r = batch([("eth_blockNumber", [])], endpoint=ep, timeout=8)
            return int(r[0], 16)
        except Exception:
            continue
    return None

out = {"block": get_block(), "reread": {}, "caishen": {}, "started_wib": "2026-11-08 07:09 WIB"}
print("BLOCK", out["block"], flush=True)

# ---- Caishen Agents 0x85df79ad6df9bca9292e73f973ecf49205e62db8 ----
CA = "0x85df79ad6df9bca9292e73f973ecf49205e62db8"
code = get_code(CA)
c = {"address": CA, "code_len": (len(code) - 2) // 2 if code else None,
     "registry_bytes": (REGISTRY in (code or "").lower())}
print("CAISHEN code_len", c["code_len"], "registry_bytes", c["registry_bytes"], flush=True)
# string views
for sig in ["name()", "symbol()", "totalSupply()", "totalMinted()", "mintOpen()",
            "freeClaimed()", "freeMinted()", "FREE_SUPPLY()", "MAX_SUPPLY()",
            "FREE_PER_WALLET()", "MAX_MINTS()"]:
    c[sig.split("(")[0]] = call_view(CA, sig)
for sig in ["balanceOf(address)", "freeClaimed(address)", "freeLeft(address)",
            "mintedBy(address)", "freeMinted(address)"]:
    c[sig.split("(")[0] + "_user"] = call_view(CA, sig, arg="user")
c["quote_user_1"] = call_view(CA, "quote(address,uint256)", arg=("user", 1))
c["costOf_user_1"] = call_view(CA, "costOf(address,uint256)", arg=("user", 1))
c["freeFor_user_1"] = call_view(CA, "freeFor(address,uint256)", arg=("user", 1))
out["caishen"] = c
print("CAISHEN", json.dumps(c), flush=True)

# ---- Focused re-reads of live gate-blocked leads ----
ITEMS = {
 "CipherAgent": ("0x158b5e25015758a94703A27c152889451E5d52E5",
   ["totalMints()", "mintOpen()", "FREE_PER_WALLET()", "MAX_MINTS()"],
   ["freeLeft(address)", "mintedBy(address)", "balanceOf(address)"],
   [("quote(address,uint256)", ("user", 1))]),
 "MarsAgent": ("0x2231FdAe405c33dc4993f8C577c453802FF1AcE9",
   ["totalMints()", "mintOpen()", "FREE_PER_WALLET()", "MAX_MINTS()"],
   ["freeLeft(address)", "mintedBy(address)", "balanceOf(address)"],
   [("quote(address,uint256)", ("user", 1))]),
 "HOG": ("0x7bc0b487febcbb1caa781148bf05a8cd72d02ec5",
   ["totalSupply()", "freeMinted()", "FREE_SUPPLY()"],
   ["mintedBy(address)", "balanceOf(address)"],
   [("costOf(address,uint256)", ("user", 1)), ("freeOf(address,uint256)", ("user", 1))]),
 "REWARD": ("0xcfe5e4925a76a3aa11afa79e04c6fad3611cee40",
   ["freeMintedTotal()", "FREE_CAP()", "mintActive()"],
   ["freeMinted(address)", "mintedCount(address)", "balanceOf(address)"],
   []),
 "HUNT": ("0x885128Cf234c768F1353e2C1432D55873C6b67dD",
   ["totalMinted()", "FREE_SUPPLY()"],
   ["mintedBy(address)", "balanceOf(address)"],
   []),
 "KAGENT": ("0xb34105002B19EF0ce43B59011fE848df5c8B174f",
   ["phase()", "launched()", "sold()", "freeClaimed()"],
   ["balanceOf(address)"],
   []),
 "Ghostling": ("0x6a4847cb5f658943222fbd23d2520049f824789d",
   ["freeClaimed()", "mintOpen()"],
   ["freeLeft(address)", "balanceOf(address)"],
   [("quote(address,uint256)", ("user", 1))]),
}
for name, (addr, noviews, userviews, tupl) in ITEMS.items():
    d = {"address": addr}
    for sig in noviews:
        d[sig.split("(")[0]] = call_view(addr, sig)
    for sig in userviews:
        d[sig.split("(")[0] + "_user"] = call_view(addr, sig, arg="user")
    for sig, arg in tupl:
        d[sig.split("(")[0] + "_user_1"] = call_view(addr, sig, arg=arg)
    out["reread"][name] = d
    print(name, json.dumps(d), flush=True)

with open(f"{BASE}/run-{TS}-reread.json.tmp", "w") as f:
    json.dump(out, f, indent=1)
os.replace(f"{BASE}/run-{TS}-reread.json.tmp", f"{BASE}/run-{TS}-reread.json")
print("DONE", time.time(), flush=True)
