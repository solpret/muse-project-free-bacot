#!/usr/bin/env python3
"""Velocity analysis run 2026-11-06 18:01 vs run 17:31 (view-consistent).
Worker A leg 1. Interval from block delta x 0.45s/block.
New early leads (WeZards, AgentB-c047, AgentB-06ec): baseline = triage read
~15:06 WIB (snapshot lastReadWib), no previous rate -> velocity cannot pass.
Fallback: where the primary view is null this run but totalSupply read OK on
both runs, compute on totalSupply and mark view='totalSupply*'.
"""
import json

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TS = "2026-11-06-1901"
prev = json.load(open(f"{BASE}/run-2026-11-06-1831-reread-lean.json"))
now = json.load(open(f"{BASE}/run-{TS}-reread-lean.json"))
prev_vel = json.load(open(f"{BASE}/run-2026-11-06-1831-velocity.json"))

BLOCK_PREV = prev["block"] if prev.get("block") is not None else prev_vel.get("block_now")
BLOCK_NOW = now["block"]
if BLOCK_NOW is None:
    # leg-1 block() failed on all RPCs this run (degraded); fetch head fresh
    import urllib.request
    for _rpc in ["https://bsc-dataseed1.bnbchain.org", "https://bsc.publicnode.com"]:
        try:
            _b = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}).encode()
            _q = urllib.request.Request(_rpc, data=_b, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(_q, timeout=8) as _r:
                BLOCK_NOW = int(json.load(_r)["result"], 16)
            break
        except Exception:
            continue
if BLOCK_NOW is None:
    BLOCK_NOW = None
    print("BLOCK_NOW fallback = preflight head 131998436", flush=True)
INTERVAL_MIN = (BLOCK_NOW - BLOCK_PREV) * 0.45 / 60.0

# row[5] of the 1801 velocity file is run 1801's OWN rate (correct prev rate)
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
    ("BOBBIE", "totalMinted"), ("AgentPad Agent", "totalMinted"),
    ("Quantumfarm", "freeClaimed"), ("Soul Agent", "totalSupply"),
    ("Driftnauts", "freeMinted"), ("CATAI", "totalMinted"),
    ("Blox", "totalSupply"), ("Mindvolt", "totalSupply"),
    ("Hivefacai", "totalSupply"), ("Botphoenix", "totalSupply"),
    ("Kaiju-1831", "totalSupply"), ("Peepers-1831", "totalSupply"),
    ("Goblins-1831", "totalSupply"), ("Sprouts-1831", "totalSupply"),
    ("PropertyAgent-1831", "totalMinted"), ("MoonCat", "totalSupply"),
    ("Lion's Share", "totalSupply"), ("WHALE-A", "totalSupply"),
    ("WHALE-B", "totalSupply"), ("Muster", "totalMinted"),
]
# Baselines: all pairs now present in the 1801 reread file (WeZards/AgentB trio
# baselined in 1801; BOBBIE/AgentPad Agent baselined in 1801; QF/Soul baselined here).
rows = []
SNAP_BASE = {"Driftnauts": ("freeMinted", 811), "CATAI": ("totalMinted", 76), "Blox": ("totalSupply", 21), "Mindvolt": ("totalSupply", 676), "Hivefacai": ("totalSupply", 658), "Botphoenix": ("totalSupply", 600), "Kaiju-1831": ("totalSupply", 195), "Peepers-1831": ("totalSupply", 205), "Goblins-1831": ("totalSupply", 200), "Sprouts-1831": ("totalSupply", 93), "PropertyAgent-1831": ("totalMinted", 88), "MoonCat": ("totalSupply", 1029), "Lion's Share": ("totalSupply", 580), "WHALE-A": ("totalSupply", 4820), "WHALE-B": ("totalSupply", 1446), "Muster": ("totalMinted", 1)}
for name, view in PAIRS:
    p = prev["reread"].get(name, {})
    n = now["reread"].get(name, {})
    if name in SNAP_BASE and p.get(view) is None:
        p = dict(p); p[view] = SNAP_BASE[name][1]
    pv = p.get(view)
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
    "interval_method": f"ESTIMATE {BLOCK_NOW - BLOCK_PREV} blocks x 0.45s/block (head fetched fresh; leg-1 block() was None)",
    "block_prev": BLOCK_PREV,
    "block_now": BLOCK_NOW,
    "rows": rows,
    "free_pct_verified": free_pct,
    "track_c_changes": tc_changes,
    "notes": [
        "New 1901 pairs (Kaiju/Peepers/Goblins/Sprouts/PropertyAgent/MoonCat/Lion's Share/WHALE-A/B/Muster) baselined from run 1831 verify reads; prev_rate None -> velocity cannot pass this run.",
        "Null reads this run are UNVERIFIED, not zero; baselines retained from run 1801."
        "HIVE Agents: minted-by-user 2026-11-02, grandfathered - 48h age rule does not remove an already-minted item; kept, not flagged.",
        "StarAgent first mint est. 2026-11-04 ~21:26 WIB - crosses 48h ~21:26 WIB tonight if not sold out; Quantumfarm deadline 2026-11-06 21:00:37 WIB; Soul Agent deadline 2026-11-06 23:53:44 WIB; age-exclusion applies ONLY if deadline passes DURING this run.",
        "Quantumfarm 48h deadline 2026-11-06 21:00:37 WIB; Soul Agent deadline 2026-11-06 23:53:44 WIB.",
    ],
}
json.dump(out, open(f"{BASE}/run-{TS}-velocity.json", "w"), indent=1)
for r in rows:
    print(r)
print("FREE_PCT", json.dumps(free_pct))
print("TRACK_C_CHANGES", json.dumps(tc_changes, indent=1))
print("interval_min", round(INTERVAL_MIN, 2))
