#!/usr/bin/env python3
"""Run 2026-11-06 0931 WIB: triage route-4 scan output onchain-scan-2026-11-06-0931.json
(window 131926748-131927747, cap 1000 blocks, amendment 2026-11-06 ~07:49).
FIXES vs 0801 triage: first-seen check uses NESTED seen['contracts'] (lowercase)
- the top-level-keys bug that inflated 0801 raw first-seen to 98 is NOT repeated;
new first-seen are appended to seen['contracts'], never top-level.
- first-mint verification uses Ankr module directly (dataseed eth_getLogs failed 14/14 in 0801).
- 5c: top-20 ERC20 mint_count>=10, skip already-checked, S1/S2 test.
- advances main-scan watermark to scan to_block; records skipped gap for backfill.
Read-only otherwise (writes: triage JSON, track-c-scan-checked.json, seen file, scan state)."""
import json, sys, time, urllib.request
sys.path.insert(0, "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files")
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from feed_shape_0001 import sourcify_abi, classify
from ankr import ankr_post

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TS = "2026-11-06-0931"
scan = json.load(open(f"{BASE}/onchain-scan-2026-11-06-0931.json"))
seen = json.load(open(f"{BASE}/onchain-scan-seen.json"))
snap = json.load(open(f"{BASE}/onchain-snapshot.json"))
snap_addrs = set()
for v in snap.get("contracts", {}).values():
    if isinstance(v, dict) and v.get("address"):
        snap_addrs.add(v["address"].lower())
for v in snap.get("track_c", {}).values():
    if isinstance(v, dict) and v.get("address"):
        snap_addrs.add(v["address"].lower())
# FIXED: nested contracts dict (lowercase keys), not top-level keys
seen_contracts = {k.lower(): v for k, v in seen.get("contracts", {}).items()}
out = {"window": [scan.get("from_block"), scan.get("to_block")],
       "ankr_calls": scan.get("ankr_calls"), "errors": scan.get("errors"),
       "nft_contracts": len(scan.get("contracts", [])),
       "erc20_mint_contracts": scan.get("erc20_mint_contracts"),
       "nft_first_seen": [], "erc20_5c": []}

# --- 1. NFT first-seen shape check ---
first_seen = [c for c in scan.get("contracts", [])
              if c["address"].lower() not in seen_contracts and c["address"].lower() not in snap_addrs]
print(f"NFT contracts in window: {len(scan.get('contracts', []))}; first-seen (nested seen + snapshot): {len(first_seen)}", flush=True)
for c in first_seen:
    addr = c["address"]
    status, abi = sourcify_abi(addr)
    r = {"address": addr, "name": c.get("name"), "symbol": c.get("symbol"),
         "kind": c.get("kind"), "mint_count": c.get("mint_count"),
         "distinct_minters": c.get("distinct_minters"),
         "first_block": c.get("first_block"), "last_block": c.get("last_block"),
         "registry_bytes_hit": c.get("registry_bytes_hit"),
         "scan_sourcify": c.get("sourcify"), "sourcify": status}
    if abi is not None:
        r.update(classify(abi))
        funcs = [it.get("name", "") for it in abi if isinstance(it, dict) and it.get("type") == "function"]
        r["gate_fns_corrected"] = [f for f in funcs if "agent_registry" in f.lower() or "agentregistry" in f.lower() or "agentgate" in f.lower() or "agent_gate" in f.lower() or "agent_id" in f.lower()]
        r["agent_shaped"] = bool(r.get("gate_fns_corrected")) or bool(r.get("gate_fns")) or (bool(r.get("mint_fns")) and bool(r.get("free_views")))
    else:
        r.update({"functions": 0, "mint_fns": [], "quote_fns": [], "free_views": [],
                  "gate_fns": [], "token_fns": [], "S1": False, "S2": False,
                  "gate_fns_corrected": [], "agent_shaped": False})
    out["nft_first_seen"].append(r)
    print("NFT", addr, c.get("name"), status, "agent_shaped=", r["agent_shaped"],
          "mint=", r.get("mint_fns"), "quote=", r.get("quote_fns"),
          "free=", r.get("free_views"), "gate=", r.get("gate_fns_corrected"), flush=True)

# --- 2. First-mint verification for agent-shaped (Ankr module) ---
TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO_TOPIC = "0x0000000000000000000000000000000000000000000000000000000000000000"
def ankr_earlier(addr, frm, to):
    total = 0; earliest = None; token = None; pages = 0
    while True:
        params = {"blockchain": "bsc", "fromBlock": hex(frm), "toBlock": hex(to),
                  "pageSize": 1000, "decodeLogs": False, "address": addr,
                  "topics": [TRANSFER, ZERO_TOPIC]}
        if token: params["pageToken"] = token
        body = ankr_post("ankr_getLogs", params, timeout=30)
        result = body.get("result", {}) if isinstance(body, dict) else {}
        logs = result.get("logs", [])
        for lg in logs:
            total += 1
            b = int(lg.get("blockNumber", "0x0"), 16)
            earliest = b if earliest is None else min(earliest, b)
        token = result.get("nextPageToken"); pages += 1
        if not token or pages >= 15: break
        time.sleep(2.2)
    return total, earliest
