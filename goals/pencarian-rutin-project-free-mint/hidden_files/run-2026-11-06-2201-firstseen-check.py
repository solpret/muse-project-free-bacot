#!/usr/bin/env python3
"""Run 2201 scan-leg definitive first-seen check (case-insensitive).
Partial scan: only enriched contracts are in the JSON (44 of 157 window NFT
contracts; enrichment killed by the 780s timeout)."""
import json
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TS = "2026-11-06-2201"
scan = json.load(open(f"{BASE}/run-{TS}-scan.json"))
seen = json.load(open(f"{BASE}/onchain-scan-seen.json"))
snap = json.load(open(f"{BASE}/onchain-snapshot.json"))
seen_addr = set()
if isinstance(seen, dict):
    for k in ("contracts", "known_older_leads"):
        seen_addr |= {str(a).lower() for a in seen.get(k, {})}
    # also any other top-level dict of addresses
    for k, v in seen.items():
        if isinstance(v, dict):
            seen_addr |= {str(a).lower() for a in v.keys() if str(a).startswith("0x")}
snap_addr = set()
for name, v in snap.get("contracts", {}).items():
    if isinstance(v, dict):
        for k in ("address", "saleContract", "token"):
            if v.get(k):
                snap_addr.add(str(v[k]).lower())
for name, v in snap.get("track_c", {}).items():
    if isinstance(v, dict):
        for k in ("sale", "address", "token"):
            if v.get(k):
                snap_addr.add(str(v[k]).lower())
for name, v in snap.get("excluded", {}).items():
    if isinstance(v, dict):
        for k in ("address", "sale", "token"):
            if v.get(k):
                snap_addr.add(str(v[k]).lower())
first = [c for c in scan["contracts"]
         if c["address"].lower() not in seen_addr
         and c["address"].lower() not in snap_addr]
print("scan contracts (enriched only):", len(scan["contracts"]))
print("seen addrs (lowercased set):", len(seen_addr), "snapshot addrs:", len(snap_addr))
print("TRUE FIRST-SEEN (case-insensitive, definitive):", len(first))
for c in first:
    print(json.dumps(c, indent=1))
json.dump(first, open(f"{BASE}/run-{TS}-firstseen.json", "w"), indent=1)
print("firstseen.json written")
