#!/usr/bin/env python3
"""Analysis run 1231: velocity (baseline=currentRatePerMin), sellout, slot, age, track_c. Read-only."""
import json
from datetime import datetime, timezone
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
snap = json.load(open(f"{BASE}/onchain-snapshot.json"))
r = json.load(open(f"{BASE}/run-2026-11-08-1331-reread.json"))
blk = r["block"]; prev_blk = 132340101
interval_min = (blk - prev_blk) * 0.45 / 60.0
print(f"interval blocks {blk-prev_blk} = {interval_min:.1f} min")
NONPROMO = ("minted-by-user", "discarded", "sold-out", "age-excluded", "excluded")
vel_pass, vel_watch, sellout_new, slot_changed, movers = [], [], [], [], []
free_new_reads = []
rpc_none = 0
for name, d in r.get("reread", {}).items():
    s = snap.get("contracts", {}).get(name)
    if not s:
        continue
    ts = d.get("totalSupply"); prev = s.get("totalSupply")
    if ts is None:
        rpc_none += 1
        continue
    if prev is None:
        continue
    minted = ts - prev
    if minted != 0:
        movers.append({"name": name, "prev": prev, "new": ts, "minted": minted,
                       "status": s.get("status")})
    base = s.get("currentRatePerMin")
    rate = minted / interval_min if interval_min > 0 else 0
    if base is None:
        base = s.get("previousRatePerMin") or 0
    ratio = (rate / base) if base and base > 0 else None
    if ratio is not None and ratio >= 1.5 and minted >= 20:
        vel_pass.append({"name": name, "address": s.get("address"), "status": s.get("status"),
                         "minted": minted, "rate": round(rate, 4), "baseline_rate": base,
                         "ratio": round(ratio, 2),
                         "freePct_snap": s.get("freePctVerified"),
                         "freeClaimed_new": d.get("freeClaimed"),
                         "FREE_SUPPLY_new": d.get("FREE_SUPPLY")})
    elif base == 0 and minted >= 20:
        vel_watch.append({"name": name, "address": s.get("address"), "status": s.get("status"),
                          "minted": minted, "rate": round(rate, 4), "baseline_rate": 0})
    # sellout: fresh freeClaimed >= FREE_SUPPLY, or totalSupply >= MAX_SUPPLY
    ms = d.get("MAX_SUPPLY") or s.get("MAX_SUPPLY")
    fs = d.get("FREE_SUPPLY") or s.get("FREE_SUPPLY")
    fc = d.get("freeClaimed")
    sold = False; why = ""
    if fs and fc is not None and fc >= fs:
        sold = True; why = f"freeClaimed {fc} >= FREE_SUPPLY {fs}"
    if ms and ts >= ms:
        sold = True; why += f" totalSupply {ts} >= MAX_SUPPLY {ms}"
    if sold and "sold-out" not in str(s.get("status")):
        # verify not already sold out in snapshot by same measure
        prev_fc = s.get("freeClaimed"); prev_fs = s.get("FREE_SUPPLY")
        already = bool(prev_fs and prev_fc is not None and prev_fc >= prev_fs)
        already = already or bool(s.get("MAX_SUPPLY") and prev is not None and prev >= s["MAX_SUPPLY"])
        if not already:
            sellout_new.append({"name": name, "address": s.get("address"),
                                "status": s.get("status"), "totalSupply": ts,
                                "MAX_SUPPLY": ms, "freeClaimed": fc,
                                "FREE_SUPPLY": fs, "why": why.strip()})
    # slot: balanceOf user
    bal = d.get("balanceOf_user")
    old = s.get("balanceOf_user")
    if old is None:
        old = s.get("userBalance")
    if bal is not None and old is not None and bal != old:
        slot_changed.append({"name": name, "address": s.get("address"), "status": s.get("status"),
                             "balance_old": old, "balance_new": bal})
    # free views newly readable (snapshot had None, now int)
    if d.get("freeClaimed") is not None and s.get("freeClaimed") is None:
        free_new_reads.append({"name": name, "freeClaimed": d.get("freeClaimed"),
                               "FREE_SUPPLY": d.get("FREE_SUPPLY"),
                               "freePct": round(d["freeClaimed"] / d["FREE_SUPPLY"] * 100, 2)
                               if d.get("FREE_SUPPLY") else None})

