#!/usr/bin/env python3
"""Sequential retry of the 10 Sourcify ABI fetches that timed out in parallel
in hot-leg run 0859 (precedent: earlier run closed the same gap with a
sequential retry). Updates hot-leg-seen.json entries only for contracts whose
ABI is now actually read; leaves checked-abi-unavailable otherwise."""
import json, time, urllib.request
from datetime import datetime, timezone, timedelta
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
NOW_ISO = datetime.now(timezone(timedelta(hours=7))).strftime("%Y-%m-%dT%H:%M:%S+07:00")
FREE_VIEWS = ["freeSharesRemaining","freeClaimed","freeFor","freeLeft","freeUsed",
              "freeAvailable","freeSharePoolExhausted","freeSharesClaimed",
              "freeMinted","freeCardsRemaining"]
ADDRS = ["0xd2621425d891424ee1799D777D3807D375b1A7cc",
 "0x924FCe6ed3Cf8c570aD713a86a941C40816b9151",
 "0x28508164A7a36B95A4662d0faB40aCB0c19F726C",
 "0xA7B7A88D8AcbdA2502503EDaF8d22561DF9018D4",
 "0xf6C03bFf9e5Bd88e26f152a263EACee8ea0c7A72",
 "0xDDc2352d1ceC10b42e05A297232f5328902C6c2C",
 "0x5f1413FDbe0F26D5a977877ca7DaEe7513B57C22",
 "0x4884Ab2C338bf4434cB222d19FaB55073877D069",
 "0x5c335d0dF305328816d6dAFA39abdd221A78EA5f",
 "0xA682b3f277af0583Ef7e1952B0524Bca621Fbe69"]
def fetch_abi(addr):
    url = f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi"
    req = urllib.request.Request(url, headers={"User-Agent": "hot-leg/1.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        meta = json.loads(r.read().decode())
    abi = meta.get("abi", [])
    fns = {}
    for e in abi:
        if e.get("type") == "function":
            fns.setdefault(e["name"], []).append(e)
    names = set(fns)
    has_mint = any(n.lower().startswith("mint") for n in names)
    has_quote = bool(names & {"quote","cost","getQuote","mintCost","price","getPrice"})
    free_views = sorted(names & set(FREE_VIEWS))
    agent_ref = bool(names & {"agentId","agentRegistry","registry","getAgentId","agentGate","AgentGate"})
    is_token = bool(names & {"name","symbol","decimals","totalSupply"})
    mintfree = "mintFree" in fns and any(len(e.get("inputs", [])) == 0 for e in fns["mintFree"])
    s1 = has_mint and has_quote and bool(free_views) and agent_ref
    s2 = is_token and mintfree and bool(names & {"freeClaimed","freeMinted"}) and bool(names & {"FREE_SLOTS","FREE_SUPPLY"}) and agent_ref
    return {"S1": s1, "S2": s2, "has_mint": has_mint, "has_quote": has_quote,
            "free_views": free_views, "agent_ref": agent_ref, "is_token": is_token,
            "n_fns": len(abi)}
seen = json.load(open(BASE + "hot-leg-seen.json"))
results = {}
for a in ADDRS:
    try:
        s = fetch_abi(a)
        results[a] = s
        seen[a] = {"first_seen_wib": NOW_ISO,
                   "note": f"Sequential retry run 0859 (parallel ABI fetch timed out): S1={s['S1']} S2={s['S2']} mint={s['has_mint']} quote={s['has_quote']} free={s['free_views']} agent={s['agent_ref']} token={s['is_token']} fns={s['n_fns']}",
                   "source": "sourcify-feed", "status": "checked-not-sale-shape" if not (s["S1"] or s["S2"]) else "sale-shape-pass"}
    except Exception as ex:
        results[a] = {"error": f"{type(ex).__name__}: {str(ex)[:100]}"}
        seen[a]["note"] = seen[a].get("note","") + f" | sequential retry 0859 also failed: {type(ex).__name__}: {str(ex)[:80]}"
    time.sleep(1)
json.dump(seen, open(BASE + "hot-leg-seen.json", "w"), indent=1)
json.dump(results, open(BASE + "hot-leg-2026-11-11-0859-retry.json", "w"), indent=1)
print(json.dumps(results, indent=1))
