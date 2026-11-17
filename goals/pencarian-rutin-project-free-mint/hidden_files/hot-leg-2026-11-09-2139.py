#!/usr/bin/env python3
"""Hot-leg run 2026-11-09 21:39 WIB (scheduled 21:39:38).
Legs 1-2 live (Sourcify feed + Boltbook EN/ZH), leg 3 only if new sale shape,
leg 4 priority re-read, bridge leg read-only. Adapted from hot-leg-2026-11-09-2119.py (identical legs)."""
import json, time, os, glob, subprocess, datetime, re, urllib.request
from concurrent.futures import ThreadPoolExecutor
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TS = "2026-11-09-2139"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
REGISTRY = "0x60b9262456de011f7d15a54cdd8c48baa8b022f"
T0 = time.time()
WIB = datetime.timezone(datetime.timedelta(hours=7))

def wib_now():
    return datetime.datetime.now(WIB).isoformat(timespec="seconds")

seen = json.load(open(f"{BASE}/hot-leg-seen.json"))
reported = json.load(open(f"{BASE}/hot-leg-reported.json"))
seen_low = {k.lower(): k for k in seen}
out = {"run": "free-mint-hot-leg 2026-11-09 21:39:38 WIB", "started_wib": wib_now()}

def http_get(url, timeout=20):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.status, r.read()

FREE_VIEWS = ["freeSharesRemaining", "freeClaimed", "freeFor", "freeLeft", "freeUsed",
              "freeAvailable", "freeSharePoolExhausted", "freeSharesClaimed", "freeMinted"]

