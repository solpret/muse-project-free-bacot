#!/usr/bin/env python3
"""Run 2026-11-06 1531 WIB: compute first-seen NFT contracts from scan output.
First-seen = absent from BOTH onchain-scan-seen.json contracts (case-insensitive)
AND snapshot contracts (address keys) AND snapshot track_c. Registry address
itself excluded. READ-ONLY on shared state; writes only run-1531-firstseen.json."""
import json
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
scan = json.load(open(f"{BASE}/run-2026-11-06-1531-scan.json"))
seen = json.load(open(f"{BASE}/onchain-scan-seen.json"))
seen_addrs = {k.lower() for k in seen.get("contracts", {}).keys()}
snap = json.load(open(f"{BASE}/onchain-snapshot.json"))
snap_addrs = set()
for k in snap.get("contracts", {}).keys():
    if isinstance(k, str) and k.lower().startswith("0x"):
        snap_addrs.add(k.lower())
for k in snap.get("track_c", {}).keys():
    if isinstance(k, str) and k.lower().startswith("0x"):
        snap_addrs.add(k.lower())
# snapshot contracts may also be keyed by name with address inside values
for v in snap.get("contracts", {}).values():
    if isinstance(v, dict):
        a = v.get("address") or v.get("contract")
        if isinstance(a, str) and a.lower().startswith("0x"):
            snap_addrs.add(a.lower())
REG = "0x60b9262456de011f7d15a54cdd8c48baaa8b022f"
EXCLUDED = {
    "0x827e83e49bd7e15b67efa0e90fc25f17b8d96124",  # long-agent
    "0x8b47354e7b76b1970a0d06365c8244a810d37493",  # chuan huo ren
}
first = []
for c in scan["contracts"]:
    a = c["address"].lower()
    if a == REG.lower() or a in EXCLUDED:
        continue
    if a not in seen_addrs and a not in snap_addrs:
        first.append(c)
print(f"scan contracts={len(scan['contracts'])} seen_entries={len(seen_addrs)} "
      f"snapshot_addrs={len(snap_addrs)} first_seen={len(first)} partial={scan.get('partial')}")
for c in first:
    print(f"  FIRST {c['kind']} {c['address']} {c['name']} / {c['symbol']} "
          f"mints={c['mint_count']} minters={c['distinct_minters']} first_block={c['first_block']} "
          f"registry={c['registry_bytes_hit']} sourcify={c['sourcify']} free={c.get('free_shaped')}")
json.dump(first, open(f"{BASE}/run-2026-11-06-1531-firstseen.json", "w"), indent=1)
print("WROTE run-2026-11-06-1531-firstseen.json")
