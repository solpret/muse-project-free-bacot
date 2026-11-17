#!/usr/bin/env python3
"""Run 1531: first-seen computation from scan output (read-only wrt snapshot/seen).
Writes run-2026-11-05-1531-scan-firstseen.json (does NOT touch seen/snapshot files;
appending to seen + state update is a separate step after this)."""
import json

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
REGISTRY = "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F"

scan = json.load(open(f"{BASE}/onchain-scan-2026-11-05-1531.json"))
seen = json.load(open(f"{BASE}/onchain-scan-seen.json"))
seen_addrs = {k.lower() for k in seen.get("contracts", {}).keys()}
snap = json.load(open(f"{BASE}/onchain-snapshot.json"))
snap_addrs = set()
for name, e in snap.get("contracts", {}).items():
    if isinstance(e, dict) and e.get("address"):
        snap_addrs.add(str(e["address"]).lower())
# track_c entries may also carry addresses
for name, e in snap.get("track_c", {}).items():
    if isinstance(e, dict):
        for f in ("address", "sale", "token", "contract"):
            if e.get(f) and isinstance(e[f], str) and e[f].startswith("0x"):
                snap_addrs.add(e[f].lower())

first_seen = []
for c in scan.get("contracts", []):
    addr = c["address"].lower()
    if addr == REGISTRY.lower():
        continue
    if addr in seen_addrs or addr in snap_addrs:
        continue
    agent_shaped = bool(
        c.get("registry_bytes_hit")
        or (c.get("sourcify") == "verified" and c.get("free_shaped"))
        or (c.get("free_shaped") and c.get("mint_funcs"))
    )
    # stricter: agent-shaped requires registry/AgentGate/free-mint evidence.
    # registry_bytes_hit alone is weak (factory template common) but counts as
    # shape evidence per body; free_shaped without registry/sourcify is NOT enough.
    agent_shaped = bool(
        c.get("registry_bytes_hit")
        or (c.get("sourcify") == "verified" and c.get("free_shaped"))
    )
    first_seen.append({
        "address": c["address"],
        "kind": c["kind"],
        "mint_count": c["mint_count"],
        "distinct_minters": c["distinct_minters"],
        "minters_sample": c.get("minters_sample", []),
        "first_block": c["first_block"],
        "last_block": c["last_block"],
        "registry_bytes_hit": c.get("registry_bytes_hit"),
        "sourcify": c.get("sourcify"),
        "free_shaped": c.get("free_shaped", []),
        "mint_funcs": c.get("mint_funcs", []),
        "name": c.get("name"),
        "symbol": c.get("symbol"),
        "agent_shaped": agent_shaped,
        "shape_evidence": {
            "registry_bytes_hit": c.get("registry_bytes_hit"),
            "sourcify": c.get("sourcify"),
            "free_shaped": c.get("free_shaped", []),
            "mint_funcs": c.get("mint_funcs", []),
        },
    })

out = {
    "run": "1531",
    "window": [scan["from_block"], scan["to_block"]],
    "window_blocks": scan["to_block"] - scan["from_block"] + 1,
    "scan_latest_block": scan["latest_block"],
    "ankr_calls": scan.get("ankr_calls"),
    "errors": scan.get("errors", []),
    "nft_contracts_in_window": len(scan.get("contracts", [])),
    "erc20_mint_contracts_in_window": scan.get("erc20_mint_contracts"),
    "first_seen": first_seen,
    "first_seen_agent_shaped": [f["address"] for f in first_seen if f["agent_shaped"]],
    "first_seen_not_agent_shaped": [f["address"] for f in first_seen if not f["agent_shaped"]],
}
json.dump(out, open(f"{BASE}/run-2026-11-05-1531-scan-firstseen.json", "w"), indent=1)
print(f"first-seen total: {len(first_seen)}; agent-shaped: {len(out['first_seen_agent_shaped'])}")
for f in first_seen:
    print(f"  {'AGENT' if f['agent_shaped'] else '     '} {f['kind']} {f['address']} {f['name']} ({f['symbol']}) mints={f['mint_count']} minters={f['distinct_minters']} registry={f['registry_bytes_hit']} sourcify={f['sourcify']} free={f['free_shaped']}")
