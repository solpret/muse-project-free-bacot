#!/usr/bin/env python3
"""Hot-leg 2026-11-10 05:44 run: legs 1 (Sourcify feed) + 2 (Boltbook EN/ZH).
Read-only. Writes run json + updates hot-leg-seen.json (new contracts only)."""
import json, urllib.request, concurrent.futures, re, time
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
T0 = time.time()
NOW = "2026-11-10T05:44:00+07:00"
def get(url, timeout=20):
    req = urllib.request.Request(url, headers={"User-Agent": "hot-leg/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", "replace"), r.status
seen = json.load(open(BASE + "hot-leg-seen.json"))
seen_keys = {k.lower() for k in seen.keys()}
# --- LEG 1: Sourcify feed ---
feed = []
try:
    body, st = get("https://sourcify.dev/server/v2/contracts/56?limit=20&sort=desc")
    data = json.loads(body)
    items = data if isinstance(data, list) else data.get("contracts", data.get("results", []))
    for it in items:
        if isinstance(it, dict):
            feed.append((it.get("address"), it.get("verifiedAt")))
        elif isinstance(it, str):
            feed.append((it, None))
    print("feed n=", len(feed), "range=", feed[-1][1], "..", feed[0][1] if feed else None)
except Exception as e:
    print("FEED FAILED:", repr(e))
new_feed = [(a, v) for a, v in feed if a and a.lower() not in seen_keys]
print("feed new:", len(new_feed), [a for a, _ in new_feed])
FREE_VIEWS = ["freeSharesRemaining","freeClaimed","freeFor","freeLeft","freeUsed","freeAvailable",
              "freeSharePoolExhausted","freeSharesClaimed","freeMinted","freeCardsRemaining"]
def fetch_abi(addr):
    url = f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi"
    try:
        body, st = get(url, timeout=15)
        meta = json.loads(body)
        abi = meta.get("abi", [])
        names = {e["name"] for e in abi if e.get("type") == "function"}
        fns = {}
        for e in abi:
            if e.get("type") == "function":
                fns.setdefault(e["name"], []).append(e)
        has_mint = any(n.lower().startswith("mint") for n in names)
        has_quote = bool(names & {"quote","cost","getQuote","mintCost","price","getPrice"})
        free_views = sorted(names & set(FREE_VIEWS))
        agent_ref = bool(names & {"agentId","agentRegistry","registry","getAgentId","agentGate","AgentGate"})
        s1 = has_mint and has_quote and bool(free_views) and agent_ref
        is_token = bool(names & {"name","symbol","decimals","totalSupply"})
        mintfree = "mintFree" in fns and any(len(e.get("inputs", [])) == 0 for e in fns["mintFree"])
        s2 = is_token and mintfree and bool(names & {"freeClaimed","freeMinted"}) and bool(names & {"FREE_SLOTS","FREE_SUPPLY"}) and agent_ref
        return {"address": addr, "functions": sorted(names), "S1": s1, "S2": s2,
                "has_mint": has_mint, "has_quote": has_quote, "free_views": free_views,
                "agent_ref": agent_ref, "is_token": is_token}
    except Exception as ex:
        return {"address": addr, "error": f"{type(ex).__name__}: {str(ex)[:120]}"}
shapes = []
if new_feed:
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:
        shapes = list(ex.map(fetch_abi, [a for a, _ in new_feed]))
    for o in shapes:
        print(json.dumps(o))
# --- LEG 2: Boltbook EN + ZH ---
addrs = {}
for lang, url in (("en", "https://boltbook.fun/"), ("zh", "https://boltbook.fun/?lang=zh")):
    try:
        body, st = get(url, timeout=20)
        found = re.findall(r"0x[0-9a-fA-F]{40}", body)
        print(f"boltbook {lang}: {st} {len(body)}B addrs={len(set(found))}")
        for a in set(found):
            addrs.setdefault(a, []).append(lang)
    except Exception as e:
        print(f"boltbook {lang} FAILED:", repr(e))
new_bb = [(a, langs) for a, langs in addrs.items() if a.lower() not in seen_keys and a.lower() not in {x.lower() for x, _ in new_feed}]
print("boltbook new:", len(new_bb), new_bb)
# --- persist new seen entries ---
va = {a.lower(): v for a, v in feed}
for a, v in new_feed:
    o = next((s for s in shapes if s["address"].lower() == a.lower()), {})
    if o.get("S1") or o.get("S2"):
        note = f"S1={o.get('S1')} S2={o.get('S2')} mint={o.get('has_mint')} quote={o.get('has_quote')} free={o.get('free_views')} agent={o.get('agent_ref')} token={o.get('is_token')} verifiedAt={v}"
        status = "sale-shape-new"
    elif "error" in o:
        note = f"Sourcify ABI error: {o['error']} verifiedAt={v}"
        status = "checked-abi-unavailable"
    else:
        note = f"S1={o.get('S1')} S2={o.get('S2')} mint={o.get('has_mint')} quote={o.get('has_quote')} free={o.get('free_views')} agent={o.get('agent_ref')} token={o.get('is_token')} verifiedAt={v}"
        status = "checked-not-sale-shape"
    seen[a] = {"first_seen_wib": NOW, "note": note, "source": "sourcify-feed", "status": status}
for a, langs in new_bb:
    seen[a] = {"first_seen_wib": NOW, "note": f"Boltbook {langs} front page; ABI not yet fetched this run", "source": "boltbook-" + langs[0], "status": "boltbook-new-unchecked"}
json.dump(seen, open(BASE + "hot-leg-seen.json", "w"), indent=1)
out = {"run": "hot-leg 2026-11-10 05:44", "feed": feed, "feed_new": new_feed,
       "shapes": shapes, "boltbook_addrs": {a: l for a, l in addrs.items()},
       "boltbook_new": new_bb, "seen_total_end": len(seen), "elapsed": round(time.time() - T0, 1)}
json.dump(out, open(BASE + "hot-leg-2026-11-10-0544-feed.json", "w"), indent=1)
print("S1_PASS:", [o["address"] for o in shapes if o.get("S1")])
print("S2_PASS:", [o["address"] for o in shapes if o.get("S2")])
print("seen_total_end:", len(seen), "elapsed:", round(time.time() - T0, 1))
