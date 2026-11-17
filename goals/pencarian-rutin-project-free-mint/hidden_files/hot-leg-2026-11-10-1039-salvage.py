#!/usr/bin/env python3
"""1039 salvage: bounded shape-check of the 20 fresh feed + 3 Boltbook addrs
that the 1039 run fetched before its 280s timeout killed the main script.
Hard cap via outer `timeout 100`. 10s per ABI fetch, 8 workers.
Writes results into hot-leg-seen.json (own state only) + salvage JSON.
No preview/mint. No snapshot writes."""
import json, subprocess, concurrent.futures

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
REG = "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F"
EXCLUDED = {"0x827e83e49bd7e15b67efa0e90fc25f17b8d96124",
            "0x8b47354e7b76b1970a0d06365c8244a810d37493"}
NOW_ISO = "2026-11-10T10:44:00+07:00"
FREE_VIEWS = {"freeSharesRemaining", "freeClaimed", "freeFor", "freeLeft", "freeUsed",
              "freeAvailable", "freeSharePoolExhausted", "freeSharesClaimed",
              "freeMinted", "freeCardsRemaining"}

feed = json.load(open(BASE + "hot-leg-2026-11-10-1039-feed.json"))
addrs = [a for a, _ in feed.get("feed", [])]
import re
ADDR_RE = re.compile(r"0x[0-9a-fA-F]{40}")
seen = json.load(open(BASE + "hot-leg-seen.json"))
seen_l = {k.lower() for k in seen}
for lang in ("en", "zh"):
    txt = open(BASE + f"hot-leg-2026-11-10-1039-boltbook-{lang}.html", errors="ignore").read()
    addrs += [a for a in sorted(set(ADDR_RE.findall(txt))) if a.lower() not in seen_l]
addrs = sorted(set(addrs) - {REG} - EXCLUDED, key=str.lower)
try:
    discards = json.load(open(BASE + "same-owner-discards.json"))
    discard_contracts = {str(e.get("contract", "")).lower() for e in discards if isinstance(e, dict)}
except Exception:
    discard_contracts = set()

def shape_check(addr):
    try:
        r = subprocess.run(["curl", "-sS", "-m", "10", "-A", "hot-leg/1.0",
                            f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi"],
                           capture_output=True, timeout=15)
        if r.returncode != 0 or not r.stdout:
            return {"address": addr, "error": f"curl rc={r.returncode}"}
        meta = json.loads(r.stdout.decode())
        abi = meta.get("abi", [])
        fns = {}
        for e in abi:
            if e.get("type") == "function":
                fns.setdefault(e["name"], []).append(e)
        names = set(fns)
        has_mint = any(n.lower().startswith("mint") for n in names)
        has_quote = bool(names & {"quote", "cost", "getQuote", "mintCost", "price", "getPrice"})
        free_views = sorted(names & FREE_VIEWS)
        agent_ref = bool(names & {"agentId", "agentRegistry", "registry", "getAgentId",
                                  "agentGate", "AgentGate"})
        is_token = bool(names & {"name", "symbol", "decimals", "totalSupply"})
        mintfree = "mintFree" in fns and any(len(e.get("inputs", [])) == 0 for e in fns["mintFree"])
        s1 = has_mint and has_quote and bool(free_views) and agent_ref
        s2 = (is_token and mintfree and bool(names & {"freeClaimed", "freeMinted"})
              and bool(names & {"FREE_SLOTS", "FREE_SUPPLY"}) and agent_ref)
        return {"address": addr, "S1": s1, "S2": s2, "has_mint": has_mint,
                "has_quote": has_quote, "free_views": free_views, "agent_ref": agent_ref,
                "is_token": is_token}
    except Exception as e:
        return {"address": addr, "error": f"{type(e).__name__}: {str(e)[:60]}"}

results = []
with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:
    results = list(ex.map(shape_check, addrs))
sale_shape = []
for r in results:
    a = r["address"]
    if a.lower() in discard_contracts:
        stt, note = "blocked-same-owner-discarded", "in same-owner-discards.json - never promoted/reported"
    elif r.get("S1") or r.get("S2"):
        stt, note = "sale-shape", f"S1={r.get('S1')} S2={r.get('S2')} free={r.get('free_views')} (1039 salvage; on-chain verification NOT done - watchlist-only until verified)"
        sale_shape.append(r)
    elif r.get("error"):
        stt, note = "checked-abi-unavailable", f"Sourcify ABI error (1039 salvage): {r['error']}"
    else:
        stt, note = "checked-not-sale-shape", (
            f"S1={r.get('S1')} S2={r.get('S2')} mint={r.get('has_mint')} "
            f"quote={r.get('has_quote')} free={r.get('free_views')} "
            f"agent={r.get('agent_ref')} token={r.get('is_token')}")
    seen[a] = {"first_seen_wib": seen.get(a, {}).get("first_seen_wib", NOW_ISO),
               "note": note, "source": "hot-leg-1039", "status": stt}
json.dump(seen, open(BASE + "hot-leg-seen.json", "w"), indent=1)
json.dump({"run": "2026-11-10 10:39 WIB salvage", "checked": len(results),
           "sale_shape": sale_shape, "results": results},
          open(BASE + "hot-leg-2026-11-10-1039-salvage.json", "w"), indent=1)
print(json.dumps({"checked": len(results),
                  "sale_shape": sale_shape,
                  "errors": sum(1 for r in results if r.get("error")),
                  "not_sale": sum(1 for r in results if not r.get("error") and not r.get("S1") and not r.get("S2"))}, indent=1))
