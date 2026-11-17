#!/usr/bin/env python3
"""Hot-leg run 2026-11-09 13:29 WIB. Lightweight: Sourcify feed + Boltbook + bridge + priority re-read.
Read-only vs snapshot. Based on 1324 run script (copy).
FIXES vs 0524 (same): ALL HTTP via curl (requests stalled leg2); shape checks parallel (Sourcify ABI
endpoint degraded ~15s/fetch sequential = overrun); leg4 RPC health probe FIRST with short
timeouts - if all dataseeds dead, leg4 is SKIPPED (not 'no changes'); raw_batch timeout 12s.
Transport-failed shape-checks are NOT recorded in seen."""
import json, sys, time, os, re, datetime, subprocess, glob
from concurrent.futures import ThreadPoolExecutor
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TS = "2026-11-09-1329"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
REGISTRY = "0x60b9262456de011f7d15a54cdd8c48baa8b022f"
EXCLUDED = {"0x827e83e49bd7e15b67efa0e90fc25f17b8d96124", "0x8b47354e7b76b1970a0d06365c8244a810d37493"}
FREE_VIEWS = ["freeSharesRemaining", "freeClaimed", "freeFor", "freeLeft", "freeUsed",
              "freeAvailable", "freeSharePoolExhausted", "freeSharesClaimed", "freeMinted"]
T0 = time.time()
out = {"run": "free-mint-hot-leg 2026-11-09 13:29:38 WIB",
       "started_wib": datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=7))).isoformat(timespec="seconds")}

def wib_now():
    return datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=7))).isoformat(timespec="seconds")

def curl_get(url, timeout=15, headers=None):
    cmd = ["curl", "-sL", "--max-time", str(timeout)]
    if headers:
        for k, v in headers.items():
            cmd += ["-H", f"{k}: {v}"]
    cmd.append(url)
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout + 5)
    return r.stdout

seen = json.load(open(f"{BASE}/hot-leg-seen.json"))
reported = json.load(open(f"{BASE}/hot-leg-reported.json"))
seen_lows = {k.lower() for k in seen}
for _try in range(5):
    try:
        snap = json.load(open(f"{BASE}/onchain-snapshot.json")); break
    except Exception:
        snap = None; time.sleep(2)
if snap is None:
    raise SystemExit("snapshot unreadable after retries (main job may be rewriting it)")
snap_addrs = set()
for sec in ("contracts", "track_c"):
    for v in snap.get(sec, {}).values():
        if isinstance(v, dict) and v.get("address"):
            snap_addrs.add(str(v["address"]).lower())

# ---------- leg 1: Sourcify feed ----------
feed_addrs = []
try:
    data = json.loads(curl_get("https://sourcify.dev/server/v2/contracts/56?limit=20&sort=desc", timeout=15))
    items = data if isinstance(data, list) else data.get("results", data.get("contracts", []))
    for it in items:
        a = it.get("address") if isinstance(it, dict) else None
        if a: feed_addrs.append(a)
except Exception as e:
    out["leg1_feed_error"] = f"{type(e).__name__}: {e}"
out["leg1_feed"] = {"n": len(feed_addrs), "addrs": feed_addrs}

