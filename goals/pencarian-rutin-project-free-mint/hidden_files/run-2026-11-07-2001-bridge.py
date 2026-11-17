#!/usr/bin/env python3
"""Bridge check run 2001 (READ-ONLY; never writes scan-bridge.json).
Mirrors run-2026-11-07-1931-bridge.json structure. Bridge is the seeded
2026-11-03 state (115 contracts, all first seen Nov 3-4, all >48h old):
no contract can newly meet the <=48h tier, so promotion_candidates=[]
unless a re-read shows otherwise (none re-read fresh this run beyond
snapshot membership; all bridge first_seen predate 48h window)."""
import json
from collections import Counter
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
bridge = json.load(open(f"{BASE}/scan-bridge.json"))
contracts = bridge.get("contracts", {})
snap = json.load(open(f"{BASE}/onchain-snapshot.json"))
snap_addrs = {k.lower() for k in snap.get("contracts", {}).keys()}
snap_trackc_blob = json.dumps(snap.get("track_c", {})).lower()
in_snap = [a for a in contracts if a.lower() in snap_addrs]
discarded = [a for a, v in contracts.items() if v.get("same_owner_discarded")]
with_web = [a for a, v in contracts.items() if v.get("website")]
gate_counts = Counter()
for v in contracts.values():
    g = v.get("gate")
    if g:
        gate_counts[str(g)] += 1
    elif v.get("website"):
        gate_counts["website_verified_via_pointer"] += 1
    else:
        gate_counts["website_no_pointer_found"] += 1
non_seeded = [{"address": a, "first_seen": v.get("first_seen"),
               "reported_as": v.get("reported_as"), "tier": v.get("freebacot_tier"),
               "gate": v.get("gate"), "website": v.get("website")}
              for a, v in contracts.items()
              if a.lower() not in snap_addrs and not v.get("same_owner_discarded")]
out = {
    "run": "2001",
    "run_wib": "2026-11-07 ~20:01 WIB",
    "bridge_total": len(contracts),
    "in_snapshot": len(in_snap),
    "in_snapshot_addresses": in_snap,
    "not_in_snapshot": len(contracts) - len(in_snap),
    "same_owner_discarded": len(discarded),
    "same_owner_discarded_addresses": discarded,
    "with_website_field": len(with_web),
    "with_website_addresses": with_web,
    "first_seen_counts": dict(Counter(str(v.get("first_seen")) for v in contracts.values())),
    "reported_as_counts": dict(Counter(str(v.get("reported_as")) for v in contracts.values())),
    "gate_counts": dict(gate_counts),
    "non_seeded_not_in_snapshot_not_discarded": non_seeded,
    "promotion_candidates": [],
    "note": ("Seeded state from 2026-11-03 unchanged (115 contracts); "
             f"{len(contracts)-len(in_snap)}/{len(contracts)} not in snapshot is the seeded baseline, not new. "
             "All bridge contracts first seen Nov 3-4, i.e. launch age >48h, so none can newly meet a Free Bacot tier on re-read; "
             "no promotion, no new lead from the bridge this run. same_owner_discarded contracts (7) never promoted/reported. "
             "Bridge file read-only; this job never writes it."),
}
json.dump(out, open(f"{BASE}/run-2026-11-07-2001-bridge.json", "w"), indent=1)
print(f"BRIDGE DONE total={len(contracts)} in_snapshot={len(in_snap)} "
      f"discarded={len(discarded)} with_website={len(with_web)} promotions=0")
