#!/usr/bin/env python3
"""Track-C 5c for backfill run 132254478-132257813.
READ-ONLY. Combines erc20_mint_contracts_list from both chunk JSONs,
mint_count>=10 desc, shape-checks max 20 NEW (skip track-c-scan-checked),
S1/S2 via Sourcify ABI fetched with curl (urllib fallback-prone)."""
import json, subprocess, sys

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
REG = "0x60b9262456de011f7d15a54cdd8c48baaa8b022f"

tot = {}
for f in ["backfill-132254478-132256477.json", "backfill-132256478-132257813.json"]:
    d = json.load(open(BASE + f))
    for e in d["erc20_mint_contracts_list"]:
        tot[e["address"]] = tot.get(e["address"], 0) + e.get("mint_count", 0)

ge10 = sorted([(a, c) for a, c in tot.items() if c >= 10], key=lambda x: -x[1])

checked_doc = json.load(open(BASE + "track-c-scan-checked.json"))
checked = checked_doc.get("checked", [])
checked_lower = {a.lower() for a in checked}

new = [a for a, c in ge10 if a.lower() not in checked_lower][:20]
already = len(ge10) - len([a for a, c in ge10 if a.lower() not in checked_lower])
print(f"ERC20 unique={len(tot)} mint>=10={len(ge10)} already_checked={already} new_to_check={len(new)}")

def fetch_abi(addr):
    url = f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi"
    try:
        r = subprocess.run(["curl", "-s", "-m", "45", url], capture_output=True, text=True)
        d = json.loads(r.stdout)
        return d.get("abi"), d.get("match")
    except Exception as e:
        return None, f"error:{e}"

def shape(abi):
    if not abi:
        return "not_verified", []
    fns = {e["name"] for e in abi if e.get("type") == "function"}
    src = json.dumps(abi).lower()
    # S1: mint + quote/cost + free-share view + registry/AgentGate
    has_mint = any(n in fns for n in ("mint", "mintFree", "mintShares", "buyShares", "claimShares"))
    has_quote = any(n in fns for n in ("quote", "getQuote", "cost", "priceFor", "getPrice", "mintPrice"))
    has_free = any(n in fns for n in ("freeClaimed", "freeMinted", "freeRemaining", "freeSupply", "freeShares", "FREE_SUPPLY", "FREE_SLOTS", "freeLeft"))
    has_reg = ("agentregistry" in src) or ("agentgate" in src) or ("agentid" in src)
    if has_mint and has_quote and has_free and has_reg:
        return "S1", sorted(fns)
    # S2: single-contract token+sale: token fns + mintFree() + free views + agentRegistry + mintPaid + PRICE
    has_token = {"name", "symbol", "decimals", "totalSupply"} <= fns
    has_mintfree = "mintFree" in fns
    has_mintpaid = "mintPaid" in fns
    has_price = "PRICE" in fns
    if has_token and has_mintfree and has_free and has_reg and has_mintpaid and has_price:
        return "S2", sorted(fns)
    return "not_sale_shape", sorted(fns)

results = []
for addr in new:
    mc = dict(ge10)[addr]
    abi, match = fetch_abi(addr)
    s, fns = shape(abi)
    results.append({"address": addr, "mint_count": mc, "sourcify": match, "shape": s})
    print(f"  {addr} mc={mc} sourcify={match} shape={s}")

hits = [r for r in results if r["shape"] in ("S1", "S2")]
print("HITS:", json.dumps(hits, indent=1) if hits else "none")

# record newly checked
for r in results:
    if r["address"] not in checked:
        checked.append(r["address"])
    checked_doc[r["address"]] = {
        "shape": r["shape"], "sourcify": r["sourcify"], "mint_count": r["mint_count"],
        "run": "backfill 132254478-132257813", "wib": "2026-11-08 ~02:50",
    }
checked_doc["checked"] = checked
json.dump(checked_doc, open(BASE + "track-c-scan-checked.json", "w"), indent=1)
print(f"track-c-scan-checked.json checked list: {len(checked)-len(results)} -> {len(checked)}")
json.dump({"run": "backfill-132254478-132257813", "ge10": len(ge10),
           "already": already, "new_checked": len(results), "hits": hits,
           "results": results},
          open(BASE + "backfill-trackc-132254478-132257813.json", "w"), indent=1)
print("wrote backfill-trackc-132254478-132257813.json")
