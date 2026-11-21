#!/usr/bin/env python3
"""Triage backfill run 134722590-134728589 (2026-11-21 ~15:31 WIB cron).
Read-only (Sourcify + eth_call + eth_getBlockByNumber). No preview/mint/sign.
Phase A: Sourcify ABI for all first-seen NOT already in watchlist.
Phase B: on-chain probes only for registry_bytes_hit OR ABI agentRegistry fn.
Phase C: first-mint timestamp + owner check only for registry-exact passers.
"""
import json, subprocess, sys, time
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _single
from eth_hash.auto import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
OUT = f"{BASE}/backfill-triage-134722590-134728589.json"
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
            last = f"{type(e).__name__}: {str(e)[:100]}"
    return None, last

def call(to, data, pause=2):
    r, e = rpc("eth_call", [{"to": to, "data": data}, "latest"])
    time.sleep(pause)
    return r, e

def dec_addr(raw):
    if isinstance(raw, str) and raw.startswith("0x") and len(raw) >= 66:
        return "0x" + raw[-40:]
    return None

def dec_uint(raw):
    if isinstance(raw, str) and raw.startswith("0x"):
        try:
            return int(raw, 16)
        except Exception:
            return None
    return None

def dec_str(raw):
    # abi-encoded string: offset(32) len(32) data
    try:
        if not raw or not raw.startswith("0x") or len(raw) < 194:
            return None
        ln = int(raw[66:130], 16)
        data = bytes.fromhex(raw[130:130 + ln * 2])
        return data.decode("utf-8", "replace")
    except Exception:
        return None

def sourcify(addr):
    url = f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi"
    for attempt in range(2):
        try:
            p = subprocess.run(["curl", "-s", "-m", "25", url],
                               capture_output=True, text=True, timeout=35)
            d = json.loads(p.stdout)
            if isinstance(d, dict) and isinstance(d.get("abi"), list):
                return d["abi"], None
            if isinstance(d, dict) and "message" in d:
                return None, str(d.get("message"))[:80]
            return None, "no-abi-field"
        except Exception as e:
            err = f"{type(e).__name__}: {str(e)[:80]}"
            time.sleep(3)
    return None, err

def save(obj):
    tmp = OUT + ".tmp"
    json.dump(obj, open(tmp, "w"), indent=1)
    import os
    os.replace(tmp, OUT)

# ---- load candidates: first-seen NOT in watchlist ----
snap = json.load(open(f"{BASE}/onchain-snapshot.json"))
wl = set()
for v in snap.get("contracts", {}).values():
    if isinstance(v, dict) and v.get("address"):
        wl.add(v["address"].lower())
seen = {}
for f in ["backfill-134722590-134724589.json",
          "backfill-134724590-134726589.json",
          "backfill-134726590-134728589.json"]:
    d = json.load(open(f"{BASE}/{f}"))
    for e in d.get("first_seen", []):
        a = e["address"].lower()
        if a not in seen:
            seen[a] = dict(e)
        else:
            seen[a]["mint_count"] += e["mint_count"]
cands = {a: e for a, e in seen.items() if a not in wl}
print(f"total first-seen deduped={len(seen)} in-watchlist={len(seen)-len(cands)} candidates={len(cands)}", flush=True)

try:
    out = json.load(open(OUT))
except Exception:
    out = {}

REG_FNS = {"agentRegistry", "AGENT_ID_REGISTRY", "AGENT_REGISTRY", "REGISTRY"}
FREE_FNS = {"freeMinted", "freeClaimed", "freeSupply", "freeLeft", "FREE_SUPPLY",
            "FREE_SLOTS", "freeFor", "mintFree", "freeMint", "claimFree", "freeClaim"}
QUOTE_FNS = {"quote"}

