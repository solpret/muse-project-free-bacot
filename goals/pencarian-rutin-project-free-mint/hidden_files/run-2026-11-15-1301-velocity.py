#!/usr/bin/env python3
"""Velocity for free-mint-search run 2026-11-15 13:01 WIB.
Delta reread-ke-reread (1231 -> 1301), interval 30.0 mnt dari started_wib.
prev_rate = snapshot contracts[name].currentRatePerMin (rate interval sebelumnya).
Pass: delta >= 20 DAN rate >= 1.5x prev_rate. Read-only; writes run-2026-11-15-1301-velocity.json."""
import json

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
INTERVAL = 30.0

def metric(views):
    if views.get("totalSupply") is not None:
        return views["totalSupply"], "totalSupply"
    if views.get("totalMinted") is not None:
        return views["totalMinted"], "totalMinted"
    return None, None

r1 = json.load(open(BASE + "run-2026-11-15-1301-reread.json"))
r0 = json.load(open(BASE + "run-2026-11-15-1231-reread.json"))
snap = json.load(open(BASE + "onchain-snapshot.json"))
contracts = snap.get("contracts", {})

vel = {}
for name, item in sorted(r1["reads"].items()):
    now, src = metric(item["views"])
    prev_item = r0["reads"].get(name)
    if prev_item is None:
        vel[name] = {"error": "not in 1231 reread"}
        continue
    prev, _ = metric(prev_item["views"])
    if now is None or prev is None:
        vel[name] = {"prev": prev, "now": now, "velocity": None,
                     "note": "supply None, nilai lama dipertahankan"}
        continue
    delta = now - prev
    rate = round(delta / INTERVAL, 4)
    prev_rate = contracts.get(name, {}).get("currentRatePerMin")
    if prev_rate is None:
        prev_rate = 0.0
    ratio = round(rate / prev_rate, 2) if prev_rate and prev_rate > 0 else None
    passes = delta >= 20 and ratio is not None and ratio >= 1.5
    vel[name] = {"prev": prev, "now": now, "delta": delta, "source": src,
                 "rate_per_min": rate, "prev_rate": prev_rate,
                 "ratio": ratio, "velocity_pass": passes}

out = {"run": "free-mint-search 2026-11-15 13:01 WIB",
       "block": r1.get("block"), "interval_min": INTERVAL,
       "velocity": vel,
       "velocity_pass_list": [k for k, v in vel.items() if v.get("velocity_pass")]}
json.dump(out, open(BASE + "run-2026-11-15-1301-velocity.json", "w"), indent=1)
print("velocity_pass:", out["velocity_pass_list"])
for k, v in vel.items():
    if v.get("delta", 0) >= 5 or v.get("velocity_pass"):
        print(k, v)
print("done, interval", INTERVAL)
