#!/usr/bin/env python3
"""Hot-leg run 2026-11-01 23:14 WIB. Read-only except own state files."""
import json, re, urllib.request, concurrent.futures, os
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
seen = json.load(open(f"{BASE}/hot-leg-seen.json"))
# Leg 1: Sourcify feed
feed = []
feed_err = None
try:
    req = urllib.request.Request("https://sourcify.dev/server/v2/contracts/56?limit=20&sort=desc", headers={"User-Agent":"hot-leg/1.0"})
    with urllib.request.urlopen(req, timeout=15) as r:
        data = json.loads(r.read().decode())
    # feed shape: list of {address, ...} or dict with results
    items = data if isinstance(data, list) else data.get("results", data.get("contracts", []))
    for it in items:
        if isinstance(it, dict):
            a = it.get("address") or it.get("contractAddress")
            if a: feed.append(a)
        elif isinstance(it, str):
            feed.append(it)
except Exception as e:
    feed_err = f"{type(e).__name__}: {str(e)[:200]}"
print("FEED_COUNT", len(feed), "ERR", feed_err)
print("FEED", feed)
new_feed = [a for a in feed if a not in seen and a.lower() not in [k.lower() for k in seen]]
print("NEW_FEED", new_feed)
# shape-check only new
FREE_VIEWS = {"freeSharesRemaining","freeClaimed","freeFor","freeLeft","freeUsed","freeAvailable","freeSharePoolExhausted","freeSharesClaimed","freeMinted","freeCardsRemaining"}
def shape(addr):
    try:
        req = urllib.request.Request(f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi", headers={"User-Agent":"hot-leg/1.0"})
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
        s1 = has_mint and has_quote and bool(free_views) and agent_ref
        is_token = bool(names & {"name","symbol","decimals","totalSupply"})
        mintfree = "mintFree" in fns and any(len(e.get("inputs",[]))==0 for e in fns["mintFree"])
        s2 = is_token and mintfree and bool(names & {"freeClaimed","freeMinted"}) and bool(names & {"FREE_SLOTS","FREE_SUPPLY"}) and agent_ref
        return {"address": addr, "S1": s1, "S2": s2, "functions": sorted(names), "has_mint": has_mint, "has_quote": has_quote, "free_views": free_views, "agent_ref": agent_ref, "is_token": is_token}
    except Exception as ex:
        return {"address": addr, "error": f"{type(ex).__name__}: {str(ex)[:150]}"}
shapes = []
if new_feed:
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as ex:
        shapes = list(ex.map(shape, new_feed))
print("SHAPES", json.dumps(shapes))
json.dump({"feed": feed, "feed_err": feed_err, "new_feed": new_feed, "shapes": shapes}, open(f"{BASE}/hot-leg-2026-11-01-2314-sourcify.json","w"), indent=1)
# Leg 2: Boltbook front page en + zh, direct fetch
bolt_addrs = {}
for label, url in [("en","https://boltbook.example/"),]:
    pass
# Boltbook actual domain: try boltbook.io / boltbook.xyz? Previous run used direct reads; search memory: use browser? Keep fast: try known domains from prior files via grep in script? Instead fetch via known URL patterns attempted below.
import subprocess
for label, url in [("en","https://boltbook.fun/?lang=en"), ("zh","https://boltbook.fun/?lang=zh")]:
    try:
        req = urllib.request.Request(url, headers={"User-Agent":"Mozilla/5.0 hot-leg/1.0"})
        with urllib.request.urlopen(req, timeout=15) as r:
            html = r.read().decode(errors="ignore")
        addrs = sorted(set(re.findall(r"0x[a-fA-F0-9]{40}", html)))
        bolt_addrs[label] = {"url": url, "len": len(html), "addrs": addrs}
        print(label, "len", len(html), "addrs", addrs)
    except Exception as e:
        bolt_addrs[label] = {"url": url, "error": f"{type(e).__name__}: {str(e)[:150]}"}
        print(label, "ERR", bolt_addrs[label]["error"])
json.dump(bolt_addrs, open(f"{BASE}/hot-leg-2026-11-01-2314-boltbook.json","w"), indent=1)
