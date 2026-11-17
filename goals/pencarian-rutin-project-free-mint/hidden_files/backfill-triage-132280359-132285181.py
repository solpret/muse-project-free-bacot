#!/usr/bin/env python3
"""Triage backfill run 132280359-132285181 (3 first-seen), 2026-11-08 ~06:15 WIB.
Decisive selectors only, ONE endpoint at a time, 4s pause between calls.
Read-only. Prints + flushes per call, appends incrementally to JSON.
"""
import json, sys, time, os
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _single
from eth_hash.auto import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
OUT = f"{BASE}/backfill-triage-132280359-132285181.json"
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

def dec_bool(raw):
    u = dec_uint(raw)
    return None if u is None else bool(u)

def dec_str(raw):
    try:
        if not raw or not raw.startswith("0x") or len(raw) < 130:
            return None
        b = bytes.fromhex(raw[2:])
        off = int.from_bytes(b[0:32], "big")
        ln = int.from_bytes(b[off:off+32], "big")
        return b[off+32:off+32+ln].decode("utf-8", "replace")
    except Exception:
        return None

def save(obj):
    tmp = OUT + ".tmp"
    json.dump(obj, open(tmp, "w"), indent=1)
    os.replace(tmp, OUT)

try:
    out = json.load(open(OUT))
except Exception:
    out = {}

# Block timestamps first (dataseed, NOT Ankr — Ankr returns fake timestamps)
blocks = {"0x69D60ad11fEB699fE5fEEeB16AC691dF090bfd50": 132284039,
          "0x11c0f64C2424cf80ed537DE1f875583De5d17e61": 132284154,
          "0x4763d7A5a69Eb48C3fdd92655933a818Af61EcCe": 132284138}
for addr, blk in blocks.items():
    row = out.setdefault(addr, {"address": addr, "first_block": blk, "calls": {}})
    if "first_mint_ts" not in row:
        r, e = rpc("eth_getBlockByNumber", [hex(blk), False], timeout=10)
        ts = None
        if isinstance(r, dict) and r.get("timestamp"):
            ts = int(r["timestamp"], 16)
        row["first_mint_ts"] = ts
        row["first_mint_ts_err"] = e
        print(f"{addr} block {blk} ts={ts} err={e}", flush=True)
        save(out)
        time.sleep(2)

# Probes: (sig, kind) kind: none/addr/uint/addr_uint/str
# #1 (0x69D6...) has exact-match ABI with NO agent/free/quote fns -> only id + owner + supply
# #2/#3 not_verified -> probe full agent selector set
PROBES_COMMON = [("name()", "str"), ("symbol()", "str"), ("owner()", "addr"),
                 ("totalSupply()", "uint")]
PROBES_AGENT = [("agentRegistry()", "addr"), ("AGENT_REGISTRY()", "addr"),
                ("agentIdRegistry()", "addr"), ("PRICE()", "uint"),
                ("mintOpen()", "bool"), ("totalMinted()", "uint"),
                ("freeMinted()", "uint"), ("freeClaimed(address)", "addr"),
                ("freeCount(address)", "addr"), ("freeLeft()", "uint"),
                ("spotsLeft()", "uint"), ("quote(address,uint256)", "addr_uint"),
                ("quote(uint256)", "uint")]

targets = [
    ("0x69D60ad11fEB699fE5fEEeB16AC691dF090bfd50", PROBES_COMMON),
    ("0x11c0f64C2424cf80ed537DE1f875583De5d17e61", PROBES_COMMON + PROBES_AGENT),
    ("0x4763d7A5a69Eb48C3fdd92655933a818Af61EcCe", PROBES_COMMON + PROBES_AGENT),
]
for addr, probes in targets:
    row = out.setdefault(addr, {"address": addr, "calls": {}})
    for sig, kind in probes:
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
        entry = {"raw": (raw or "")[:130],
                 "uint": dec_uint(raw) if raw else None,
                 "addr": dec_addr(raw) if raw else None,
                 "bool": dec_bool(raw) if raw else None,
                 "str": dec_str(raw) if raw else None,
                 "err": e}
        row["calls"][sig] = entry
        print(f"{addr[:10]} {sig} -> uint={entry['uint']} addr={entry['addr']} bool={entry['bool']} str={entry['str']!r} err={e}", flush=True)
        save(out)

print("TRIAGE DONE", flush=True)
print(json.dumps(out, indent=1)[:4000])
