#!/usr/bin/env python3
"""Hot-leg run 2026-11-05 15:44 WIB — legs 1,2,3 (Sourcify feed, shape, Boltbook, bridge). Read-only except own state files."""
import json, urllib.request, concurrent.futures, re
HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
STAMP = "2026-11-05-1544"
REG = "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F"
FREE_VIEWS = ["freeSharesRemaining","freeClaimed","freeFor","freeLeft","freeUsed","freeAvailable",
              "freeSharePoolExhausted","freeSharesClaimed","freeMinted","freeCardsRemaining"]
EXCLUDED = {"0x827e83e49bd7e15b67efa0e90fc25f17b8d96124","0x8b47354e7b76b1970a0d06365c8244a810d37493"}

def get(url, timeout=15, headers=None):
    req = urllib.request.Request(url, headers=headers or {"User-Agent":"hot-leg/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()

# --- Leg 1: Sourcify feed ---
feed = json.loads(get("https://sourcify.dev/server/v2/contracts/56?limit=20&sort=desc").decode())
addrs = [c["address"] for c in feed.get("results", feed if isinstance(feed, list) else [])]
if not addrs:
    addrs = [c.get("address") for c in feed]
json.dump(feed, open(f"{HF}/hot-leg-{STAMP}-sourcify.json","w"), indent=1)
seen = json.load(open(f"{HF}/hot-leg-seen.json"))
new = [a for a in addrs if a.lower() not in {k.lower() for k in seen} and a.lower() not in EXCLUDED and a.lower() != REG.lower()]
excl_hit = [a for a in addrs if a.lower() in EXCLUDED]
print("feed_addrs:", len(addrs), "new:", new, "excluded_hit:", excl_hit)
print("latest_verifiedAt:", (feed.get("results") or [{}])[0].get("verifiedAt") if isinstance(feed, dict) else "?")

# --- shape-check new contracts ---
def shape(addr):
    url = f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi"
    try:
        meta = json.loads(get(url).decode())
        abi = meta.get("abi", [])
        fns = {}
        for e in abi:
            if e.get("type") == "function":
                fns.setdefault(e["name"], []).append(e)
        names = set(fns)
        has_mint = any(n.lower().startswith("mint") for n in names)
        has_quote = bool(names & {"quote","cost","getQuote","mintCost","price","getPrice"})
        free_views = sorted(names & set(FREE_VIEWS))
        agent_ref = bool(names & {"agentId","agentRegistry","registry","getAgentId","agentGate","AgentGate"})
        is_token = bool(names & {"name","symbol","decimals","totalSupply"})
        mintfree = "mintFree" in fns and any(len(e.get("inputs",[]))==0 for e in fns["mintFree"])
        s1 = has_mint and has_quote and bool(free_views) and agent_ref
        s2 = is_token and mintfree and bool(names & {"freeClaimed","freeMinted"}) and bool(names & {"FREE_SLOTS","FREE_SUPPLY"}) and agent_ref
        return {"address": addr, "S1": s1, "S2": s2, "has_mint": has_mint, "has_quote": has_quote,
                "free_views": free_views, "agent_ref": agent_ref, "is_token": is_token,
                "functions": sorted(names)}
    except Exception as ex:
        return {"address": addr, "error": f"{type(ex).__name__}: {str(ex)[:120]}"}

shapes = []
if new:
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as ex:
        shapes = list(ex.map(shape, new))
json.dump(shapes, open(f"{HF}/hot-leg-{STAMP}-sourcify-shape.json","w"), indent=1)
for s in shapes:
    print("SHAPE", json.dumps(s)[:600])
    if not s.get("error"):
        seen[s["address"]] = {"first_seen_wib": "2026-11-05T15:44:00+07:00", "source": "sourcify-feed",
            "status": "checked-not-sale-shape" if not (s["S1"] or s["S2"]) else "SALE-SHAPE",
            "note": f"S1={s['S1']} S2={s['S2']} mint={s['has_mint']} quote={s['has_quote']} free={s['free_views']} agent={s['agent_ref']} token={s['is_token']}"}
json.dump(seen, open(f"{HF}/hot-leg-seen.json","w"), indent=1)
print("seen_count:", len(seen))

# --- Leg 2: Boltbook EN + ZH ---
def boltbook(lang):
    url = "https://boltbook.fun/" + ("?lang=zh" if lang=="zh" else "")
    try:
        html = get(url, timeout=15).decode("utf-8", "ignore")
        open(f"{HF}/hot-leg-{STAMP}-boltbook-{lang}.html","w").write(html)
        addrs_found = sorted(set(re.findall(r"0x[0-9a-fA-F]{40}", html)))
        kws = ["free share","first share free","1 free share","free mint share"] if lang=="en" else ["免费份额","首个免费","免费铸造","免费mint"]
        hits = {k: (k.lower() in html.lower()) for k in kws}
        return {"lang": lang, "bytes": len(html), "addrs": addrs_found, "kw_hits": hits}
    except Exception as ex:
        return {"lang": lang, "error": f"{type(ex).__name__}: {str(ex)[:120]}"}

bb = [boltbook("en"), boltbook("zh")]
print("BOLTBOOK", json.dumps(bb))
bb_new = []
for b in bb:
    for a in b.get("addrs", []):
        if a.lower() not in {k.lower() for k in seen}:
            bb_new.append(a)
print("boltbook_new_vs_seen:", bb_new)

# --- Leg 3: bridge (read-only) ---
try:
    bridge = json.load(open(f"{HF}/scan-bridge.json"))
    bcontracts = bridge.get("contracts", {})
    snap = json.load(open(f"{HF}/onchain-snapshot.json"))
    snap_text = json.dumps(snap)
    not_in_snap = [a for a in bcontracts if a.lower() not in snap_text.lower()]
    discarded = [a for a,v in bcontracts.items() if v.get("same_owner_discarded")]
    snap_addrs = set(re.findall(r"0x[0-9a-fA-F]{40}", snap_text))
    in_snap = [a for a in bcontracts if a.lower() in {s.lower() for s in snap_addrs}]
    out = {"bridge_count": len(bcontracts), "same_owner_discarded": len(discarded),
           "not_in_snapshot": not_in_snap, "in_snapshot": in_snap}
    json.dump(out, open(f"{HF}/hot-leg-{STAMP}-bridge.json","w"), indent=1)
    print("BRIDGE", json.dumps(out)[:800])
except Exception as ex:
    print("BRIDGE-ERROR", type(ex).__name__, str(ex)[:200])
print("DONE")
