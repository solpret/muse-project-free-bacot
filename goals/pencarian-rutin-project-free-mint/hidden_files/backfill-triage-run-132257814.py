#!/usr/bin/env python3
"""Triage backfill run 132257814-132260648: 1 first-seen (ZSEAT).
Read-only. Decisive selectors only, one endpoint at a time, 3s pause.
Saves incrementally to backfill-triage-132257814-132260648.json.
"""
import json, sys, time
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _single
from eth_hash.auto import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
OUT = f"{BASE}/backfill-triage-132257814-132260648.json"
REGISTRY = "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
USER_PAD = USER[2:].lower().rjust(64, "0")
ONE = "0000000000000000000000000000000000000000000000000000000000000001"
EPS = ["https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/",
       "https://bsc-dataseed.binance.org/",
       "https://bsc-dataseed3.bnbchain.org/",
       "https://bsc-rpc.publicnode.com/"]
ADDR = "0xA5C09809Ada4969FBe1D67A9034Ed9633C98Ab87"

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
    time.sleep(3)
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

def save(obj):
    tmp = OUT + ".tmp"
    json.dump(obj, open(tmp, "w"), indent=1)
    import os
    os.replace(tmp, OUT)

out = {"address": ADDR, "name": "ZenithArena Seat", "symbol": "ZSEAT",
       "kind": "ERC721", "first_block": 132259700, "last_block": 132260641,
       "mint_count_window": 56, "distinct_minters_window": 56,
       "sourcify": "not_verified (HTTP 404 via curl, 2026-11-08 ~03:0x WIB)",
       "calls": {}}
save(out)

SIGS = [("agentRegistry()", "zero", "addr"),
        ("agentIdRegistry()", "zero", "addr"),
        ("AGENT_ID_REGISTRY()", "zero", "addr"),
        ("AGENT_REGISTRY()", "zero", "addr"),
        ("REGISTRY()", "zero", "addr"),
        ("owner()", "zero", "addr"),
        ("name()", "zero", "str"),
        ("symbol()", "zero", "str"),
        ("totalSupply()", "zero", "uint"),
        ("MAX_SUPPLY()", "zero", "uint"),
        ("maxSupply()", "zero", "uint"),
        ("PRICE()", "zero", "uint"),
        ("price()", "zero", "uint"),
        ("mintPrice()", "zero", "uint"),
        ("FREE_SUPPLY()", "zero", "uint"),
        ("freeSupply()", "zero", "uint"),
        ("freeMinted()", "zero", "uint"),
        ("freeLeft()", "zero", "uint"),
        ("freeClaimed(address)", "addr", "uint"),
        ("freeFor(address)", "addr", "uint"),
        ("freeCount(address)", "addr", "uint"),
        ("mintOpen()", "zero", "bool"),
        ("maxPerWallet()", "zero", "uint"),
        ("FREE_PER_WALLET()", "zero", "uint"),
        ("quote(address,uint256)", "addr_uint", "uint"),
        ("quote(uint256)", "uint", "uint"),
        ("priceFor(address,uint256)", "addr_uint", "uint"),
        ("minted(address)", "addr", "uint"),
        ("spotsLeft()", "zero", "uint"),
        ("totalMinted()", "zero", "uint")]

for sig, kind, dec in SIGS:
    if sig in out["calls"] and out["calls"][sig].get("raw"):
        continue
    data = sel(sig)
    if kind == "addr":
        data += USER_PAD
    elif kind == "uint":
        data += ONE
    elif kind == "addr_uint":
        data += USER_PAD + ONE
    raw, e = call(ADDR, data)
    row = {"raw": (raw or "")[:130], "error": e}
    if dec == "addr":
        row["addr"] = dec_addr(raw) if raw else None
    elif dec == "uint":
        row["uint"] = dec_uint(raw) if raw else None
    elif dec == "bool":
        row["bool"] = dec_bool(raw) if raw else None
    out["calls"][sig] = row
    print(f"{sig}: raw={(raw or '')[:66]} -> {row.get('addr') or row.get('uint') if dec!='bool' else row.get('bool')} err={str(e)[:80] if e else None}", flush=True)
    save(out)

# first-mint block timestamp via eth_getBlockByNumber (fast_rpc/dataseed only, NEVER Ankr)
blk, e = rpc("eth_getBlockByNumber", [hex(132259700), False], timeout=10)
ts = None
if isinstance(blk, dict):
    ts = blk.get("timestamp")
    if isinstance(ts, str):
        ts = int(ts, 16)
out["first_block_timestamp"] = ts
out["first_block_timestamp_error"] = e
print(f"first block 132259700 timestamp: {ts} err={e}", flush=True)
save(out)

# owner vs discards
disc = json.load(open(f"{BASE}/same-owner-discards.json"))
owners = set()
if isinstance(disc, list):
    for r in disc:
        if isinstance(r, dict):
            owners.add(str(r.get("owner", "")).lower())
        elif isinstance(r, str):
            owners.add(r.lower())
elif isinstance(disc, dict):
    for r in disc.get("records", disc.get("discards", [])):
        if isinstance(r, dict):
            owners.add(str(r.get("owner", "")).lower())
out["owner_in_discards"] = (out["calls"].get("owner()", {}).get("addr") or "").lower() in owners if out["calls"].get("owner()", {}).get("addr") else None
print(f"owner_in_discards: {out['owner_in_discards']} (discards entries: {len(owners)})", flush=True)
save(out)
print("TRIAGE DONE", flush=True)
