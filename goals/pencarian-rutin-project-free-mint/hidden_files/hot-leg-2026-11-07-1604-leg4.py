#!/usr/bin/env python3
"""Hot-leg run 2026-11-07 15:49 WIB — leg 4 re-read (read-only).
Re-reads the same 37 snapshot items the 15:34 run read + the 5 gate-blocked
track-C leads from 15:34 + NOVRA pool retry. Compares vs 15:34 recorded values.
Detects: sellout, slot lost, pool change, mintOpen change. No snapshot writes."""
import json, sys, concurrent.futures
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _single as _fast_single
from Crypto.Hash import keccak

HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/", "https://bsc-dataseed3.bnbchain.org/",
       "https://rpc.ankr.com/bsc"]

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def enc_uint(n): return format(n, "064x")

def call(to, data, timeout=6):
    for ep in EPS:
        try:
            v = _fast_single(ep, "eth_call", [{"to": to, "data": data}, "latest"], timeout, retries=0)
            if v is None or v == "0x":
                return None
            return v
        except Exception:
            continue
    return "transport-fail"

def call_int(to, sig, args=""):
    v = call(to, sel(sig) + args)
    if v is None or v == "transport-fail":
        return v
    try:
        return int(v, 16)
    except Exception:
        return v

def call_tuple2(to, sig, args=""):
    v = call(to, sel(sig) + args)
    if v is None or v == "transport-fail":
        return v
    try:
        raw = bytes.fromhex(v[2:])
        return [int.from_bytes(raw[0:32], "big"), int.from_bytes(raw[32:64], "big")]
    except Exception:
        return v

prev = json.load(open(f"{HF}/hot-leg-2026-11-07-1549-leg4.json"))
prev_items = prev["items"]  # name -> {address, totalSupply, ...}
LEADS5 = {
    "WibblezapAgent": "0x8717fc8751b8Ebd6832EA145974AA77D86bE9EaD",
    "QuonkersAgent": "0xe8b5E3ca9f4F51366f9f4860ed70b8e929e80470",
    "DribblonAgent": "0x16A8aFdc97F8Cf48617bF15E47b4dA2217ea04A5",
    "HobnorbAgent": "0xab3F2dA0b63F5A823510095263789E9e6F26329a",
    "YammerjackAgent": "0x2a71CEF7101B8b19c4ab18BeD40C3ec5EC87B9b7",
}
NOVRA = "0x75Ac13cF23a8dccC703D1496138251FD7f247890"

blk = None
for ep in EPS:
    try:
        blk = _fast_single(ep, "eth_blockNumber", [], 6, retries=0)
        if blk: blk = int(blk, 16); break
    except Exception:
        continue

GENERIC = ["totalSupply", "freeClaimed", "freeMinted", "FREE_SUPPLY",
           "balanceOf(address)", "mintedBy(address)", "freeUsed(address)",
           "claimedFree(address)", "mintOpen"]
S1_EXTRA = ["sharesSold", "freeSharesClaimed", "freeSharesRemaining", "freeRemaining",
            "MAX_SHARES", "FREE_PER_AGENT"]

def probe_snapshot(item):
    name, prevd = item
    a = prevd["address"]
    d = {"address": a}
    for sig in GENERIC:
        if "(address)" in sig:
            d[sig.split("(")[0] + "_user"] = call_int(a, sig, enc(USER))
        else:
            d[sig] = call_int(a, sig + "()")
    return name, d

def probe_s1(name, a):
    d = {"address": a}
    for sig in GENERIC + S1_EXTRA:
        if "(address)" in sig:
            d[sig.split("(")[0] + "_user"] = call_int(a, sig, enc(USER))
        else:
            d[sig] = call_int(a, sig + "()")
    d["quote_user1"] = call_tuple2(a, "quote(address,uint256)", enc(USER) + enc_uint(1))
    return name, d

out = {"block": blk, "items": {}, "leads5": {}, "novra_retry": {}}
with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:
    for name, d in ex.map(probe_snapshot, list(prev_items.items())):
        out["items"][name] = d
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as ex:
    for name, d in ex.map(lambda kv: probe_s1(kv[0], kv[1]), list(LEADS5.items())):
        out["leads5"][name] = d

# NOVRA pool retry
nd = {}
for sig in ["freeSharesRemaining", "freeSharesClaimed", "freeRemaining", "mintOpen", "FREE_SUPPLY", "FREE_PER_AGENT"]:
    nd[sig] = call_int(NOVRA, sig + "()")
nd["quote_user1"] = call_tuple2(NOVRA, "quote(address,uint256)", enc(USER) + enc_uint(1))
out["novra_retry"] = nd

json.dump(out, open(f"{HF}/hot-leg-2026-11-07-1604-leg4.json", "w"), indent=1)

# change detection vs 15:34
changes = []
for name, d in out["items"].items():
    p = prev_items[name]
    for k in ("totalSupply", "freeClaimed", "freeMinted", "FREE_SUPPLY", "balanceOf_user", "mintedBy_user", "mintOpen"):
        old, new = p.get(k), d.get(k)
        if isinstance(old, int) and isinstance(new, int) and old != new:
            changes.append(f"{name}: {k} {old}->{new}")
        elif isinstance(old, int) and new == "transport-fail":
            pass
print("block", blk)
print("CHANGES vs 15:34:")
for c in changes:
    print(" ", c)
if not changes:
    print("  none detected (transport-fail values excluded)")
print("LEADS5:")
for name, d in out["leads5"].items():
    print(" ", name, "sharesSold", d.get("sharesSold"), "freeClaimed", d.get("freeSharesClaimed"),
          "freeRemaining", d.get("freeSharesRemaining"), "quote(user,1)", d.get("quote_user1"),
          "freeUsed(user)", d.get("freeUsed_user"), "mintedBy(user)", d.get("mintedBy_user"),
          "bal(user)", d.get("balanceOf_user"), "mintOpen", d.get("mintOpen"))
print("NOVRA retry:", json.dumps(nd))
