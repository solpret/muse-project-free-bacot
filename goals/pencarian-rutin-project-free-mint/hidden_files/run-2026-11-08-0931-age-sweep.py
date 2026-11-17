#!/usr/bin/env python3
"""Age sweep run 0931: parse verified first-mint times from snapshot contracts,
flag those >48h old at sweep time (recorded in output), not sold out (fresh reread),
not grandfathered (minted-by-user), not same-owner-discarded.
Read-only; writes run-2026-11-08-0931-age-sweep.json."""
import json, re
from datetime import datetime, timezone, timedelta
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
WIB = timezone(timedelta(hours=7))
NOW = datetime.now(WIB)  # sweep time actually used
snap = json.load(open(f"{BASE}/onchain-snapshot.json"))
re_ = json.load(open(f"{BASE}/run-2026-11-08-0931-reread.json"))
vel = json.load(open(f"{BASE}/run-2026-11-08-0931-velocity.json"))
vel_rows = {r["name"]: r for r in vel["rows"]}

PATTERNS = [
    # "first Transfer-from-zero at block 131079654, 2026-11-01 23:18 WIB"
    re.compile(r"first Transfer-from-zero at block \d+, (\d{4}-\d{2}-\d{2} \d{2}:\d{2}(?::\d{2})?) WIB"),
    re.compile(r"first mint .*?(\d{4}-\d{2}-\d{2} \d{2}:\d{2}(?::\d{2})?) WIB"),
    re.compile(r"(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\+07:00)"),
]

def parse_time(s):
    if not s:
        return None
    for pat in PATTERNS:
        m = pat.search(s)
        if m:
            t = m.group(1)
            for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%dT%H:%M:%S%z"):
                try:
                    dt = datetime.strptime(t, fmt)
                    if dt.tzinfo is None:
                        dt = dt.replace(tzinfo=WIB)
                    return dt
                except Exception:
                    continue
    return None

def first_mint_time(c):
    for field in ("firstMintWib", "firstMintTime", "launchTimeWib"):
        dt = parse_time(str(c.get(field, "") or ""))
        if dt:
            return dt, field
    dt = parse_time(c.get("launchNote", "") or "")
    if dt:
        return dt, "launchNote"
    return None, None

KEEP_STATUSES = ("minted-by-user", "promotion-discarded-same-owner",
                 "watchlist-only-same-owner-discarded", "sold-out")
out = {"now_wib": NOW.isoformat(), "candidates": [], "kept": [], "unverified": 0}
for name, c in snap["contracts"].items():
    dt, src = first_mint_time(c)
    if dt is None:
        out["unverified"] += 1
        continue
    age_h = (NOW - dt).total_seconds() / 3600.0
    vrow = vel_rows.get(name, {})
    cur = vrow.get("curSupply")
    maxs = vrow.get("maxSupply")
    sold_out = bool(vrow.get("soldOut")) if "soldOut" in vrow else None
    status = c.get("status", "")
    row = {"name": name, "address": c.get("address"), "firstMintWib": dt.isoformat(),
           "source": src, "ageHours": round(age_h, 1), "status": status,
           "curSupply": cur, "maxSupply": maxs, "soldOut": sold_out}
    if age_h <= 48:
        continue
    if sold_out:
        row["decision"] = "keep-sold-out"
        out["kept"].append(row)
        continue
    if any(k in status for k in KEEP_STATUSES):
        row["decision"] = "keep-" + ("minted-by-user" if "minted-by-user" in status else "same-owner-discarded")
        out["kept"].append(row)
        continue
    row["decision"] = "REMOVE"
    out["candidates"].append(row)

json.dump(out, open(f"{BASE}/run-2026-11-08-0931-age-sweep.json", "w"), indent=1)
print(f"AGE-SWEEP remove={len(out['candidates'])} kept={len(out['kept'])} unverified-launch={out['unverified']}")
for r in out["candidates"]:
    print(" REMOVE", r["name"], r["firstMintWib"], f"{r['ageHours']}h", r["curSupply"], "/", r["maxSupply"], r["status"])
for r in out["kept"][:8]:
    print(" KEEP", r["name"], r["decision"], f"{r['ageHours']}h")
