#!/usr/bin/env python3
"""Hot-leg run 2026-11-14 09:19 WIB (part 2, corrected): Sourcify feed parse
(results array) + shape-check genuinely-new feed contracts + the 3 new
Boltbook contracts (FIREWYRM, Sol, CLOUDFLOCK). Read-only except appending
truly-new contracts to hot-leg-seen.json (case-insensitive dedupe)."""
import json, time, urllib.request, concurrent.futures

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
t0 = time.time()
FREE_VIEWS = {"freeSharesRemaining","freeClaimed","freeFor","freeLeft","freeUsed","freeAvailable",
              "freeSharePoolExhausted","freeSharesClaimed","freeMinted","freeCardsRemaining"}
EXCLUDED = {"0x827e83e49bd7e15b67efa0e90fc25f17b8d96124", "0x8b47354e7b76b1970a0d06365c8244a810d37493"}

seen = json.load(open(BASE + "hot-leg-seen.json"))
seen_lower = {k.lower(): k for k in seen}
out = {"started_wib": "2026-11-14T09:19+07:00", "feed": {}, "boltbook_shapecheck": {}}

# --- Leg 1 (corrected): Sourcify feed ---
try:
    req = urllib.request.Request(
        "https://sourcify.dev/server/v2/contracts/56?limit=20&sort=desc",
        headers={"User-Agent": "hot-leg/1.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        payload = json.loads(r.read().decode())
    results = payload.get("results", []) if isinstance(payload, dict) else payload
    addrs = [c.get("address") for c in results if isinstance(c, dict) and c.get("address")]
    newest = results[0].get("verifiedAt") if results else None
    genuinely_new = [a for a in addrs if a.lower() not in seen_lower and a.lower() not in EXCLUDED]
    out["feed"] = {"total": len(addrs), "newest_verifiedAt": newest,
                   "addresses": addrs, "genuinely_new": genuinely_new}
except Exception as e:
    out["feed"] = {"error": f"{type(e).__name__}: {str(e)[:150]}"}

def shapecheck(addr):
    try:
        req = urllib.request.Request(
            f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi",
            headers={"User-Agent": "hot-leg/1.0"})
        with urllib.request.urlopen(req, timeout=15) as r:
            meta = json.loads(r.read().decode())
        abi = meta.get("abi", [])
        fns = {}
        for e in abi:
            if e.get("type") == "function":
                fns.setdefault(e["name"], []).append(e)
        names = set(fns)
        has_mint = any(n.lower().startswith("mint") for n in names)
        has_quote = bool(names & {"quote","cost","getQuote","mintCost","price","getPrice"})
        free_views = sorted(names & FREE_VIEWS)
        agent_ref = bool(names & {"agentId","agentRegistry","registry","getAgentId","agentGate","AgentGate"})
        is_token = bool(names & {"name","symbol","decimals","totalSupply"})
        mintfree = "mintFree" in fns and any(len(e.get("inputs",[]))==0 for e in fns["mintFree"])
        s1 = has_mint and has_quote and bool(free_views) and agent_ref
        s2 = is_token and mintfree and bool(names & {"freeClaimed","freeMinted"}) and bool(names & {"FREE_SLOTS","FREE_SUPPLY"}) and agent_ref
        return {"address": addr, "S1": s1, "S2": s2, "has_mint": has_mint,
                "has_quote": has_quote, "free_views": free_views, "agent_ref": agent_ref,
                "is_token": is_token, "functions": sorted(names)}
    except Exception as e:
        return {"address": addr, "error": f"{type(e).__name__}: {str(e)[:120]}"}

targets = list(out["feed"].get("genuinely_new", []))
boltbook_new = {
    "FIREWYRM": "0x595b58497b0521af473aef78f4518928b781c869",
    "Sol": "0xf4d75a6e5fd3158a573d0f58676f9667e97eb606",
    "CLOUDFLOCK": "0xe233d131e0b2567d5cedd5259cc2c1b73cf20a9d",
}
for name, addr in boltbook_new.items():
    if addr.lower() not in seen_lower:
        targets.append(addr)

with concurrent.futures.ThreadPoolExecutor(max_workers=5) as ex:
    shapes = list(ex.map(shapecheck, targets))
out["feed"]["shapes"] = [s for s in shapes if s["address"] in (out["feed"].get("genuinely_new") or [])]
by_addr = {s["address"].lower(): s for s in shapes}
out["boltbook_shapecheck"] = {name: by_addr.get(addr.lower(), {"address": addr, "error": "not shape-checked"}) for name, addr in boltbook_new.items()}

# record truly-new contracts (feed + boltbook), storing the page/feed form
now_wib = "2026-11-14T09:19:00+07:00"
added = []
for a in out["feed"].get("genuinely_new", []):
    seen[a] = {"first_seen": now_wib, "source": "hot-leg 0919 sourcify-feed"}
    added.append(a)
for name, addr in boltbook_new.items():
    if addr.lower() not in seen_lower:
        seen[addr] = {"first_seen": now_wib, "source": f"hot-leg 0919 boltbook ({name})"}
        added.append(addr)
        seen_lower[addr.lower()] = addr
if added:
    json.dump(seen, open(BASE+"hot-leg-seen.json","w"), indent=1)
out["added_to_seen"] = added
out["elapsed_s"] = round(time.time()-t0, 1)
json.dump(out, open(BASE+"run-2026-11-14-0919-feed2.json","w"), indent=1)
print(json.dumps(out, indent=1))
print("DONE elapsed", out["elapsed_s"])
