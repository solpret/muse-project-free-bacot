#!/usr/bin/env python3
"""Lean deepcheck 2026-11-07 ~18:0x WIB run 132184220-132188665.
Decisive selectors only, ONE endpoint at a time, 4s pause between calls.
Prints + flushes per call and appends incrementally to JSON so a kill loses nothing.
Read-only.
"""
import json, sys, time
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _single
from eth_hash.auto import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
OUT = f"{BASE}/backfill-deepcheck-lean-132184220-132188665.json"
REGISTRY = "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F"
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

def save(obj):
    tmp = OUT + ".tmp"
    json.dump(obj, open(tmp, "w"), indent=1)
    import os
    os.replace(tmp, OUT)

try:
    out = json.load(open(OUT))
except Exception:
    out = {}

def probe(addr, label, sigs):
    row = out.get(addr, {"address": addr, "label": label, "calls": {}})
    for sig, kind in sigs:
        if sig in row["calls"] and row["calls"][sig].get("raw"):
            continue
        data = sel(sig)
        if kind == "addr":
            data += USER_PAD
        elif kind == "uint":
            data += ONE
        elif kind == "addr_uint":
            data += USER_PAD + ONE
        raw, e = call(addr, data)
        row["calls"][sig] = {"raw": (raw or "")[:130],
                             "uint": dec_uint(raw) if raw else None,
                             "addr": dec_addr(raw) if raw else None,
                             "error": e}
        print(f"{label} {sig}: raw={(raw or '')[:66]} uint={row['calls'][sig]['uint']} addr={row['calls'][sig]['addr']} err={str(e)[:100] if e else None}", flush=True)
        save(out)
    out[addr] = row
    return row

SIGS = [("agentRegistry()", "zero"), ("AGENT_ID_REGISTRY()", "zero"),
        ("AGENT_REGISTRY()", "zero"), ("REGISTRY()", "zero"),
        ("freeLeft()", "zero"), ("FREE_SUPPLY()", "zero"),
        ("freeMinted()", "zero"), ("freeSupply()", "zero"),
        ("freeClaimed(address)", "addr"), ("freeFor(address)", "addr"),
        ("quote(address,uint256)", "addr_uint"), ("quote(uint256)", "uint"),
        ("PRICE()", "zero"), ("price()", "zero"), ("mintPrice()", "zero"),
        ("MAX_SUPPLY()", "zero"), ("maxSupply()", "zero"),
        ("totalMinted()", "zero"), ("totalSupply()", "zero"),
        ("mintOpen()", "zero"), ("maxPerWallet()", "zero"),
        ("freeMinted()", "zero")]

TARGETS = [
    ("0xBa024D49cce9CFE7678a9fB26a9bDf69C4174350", "NFT-NFT-20mint"),
    ("0x6d69790292c9288Fbb9e061b1B8AAe653E5B1161", "0x6d69-1mint"),
    ("0xb6A96379FBE88a517Ccc615C8F98470C53C74A88", "0xb6A9-1mint"),
    ("0xc8642ce2Ede98c869A39c4cc3fb1e4D402c71582", "0xc864-1mint"),
    ("0x31975837D5C68Eea0B66b5Fd27De3506c2f109ba", "TPET-9mint"),
]

for addr, label in TARGETS:
    print(f"== {label} ==", flush=True)
    probe(addr, label, SIGS)

for addr, label in TARGETS:
    row = out.get(addr, {"address": addr, "label": label, "calls": {}})
    if not row.get("owner"):
        raw, e = call(addr, "0x8da5cb5b")
        row["owner"] = dec_addr(raw) if raw else None
        row["owner_error"] = e
        print(f"{label}: owner={row['owner']} err={str(e)[:100] if e else None}", flush=True)
        out[addr] = row
        save(out)

for blk in (132184270, 132185233, 132186567, 132187900, 132188200):
    key = f"block_{blk}"
    if key in out and out[key].get("timestamp"):
        continue
    b, e = rpc("eth_getBlockByNumber", [hex(blk), False])
    time.sleep(4)
    if b:
        ts = int(b["timestamp"], 16)
        out[key] = {"timestamp": ts, "wib": time.strftime("%Y-%m-%d %H:%M:%S WIB", time.gmtime(ts + 7*3600))}
    else:
        out[key] = {"timestamp": None, "error": e}
    print(f"{key}: {out[key]}", flush=True)
    save(out)

print("DONE", flush=True)
