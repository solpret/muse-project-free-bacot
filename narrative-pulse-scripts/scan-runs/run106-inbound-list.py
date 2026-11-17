#!/usr/bin/env python3
"""Run 106 deployment extraction (read-only): read contract creations from the RAW
receipts partial file (to null + contractAddress present). The parsed receipts JSON
never carries contractAddress - reading it there is the run-101 parser mistake.
Also collects new rotation tokens (>=12 wallets) from run106-paid.json for the
inbound list. Writes run106-inbound-contracts.json = run105 list + deployments +
new rotation tokens (deduped, lowercased)."""
import json
from pathlib import Path

SR = Path("/home/hatch/workspace/narrative-pulse/scan-runs")
raw = json.load(open(SR / "run106-receipts-partial.json"))
deployments = []
for h, r in raw.items():
    if not isinstance(r, dict):
        continue
    if r.get("to") is None and r.get("contractAddress"):
        deployments.append(r["contractAddress"].lower())
deployments = sorted(set(deployments))
print(f"deployments from raw receipts: {len(deployments)}")
for d in deployments:
    print("  DEPLOY", d)

paid = json.load(open(SR / "run106-paid.json"))
new_rot = sorted(tok for tok, w in paid.items() if len(w) >= 12)
print(f"new rotation tokens (>=12 wallets): {len(new_rot)}")
for t in new_rot:
    print("  ROT", t, "wallets:", len(paid[t]))

base = json.load(open(SR / "run105-inbound-contracts.json"))
merged = []
seen = set()
for c in [x.lower() for x in base] + deployments + new_rot:
    if c not in seen:
        seen.add(c)
        merged.append(c)
json.dump(merged, open(SR / "run106-inbound-contracts.json", "w"), indent=1)
print(f"inbound list run106: {len(merged)} (base {len(base)} + {len(deployments)} deployments + {len(new_rot)} new rotations, deduped)")
json.dump({"deployments": deployments, "new_rotation_tokens": new_rot,
           "base": len(base), "total": len(merged)},
          open(SR / "run106-inbound-additions.json", "w"), indent=1)
