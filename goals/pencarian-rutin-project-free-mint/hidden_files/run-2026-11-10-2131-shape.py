#!/usr/bin/env python3
"""Run 2131 feed shape-check: 14 newest Sourcify contracts (verified 13:05-13:25Z),
not yet in hot-leg-seen. Same S1/S2 logic as hot-leg 1959 shape.py. Read-only."""
import json, subprocess
FEED = {it["address"].lower(): it.get("verifiedAt") for it in json.load(open("run-2026-11-10-2131-feed.json"))["results"]}
hl = json.load(open("hot-leg-seen.json"))
hlkeys = {k.lower() for k in hl.keys()}
NEW = [a for a in FEED if a not in hlkeys and a != "0x9aab6e84096a780f9400cdd4e230faa41b4545f2"]
print("NEW to shape-check:", len(NEW), NEW)
FREE_VIEWS = ["freeSharesRemaining","freeClaimed","freeFor","freeLeft","freeUsed",
              "freeAvailable","freeSharePoolExhausted","freeSharesClaimed","freeMinted"]
def get(url):
    p = subprocess.run(["curl","-s","--max-time","20",url], capture_output=True, text=True)
    return p.stdout
out = {}
for addr in NEW:
    abi = None; err = ""
    raw = get(f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=metadata")
    try:
        m = json.loads(raw)
        abi = (m.get("metadata") or {}).get("output",{}).get("abi")
        if not abi: err = "no-abi-in-metadata"
    except Exception as e:
        err = f"parse:{e}:{raw[:120]}"
    if not abi:
        out[addr] = {"error": err or "abi-unavailable", "verifiedAt": FEED.get(addr)}
        print(addr, "ERR", err, flush=True)
        continue
    fns = [f.get("name") for f in abi if f.get("type")=="function"]
    fnset = set(fns)
    mint = [f for f in fns if f and "mint" in f.lower()]
    quote = [f for f in fns if f and ("quote" in f.lower() or f in ("cost","getCost","mintCost","price"))]
    free = [f for f in FREE_VIEWS if f in fnset]
    agent = [f for f in fns if f and ("agent" in f.lower() or f in ("registry","AGENT_REGISTRY","agentRegistry","AGENT_ID"))]
    token = [f for f in ("name","symbol","decimals","totalSupply") if f in fnset]
    s1 = bool(mint) and bool(quote) and bool(free) and bool(agent)
    s2 = bool(token) and ("mintFree" in fnset) and bool(set(["freeClaimed","freeMinted"]) & fnset) and bool(set(["FREE_SLOTS","FREE_SUPPLY","FREE_SHARES"]) & fnset) and bool(agent)
    out[addr] = {"S1": s1, "S2": s2, "mint": mint, "quote": quote, "free": free,
                 "agent": agent, "token": token, "fns": len(fns), "verifiedAt": FEED.get(addr)}
    print(addr, "S1=", s1, "S2=", s2, "fns=", len(fns), "mint=", mint[:6], "quote=", quote, "free=", free, "agent=", agent, flush=True)
json.dump(out, open("run-2026-11-10-2131-shape.json","w"), indent=1)
print("SHAPE DONE hits:", [a for a,r in out.items() if r.get("S1") or r.get("S2")])
