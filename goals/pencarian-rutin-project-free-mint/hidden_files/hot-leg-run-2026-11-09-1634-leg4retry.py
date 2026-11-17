#!/usr/bin/env python3
"""Hot-leg run 2026-11-09 16:34 WIB — LEG 4 RETRY ONLY (lean).

The full 1634 runner completed legs 1-2 + bridge, then stalled in the leg-4
prefetch: fast_rpc batch() walks the healthy-endpoint list, but ALL BSC
endpoints are circuit-breaker-open right now (latency ~8s = timeout), so
batch() failed every chunk and the per-call race fallback burned ~10s per
call sequentially. This retry pins ONE endpoint per batch chunk (publicnode,
then dataseed1/2) with a 20s timeout; a reverting item fails fast and falls
back to a per-call pinned batch (revert returns immediately, no timeout
burn). Read-only except own hot-leg state files. Never writes main snapshot.
"""
import json, sys, time
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import batch
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TS = "2026-11-09-1634"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
NOW = "2026-11-09T16:47:00+07:00"
EPS_PIN = ["https://bsc.publicnode.com/", "https://bsc-dataseed1.bnbchain.org/",
           "https://bsc-dataseed2.bnbchain.org/"]
t0 = time.time()
out = {"run": "free-mint-hot-leg 2026-11-09 16:34:38 WIB (leg4 retry)", "leg4_retry": True}

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc_addr(a): return a[2:].lower().rjust(64, "0")
def enc_u(n): return format(n, "064x")
def to_int(v):
    try: return int(v, 16)
    except Exception: return None
def call_data(addr, sig, args=None):
    data = sel(sig)
    if args:
        for a in args:
            data += enc_addr(a) if isinstance(a, str) and a.startswith("0x") else enc_u(a)
    return data

# ITEMS: parsed from the full 1634 runner (ast, no execution of its legs).
import ast
src = open(f"{BASE}/hot-leg-run-{TS}.py").read()
tree = ast.parse(src)
ITEMS = None
for node in tree.body:
    if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") == "ITEMS":
        ITEMS = ast.literal_eval(node.value)
assert ITEMS, "ITEMS not found"
out["leg4_items"] = len(ITEMS)

def pinned_batch(calls, timeout=20):
    last = None
    for ep in EPS_PIN:
        try:
            return batch(calls, endpoint=ep, timeout=timeout), ep
        except Exception as e:
            last = e
            continue
    raise IOError(f"pinned batch failed on all endpoints: {last}")

def single_pinned(addr, sig, args=None, timeout=12):
    c = [("eth_call", [{"to": addr, "data": call_data(addr, sig, args)}, "latest"])]
    try:
        res, _ep = pinned_batch(c, timeout=timeout)
        return to_int(res[0])
    except Exception:
        return None

# Build the full call list, chunked at 25 (dataseed batch cap <50).
keys, calls = [], []
for name, (addr, views) in ITEMS.items():
    for sig in views:
        if "(address)" in sig:
            args = [USER]
        elif sig == "quote(address,uint256)":
            args = [USER, 1]
        elif sig == "freeFor(address,uint256)":
            args = [USER, 1]
        else:
            args = None
        keys.append((name, addr, sig, tuple(args) if args else None))
        calls.append(("eth_call", [{"to": addr, "data": call_data(addr, sig, args)}, "latest"]))
