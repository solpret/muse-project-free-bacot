#!/usr/bin/env python3
"""Velocity analysis for run 2026-11-09-0501 re-read vs onchain-snapshot.json (READ ONLY).
Velocity PASS iff current rate >= 1.5x previous rate AND >= 20 tokens minted in interval.
Interval: snapshot lastRereadWib (0401 run) -> this run read time (approx 05:01 WIB + read span).
Uses block-based interval as cross-check: BSC ~0.45s/block (per AGENTS.md).
Writes run-2026-11-09-0501-velocity.json (own new file, allowed).
"""
import json, re
from datetime import datetime, timezone, timedelta

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
WIB = timezone(timedelta(hours=7))

snap = json.load(open(f"{BASE}/onchain-snapshot.json"))
rr = json.load(open(f"{BASE}/run-2026-11-09-0501-reread.json"))

def parse_wib(s):
    if not s or not isinstance(s, str):
        return None
    m = re.match(r"(\d{4})-(\d{2})-(\d{2})[ T](\d{2}):(\d{2})", s)
    if not m:
        return None
    y, mo, d, h, mi = map(int, m.groups())
    return datetime(y, mo, d, h, mi, tzinfo=WIB)

# previous read time: snapshot last_run_wib / per-contract lastRereadWib
prev_times = []
for v in snap["contracts"].values():
    t = parse_wib(v.get("lastRereadWib") or v.get("lastReadWib"))
    if t:
        prev_times.append(t)
prev_times.sort()
print("prev read times: n=%d earliest=%s latest=%s" % (len(prev_times), prev_times[0] if prev_times else None, prev_times[-1] if prev_times else None))

# this run: block-based interval. snapshot lastRereadBlock per contract vs rr block.
cur_block = rr.get("block")
print("current block:", cur_block)

# interval minutes: assume reads centred ~05:01 + span; use 60 min nominal 0401->0501,
# but per-contract use its own lastRereadWib when available.
NOW = datetime(2026, 11, 9, 5, 1, tzinfo=WIB)

MINTED_BY_USER = {"HIVE Agents", "Bubblebruin", "Zapcourier", "Cryonyx", "Cathodex", "Kirinova"}

results = []
for name, cur in rr.get("reread", {}).items():
    s = snap["contracts"].get(name)
    if not s:
        continue
    prev_ts = s.get("previousTotalSupply")
    prev_rate = s.get("previousRatePerMin")
    cur_ts = cur.get("totalSupply")
    entry = {"name": name, "address": s.get("address"), "status": s.get("status"),
             "prevTotalSupply": prev_ts, "prevRatePerMin": prev_rate,
             "curTotalSupply": cur_ts, "batch_fail": bool(cur.get("_batch_fail"))}
    # interval minutes from this contract's last reread time to now (fallback 60)
    t0 = parse_wib(s.get("lastRereadWib") or s.get("lastReadWib"))
    entry["prevReadWib"] = s.get("lastRereadWib") or s.get("lastReadWib")
    if t0:
        entry["intervalMin"] = round((NOW - t0).total_seconds() / 60, 1)
    else:
        entry["intervalMin"] = 60.0
    if cur_ts is None or prev_ts is None:
        entry["velocity"] = "READ-FAIL / NO-BASELINE"
        entry["mintedInInterval"] = None
        entry["curRatePerMin"] = None
        entry["ratioVsPrev"] = None
        entry["pass"] = False
    else:
        minted = cur_ts - prev_ts
        entry["mintedInInterval"] = minted
        rate = minted / entry["intervalMin"] if entry["intervalMin"] > 0 else None
        entry["curRatePerMin"] = round(rate, 4) if rate is not None else None
        # 90-min cross-check rate (conservative: reads span ~04:01-04:55 -> ~05:07-05:42)
        rate90 = minted / 90.0
        entry["curRatePerMin90"] = round(rate90, 4)
        if prev_rate is None:
            entry["ratioVsPrev"] = None
            entry["ratioVsPrev90"] = None
        elif prev_rate == 0:
            # dormant baseline: any positive rate is unbounded acceleration; pass iff >=20 minted
            entry["ratioVsPrev"] = "inf" if rate and rate > 0 else 0
            entry["ratioVsPrev90"] = "inf" if rate90 > 0 else 0
        else:
            entry["ratioVsPrev"] = round(rate / prev_rate, 3) if rate is not None else None
            entry["ratioVsPrev90"] = round(rate90 / prev_rate, 3)
        r60 = entry["ratioVsPrev"]
        r60n = float("inf") if r60 == "inf" else (r60 if isinstance(r60, (int, float)) else None)
        entry["pass"] = bool(rate is not None and r60n is not None and r60n >= 1.5 and minted >= 20)
        entry["borderline90"] = bool(entry["pass"] and isinstance(entry.get("ratioVsPrev90"), (int, float)) and entry["ratioVsPrev90"] < 1.5)
        entry["velocity"] = "PASS" if entry["pass"] else "FAIL"
    # free pool / user slot deltas
    entry["prevFreeClaimed"] = s.get("freeClaimed")
    entry["curFreeClaimed"] = cur.get("freeClaimed")
    entry["prevFreeSupply"] = s.get("FREE_SUPPLY")
    entry["curFreeSupply"] = cur.get("FREE_SUPPLY")
    entry["prevMintOpen"] = s.get("mintOpen")
    entry["curMintOpen"] = cur.get("mintOpen")
    entry["prevUserBal"] = s.get("balanceOf_user") if "balanceOf_user" in s else s.get("userBalance")
    entry["curUserBal"] = cur.get("balanceOf_user")
    entry["prevFreeClaimedUser"] = s.get("freeClaimed_user")
    entry["curFreeClaimedUser"] = cur.get("freeClaimed_user")
    entry["freePoolExhausted"] = None
    if entry["curFreeClaimed"] is not None and entry["curFreeSupply"] is not None:
        entry["freePoolExhausted"] = entry["curFreeClaimed"] >= entry["curFreeSupply"]
    entry["ageHours"] = s.get("ageHours")
    entry["ageNote"] = s.get("ageNote") or s.get("ageExclusionNote")
    results.append(entry)

