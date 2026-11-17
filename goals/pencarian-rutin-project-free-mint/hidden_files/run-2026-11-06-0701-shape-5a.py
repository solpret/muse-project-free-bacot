#!/usr/bin/env python3
"""Leg 5a run 2026-11-06 0701 WIB: shape-check the 4 Sourcify feed contracts new
vs hot-leg-seen.json (verified 2026-11-05 23:57:43Z - 2026-11-06 00:02:58Z).
Read-only; writes ONLY run-2026-11-06-0701-sourcify-shape.json. Never touches
hot-leg-seen.json or any other shared state file."""
import json, sys
sys.path.insert(0, "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files")
from feed_shape_0001 import sourcify_abi, classify

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TS = "2026-11-06-0701"
NEW = ["0xacb8bc76d91DE219aA7C1a040F31322A0162a8A3",
       "0xcED8b1A3f93e2D467df848603950Cc3d6a83Dc71",
       "0x30Ffd5d0b2d3908A38fA31016F148E6b651587A2",
       "0x3E56BeF7d8A5C05df60208ccd9F9e444423D9D57"]
feed = json.load(open(f"{BASE}/run-{TS}-sourcify-feed.json"))
vat = {it["address"].lower(): it.get("verifiedAt") for it in feed["results"]}
out = []
for addr in NEW:
    status, abi = sourcify_abi(addr)
    r = {"address": addr, "verifiedAt": vat.get(addr.lower()), "sourcify": status}
    if abi is not None:
        r.update(classify(abi))
    else:
        r["S1"] = False
        r["S2"] = False
    out.append(r)
    print(addr, status, "S1=", r.get("S1"), "S2=", r.get("S2"),
          "mint=", r.get("mint_fns"), "quote=", r.get("quote_fns"),
          "free=", r.get("free_views"), "agent=", r.get("gate_fns"),
          "token=", r.get("token_fns"), flush=True)
json.dump(out, open(f"{BASE}/run-{TS}-sourcify-shape.json", "w"), indent=1)
print("wrote", f"run-{TS}-sourcify-shape.json", "n=", len(out))
