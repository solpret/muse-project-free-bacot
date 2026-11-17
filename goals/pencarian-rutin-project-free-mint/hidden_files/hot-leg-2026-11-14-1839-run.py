#!/usr/bin/env python3
"""free-mint-hot-leg run 2026-11-14 18:39 WIB.
Legs (1) Sourcify feed, (2) Boltbook en+zh, (3) shape-check new feed contracts,
bridge read-only. Read-only except hot-leg-seen.json update + run outputs.
Target < 2 min; skip stalled legs."""
import json, re, time, urllib.request, concurrent.futures

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
TAG = "2026-11-14-1839"
NOW = "2026-11-14T18:39+07:00"
t0 = time.time()
out = {"run": "free-mint-hot-leg " + NOW, "started_wib": NOW}

def get(url, timeout=25, ua="free-mint-hot-leg/1839"):
    req = urllib.request.Request(url, headers={"User-Agent": ua})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()

# --- seen ---
seen = json.load(open(BASE + "hot-leg-seen.json"))
seen_n_prev = len(seen)

# --- (1) Sourcify feed ---
try:
    raw = get("https://sourcify.dev/server/v2/contracts/56?limit=20&sort=desc", timeout=25)
    feed = json.loads(raw.decode())
    json.dump(feed, open(BASE + "run-" + TAG + "-sourcify.json", "w"), indent=1)
    results = feed.get("results", [])
    feed_addrs = [r["address"] for r in results]
    new_feed = [a for a in feed_addrs if a not in seen]
    out["sourcify_feed"] = {"total": len(results), "new": len(new_feed),
                            "new_contracts": new_feed,
                            "top": feed_addrs[0] if feed_addrs else None,
                            "top_verifiedAt": results[0].get("verifiedAt") if results else None}
except Exception as e:
    out["sourcify_feed"] = {"error": f"{type(e).__name__}: {str(e)[:200]}"}
    feed_addrs, new_feed = [], []

# --- (2) Boltbook en + zh ---
ADDR_RE = re.compile(r"0x[0-9a-fA-F]{40}")
for lang, fn in (("en", "https://boltbook.fun/"), ("zh", "https://boltbook.fun/?lang=zh")):
    key = "boltbook_" + lang
    try:
        html = get(fn, timeout=25).decode(errors="replace")
        open(BASE + "run-" + TAG + "-boltbook-" + lang + ".html", "w").write(html)
        addrs = sorted(set(ADDR_RE.findall(html)))
        newb = [a for a in addrs if a not in seen]
        out[key] = {"bytes": len(html), "full_address_contracts": len(addrs), "new": len(newb),
                    "new_contracts": newb}
    except Exception as e:
        out[key] = {"error": f"{type(e).__name__}: {str(e)[:200]}"}

# --- (3) shape-check new feed contracts ---
FREE_VIEWS = {"freeSharesRemaining","freeClaimed","freeFor","freeLeft","freeUsed","freeAvailable",
              "freeSharePoolExhausted","freeSharesClaimed","freeMinted","freeCardsRemaining"}
def shape(addr):
    url = f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi"
    try:
        meta = json.loads(get(url, timeout=20).decode())
        abi = meta.get("abi", [])
        names = {e["name"] for e in abi if e.get("type") == "function"}
        has_mint = any(n.lower().startswith("mint") for n in names)
        has_quote = bool(names & {"quote","cost","getQuote","mintCost","price","getPrice"})
        free_views = sorted(names & FREE_VIEWS)
        agent_ref = bool(names & {"agentId","agentRegistry","registry","getAgentId","agentGate","AgentGate"})
        is_token = bool(names & {"name","symbol","decimals","totalSupply"})
        mintfree = "mintFree" in names
        s1 = has_mint and has_quote and bool(free_views) and agent_ref
        s2 = is_token and mintfree and bool(names & {"freeClaimed","freeMinted"}) and bool(names & {"FREE_SLOTS","FREE_SUPPLY"}) and agent_ref
        return {"address": addr, "verifiedAt": None, "S1": s1, "S2": s2, "has_mint": has_mint,
                "has_quote": has_quote, "free_views": free_views, "agent_ref": agent_ref,
                "is_token": is_token, "n_fns": len(names), "status": "checked"}
    except Exception as ex:
        return {"address": addr, "error": f"{type(ex).__name__}: {str(ex)[:150]}"}

shapes = []
if new_feed:
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as ex:
        shapes = list(ex.map(shape, new_feed))
    # attach verifiedAt
    va = {r["address"]: r.get("verifiedAt") for r in (feed.get("results", []) if isinstance(feed, dict) else [])}
    for s in shapes:
        s["verifiedAt"] = va.get(s["address"])
out["shape_check"] = shapes
out["shape_hits"] = [s["address"] for s in shapes if s.get("S1") or s.get("S2")]

# --- bridge (read-only) ---
try:
    bridge = json.load(open(BASE + "scan-bridge.json"))
    cons = bridge.get("contracts", {})
    snap = set()
    try:
        snapj = json.load(open(BASE + "onchain-snapshot.json"))
        for sec in ("contracts", "track_c", "pending_claims"):
            for k in snapj.get(sec, {}):
                snap.add(k)
    except Exception:
        pass
    not_in_snap = [a for a in cons if a not in snap]
    out["bridge"] = {"contracts": len(cons),
                     "same_owner_discarded": sum(1 for c in cons.values() if c.get("same_owner_discarded")),
                     "not_in_snapshot": len(not_in_snap),
                     "not_in_snapshot_list": not_in_snap[:10]}
except Exception as e:
    out["bridge"] = {"error": f"{type(e).__name__}: {str(e)[:200]}"}

# --- update seen with new contracts (feed + boltbook) ---
added = 0
for a in new_feed:
    if a not in seen:
        seen[a] = {"first_seen_wib": NOW, "source": "sourcify-feed",
                   "status": "checked-not-sale-shape" if not any(s.get("address") == a and (s.get("S1") or s.get("S2")) for s in shapes) else "SALE-SHAPE",
                   "note": str([s for s in shapes if s.get("address") == a])[:300]}
        added += 1
for lang in ("en", "zh"):
    for a in out.get("boltbook_" + lang, {}).get("new_contracts", []):
        if a not in seen:
            seen[a] = {"first_seen_wib": NOW, "source": "boltbook-" + lang, "status": "seen"}
            added += 1
if added:
    json.dump(seen, open(BASE + "hot-leg-seen.json", "w"))
out["seen_n"] = len(seen)
out["seen_n_prev"] = seen_n_prev
out["elapsed_s"] = round(time.time() - t0, 1)
json.dump(out, open(BASE + "hot-leg-run-" + TAG + ".json", "w"), indent=1)
print(json.dumps(out, indent=1))