promotable = [v for v in vel_pass if not any(k in str(v["status"]) for k in NONPROMO)]
print(f"velocity pass: {len(vel_pass)} promotable: {len(promotable)} watch-from-zero: {len(vel_watch)}")
for v in vel_pass: print("  VEL", v)
for v in vel_watch: print("  VEL-WATCH", v)
print(f"sellout new: {len(sellout_new)}")
for x in sellout_new: print("  SOLD", x)
print(f"slot changed: {len(slot_changed)}")
for x in slot_changed: print("  SLOT", x)
print(f"movers: {len(movers)} rpc_none_totalSupply: {rpc_none}")
print(f"free views newly readable: {len(free_new_reads)}")

# --- age sweep: verified launch time > 48h and not sold out ---
now = datetime(2026, 11, 8, 13, 31, tzinfo=timezone.utc).astimezone()
# WIB = UTC+7; use naive WIB datetimes
from datetime import datetime as dt
now_wib = dt(2026, 11, 8, 13, 31)
age_excluded, age_checked = [], 0
for name, s in snap.get("contracts", {}).items():
    st = str(s.get("status") or "")
    if any(k in st for k in ("sold-out", "age-excluded", "minted-by-user", "excluded")):
        continue
    launch = None; src = None
    if s.get("startTimeWib"):
        try:
            launch = dt.fromisoformat(str(s["startTimeWib"]).replace("Z", ""))
            src = "startTimeWib"
        except Exception:
            pass
    if launch is None:
        continue
    age_checked += 1
    age_h = (now_wib - launch).total_seconds() / 3600
    d = r.get("reread", {}).get(name, {})
    if age_h > 48:
        age_excluded.append({"name": name, "address": s.get("address"), "status": st,
                             "launch_wib": str(s.get("startTimeWib")), "source": src,
                             "age_hours": round(age_h, 1),
                             "totalSupply_now": d.get("totalSupply"),
                             "totalSupply_snap": s.get("totalSupply"),
                             "freeClaimed_now": d.get("freeClaimed"),
                             "FREE_SUPPLY": d.get("FREE_SUPPLY") or s.get("FREE_SUPPLY")})
print(f"age: verified-launch active checked: {age_checked}, >48h: {len(age_excluded)}")
for x in age_excluded: print("  AGE", x)

# --- track_c changes ---
tc_changes = []
for name, d in r.get("track_c", {}).items():
    s = snap.get("track_c", {}).get(name)
    if not s or not isinstance(s, dict):
        continue
    ch = {}
    for newk, oldks in [("totalSupply", ["totalSupply", "totalMinted", "sharesMinted"]),
                        ("freeMinted", ["freeMinted", "freeClaimed_total"]),
                        ("freeSharesRemaining", ["freeSharesRemaining", "freeCardsRemaining"])]:
        nv = d.get(newk)
        ov = None
        for ok in oldks:
            if s.get(ok) is not None:
                ov = s.get(ok); break
        if nv is not None and ov is not None and nv != ov:
            ch[newk] = {"old": ov, "new": nv}
    if ch:
        tc_changes.append({"name": name, "status": s.get("status"), "changes": ch,
                           "sale": s.get("sale"), "token": s.get("token")})
print(f"track_c changes: {len(tc_changes)}")
for x in tc_changes: print("  TC", x)

out = {"run": "2026-11-08-1331", "block": blk, "prev_block": prev_blk,
       "interval_min": round(interval_min, 1),
       "contracts_read": len(r.get("reread", {})),
       "track_c_read": len(r.get("track_c", {})),
       "rpc_none_totalSupply": rpc_none,
       "velocity_pass": vel_pass, "promotable": promotable,
       "velocity_watch_from_zero_baseline": vel_watch,
       "sellout_new": sellout_new, "slot_changed": slot_changed,
       "movers": movers, "free_new_reads": free_new_reads,
       "age_checked_verified_launch": age_checked,
       "age_excluded": age_excluded,
       "track_c_changes": tc_changes}
json.dump(out, open(f"{BASE}/run-2026-11-08-1331-analysis.json", "w"), indent=1)
print("wrote run-2026-11-08-1331-analysis.json")
