#!/usr/bin/env python3
"""Scan triage run 1501: first-seen NFT from PARTIAL scan output (enrichment
stalled at 92/160, SCAN_EXIT=124). Read-only except appending newly seen
addresses to onchain-scan-seen.json. Writes run-2026-11-07-1501-triage-scan.json."""
import json
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
scan = json.load(open(f"{BASE}/onchain-scan-2026-11-07-1501.json"))
seen = json.load(open(f"{BASE}/onchain-scan-seen.json"))
snap = json.load(open(f"{BASE}/onchain-snapshot.json"))
seen_keys = {k.lower() for k in seen.get("contracts", {}).keys()}
snap_addrs = {v.get("address", "").lower() for v in snap.get("contracts", {}).values() if isinstance(v, dict)}
excl_addrs = set()
for v in snap.get("excluded", {}).values():
    if isinstance(v, dict) and v.get("address"):
        excl_addrs.add(v["address"].lower())
# stuck address from progress log (enrichment started, never finished)
STUCK = "0x099096C6028FcF7Db9AA3ca7FE23AE3fA70b5F58"
rows = scan.get("contracts", [])
print(f"scan window {scan.get('from_block')}-{scan.get('to_block')} partial={scan.get('partial')} enriched={len(rows)} erc20={scan.get('erc20_mint_contracts')} errors={scan.get('errors')}", flush=True)
first_seen = []
for c in rows:
    a = c["address"].lower()
    if a not in seen_keys and a not in snap_addrs and a not in excl_addrs:
        agent = bool(c.get("registry_bytes_hit")) or (c.get("sourcify") == "verified" and bool(c.get("mint_funcs") or c.get("free_shaped")))
        first_seen.append({**c, "agent_shaped": agent})
print(f"first-seen (enriched): {len(first_seen)}", flush=True)
for c in first_seen:
    print(f"  FIRST {c['address']} {c.get('name')} / {c.get('symbol')} mints={c.get('mint_count')} minters={c.get('distinct_minters')} first_block={c.get('first_block')} registry={c.get('registry_bytes_hit')} sourcify={c.get('sourcify')} free_shaped={c.get('free_shaped')} mint_funcs={c.get('mint_funcs')} agent_shaped={c.get('agent_shaped')}", flush=True)
# stuck address: seen-only, no enrichment data -> cannot judge shape
stuck_known = STUCK.lower() in seen_keys or STUCK.lower() in snap_addrs or STUCK.lower() in excl_addrs
print(f"stuck address {STUCK} already-known={stuck_known} (no enrichment data; seen-only, no shape verdict)", flush=True)
# append newly seen to seen file
added = 0
for c in first_seen:
    seen["contracts"][c["address"].lower()] = c.get("first_block")
    added += 1
if not stuck_known:
    seen["contracts"][STUCK.lower()] = 132169528  # last_block of scan window approx; first_block unknown
    added += 1
seen.setdefault("_meta", {})["last_updated_wib"] = "2026-11-07 run 1501"
seen["_meta"]["note_1501"] = (f"Run 1501: scan partial (chunks 20/20, enrichment 92/160, SCAN_EXIT=124); "
    f"{len(first_seen)} first-seen enriched appended + 1 stuck-address appended; 69 window NFT contracts "
    f"never enriched (addresses not recoverable from partial output) - pending backfill re-triage of window 132168529-132169528.")
json.dump(seen, open(f"{BASE}/onchain-scan-seen.json", "w"), indent=1)
out = {"window_from": scan.get("from_block"), "window_to": scan.get("to_block"), "partial": scan.get("partial"),
       "enriched": len(rows), "erc20_mint_contracts": scan.get("erc20_mint_contracts"),
       "ankr_calls": scan.get("ankr_calls"), "errors": scan.get("errors"),
       "first_seen": first_seen, "stuck_address": {"address": STUCK, "already_known": stuck_known},
       "seen_added": added, "unenriched_window_contracts": 69}
json.dump(out, open(f"{BASE}/run-2026-11-07-1501-triage-scan.json", "w"), indent=1)
print(f"TRIAGE DONE first_seen={len(first_seen)} agent_shaped={[c['address'] for c in first_seen if c.get('agent_shaped')]} seen_added={added}", flush=True)
