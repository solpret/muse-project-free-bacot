#!/usr/bin/env python3
"""Run 1001 Sourcify feed shape-check (S1/S2), read-only.
Fetches the fresh recently-verified feed (limit 20), shape-checks each ABI.
Writes run-2026-11-10-1231-feed-shape.json."""
import json, urllib.request, concurrent.futures, time
REG = "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F"
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
FREE_VIEWS = ["freeSharesRemaining", "freeClaimed", "freeFor", "freeLeft", "freeUsed", "freeAvailable",
              "freeSharePoolExhausted", "freeSharesClaimed", "freeMinted", "freeCardsRemaining"]

def fetch_json(url, timeout=30):
    req = urllib.request.Request(url, headers={"User-Agent": "free-bacot/1001"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode())

feed = fetch_json("https://sourcify.dev/server/v2/contracts/56?limit=20&sort=desc", timeout=40)
addrs = [x["address"] for x in feed["results"]]
print("FEED", len(addrs), [x["verifiedAt"] for x in feed["results"][:3]], flush=True)

def check(addr):
    url = f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi"
    try:
        meta = fetch_json(url, timeout=30)
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
        s1 = has_mint and has_quote and bool(free_views) and agent_ref
        is_token = bool(names & {"name", "symbol", "decimals", "totalSupply"})
        mintfree = "mintFree" in fns and any(len(e.get("inputs", [])) == 0 for e in fns["mintFree"])
        s2 = is_token and mintfree and bool(names & {"freeClaimed", "freeMinted"}) and bool(names & {"FREE_SLOTS", "FREE_SUPPLY"}) and agent_ref
        return {"address": addr, "S1": s1, "S2": s2, "has_mint": has_mint,
                "has_quote": has_quote, "free_views": free_views, "agent_ref": agent_ref,
                "is_token": is_token}
    except Exception as ex:
        return {"address": addr, "error": f"{type(ex).__name__}: {str(ex)[:150]}"}

t0 = time.time()
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as ex:
    out = list(ex.map(check, addrs))
for o in out:
    print(json.dumps(o), flush=True)
json.dump({"feed_verifiedAt": [x["verifiedAt"] for x in feed["results"]], "results": out},
          open(f"{BASE}/run-2026-11-10-1231-feed-shape.json", "w"), indent=1)
print("S1_PASS:", [o["address"] for o in out if o.get("S1")])
print("S2_PASS:", [o["address"] for o in out if o.get("S2")])
print("ERRORS:", [(o["address"], o.get("error")) for o in out if o.get("error")])
print("ELAPSED %.1fs" % (time.time() - t0))
