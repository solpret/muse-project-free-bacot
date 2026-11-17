#!/usr/bin/env python3
"""Hot-leg 2026-11-07 01:49 leg-1 feed retry (urllib IncompleteRead; curl OK). Shape-check 5 new feed addrs."""
import json, subprocess
from concurrent.futures import ThreadPoolExecutor
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
NOW = "2026-11-07T01:49:38+07:00"
FREE_VIEWS = ["freeSharesRemaining", "freeClaimed", "freeFor", "freeLeft", "freeUsed", "freeAvailable",
              "freeSharePoolExhausted", "freeSharesClaimed", "freeMinted", "freeCardsRemaining"]
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
addrs = json.load(open("/tmp/feed-0149-addrs.json"))
seen = json.load(open(f"{BASE}/hot-leg-seen.json"))
new = [a for a in addrs if a not in seen]
with ThreadPoolExecutor(max_workers=5) as ex:
    shapes = list(ex.map(shape_check, new))
for s in shapes:
    if s.get("error"):
        seen[s["address"]] = {"first_seen_wib": NOW,
            "note": f"shape-check failed on transport ({s.get('error')}) - NOT verified as not-sale-shape; retry next run",
            "source": "sourcify-feed", "status": "shape-check-failed-transport"}
        continue
    seen[s["address"]] = {"first_seen_wib": NOW,
        "note": f"S1={s.get('S1')} S2={s.get('S2')} mint={s.get('has_mint')} quote={s.get('has_quote')} free={s.get('free_views')} agent={s.get('agent_ref')} token={s.get('is_token')}",
        "source": "sourcify-feed", "status": "checked-not-sale-shape" if not (s.get("S1") or s.get("S2")) else "sale-shape"}
json.dump(seen, open(f"{BASE}/hot-leg-seen.json", "w"), indent=1)
out = {"feed_addrs": addrs, "new": new, "shapes": shapes, "seen_total": len(seen)}
json.dump(out, open(f"{BASE}/hot-leg-run-2026-11-07-0149-feedretry.json", "w"), indent=1)
print(json.dumps(out, indent=1))
