#!/usr/bin/env python3
"""Hot-leg 1054 follow-up: single retry of skipped legs 1+2 only.
Both sources confirmed reachable by diagnostic curl (Boltbook 200 47KB in 13s,
Sourcify 200 in 6.7s) — earlier failures were transient slowness, not outages.
One retry, longer timeouts; no further retry this run."""
import json, re, subprocess, concurrent.futures, time
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
TAG = "hot-leg-2026-11-08-1054-retry"
REGISTRY = "0x60b9262456de011f7d15a54cdD8c48bAaa8B022F"
EXCLUDED = {"0x827e83e49bd7e15b67efa0e90fc25f17b8d96124",
            "0x8b47354e7b76b1970a0d06365c8244a810d37493"}
FREE_VIEWS = ["freeSharesRemaining","freeClaimed","freeFor","freeLeft","freeUsed","freeAvailable",
              "freeSharePoolExhausted","freeSharesClaimed","freeMinted","freeCardsRemaining"]
t0 = time.time()
log = {"run": "hot-leg-1054 legs 1+2 retry"}

def curl(url, timeout=25):
    return subprocess.run(["curl","-sL","--max-time",str(timeout),url],
                          capture_output=True, text=True).stdout

seen = json.load(open(BASE+"hot-leg-seen.json"))
seen_lower = {k.lower(): k for k in seen}
def is_seen(a): return a.lower() in seen_lower
snap = json.load(open(BASE+"onchain-snapshot.json"))
snap_addrs = set()
for v in snap.get("contracts", {}).values():
    if isinstance(v, dict):
        for f in ("address","sale","token"):
            if v.get(f): snap_addrs.add(v[f].lower())

def shape(addr):
    try:
        out = curl(f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi", timeout=25)
        meta = json.loads(out)
        abi = meta.get("abi", [])
        fns = {}
        for e in abi:
            if e.get("type") == "function":
                fns.setdefault(e["name"], []).append(e)
        names = set(fns)
        has_mint = any(n.lower().startswith("mint") for n in names) or bool(names & {"claimFreeShare","claimFree","claim"})
        has_quote = bool(names & {"quote","cost","getQuote","mintCost","price","getPrice"})
        free_views = sorted(names & set(FREE_VIEWS))
        agent_ref = bool(names & {"agentId","agentRegistry","registry","REGISTRY","getAgentId","agentGate","AgentGate","AGENT_ID","AGENT_ID_REGISTRY","agentIdOf","AGENT_REGISTRY","hasAgentId"})
        is_token = bool(names & {"name","symbol","decimals","totalSupply"})
        mintfree = "mintFree" in fns and any(len(e.get("inputs",[]))==0 for e in fns["mintFree"])
        s1 = has_mint and has_quote and bool(free_views) and agent_ref
        s2 = is_token and mintfree and bool(names & {"freeClaimed","freeMinted"}) and bool(names & {"FREE_SLOTS","FREE_SUPPLY"}) and agent_ref
        return {"address": addr, "abi_functions": sorted(names), "S1": s1, "S2": s2,
                "mint": has_mint, "quote": has_quote, "free": free_views, "agent": agent_ref, "token": is_token}
    except Exception as ex:
        return {"address": addr, "error": f"{type(ex).__name__}: {str(ex)[:120]}"}

def record(addr, source, status, note):
    seen[addr] = {"first_seen_wib": "2026-11-08T10:54:00+07:00", "source": source,
                  "status": status, "note": note}
    seen_lower[addr.lower()] = addr

def check_new(addrs, source):
    out = []
    new = [a for a in addrs if not is_seen(a) and a.lower() not in EXCLUDED
           and a.lower() != REGISTRY.lower()]
    if not new: return {"new": [], "shapes": []}
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as ex:
        shapes = list(ex.map(shape, new))
    for s in shapes:
        a = s["address"]
        if s.get("error") or not s.get("abi_functions"):
            continue
        if (s.get("S1") or s.get("S2")) and "ownerOf" in (s.get("abi_functions") or []):
            record(a, source, "checked-not-track-c",
                   f"S1={s['S1']} S2={s['S2']} BUT ERC-721 NFT, not fungible share sale.")
        elif s.get("S1") or s.get("S2"):
            record(a, source, "sale-shape-pass",
                   f"S1={s['S1']} S2={s['S2']} fns={s['abi_functions']}")
        else:
            record(a, source, "checked-not-sale-shape",
                   f"S1={s['S1']} S2={s['S2']} mint={s['mint']} quote={s['quote']} free={s['free']} agent={s['agent']} token={s['token']}")
    return {"new": new, "shapes": shapes}

# leg 1 retry
try:
    feed = json.loads(curl("https://sourcify.dev/server/v2/contracts/56?limit=20&sort=desc", timeout=25))
    json.dump(feed, open(BASE+TAG+"-sourcify.json","w"), indent=1)
    results = feed.get("results", feed) if isinstance(feed, dict) else feed
    feed_addrs = []
    for e in results:
        a = e if isinstance(e, str) else (e.get("address") or (e.get("contract") or {}).get("address"))
        if a: feed_addrs.append(a)
    log["leg1_feed"] = {"n": len(feed_addrs), "addrs": feed_addrs}
    log["leg1"] = check_new(feed_addrs, "sourcify-feed")
except Exception as ex:
    log["leg1"] = {"error": f"{type(ex).__name__}: {str(ex)[:160]}", "skipped": True}

# leg 2 retry
KW_EN = ["free share","first share free","1 free share","free mint share"]
KW_ZH = ["免费份额","首个免费","免费铸造","免费mint"]
bolt = {}
for lang in ("en","zh"):
    url = "https://boltbook.fun/" + ("?lang=zh" if lang == "zh" else "")
    html = curl(url, timeout=25)
    open(BASE+TAG+f"-boltbook-{lang}.html","w").write(html)
    found = sorted(set(re.findall(r"0x[0-9a-fA-F]{40}", html)))
    low = html.lower()
    kws = {k: low.count(k.lower()) for k in (KW_EN if lang=="en" else KW_ZH)}
    new_vs_snap = [a for a in found if not is_seen(a) and a.lower() not in EXCLUDED
                   and a.lower() != REGISTRY.lower() and a.lower() not in snap_addrs]
    sc = check_new(new_vs_snap, f"boltbook-{lang}")
    bolt[lang] = {"bytes": len(html), "addrs": len(found), "keyword_hits": kws,
                  "new_vs_snapshot": new_vs_snap, "shape_check": sc}
log["leg2_boltbook"] = bolt
json.dump(seen, open(BASE+"hot-leg-seen.json","w"), indent=1)
log["seen_total_after"] = len(seen)
log["elapsed_sec"] = round(time.time()-t0, 1)
json.dump(log, open(BASE+TAG+".log","w"), indent=1)
print(json.dumps(log, indent=1)[:5000])
print("ELAPSED", round(time.time()-t0, 1))
