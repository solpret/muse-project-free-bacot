#!/usr/bin/env python3
"""Lean triage 2026-11-07 ~22:0x WIB run backfill 132191166-132197165.
Single first-seen: 0x59C4414e88a53f2dbA6c9c466B8bdF46F4E4DCab (ERC721, 1 mint, first block 132197138).
Read-only. Uses fast_rpc dataseed endpoints (NOT Ankr) for eth_call + block timestamp.
"""
import json, sys, time
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _single
from eth_hash.auto import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
OUT = f"{BASE}/backfill-triage-132191166-132197165.json"
ADDR = "0x59C4414e88a53f2dbA6c9c466B8bdF46F4E4DCab"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
USER_PAD = USER[2:].lower().rjust(64, "0")
ONE = "0000000000000000000000000000000000000000000000000000000000000001"
EPS = ["https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/",
       "https://bsc-dataseed.binance.org/",
       "https://bsc-dataseed3.bnbchain.org/",
       "https://bsc-rpc.publicnode.com/"]

def sel(sig):
    return "0x" + keccak(sig.encode()).hex()[:8]

def rpc(method, params, timeout=10):
    last = None
    for ep in EPS:
        try:
            return _single(ep, method, params, timeout, retries=0), None
        except Exception as e:
            last = f"{type(e).__name__}: {str(e)[:120]}"
    return None, last

def call(to, data):
    r, e = rpc("eth_call", [{"to": to, "data": data}, "latest"])
    time.sleep(4)
    return r, e

def dec_addr(raw):
    if isinstance(raw, str) and raw.startswith("0x") and len(raw) >= 66:
        return "0x" + raw[-40:]
    return None

def dec_uint(raw):
    if isinstance(raw, str) and raw.startswith("0x") and len(raw) >= 2:
        try:
            return int(raw, 16)
        except Exception:
            return None
    return None

def dec_str(raw):
    # ABI string: offset(32) + len(32) + data
    if isinstance(raw, str) and raw.startswith("0x") and len(raw) >= 130:
        try:
            b = bytes.fromhex(raw[2:])
            ln = int.from_bytes(b[32:64], "big")
            return b[64:64+ln].decode("utf-8", "replace")
        except Exception:
            return None
    return None

out = {"address": ADDR, "first_block": 132197138, "mint_count": 1,
       "distinct_minters": 1, "calls": {}}
SIGS = [
    ("agentRegistry()", "zero", "uint_addr"),
    ("name()", "zero", "str"),
    ("symbol()", "zero", "str"),
    ("tick()", "zero", "str"),
    ("quote(uint256)", "uint", "uint"),
    ("quoteFor(address,uint256)", "addr_uint", "uint"),
    ("currentPrice()", "zero", "uint"),
    ("totalMinted()", "zero", "uint"),
    ("maxSupply()", "zero", "uint"),
    ("remaining()", "zero", "uint"),
    ("circulatingSupply()", "zero", "uint"),
    ("maxPerWallet()", "zero", "uint"),
    ("owner()", "zero", "uint_addr"),
]
for sig, kind, dec in SIGS:
    data = sel(sig)
    if kind == "addr":
        data += USER_PAD
    elif kind == "uint":
        data += ONE
    elif kind == "addr_uint":
        data += USER_PAD + ONE
    raw, e = call(ADDR, data)
    row = {"raw": (raw or "")[:130], "error": e}
    if dec == "uint":
        row["uint"] = dec_uint(raw) if raw else None
    elif dec == "uint_addr":
        row["uint"] = dec_uint(raw) if raw else None
        row["addr"] = dec_addr(raw) if raw else None
    elif dec == "str":
        row["str"] = dec_str(raw) if raw else None
    out["calls"][sig] = row
    print(f"{sig}: {row}", flush=True)
    json.dump(out, open(OUT, "w"), indent=1)

# first-mint block timestamp via dataseed (Ankr returns fake timestamps)
blk, e = rpc("eth_getBlockByNumber", [hex(132197138), False])
out["block"] = blk
out["block_error"] = e
if blk and isinstance(blk, dict):
    ts = blk.get("timestamp")
    out["first_mint_timestamp"] = int(ts, 16) if ts else None
print("block ts:", out.get("first_mint_timestamp"), "err:", e, flush=True)
json.dump(out, open(OUT, "w"), indent=1)
print("saved", OUT)
