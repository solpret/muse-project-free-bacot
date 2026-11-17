#!/usr/bin/env python3
"""Track-C 5c shape-check for backfill run 132158419-132164418 (2026-11-07 ~14:16 WIB).
Read-only except appending newly checked addresses to track-c-scan-checked.json.
S1 = mint + quote/cost + free-share view + registry/AgentGate.
S2 = single-contract token+sale: name/symbol/decimals/totalSupply + mintFree()
     + free views + agentRegistry + mintPaid with PRICE.
Merged erc20_mint_contracts_list from both chunk JSONs (mint_count summed),
mint_count >= 10, desc, max 20 NEW (case-insensitive vs checked).
"""
import json, subprocess
from datetime import datetime, timezone, timedelta

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
WIB = timezone(timedelta(hours=7))

def build_new():
    checked = json.load(open(f"{BASE}/track-c-scan-checked.json"))
    lst = checked.get("checked", []) if isinstance(checked, dict) else checked
    have = {a.lower() for a in lst}
    merged = {}
    for f in ["backfill-132158419-132160418.json", "backfill-132160419-132162418.json"]:
        d = json.load(open(f"{BASE}/{f}"))
        for e in d["erc20_mint_contracts_list"]:
            m = merged.setdefault(e["address"], {"address": e["address"], "mint_count": 0})
            m["mint_count"] += e["mint_count"]
    cands = [m for m in merged.values() if m["mint_count"] >= 10]
    cands.sort(key=lambda x: -x["mint_count"])
    new = [(c["address"], c["mint_count"]) for c in cands if c["address"].lower() not in have][:20]
    return new

NEW = build_new()
print("NEW to shape-check:", len(NEW))
for a, mc in NEW:
    print(" ", a, mc)

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

def main():
    results = []
    for addr, mc in NEW:
        status, abi = sourcify_abi(addr)
        fns = [i.get("name") for i in abi if isinstance(abi, list) and i.get("type") == "function"] if isinstance(abi, list) else []
        low = [f.lower() for f in fns]
        has = lambda *names: any(n.lower() in low for n in names)
        s1 = has("mint") and has("quote", "cost") and has("freeclaimed", "freeminted", "freesupply", "freeleft", "free_claimed") and (has("agentregistry") or has("agentgate"))
        s2 = has("mintfree") and has("agentregistry") and has("name", "symbol", "decimals", "totalsupply") and (has("freeclaimed", "freeminted") or has("free_slots", "free_supply"))
        verdict = "S1" if s1 else ("S2" if s2 else "not-sale-shape")
        results.append({"address": addr, "mint_count": mc, "sourcify": status,
                        "abi_functions": fns, "shape": verdict})
        print(f"{addr} mc={mc} sourcify={status} fns={len(fns)} shape={verdict}", flush=True)
        if fns:
            print("   ", ", ".join(fns[:40]), flush=True)
    checked = json.load(open(f"{BASE}/track-c-scan-checked.json"))
    lst = checked.get("checked", []) if isinstance(checked, dict) else checked
    have = {a.lower() for a in lst}
    added = [a for a, _ in NEW if a.lower() not in have]
    lst += added
    checked["checked"] = lst
    json.dump(checked, open(f"{BASE}/track-c-scan-checked.json", "w"), indent=1)
    print(f"track-c-scan-checked.json: +{len(added)} -> {len(lst)} total")
    out = {"run": "backfill-132158419-132164418",
           "checked_wib": datetime.now(WIB).strftime("%Y-%m-%d %H:%M:%S"),
           "track_c_5c_shape": results}
    json.dump(out, open(f"{BASE}/backfill-triage-132158419-132164418-trackc.json", "w"), indent=1)
    print("WROTE backfill-triage-132158419-132164418-trackc.json")

if __name__ == "__main__":
    main()
