#!/usr/bin/env python3
"""Run 2131 scan-leg definitive first-seen check (case-insensitive) + firstseen note."""
import json
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
scan = json.load(open(f"{BASE}/run-2026-11-06-2131-scan.json"))
seen = json.load(open(f"{BASE}/onchain-scan-seen.json"))
snap = json.load(open(f"{BASE}/onchain-snapshot.json"))
seen_addr = {str(k).lower() for k in seen.get("contracts", {})} | \
            {str(k).lower() for k in seen.get("known_older_leads", {})}
snap_addr = set()
for name, v in snap.get("contracts", {}).items():
    if isinstance(v, dict):
        for k in ("address", "saleContract", "token"):
            if v.get(k):
                snap_addr.add(str(v[k]).lower())
first = [c for c in scan["contracts"]
         if c["address"].lower() not in seen_addr
         and c["address"].lower() not in snap_addr]
print("scan contracts:", len(scan["contracts"]))
print("seen addrs (lowercased set):", len(seen_addr), "snapshot addrs:", len(snap_addr))
print("TRUE FIRST-SEEN (case-insensitive, definitive):", len(first))
for c in first:
    print(c)
note = [{
    "address": "0x7fe03C055588bd5018825175D791103c5CBEd8be",
    "name": "BNBFLY Agent Pass",
    "note": ("NOT true first-seen for this leg: backfill 132024438-132027026 already "
             "found + triaged it (backfill-triage-132024438-132027026.json, verdict "
             "not-agent-shaped/no-free-path) and merged it into onchain-scan-seen.json "
             "at 14:55:27 UTC with first-seen block 132024991 (key stored "
             "checksummed-case, not lowercase -- naive lowercase-key lookup misses it). "
             "Definitive case-insensitive check: 0 true first-seen in this scan window."),
}]
json.dump(note, open(f"{BASE}/run-2026-11-06-2131-firstseen.json", "w"), indent=1)
print("firstseen.json written")
