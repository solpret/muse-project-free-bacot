#!/usr/bin/env python3
"""Track-C 5c shape-check for backfill run 132118975-132122532 (2026-11-07 ~09:45 WIB).
Read-only except appending newly checked addresses to track-c-scan-checked.json.
S1 = mint + quote/cost + free-share view + registry/AgentGate.
S2 = single-contract token+sale: name/symbol/decimals/totalSupply + mintFree()
     + free views + agentRegistry + mintPaid with PRICE.
"""
import json, subprocess
from datetime import datetime, timezone, timedelta

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
WIB = timezone(timedelta(hours=7))
NEW = [ ("0xd5E5f613C024EA161814085D281B996C6591647C", 54),
 ("0xDb178DF31ff0D2A53a6e2DB405CDDfb5cC396c2e", 32),
 ("0xc708Ec07D9D6F981f9ebbaaF6580A33aD2755177", 27),
 ("0x8CFfA82225b2D4f4F9b2cdD99aAC054ca72c0bA0", 23),
 ("0xc0264256E74E94A2C56265e1CD5CC90F3f528edd", 23),
 ("0xEC428D38aB8cA3F67E89A8A4DB989b0Fa8283092", 16),
 ("0x49Dc58d7AfEFa8b7CBF7e6E9C2f97f8b689EF2Bb", 15),
 ("0x6397626D244EEbB27A2C417C01e277FE20285c0B", 15),
 ("0xD9336699445CA0a87B58b2350a99eA88B00Cf8f1", 15),
 ("0x62157Bc9E207659eCA62d3Aca5F257d975B85562", 15),
 ("0x47C6058b0FFf389Ec3491b592917D628605DF131", 15),
 ("0xFC24CA7a2Df32927e85e7D85CA4C1d10a8557509", 14),
 ("0x82319D55FF41459A71420cA40A1216EE93E29d80", 14),
 ("0xC6f7cC1623984BC33d578fE3Af9b4D04e3cd6641", 14),
 ("0xF3e7523740D22e34504A56829D3434e3436DF99b", 14),
 ("0xBdD8112e44edC48f60380cf03B71A80e950418dC", 13),
 ("0x908e902d4b672D03704365C51D70461eA647418b", 13),
 ("0x4fD920D734c98A6946132AA7F7ED9977E6e3B47b", 13),
 ("0xd3ad27A38f8263D3122EF5dD6d97Df7e72d1a26B", 13),
 ("0x9dBC25A446775ac68E9Dd6830314105b65A5425b", 13),
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
    out = {"run": "backfill-132118975-132122532",
           "checked_wib": datetime.now(WIB).strftime("%Y-%m-%d %H:%M:%S"),
           "track_c_5c_shape": results}
    json.dump(out, open(f"{BASE}/backfill-triage-132118975-132122532-trackc.json", "w"), indent=1)
    print("WROTE backfill-triage-132118975-132122532-trackc.json")

if __name__ == "__main__":
    main()
