#!/usr/bin/env python3
"""Curl retry of Sourcify shape-checks that failed on transport in run 2026-11-07-0014.
Precedent: 00:04 run retried IncompleteRead failures via curl and all resolved."""
import json, subprocess
from concurrent.futures import ThreadPoolExecutor

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
NOW = "2026-11-07T00:14:38+07:00"
FREE_VIEWS = ["freeSharesRemaining", "freeClaimed", "freeFor", "freeLeft", "freeUsed", "freeAvailable",
              "freeSharePoolExhausted", "freeSharesClaimed", "freeMinted", "freeCardsRemaining"]
addrs = [l.strip() for l in open("/tmp/hotleg-retry-addrs.txt") if l.strip()]

def shape_check(addr):
    try:
        p = subprocess.run(["curl", "-sS", "--max-time", "20", "-A", "hot-leg/1.0",
                            f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi"],
                           capture_output=True, text=True, timeout=25)
        if p.returncode != 0:
            return {"address": addr, "error": f"curl rc={p.returncode}: {p.stderr.strip()[:100]}"}
        meta = json.loads(p.stdout)
        abi = meta.get("abi", [])
        fns = {}
        for e in abi:
            if e.get("type") == "function":
                fns.setdefault(e["name"], []).append(e)
        names = set(fns)
        has_mint = any(n.lower().startswith("mint") for n in names)
        has_quote = bool(names & {"quote", "cost", "getQuote", "mintCost", "price", "getPrice"})
        free_views = sorted(names & set(FREE_VIEWS))
        agent_ref = bool(names & {"agentId", "agentRegistry", "registry", "getAgentId", "agentGate", "AgentGate", "AGENT_ID"})
        is_token = bool(names & {"name", "symbol", "decimals", "totalSupply"})
        mintfree = "mintFree" in fns and any(len(e.get("inputs", [])) == 0 for e in fns["mintFree"])
        s1 = has_mint and has_quote and bool(free_views) and agent_ref
        s2 = is_token and mintfree and bool(names & {"freeClaimed", "freeMinted"}) and bool(names & {"FREE_SLOTS", "FREE_SUPPLY"}) and agent_ref
        return {"address": addr, "S1": s1, "S2": s2, "has_mint": has_mint, "has_quote": has_quote,
                "free_views": free_views, "agent_ref": agent_ref, "is_token": is_token}
    except Exception as e:
        return {"address": addr, "error": f"{type(e).__name__}: {str(e)[:100]}"}

with ThreadPoolExecutor(max_workers=8) as ex:
    results = list(ex.map(shape_check, addrs))
seen = json.load(open(f"{BASE}/hot-leg-seen.json"))
sale = []
for s in results:
    a = s["address"]
    if s.get("error"):
        seen[a] = {"first_seen_wib": seen.get(a, {}).get("first_seen_wib", NOW),
                   "note": f"curl retry also failed on transport ({s.get('error')}) - NOT verified as not-sale-shape; retry next run",
                   "source": seen.get(a, {}).get("source", "sourcify-feed"), "status": "shape-check-failed-transport"}
        continue
    seen[a] = {"first_seen_wib": NOW,
               "note": f"S1={s.get('S1')} S2={s.get('S2')} mint={s.get('has_mint')} quote={s.get('has_quote')} free={s.get('free_views')} agent={s.get('agent_ref')} token={s.get('is_token')} (curl retry)",
               "source": seen.get(a, {}).get("source", "sourcify-feed"),
               "status": "checked-not-sale-shape" if not (s.get("S1") or s.get("S2")) else "sale-shape"}
    if s.get("S1") or s.get("S2"):
        sale.append(s)
json.dump(seen, open(f"{BASE}/hot-leg-seen.json", "w"), indent=1)
json.dump({"retry": results, "sale_shapes": sale}, open(f"{BASE}/hot-leg-2026-11-07-0014-shape-retry.json", "w"), indent=1)
n_ok = sum(1 for s in results if not s.get("error"))
print(json.dumps({"total": len(results), "resolved": n_ok, "still_failed": len(results) - n_ok,
                  "sale_shapes": sale,
                  "still_failed_addrs": [s["address"] for s in results if s.get("error")]}, indent=1))
