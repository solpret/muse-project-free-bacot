#!/usr/bin/env python3
"""Hot-leg run 2026-11-09 02:04 WIB. Lightweight: Sourcify feed + Boltbook + bridge + priority re-read. Read-only vs snapshot. Based on 02:04 run script; prev reread = 0204."""
import json, sys, time, os, re, datetime
import requests
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _post as _fr_post
from concurrent.futures import ThreadPoolExecutor
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TS = "2026-11-09-0209"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
REGISTRY = "0x60b9262456de011f7d15a54cdd8c48baa8b022f"
EXCLUDED = {"0x827e83e49bd7e15b67efa0e90fc25f17b8d96124", "0x8b47354e7b76b1970a0d06365c8244a810d37493"}
FREE_VIEWS = ["freeSharesRemaining", "freeClaimed", "freeFor", "freeLeft", "freeUsed",
              "freeAvailable", "freeSharePoolExhausted", "freeSharesClaimed", "freeMinted"]
T0 = time.time()
now_wib = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=7))).isoformat(timespec="seconds")
out = {"run": "free-mint-hot-leg 2026-11-09 02:09:38 WIB", "started_wib": now_wib}

def wib_now():
    return datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=7))).isoformat(timespec="seconds")

# ---------- leg 1: Sourcify feed ----------
feed_addrs = []
try:
    r = requests.get("https://sourcify.dev/server/v2/contracts/56?limit=20&sort=desc", timeout=15)
    data = r.json()
    items = data if isinstance(data, list) else data.get("results", data.get("contracts", []))
    for it in items:
        a = it.get("address") if isinstance(it, dict) else None
        if a: feed_addrs.append(a)
except Exception as e:
    out["leg1_feed_error"] = f"{type(e).__name__}: {e}"
out["leg1_feed"] = {"n": len(feed_addrs), "addrs": feed_addrs}

seen = json.load(open(f"{BASE}/hot-leg-seen.json"))
reported = json.load(open(f"{BASE}/hot-leg-reported.json"))
snap = json.load(open(f"{BASE}/onchain-snapshot.json"))
snap_addrs = {str(v.get("address", "")).lower() for v in snap.get("contracts", {}).values() if isinstance(v, dict)}
snap_addrs |= {str(v.get("address", "")).lower() for v in snap.get("track_c", {}).values() if isinstance(v, dict)}

