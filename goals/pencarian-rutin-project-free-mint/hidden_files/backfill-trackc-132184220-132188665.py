#!/usr/bin/env python3
"""Track-C 5c shape-check for backfill run 132184220-132188665 (2026-11-07 ~18:1x WIB).
Read-only except appending newly checked addresses to track-c-scan-checked.json.
S1 = mint + quote/cost + free-share view + registry/AgentGate.
S2 = single-contract token+sale: name/symbol/decimals/totalSupply + mintFree()
     + free views + agentRegistry + mintPaid with PRICE.
Merged erc20_mint_contracts_list from all 3 chunk JSONs (mint_count summed),
mint_count >= 10, desc, max 20 NEW (case-insensitive vs checked).
Dedupe gabungan: sub-dict 'checked' + top-level 0x keys.
"""
import json, subprocess
from datetime import datetime, timezone, timedelta

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
WIB = timezone(timedelta(hours=7))

def load_checked():
    d = json.load(open(f"{BASE}/track-c-scan-checked.json"))
    have = set()
    if isinstance(d, dict):
        lst = d.get("checked", [])
        if isinstance(lst, list):
            have |= {a.lower() for a in lst if isinstance(a, str)}
        have |= {k.lower() for k in d.keys() if isinstance(k, str) and k.startswith("0x")}
    elif isinstance(d, list):
        have |= {a.lower() for a in d if isinstance(a, str)}
    return d, have

def build_new():
    _, have = load_checked()
    merged = {}
    for f in ["backfill-132184220-132186219.json", "backfill-132186220-132188219.json",
              "backfill-132188220-132188665.json"]:
        d = json.load(open(f"{BASE}/{f}"))
        for e in d["erc20_mint_contracts_list"]:
            m = merged.setdefault(e["address"], {"address": e["address"], "mint_count": 0})
            m["mint_count"] += e["mint_count"]
    cands = [m for m in merged.values() if m["mint_count"] >= 10]
    cands.sort(key=lambda x: -x["mint_count"])
    new = [(c["address"], c["mint_count"]) for c in cands if c["address"].lower() not in have][:20]
    return new, len(cands), len(merged)

NEW, NCAND, NMERGED = build_new()
print(f"merged ERC20 unique={NMERGED} mint_count>=10={NCAND} NEW to shape-check={len(NEW)}")
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
    checked, have = load_checked()
    lst = checked.get("checked", []) if isinstance(checked, dict) else checked
    added = [a for a, _ in NEW if a.lower() not in have]
    lst += added
    checked["checked"] = lst
    json.dump(checked, open(f"{BASE}/track-c-scan-checked.json", "w"), indent=1)
    print(f"track-c-scan-checked.json sub-dict: +{len(added)} -> {len(lst)} total")
    out = {"run": "backfill-132184220-132188665",
           "checked_wib": datetime.now(WIB).strftime("%Y-%m-%d %H:%M:%S"),
           "merged_unique": NMERGED, "candidates_ge10": NCAND,
           "track_c_5c_shape": results}
    json.dump(out, open(f"{BASE}/backfill-triage-132184220-132188665-trackc.json", "w"), indent=1)
    print("WROTE backfill-triage-132184220-132188665-trackc.json")

if __name__ == "__main__":
    main()
