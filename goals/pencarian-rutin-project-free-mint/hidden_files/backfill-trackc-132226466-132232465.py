#!/usr/bin/env python3
"""Track-C 5c shape-check, backfill run 132226466-132232465 (2026-11-07 ~23:5x WIB).
Read-only. Top 6 NEW ERC20 (mint_count>=10, deduped across 3 chunks,
not yet in track-c-scan-checked.json keys NOR checked list) -> Sourcify ABI via curl, S1/S2.
"""
import json, subprocess

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TODO = json.load(open("/tmp/trackc-new-top20-132226466.json"))
OUT = f"{BASE}/backfill-trackc-132226466-132232465.json"
FREE_VIEWS = {"freeSharesRemaining", "freeClaimed", "freeFor", "freeLeft",
              "freeUsed", "freeAvailable", "freeSharePoolExhausted",
              "freeSharesClaimed", "freeMinted", "freeCardsRemaining"}

def sourcify_abi(address):
    try:
        p = subprocess.run(["curl", "-s", "-m", "20",
            f"https://sourcify.dev/server/v2/contract/56/{address}?fields=abi"],
            capture_output=True, text=True, timeout=25)
        if p.returncode != 0 or not p.stdout.strip():
            return ("curl_error", None)
        d = json.loads(p.stdout)
        if d.get("match") is None and d.get("abi") is None:
            return ("not_verified", None)
        return ("verified", d.get("abi"))
    except Exception as e:
        return (f"error:{type(e).__name__}", None)

results = []
for c in TODO:
    addr = c["address"]
    status, abi = sourcify_abi(addr)
    fns = {}
    if isinstance(abi, list):
        for e in abi:
            if e.get("type") == "function":
                fns.setdefault(e["name"], []).append(e)
    names = set(fns)
    has_mint = any(n.lower().startswith("mint") for n in names)
    has_quote = bool(names & {"quote", "cost", "getQuote", "mintCost", "price", "getPrice"})
    free_views = sorted(names & FREE_VIEWS)
    agent_ref = bool(names & {"agentId", "agentRegistry", "registry", "getAgentId", "agentGate", "AgentGate"})
    s1 = has_mint and has_quote and bool(free_views) and agent_ref
    is_token = bool(names & {"name", "symbol", "decimals", "totalSupply"})
    mintfree = "mintFree" in fns and any(len(e.get("inputs", [])) == 0 for e in fns["mintFree"])
    s2 = is_token and mintfree and bool(names & {"freeClaimed", "freeMinted"}) and bool(names & {"FREE_SLOTS", "FREE_SUPPLY"}) and agent_ref
    row = {"address": addr, "mint_count": c["mint_count"], "distinct_minters": c["distinct_minters"],
           "first_block": c["first_block"], "sourcify": status, "S1": s1, "S2": s2,
           "shape_pass": s1 or s2, "has_mint": has_mint, "has_quote": has_quote,
           "free_views": free_views, "agent_ref": agent_ref, "is_token": is_token,
           "functions": sorted(names)}
    results.append(row)
    print(addr, "S1" if s1 else "-", "S2" if s2 else "-", status, "mints", c["mint_count"], flush=True)

json.dump({"run": "backfill-132226466-132232465", "results": results}, open(OUT, "w"), indent=1)
print("saved", OUT)
print("S1_PASS:", [r["address"] for r in results if r["S1"]])
print("S2_PASS:", [r["address"] for r in results if r["S2"]])

# record newly checked in track-c-scan-checked.json (both stores: keys + checked list)
checked_path = f"{BASE}/track-c-scan-checked.json"
d = json.load(open(checked_path))
checked = d.get("checked", [])
have = {x.lower() for x in checked} | {k.lower() for k in d.keys() if k.startswith("0x")}
added = 0
for c in TODO:
    if c["address"].lower() not in have:
        checked.append(c["address"])
        have.add(c["address"].lower())
        added += 1
d["checked"] = checked
json.dump(d, open(checked_path, "w"), indent=1)
print(f"track-c-scan-checked.json: +{added} -> {len(checked)} total in list")