def shape_check(addr):
    """S1/S2 shape from Sourcify ABI function names."""
    try:
        r = requests.get(f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi", timeout=12)
        d = r.json()
        abi = d.get("abi") or []
        fns = [e.get("name") for e in abi if isinstance(e, dict) and e.get("type") == "function"]
    except Exception as e:
        return {"address": addr, "error": f"{type(e).__name__}: {e}"}
    names = set(fns)
    has_mint = bool(names & {"mint", "mintFree", "mintWithInviter", "claimMint", "mintShare", "buyShare"})
    has_quote = bool(names & {"quote", "cost", "price", "priceFor", "getPrice", "mintPrice"})
    free = sorted([f for f in FREE_VIEWS if f in names])
    agent = bool(names & {"identityRegistry", "agentRegistry", "AgentGate", "agentId", "agentID"}) or any("agent" in (f or "").lower() or "registry" in (f or "").lower() for f in fns)
    token = bool({"name", "symbol", "decimals", "totalSupply"} <= names)
    s1 = has_mint and has_quote and bool(free) and agent
    s2 = token and ("mintFree" in names) and bool(names & {"freeClaimed", "freeMinted"}) and bool(names & {"FREE_SLOTS", "FREE_SUPPLY", "FREE_AMOUNT"})
    return {"address": addr, "S1": s1, "S2": s2, "mint": has_mint, "quote": has_quote,
            "free": free, "agent": agent, "token": token,
            "note": f"S1={s1} S2={s2} mint={has_mint} quote={has_quote} free={free} agent={agent} token={token}"}

new_feed = []
for a in feed_addrs:
    al = a.lower()
    if al == REGISTRY.lower() or al in EXCLUDED: continue
    if al in {k.lower() for k in seen}: continue
    new_feed.append(a)
shapes = {}
for a in new_feed:
    shapes[a] = shape_check(a)
    seen[a] = {"first_seen_wib": wib_now(), "note": shapes[a].get("note", shapes[a].get("error", ""))}
    time.sleep(0.2)
out["leg1"] = {"new": new_feed, "shapes": list(shapes.values()), "seen_total": len(seen)}
json.dump(feed_addrs, open(f"{BASE}/hot-leg-{TS}-sourcify.json", "w"), indent=1)
json.dump(list(shapes.values()), open(f"{BASE}/hot-leg-{TS}-sourcify-shape.json", "w"), indent=1)

# ---------- leg 2: Boltbook ----------
ADDR_RE = re.compile(r"0x[0-9a-fA-F]{40}")
KW_EN = ["free share", "first share free", "1 free share", "free mint share"]
KW_ZH = ["免费份额", "首个免费", "免费铸造", "免费mint"]
bb = {}
for lang, url in (("en", "https://boltbook.fun/"), ("zh", "https://boltbook.fun/?lang=zh")):
    try:
        r = requests.get(url, timeout=20, headers={"User-Agent": "Mozilla/5.0"})
        html = r.text
        open(f"{BASE}/hot-leg-{TS}-boltbook-{lang}.html", "w").write(html)
        bb[lang] = {"bytes": len(html), "rc": r.status_code,
                    "addrs": sorted(set(ADDR_RE.findall(html))),
                    "kw": {k: html.lower().count(k.lower()) for k in (KW_EN if lang == "en" else KW_ZH)}}
    except Exception as e:
        bb[lang] = {"error": f"{type(e).__name__}: {e}", "bytes": 0, "rc": None, "addrs": [], "kw": {}}
all_bb = sorted(set(bb.get("en", {}).get("addrs", [])) | set(bb.get("zh", {}).get("addrs", [])))
new_bb = [a for a in all_bb if a.lower() not in {k.lower() for k in seen} and a.lower() != REGISTRY.lower() and a.lower() not in EXCLUDED]
new_bb_vs_snap = [a for a in new_bb if a.lower() not in snap_addrs]
bb_shapes = {}
for a in new_bb:
    if a.lower() in snap_addrs:
        bb_shapes[a] = {"note": "already in snapshot"}
        continue
    bb_shapes[a] = shape_check(a)
    seen[a] = {"first_seen_wib": wib_now(), "note": bb_shapes[a].get("note", bb_shapes[a].get("error", ""))}
    time.sleep(0.2)
out["leg2_boltbook"] = {"en_bytes": bb.get("en", {}).get("bytes", 0), "en_rc": bb.get("en", {}).get("rc"),
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
            res = _fr_post(ep, calls, timeout=30, retries=0)
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
    baddrs = set(bcontracts.keys())
    same_disc = sum(1 for v in bcontracts.values() if isinstance(v, dict) and v.get("same_owner_discarded"))
    in_snap = sum(1 for k in baddrs if k.lower() in snap_addrs)
    out["bridge_leg"] = {"total": len(bcontracts), "same_owner_discarded": same_disc,
                         "in_snapshot_addr": in_snap, "not_in_snapshot_addr": len(bcontracts) - in_snap,
                         "mtime": time.strftime("%Y-%m-%d %H:%M UTC", time.gmtime(os.path.getmtime(f"{BASE}/scan-bridge.json"))),
                         "note": "Bridge is read-only for this job; promotions only if a bridge contract already in snapshot newly meets a tier or changes state."}
except Exception as e:
    out["bridge_leg"] = {"error": f"{type(e).__name__}: {e}", "note": "bridge skipped, run continues"}

# ---------- leg 4: priority re-read (diff vs 01:24 run) ----------
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
prev = json.load(open(f"{BASE}/hot-leg-2026-11-09-0204-reread.json"))
prev_items = prev.get("items", {})
prev_block = prev.get("block")

def get_block():
    for ep in EPS:
        try:
            r = _fr_post(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}, timeout=15, retries=0)
            return int(r["result"], 16)
        except Exception:
            continue
    return None

block = get_block()
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
            if f != "address": d[f] = None
    else:
        d.update(got)
    return name, d

todo = list(prev_items.items())
with ThreadPoolExecutor(max_workers=8) as ex:
    for name, d in ex.map(read_item, todo):
        items[name] = d
json.dump({"block": block, "items": items, "duration_sec": round(time.time() - T0, 1)},
          open(f"{BASE}/hot-leg-{TS}-reread.json", "w"), indent=1)
out["leg4_priority"] = {"block": block, "prev_block": prev_block, "items": items, "duration_sec": round(time.time() - T0, 1)}

# diff vs 02:04
changes = []
for name, d in items.items():
    pd = prev_items.get(name)
    if not pd: continue
    for f, v in d.items():
        if f in ("address", "_batch_fail"): continue
        ov = pd.get(f)
        if v != ov and not (v is None and ov is None):
            changes.append({"item": name, "field": f, "old": ov, "new": v})
out["leg4_changes"] = changes

# promo / sellout flags (suppressed with reason when already known)
snap_contracts = snap.get("contracts", {})
snap_status_by_addr = {}
for _v in snap_contracts.values():
    if isinstance(_v, dict) and _v.get("address"):
        snap_status_by_addr[str(_v["address"]).lower()] = str(_v.get("status", ""))
rep_addrs = {k.lower().split("#")[0] for k in reported}
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
            # strong-lead promotion check: slot open + not minted by user + not already known
            slot_open = ((d.get("freeLeft_user") or 0) > 0 or d.get("freeFor_user1") == 1
                         or d.get("quote_user1") == 0 or d.get("freeClaimed_user") == 0
                         or d.get("freeCount_user") == 0)
            minted_by_user = (d.get("balanceOf_user") or 0) > 0 or d.get("freeClaimed_user") == 1
            addr_low = d["address"].lower()
            seen_entry = seen.get(d["address"]) or seen.get(addr_low) or {}
            seen_status = seen_entry.get("status", "") if isinstance(seen_entry, dict) else ""
            snap_status = snap_status_by_addr.get(addr_low, "")
            age_excluded = seen_status == "checked-not-lead-age-excluded"
            already_reported_snap = any(t in snap_status for t in ("strong-lead", "early-lead-reported", "gate-blocked", "candidate", "sold-out"))
            gate_blocked_reported = any(k.lower().startswith(addr_low + "#gate-blocked") for k in reported)
            if pct >= 0.25 and slot_open and not minted_by_user and addr_low not in rep_addrs \
                    and not age_excluded and not already_reported_snap and not gate_blocked_reported:
                promo.append({"item": name, "address": d["address"], "pct": round(pct, 4),
                              "free": claimed, "cap": cap, "kind": "strong-lead-promotion-candidate",
                              "note": "needs age verification + website gate before any lead/preview"})
            elif pct >= 0.25 and slot_open and not minted_by_user:
                promo.append({"item": name, "address": d["address"], "pct": round(pct, 4),
                              "free": claimed, "cap": cap, "suppressed": True,
                              "reason": ("age-excluded" if age_excluded else
                                         "already-reported-in-snapshot" if already_reported_snap else
                                         "gate-blocked-already-reported" if gate_blocked_reported else
                                         "already-in-hot-leg-reported"),
                              "kind": "strong-lead-promotion-candidate"})
out["leg4_promo_flags"] = promo
out["pending_claims"] = "snapshot pending_claims empty at run start - nothing to re-read"
out["leg4_bulk"] = "not attempted - priority items cover all promotion/sellout watches; bulk leg skipped to stay under 2-min target"
out["duration_s"] = round(time.time() - T0, 1)
json.dump(out, open(f"{BASE}/hot-leg-run-{TS}.json", "w"), indent=1)
print(json.dumps({"duration": out["duration_s"], "leg1_new": new_feed, "leg2_new": new_bb,
                  "leg3_sales": new_sales, "changes": len(changes), "block": block}, indent=1))
