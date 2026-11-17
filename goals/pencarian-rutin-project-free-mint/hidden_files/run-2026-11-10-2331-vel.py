#!/usr/bin/env python3
"""Velocity run 2331: reread vs snapshot-prev, interval nominal 30.0 (same as run 1901)."""
import json
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TS = "2026-11-10-2331"
INTERVAL = 30.0
snap = json.load(open(f"{BASE}/onchain-snapshot.json"))
rr = json.load(open(f"{BASE}/run-{TS}-reread.json"))
BLOCK = rr.get("block")
rows = {}
passes = []
for name, entry in snap.get("contracts", {}).items():
    if not isinstance(entry, dict):
        continue
    f = rr.get("reread", {}).get(name)
    if not f:
        continue
    view, prev, new = None, None, None
    if entry.get("totalSupply") is not None and f.get("totalSupply") is not None:
        view, prev, new = "totalSupply", entry["totalSupply"], f["totalSupply"]
    elif entry.get("totalMinted") is not None and f.get("totalMinted") is not None:
        view, prev, new = "totalMinted", entry["totalMinted"], f["totalMinted"]
    elif f.get("totalSupply") is not None:
        view, prev, new = "totalSupply", None, f["totalSupply"]
    elif f.get("totalMinted") is not None:
        view, prev, new = "totalMinted", None, f["totalMinted"]
    if prev is None or new is None:
        rows[name] = {"view": view, "prev": prev, "new": new, "minted": None,
                      "rate": None, "prev_rate": entry.get("currentRatePerMin"),
                      "ratio": None, "passes": False}
        continue
    minted = new - prev
    rate = minted / INTERVAL
    prev_rate = entry.get("currentRatePerMin")
    ratio = (rate / prev_rate) if prev_rate else None
    ok = bool(prev_rate is not None and ratio is not None and ratio >= 1.5 and minted >= 20)
    rows[name] = {"view": view, "prev": prev, "new": new, "minted": minted,
                  "rate": round(rate, 3), "prev_rate": prev_rate,
                  "ratio": round(ratio, 2) if ratio is not None else None, "passes": ok}
    if ok:
        passes.append((name, minted, ratio))
out = {"interval_min": INTERVAL, "block": BLOCK, "passes": passes, "rows": rows}
json.dump(out, open(f"{BASE}/run-{TS}-vel.json", "w"), indent=1)
print(f"VEL DONE block={BLOCK} rows={len(rows)} passes={passes}")
# top movers
top = sorted(((k, v) for k, v in rows.items() if v.get("minted") is not None),
             key=lambda kv: -kv[1]["minted"])[:15]
for k, v in top:
    print(f"  {k}: {v['prev']}->{v['new']} (+{v['minted']}, {v['rate']}/mnt, ratio={v['ratio']}, passes={v['passes']})")
