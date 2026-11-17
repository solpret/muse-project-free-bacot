#!/usr/bin/env python3
"""First-seen triage for run 2026-11-07 08:01 WIB — mirrors run 0101 structure.
Read-only on inputs (scan output, seen file, snapshot); writes only
run-2026-11-07-0931-firstseen.json and run-2026-11-07-0931-firstseen-verify.json.
Never writes seen/snapshot/state files.
True first-seen = absent from seen file AND snapshot AND excluded list AND
not the registry itself. Agent-shape test uses the scan enrichment fields
(registry_bytes_hit, sourcify, free_shaped, mint_funcs); a true first-seen
with registry hit or free-mint evidence gets a deeper Sourcify ABI check.
"""
import json, time, urllib.request, urllib.error

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
REGISTRY = "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F"
TS = "2026-11-07-0931"

scan = json.load(open(f"{BASE}/onchain-scan-2026-11-07-0931.json"))
seen = json.load(open(f"{BASE}/onchain-scan-seen.json"))
seen_contracts = seen.get("contracts", {})
snap = json.load(open(f"{BASE}/onchain-snapshot.json"))
snap_addrs = {v.get("address", "").lower() for v in snap.get("contracts", {}).values() if isinstance(v, dict) and v.get("address")}
snap_addrs |= {v.get("address", "").lower() for v in snap.get("track_c", {}).values() if isinstance(v, dict) and v.get("address")}
excluded = snap.get("excluded", {})
excl_addrs = set()
if isinstance(excluded, dict):
    excl_addrs = {k.lower() for k in excluded.keys()}
elif isinstance(excluded, list):
    excl_addrs = {str(a).lower() for a in excluded}

def fetch_abi(addr):
    url = f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "free-bacot-firstseen/1.0"})
        with urllib.request.urlopen(req, timeout=20) as r:
            return json.loads(r.read().decode()), None
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return {"__not_verified__": True}, None
        return None, f"HTTPError {e.code}"
    except Exception as e:
        return None, f"{type(e).__name__}: {e}"

triage = []
first_seen = []
for c in scan.get("contracts", []):
    addr = c["address"]
    low = addr.lower()
    row = {"address": addr, "mint_count": c["mint_count"],
           "distinct_minters": c["distinct_minters"],
           "first_block": c["first_block"], "last_block": c["last_block"],
           "name": c.get("name"), "symbol": c.get("symbol"),
           "registry_bytes_hit": c.get("registry_bytes_hit"),
           "sourcify": c.get("sourcify"), "free_shaped": c.get("free_shaped", []),
           "mint_funcs": c.get("mint_funcs", []), "enriched": True}
    if low == REGISTRY.lower():
        row["status"] = "registry-itself"
    elif low in excl_addrs:
        row["status"] = "excluded-list"
    elif low in snap_addrs:
        row["status"] = "known-snapshot"
    elif low in {k.lower() for k in seen_contracts.keys()}:
        row["status"] = "known-seen"
    else:
        row["status"] = "FIRST-SEEN"
        first_seen.append(row)
    triage.append(row)

# Deep verify any true first-seen: Sourcify ABI for AgentGate/free-mint evidence
verify = {"run": TS, "window": [scan.get("from_block"), scan.get("to_block")],
          "early_lead_candidates": [], "verdict": "",
          "agent_shaped_refound_registry_hit": [],
          "notable_refound": [],
          "method": "Agent-shape test = Sourcify verified ABI or bytecode registry reference / AgentGate / free-mint function / free-supply constant + first mints verified on-chain in this run. Sourcify-unverified with no free-mint/AgentGate evidence = NOT an early lead (log only)."}
