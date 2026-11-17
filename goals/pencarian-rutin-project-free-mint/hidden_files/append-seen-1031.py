#!/usr/bin/env python3
"""Append newly seen contracts from partial scan run 2026-11-07-1031 to
onchain-scan-seen.json. A contract counts as newly seen ONLY if absent from
BOTH the seen file and onchain-snapshot.json. Scan was partial (log phase
complete, enrichment died at 125/193) — only contracts present in the partial
output JSON can be recorded; the 68 unenriched NFT contracts are NOT
identified and are NOT appended (backfill will cover the window since the
watermark was not advanced)."""
import json

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
sc = json.load(open(f"{BASE}/onchain-scan-2026-11-07-1031.json"))
seen = json.load(open(f"{BASE}/onchain-scan-seen.json"))
seen_contracts = seen["contracts"]
snap = json.load(open(f"{BASE}/onchain-snapshot.json"))
snap_l = {k.lower() for k in snap.get("contracts", {})}
window = f"{sc['from_block']}-{sc['to_block']}"
run = "2026-11-07-1031"

added = []
# ERC-20 mint contracts from the (complete) log phase
for e in sc.get("erc20_mint_contracts_list", []):
    a = e["address"]
    if a.lower() in {k.lower() for k in seen_contracts} or a.lower() in snap_l:
        continue
    seen_contracts[a] = {
        "first_seen_block": e["first_block"], "last_block": e["last_block"],
        "window": window, "run": run, "kind": "ERC20",
        "name": None, "symbol": None,
        "mint_count": e["mint_count"], "distinct_minters": e["distinct_minters"],
    }
    added.append(a)
# Enriched NFT contracts (0 new among the 125, verified separately)
for c in sc.get("contracts", []):
    a = c["address"]
    if a.lower() in {k.lower() for k in seen_contracts} or a.lower() in snap_l:
        continue
    seen_contracts[a] = {
        "first_seen_block": c["first_block"], "last_block": c["last_block"],
        "window": window, "run": run, "kind": c["kind"],
        "name": c.get("name"), "symbol": c.get("symbol"),
        "mint_count": c["mint_count"], "distinct_minters": c["distinct_minters"],
    }
    added.append(a)

json.dump(seen, open(f"{BASE}/onchain-scan-seen.json", "w"), indent=1)
print(f"appended {len(added)} newly seen contracts; seen file now "
      f"{len(seen_contracts)} entries")
print("sample:", added[:5])
