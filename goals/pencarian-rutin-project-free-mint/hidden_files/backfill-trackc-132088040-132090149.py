#!/usr/bin/env python3
"""Track-C 5c shape-check for backfill run 132088040-132090149 (2026-11-07).
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
 ("0x3fC32b71fbB8f0Ae67091a789d1f3FC7410DEc3b", 34),
 ("0xeCF9a832F176C2a197AaA24B6bC4d6443373E355", 18),
 ("0xcF7f7575bcbE6E93C479B66822f5C2F5A631c806", 16),
 ("0xEc48596Eb7029515DD8D6D1b54672b908Bd108CD", 12),
 ("0xDB0C9E3Db576118eF9BB684aaE05Faf0A6650a70", 12),
 ("0xFfF477411B6F436dF4bfAB9683192A8FEA3Ec835", 12),
 ("0x7571C4C7bCd7DD85707121C1d540c32fB0C64A64", 10),
 ("0x49A9BAd62bba71422D5Ed0abC246c7E37179C9a4", 10),
 ("0x72B5AbE8d24C90FE588846413Ad3220B96f8Bdcb", 10),
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
    out = {"run": "backfill-132088040-132090149",
           "checked_wib": datetime.now(WIB).strftime("%Y-%m-%d %H:%M:%S"),
           "track_c_5c_shape": results}
    json.dump(out, open(f"{BASE}/backfill-triage-132088040-132090149-trackc.json", "w"), indent=1)
    print("WROTE backfill-triage-132088040-132090149-trackc.json")

if __name__ == "__main__":
    main()