out["leg4_calls"] = len(calls)
cache = {}
chunk_stats = []
for i in range(0, len(calls), 25):
    cc, ck = calls[i:i + 25], keys[i:i + 25]
    try:
        res, ep = pinned_batch(cc, timeout=20)
        for k, r in zip(ck, res):
            cache[(k[1], k[2], k[3])] = to_int(r)
        chunk_stats.append({"chunk": i // 25, "endpoint": ep, "mode": "batch", "n": len(cc)})
    except Exception as e:
        # Chunk failed (usually one reverting item kills the batch): per-call.
        n_ok = n_none = 0
        for k, c in zip(ck, cc):
            v = single_pinned(k[1], k[2], list(k[3]) if k[3] else None)
            cache[(k[1], k[2], k[3])] = v
            if v is None:
                n_none += 1
            else:
                n_ok += 1
        chunk_stats.append({"chunk": i // 25, "mode": "per-call-fallback",
                            "ok": n_ok, "none": n_none, "err": str(e)[:120]})
out["leg4_chunks"] = chunk_stats

try:
    b, _ep = pinned_batch([("eth_blockNumber", [])], timeout=20)
    block = int(b[0], 16)
except Exception as e:
    block = None
    out["leg4_block_error"] = str(e)

def single(addr, sig, args=None):
    key = (addr, sig, tuple(args) if args else None)
    if key in cache:
        return cache[key]
    return single_pinned(addr, sig, args)

reread = {"block": block, "items": {}}
for name, (addr, views) in ITEMS.items():
    d = {"address": addr}
    for sig in views:
        base = sig.split("(")[0]
        if "(address)" in sig:
            d[base + "_user"] = single(addr, sig, [USER])
        elif sig == "quote(address,uint256)":
            d["quote_user1"] = single(addr, sig, [USER, 1])
        elif sig == "freeFor(address,uint256)":
            d["freeFor_user1"] = single(addr, sig, [USER, 1])
        else:
            d[base] = single(addr, sig)
    reread["items"][name] = d
reread["duration_sec"] = round(time.time() - t0, 1)
json.dump(reread, open(f"{BASE}/hot-leg-{TS}-reread.json", "w"), indent=1)
out["leg4_priority"] = reread

# --- diff vs 1624 reread (same logic as the 1629 runner) ---
snap = json.load(open(f"{BASE}/onchain-snapshot.json"))
seen = json.load(open(f"{BASE}/hot-leg-seen.json"))
changes, read_artifacts, promo_flags = [], [], []
try:
    prev_items, prev_blocks = {}, {}
    try:
        pd = json.load(open(f"{BASE}/hot-leg-2026-11-09-1624-reread.json"))
        prev_items.update(pd.get("items", {}))
        prev_blocks["hot-leg-2026-11-09-1624-reread.json"] = pd.get("block")
    except Exception as e:
        out.setdefault("leg4_diff_prev_notes", []).append(f"1624 reread: {e}")
    out["leg4_diff_prev"] = prev_blocks
    reported = json.load(open(f"{BASE}/hot-leg-reported.json"))
    rep_addrs = {k.lower().split("#")[0] for k in reported}
    ghost_age = {"verdict": "AGE-EXCLUDED >48h (verified first-mint time 2026-11-05 22:14:54 WIB, run 0639)"}
    for name, d in reread["items"].items():
        p = prev_items.get(name, {})
        for k, v in d.items():
            if k == "address":
                continue
            if k in p and p[k] != v:
                if p[k] is None or v is None:
                    read_artifacts.append({"item": name, "field": k, "old": p[k], "new": v})
                else:
                    changes.append({"item": name, "field": k, "old": p[k], "new": v})
        num = d.get("freeMinted") or d.get("freeClaimed") or d.get("freeMintedTotal")
        den = d.get("FREE_CAP") or d.get("FREE_SUPPLY") or d.get("FREE_SHARES")
        if isinstance(num, int) and isinstance(den, int) and den > 0:
            pct = num / den
            slot_open = ((d.get("freeLeft_user") or 0) > 0 or d.get("freeFor_user1") == 1
                         or d.get("quote_user1") == 0 or d.get("freeClaimed_user") == 0
                         or d.get("freeCount_user") == 0)
            minted_by_user = (d.get("balanceOf_user") or 0) > 0 or d.get("freeClaimed_user") == 1
            addr_low = d.get("address", "").lower()
            seen_entry = seen.get(d.get("address")) or seen.get(addr_low) or {}
            seen_status = seen_entry.get("status", "") if isinstance(seen_entry, dict) else ""
            snap_status = ""
            for _v in snap.get("contracts", {}).values():
                if isinstance(_v, dict) and str(_v.get("address", "")).lower() == addr_low:
                    snap_status = str(_v.get("status", "")); break
            age_excluded = seen_status == "checked-not-lead-age-excluded"
            already_reported_snap = any(t in snap_status for t in ("strong-lead", "early-lead-reported", "gate-blocked", "candidate", "sold-out"))
            ghostling_age_ok = True
            if name == "Ghostling":
                ghostling_age_ok = ghost_age.get("verdict", "").startswith("VERIFIED")
            discarded = False
            try:
                _disc = json.load(open(f"{BASE}/same-owner-discards.json"))
                discarded = any(isinstance(_e, dict) and _e.get("discarded_wib") and
                                str(_e.get("contract", "")).lower() == addr_low for _e in _disc)
            except Exception:
                discarded = False
            if pct >= 0.25 and slot_open and not minted_by_user and addr_low not in rep_addrs \
                    and not age_excluded and not already_reported_snap and ghostling_age_ok and not discarded:
                promo_flags.append({"item": name, "address": d.get("address"), "pct": round(pct, 4),
                                    "free": num, "cap": den})
            elif pct >= 0.25 and slot_open and not minted_by_user:
                promo_flags.append({"item": name, "address": d.get("address"), "pct": round(pct, 4),
                                    "free": num, "cap": den, "suppressed": True,
                                    "reason": ("same-owner-discarded" if discarded else
                                               "age-excluded" if age_excluded else
                                               "already-reported-in-snapshot" if already_reported_snap else
                                               "ghostling-age-unverified" if name == "Ghostling" else
                                               "already-in-hot-leg-reported")})
except Exception as e:
    out["leg4_diff_error"] = f"{type(e).__name__}: {e}"
out["leg4_changes"] = changes
out["leg4_read_artifacts"] = read_artifacts
out["leg4_promo_flags"] = promo_flags
# Ghostling seen-note append (age-excluded, numbers only).
try:
    gseen = seen.get("0x6a4847cb5f658943222fbd23d2520049f824789d", {})
    _prior = (gseen.get("note", "") or "")
    _g = reread["items"].get("Ghostling", {})
    seen["0x6a4847cb5f658943222fbd23d2520049f824789d"] = {
        "first_seen_wib": gseen.get("first_seen_wib", NOW),
        "note": (_prior + f" | Run 1634: freeClaimed {_g.get('freeClaimed')}/7000, "
                 f"slot open (freeLeft {_g.get('freeLeft_user')}, quote {_g.get('quote_user1')}). "
                 f"AGE-EXCLUDED >48h (verified first-mint time 2026-11-05 22:14:54 WIB, run 0639)."),
        "source": "boltbook-en",
        "status": "checked-not-lead-age-excluded"}
    json.dump(seen, open(f"{BASE}/hot-leg-seen.json", "w"), indent=1)
except Exception as e:
    out["ghostling_age_seen_update_error"] = str(e)
out["duration_s"] = round(time.time() - t0, 1)
json.dump(out, open(f"{BASE}/hot-leg-run-{TS}-leg4retry.json", "w"), indent=1)
print(json.dumps({"block": block, "changes": changes, "read_artifacts": read_artifacts,
                  "promo_flags": promo_flags, "chunks": chunk_stats,
                  "duration_s": out["duration_s"]}, indent=1, default=str))
