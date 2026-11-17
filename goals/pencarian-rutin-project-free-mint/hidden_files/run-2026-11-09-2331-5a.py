#!/usr/bin/env python3
"""Run 2331 route 5a: shape-check 5 fresh Sourcify feed addresses (not hot-leg-seen/reported/snapshot). Read-only. 0xC8113f80 re-checked (was in 2301 5a list, S1/S2 False).
Writes run-2026-11-09-2331-5a.json."""
import json, urllib.request
from concurrent.futures import ThreadPoolExecutor

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
FREE_VIEWS = ["freeSharesRemaining", "freeClaimed", "freeFor", "freeLeft", "freeUsed",
              "freeAvailable", "freeSharePoolExhausted", "freeSharesClaimed",
              "freeMinted", "FREE_SLOTS", "FREE_SUPPLY", "freeClaimCount", "freeMintsLeft"]

def fetch_abi(addr):
    url = f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi"
    req = urllib.request.Request(url, headers={"User-Agent": "curl/8"})
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            d = json.load(r)
        return d.get("abi"), d.get("verifiedAt")
    except Exception as e:
        return {"_error": str(e)}, None

def shape(addr):
    abi, verified_at = fetch_abi(addr)
    if not isinstance(abi, list):
        return {"address": addr, "error": str(abi), "verifiedAt": verified_at}
    fns = {}
    for f in abi:
        if f.get("type") == "function":
            fns.setdefault(f.get("name"), []).append(f)
    names = set(fns)
    has_mint = any(n.lower().startswith("mint") for n in names)
    has_quote = any("quote" in n.lower() or n in ("cost", "price", "getPrice", "mintPrice") for n in names)
    free = [n for n in FREE_VIEWS if n in names]
    src = json.dumps(abi).lower()
    agent = ("60b9262456de011f7d15a54cdd8c48baaa8b022f" in src or "agentid" in src
             or "agentgate" in src or "agentregistry" in src or "registry" in names)
    tokenish = bool({"name", "symbol", "decimals", "totalSupply"} <= names)
    s1 = has_mint and has_quote and bool(free) and agent
    s2 = tokenish and ("mintFree" in names or "mintfree" in [n.lower() for n in names]) and bool(free) and agent
    return {"address": addr, "verifiedAt": verified_at, "S1": s1, "S2": s2,
            "mint": has_mint, "quote": has_quote, "free": free, "agent": agent,
            "token": tokenish, "fns": sorted(names)}

new5a = ['0xAC80A598bCae80d6559B74f6658d63BF4bE38930', '0xF638Fe9aA85eA2Ab3BF5d008E70A53c1C1474485', '0x67BB53e726353489160d925A27154Db99B208b4D', '0x88601D45D168f1691eaeB04bc983AF60773F06Ea', '0xC8113f80E2613E4E520F448060e34d85323E764a']
out = {"run": "2026-11-09-2331", "5a": {}}
with ThreadPoolExecutor(max_workers=10) as ex:
    for s in ex.map(shape, new5a):
        out["5a"][s["address"]] = s
        print("5a", s["address"], "S1", s.get("S1"), "S2", s.get("S2"),
              "mint", s.get("mint"), "quote", s.get("quote"), "free", s.get("free"),
              "agent", s.get("agent"), "token", s.get("token"), flush=True)
with open(f"{BASE}/run-2026-11-09-2331-5a.json", "w") as f:
    json.dump(out, f, indent=1)
print("5A DONE", flush=True)
