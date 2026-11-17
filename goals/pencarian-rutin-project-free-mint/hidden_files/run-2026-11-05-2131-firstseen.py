#!/usr/bin/env python3
"""Compute first-seen contracts from the 2131 scan output.
first-seen = in scan output AND absent from BOTH onchain-scan-seen.json
(seen['contracts'] keys) AND snapshot contracts (by ADDRESS, not name keys)
AND the snapshot excluded list (addresses extracted from dict values).
Excludes the Agent ID registry (infrastructure).
Writes run-2026-11-05-2131-scan-firstseen.json
"""
import json

SCAN = "onchain-scan-2026-11-05-2131.json"
OUT = "run-2026-11-05-2131-scan-firstseen.json"
REGISTRY = "0x60b9262456de011f7d15a54cdd8c48baaa8b022f"

d = json.load(open(SCAN))
seen = json.load(open("onchain-scan-seen.json"))["contracts"]
seen_set = {k.lower() for k in seen}
snap = json.load(open("onchain-snapshot.json"))
snap_set = set()
for k, v in snap.get("contracts", {}).items():
    if isinstance(v, dict):
        for f in ("address", "sale", "token"):
            if v.get(f):
                snap_set.add(str(v[f]).lower())
# track_c sale/token addresses also count as snapshot-known
for k, v in snap.get("track_c", {}).items():
    if isinstance(v, dict):
        for f in ("sale", "token"):
            if v.get(f):
                snap_set.add(str(v[f]).lower())
excl_set = set()
ex = snap.get("excluded", {})
if isinstance(ex, dict):
    for k, v in ex.items():
        if isinstance(v, dict):
            for f in ("address", "sale", "token"):
                if v.get(f):
                    excl_set.add(str(v[f]).lower())
elif isinstance(ex, list):
    excl_set = {str(a).lower() for a in ex}

nft = d.get("contracts", [])
erc20 = d.get("erc20_mint_contracts_list", [])

def classify(items):
    first, already_seen, in_snapshot, excluded = [], [], [], []
    for c in items:
        a = c["address"].lower()
        if a == REGISTRY.lower() or a in excl_set:
            excluded.append(c)
        elif a in snap_set:
            in_snapshot.append(c)
        elif a in seen_set:
            already_seen.append(c)
        else:
            first.append(c)
    return first, already_seen, in_snapshot, excluded

nft_first, nft_seen, nft_snap, nft_excl = classify(nft)
e20_first, e20_seen, e20_snap, e20_excl = classify(erc20)

out = {
    "scan_from": d.get("from_block"),
    "scan_to": d.get("to_block"),
    "latest_block": d.get("latest_block"),
    "ankr_calls": d.get("ankr_calls"),
    "errors": d.get("errors"),
    "nft_total": len(nft),
    "nft_first_seen": nft_first,
    "nft_first_seen_count": len(nft_first),
    "nft_already_seen": len(nft_seen),
    "nft_in_snapshot": len(nft_snap),
    "nft_excluded": len(nft_excl),
    "erc20_total": len(erc20),
    "erc20_first_seen": e20_first,
    "erc20_first_seen_count": len(e20_first),
    "erc20_already_seen": len(e20_seen),
    "erc20_in_snapshot": len(e20_snap),
    "erc20_excluded": len(e20_excl),
}
with open(OUT, "w") as f:
    json.dump(out, f, indent=1)
print(f"NFT total {len(nft)}: first-seen {len(nft_first)}, already-seen {len(nft_seen)}, in-snapshot {len(nft_snap)}, excluded {len(nft_excl)}")
print(f"ERC20 total {len(erc20)}: first-seen {len(e20_first)}, already-seen {len(e20_seen)}, in-snapshot {len(e20_snap)}, excluded {len(e20_excl)}")
for c in nft_first:
    print("NFT FIRST:", c["address"], c.get("kind"), "mints:", c.get("mint_count"), "minters:", c.get("distinct_minters"), "first_block:", c.get("first_block"), "registry_bytes:", c.get("registry_bytes_hit"), "sourcify:", c.get("sourcify"), "name:", c.get("name"), "symbol:", c.get("symbol"))
for c in e20_first:
    print("ERC20 FIRST:", c["address"], "mints:", c.get("mint_count"), "minters:", c.get("distinct_minters"), "first_block:", c.get("first_block"))
