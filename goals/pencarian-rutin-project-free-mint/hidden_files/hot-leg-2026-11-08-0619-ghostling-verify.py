#!/usr/bin/env python3
"""Ghostling 0x6a48... verify, hot-leg 2026-11-08 06:19 WIB.
New S1 from Boltbook (b/alpha 1328.ai post). Read-only: state + user slot +
age bracket via freeClaimed() at historical blocks (dataseed timestamps)."""
import sys, json, base64
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import batch
from Crypto.Hash import keccak

ADDR = "0x6a4847cb5f658943222fbd23d2520049f824789d"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed2.bnbchain.org/", "https://bsc-dataseed.binance.org/",
       "https://bsc-dataseed1.bnbchain.org/", "https://bsc.publicnode.com/"]
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc_addr(a): return a[2:].lower().rjust(64, "0")
def enc_u(n): return format(n, "064x")
def to_int(v):
    try: return int(v, 16)
    except Exception: return None

def call(addr, sig, args=None, blk="latest"):
    data = sel(sig)
    if args:
        for a in args:
            data += enc_addr(a) if isinstance(a, str) and a.startswith("0x") else enc_u(a)
    for ep in EPS:
        try:
            r = batch([("eth_call", [{"to": addr, "data": data}, blk if blk == "latest" else hex(blk)])],
                      endpoint=ep, timeout=15)
            return r[0]
        except Exception:
            continue
    return None

def call_str(addr, sig, blk="latest"):
    raw = call(addr, sig, None, blk)
    if not raw or raw == "0x":
        return None
    try:
        b = bytes.fromhex(raw[2:])
        # string: offset(32) + len(32) + data
        ln = int.from_bytes(b[32:64], "big")
        return b[64:64 + ln].decode("utf-8", "replace")
    except Exception:
        return f"<decode fail {raw[:80]}>"

def block_ts(blk):
    for ep in EPS:
        try:
            r = batch([("eth_getBlockByNumber", [hex(blk), False])], endpoint=ep, timeout=15)
            b = r[0]
            if isinstance(b, dict) and b.get("timestamp"):
                return int(b["timestamp"], 16)
        except Exception:
            continue
    return None

out = {"address": ADDR}
head = int(batch([("eth_blockNumber", [])], endpoint=EPS[0], timeout=15)[0], 16)
out["block"] = head
reads = {}
for fn in ["name()", "symbol()", "totalSupply()", "MAX_SUPPLY()", "FREE_SUPPLY()",
           "FREE_PER_WALLET()", "MAX_PER_WALLET()", "PRICE()", "freeClaimed()",
           "mintOpen()", "AGENT_ID()", "owner()"]:
    v = call(ADDR, fn)
    if fn in ("name()", "symbol()"):
        reads[fn] = call_str(ADDR, fn)
    elif fn == "AGENT_ID()":
        reads[fn] = v[-40:] if v else None
        reads[fn] = "0x" + reads[fn] if reads[fn] else None
    elif fn == "owner()":
        reads[fn] = ("0x" + v[-40:]) if v else None
    elif fn == "mintOpen()":
        reads[fn] = to_int(v)
    else:
        reads[fn] = to_int(v)
for fn, key in [("freeLeft(address)", "freeLeft_user"), ("freeUsed(address)", "freeUsed_user"),
                ("mintedBy(address)", "mintedBy_user"), ("balanceOf(address)", "balanceOf_user")]:
    reads[key] = to_int(call(ADDR, fn, [USER]))
reads["freeFor_user1"] = to_int(call(ADDR, "freeFor(address,uint256)", [USER, 1]))
reads["quote_user1"] = to_int(call(ADDR, "quote(address,uint256)", [USER, 1]))
reads["quote_user3"] = to_int(call(ADDR, "quote(address,uint256)", [USER, 3]))
out["reads"] = reads
out["contractURI_raw"] = call_str(ADDR, "contractURI()")
uri = out["contractURI_raw"]
if uri:
    try:
        dec = base64.b64decode(uri).decode("utf-8", "replace")
        out["contractURI_decoded"] = dec[:600]
    except Exception as e:
        out["contractURI_decoded"] = f"<not base64: {e}>"
out["tokenURI_1"] = call_str(ADDR, "tokenURI(uint256)", ) if False else None
# tokenURI takes an arg
raw = call(ADDR, "tokenURI(uint256)", [1])
if raw and raw != "0x":
    try:
        b = bytes.fromhex(raw[2:])
        ln = int.from_bytes(b[32:64], "big")
        out["tokenURI_1"] = b[64:64 + ln].decode("utf-8", "replace")[:800]
    except Exception:
        out["tokenURI_1"] = f"<decode fail {raw[:80]}>"

# age: calibrate block time, sample freeClaimed at 48h-ago block
t_head = block_ts(head)
t_old = block_ts(head - 20000)
rate = (t_head - t_old) / 20000.0 if (t_head and t_old) else 3.0
out["sec_per_block"] = round(rate, 4)
blocks_48h = int(48 * 3600 / rate)
out["blocks_48h"] = blocks_48h
blk48 = head - blocks_48h
fc48 = to_int(call(ADDR, "freeClaimed()", None, blk48))
out["freeClaimed_at_48h_ago_block"] = fc48
out["block_48h_ago"] = blk48
if fc48 is None:
    out["age_verdict"] = "UNVERIFIED - freeClaimed at 48h-ago block unreadable"
elif fc48 > 0:
    out["age_verdict"] = "AGE-EXCLUDED - freeClaimed already >0 48h ago (first mint older than 48h)"
    lo, hi = head - blocks_48h, head
    # binary search first block with freeClaimed>0 only within 48h..7d to date it
    lo2, hi2 = head - int(7 * 24 * 3600 / rate), head
    for _ in range(20):
        mid = (lo2 + hi2) // 2
        v = to_int(call(ADDR, "freeClaimed()", None, mid))
        if v is None:
            break
        if v > 0:
            hi2 = mid
        else:
            lo2 = mid
        if hi2 - lo2 <= 1:
            break
    out["first_mint_block_bracket"] = {"lo_zero": lo2, "hi_positive": hi2}
    ts = block_ts(hi2)
    out["first_mint_block_ts"] = ts
    if ts:
        from datetime import datetime, timezone, timedelta
        out["first_mint_wib"] = datetime.fromtimestamp(ts, timezone(timedelta(hours=7))).strftime("%Y-%m-%d %H:%M:%S WIB")
else:
    out["age_verdict"] = "AGE-OK - freeClaimed was 0 48h ago (first mint within 48h)"
    lo, hi = blk48, head
    for _ in range(20):
        mid = (lo + hi) // 2
        v = to_int(call(ADDR, "freeClaimed()", None, mid))
        if v is None:
            break
        if v > 0:
            hi = mid
        else:
            lo = mid
        if hi - lo <= 1:
            break
    out["first_mint_block_bracket"] = {"lo_zero": lo, "hi_positive": hi}
    ts = block_ts(hi)
    out["first_mint_block_ts"] = ts
    if ts:
        from datetime import datetime, timezone, timedelta
        out["first_mint_wib"] = datetime.fromtimestamp(ts, timezone(timedelta(hours=7))).strftime("%Y-%m-%d %H:%M:%S WIB")

json.dump(out, open(f"{BASE}/hot-leg-2026-11-08-0619-ghostling-verify.json", "w"), indent=1)
print(json.dumps(out, indent=1))
