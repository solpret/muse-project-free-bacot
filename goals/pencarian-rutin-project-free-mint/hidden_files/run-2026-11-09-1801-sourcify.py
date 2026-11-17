#!/usr/bin/env python3
"""Sourcify recently-verified feed poll run 1801 + shape-check newest.
Read-only; writes run-2026-11-09-1801-sourcify.json / -shape.json."""
import json, urllib.request, time
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
REG = "60b9262456de011f7d15a54cdd8c48baaa8b022f"
def fetch(url, timeout=25):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.load(r)
try:
    feed = fetch("https://sourcify.dev/server/v2/contracts/56?limit=20&sort=desc")
    items = feed if isinstance(feed, list) else feed.get("results", feed)
    print("FEED n=", len(items))
    for it in items[:20]:
        print(" ", it.get("address"), it.get("verifiedAt"), it.get("match"))
    json.dump(items, open(f"{BASE}/run-2026-11-09-1801-sourcify.json","w"), indent=1)
except Exception as e:
    print("FEED ERR", str(e)[:300])
    items = []
# shape-check: newest 6 not already triaged in run 1731
KNOWN1731 = {"0xa705707F96d4ADFF8c2CC457bBa68CBdbdD0Be38","0x13A1Ebc988977f8AF0c2983027FF72f4D81BEF00",
 "0x260bf39a6f3aB5E459856297178CC0DF6003374a","0xaA972433937D6eD7AFd91cabE3B4a26746D94A11",
 "0xB65390e3Af752e4e74D88c43c8eA326eee175485","0x32CBF1f57090394cF2578aDEa345051e75b37B8d"}
FREE_VIEWS = ["freeSharesRemaining","freeClaimed","freeFor","freeLeft","freeUsed",
              "freeAvailable","freeSharePoolExhausted","freeSharesClaimed","freeMinted",
              "freeSupply"]
out = {}
cands = [it for it in items[:12] if it.get("address") and it["address"] not in KNOWN1731][:6]
print("SHAPE candidates:", len(cands))
for it in cands:
    addr = it["address"]
    try:
        d = fetch(f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi")
        abi = d.get("abi") or []
        fns = [f.get("name") for f in abi if isinstance(f, dict) and f.get("type")=="function"]
        src = json.dumps(d.get("stdJson", {}) or {})
        reg = REG.lower() in src.lower() or "agentIdRegistry" in src.lower() or "AGENT_ID_REGISTRY" in src
        has_mint = any(n in fns for n in ("mint","mintFree","claimFree","mintWithAgentTokenId"))
        has_quote = any("quote" in n.lower() or "cost" in n.lower() for n in fns)
        free_views = [n for n in fns if any(fv.lower() in n.lower() for fv in FREE_VIEWS)]
        is_token = any(n in fns for n in ("name","symbol","decimals","totalSupply"))
        s1 = has_mint and has_quote and bool(free_views) and reg
        s2 = is_token and ("mintFree" in fns) and bool(free_views) and reg
        out[addr] = {"verifiedAt": it.get("verifiedAt"), "match": d.get("match"), "fns": fns[:60],
                     "registry_ref": reg, "has_mint": has_mint, "has_quote": has_quote,
                     "free_views": free_views, "is_token": is_token, "S1": s1, "S2": s2}
        print(addr, "S1" if s1 else "-", "S2" if s2 else "-", "reg" if reg else "noreg",
              "fns:", len(fns), fns[:12], flush=True)
    except Exception as e:
        out[addr] = {"error": str(e)[:200]}
        print(addr, "ERR", str(e)[:150], flush=True)
json.dump(out, open(f"{BASE}/run-2026-11-09-1801-sourcify-shape.json","w"), indent=1)
print("SHAPE DONE")
