#!/usr/bin/env python3
"""Run 2026-11-06 0601 WIB: shape-check the 1 Sourcify feed contract new vs hot-leg-seen.
Reuses classify() logic from feed_shape_0001.py. Read-only; updates hot-leg-seen.json
only for the checked address (same format as the hot leg)."""
import json, sys, time, urllib.request, urllib.error
sys.path.insert(0, "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files")
from feed_shape_0001 import sourcify_abi, classify

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
ADDR = "0x7d137985f1d993dfeb5a2ac22e2df8e47154edbf"
feed = json.load(open(f"{BASE}/run-2026-11-06-0601-sourcify-feed.json"))
vat = next((it.get("verifiedAt") for it in feed["results"] if it["address"].lower() == ADDR.lower()), None)
status, abi = sourcify_abi(ADDR)
r = {"address": ADDR, "verifiedAt": vat, "sourcify": status}
if abi is not None:
    r.update(classify(abi))
else:
    r["S1"] = False; r["S2"] = False
print(json.dumps(r, indent=1))
json.dump([r], open(f"{BASE}/run-2026-11-06-0601-sourcify-shape.json", "w"), indent=1)
hl = json.load(open(f"{BASE}/hot-leg-seen.json"))
hl[ADDR] = {"first_seen_wib": "2026-11-06T06:05:14+07:00",
            "note": f"S1={r.get('S1')} S2={r.get('S2')} mint={r.get('mint_fns')} quote={r.get('quote_fns')} free={r.get('free_views')} agent={r.get('gate_fns')} token={r.get('token_fns')} err=",
            "source": "sourcify-feed",
            "status": "checked-not-sale-shape" if not (r.get("S1") or r.get("S2")) else "SALE-SHAPE-PASS-NEEDS-VERIFY"}
json.dump(hl, open(f"{BASE}/hot-leg-seen.json", "w"), indent=1)
print("hot-leg-seen total now:", len(hl))
