#!/usr/bin/env python3
"""Run 2026-11-06 0801 WIB: triage route-4 scan output onchain-scan-2026-11-06-0801.json
(window 131918215-131919214, cap 1000 blocks, amendment 2026-11-06 ~07:49).
- first-seen = NFT contract absent from onchain-scan-seen.json AND snapshot.
- agent-shape test with CORRECTED gate (AGENT_REGISTRY underscore included).
- first-mint verification for agent-shaped (address-filtered eth_getLogs, <=1000-block chunks).
- 5c: top-20 ERC20 mint_count>=10, skip already-checked, S1/S2 test.
- appends first-seen to onchain-scan-seen.json; updates scan-state watermark on success.
Read-only otherwise."""
import json, sys, time, urllib.request
sys.path.insert(0, "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files")
from feed_shape_0001 import sourcify_abi, classify

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TS = "2026-11-06-0801"
scan = json.load(open(f"{BASE}/onchain-scan-2026-11-06-0801.json"))
seen = json.load(open(f"{BASE}/onchain-scan-seen.json"))
snap = json.load(open(f"{BASE}/onchain-snapshot.json"))
snap_addrs = set()
for v in snap.get("contracts", {}).values():
    if isinstance(v, dict) and v.get("address"):
        snap_addrs.add(v["address"].lower())
for v in snap.get("track_c", {}).values():
    if isinstance(v, dict) and v.get("address"):
        snap_addrs.add(v["address"].lower())
seen_l = {k.lower() for k in seen}
out = {"window": [scan.get("from_block"), scan.get("to_block")],
       "ankr_calls": scan.get("ankr_calls"), "errors": scan.get("errors"),
       "nft_contracts": len(scan.get("contracts", [])),
       "erc20_mint_contracts": scan.get("erc20_mint_contracts"),
       "nft_first_seen": [], "erc20_5c": []}

# --- 1. NFT first-seen shape check ---
first_seen = [c for c in scan.get("contracts", [])
              if c["address"].lower() not in seen_l and c["address"].lower() not in snap_addrs]
print(f"NFT contracts in window: {len(scan.get('contracts', []))}; first-seen: {len(first_seen)}", flush=True)
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

# --- 2. First-mint verification for agent-shaped ---
TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO_TOPIC = "0x0000000000000000000000000000000000000000000000000000000000000000"
RPCS = ["https://bsc-dataseed1.bnbchain.org", "https://bsc.publicnode.com", "https://bsc-dataseed2.bnbchain.org"]
def getlogs(addr, frm, to):
    for rpc in RPCS:
        try:
            body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_getLogs", "params": [{
                "fromBlock": hex(frm), "toBlock": hex(to), "address": addr,
                "topics": [TRANSFER, ZERO_TOPIC]}]}).encode()
            req = urllib.request.Request(rpc, data=body, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.load(resp)
            if "result" in data:
                return data["result"]
        except Exception:
            continue
    return None
for r in out["nft_first_seen"]:
    if not r.get("agent_shaped"):
        continue
    addr, fb = r["address"], r["first_block"]
    earlier = 0
    failed = False
    start = 131899549  # watermark start of the un-scanned gap; earlier mints before that are covered by prior scans/seen
    while start < fb:
        end = min(start + 999, fb - 1)
        logs = getlogs(addr, start, end)
        if logs is None:
            failed = True
            break
        earlier += len(logs)
        start = end + 1
    r["earlier_mints_before_window"] = None if failed else earlier
    r["first_mint_verified"] = (not failed) and earlier == 0
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
    checked.setdefault("checked", {})[addr] = {"source": "scan-2026-11-06-0801-5c",
                                               "run": "2026-11-06-0801",
                                               "S1": r.get("S1"), "S2": r.get("S2")}
    print("5c", addr, "mints=", c.get("mint_count"), "minters=", c.get("distinct_minters"),
          status, "S1=", r.get("S1"), "S2=", r.get("S2"), flush=True)
out["erc20_5c_dropped_sampling"] = dropped
json.dump(out, open(f"{BASE}/run-{TS}-scan-triage.json", "w"), indent=1)
json.dump(checked, open(f"{BASE}/track-c-scan-checked.json", "w"), indent=1)

# --- 4. Append first-seen to seen file; advance watermark ---
for c in scan.get("contracts", []):
    a = c["address"]
    if a.lower() not in seen_l and a.lower() not in snap_addrs:
        seen[a] = {"first_seen_block": c.get("first_block"), "source": "scan-2026-11-06-0801"}
json.dump(seen, open(f"{BASE}/onchain-scan-seen.json", "w"), indent=1)
state = json.load(open(f"{BASE}/onchain-scan-state.json"))
state["last_scanned_block"] = scan.get("to_block")
state["last_scan_window_from"] = scan.get("from_block")
state["last_scan_window_to"] = scan.get("to_block")
state["last_scan_wib"] = "run 2026-11-06-0801"
state["ankr_calls"] = scan.get("ankr_calls")
state["errors"] = scan.get("errors")
state["nft_contracts"] = len(scan.get("contracts", []))
state["erc20_mint_contracts"] = scan.get("erc20_mint_contracts")
state["skipped_gap"] = "131899549-131918214 (18666 blok; window dari watermark 131899548 ke head 131919214 = 19594 blok > cap 1000; scan menutup 1000 blok terbaru 131918215-131919214)"
state["note_0801_scan"] = "Run 0801: SCAN SUKSES (amendment pre-flight + cap 1000 + per-chunk log). Pre-flight OK 8,8 dtk. Watermark 131899548 -> %s. Gap 131899549-131918214 belum ter-cover (backfill)." % scan.get("to_block")
json.dump(state, open(f"{BASE}/onchain-scan-state.json", "w"), indent=1)
print("triage done; seen total now:", len(seen), "; watermark ->", scan.get("to_block"), flush=True)
