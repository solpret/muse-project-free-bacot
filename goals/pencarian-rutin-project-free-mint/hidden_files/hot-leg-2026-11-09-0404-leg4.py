#!/usr/bin/env python3
"""Leg4-only finish for hot-leg run 2026-11-09 04:04 WIB.
Both the main script and the salvage overran (Sourcify ABI endpoint degraded:
~15s per fetch). Leg1 salvage outcome already banked in seen.json (16/20 feed
contracts shape-checked, all non-sale; 4 transport-failed, not recorded).
This script does ONLY: Boltbook new-address accounting (no network) + leg4
priority re-read via curl RPC + run-file write. Strict 100s budget."""
import json, time, os, re, subprocess, datetime
from concurrent.futures import ThreadPoolExecutor
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TS = "2026-11-09-0404"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
T0 = time.time()
now_wib = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=7))).isoformat(timespec="seconds")

seen = json.load(open(f"{BASE}/hot-leg-seen.json"))
reported = json.load(open(f"{BASE}/hot-leg-reported.json"))
snap = json.load(open(f"{BASE}/onchain-snapshot.json"))
snap_addrs = {str(v.get("address", "")).lower() for v in snap.get("contracts", {}).values() if isinstance(v, dict)}
snap_addrs |= {str(v.get("address", "")).lower() for v in snap.get("track_c", {}).values() if isinstance(v, dict)}
seen_lower = {k.lower() for k in seen}

# Boltbook accounting from the two HTML files already on disk (no network)
ADDR_RE = re.compile(r"0x[0-9a-fA-F]{40}")
bb = {}
for lang, path in (("en", f"{BASE}/hot-leg-{TS}-boltbook-en.html"), ("zh", "/tmp/bb-zh.html")):
    try:
        html = open(path, errors="ignore").read()
        bb[lang] = {"bytes": len(html), "addrs": sorted(set(ADDR_RE.findall(html))),
                    "kw_free_mint": html.lower().count("free mint"),
                    "kw_zh": {k: html.lower().count(k) for k in ["免费份额", "首个免费", "免费铸造", "免费mint"]}}
    except Exception as e:
        bb[lang] = {"error": f"{type(e).__name__}: {e}", "bytes": 0, "addrs": []}
all_bb = sorted(set(bb.get("en", {}).get("addrs", [])) | set(bb.get("zh", {}).get("addrs", [])))
new_bb = [a for a in all_bb if a.lower() not in seen_lower]
new_bb_vs_snap = [a for a in new_bb if a.lower() not in snap_addrs]
# NOTE: shape-checks for new Boltbook addresses were NOT completed (salvage killed
# mid-leg2 after recording at most 1); unrecorded new addresses stay unrecorded and
# will be picked up by the next run's Boltbook leg. Record that explicitly.
leg2 = {"en_bytes": bb.get("en", {}).get("bytes", 0), "zh_bytes": bb.get("zh", {}).get("bytes", 0),
        "en_addrs": len(bb.get("en", {}).get("addrs", [])), "zh_addrs": len(bb.get("zh", {}).get("addrs", [])),
        "unique_addrs": len(all_bb), "new_vs_seen": new_bb, "new_vs_snapshot": new_bb_vs_snap,
        "shape_check": "NOT COMPLETED - salvage killed mid-leg2 (Sourcify ABI endpoint degraded); "
                       "new addresses NOT recorded in seen, retried next run",
        "keyword_hits": {"en_free_mint": bb.get("en", {}).get("kw_free_mint", 0),
                         "zh_free_mint": bb.get("zh", {}).get("kw_free_mint", 0),
                         "zh_kw": bb.get("zh", {}).get("kw_zh", {})}}

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def to_int(v):
    try:
        if v is None or v == "0x": return None
        return int(v, 16)
    except Exception: return None
EPS = ["https://bsc-dataseed1.bnbchain.org/", "https://bsc-dataseed2.bnbchain.org/"]
def post_rpc(ep, payload, timeout=20):
    r = subprocess.run(["curl", "-sL", "--max-time", str(timeout), "-X", "POST", ep,
                        "-H", "Content-Type: application/json", "-d", json.dumps(payload)],
                       capture_output=True, text=True, timeout=timeout + 5)
    return json.loads(r.stdout)
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
            res = post_rpc(ep, calls, timeout=20)
            if not isinstance(res, list) or len(res) != len(calls): continue
            return {key: (None if (isinstance(it, dict) and "error" in it) else (to_int(it.get("result")) if isinstance(it, dict) else None)) for it, key in zip(res, keys)}
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
prev = json.load(open(f"{BASE}/hot-leg-2026-11-09-0359-reread.json"))
prev_items = prev.get("items", {})
prev_block = prev.get("block")

