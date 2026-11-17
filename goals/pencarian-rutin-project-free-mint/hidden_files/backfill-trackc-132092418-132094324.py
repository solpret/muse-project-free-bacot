#!/usr/bin/env python3
"""Track-C 5c shape-check for backfill run 132092418-132094324 (2026-11-07).
Read-only except appending newly checked addresses to track-c-scan-checked.json.
S1 = mint + quote/cost + free-share view + registry/AgentGate.
S2 = single-contract token+sale: name/symbol/decimals/totalSupply + mintFree()
     + free views + agentRegistry + mintPaid with PRICE.
"""
import json, subprocess, sys
from datetime import datetime, timezone, timedelta

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
WIB = timezone(timedelta(hours=7))
NEW = [
 ("0x335eed256263605CF1271de2bAdcFE5a76795973", 39),
 ("0xc69C04814B0dD627e22afD3F8a453b97745473d0", 24),
 ("0xb634a46ACac0B1daE630AE5d252948d7A19314DD", 20),
 ("0x6a08aEF0568E8a049a17388e755749a5CB4f16cB", 13),
 ("0xe6Fe3e8258c25E899Ec612A5226ba6D7c9894ff5", 13),
 ("0xb059B71dbcB643C39a165cdFbf9AA849f38B3be1", 10),
]

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
        print(f"{addr} mc={mc} sourcify={status} fns={len(fns)} shape={verdict}")
        if fns:
            print("   ", ", ".join(fns[:40]))
    checked = json.load(open(f"{BASE}/track-c-scan-checked.json"))
    lst = checked.get("checked", []) if isinstance(checked, dict) else checked
    have = {a.lower() for a in lst}
    added = [a for a, _ in NEW if a.lower() not in have]
    lst += added
    checked["checked"] = lst
    json.dump(checked, open(f"{BASE}/track-c-scan-checked.json", "w"), indent=1)
    print(f"track-c-scan-checked.json: +{len(added)} -> {len(lst)} total")
    out = {"run": "backfill-132092418-132094324",
           "checked_wib": datetime.now(WIB).strftime("%Y-%m-%d %H:%M:%S"),
           "track_c_5c_shape": results}
    json.dump(out, open(f"{BASE}/backfill-triage-132092418-132094324-trackc.json", "w"), indent=1)
    print("WROTE backfill-triage-132092418-132094324-trackc.json")

if __name__ == "__main__":
    main()
