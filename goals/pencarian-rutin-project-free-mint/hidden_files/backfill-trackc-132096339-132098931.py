#!/usr/bin/env python3
"""Track-C 5c shape-check for backfill run 132096339-132098931 (2026-11-07 ~06:55 WIB).
Read-only except appending newly checked addresses to track-c-scan-checked.json.
S1 = mint + quote/cost + free-share view + registry/AgentGate.
S2 = single-contract token+sale: name/symbol/decimals/totalSupply + mintFree()
     + free views + agentRegistry + mintPaid with PRICE.
"""
import json, subprocess
from datetime import datetime, timezone, timedelta

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
WIB = timezone(timedelta(hours=7))
NEW = [ ("0x730482D0792d0613898f16eFF720e4A1998B073e", 40),
 ("0xd649aa16c20bd91758D85C82130254029A9b0463", 26),
 ("0x486c29a5A5923e7E2D63574491B4D95Fd74Ab684", 19),
 ("0x61c937308D6591ba2bf9934b00af941405B3E398", 13),
 ("0x27c5165f01B990CDA880388E2BDa520f0D96CF8E", 13),
 ("0xD9dDa887eB972e59e93A6B1eA83da1d111e80EDc", 11),
 ("0xdb760059Bf7C6b089D0088b2C040f5d06A69BB1b", 11),
 ("0xC37a7C2a5333f4A04c2EB5C9171fEec0665a0c61", 10),
 ("0xC98101E427609CF5DA4FfDE9c588C091eB2dE0fF", 10),
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
    out = {"run": "backfill-132096339-132098931",
           "checked_wib": datetime.now(WIB).strftime("%Y-%m-%d %H:%M:%S"),
           "track_c_5c_shape": results}
    json.dump(out, open(f"{BASE}/backfill-triage-132096339-132098931-trackc.json", "w"), indent=1)
    print("WROTE backfill-triage-132096339-132098931-trackc.json")

if __name__ == "__main__":
    main()
