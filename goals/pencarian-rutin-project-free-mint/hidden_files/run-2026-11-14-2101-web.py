#!/usr/bin/env python3
"""free-mint-search run 2026-11-14 21:01 WIB — web legs.
(1) Sourcify recently-verified feed, (2) Boltbook en+zh (curl),
(3) shape-check new feed contracts S1/S2, (4) Ankr pre-flight (fast-fail expected),
(5) scan-bridge read-only.
Read-only except run output files + hot-leg-seen.json additions for newly seen feed contracts.
No preview/mint. Adapted from hot-leg-2026-11-14-2054-run.py."""
import json, re, subprocess, time, urllib.request, concurrent.futures, sys

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
TAG = "2026-11-14-2101"
NOW = "2026-11-14T21:01+07:00"
t0 = time.time()
out = {"run": "free-mint-search " + NOW, "started_wib": NOW}

def get(url, timeout=25, ua="free-mint-search/2101"):
    req = urllib.request.Request(url, headers={"User-Agent": ua})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()

def curl_get(url, timeout=25):
    r = subprocess.run(["curl", "-sL", "--max-time", str(timeout), url],
                       capture_output=True, timeout=timeout + 10)
    return r.stdout

seen = json.load(open(BASE + "hot-leg-seen.json"))
seen_n_prev = len(seen)
seen_lower = {k.lower() for k in seen}

# --- (1) Sourcify feed ---
feed = None
try:
    raw = get("https://sourcify.dev/server/v2/contracts/56?limit=20&sort=desc", timeout=25)
    feed = json.loads(raw.decode())
    json.dump(feed, open(BASE + "run-" + TAG + "-sourcify.json", "w"), indent=1)
    results = feed.get("results", [])
    feed_addrs = [r["address"] for r in results]
    new_feed = [a for a in feed_addrs if a.lower() not in seen_lower]
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
        html = curl_get(fn, timeout=25).decode(errors="replace")
        open(BASE + "run-" + TAG + "-boltbook-" + lang + ".html", "w").write(html)
        addrs = sorted(set(ADDR_RE.findall(html)))
        newb = [a for a in addrs if a.lower() not in seen_lower]
        out[key] = {"bytes": len(html), "full_address_contracts": len(addrs), "new": len(newb),
                    "new_contracts": newb}
    except Exception as e:
        out[key] = {"error": f"{type(e).__name__}: {str(e)[:200]}"}

# --- (3) shape-check new feed contracts ---
FREE_VIEWS = {"freeSharesRemaining", "freeClaimed", "freeFor", "freeLeft", "freeUsed", "freeAvailable",
              "freeSharePoolExhausted", "freeSharesClaimed", "freeMinted", "freeCardsRemaining"}
def shape(addr):
    url = f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi"
    try:
        meta = json.loads(get(url, timeout=20).decode())
        abi = meta.get("abi", [])
        names = {e["name"] for e in abi if e.get("type") == "function"}
        has_mint = any(n.lower().startswith("mint") for n in names)
        has_quote = bool(names & {"quote", "cost", "getQuote", "mintCost", "price", "getPrice"})
        free_views = sorted(names & FREE_VIEWS)
        agent_ref = bool(names & {"agentId", "agentRegistry", "registry", "getAgentId", "agentGate", "AgentGate"})
        is_token = bool(names & {"name", "symbol", "decimals", "totalSupply"})
        mintfree = "mintFree" in names
        s1 = has_mint and has_quote and bool(free_views) and agent_ref
        s2 = is_token and mintfree and bool(names & {"freeClaimed", "freeMinted"}) and bool(names & {"FREE_SLOTS", "FREE_SUPPLY"}) and agent_ref
        return {"address": addr, "S1": s1, "S2": s2, "has_mint": has_mint,
                "has_quote": has_quote, "free_views": free_views, "agent_ref": agent_ref,
                "is_token": is_token, "n_fns": len(names), "status": "checked"}
    except Exception as ex:
        return {"address": addr, "error": f"{type(ex).__name__}: {str(ex)[:150]}"}

