#!/usr/bin/env python3
"""Hot-leg continuation 2026-11-10 ~12:56 WIB.
The 12:55 run's Sourcify feed fetch timed out (curl rc=28), so its leg1 saw
only 1 new contract. This run's own feed fetch succeeded and found 8
contracts not yet in hot-leg-seen.json. Shape-check those 8 only (S1/S2),
record them in hot-leg-seen.json. Legs 2-4 + bridge were already done by
the 12:55 run (silent, no report) and are NOT repeated here.
No preview/mint. No snapshot/seen-file writes besides hot-leg-seen.json."""
import json, subprocess, time

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
REG = "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F"
EXCLUDED = {"0x827e83e49bd7e15b67efa0e90fc25f17b8d96124",
            "0x8b47354e7b76b1970a0d06365c8244a810d37493"}
NOW = "2026-11-10T12:56:30+07:00"
RUN = "2026-11-10 12:56 WIB (continuation of 12:55 run)"
T0 = time.time()
FREE_VIEWS = {"freeSharesRemaining", "freeClaimed", "freeFor", "freeLeft", "freeUsed",
              "freeAvailable", "freeSharePoolExhausted", "freeSharesClaimed",
              "freeMinted", "freeCardsRemaining"}

NEW = ["0x1b7e286cb07E16Bd57069C164f5c2d0Edbc9ceeC",
       "0x603e2bd6D1Dc6bA98713b7dd6D9e4766197f8637",
       "0x53bF17c573227911c4e5120444e3E323eA4D35eD",
       "0xF25AB4Af85c480eAc6F4CB66690648B2F1ad78A2",
       "0x761fE3D1F194D2beFACf46a8baA82d9b6b2d9F93",
       "0x8A45072ADa2d47699AA80481E8EeF773250e4122",
       "0xC41Ca4efDF68cDBd8375628a4c67b664ab900330",
       "0x49cd102Dc347d223360B56152AF6Aab534464825"]

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

seen = json.load(open(BASE + "hot-leg-seen.json"))
results, shapes, errs = [], [], 0
for a in NEW:
    if a.lower() in {k.lower() for k in seen} or a.lower() == REG.lower() or a.lower() in EXCLUDED:
        continue
    r = shape_check(a)
    results.append(r)
    if "error" in r:
        errs += 1
        seen[a] = {"first_seen_wib": NOW, "note": f"Sourcify ABI error (1256): {r['error']}",
                   "source": "sourcify-feed", "status": "checked-abi-unavailable"}
    elif r["S1"] or r["S2"]:
        shapes.append(r)
        seen[a] = {"first_seen_wib": NOW,
                   "note": f"S1={r['S1']} S2={r['S2']} free={r['free_views']} (1256; on-chain verification NOT done - watchlist-only until verified)",
                   "source": "sourcify-feed", "status": "sale-shape"}
    else:
        seen[a] = {"first_seen_wib": NOW,
                   "note": f"S1={r['S1']} S2={r['S2']} mint={r['has_mint']} quote={r['has_quote']} free={r['free_views']} agent={r['agent_ref']} token={r['is_token']}",
                   "source": "sourcify-feed", "status": "checked-not-sale-shape"}

json.dump(seen, open(BASE + "hot-leg-seen.json", "w"), indent=1)
out = {"run": RUN, "leg1_new": NEW, "shape_results": results,
       "sale_shape": shapes, "errors": errs,
       "report": "NONE - silent run" if not shapes else "SALE-SHAPE FOUND - see detail",
       "elapsed_s": round(time.time() - T0, 1),
       "note": "Continuation: 12:55 run feed timed out; this run's feed succeeded. Legs 2-4 + bridge already done by 12:55 run, not repeated."}
json.dump(out, open(BASE + "hot-leg-run-2026-11-10-1256.json", "w"), indent=1)
print(json.dumps(out, indent=1))
