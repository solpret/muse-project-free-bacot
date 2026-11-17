#!/usr/bin/env python3
"""Leg 1 shape-check run 2026-11-06 0714 WIB: 5 Sourcify feed contracts new
vs hot-leg-seen.json (verified 2026-11-06 00:06:19Z - 00:11:29Z).
Read-only; writes ONLY run-2026-11-06-0714-sourcify-shape.json."""
import json, sys
sys.path.insert(0, "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files")
from feed_shape_0001 import sourcify_abi, classify

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TS = "2026-11-06-0714"
NEW = ["0x6E2edc2040Ad7e1eA71a714d8Ad6009172839f7a",
       "0x1e221B48f016899A76D2783621Df0512cF078A0f",
       "0xD0e2d313F6E0982154A3CCB18cF470F8Fb930db6",
       "0xE4dC6321008aE6Ed9695f3876780932C4a61585B",
       "0x26Eb899cb65b8cd5A885C358abA9332F36fd84f8"]
feed = json.load(open(f"{BASE}/run-{TS}-sourcify-feed.json"))
vat = {it["address"].lower(): it.get("verifiedAt") for it in feed["results"]}
out = []
for addr in NEW:
    status, abi = sourcify_abi(addr)
    r = {"address": addr, "verifiedAt": vat.get(addr.lower()), "sourcify": status}
    if abi is not None:
        r.update(classify(abi))
    else:
        r["S1"] = False; r["S2"] = False
    out.append(r)
    print(addr, status, "S1=", r.get("S1"), "S2=", r.get("S2"),
          "mint=", r.get("mint_fns"), "quote=", r.get("quote_fns"),
          "free=", r.get("free_views"), "agent=", r.get("gate_fns"),
          "token=", r.get("token_fns"), flush=True)
json.dump(out, open(f"{BASE}/run-{TS}-sourcify-shape.json", "w"), indent=1)
print("wrote", f"run-{TS}-sourcify-shape.json", "n=", len(out))