GAP_START = 131919215  # main-scan watermark before this run; earlier mints covered by prior scans/seen (known gaps stated)
for r in out["nft_first_seen"]:
    if not r.get("agent_shaped"):
        continue
    addr, fb = r["address"], r["first_block"]
    if fb is None or fb <= GAP_START:
        r["earlier_mints_before_window"] = None
        r["first_mint_verified"] = False
        r["first_mint_note"] = "first_block <= gap start; cannot verify via gap range"
        continue
    try:
        earlier, earliest = ankr_earlier(addr, GAP_START, fb - 1)
        r["earlier_mints_before_window"] = earlier
        r["earliest_before_window"] = earliest
        r["first_mint_verified"] = (earlier == 0)
    except Exception as e:
        r["earlier_mints_before_window"] = None
        r["first_mint_verified"] = False
        r["first_mint_note"] = f"Ankr error: {e!r}"
    print("FIRST-MINT", addr, "earlier=", r["earlier_mints_before_window"],
          "verified=", r["first_mint_verified"], flush=True)

# --- 3. 5c: ERC20 backlog shape-check ---
checked = json.load(open(f"{BASE}/track-c-scan-checked.json"))
checked_set = {k.lower() for k in checked.get("checked", {})}
cands = [c for c in scan.get("erc20_mint_contracts_list", []) if c.get("mint_count", 0) >= 10]
cands.sort(key=lambda c: -c.get("mint_count", 0))
todo = [c for c in cands if c["address"].lower() not in checked_set][:20]
dropped = max(0, len([c for c in cands if c["address"].lower() not in checked_set]) - 20)
print(f"5c: {len(cands)} ERC20 >=10 mints, {len(todo)} to check, {dropped} dropped (sampling limit)", flush=True)
for c in todo:
    addr = c["address"]
    status, abi = sourcify_abi(addr)
    r = {"address": addr, "mint_count": c.get("mint_count"),
         "distinct_minters": c.get("distinct_minters"),
         "first_block": c.get("first_block"), "last_block": c.get("last_block"),
         "sourcify": status}
    if abi is not None:
        r.update(classify(abi))
    else:
        r.update({"functions": 0, "mint_fns": [], "quote_fns": [], "free_views": [],
                  "gate_fns": [], "token_fns": [], "S1": False, "S2": False})
    out["erc20_5c"].append(r)
    checked.setdefault("checked", {})[addr] = {"source": "scan-2026-11-06-0931-5c",
                                               "run": "2026-11-06-0931",
                                               "S1": r.get("S1"), "S2": r.get("S2")}
    print("5c", addr, "mints=", c.get("mint_count"), "minters=", c.get("distinct_minters"),
          status, "S1=", r.get("S1"), "S2=", r.get("S2"), flush=True)
out["erc20_5c_dropped_sampling"] = dropped
json.dump(out, open(f"{BASE}/run-{TS}-scan-triage.json", "w"), indent=1)
json.dump(checked, open(f"{BASE}/track-c-scan-checked.json", "w"), indent=1)

# --- 4. Append first-seen to NESTED seen['contracts']; advance watermark ---
for c in first_seen:
    seen.setdefault("contracts", {})[c["address"].lower()] = c.get("first_block")
seen.setdefault("_meta", {})["last_scan_wib"] = "2026-11-06 run 0931"
seen["_meta"]["last_scan_window"] = "131926748-131927747"
seen["_meta"]["last_scan_added"] = len(first_seen)
seen["_meta"]["last_updated_wib"] = "2026-11-06 run 0931"
json.dump(seen, open(f"{BASE}/onchain-scan-seen.json", "w"), indent=1)
state = json.load(open(f"{BASE}/onchain-scan-state.json"))
state["last_scanned_block"] = scan.get("to_block")
state["last_scan_window_from"] = scan.get("from_block")
state["last_scan_window_to"] = scan.get("to_block")
state["last_scan_wib"] = "run 2026-11-06-0931"
state["ankr_calls"] = scan.get("ankr_calls")
state["errors"] = scan.get("errors")
state["nft_contracts"] = len(scan.get("contracts", []))
state["erc20_mint_contracts"] = scan.get("erc20_mint_contracts")
state["skipped_gap"] = "131919215-131926747 (7533 blok; window dari watermark 131919214 ke head 131927747 = 8533 blok > cap 1000; scan menutup 1000 blok terbaru 131926748-131927747)"
state["note_0931_scan"] = "Run 0931: SCAN SUKSES (amendment pre-flight + cap 1000 + per-chunk log). Pre-flight OK 5,0 dtk. Watermark 131919214 -> 131927747. Gap 131919215-131926747 belum ter-cover (backfill). Shape-check phase lambat (762 dtk total, nyaris timeout 780) - risiko JSON hilang bila shape mati; perlu penulisan parsial / pemisahan shape-check."
json.dump(state, open(f"{BASE}/onchain-scan-state.json", "w"), indent=1)
print("triage done; first-seen:", len(first_seen), "; nested seen now:", len(seen.get("contracts", {})), "; watermark ->", scan.get("to_block"), flush=True)
