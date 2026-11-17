#!/usr/bin/env python3
"""Run 2026-11-06 0731 WIB: triage backfill chunk 131897549-131899548 (the cron worker's job
per backfill-scan.py docstring: 'snapshot / reporting is the CRON WORKER's job, from the
chunk JSON'). Route-4 scan of this run stalled, so this chunk is the only fresh chain-wide
coverage for the window. Read-only except track-c-scan-checked.json appends.
- 5 first-seen ERC721 (FOD Agent + 4 unnamed 1-mint contracts): Sourcify ABI retry
  (backfill's checks errored IncompleteRead/None) + agent-shape test.
- 5c: top-20 ERC20 by window mint_count >= 10, skip already-checked, S1/S2 sale-shape test.
Agent-shape (NFT early lead): gate_fns non-empty OR (mint_fns AND free_views) - per body,
registry/AgentGate reference or free-mint function/free-supply constant. Registry-bytes hit
alone is NOT enough (81% of test contracts hit it)."""
import json, sys, time, urllib.request
sys.path.insert(0, "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files")
from feed_shape_0001 import sourcify_abi, classify

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TS = "2026-11-06-0731"
bf = json.load(open(f"{BASE}/backfill-131897549-131899548.json"))
out = {"chunk": "131897549-131899548", "nft_first_seen": [], "erc20_5c": []}

# --- 1. NFT first-seen shape check ---
for c in bf.get("first_seen", []):
    addr = c["address"]
    status, abi = sourcify_abi(addr)
    r = {"address": addr, "name": c.get("name"), "symbol": c.get("symbol"),
         "kind": c.get("kind"), "mint_count": c.get("mint_count"),
         "distinct_minters": c.get("distinct_minters"),
         "first_block": c.get("first_block"), "last_block": c.get("last_block"),
         "registry_bytes_hit": c.get("registry_bytes_hit"),
         "backfill_sourcify": c.get("sourcify"), "sourcify": status}
    if abi is not None:
        r.update(classify(abi))
        # CORRECTED gate: classify() GATE_WORDS misses 'AGENT_REGISTRY' (underscore) - blind spot noted run 0701
        funcs = [it.get("name", "") for it in abi if isinstance(it, dict) and it.get("type") == "function"]
        r["gate_fns_corrected"] = [f for f in funcs if "agent_registry" in f.lower() or "agentregistry" in f.lower() or "agentgate" in f.lower()]
        r["agent_shaped"] = bool(r.get("gate_fns_corrected")) or bool(r.get("gate_fns")) or (bool(r.get("mint_fns")) and bool(r.get("free_views")))
    else:
        r.update({"functions": 0, "mint_fns": [], "quote_fns": [], "free_views": [],
                  "gate_fns": [], "token_fns": [], "S1": False, "S2": False,
                  "agent_shaped": False})
    out["nft_first_seen"].append(r)
    print("NFT", addr, c.get("name"), status, "agent_shaped=", r["agent_shaped"],
          "mint=", r.get("mint_fns"), "quote=", r.get("quote_fns"),
          "free=", r.get("free_views"), "gate=", r.get("gate_fns"), flush=True)

# --- 2. First-mint verification for any agent-shaped NFT (no earlier mints) ---
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
    # check for any mint before first_block, back to 131880000, in <=2000-block chunks
    earlier = 0
    failed = False
    start = 131880000
    while start < fb:
        end = min(start + 1999, fb - 1)
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

# --- 3. 5c: ERC20 backlog shape-check (top 20 by mint_count >= 10) ---
checked = json.load(open(f"{BASE}/track-c-scan-checked.json"))
checked_set = {k.lower() for k in checked.get("checked", {})}
cands = [c for c in bf.get("erc20_mint_contracts_list", []) if c.get("mint_count", 0) >= 10]
cands.sort(key=lambda c: -c.get("mint_count", 0))
todo = [c for c in cands if c["address"].lower() not in checked_set][:20]
print(f"5c: {len(cands)} ERC20 >=10 mints, {len(todo)} to check (rest already checked / beyond 20 cap)", flush=True)
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
    checked.setdefault("checked", {})[addr] = {"source": "backfill-131897549-131899548-5c",
                                               "run": "2026-11-06-0731",
                                               "S1": r.get("S1"), "S2": r.get("S2")}
    print("5c", addr, "mints=", c.get("mint_count"), "minters=", c.get("distinct_minters"),
          status, "S1=", r.get("S1"), "S2=", r.get("S2"), flush=True)
out["erc20_5c_skipped_already_checked"] = len(cands) - len(todo) - max(0, len(cands) - 20 - 0) if False else None
json.dump(out, open(f"{BASE}/run-{TS}-backfill-triage.json", "w"), indent=1)
json.dump(checked, open(f"{BASE}/track-c-scan-checked.json", "w"), indent=1)
print("triage done; track-c checked total now:", len(checked.get("checked", {})))