def shape_check(addr):
    """Return dict with S1/S2 flags using Sourcify v2 ABI.
    ROUTE FIX 2026-11-09 21:33 WIB: Sourcify removed API v1; the old plural route
    GET /v2/contracts/56/{addr} now 404s for every contract. Working route:
    GET /v2/contract/56/{addr}?fields=abi (singular, returns {"abi": [...]}).
    curl is used instead of urllib: urllib hit IncompleteRead on ~28KB metadata
    bodies this run. A v2 404 / match=null means the contract is NOT verified
    on Sourcify (no ABI available), not a transport failure."""
    try:
        r = subprocess.run(["curl", "-sL", "--max-time", "25", "-A", "Mozilla/5.0",
                            f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi"],
                           capture_output=True, text=True, timeout=30)
        if r.returncode != 0:
            return {"error": f"curl rc={r.returncode}"}
        d = json.loads(r.stdout)
        abi = d.get("abi") or []
        if isinstance(abi, str):
            abi = json.loads(abi)
        fns = {}
        for e in abi:
            if isinstance(e, dict) and e.get("type") == "function":
                fns.setdefault(e.get("name"), []).append(e)
        names = set(fns)
        has_mint = any(n.startswith("mint") for n in names)
        has_quote = bool(names & {"quote", "cost", "priceFor", "getQuote"})
        free_hits = sorted(names & set(FREE_VIEWS))
        src = json.dumps(d)
        has_agent = ("0x60b9262456de011f7d15a54cdd8c48baa8b022f" in src.lower()
                     or "agentgate" in src.lower() or "agentidregistry" in src.lower()
                     or "AgentGate" in src or "AGENT_ID_REGISTRY" in src)
        s1 = has_mint and has_quote and bool(free_hits) and has_agent
        is_token = bool(names & {"name", "symbol", "decimals", "totalSupply"})
        s2 = is_token and ("mintFree" in names) and bool(names & {"freeClaimed", "freeMinted"}) \
             and bool(names & {"FREE_SLOTS", "FREE_SUPPLY", "FREE_AMOUNT"}) and has_agent
        return {"s1": s1, "s2": s2, "mint": has_mint, "quote": has_quote,
                "free": free_hits, "agent": has_agent, "token": is_token,
                "fn_names": sorted(names)[:60]}
    except Exception as e:
        return {"error": f"{type(e).__name__}: {e}"}

# ---- leg 1: Sourcify feed ----
try:
    st, body = http_get("https://sourcify.dev/server/v2/contracts/56?limit=20&sort=desc", timeout=25)
    feed = json.loads(body)
    addrs = []
    # FEED SHAPE FIX 2026-11-09 21:29 WIB: list endpoint now returns
    # {"results": [...]} (was a bare list at 20:54); handle all three shapes.
    _items = feed if isinstance(feed, list) else (feed.get("results") or feed.get("contracts") or [])
    for item in _items:
        a = item.get("address") or (item.get("contract", {}) or {}).get("address")
        if a:
            addrs.append(a)
    feed_n = len(addrs)
except Exception as e:
    addrs, feed_n = [], 0
    out["leg1_error"] = f"{type(e).__name__}: {e}"

EXCLUDED = {"0x827e83e49bd7e15b67efa0e90fc25f17b8d96124",
            "0x8b47354e7b76b1970a0d06365c8244a810d37493"}
new_addrs = [a for a in addrs if a.lower() not in seen_low and a.lower() != REGISTRY.lower()
             and a.lower() not in EXCLUDED]
leg1 = {"feed_n": feed_n, "new": new_addrs, "shapes": {}}
for a in new_addrs:
    sc = shape_check(a)
    leg1["shapes"][a] = sc
    if sc.get("s1") or sc.get("s2"):
        seen[a] = {"first_seen_wib": wib_now(),
                   "note": f"SALE SHAPE {'S1' if sc.get('s1') else 'S2'} PASS from Sourcify feed: {sc}",
                   "source": "sourcify-feed", "status": "sale-shape-new"}
    elif "error" in sc:
        seen[a] = {"first_seen_wib": wib_now(), "note": f"ABI fetch error: {sc['error']}",
                   "source": "sourcify-feed", "status": "checked-abi-unavailable"}
    else:
        seen[a] = {"first_seen_wib": wib_now(),
                   "note": f"S1={sc.get('s1')} S2={sc.get('s2')} mint={sc.get('mint')} quote={sc.get('quote')} free={sc.get('free')} agent={sc.get('agent')} token={sc.get('token')}",
                   "source": "sourcify-feed", "status": "checked-not-sale-shape"}
leg1["seen_total"] = len(seen)
out["leg1"] = leg1
json.dump(seen, open(f"{BASE}/hot-leg-seen.json", "w"), indent=1)

# ---- leg 2: Boltbook EN + ZH ----
def boltbook(lang):
    try:
        st, body = http_get(f"https://boltbook.fun/?lang={lang}", timeout=25)
        if st == 200 and len(body) > 1000:
            return st, body.decode("utf-8", "replace")
    except Exception:
        pass
    # curl fallback: urllib has intermittently returned 44-byte error bodies
    try:
        r = subprocess.run(["curl", "-sL", "--max-time", "25", "-A", "Mozilla/5.0",
                            f"https://boltbook.fun/?lang={lang}"],
                           capture_output=True, timeout=30)
        if r.returncode == 0 and len(r.stdout) > 1000:
            return 200, r.stdout.decode("utf-8", "replace")
        return None, f"curl short/empty body ({len(r.stdout)} bytes)"
    except Exception as e:
        return None, f"{type(e).__name__}: {e}"

en_st, en = boltbook("en")
zh_st, zh = boltbook("zh")
addrs_bb = set()
kw_hits = []
for txt, lang in ((en, "en"), (zh, "zh")):
    if isinstance(txt, str):
        for m in re.findall(r"0x[0-9a-fA-F]{40}", txt):
            addrs_bb.add(m)
        for kw in ("free share", "first share free", "1 free share", "free mint share",
                   "免费份额", "首个免费", "免费铸造", "免费mint"):
            if kw.lower() in txt.lower():
                kw_hits.append(f"{lang}:{kw}")
bb_new = [a for a in sorted(addrs_bb) if a.lower() not in seen_low and a.lower() not in EXCLUDED]
bb_sale_shapes = []
for a in bb_new:
    sc = shape_check(a)
    if sc.get("s1") or sc.get("s2"):
        bb_sale_shapes.append(a)
        seen[a] = {"first_seen_wib": wib_now(),
                   "note": f"SALE SHAPE {'S1' if sc.get('s1') else 'S2'} PASS from boltbook.fun front page: {sc}",
                   "source": "boltbook-frontpage", "status": "sale-shape-new"}
    elif "error" in sc:
        seen[a] = {"first_seen_wib": wib_now(), "note": f"From boltbook.fun front page; ABI fetch error: {sc['error']}",
                   "source": "boltbook-frontpage", "status": "checked-abi-unavailable"}
    else:
        seen[a] = {"first_seen_wib": wib_now(),
                   "note": f"From boltbook.fun front page. S1={sc.get('s1')} S2={sc.get('s2')} mint={sc.get('mint')} quote={sc.get('quote')} free={sc.get('free')} agent={sc.get('agent')} token={sc.get('token')}",
                   "source": "boltbook-frontpage", "status": "checked-not-sale-shape"}
out["leg2_boltbook"] = {"en_status": en_st, "en_bytes": len(en) if isinstance(en, str) else 0,
                        "zh_status": zh_st, "zh_bytes": len(zh) if isinstance(zh, str) else 0,
                        "unique_addresses": len(addrs_bb), "new_vs_seen": bb_new,
                        "keyword_hits": sorted(set(kw_hits))}
json.dump(seen, open(f"{BASE}/hot-leg-seen.json", "w"), indent=1)

# ---- leg 3: fast on-chain probe for NEW sale shapes found this run ----
leg3 = {"new_sale_shapes": [], "probes": {}}
_sale_new = [a for a, sc in leg1["shapes"].items() if sc.get("s1") or sc.get("s2")] + bb_sale_shapes
leg3["new_sale_shapes"] = _sale_new
if _sale_new:
    _EPS3 = ["https://bsc-dataseed.binance.org/", "https://bsc.publicnode.com"]
    def _sel3(s):
        k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
    def _call3(addr, data):
        payload = {"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                   "params": [{"to": addr, "data": data}, "latest"]}
        for ep in _EPS3:
            try:
                r = subprocess.run(["curl", "-sL", "--max-time", "10", "-X", "POST", ep,
                                    "-H", "Content-Type: application/json", "-d", json.dumps(payload)],
                                   capture_output=True, text=True, timeout=15)
                d = json.loads(r.stdout)
                if isinstance(d, dict) and "result" in d and d["result"] not in (None, "0x"):
                    return int(d["result"], 16)
                return None
            except Exception:
                continue
        return None
    for a in _sale_new:
        p = {}
        for fn in ("freeClaimed()", "freeMinted()", "FREE_SUPPLY()", "FREE_SLOTS()",
                   "freeLeft()", "freeSharesRemaining()"):
            p[fn[:-2]] = _call3(a, _sel3(fn))
        p["freeClaimed_user"] = _call3(a, _sel3("freeClaimed(address)") + USER[2:].lower().rjust(64, "0"))
        p["quote_user1"] = _call3(a, _sel3("quote(address,uint256)") + USER[2:].lower().rjust(64, "0") + format(1, "064x"))
        # Age: first-mint time needs eth_getLogs (Ankr quota 0% until 1 Dec; public RPCs -32005) -> unverifiable this run.
        p["age"] = "unverified-no-logs-source"
        leg3["probes"][a] = p
        pool = p.get("freeClaimed") or p.get("freeMinted")
        cap = p.get("FREE_SUPPLY") or p.get("FREE_SLOTS")
        slot_open = (p.get("freeClaimed_user") == 0) or (p.get("quote_user1") == 0)
        if pool is not None and cap and pool < cap and slot_open:
            seen[a]["status"] = "sale-shape-age-unverified-watchlist"
            seen[a]["note"] += f" | leg3 pool {pool}/{cap}, user slot open, AGE UNVERIFIED (no logs source) -> watchlist-only, never a lead."
        elif pool is not None and cap and pool >= cap:
            seen[a]["status"] = "sale-shape-sold-out"
            seen[a]["note"] += f" | leg3 pool {pool}/{cap} SOLD OUT."
        else:
            seen[a]["status"] = "sale-shape-pool-unverified"
            seen[a]["note"] += " | leg3 pool/slot reads inconclusive (views absent or RPC fail)."
        json.dump(seen, open(f"{BASE}/hot-leg-seen.json", "w"), indent=1)
out["leg3"] = leg3

# ---- snapshot + bridge (read-only) ----
for _try in range(5):
    try:
        snap = json.load(open(f"{BASE}/onchain-snapshot.json")); break
    except Exception:
        snap = None; time.sleep(2)
if snap is None:
    raise SystemExit("snapshot unreadable after retries")
snap_addrs = set()
for sec in ("contracts", "track_c"):
    for v in snap.get(sec, {}).values():
        if isinstance(v, dict) and v.get("address"):
            snap_addrs.add(str(v["address"]).lower())
try:
    bridge = json.load(open(f"{BASE}/scan-bridge.json"))
    bcontracts = bridge.get("contracts", {})
    same_disc = sum(1 for v in bcontracts.values() if isinstance(v, dict) and v.get("same_owner_discarded"))
    in_snap = sum(1 for k in bcontracts if k.lower() in snap_addrs)
    out["bridge_leg"] = {"total": len(bcontracts), "same_owner_discarded": same_disc,
                         "in_snapshot_addr": in_snap, "not_in_snapshot_addr": len(bcontracts) - in_snap,
                         "mtime": time.strftime("%Y-%m-%d %H:%M UTC", time.gmtime(os.path.getmtime(f"{BASE}/scan-bridge.json"))),
                         "note": "Bridge read-only; promotions only if a bridge contract already in snapshot newly meets a tier or changes state."}
except Exception as e:
    out["bridge_leg"] = {"error": f"{type(e).__name__}: {e}", "note": "bridge skipped, run continues"}

# ---- leg 4: priority re-read (same mechanism as 2034 run) ----
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def to_int(v):
    try:
        if v is None or v == "0x": return None
        return int(v, 16)
    except Exception: return None
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc.publicnode.com", "https://bsc-dataseed1.bnbchain.org/"]
def post_rpc(ep, payload, timeout=12):
    r = subprocess.run(["curl", "-sL", "--max-time", str(timeout), "-X", "POST", ep,
                        "-H", "Content-Type: application/json", "-d", json.dumps(payload)],
                       capture_output=True, text=True, timeout=timeout + 5)
    return json.loads(r.stdout)
def rpc_healthy():
    for ep in EPS:
        try:
            r = post_rpc(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}, timeout=8)
            if r.get("result"): return ep, int(r["result"], 16)
        except Exception:
            continue
    return None, None
def raw_batch(addr, views):
    calls, keys = [], []
    for i, sig in enumerate(views):
        base = sig.split("(")[0]
        if "(address,uint256)" in sig:
            data = sel(sig) + enc(USER) + format(1, "064x"); key = base + "_user1"
        elif "(address)" in sig:
            data = sel(sig) + enc(USER); key = base + "_user"
        else:
            data = sel(sig); key = base
        calls.append({"jsonrpc": "2.0", "id": i + 1, "method": "eth_call",
                      "params": [{"to": addr, "data": data}, "latest"]})
        keys.append(key)
    for ep in EPS:
        try:
            res = post_rpc(ep, calls, timeout=12)
            if not isinstance(res, list) or len(res) != len(calls): continue
            outd = {}
            for item, key in zip(res, keys):
                outd[key] = None if (isinstance(item, dict) and "error" in item) else (to_int(item.get("result")) if isinstance(item, dict) else None)
            return outd
        except Exception:
            continue
    return None

FIELD_TO_SIG = {
    "freeMinted": "freeMinted()", "FREE_CAP": "FREE_CAP()", "freeCount_user": "freeCount(address)",
    "mintOpen": "mintOpen()", "balanceOf_user": "balanceOf(address)", "totalSupply": "totalSupply()",
    "FREE_SUPPLY": "FREE_SUPPLY()", "mintedBy_user": "mintedBy(address)", "FREE_SHARES": "FREE_SHARES()",
    "totalMinted": "totalMinted()", "finalized": "finalized()", "freeClaimed_user": "freeClaimed(address)",
    "freeClaimed": "freeClaimed()", "freeLeft": "freeLeft()", "remainingFree": "remainingFree()",
    "FREE_QUOTA": "FREE_QUOTA()", "freeUsed": "freeUsed()", "freeTakenBy_user": "freeTakenBy(address)",
    "MAX_SUPPLY": "MAX_SUPPLY()", "totalMints": "totalMints()", "mintActive": "mintActive()",
    "freeMintedTotal": "freeMintedTotal()", "quote_user1": "quote(address,uint256)",
    "freeLeft_user": "freeLeft(address)", "freeUsed_user": "freeUsed(address)",
    "freeFor_user1": "freeFor(address,uint256)", "priceFor_user": "priceFor(address)",
    "FREE_PER_WALLET": "FREE_PER_WALLET()", "mintedCount_user": "mintedCount(address)",
    "freeMinted_user": "freeMinted(address)", "phase": "phase()", "launched": "launched()",
    "sold": "sold()", "MAX_FREE": "MAX_FREE()", "sharesMinted": "sharesMinted()",
    "soldOut": "soldOut()", "closed": "closed()", "freeAvailable_user": "freeAvailable(address)",
    "hasMinted_user": "hasMinted(address)", "quotaOf_user": "quotaOf(address)",
}
def _load_prev():
    cands = sorted(glob.glob(f"{BASE}/hot-leg-*-reread.json"), reverse=True)
    for _f in cands:
        try:
            _d = json.load(open(_f))
        except Exception:
            continue
        if _d.get("FAILED"):
            continue
        _items = _d.get("items", {})
        if _d.get("block") is None and _items and all(v.get("_batch_fail") for v in _items.values()):
            continue
        out["leg4_diff_prev_file"] = _f.split("/")[-1]
        return _d
    out["leg4_diff_prev_file"] = None
    return {"items": {}, "block": None}
prev = _load_prev()
prev_items = prev.get("items", {})
prev_block = prev.get("block")

healthy_ep, block = rpc_healthy()
out["leg4_rpc"] = {"healthy_endpoint": healthy_ep, "block": block}
if healthy_ep is None:
    out["leg4_priority"] = "SKIPPED - RPC transport dead. No reread data; 'no changes' NOT established."
    out["leg4_changes"] = []
    out["leg4_promo_flags"] = []
else:
    items = {}
    def read_item(kv):
        name, prevd = kv
        addr = prevd["address"]
        views = [FIELD_TO_SIG[f] for f in prevd if f in FIELD_TO_SIG]
        got = raw_batch(addr, views)
        d = {"address": addr}
        if got is None:
            d["_batch_fail"] = True
            for f in prevd:
                if f != "address": d[f] = prevd[f]
        else:
            d.update(got)
        return name, d
    with ThreadPoolExecutor(max_workers=8) as ex:
        for name, d in ex.map(read_item, list(prev_items.items())):
            items[name] = d
    json.dump({"block": block, "items": items, "duration_sec": round(time.time() - T0, 1)},
              open(f"{BASE}/hot-leg-{TS}-reread.json", "w"), indent=1)
    out["leg4_priority"] = {"block": block, "prev_block": prev_block, "n_items": len(items), "duration_sec": round(time.time() - T0, 1)}
    changes = []
    for name, d in items.items():
        pd = prev_items.get(name)
        if not pd or d.get("_batch_fail"): continue
        for f, v in d.items():
            if f in ("address", "_batch_fail"): continue
            ov = pd.get(f)
            if v != ov and not (v is None and ov is None):
                changes.append({"item": name, "field": f, "old": ov, "new": v})
    out["leg4_changes"] = changes
    snap_contracts = snap.get("contracts", {})
    snap_status_by_addr = {}
    for _v in snap_contracts.values():
        if isinstance(_v, dict) and _v.get("address"):
            snap_status_by_addr[str(_v["address"]).lower()] = str(_v.get("status", ""))
    rep_addrs = {k.lower().split("#")[0] for k in reported}
    seen_by_low = {k.lower(): v for k, v in seen.items()}
    try:
        _disc = json.load(open(f"{BASE}/same-owner-discards.json"))
        same_owner_discards_lows = {str(e.get("contract", "")).lower() for e in _disc if isinstance(e, dict)}
    except Exception:
        same_owner_discards_lows = set()
    promo = []
    for name, d in items.items():
        if d.get("_batch_fail"): continue
        cap = d.get("FREE_SUPPLY") or d.get("FREE_CAP") or d.get("FREE_SHARES") or d.get("FREE_QUOTA") or d.get("MAX_FREE")
        claimed = d.get("freeClaimed") if d.get("freeClaimed") is not None else d.get("freeMinted")
        if cap and claimed is not None:
            pct = claimed / cap
            if pct >= 0.99:
                ent_status = snap_status_by_addr.get(d["address"].lower(), "")
                reason = "already-reported-in-snapshot" if "sold" in ent_status else "check-main-job"
                promo.append({"item": name, "address": d["address"], "pct": round(pct, 4),
                              "free": claimed, "cap": cap, "suppressed": True,
                              "reason": reason, "kind": "sellout-or-near"})
            elif pct >= 0.25:
                slot_open = ((d.get("freeLeft_user") or 0) > 0 or d.get("freeFor_user1") == 1
                             or d.get("quote_user1") == 0 or d.get("freeClaimed_user") == 0
                             or d.get("freeCount_user") == 0)
                minted_by_user = (d.get("balanceOf_user") or 0) > 0 or d.get("freeClaimed_user") == 1
                addr_low = d["address"].lower()
                seen_entry = seen_by_low.get(addr_low, {})
                seen_status = seen_entry.get("status", "") if isinstance(seen_entry, dict) else ""
                snap_status = snap_status_by_addr.get(addr_low, "")
                age_excluded = seen_status == "checked-not-lead-age-excluded"
                already_reported_snap = any(t in snap_status for t in ("strong-lead", "early-lead-reported", "gate-blocked", "candidate", "sold-out"))
                gate_blocked_reported = any(k.lower().startswith(addr_low + "#gate-blocked") for k in reported)
                discarded = addr_low in same_owner_discards_lows
                if pct >= 0.25 and slot_open and not minted_by_user and addr_low not in rep_addrs \
                        and not age_excluded and not already_reported_snap and not gate_blocked_reported and not discarded:
                    promo.append({"item": name, "address": d["address"], "pct": round(pct, 4),
                                  "free": claimed, "cap": cap, "kind": "strong-lead-promotion-candidate",
                                  "note": "needs age verification + website gate before any lead/preview"})
                elif pct >= 0.25 and slot_open and not minted_by_user:
                    promo.append({"item": name, "address": d["address"], "pct": round(pct, 4),
                                  "free": claimed, "cap": cap, "suppressed": True,
                                  "reason": ("same-owner-discarded" if discarded else
                                             "age-excluded" if age_excluded else
                                             "already-reported-in-snapshot" if already_reported_snap else
                                             "gate-blocked-already-reported" if gate_blocked_reported else
                                             "already-in-hot-leg-reported"),
                                  "kind": "strong-lead-promotion-candidate"})
    out["leg4_promo_flags"] = promo
out["pending_claims"] = snap.get("pending_claims") or "snapshot pending_claims empty at run start - nothing to re-read"
out["duration_s"] = round(time.time() - T0, 1)
json.dump(out, open(f"{BASE}/hot-leg-run-{TS}.json", "w"), indent=1)
print(json.dumps({"duration": out["duration_s"], "block": block,
                  "leg1": leg1, "leg2": out["leg2_boltbook"], "leg3": out.get("leg3"),
                  "changes": out.get("leg4_changes"), "promo": out.get("leg4_promo_flags"),
                  "bridge": out.get("bridge_leg")}, indent=1))
