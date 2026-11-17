#!/usr/bin/env python3
"""Run 2031 analysis: compare run-2026-11-08-2031-reread.json vs onchain-snapshot.json.
Velocity: rate >= 1.5x previous rate AND >= 20 minted in interval.
None = read artifact, never zero. Read-only on snapshot; writes analysis JSON only."""
import json, re
from datetime import datetime, timezone, timedelta

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
WIB = timezone(timedelta(hours=7))
NOW = datetime(2026, 11, 8, 20, 31, tzinfo=WIB)

snap = json.load(open(f"{BASE}/onchain-snapshot.json"))
rr = json.load(open(f"{BASE}/run-2026-11-08-2031-reread.json"))
contracts = snap.get("contracts", {})
reread = rr.get("reread", {})
tc_rr = rr.get("track_c", {})

def parse_wib(s):
    if not isinstance(s, str): return None
    m = re.match(r"(\d{4})-(\d{2})-(\d{2})[ T](\d{2}):(\d{2})", s)
    if not m: return None
    y, mo, d, h, mi = map(int, m.groups())
    return datetime(y, mo, d, h, mi, tzinfo=WIB)

TERMINAL = ("sold-out", "age-excluded", "minted-by-user", "excluded",
            "same-owner-discarded", "promotion-discarded")

out = {"block": rr.get("block"), "velocity_passes": [], "supply_changes": [],
       "degraded": [], "no_address_skipped": [], "age_exclusion_candidates": [],
       "track_c_changes": []}
n_supply_change = 0
for name, entry in contracts.items():
    addr = entry.get("address")
    if not addr:
        out["no_address_skipped"].append(name)
        continue
    d = reread.get(name)
    if d is None:
        out["degraded"].append({"name": name, "reason": "not in reread output"})
        continue
    old_sup = entry.get("totalSupply")
    new_sup = d.get("totalSupply")
    old_m = entry.get("totalMinted")
    new_m = d.get("totalMinted")
    # prefer totalSupply, else totalMinted
    if old_sup is not None and new_sup is not None:
        delta, base = new_sup - old_sup, "totalSupply"
    elif old_m is not None and new_m is not None:
        delta, base = new_m - old_m, "totalMinted"
    else:
        delta, base = None, None
    if new_sup is None and new_m is None:
        out["degraded"].append({"name": name, "address": addr})
    if delta is not None and delta != 0:
        n_supply_change += 1
        out["supply_changes"].append({"name": name, "address": addr, "base": base,
                                       "old": old_sup if base == "totalSupply" else old_m,
                                       "new": new_sup if base == "totalSupply" else new_m,
                                       "delta": delta})
    # velocity
    last_read = parse_wib(entry.get("lastReadWib"))
    prev_rate = entry.get("currentRatePerMin")
    if delta is not None and delta > 0 and last_read is not None and prev_rate is not None:
        mins = max(1.0, (NOW - last_read).total_seconds() / 60.0)
        rate = delta / mins
        if prev_rate and prev_rate > 0:
            ratio = rate / prev_rate
            if ratio >= 1.5 and delta >= 20:
                out["velocity_passes"].append({"name": name, "address": addr, "delta": delta,
                                               "interval_min": round(mins, 1), "rate": round(rate, 3),
                                               "prev_rate": prev_rate, "ratio": round(ratio, 2)})
        elif prev_rate == 0 and delta >= 20:
            # no base rate: record but NOT a pass (1931 precedent: ETHBack)
            out.setdefault("no_base_rate", []).append({"name": name, "delta": delta,
                                                        "interval_min": round(mins, 1),
                                                        "rate": round(rate, 3)})
    # age sweep
    st = str(entry.get("status") or "")
    if not any(t in st for t in TERMINAL):
        fm = parse_wib(entry.get("firstMintWib"))
        if fm is not None:
            age_h = (NOW - fm).total_seconds() / 3600.0
            if age_h > 48:
                out["age_exclusion_candidates"].append(
                    {"name": name, "address": addr, "status": st,
                     "firstMintWib": entry.get("firstMintWib"), "age_h": round(age_h, 1),
                     "totalSupply_new": new_sup, "freePct": entry.get("freePct")})

# track_c changes
tc = snap.get("track_c", {})
for name, entry in tc.items():
    if not isinstance(entry, dict): continue
    d = tc_rr.get(name)
    if d is None: continue
    addr = entry.get("address") or entry.get("sale") or entry.get("token")
    old_fm = entry.get("freeMinted")
    new_fm = d.get("freeMinted")
    if old_fm is not None and new_fm is not None and old_fm != new_fm:
        out["track_c_changes"].append({"name": name, "address": addr,
                                        "freeMinted_old": old_fm, "freeMinted_new": new_fm})
    old_ts = entry.get("totalSupply")
    new_ts = d.get("totalSupply")
    if old_ts is not None and new_ts is not None and old_ts != new_ts:
        out["track_c_changes"].append({"name": name, "address": addr,
                                        "totalSupply_old": old_ts, "totalSupply_new": new_ts})

out["counts"] = {"contracts_in_snapshot": len(contracts),
                 "reread": len(reread), "track_c_reread": len(tc_rr),
                 "supply_changes": n_supply_change,
                 "degraded": len(out["degraded"]),
                 "velocity_passes": len(out["velocity_passes"]),
                 "age_exclusion_candidates": len(out["age_exclusion_candidates"])}
json.dump(out, open(f"{BASE}/run-2026-11-08-2031-analysis.json", "w"), indent=1)
print(json.dumps(out["counts"], indent=1))
print("VELOCITY PASSES:")
for v in out["velocity_passes"]: print(" ", v)
print("AGE EXCLUSION CANDIDATES:")
for a in out["age_exclusion_candidates"]: print(" ", a)
print("NO BASE RATE (>=20 minted, prev 0):")
for v in out.get("no_base_rate", []): print(" ", v)
print("SUPPLY CHANGES:", n_supply_change, "DEGRADED:", len(out["degraded"]))