def get_block():
    for ep in EPS:
        try:
            r = post_rpc(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}, timeout=15)
            return int(r["result"], 16)
        except Exception:
            continue
    return None

block = get_block()
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

items = {}
with ThreadPoolExecutor(max_workers=4) as ex:
    for name, d in ex.map(read_item, list(prev_items.items())):
        items[name] = d
json.dump({"block": block, "items": items, "duration_sec": round(time.time() - T0, 1)},
          open(f"{BASE}/hot-leg-{TS}-reread.json", "w"), indent=1)

changes = []
for name, d in items.items():
    pd = prev_items.get(name)
    if not pd: continue
    for f, v in d.items():
        if f in ("address", "_batch_fail"): continue
        ov = pd.get(f)
        if v != ov and not (v is None and ov is None):
            changes.append({"item": name, "field": f, "old": ov, "new": v})

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

# bridge (read-only, cheap local read)
try:
    bridge = json.load(open(f"{BASE}/scan-bridge.json"))
    bcontracts = bridge.get("contracts", {})
    baddrs = set(bcontracts.keys())
    same_disc = sum(1 for v in bcontracts.values() if isinstance(v, dict) and v.get("same_owner_discarded"))
    in_snap = sum(1 for k in baddrs if k.lower() in snap_addrs)
    bridge_leg = {"total": len(bcontracts), "same_owner_discarded": same_disc,
                  "in_snapshot_addr": in_snap, "not_in_snapshot_addr": len(bcontracts) - in_snap,
                  "mtime": time.strftime("%Y-%m-%d %H:%M UTC", time.gmtime(os.path.getmtime(f"{BASE}/scan-bridge.json"))),
                  "note": "Bridge is read-only for this job; promotions only if a bridge contract already in snapshot newly meets a tier or changes state."}
except Exception as e:
    bridge_leg = {"error": f"{type(e).__name__}: {e}", "note": "bridge skipped, run continues"}

out = {"run": "free-mint-hot-leg 2026-11-09 04:04:38 WIB (leg4-only finish after 2 overruns)",
       "started_wib": now_wib,
       "overruns": "main 0404 script killed at 280s; salvage killed at 240s (Sourcify ABI endpoint degraded, ~15s/fetch)",
       "leg1_feed": {"n": 20, "shape_checked": 16, "sale_shapes": [],
                     "transport_failed_not_recorded": ["0x9199602A03696401bc7E15343E7D9CA00997Efb4",
                        "0xe0Dc3211294F5e00677051B00816015934cCD835",
                        "0x593a98b20A78538432571cb90704A234fa9D7ED5",
                        "0x7b63b4C482E23C423ED65a8648358C5417703Ea3"],
                     "note": "16/20 feed contracts shape-checked (6 main + 10 salvage), all S1=False S2=False; 4 Sourcify ABI timeouts not recorded in seen"},
       "leg1": {"new": [], "shapes": "see hot-leg-2026-11-09-0404-sourcify-shape.json + seen.json notes", "seen_total": len(seen)},
       "leg2_boltbook": leg2,
       "leg3_new_sale_shapes": [], "leg3_verify": {},
       "bridge_leg": bridge_leg,
       "leg4_diff_prev_file": "hot-leg-2026-11-09-0359-reread.json",
       "leg4_priority": {"block": block, "prev_block": prev_block, "items": items, "duration_sec": round(time.time() - T0, 1)},
       "leg4_changes": changes,
       "leg4_promo_flags": promo,
       "pending_claims": snap.get("pending_claims") or "snapshot pending_claims empty at run start - nothing to re-read",
       "leg4_bulk": "not attempted - priority items cover all promotion/sellout watches; bulk leg skipped to stay under 2-min target",
       "duration_s": round(time.time() - T0, 1)}
json.dump(out, open(f"{BASE}/hot-leg-run-{TS}.json", "w"), indent=1)
print(json.dumps({"duration": out["duration_s"], "block": block, "prev_block": prev_block,
                  "items": len(items), "batch_fail": sum(1 for v in items.values() if v.get("_batch_fail")),
                  "changes": len(changes), "promo": promo,
                  "bb_new_vs_seen": new_bb, "bb_new_vs_snap": new_bb_vs_snap}, indent=1))
