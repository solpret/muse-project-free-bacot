#!/usr/bin/env python3
"""One-off curl-based leg3 probe for hot-leg 2026-11-18 21:14 run.
Leg3 urllib shape-check failed all 51 (URLError timed out) while legs 1-2
via curl succeeded - retry the 22 FRESH contracts (20 feed + 2 Boltbook)
via curl so this run's new contracts are actually shape-checked.
Same S1/S2 logic as the run script. Read-only; writes only the probe JSON."""
import json, subprocess

HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
d = json.load(open(f"{HF}/hot-leg-run-2026-11-18-2114.json"))
targets = list(dict.fromkeys(
    [a for a, _ in [(c, None) for c in d["leg1_sourcify"].get("new_contracts", [])]]
    + d["leg2_boltbook_en"].get("new_contracts", [])))
FREE_VIEWS = {"freeSharesRemaining","freeClaimed","freeFor","freeLeft","freeUsed","freeAvailable",
              "freeSharePoolExhausted","freeSharesClaimed","freeMinted","freeCardsRemaining"}

def shape_check(addr):
    try:
        p = subprocess.run(["curl","-sS","--max-time","10","-A","muse-hotleg/1.0",
            f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi,metadata"],
            capture_output=True, timeout=15)
        if p.returncode != 0:
            return {"address": addr, "status": "shape-check-failed",
                    "error": f"curl rc={p.returncode}: {p.stderr.decode(errors='replace')[:100]}"}
        meta = json.loads(p.stdout.decode())
        abi = meta.get("abi", [])
        fns = {}
        for e in abi:
            if e.get("type") == "function": fns.setdefault(e["name"], []).append(e)
        names = set(fns)
        has_mint = any(n.lower().startswith("mint") for n in names)
        has_quote = bool(names & {"quote","cost","getQuote","mintCost","price","getPrice"})
        free_views = sorted(names & FREE_VIEWS)
        agent_ref = bool(names & {"agentId","agentRegistry","registry","getAgentId","agentGate","AgentGate"})
        is_token = bool(names & {"name","symbol","decimals","totalSupply"})
        s1 = has_mint and has_quote and bool(free_views) and agent_ref
        mintfree = "mintFree" in fns and any(len(e.get("inputs", [])) == 0 for e in fns["mintFree"])
        s2 = is_token and mintfree and bool(names & {"freeClaimed","freeMinted"}) and bool(names & {"FREE_SLOTS","FREE_SUPPLY"}) and agent_ref
        return {"address": addr, "S1": s1, "S2": s2, "has_mint": has_mint, "has_quote": has_quote,
                "free_views": free_views, "agent_ref": agent_ref, "is_token": is_token,
                "n_fns": len(names), "status": "checked", "verifiedAt": meta.get("verifiedAt")}
    except Exception as e:
        return {"address": addr, "status": "shape-check-failed", "error": f"{type(e).__name__}: {str(e)[:120]}"}

res = [shape_check(a) for a in targets]
out = {"probe": "curl leg3 retry, hot-leg 2026-11-18 21:14",
       "targets": len(targets),
       "checked": [r for r in res if r.get("status") == "checked"],
       "failed": [r["address"] for r in res if r.get("status") == "shape-check-failed"],
       "sale_shape": [r for r in res if r.get("S1") or r.get("S2")]}
json.dump(out, open(f"{HF}/hot-leg-2026-11-18-2114-leg3-curl-probe.json", "w"), indent=1)
print(json.dumps(out, indent=1)[:6000])