for row in first_seen:
    addr = row["address"]
    data, err = fetch_abi(addr)
    abi = None
    if isinstance(data, dict):
        abi = data.get("abi")
        if abi is None and isinstance(data.get("stdJson"), dict):
            abi = data["stdJson"].get("abi")
    detail = {"address": addr, "mint_count": row["mint_count"],
              "distinct_minters": row["distinct_minters"],
              "first_block": row["first_block"], "name": row["name"],
              "symbol": row["symbol"], "registry_bytes_hit": row["registry_bytes_hit"],
              "sourcify_scan": row["sourcify"], "free_shaped": row["free_shaped"],
              "mint_funcs": row["mint_funcs"]}
    if data is not None and data.get("__not_verified__"):
        detail["sourcify_deep"] = "not_verified"
        detail["agent_shaped"] = bool(row["registry_bytes_hit"])
    elif abi is not None:
        fns = [e for e in abi if isinstance(e, dict) and e.get("type") == "function"]
        names = [f.get("name", "") for f in fns]
        raw = json.dumps(abi).lower()
        detail["sourcify_deep"] = "verified"
        detail["abi_functions"] = names
        detail["has_registry_ref"] = ("60b9262456de011f7d15a54cdd8c48baaa8b022f" in raw
                                      or "agentregistry" in [n.lower() for n in names]
                                      or "agentgate" in [n.lower() for n in names])
        detail["free_funcs"] = [n for n in names if "free" in n.lower() and not n.lower().startswith("freeze")]
        detail["agent_shaped"] = bool(detail["has_registry_ref"] or detail["free_funcs"] or row["registry_bytes_hit"])
    else:
        detail["sourcify_deep"] = f"transport-failed: {err}"
        detail["agent_shaped"] = bool(row["registry_bytes_hit"])
    row["deep_verify"] = detail
    if detail.get("agent_shaped"):
        verify["early_lead_candidates"].append(detail)

for row in triage:
    if row["status"] in ("known-seen", "known-snapshot") and row.get("registry_bytes_hit"):
        verify["agent_shaped_refound_registry_hit"].append(
            {"address": row["address"], "name": row["name"], "symbol": row["symbol"],
             "mint_count": row["mint_count"], "distinct_minters": row["distinct_minters"],
             "sourcify": row["sourcify"], "status": row["status"]})
    if row["mint_count"] >= 100 and row["status"] != "FIRST-SEEN":
        verify["notable_refound"].append(
            {"address": row["address"], "name": row["name"], "mint_count": row["mint_count"],
             "distinct_minters": row["distinct_minters"], "registry_bytes_hit": row["registry_bytes_hit"],
             "sourcify": row["sourcify"], "status": row["status"]})

counts = {}
for r in triage:
    counts[r["status"]] = counts.get(r["status"], 0) + 1
if verify["early_lead_candidates"]:
    verify["verdict"] = (f"{len(verify['early_lead_candidates'])} EARLY lead candidate(s): agent-shaped + first mints verified on-chain in window "
                         f"{scan.get('from_block')}-{scan.get('to_block')}.")
else:
    verify["verdict"] = (f"0 EARLY leads: {len(first_seen)} true first-seen in window, "
                         f"none agent-shaped (or none at all). All registry-hit contracts in window were already seen in earlier runs and are recorded as re-finds only, never re-reported as early.")

out = {"from_block": scan.get("from_block"), "to_block": scan.get("to_block"), "run": TS,
       "scan_status": "complete" if not scan.get("partial") else "partial",
       "first_seen": [r["address"] for r in first_seen],
       "first_seen_count": len(first_seen),
       "new_seen_total": 0, "seen_total": len(seen_contracts),
       "window_contracts": len(scan.get("contracts", [])),
       "enriched": len(scan.get("contracts", [])),
       "unenriched_recovered": 0,
       "triage": triage,
       "status_counts": counts,
       "note": (f"{len(first_seen)} true first-seen in window {scan.get('from_block')}-{scan.get('to_block')}: "
                f"{counts}. Nothing appended to onchain-scan-seen.json. "
                f"{'No EARLY-LEAD candidate this run.' if not verify['early_lead_candidates'] else str(len(verify['early_lead_candidates'])) + ' EARLY candidate(s) — see verify file.'}")}
json.dump(out, open(f"{BASE}/run-{TS}-firstseen.json", "w"), indent=1)
json.dump(verify, open(f"{BASE}/run-{TS}-firstseen-verify.json", "w"), indent=1)
print(f"FIRSTSEEN window {scan.get('from_block')}-{scan.get('to_block')} contracts={len(triage)} counts={counts} first_seen={len(first_seen)} early={len(verify['early_lead_candidates'])}")
for r in first_seen:
    print(" FIRST-SEEN", r["address"], r["name"], "mints", r["mint_count"], "registry", r["registry_bytes_hit"], "sourcify", r["sourcify"])
for r in verify["agent_shaped_refound_registry_hit"]:
    print(" REFIND-REGISTRY", r["address"], r["name"], "mints", r["mint_count"], "sourcify", r["sourcify"], r["status"])