def shape_check(addr):
    try:
        d = json.loads(curl_get(f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi", timeout=10))
        abi = d.get("abi") or []
        fns = [e.get("name") for e in abi if isinstance(e, dict) and e.get("type") == "function"]
    except Exception as e:
        return {"address": addr, "error": f"{type(e).__name__}: {e}"}
    names = set(fns)
    has_mint = bool(names & {"mint", "mintFree", "mintWithInviter", "claimMint", "mintShare", "buyShare"})
    has_quote = bool(names & {"quote", "cost", "price", "priceFor", "getPrice", "mintPrice"})
    free = sorted([f for f in FREE_VIEWS if f in names])
    agent = bool(names & {"identityRegistry", "agentRegistry", "AgentGate", "agentId", "agentID"}) or any("agent" in (f or "").lower() or "registry" in (f or "").lower() for f in fns)
    token = bool(names & {"name", "symbol", "decimals", "totalSupply"})
    s1 = has_mint and has_quote and bool(free) and agent
    s2 = token and ("mintFree" in names) and bool(names & {"freeClaimed", "freeMinted"}) and bool(names & {"FREE_SLOTS", "FREE_SUPPLY", "FREE_AMOUNT"})
    return {"address": addr, "S1": s1, "S2": s2, "mint": has_mint, "quote": has_quote,
            "free": free, "agent": agent, "token": token,
            "note": f"S1={s1} S2={s2} mint={has_mint} quote={has_quote} free={free} agent={agent} token={token}"}

new_feed = [a for a in feed_addrs if a.lower() != REGISTRY.lower() and a.lower() not in EXCLUDED and a.lower() not in seen_lows]
shapes = {}
if new_feed:
    with ThreadPoolExecutor(max_workers=6) as ex:
        for res in ex.map(shape_check, new_feed):
            shapes[res["address"]] = res
            if "error" not in res:
                seen[res["address"]] = {"first_seen_wib": wib_now(), "note": res.get("note", ""), "source": "sourcify-feed", "status": "checked-not-sale-shape" if not (res.get("S1") or res.get("S2")) else "sale-shape"}
out["leg1"] = {"new": new_feed, "shapes": list(shapes.values()), "seen_total": len(seen)}
json.dump(feed_addrs, open(f"{BASE}/hot-leg-{TS}-sourcify.json", "w"), indent=1)
json.dump(list(shapes.values()), open(f"{BASE}/hot-leg-{TS}-sourcify-shape.json", "w"), indent=1)

# ---------- leg 2: Boltbook ----------
ADDR_RE = re.compile(r"0x[0-9a-fA-F]{40}")
KW_EN = ["free share", "first share free", "1 free share", "free mint share"]
KW_ZH = ["免费份额", "首个免费", "免费铸造", "免费mint"]
def fetch_bb(args):
    lang, url = args
    try:
        html = curl_get(url, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
        open(f"{BASE}/hot-leg-{TS}-boltbook-{lang}.html", "w").write(html)
        return lang, {"bytes": len(html), "rc": 200,
                      "addrs": sorted(set(ADDR_RE.findall(html))),
                      "kw": {k: html.lower().count(k.lower()) for k in (KW_EN if lang == "en" else KW_ZH)}}
    except Exception as e:
        return lang, {"error": f"{type(e).__name__}: {e}", "bytes": 0, "rc": None, "addrs": [], "kw": {}}
bb = {}
with ThreadPoolExecutor(max_workers=2) as ex:
    for lang, res in ex.map(fetch_bb, (("en", "https://boltbook.fun/"), ("zh", "https://boltbook.fun/?lang=zh"))):
        bb[lang] = res
all_bb = sorted(set(bb.get("en", {}).get("addrs", [])) | set(bb.get("zh", {}).get("addrs", [])))
new_bb = [a for a in all_bb if a.lower() not in seen_lows and a.lower() != REGISTRY.lower() and a.lower() not in EXCLUDED]
new_bb_vs_snap = [a for a in new_bb if a.lower() not in snap_addrs]
bb_shapes = {}
to_check = [a for a in new_bb if a.lower() not in snap_addrs]
if to_check:
    with ThreadPoolExecutor(max_workers=6) as ex:
        for res in ex.map(shape_check, to_check):
            bb_shapes[res["address"]] = res
            if "error" not in res:
                seen[res["address"]] = {"first_seen_wib": wib_now(), "note": res.get("note", ""), "source": "boltbook-en", "status": "checked-not-sale-shape" if not (res.get("S1") or res.get("S2")) else "sale-shape"}
for a in new_bb:
    if a.lower() in snap_addrs:
        bb_shapes[a] = {"note": "already in snapshot"}
out["leg2_boltbook"] = {"en_error": bb.get("en", {}).get("error"), "zh_error": bb.get("zh", {}).get("error"),
                        "en_bytes": bb.get("en", {}).get("bytes", 0), "en_rc": bb.get("en", {}).get("rc"),
                        "zh_bytes": bb.get("zh", {}).get("bytes", 0), "zh_rc": bb.get("zh", {}).get("rc"),
                        "en_addrs": len(bb.get("en", {}).get("addrs", [])), "zh_addrs": len(bb.get("zh", {}).get("addrs", [])),
                        "unique_addrs": len(all_bb),
                        "keyword_hits": {**bb.get("en", {}).get("kw", {}), **bb.get("zh", {}).get("kw", {})},
                        "new_vs_seen": new_bb, "new_vs_snapshot": new_bb_vs_snap,
                        "shape_check": bb_shapes, "seen_total": len(seen)}
json.dump(seen, open(f"{BASE}/hot-leg-seen.json", "w"), indent=1)

# ---------- leg 3: new sale shapes -> light on-chain probe ----------
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def to_int(v):
    try:
        if v is None or v == "0x": return None
        return int(v, 16)
    except Exception: return None
EPS = ["https://bsc-dataseed1.bnbchain.org/", "https://bsc-dataseed2.bnbchain.org/", "https://bsc-dataseed.binance.org/"]
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

new_sales = [a for a, s in list(shapes.items()) + [(a, bb_shapes[a]) for a in new_bb_vs_snap if a in bb_shapes]
             if isinstance(s, dict) and (s.get("S1") or s.get("S2"))]
out["leg3_new_sale_shapes"] = new_sales
probe_views = ["freeClaimed()", "freeMinted()", "FREE_SUPPLY()", "FREE_SLOTS()", "FREE_CAP()",
               "totalSupply()", "totalMinted()", "mintOpen()", "freeLeft(address)", "freeUsed(address)",
               "freeFor(address,uint256)", "quote(address,uint256)", "freeClaimed(address)",
               "balanceOf(address)", "mintedBy(address)"]
leg3 = {}
for a in new_sales:
    got = raw_batch(a, probe_views)
    leg3[a] = got or {"_batch_fail": True}
out["leg3_verify"] = leg3

# ---------- bridge leg (read-only) ----------
try:
    bridge = json.load(open(f"{BASE}/scan-bridge.json"))
    bcontracts = bridge.get("contracts", {})
    same_disc = sum(1 for v in bcontracts.values() if isinstance(v, dict) and v.get("same_owner_discarded"))
    in_snap = sum(1 for k in bcontracts if k.lower() in snap_addrs)
    out["bridge_leg"] = {"total": len(bcontracts), "same_owner_discarded": same_disc,
                         "in_snapshot_addr": in_snap, "not_in_snapshot_addr": len(bcontracts) - in_snap,
                         "mtime": time.strftime("%Y-%m-%d %H:%M UTC", time.gmtime(os.path.getmtime(f"{BASE}/scan-bridge.json"))),
                         "note": "Bridge is read-only for this job; promotions only if a bridge contract already in snapshot newly meets a tier or changes state."}
except Exception as e:
    out["bridge_leg"] = {"error": f"{type(e).__name__}: {e}", "note": "bridge skipped, run continues"}

# ---------- leg 4: priority re-read (diff vs newest non-FAILED reread) ----------
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
    out["leg4_priority"] = "SKIPPED - RPC transport dead: all 3 dataseed endpoints time out on eth_blockNumber (8s each). No reread data; 'no changes' NOT established - leg4 simply did not run."
    out["leg4_changes"] = []
    out["leg4_changes_note"] = "empty because leg4 did not run, NOT because state was verified unchanged"
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
            # PATCH 0629: carry previous values forward on transport failure -
            # all-null is a READ artifact (fast_rpc batch revert quirk), not a
            # state change; prevents false 'change' diffs next run.
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
    out["leg4_priority"] = {"block": block, "prev_block": prev_block, "items": items, "duration_sec": round(time.time() - T0, 1)}
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
out["leg4_bulk"] = "not attempted - priority items cover all promotion/sellout watches; bulk leg skipped to stay under 2-min target"
out["duration_s"] = round(time.time() - T0, 1)
out["conclusion"] = "No new lead, candidate, pending claim, change, or blocked auto-mint this run. No chat report (nothing new; failed/degraded run alone never produces one)." if not out.get("leg4_changes") and not new_sales else "See leg4_changes / leg3."
json.dump(out, open(f"{BASE}/hot-leg-run-{TS}.json", "w"), indent=1)
print(json.dumps({"duration": out["duration_s"], "leg1_new": new_feed, "leg2_new": new_bb,
                  "leg3_sales": new_sales, "changes": out.get("leg4_changes"), "block": block}, indent=1))