# ---- Phase A: Sourcify ----
for a, e in sorted(cands.items(), key=lambda kv: -kv[1]["mint_count"]):
    addr = e["address"]
    row = out.get(addr, {"address": addr, "kind": e.get("kind"),
                         "mint_count": e["mint_count"],
                         "first_block": e["first_block"],
                         "registry_bytes_hit": bool(e.get("registry_bytes_hit"))})
    if "sourcify" not in row:
        abi, err = sourcify(addr)
        if abi is None:
            row["sourcify"] = {"verified": False, "error": err}
        else:
            fns = sorted({fn.get("name") for fn in abi
                          if fn.get("type") == "function" and fn.get("name")})
            row["sourcify"] = {"verified": True, "functions": fns,
                               "has_registry_fn": bool(set(fns) & REG_FNS),
                               "has_free_fn": bool(set(fns) & FREE_FNS),
                               "has_quote_fn": bool(set(fns) & QUOTE_FNS)}
        out[addr] = row
        save(out)
        s = row["sourcify"]
        print(f"{addr} mint={e['mint_count']} regbytes={row['registry_bytes_hit']} "
              f"sourcify_verified={s['verified']} regfn={s.get('has_registry_fn')} "
              f"freefn={s.get('has_free_fn')} quotefn={s.get('has_quote_fn')} "
              f"err={s.get('error')}", flush=True)

# ---- Phase B: on-chain probes for regbytes OR ABI registry fn ----
PROBES = [("agentRegistry()", "zero"), ("AGENT_ID_REGISTRY()", "zero"),
          ("freeLeft()", "zero"), ("FREE_SUPPLY()", "zero"),
          ("freeMinted()", "zero"), ("freeSupply()", "zero"),
          ("freeClaimed(address)", "addr"), ("quote(address,uint256)", "addr_uint"),
          ("PRICE()", "zero"), ("totalSupply()", "zero"),
          ("MAX_SUPPLY()", "zero"), ("mintOpen()", "zero"),
          ("owner()", "zero"), ("name()", "zero"), ("symbol()", "zero")]
for a, e in sorted(cands.items(), key=lambda kv: -kv[1]["mint_count"]):
    addr = e["address"]
    row = out[addr]
    need = row["registry_bytes_hit"] or row["sourcify"].get("has_registry_fn")
    if not need:
        continue
    if "calls" in row and row["calls"].get("agentRegistry()"):
        print(f"{addr} probes already done, skip", flush=True)
        continue
    print(f"== probing {addr} mint={e['mint_count']} ==", flush=True)
    calls = row.get("calls", {})
    for sig, kind in PROBES:
        if sig in calls and calls[sig].get("raw"):
            continue
        data = sel(sig)
        if kind == "addr":
            data += USER_PAD
        elif kind == "addr_uint":
            data += USER_PAD + ONE
        raw, err = call(addr, data)
        calls[sig] = {"raw": (raw or "")[:130],
                      "uint": dec_uint(raw) if raw else None,
                      "addr": dec_addr(raw) if raw else None,
                      "str": dec_str(raw) if raw and sig in ("name()", "symbol()") else None,
                      "error": err}
        print(f"  {sig}: uint={calls[sig]['uint']} addr={calls[sig]['addr']} "
              f"str={calls[sig]['str']} err={str(err)[:80] if err else None}", flush=True)
        row["calls"] = calls
        out[addr] = row
        save(out)

# ---- Phase C: timestamp + owner-discard check for registry-exact passers ----
disc = json.load(open(f"{BASE}/same-owner-discards.json"))
disc_owners = {r["owner"].lower() for r in disc if r.get("owner")}
for a, e in sorted(cands.items(), key=lambda kv: -kv[1]["mint_count"]):
    addr = e["address"]
    row = out[addr]
    calls = row.get("calls", {})
    reg = calls.get("agentRegistry()", {}).get("addr")
    if not reg:
        continue
    row["registry_exact"] = (reg.lower() == REGISTRY.lower())
    if row["registry_exact"]:
        fb = e["first_block"]
        if "first_mint_ts" not in row:
            blk, err = rpc("eth_getBlockByNumber", [hex(fb), False])
            ts = None
            if isinstance(blk, dict) and blk.get("timestamp"):
                ts = int(blk["timestamp"], 16)
            row["first_mint_ts"] = ts
            row["first_mint_ts_error"] = err
            print(f"{addr} registry EXACT, first_block={fb} ts={ts}", flush=True)
        own = calls.get("owner()", {}).get("addr")
        row["owner"] = own
        row["same_owner_discard"] = bool(own and own.lower() in disc_owners)
        print(f"{addr} owner={own} same_owner_discard={row['same_owner_discard']}", flush=True)
    else:
        print(f"{addr} registry NOT exact: {reg} (expected {REGISTRY})", flush=True)
    out[addr] = row
    save(out)

print("DONE", flush=True)
