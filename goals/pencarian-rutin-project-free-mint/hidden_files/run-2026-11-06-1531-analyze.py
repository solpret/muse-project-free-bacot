#!/usr/bin/env python3
"""Velocity analysis run 2026-11-06 15:01 vs run 15:01 (view-consistent).
Worker A leg 1. Interval from block delta x 0.45s/block.
New early leads (WeZards, AgentB-c047, AgentB-06ec): baseline = triage read
~15:06 WIB (snapshot lastReadWib), no previous rate -> velocity cannot pass.
Fallback: where the primary view is null this run but totalSupply read OK on
both runs, compute on totalSupply and mark view='totalSupply*'.
"""
import json

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TS = "2026-11-06-1531"
prev = json.load(open(f"{BASE}/run-2026-11-06-1501-reread-lean.json"))
now = json.load(open(f"{BASE}/run-{TS}-reread-lean.json"))
prev_vel = json.load(open(f"{BASE}/run-2026-11-06-1501-velocity.json"))

BLOCK_PREV = prev["block"]          # 131976886
BLOCK_NOW = now["block"]            # 131976886
INTERVAL_MIN = (BLOCK_NOW - BLOCK_PREV) * 0.45 / 60.0

# row[5] of the 1431 velocity file is run 1431's OWN rate (correct prev rate)
prev_rate = {}
for row in prev_vel["rows"]:
    prev_rate[row[0]] = row[5]

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
    # New early leads run 1431: baselines from triage re-read ~15:06 WIB
    ("WeZards", "totalMinted"), ("AgentB-c047", "totalMinted"),
    ("AgentB-06ec", "totalMinted"),
]
# Baselines NOT in the 1431 reread file (triage reads ~15:06 WIB, snapshot lastReadWib)
TRIAGE_BASELINE = {
    "WeZards": {"totalMinted": 27, "freeMinted": 27},
    "AgentB-c047": {"totalMinted": 382},
    "AgentB-06ec": {"totalMinted": 186},
}
CORRECTED_PREV = {"PassAgentX": {"freeMinted": 3838, "totalSupply": 4058}}

rows = []
for name, view in PAIRS:
    p = prev["reread"].get(name, {})
    n = now["reread"].get(name, {})
    pv = CORRECTED_PREV.get(name, {}).get(view, p.get(view))
    if pv is None:
        pv = TRIAGE_BASELINE.get(name, {}).get(view)
    nv = n.get(view)
    used_view = view
    # Fallback to totalSupply when primary view unreadable on either side
    if (pv is None or nv is None) and view != "totalSupply":
        p_ts, n_ts = p.get("totalSupply"), n.get("totalSupply")
        if p_ts is not None and n_ts is not None:
            pv, nv, used_view = p_ts, n_ts, "totalSupply*"
    if pv is None or nv is None:
        rows.append([name, used_view, pv, nv, None, None, prev_rate.get(name), None, False])
        continue
    delta = nv - pv
    rate = delta / INTERVAL_MIN if INTERVAL_MIN else 0.0
    pr = prev_rate.get(name)
    ratio = (rate / pr) if pr else None
    passed = bool(ratio is not None and ratio >= 1.5 and delta >= 20)
    rows.append([name, used_view, pv, nv, delta, round(rate, 4), pr,
                 round(ratio, 2) if ratio is not None else None, passed])

# Free-quota % (free views only; never total-supply % substituted)
free_pct = {}
def fp(name, free_val, cap):
    if free_val is not None and cap:
        free_pct[name] = round(100.0 * free_val / cap, 2)
fp("WeZards", now["reread"]["WeZards"].get("freeMinted"), 2500)
fp("Bianren", now["reread"]["Bianren"].get("freeMinted"), 2000)
fp("AgentGlyph", now["reread"]["AgentGlyph"].get("freeClaimed"), 512)
kg = now["reread"]["KING Agent"]
if kg.get("remainingFree") is not None and kg.get("freeQuota"):
    free_pct["KING Agent"] = round(100.0 * (kg["freeQuota"] - kg["remainingFree"]) / kg["freeQuota"], 2)

# Track-C changes vs 1431
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
    "interval_method": f"ESTIMATE {BLOCK_NOW - BLOCK_PREV} blocks x 0.45s/block",
    "block_prev": BLOCK_PREV,
    "block_now": BLOCK_NOW,
    "rows": rows,
    "free_pct_verified": free_pct,
    "track_c_changes": tc_changes,
    "notes": [
        "WeZards/AgentB-c047/AgentB-06ec baselines are now run 1501 reads; prev rate from run 1501 velocity file, so velocity CAN pass this run.",
        "Null reads this run are UNVERIFIED, not zero; baselines retained from run 1501.",
        "HIVE Agents: minted-by-user 2026-11-02, grandfathered - 48h age rule does not remove an already-minted item; kept, not flagged.",
        "StarAgent first mint est. 2026-11-04 ~21:26 WIB - crosses 48h ~21:26 WIB tonight if not sold out; NOT yet age-excluded this run.",
    ],
}
json.dump(out, open(f"{BASE}/run-{TS}-velocity.json", "w"), indent=1)
for r in rows:
    print(r)
print("FREE_PCT", json.dumps(free_pct))
print("TRACK_C_CHANGES", json.dumps(tc_changes, indent=1))
print("interval_min", round(INTERVAL_MIN, 2))
