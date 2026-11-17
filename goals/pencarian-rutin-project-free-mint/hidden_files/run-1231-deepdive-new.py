#!/usr/bin/env python3
"""Deep-dive run 1231: HokiBunny + EMBER (new from discovery leg) + Horus AI pool check.
Read-only. Verifies: free views, user slot, first-mint block (binary search on
totalSupply at historical blocks), block timestamps via dataseed (NOT Ankr)."""
import json, sys, time
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import batch, race
from Crypto.Hash import keccak

USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed1.bnbchain.org/", "https://bsc.publicnode.com/",
       "https://bsc-dataseed2.bnbchain.org/"]
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def to_int(v):
    try: return int(v, 16)
    except Exception: return None

def view_at(addr, sig, block="latest", ep=None):
    data = sel(sig) + (enc(USER) if "(address)" in sig else "")
    calls = [("eth_call", [{"to": addr, "data": data}, block])]
    for e in (EPS if ep is None else [ep]):
        try:
            r = batch(calls, endpoint=e, timeout=10)
            return to_int(r[0])
        except Exception:
            continue
    return None

def block_ts(n):
    for e in EPS:
        try:
            r = batch([("eth_getBlockByNumber", [hex(n), False])], endpoint=e, timeout=10)
            b = r[0]
            return int(b["timestamp"], 16) if b else None
        except Exception:
            continue
    return None

def head():
    for e in EPS:
        try:
            r = batch([("eth_blockNumber", [])], endpoint=e, timeout=8)
            return int(r[0], 16)
        except Exception:
            continue
    return None

def first_mint_block(addr, h):
    """Binary search earliest block with totalSupply>0. Search window: last 200k blocks (~25h)."""
    lo, hi = max(0, h - 200000), h
    if view_at(addr, "totalSupply()", hex(lo)) not in (None, 0):
        return lo, "window-too-small"
    while lo + 1 < hi:
        mid = (lo + hi) // 2
        v = view_at(addr, "totalSupply()", hex(mid))
        if v is None:
            return None, "read-failed"
        if v > 0: hi = mid
        else: lo = mid
    return hi, "ok"

out = {}
h = head()
out["head"] = h
print("head", h, flush=True)

for name, addr in [
    ("HokiBunny", "0xb0C14C75E747DD9cf94D907ff5191425059540aD"),
    ("EMBER", "0xAAEF5BB8A7363B5997F17149d554640DC35f306d"),
    ("HorusAI", "0x794ad67a5590c7e5848e49181297f9cc7c6ce00e"),
]:
    d = {}
    for sig in ["totalSupply()", "totalMinted()", "freeMinted()", "freeClaimed()",
                "FREE_SUPPLY()", "MAX_SUPPLY()", "mintOpen()", "mintActive()",
                "balanceOf(address)", "freeClaimed(address)", "freeMintedBy(address)"]:
        d[sig.split("(")[0] + ("_user" if "(address)" in sig else "")] = view_at(addr, sig)
    fmb, why = first_mint_block(addr, h)
    d["first_mint_block"] = fmb
    d["first_mint_search"] = why
    if fmb:
        ts = block_ts(fmb)
        d["first_mint_ts"] = ts
        if ts:
            import datetime
            d["first_mint_wib"] = datetime.datetime.fromtimestamp(ts, datetime.timezone(datetime.timedelta(hours=7))).strftime("%Y-%m-%d %H:%M:%S WIB")
    out[name] = d
    print(name, json.dumps(d), flush=True)

json.dump(out, open("run-1231-deepdive-new.json", "w"), indent=1)
print("DONE")
