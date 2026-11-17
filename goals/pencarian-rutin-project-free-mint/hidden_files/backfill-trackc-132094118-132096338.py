#!/usr/bin/env python3
"""Track-C 5c shape-check for backfill run 132094118-132096338 (2026-11-07).
Read-only except appending newly checked addresses to track-c-scan-checked.json.
S1 = mint + quote/cost + free-share view + registry/AgentGate.
S2 = single-contract token+sale: name/symbol/decimals/totalSupply + mintFree()
     + free views + agentRegistry + mintPaid with PRICE.
"""
import json, subprocess
from datetime import datetime, timezone, timedelta

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
WIB = timezone(timedelta(hours=7))
NEW = [
 ("0xE6f92Fe5f40c7B25D7bd748a0eeBF1Fbccbe3Ce1", 48),
 ("0xb1D4F4F396e6Da9d3777242Ae5cD3763238D3f7d", 22),
 ("0x88357433e8765756c795EaafE466dA8d2D8D5EF9", 16),
 ("0x833d37Ba8D67Be0f5B86D72DbA88CeFb0527AAFF", 15),
 ("0xA385c9A6C3624c5aa4CbCE3D251b95bb632eE7Df", 14),
 ("0x750781f162Fa47aC7DFC88839C20Aa7C4D33D9BC", 14),
 ("0xf4bd926EBF76B468F1963085EE121B5F0c7E06Ea", 10),
 ("0xe77F94b8D9636025F4Cdc027F680327818f1351E", 10),
 ("0xE9793faF3E59BC2c29E0747605f319F93B9B5200", 10),
 ("0xaC48F1cCA74681Df2B2A84c09eD3a746b699fe3f", 10),
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
    out = {"run": "backfill-132094118-132096338",
           "checked_wib": datetime.now(WIB).strftime("%Y-%m-%d %H:%M:%S"),
           "track_c_5c_shape": results}
    json.dump(out, open(f"{BASE}/backfill-triage-132094118-132096338-trackc.json", "w"), indent=1)
    print("WROTE backfill-triage-132094118-132096338-trackc.json")

if __name__ == "__main__":
    main()
