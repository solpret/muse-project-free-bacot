#!/usr/bin/env python3
"""Run 1601: first-seen computation from scan output (read-only wrt snapshot/seen).
Writes run-2026-11-05-1601-scan-firstseen.json (does NOT touch seen/snapshot files).
STRICT agent-shape (task rule, lesson from run 1531): a contract is agent-shaped
ONLY if (a) registry bytes verified via eth_getCode (scan registry_bytes_hit)
AND (b) free-mint fn / free-supply constant / free views that actually RESPOND
on-chain. registry-bytes alone or ABI-name free-shape alone is NOT agent-shaped.
This script flags 'strict_pending_probe' for registry-hit contracts so the
verify step can probe (b) on-chain; final verdict lives in the verify output.
"""
import json

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
REGISTRY = "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F"

scan = json.load(open(f"{BASE}/onchain-scan-2026-11-05-1601.json"))
seen = json.load(open(f"{BASE}/onchain-scan-seen.json"))
seen_addrs = {k.lower() for k in seen.get("contracts", {}).keys()}
snap = json.load(open(f"{BASE}/onchain-snapshot.json"))
snap_addrs = set()
for name, e in snap.get("contracts", {}).items():
    if isinstance(e, dict) and e.get("address"):
        snap_addrs.add(str(e["address"]).lower())
for name, e in snap.get("track_c", {}).items():
    if isinstance(e, dict):
        for f in ("address", "sale", "token", "contract"):
            if e.get(f) and isinstance(e[f], str) and e[f].startswith("0x"):
                snap_addrs.add(e[f].lower())
for name, e in snap.get("excluded", {}).items():
    if isinstance(e, dict):
        for f in ("address", "sale", "token", "contract"):
            if e.get(f) and isinstance(e[f], str) and e[f].startswith("0x"):
                snap_addrs.add(e[f].lower())
# pending_claims entries may carry mint/token addresses
for name, e in snap.get("pending_claims", {}).items():
    if isinstance(e, dict):
        for f in ("address", "mint", "token", "contract"):
            if e.get(f) and isinstance(e[f], str) and e[f].startswith("0x"):
                snap_addrs.add(e[f].lower())

first_seen = []
for c in scan.get("contracts", []):
    addr = c["address"].lower()
    if addr == REGISTRY.lower():
        continue
    if addr in seen_addrs or addr in snap_addrs:
        continue
    reg = bool(c.get("registry_bytes_hit"))
    free_abi = list(c.get("free_shaped", []) or [])
    # strict: needs BOTH (a) registry bytes AND (b) free views responding on-chain.
    # ABI free-shape is only a probe trigger, not proof of (b).
    strict_pending = bool(reg and free_abi)
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
        "free_shaped": free_abi,
        "mint_funcs": c.get("mint_funcs", []),
        "name": c.get("name"),
        "symbol": c.get("symbol"),
        "strict_pending_probe": strict_pending,
        "shape_evidence": {
            "registry_bytes_hit": c.get("registry_bytes_hit"),
            "sourcify": c.get("sourcify"),
            "free_shaped": free_abi,
            "mint_funcs": c.get("mint_funcs", []),
        },
    })

out = {
    "run": "1601",
    "window": [scan["from_block"], scan["to_block"]],
    "window_blocks": scan["to_block"] - scan["from_block"] + 1,
    "scan_latest_block": scan["latest_block"],
    "ankr_calls": scan.get("ankr_calls"),
    "errors": scan.get("errors", []),
    "nft_contracts_in_window": len(scan.get("contracts", [])),
    "erc20_mint_contracts_in_window": scan.get("erc20_mint_contracts"),
    "first_seen": first_seen,
    "first_seen_strict_pending_probe": [f["address"] for f in first_seen if f["strict_pending_probe"]],
    "first_seen_registry_hit": [f["address"] for f in first_seen if f.get("registry_bytes_hit")],
}
json.dump(out, open(f"{BASE}/run-2026-11-05-1601-scan-firstseen.json", "w"), indent=1)
print(f"first-seen total: {len(first_seen)}; registry-hit: {len(out['first_seen_registry_hit'])}; strict-pending-probe: {len(out['first_seen_strict_pending_probe'])}")
for f in first_seen:
    print(f"  {'PROBE' if f['strict_pending_probe'] else '     '} {f['kind']} {f['address']} {f['name']} ({f['symbol']}) mints={f['mint_count']} minters={f['distinct_minters']} registry={f['registry_bytes_hit']} sourcify={f['sourcify']} free={f['free_shaped']} mintfuncs={f['mint_funcs']}")
