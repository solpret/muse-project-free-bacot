#!/usr/bin/env python3
"""Track-C 5c for backfill run 132266113-132268175.
READ-ONLY except track-c-scan-checked.json bookkeeping + detail JSON.
Combines erc20_mint_contracts_list from both chunk JSONs, mint_count>=10,
desc, shape-check max 20 NEW (Sourcify ABI via curl), skip already-checked.
Sale-shape S1/S2 hit -> recorded in hits (on-chain verification is a
separate step, only if a hit appears)."""
import json, subprocess, time

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
RUN = "backfill-132266113-132268175"

def sourcify_abi(addr):
    url = f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi"
    try:
        r = subprocess.run(["curl", "-s", "--max-time", "30", url],
                           capture_output=True, text=True, timeout=40)
        d = json.loads(r.stdout)
        match = d.get("match")
        abi = d.get("abi")
        return match, abi
    except Exception as e:
        return None, None

def shape_of(abi):
    if not abi:
        return "not_verified", False, False, ""
    names = {e.get("name") for e in abi if e.get("type") == "function"}
    has_registry = bool(names & {"agentRegistry", "agentIdRegistry",
                                 "AGENT_ID_REGISTRY", "AGENT_REGISTRY",
                                 "REGISTRY", "agentGate"})
    has_mint = bool(names & {"mint", "mintFree", "mintPaid", "claim",
                             "claimFree", "buyShare", "buyShares"})
    has_quote = bool(names & {"quote", "cost", "getCost", "price",
                              "mintPrice", "getPrice"})
    has_free = bool(names & {"freeClaimed", "freeMinted", "freeSupply",
                             "freeCount", "FREE_CAP", "FREE_SUPPLY",
                             "FREE_SLOTS", "FREE_AMOUNT", "FREE_PER_WALLET",
                             "freeLeft"})
    has_token = bool(names & {"name", "symbol", "decimals", "totalSupply"})
    s1 = has_mint and has_quote and has_free and has_registry
    s2 = (has_token and "mintFree" in names and has_free
          and "mintPaid" in names and has_registry)
    note = (f"S1={s1} S2={s2} (registry={has_registry} mint={has_mint} "
            f"quote={has_quote} free={has_free} token={has_token})")
    return ("sale-shape-S1" if s1 else "sale-shape-S2" if s2
            else "checked-not-sale-shape"), s1, s2, note

combined = {}
for f in ["backfill-132266113-132268112.json",
          "backfill-132268113-132268175.json"]:
    d = json.load(open(f"{BASE}/{f}"))
    for c in d.get("erc20_mint_contracts_list", []):
        a = c["address"].lower()
        if a not in combined or c.get("mint_count", 0) > combined[a].get("mint_count", 0):
            combined[a] = c

ge10 = [c for c in combined.values() if c.get("mint_count", 0) >= 10]
ge10.sort(key=lambda c: -c.get("mint_count", 0))

checked = json.load(open(f"{BASE}/track-c-scan-checked.json"))
checked_list = checked.get("checked", [])
checked_lower = {a.lower() for a in checked_list}

already = sum(1 for c in ge10 if c["address"].lower() in checked_lower)
new = [c for c in ge10 if c["address"].lower() not in checked_lower][:20]

results, hits = [], []
for c in new:
    addr = c["address"]
    mc = c.get("mint_count", 0)
    match, abi = sourcify_abi(addr)
    if match is None:
        shape, s1, s2, note = "not_verified", False, False, ""
    else:
        shape, s1, s2, note = shape_of(abi)
    results.append({"address": addr, "mint_count": mc,
                    "sourcify": match, "shape": shape})
    print(f"{mc} {addr} sourcify={match} shape={shape} {note}", flush=True)
    if s1 or s2:
        hits.append({"address": addr, "mint_count": mc,
                     "shape": shape, "note": note})
    checked_list.append(addr)
    checked[addr] = {"source": f"{RUN}-5c", "status": shape,
                     "mint_count": mc, "note": note}
    time.sleep(1)

checked["checked"] = checked_list
tmp = f"{BASE}/track-c-scan-checked.json.tmp-backfill-5c"
with open(tmp, "w") as f:
    json.dump(checked, f, indent=1)
import os
os.replace(tmp, f"{BASE}/track-c-scan-checked.json")

out = {"run": RUN, "ge10": len(ge10), "already": already,
       "new_checked": len(new), "hits": hits, "results": results}
with open(f"{BASE}/backfill-trackc-{RUN}.json", "w") as f:
    json.dump(out, f, indent=2)
print(f"ge10={len(ge10)} already={already} new_checked={len(new)} hits={len(hits)}")
print("WROTE", f"{BASE}/backfill-trackc-{RUN}.json")
