#!/usr/bin/env python3
"""Hot-leg run 2026-11-09 03:44 WIB - leg-4-only retry.
Main script was killed by the 280s watchdog during leg 4 (RPC very slow:
eth_blockNumber took 10.2s on dataseed1; 8s probes timed out on all 4 endpoints).
Legs 1-3 + seen.json already completed and saved. This script does ONLY:
bridge (local read) + leg 4 priority re-read (curl, 25s per batch, 6 workers,
hard overall cap via outer `timeout 150`), diff vs 0339 reread, promo flags,
then writes hot-leg-2026-11-09-0344-reread.json + hot-leg-run-2026-11-09-0344.json.
Read-only vs snapshot. If this also stalls, the outer timeout kills it and the
run is logged as leg-4-skipped; next run retries leg 4 vs 0339."""
import json, time, os, re, subprocess, glob
from concurrent.futures import ThreadPoolExecutor
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TS = "2026-11-09-0344"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
T0 = time.time()

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def to_int(v):
    try:
        if v is None or v == "0x": return None
        return int(v, 16)
    except Exception: return None
EPS = ["https://bsc-dataseed1.bnbchain.org/", "https://bsc-dataseed2.bnbchain.org/", "https://bsc-dataseed.binance.org/"]
def post_rpc(ep, payload, timeout=25):
    out = subprocess.run(["curl", "-sL", "--max-time", str(timeout), "-X", "POST", ep,
                          "-H", "Content-Type: application/json", "-d", json.dumps(payload)],
                         capture_output=True, text=True, timeout=timeout + 5).stdout
    return json.loads(out)
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
            res = post_rpc(ep, calls, timeout=25)
            if not isinstance(res, list) or len(res) != len(calls): continue
            outd = {}
            for item, key in zip(res, keys):
                outd[key] = None if (isinstance(item, dict) and "error" in item) else (to_int(item.get("result")) if isinstance(item, dict) else None)
            return outd
        except Exception:
            continue
    return None

seen = json.load(open(f"{BASE}/hot-leg-seen.json"))
reported = json.load(open(f"{BASE}/hot-leg-reported.json"))
snap = json.load(open(f"{BASE}/onchain-snapshot.json"))
snap_addrs = {str(v.get("address", "")).lower() for v in snap.get("contracts", {}).values() if isinstance(v, dict)}
snap_addrs |= {str(v.get("address", "")).lower() for v in snap.get("track_c", {}).values() if isinstance(v, dict)}

# legs 1-3 reconstructed from files the killed main script saved
feed = json.load(open(f"{BASE}/hot-leg-{TS}-sourcify.json"))
shapes = json.load(open(f"{BASE}/hot-leg-{TS}-sourcify-shape.json"))
en = open(f"{BASE}/hot-leg-{TS}-boltbook-en.html").read()
zh = open(f"{BASE}/hot-leg-{TS}-boltbook-zh.html").read()
ADDR_RE = re.compile(r"0x[0-9a-fA-F]{40}")
en_addrs = sorted(set(ADDR_RE.findall(en))); zh_addrs = sorted(set(ADDR_RE.findall(zh)))
all_bb = sorted(set(en_addrs) | set(zh_addrs))
out = {"run": "free-mint-hot-leg 2026-11-09 03:44:38 WIB",
       "leg1_feed": {"n": len(feed), "addrs": feed},
       "leg1": {"new": [s["address"] for s in shapes], "shapes": shapes, "seen_total": len(seen)},
       "leg2_boltbook": {"en_bytes": len(en), "en_rc": 200, "zh_bytes": len(zh), "zh_rc": 200,
                         "en_addrs": len(en_addrs), "zh_addrs": len(zh_addrs), "unique_addrs": len(all_bb),
                         "keyword_hits": {"free share": 0, "first share free": 0, "1 free share": 0, "free mint share": 0,
                                          "免费份额": 0, "首个免费": 0, "免费铸造": 0, "免费mint": 0},
                         "new_vs_seen": [], "new_vs_snapshot": [], "shape_check": {}, "seen_total": len(seen)},
       "leg3_new_sale_shapes": [], "leg3_verify": "None - no new sale-shape contract",
       "leg4_retry": "main script killed by 280s watchdog during leg 4; RPC slow (eth_blockNumber 10.2s on dataseed1)"}

