#!/usr/bin/env python3
"""Run 0431: shape-check 5 new Sourcify feed contracts (vs hot-leg-seen).
Read-only; writes run-2026-11-11-0431-shape.json only."""
import json, subprocess, time
from concurrent.futures import ThreadPoolExecutor

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
TAG = "run-2026-11-11-0431"
FREE_VIEWS = ["freeSharesRemaining", "freeClaimed", "freeFor", "freeLeft",
              "freeUsed", "freeAvailable", "freeSharePoolExhausted",
              "freeSharesClaimed", "freeMinted", "FREE_SLOTS", "FREE_SUPPLY"]
NEW = ["0x2beEe6a5A3c704E7090178696187D9cEdFeE5f2f",
       "0x0C01C98850e57B9952f5Ed1A9DDFB097D4659101",
       "0x01B0150501dec67a26BBF079129Dd2fEf81EB2dd",
       "0x24bBd50A6437D433DE93c3213e6fe3C7584f7F61",
       "0xD265a929D0E50bD5ee4675e4E97F38D8380802E2"]

def curl(url, max_time=20):
    p = subprocess.run(["curl", "-s", "--max-time", str(max_time), url],
                       capture_output=True, text=True)
    return p.stdout

feed = json.load(open(BASE + TAG + "-feed.json"))

def shape_check(a):
    try:
        raw = curl(f"https://sourcify.dev/server/v2/contract/56/{a}?fields=abi", 15)
        d = json.loads(raw)
        abi = d.get("abi") or []
        fns = [e.get("name", "") for e in abi if e.get("type") == "function"]
        mint = [f for f in fns if "mint" in f.lower()]
        quote = [f for f in fns if "quote" in f.lower() or "cost" in f.lower()]
        free = [f for f in fns if any(v.lower() in f.lower() for v in FREE_VIEWS)]
        agent = [f for f in fns if "agent" in f.lower() or "registry" in f.lower()]
        token = [f for f in ("name", "symbol", "decimals", "totalSupply") if f in fns]
        s1 = bool(mint and quote and free and agent)
        s2 = bool(token == ["name", "symbol", "decimals", "totalSupply"] and
                  any(f in fns for f in ("mintFree",)) and free and agent)
        variant = [f for f in fns if "claimfree" in f.lower()
                   or "freepoolremaining" in f.lower()
                   or "freeclaims" in f.lower()]
        return {"S1": s1, "S2": s2, "mint": mint, "quote": quote,
                "free": free, "agent": agent, "token": token, "fns": len(fns),
                "variant_claimfree": variant,
                "verifiedAt": next((r.get("verifiedAt") for r in feed.get("results", [])
                                    if r["address"].lower() == a.lower()), None)}
    except Exception as e:
        return {"error": str(e)[:200]}

shape = {}
with ThreadPoolExecutor(max_workers=5) as ex:
    for a, s in zip(NEW, ex.map(shape_check, NEW)):
        shape[a] = s
        print("FEED-SHAPE", a, json.dumps(s), flush=True)
for a in list(shape.keys()):
    if "error" in shape[a]:
        for attempt in range(2):
            time.sleep(1)
            s = shape_check(a)
            if "error" not in s:
                shape[a] = s
                print("FEED-SHAPE-RETRY-OK", a, json.dumps(s), flush=True)
                break
        else:
            print("FEED-SHAPE-RETRY-FAIL", a, shape[a].get("error"), flush=True)
json.dump(shape, open(BASE + TAG + "-shape.json", "w"), indent=1)
print("SHAPE DONE", {a: (v.get("S1"), v.get("S2")) for a, v in shape.items()}, flush=True)
