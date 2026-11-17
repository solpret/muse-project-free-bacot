#!/usr/bin/env python3
"""Velocity analysis run 2026-11-06 14:31 vs run 1401 (view-consistent)."""
import json

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TS = "2026-11-06-1431"
prev = json.load(open(f"{BASE}/run-2026-11-06-1401-reread-lean.json"))
now = json.load(open(f"{BASE}/run-{TS}-reread-lean.json"))
prev_vel = json.load(open(f"{BASE}/run-2026-11-06-1401-velocity.json"))

BLOCK_PREV = prev["block"]          # 131965602
BLOCK_NOW = now["block"]            # 131969896
INTERVAL_MIN = (BLOCK_NOW - BLOCK_PREV) * 0.45 / 60.0   # 4294 blocks -> 32.21 min

# prev rate per name from the 1401 velocity file: rows [name, view, prev, now, delta, rate, prev_rate, ratio, pass]
# row[5] is run 1401's OWN rate (the correct previous rate for this run);
# row[6] is the rate from the run before 1401 (must NOT be reused here).
prev_rate = {}
for row in prev_vel["rows"]:
    prev_rate[row[0]] = row[5]

# (name, view) view-consistent pairs; PassAgentX baseline corrected to the
# 1401 direct re-check (totalSupply 4058 / freeMinted 3838, not the stale 3836).
PAIRS = [
    ("SEAT-f11e", "totalMinted"), ("StarAgent-7d39", "totalSupply"),
    ("KING Agent", "totalMinted"), ("Thronemind", "freeMinted"),
    ("Hashseers", "freeMinted"), ("Smeltbots", "freeMinted"),
    ("Forklings", "freeMinted"), ("PassAgentX", "freeMinted"),
    ("Agent Frogs", "freeClaimed"), ("Mossminds", "freeMinted"),
    ("HIVE Agents", "totalMinted"), ("MILLION", "totalMinted"),
    ("FOD Agent", "totalMinted"), ("Bianren", "totalMinted"),
    ("Crack", "totalMinted"), ("CantonTron", "totalMinted"),
    ("Layerloom", "freeMinted"), ("Tumblebots", "freeMinted"),
    ("Jolly", "freeMinted"), ("LuckyBox-d08e", "totalSupply"),
    ("SnailMail", "totalSupply"), ("Mummyhive", "freeClaimed"),
    ("wheelz", "totalSupply"), ("WAGagent", "totalSupply"),
    ("Neurolucha", "totalSupply"), ("BNB CACHE Server", "totalSupply"),
    ("AgentGlyph", "totalSupply"), ("Pacture", "freeMinted"),
]
# Corrected 1401 baselines (direct re-check values, not stale reads)
CORRECTED_PREV = {"PassAgentX": {"freeMinted": 3838, "totalSupply": 4058}}

rows = []
for name, view in PAIRS:
    p = prev["reread"].get(name, {})
    n = now["reread"].get(name, {})
    pv = CORRECTED_PREV.get(name, {}).get(view, p.get(view))
    nv = n.get(view)
    if pv is None or nv is None:
        rows.append([name, view, pv, nv, None, None, prev_rate.get(name), None, False])
        continue
    delta = nv - pv
    rate = delta / INTERVAL_MIN if INTERVAL_MIN else 0.0
    pr = prev_rate.get(name)
    ratio = (rate / pr) if pr else None
    passed = bool(ratio is not None and ratio >= 1.5 and delta >= 20)
    rows.append([name, view, pv, nv, delta, round(rate, 4), pr,
                 round(ratio, 2) if ratio is not None else None, passed])

# Track-C changes vs 1401
tc_changes = {}
for name in now["track_c"]:
    p = prev["track_c"].get(name, {})
    n = now["track_c"][name]
    diff = {}
    for k in n:
        if k == "address":
            continue
        if p.get(k) != n.get(k):
            diff[k] = [p.get(k), n.get(k)]
    tc_changes[name] = diff

out = {
    "interval_min": round(INTERVAL_MIN, 2),
    "interval_method": f"ESTIMATE {BLOCK_NOW - BLOCK_PREV} blocks x 0.45s/block (block timestamps unreadable, RPC 403/disconnect)",
    "block_prev": BLOCK_PREV,
    "block_now": BLOCK_NOW,
    "block_ts_prev_wib": None,
    "block_ts_now_wib": None,
    "rows": rows,
    "track_c_changes": tc_changes,
    "interval_note": "CORRECTED 1401 baseline for PassAgentX: freeMinted 3838 / totalSupply 4058 (direct re-check ~14:15 WIB), not the stale 3836 read",
}
json.dump(out, open(f"{BASE}/run-{TS}-velocity.json", "w"), indent=1)
for r in rows:
    print(r)
print("TRACK_C_CHANGES", json.dumps(tc_changes, indent=1))
print("interval_min", round(INTERVAL_MIN, 2))
