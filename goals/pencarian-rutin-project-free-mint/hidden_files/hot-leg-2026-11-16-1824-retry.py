#!/usr/bin/env python3
"""Hot-leg 1824 retry: curl fallback for Sourcify feed/shape + Boltbook EN/ZH.
Feed already fetched via curl 18:26 WIB (/tmp/sourcify_feed.json, HTTP 200)."""
import json, re, subprocess
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
def curl(url, timeout=25):
    r = subprocess.run(["curl","-sS","--max-time",str(timeout),"-A","free-mint-hot-leg/1824",url],
                       capture_output=True, text=True)
    if r.returncode != 0: raise RuntimeError(r.stderr.strip()[:150])
    return r.stdout
feed = json.load(open("/tmp/sourcify_feed.json"))
json.dump(feed, open(BASE+"hot-leg-2026-11-16-1824-sourcify.json","w"), indent=1)
addrs = [x["address"] for x in feed.get("results", [])[:20]]
print("FEED addrs:", len(addrs), "newest verifiedAt:", feed.get("results",[{}])[0].get("verifiedAt"))
seen = json.load(open(BASE+"hot-leg-seen.json"))
seen_l = {k.lower() for k in seen}
new = [a for a in addrs if a.lower() not in seen_l]
print("NEW vs hot-leg-seen:", new)
FREE_VIEWS = ["freeSharesRemaining","freeClaimed","freeFor","freeLeft","freeUsed","freeAvailable",
              "freeSharePoolExhausted","freeSharesClaimed","freeMinted","freeCardsRemaining"]
def shape(addr):
    meta = json.loads(curl(f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi"))
    abi = meta.get("abi", [])
    names = {e["name"] for e in abi if e.get("type") == "function"}
    has_mint = any(n.lower().startswith("mint") for n in names)
    has_quote = bool(names & {"quote","cost","getQuote","mintCost","price","getPrice"})
    free_views = sorted(names & set(FREE_VIEWS))
    agent_ref = bool(names & {"agentId","agentRegistry","registry","getAgentId","agentGate","AgentGate"})
    is_token = bool(names & {"name","symbol","decimals","totalSupply"})
    s1 = has_mint and has_quote and bool(free_views) and agent_ref
    s2 = is_token and ("mintFree" in names) and bool(names & {"freeClaimed","freeMinted"}) and bool(names & {"FREE_SLOTS","FREE_SUPPLY"}) and agent_ref
    return {"address": addr, "S1": s1, "S2": s2, "has_mint": has_mint, "has_quote": has_quote,
            "free_views": free_views, "agent_ref": agent_ref, "is_token": is_token, "n_fns": len(names)}
out = []
for a in new:
    try:
        o = shape(a); out.append(o); print(json.dumps(o))
    except Exception as ex:
        out.append({"address": a, "error": f"{type(ex).__name__}: {str(ex)[:150]}"})
        print("SHAPE FAIL", a, type(ex).__name__, str(ex)[:120])
json.dump(out, open(BASE+"hot-leg-2026-11-16-1824-feedshape.json","w"), indent=1)
print("S1_PASS:", [o["address"] for o in out if o.get("S1")])
print("S2_PASS:", [o["address"] for o in out if o.get("S2")])
import shutil
for lang, src in (("en","/tmp/boltbook_en.html"), ("zh","/tmp/boltbook_zh.html")):
    html = open(src, errors="replace").read()
    open(BASE+f"hot-leg-2026-11-16-1824-boltbook-{lang}.html","w").write(html)
    found = sorted(set(re.findall(r"0x[0-9a-fA-F]{40}", html)))
    print(f"BOLTBOOK {lang}: {len(html)} bytes, {len(found)} addrs")
    for a in found: print("  ", a, "SEEN" if a.lower() in seen_l else "NEW")
    json.dump(found, open(BASE+f"hot-leg-2026-11-16-1824-boltbook-{lang}.json","w"))
    for kw in ("free share","first share free","1 free share","free mint share","免费份额","首个免费","免费铸造","免费mint"):
        if kw.lower() in html.lower():
            print(f"  KW hit {lang}: {kw}")