passes = [r for r in results if r.get("pass")]
fails = [r for r in results if not r.get("pass")]
readfail = [r for r in results if r["velocity"].startswith("READ-FAIL")]
print("velocity PASS:", len(passes))
for r in passes:
    print("  PASS %s minted=%s rate60=%s prevRate=%s ratio60=%s ratio90=%s borderline90=%s interval=%smin status=%s" % (
        r["name"], r["mintedInInterval"], r["curRatePerMin"], r["prevRatePerMin"], r["ratioVsPrev"], r["ratioVsPrev90"], r.get("borderline90"), r["intervalMin"], r["status"]))
print("velocity FAIL:", len(fails), "of which read-fail/no-baseline:", len(readfail))

# sellout / pool-exhausted among re-read contracts (only where both views present)
exhausted = [r for r in results if r.get("freePoolExhausted") is True]
print("freePoolExhausted (freeClaimed>=FREE_SUPPLY):", len(exhausted))
for r in exhausted:
    print("  EXHAUSTED?", r["name"], "freeClaimed=%s FREE_SUPPLY=%s status=%s" % (
        r["curFreeClaimed"], r["curFreeSupply"], r["status"]))

# user-slot changes: balanceOf_user or freeClaimed_user changed vs snapshot
slot_changes = []
for r in results:
    ch = []
    if r["prevUserBal"] is not None and r["curUserBal"] is not None and r["prevUserBal"] != r["curUserBal"]:
        ch.append("balanceOf_user %s -> %s" % (r["prevUserBal"], r["curUserBal"]))
    if r["prevFreeClaimedUser"] is not None and r["curFreeClaimedUser"] is not None and r["prevFreeClaimedUser"] != r["curFreeClaimedUser"]:
        ch.append("freeClaimed_user %s -> %s" % (r["prevFreeClaimedUser"], r["curFreeClaimedUser"]))
    if ch:
        slot_changes.append((r["name"], r["status"], ch))
print("user-slot changes:", len(slot_changes))
for n, st, ch in slot_changes:
    print("  SLOT", n, st, "; ".join(ch))

# 48h age exclusions: contracts with ageHours >= 48 not already age-excluded
age_excl = [r for r in results if r.get("ageHours") is not None and r["ageHours"] >= 48
            and "age-excluded" not in str(r["status"] or "")]
print("age>=48h not yet excluded:", len(age_excl))
for r in age_excl[:20]:
    print("  AGE", r["name"], "ageHours=%s status=%s" % (r["ageHours"], r["status"]))

# track_c summary
tc = rr.get("track_c", {})
tc_fail = sum(1 for v in tc.values() if v.get("_batch_fail"))
print("track_c re-read: %d (batch_fail=%d)" % (len(tc), tc_fail))

out = {"run": "2026-11-09-0501", "block": cur_block, "intervalNote": "per-contract lastRereadWib -> 2026-11-09 05:01 WIB (fallback 60 min)",
       "results": results, "passes": [r["name"] for r in passes],
       "freePoolExhausted": [r["name"] for r in exhausted],
       "slotChanges": [{"name": n, "status": st, "changes": ch} for n, st, ch in slot_changes],
       "ageGe48h": [{"name": r["name"], "ageHours": r["ageHours"], "status": r["status"]} for r in age_excl],
       "track_c_count": len(tc), "track_c_batch_fail": tc_fail}
with open(f"{BASE}/run-2026-11-09-0501-velocity.json", "w") as f:
    json.dump(out, f, indent=1)
print("WROTE run-2026-11-09-0501-velocity.json")
