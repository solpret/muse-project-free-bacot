#!/usr/bin/env python3
"""Lean focused retry 2026-11-07 ~17:0x WIB run 132174075-132179195.
Decisive selectors only, ONE endpoint at a time (no 11-way race), 4s pause
between calls to dodge the dataseed flakiness seen this run. Prints + flushes
per call and appends incrementally to JSON so a kill loses nothing.
Read-only.
"""
import json, sys, time
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _single
from eth_hash.auto import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
OUT = f"{BASE}/backfill-deepcheck-lean-132174075-132179195.json"
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
            continue  # already answered
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
        ("AGENT_REGISTRY()", "zero"), ("freeLeft()", "zero"),
        ("FREE_SUPPLY()", "zero"), ("freeMinted()", "zero"),
        ("freeClaimed(address)", "addr"), ("freeFor(address)", "addr"),
        ("quote(address,uint256)", "addr_uint"), ("quote(uint256)", "uint"),
        ("PRICE()", "zero"), ("price()", "zero"), ("mintPrice()", "zero"),
        ("MAX_SUPPLY()", "zero"), ("totalMinted()", "zero")]

A = "0x2e2632307aCa3314C40506431D699D9c4846f77B"
B = "0x1a79B1C274D30FAeBf747DC161d1F16501a863F6"

print("== 0x2e26 (1 mint, shape_pending) ==", flush=True)
probe(A, "0x2e26", SIGS)
print("== AgentCard Miner ACPM (6 mint, not_verified) ==", flush=True)
probe(B, "ACPM", SIGS)

for addr, label in [(A, "0x2e26-owner"), (B, "ACPM-owner")]:
    row = out.get(addr, {"address": addr, "label": label, "calls": {}})
    if not row.get("owner"):
        raw, e = call(addr, "0x8da5cb5b")
        row["owner"] = dec_addr(raw) if raw else None
        row["owner_error"] = e
        print(f"{label}: owner={row['owner']} err={str(e)[:100] if e else None}", flush=True)
        out[addr] = row
        save(out)

for blk in (132176976, 132178714):
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
