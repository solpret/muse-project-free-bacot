#!/usr/bin/env python3
"""Hot-leg 0724 leg4 retry: dataseeds dead, publicnode alive (block 132488088 probed).
One attempt only; on failure, record SKIPPED and stop."""
import json, time, datetime, subprocess
from concurrent.futures import ThreadPoolExecutor
from Crypto.Hash import keccak
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TS = "2026-11-09-0724"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
T0 = time.time()
def wib_now():
    return datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=7))).isoformat(timespec="seconds")
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def to_int(v):
    try:
        if v is None or v == "0x": return None
        return int(v, 16)
    except Exception: return None
EPS = ["https://bsc.publicnode.com", "https://bsc-dataseed1.bnbchain.org/", "https://bsc-dataseed2.bnbchain.org/", "https://bsc-dataseed.binance.org/"]
def post_rpc(ep, payload, timeout=12):
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
prev = json.load(open(f"{BASE}/hot-leg-2026-11-09-0709-reread.json"))
prev_items = prev.get("items", {})
prev_block = prev.get("block")
# health probe
block = None; healthy = None
for ep in EPS:
    try:
        r = post_rpc(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}, timeout=8)
        if r.get("result"):
            block = int(r["result"], 16); healthy = ep; break
    except Exception:
        continue
run = json.load(open(f"{BASE}/hot-leg-run-{TS}.json"))
run["leg4_retry"] = {"healthy_endpoint": healthy, "block": block}
if healthy is None:
    run["leg4_priority"] = "SKIPPED (retry) - all RPC endpoints incl. publicnode dead. No reread data; 'no changes' NOT established."
    run["leg4_changes"] = []
    run["leg4_promo_flags"] = []
    json.dump(run, open(f"{BASE}/hot-leg-run-{TS}.json", "w"), indent=1)
    print(json.dumps({"leg4": "SKIPPED", "duration": round(time.time()-T0,1)}))
else:
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
    items = {}
    with ThreadPoolExecutor(max_workers=8) as ex:
        for name, d in ex.map(read_item, list(prev_items.items())):
            items[name] = d
    json.dump({"block": block, "items": items, "duration_sec": round(time.time() - T0, 1)},
              open(f"{BASE}/hot-leg-{TS}-reread.json", "w"), indent=1)
    changes = []
    for name, d in items.items():
        pd = prev_items.get(name)
        if not pd or d.get("_batch_fail"): continue
        for f, v in d.items():
            if f in ("address", "_batch_fail"): continue
            ov = pd.get(f)
            if v != ov and not (v is None and ov is None):
                changes.append({"item": name, "field": f, "old": ov, "new": v})
    run["leg4_priority"] = {"block": block, "prev_block": prev_block, "items": items, "duration_sec": round(time.time() - T0, 1), "note": "retry via publicnode after dataseed timeouts"}
    run["leg4_changes"] = changes
    # promo flags: same logic as main script (suppressed-only check)
    snap = json.load(open(f"{BASE}/onchain-snapshot.json"))
    snap_contracts = snap.get("contracts", {})
    snap_status_by_addr = {}
    for _v in snap_contracts.values():
        if isinstance(_v, dict) and _v.get("address"):
            snap_status_by_addr[str(_v["address"]).lower()] = str(_v.get("status", ""))
    reported = json.load(open(f"{BASE}/hot-leg-reported.json"))
    seen = json.load(open(f"{BASE}/hot-leg-seen.json"))
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
                              "free": claimed, "cap": cap, "suppressed": True, "reason": reason, "kind": "sellout-or-near"})
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
    run["leg4_promo_flags"] = promo
    run["duration_s"] = round(run.get("duration_s", 0) + (time.time() - T0), 1)
    json.dump(run, open(f"{BASE}/hot-leg-run-{TS}.json", "w"), indent=1)
    print(json.dumps({"leg4": "OK", "block": block, "prev_block": prev_block, "items": len(items),
                      "batch_fail": sum(1 for v in items.values() if v.get("_batch_fail")),
                      "changes": changes, "promo": promo, "duration": round(time.time()-T0,1)}, indent=1))