shapes = []
if new_feed:
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as ex:
        shapes = list(ex.map(shape, new_feed))
    va = {r["address"]: r.get("verifiedAt") for r in (feed.get("results", []) if isinstance(feed, dict) else [])}
    for s in shapes:
        s["verifiedAt"] = va.get(s["address"])
out["shape_check"] = shapes
out["shape_hits"] = [s["address"] for s in shapes if s.get("S1") or s.get("S2")]

# --- (4) Ankr pre-flight ---
sys.path.insert(0, BASE)
TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
try:
    import onchain_nft_scan as scan
    req = urllib.request.Request("https://bsc-dataseed.binance.org/",
        data=json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}).encode(),
        headers={"Content-Type": "application/json"})
    head = int(json.load(urllib.request.urlopen(req, timeout=30))["result"], 16)
    out["head"] = head
    try:
        logs, pages = scan.ankr_logs(head - 50, head, [TRANSFER])
        out["preflight"] = {"ok": True, "logs": len(logs), "pages": pages}
    except Exception as e:
        out["preflight"] = {"ok": False, "error": str(e)[:300]}
except Exception as e:
    out["preflight"] = {"ok": False, "error": "head/scan import failed: " + str(e)[:200]}
out["preflight_elapsed_s"] = round(time.time() - t0, 1)

# --- (5) bridge (read-only) ---
def collect_addrs(obj, acc):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(k, str) and re.fullmatch(r"0x[0-9a-fA-F]{40}", k):
                acc.add(k.lower())
            collect_addrs(v, acc)
    elif isinstance(obj, list):
        for v in obj:
            collect_addrs(v, acc)
    elif isinstance(obj, str) and re.fullmatch(r"0x[0-9a-fA-F]{40}", obj):
        acc.add(obj.lower())

try:
    bridge = json.load(open(BASE + "scan-bridge.json"))
    cons = bridge.get("contracts", {})
    snap = set()
    snapj = json.load(open(BASE + "onchain-snapshot.json"))
    collect_addrs(snapj, snap)
    not_in_snap = [a for a in cons if a.lower() not in snap]
    discarded = [a for a, v in cons.items() if isinstance(v, dict) and v.get("same_owner_discarded")]
    out["bridge"] = {"contracts": len(cons), "same_owner_discarded": len(discarded),
                     "not_in_snapshot": len(not_in_snap), "not_in_snapshot_list": not_in_snap}
except Exception as e:
    out["bridge"] = {"error": f"{type(e).__name__}: {str(e)[:200]}"}

# --- record newly seen feed/boltbook contracts in hot-leg-seen.json (checked-not-sale-shape unless shape hit) ---
added = 0
for a in new_feed:
    if a.lower() not in seen_lower:
        s = next((x for x in shapes if x["address"].lower() == a.lower()), {})
        seen[a] = {"first_seen_wib": NOW, "source": "free-mint-search-2101-sourcify",
                   "status": "checked-not-sale-shape" if not (s.get("S1") or s.get("S2")) else "SHAPE-HIT",
                   "note": f"S1={s.get('S1')} S2={s.get('S2')} mint={s.get('has_mint')} quote={s.get('has_quote')} free={s.get('free_views')} agent={s.get('agent_ref')} token={s.get('is_token')}"}
        seen_lower.add(a.lower()); added += 1
for lang in ("en", "zh"):
    for a in out.get("boltbook_" + lang, {}).get("new_contracts", []):
        if a.lower() not in seen_lower:
            seen[a] = {"first_seen_wib": NOW, "source": f"free-mint-search-2101-boltbook-{lang}",
                       "status": "checked-not-sale-shape"}
            seen_lower.add(a.lower()); added += 1
if added:
    json.dump(seen, open(BASE + "hot-leg-seen.json", "w"), indent=1)
out["seen_added"] = added
out["seen_n"] = len(seen)
out["seen_n_prev"] = seen_n_prev
out["elapsed_s"] = round(time.time() - t0, 1)
json.dump(out, open(BASE + "run-" + TAG + "-web.json", "w"), indent=1)
print(json.dumps(out, indent=1))
