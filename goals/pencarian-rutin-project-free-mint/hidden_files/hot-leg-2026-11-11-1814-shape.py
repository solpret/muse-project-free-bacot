#!/usr/bin/env python3
"""Shape-check 6 feed-new addresses run 1814 via curl (urllib RemoteDisconnected)."""
import json, subprocess, concurrent.futures
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
FREE_VIEWS = ["freeSharesRemaining", "freeClaimed", "freeFor", "freeLeft", "freeUsed",
              "freeAvailable", "freeSharePoolExhausted", "freeSharesClaimed",
              "freeMinted", "freeCardsRemaining"]
def fetch(addr):
    try:
        r = subprocess.run(["curl","-sL","--max-time","25",
            f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi"],
            capture_output=True, text=True, timeout=30)
        meta = json.loads(r.stdout)
        abi = meta.get("abi", [])
        fns = {}
        for e in abi:
            if e.get("type") == "function":
                fns.setdefault(e["name"], []).append(e)
        names = set(fns)
        has_mint = any(n.lower().startswith("mint") for n in names)
        has_quote = bool(names & {"quote", "cost", "getQuote", "mintCost", "price", "getPrice"})
        free_views = sorted(names & set(FREE_VIEWS))
        agent_ref = bool(names & {"agentId", "agentRegistry", "registry", "getAgentId", "agentGate", "AgentGate"})
        is_token = bool(names & {"name", "symbol", "decimals", "totalSupply", "balanceOf"}) and "totalSupply" in names
        mintfree = "mintFree" in fns and any(len(e.get("inputs", [])) == 0 for e in fns["mintFree"])
        s1 = has_mint and has_quote and bool(free_views) and agent_ref
        s2 = is_token and mintfree and bool(names & {"freeClaimed", "freeMinted"}) and bool(names & {"FREE_SLOTS", "FREE_SUPPLY"}) and agent_ref
        return {"S1": s1, "S2": s2, "mint": has_mint, "quote": has_quote,
                "free": free_views, "agent": agent_ref, "token": is_token, "fns": len(names)}
    except Exception as ex:
        return {"error": f"{type(ex).__name__}: {str(ex)[:120]}"}
new = json.load(open("/tmp/feed1814_new.json"))
with concurrent.futures.ThreadPoolExecutor(max_workers=6) as ex:
    shapes = list(ex.map(fetch, new))
out = {a: s for a, s in zip(new, shapes)}
json.dump(out, open("/tmp/shapes1814.json", "w"), indent=1)
for a, s in out.items():
    print(a, s, flush=True)
print("S1:", [a for a, s in out.items() if s.get("S1")],
      "S2:", [a for a, s in out.items() if s.get("S2")], flush=True)
