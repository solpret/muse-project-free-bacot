#!/usr/bin/env python3
"""Hot-leg 2026-11-16 18:04 WIB — legs 1+2: Sourcify feed + Boltbook EN/ZH (read-only)."""
import json, re, urllib.request, concurrent.futures, time
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
def get(url, timeout=25):
    req = urllib.request.Request(url, headers={"User-Agent": "free-mint-hot-leg/1819"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()
# Leg 1: Sourcify feed
feed = json.loads(get("https://sourcify.dev/server/v2/contracts/56?limit=20&sort=desc").decode())
json.dump(feed, open(BASE+"hot-leg-2026-11-16-1819-sourcify.json","w"), indent=1)
addrs = [x["address"] for x in feed.get("results", [])[:20]]
print("FEED addrs:", len(addrs), "newest verifiedAt:", feed.get("results",[{}])[0].get("verifiedAt"))
FREE_VIEWS = ["freeSharesRemaining","freeClaimed","freeFor","freeLeft","freeUsed","freeAvailable",
              "freeSharePoolExhausted","freeSharesClaimed","freeMinted","freeCardsRemaining"]
def shape(addr):
    url = f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi"
    try:
        meta = json.loads(get(url, timeout=20).decode())
        abi = meta.get("abi", [])
        names = {e["name"] for e in abi if e.get("type") == "function"}
        has_mint = any(n.lower().startswith("mint") for n in names)
        has_quote = bool(names & {"quote","cost","getQuote","mintCost","price","getPrice"})
        free_views = sorted(names & set(FREE_VIEWS))
        agent_ref = bool(names & {"agentId","agentRegistry","registry","getAgentId","agentGate","AgentGate"})
        s1 = has_mint and has_quote and bool(free_views) and agent_ref
        is_token = bool(names & {"name","symbol","decimals","totalSupply"})
        s2 = is_token and ("mintFree" in names) and bool(names & {"freeClaimed","freeMinted"}) and bool(names & {"FREE_SLOTS","FREE_SUPPLY"}) and agent_ref
        return {"address": addr, "S1": s1, "S2": s2, "has_mint": has_mint, "has_quote": has_quote,
                "free_views": free_views, "agent_ref": agent_ref, "is_token": is_token, "n_fns": len(names)}
    except Exception as ex:
        return {"address": addr, "error": f"{type(ex).__name__}: {str(ex)[:150]}"}
with concurrent.futures.ThreadPoolExecutor(max_workers=10) as ex:
    out = list(ex.map(shape, addrs))
json.dump(out, open(BASE+"hot-leg-2026-11-16-1819-feedshape.json","w"), indent=1)
for o in out: print(json.dumps(o))
print("S1_PASS:", [o["address"] for o in out if o.get("S1")])
print("S2_PASS:", [o["address"] for o in out if o.get("S2")])
# Leg 2: Boltbook EN + ZH
for lang, fn in (("en","hot-leg-2026-11-16-1819-boltbook-en.html"), ("zh","hot-leg-2026-11-16-1819-boltbook-zh.html")):
    url = "https://boltbook.fun/?lang="+lang if lang=="zh" else "https://boltbook.fun/?lang=en"
    try:
        html = get(url).decode(errors="replace")
        open(BASE+fn,"w").write(html)
        found = sorted(set(re.findall(r"0x[0-9a-fA-F]{40}", html)))
        print(f"BOLTBOOK {lang}: {len(html)} bytes, {len(found)} addrs")
        for a in found: print("  ", a)
    except Exception as ex:
        print(f"BOLTBOOK {lang} FAILED: {type(ex).__name__}: {ex}")
