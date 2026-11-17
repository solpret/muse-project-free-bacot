#!/usr/bin/env python3
"""Finalize PARTIAL scan run 0731: append newly-seen ERC20 contracts from the
COMPLETE chunk phase to seen (addresses fully listed); do NOT touch the 119
unenriched ERC721 (addresses lost); do NOT advance watermark (scan failed).
Patch sourcify in_scan flags for the 2 first-seen (Dafeiyu, HokiKoi)."""
import json
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
scan = json.load(open(f"{BASE}/onchain-scan-2026-11-08-0731.json"))
assert scan["partial"] is True
seen = json.load(open(f"{BASE}/onchain-scan-seen.json"))
seen_l = {k.lower() for k in seen["contracts"]}
snap = json.load(open(f"{BASE}/onchain-snapshot.json"))
snap_addrs = set()
for v in snap.get("contracts", {}).values():
    if isinstance(v, dict) and v.get("address"):
        snap_addrs.add(v["address"].lower())
window = f"{scan['from_block']}-{scan['to_block']}"
added = []
for e in scan.get("erc20_mint_contracts_list", []):
    a = e["address"]
    if a.lower() in seen_l or a.lower() in snap_addrs:
        continue
    seen["contracts"][a] = {"first_seen_block": e["first_block"], "last_block": e["last_block"],
                            "window": window, "run": "2026-11-08-0731", "kind": "ERC20",
                            "name": None, "symbol": None,
                            "mint_count": e["mint_count"], "distinct_minters": e["distinct_minters"]}
    seen_l.add(a.lower())
    added.append(a)
json.dump(seen, open(f"{BASE}/onchain-scan-seen.json", "w"), indent=1)
print(f"ERC20 appended to seen: {len(added)}; seen total now {len(seen['contracts'])}")
# patch sourcify in_scan flags for the two first-seen (were in scan contracts)
sj = json.load(open(f"{BASE}/run-2026-11-08-0731-sourcify.json"))
scan_addrs = {c["address"].lower() for c in scan.get("contracts", [])}
n = 0
for r in sj["results"]:
    if r["address"].lower() in scan_addrs and not r.get("in_scan_window"):
        r["in_scan_window"] = True
        n += 1
sj["cross_check_note"] = ("contracts found by both feed and scan legs are reported ONCE; "
                          "run 0731 scan was PARTIAL (enrichment stall) - in_scan_window reflects the "
                          "46 enriched contracts only; 119 ERC721 in-window were not enriched.")
json.dump(sj, open(f"{BASE}/run-2026-11-08-0731-sourcify.json", "w"), indent=1)
print(f"sourcify in_scan patched: {n}")
json.dump({"erc20_appended": len(added), "sourcify_patched": n, "seen_total": len(seen["contracts"])},
          open(f"{BASE}/run-2026-11-08-0731-finalize-partial.json", "w"), indent=1)