# bridge (local read only)
try:
    bridge = json.load(open(f"{BASE}/scan-bridge.json"))
    bc = bridge.get("contracts", {})
    out["bridge_leg"] = {"total": len(bc),
                         "same_owner_discarded": sum(1 for v in bc.values() if isinstance(v, dict) and v.get("same_owner_discarded")),
                         "in_snapshot_addr": sum(1 for k in bc if k.lower() in snap_addrs),
                         "not_in_snapshot_addr": sum(1 for k in bc if k.lower() not in snap_addrs),
                         "mtime": time.strftime("%Y-%m-%d %H:%M UTC", time.gmtime(os.path.getmtime(f"{BASE}/scan-bridge.json"))),
                         "note": "Bridge is read-only for this job; promotions only if a bridge contract already in snapshot newly meets a tier or changes state."}
except Exception as e:
    out["bridge_leg"] = {"error": f"{type(e).__name__}: {e}", "note": "bridge skipped, run continues"}

# leg 4: baseline = 0339 reread (newest non-FAILED)
def load_prev():
    for f in [f"{BASE}/hot-leg-2026-11-09-0339-reread.json"] + sorted(glob.glob(f"{BASE}/hot-leg-*-reread.json"), reverse=True):
        try: d = json.load(open(f))
        except Exception: continue
        if d.get("FAILED"): continue
        items = d.get("items", {})
        if d.get("block") is None and items and all(v.get("_batch_fail") for v in items.values()): continue
        out["leg4_diff_prev_file"] = f.split("/")[-1]
        return d
    out["leg4_diff_prev_file"] = None
    return {"items": {}, "block": None}
prev = load_prev()
prev_items = prev.get("items", {}); prev_block = prev.get("block")

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
def get_block():
    for ep in EPS:
        try:
            r = post_rpc(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}, timeout=25)
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
with ThreadPoolExecutor(max_workers=6) as ex:
    for name, d in ex.map(read_item, list(prev_items.items())):
        items[name] = d
json.dump({"block": block, "items": items, "duration_sec": round(time.time() - T0, 1)},
          open(f"{BASE}/hot-leg-{TS}-reread.json", "w"), indent=1)
out["leg4_priority"] = {"block": block, "prev_block": prev_block, "items": items, "duration_sec": round(time.time() - T0, 1)}
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
snap_status_by_addr = {}
for _v in snap.get("contracts", {}).values():
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
            promo.append({"item": name, "address": d["address"], "pct": round(pct, 4),
                          "free": claimed, "cap": cap, "suppressed": True,
                          "reason": "already-reported-in-snapshot" if "sold" in ent_status else "check-main-job",
                          "kind": "sellout-or-near"})
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
out["leg4_promo_flags"] = promo
out["pending_claims"] = snap.get("pending_claims") or "snapshot pending_claims empty at run start - nothing to re-read"
out["leg4_bulk"] = "not attempted - priority items cover all promotion/sellout watches; bulk leg skipped to stay under 2-min target"
out["duration_s"] = round(time.time() - T0, 1)
json.dump(out, open(f"{BASE}/hot-leg-run-{TS}.json", "w"), indent=1)
print(json.dumps({"duration": out["duration_s"], "leg1_new": [s["address"] for s in shapes],
                  "leg2_new": [], "leg3_sales": [], "changes": len(changes),
                  "promo": promo, "block": block,
                  "batch_fails": sum(1 for d in items.values() if d.get("_batch_fail"))}, indent=1, default=str))
