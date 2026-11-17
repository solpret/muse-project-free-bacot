#!/usr/bin/env python3
"""Hot-leg 17:39 shape-fix: re-check stale shape-check-failed entries + 2 new
feed contracts via correct Sourcify v2 endpoint
GET /server/v2/contract/56/<addr>?fields=abi (plural /contracts/ path 404s).
Read-only except hot-leg-seen.json status updates for checked items."""
import json, time, urllib.request, urllib.error
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
REG = "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F"
FV = ["freeSharesRemaining","freeClaimed","freeFor","freeLeft","freeUsed",
      "freeAvailable","freeSharePoolExhausted","freeSharesClaimed","freeMinted"]
def fetch(a):
    req = urllib.request.Request(f"https://sourcify.dev/server/v2/contract/56/{a}?fields=abi",
                                 headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=15) as r: return json.loads(r.read())
    except Exception as e: return {"_err": f"{type(e).__name__}: {str(e)[:100]}"}
def check(a):
    d = fetch(a)
    if "_err" in d: return {"address": a, "status": "abi-fetch-failed", "error": d["_err"]}
    abi = d.get("abi") or []
    fns = {f.get("name","") for f in abi if isinstance(f, dict) and f.get("type")=="function"}
    has_mint = any(n.startswith("mint") for n in fns)
    has_quote = any(("quote" in n.lower() or "cost" in n.lower() or "price" in n.lower()) for n in fns)
    free = [v for v in FV if v in fns]
    agent = any(("agent" in n.lower() or "AgentGate" in n or "registry" in n.lower()) for n in fns) or REG.lower() in json.dumps(d).lower()
    is_token = {"name","symbol","decimals","totalSupply"} <= fns
    s1 = has_mint and has_quote and bool(free) and agent
    s2 = is_token and ("mintFree" in fns) and bool({"freeClaimed","freeMinted"} & fns) and bool({"FREE_SLOTS","FREE_SUPPLY"} & fns) and agent
    return {"address": a, "S1": s1, "S2": s2, "has_mint": has_mint, "has_quote": has_quote,
            "free_views": free, "agent_ref": agent, "is_token": is_token, "n_fns": len(fns),
            "status": "checked", "fns_sample": sorted(fns)[:25]}
seen = json.load(open(BASE+"hot-leg-seen.json"))
retry = [a for a,v in seen.items() if isinstance(v,dict) and v.get("status")=="shape-check-failed"
         and str(v.get("first_seen_wib","")).startswith("2026-11-15")]
new2 = ["0x7a4728dA6CD8203b4C7490E628CD3CE37AAF952C","0x25f569bE1A4241338B76aa6dA8cc0Da56223D650"]
targets = []
for a in retry + new2:
    if a not in targets: targets.append(a)
t0=time.time(); out=[]
for a in targets:
    r = check(a); out.append(r)
    if r.get("status")=="checked":
        seen[a] = {"first_seen_wib": seen.get(a,{}).get("first_seen_wib","2026-11-15T17:39+07:00"),
                   "note": f"S1={r['S1']} S2={r['S2']} mint={r['has_mint']} quote={r['has_quote']} free={r['free_views']} agent={r['agent_ref']} token={r['is_token']}",
                   "source": "hot-leg-1739-shapefix", "status": "sale-shape" if (r["S1"] or r["S2"]) else "checked-not-sale-shape"}
    time.sleep(0.2)
json.dump(seen, open(BASE+"hot-leg-seen.json","w"), indent=1)
res = {"run":"hot-leg 2026-11-15 17:39 shapefix","targets":len(targets),"hits":[r for r in out if r.get("S1") or r.get("S2")],
       "failed":[r for r in out if r.get("status")!="checked"],"checked":out,"elapsed_s":round(time.time()-t0,1)}
json.dump(res, open(BASE+"run-hot-leg-2026-11-15-1739-shapefix.json","w"), indent=1)
print("targets",len(targets),"hits",len(res["hits"]),"failed",len(res["failed"]),"elapsed",res["elapsed_s"])
for r in out:
    if r.get("S1") or r.get("S2") or r.get("status")!="checked": print(r)
