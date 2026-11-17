#!/usr/bin/env python3
"""Velocity analysis run 2031 vs run 2001 (read-only; no snapshot edit).
Interval from block timestamps: 133551667 (20:28:02 WIB) -> 133553157 (20:39:12 WIB) = 670s = 11.17 min.
Both runs executed late vs cron schedule; block-ts interval is the honest read-to-read gap."""
import json
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
INTERVAL_MIN = 670 / 60
r2001 = json.load(open(BASE + "run-2026-11-14-2001-reread.json"))["reads"]
r2031 = json.load(open(BASE + "run-2026-11-14-2031-reread.json"))["reads"]
snap = json.load(open(BASE + "onchain-snapshot.json"))["contracts"]

SUPPLY_KEYS = ["totalSupply", "totalMinted", "totalSpecimens", "totalRemnants"]

def supply(views):
    if not views: return None, None
    for k in SUPPLY_KEYS:
        if views.get(k) is not None: return k, views[k]
    return None, None

def free_pct(views):
    """(pct, basis) or (None, reason)"""
    if not views: return None, "no views"
    fc = views.get("freeClaimed"); fm = views.get("freeMinted")
    for cap_key in ("FREE_SUPPLY", "FREE_MAX", "FREE_CAP", "FREE_POOL", "FREE_SHARES"):
        cap = views.get(cap_key)
        if cap:
            n = fc if fc is not None else fm
            if n is not None: return round(100 * n / cap, 1), f"{n}/{cap} {cap_key}"
    return None, "no free cap view"

rows = []
for name, r31 in r2031.items():
    v31 = r31.get("views"); v01 = r2001.get(name, {}).get("views")
    sk31, cur = supply(v31); sk01, prev = supply(v01)
    minted = (cur - prev) if (cur is not None and prev is not None and sk31 == sk01) else None
    rate = round(minted / INTERVAL_MIN, 3) if minted is not None else None
    s = snap.get(name, {})
    prev_rate = s.get("currentRatePerMin", s.get("previousRatePerMin"))
    ratio = round(rate / prev_rate, 2) if (rate is not None and prev_rate) else None
    vel_pass = bool(ratio is not None and ratio >= 1.5 and minted is not None and minted >= 20)
    fpct, fbasis = free_pct(v31)
    # slot changes
    slot = []
    for k in ("mintedBy_user", "freeUsed_user", "freeClaimed_user", "balanceOf_user", "mintedByWallet_user", "freeMintedPerWallet_user", "freeBooked_user", "hasFreeClaimed_user"):
        a = v01.get(k) if v01 else None; b = v31.get(k) if v31 else None
        if a is not None and b is not None and a != b: slot.append(f"{k}: {a}->{b}")
    rows.append({"name": name, "supply_key": sk31, "prev": prev, "cur": cur,
                 "minted": minted, "rate": rate, "prev_rate": prev_rate,
                 "ratio": ratio, "vel_pass": vel_pass, "free_pct": fpct,
                 "free_basis": fbasis, "slot_change": slot,
                 "views_none_2031": [k for k, x in (v31 or {}).items() if x is None]})
json.dump({"interval_min": round(INTERVAL_MIN, 2), "block_2001": 133551667,
           "block_2031": 133553157, "rows": rows},
          open(BASE + "run-2026-11-14-2031-velocity.json", "w"), indent=1)
print(f"{'name':<18} {'prev':>6} {'cur':>6} {'mint':>5} {'rate':>6} {'prevRate':>8} {'ratio':>6} {'free%':>6}  vel  slot")
for r in rows:
    print(f"{r['name']:<18} {str(r['prev']):>6} {str(r['cur']):>6} {str(r['minted']):>5} {str(r['rate']):>6} {str(r['prev_rate']):>8} {str(r['ratio']):>6} {str(r['free_pct']):>6}  {'PASS' if r['vel_pass'] else 'fail'}  {';'.join(r['slot_change'])}")
print("\nVELOCITY PASS:", [r["name"] for r in rows if r["vel_pass"]] or "NONE")
print("free% >=70:", [(r["name"], r["free_pct"], r["free_basis"]) for r in rows if r["free_pct"] is not None and r["free_pct"] >= 70])
print("free% >=50:", [(r["name"], r["free_pct"], r["free_basis"]) for r in rows if r["free_pct"] is not None and r["free_pct"] >= 50])
print("free pool 0 (sellout check):", [(r["name"], r["free_basis"]) for r in rows if r["free_pct"] == 100.0])
