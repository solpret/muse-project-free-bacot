#!/usr/bin/env python3
"""Leg-1 retry for hot-leg run 2026-11-09 21:19 WIB.
Root cause: Sourcify feed response shape is now {"results": [...]} (verified live
21:29 WIB); the run script only handled a bare list or {"contracts": [...]} so
feed_n read 0 with no error. This retry parses all three shapes, shape-checks
only addresses new vs hot-leg-seen.json, records them there, and probes any
new sale shape (leg 3). Read-only except hot-leg-seen.json + this log."""
import json, time, datetime, urllib.request, subprocess
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TS = "2026-11-09-2119-leg1retry"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
REGISTRY = "0x60b9262456de011f7d15a54cdd8c48baa8b022f"
T0 = time.time()
WIB = datetime.timezone(datetime.timedelta(hours=7))

def wib_now():
    return datetime.datetime.now(WIB).isoformat(timespec="seconds")

seen = json.load(open(f"{BASE}/hot-leg-seen.json"))
seen_low = {k.lower(): k for k in seen}
out = {"run": "free-mint-hot-leg 2026-11-09 21:19 leg1-retry", "started_wib": wib_now()}

def http_get(url, timeout=25):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.status, r.read()

FREE_VIEWS = ["freeSharesRemaining", "freeClaimed", "freeFor", "freeLeft", "freeUsed",
              "freeAvailable", "freeSharePoolExhausted", "freeSharesClaimed", "freeMinted"]

def shape_check(addr):
    try:
        st, body = http_get(f"https://sourcify.dev/server/v2/contracts/56/{addr}", timeout=20)
        d = json.loads(body)
        abi = d.get("abi") or (d.get("contract", {}) or {}).get("abi") or []
        if isinstance(abi, str):
            abi = json.loads(abi)
        fns = {}
        for e in abi:
            if isinstance(e, dict) and e.get("type") == "function":
                fns.setdefault(e.get("name"), []).append(e)
        names = set(fns)
        has_mint = any(n.startswith("mint") for n in names)
        has_quote = bool(names & {"quote", "cost", "priceFor", "getQuote"})
        free_hits = sorted(names & set(FREE_VIEWS))
        src = json.dumps(d)
        has_agent = ("0x60b9262456de011f7d15a54cdd8c48baa8b022f" in src.lower()
                     or "agentgate" in src.lower() or "agentidregistry" in src.lower()
                     or "AgentGate" in src or "AGENT_ID_REGISTRY" in src)
        s1 = has_mint and has_quote and bool(free_hits) and has_agent
        is_token = bool(names & {"name", "symbol", "decimals", "totalSupply"})
        s2 = is_token and ("mintFree" in names) and bool(names & {"freeClaimed", "freeMinted"}) \
             and bool(names & {"FREE_SLOTS", "FREE_SUPPLY", "FREE_AMOUNT"}) and has_agent
        return {"s1": s1, "s2": s2, "mint": has_mint, "quote": has_quote,
                "free": free_hits, "agent": has_agent, "token": is_token}
    except Exception as e:
        return {"error": f"{type(e).__name__}: {e}"}

try:
    st, body = http_get("https://sourcify.dev/server/v2/contracts/56?limit=20&sort=desc", timeout=25)
    feed = json.loads(body)
    if isinstance(feed, list):
        items = feed
    elif isinstance(feed, dict):
        items = feed.get("results") or feed.get("contracts") or []
    else:
        items = []
    addrs, verified = [], []
    for item in items:
        a = item.get("address") if isinstance(item, dict) else None
        if a:
            addrs.append(a)
            verified.append(item.get("verifiedAt"))
    out["feed"] = {"status": st, "n": len(addrs), "top_keys": list(feed.keys()) if isinstance(feed, dict) else "list",
                   "newest_verifiedAt": verified[0] if verified else None}
except Exception as e:
    addrs = []
    out["feed"] = {"error": f"{type(e).__name__}: {e}"}

EXCLUDED = {"0x827e83e49bd7e15b67efa0e90fc25f17b8d96124",
            "0x8b47354e7b76b1970a0d06365c8244a810d37493"}
new_addrs = [a for a in addrs if a.lower() not in seen_low and a.lower() != REGISTRY.lower()
             and a.lower() not in EXCLUDED]
leg1 = {"feed_n": len(addrs), "new": new_addrs, "shapes": {}}
sale_new = []
for a in new_addrs:
    sc = shape_check(a)
    leg1["shapes"][a] = sc
    if sc.get("s1") or sc.get("s2"):
        sale_new.append(a)
        seen[a] = {"first_seen_wib": wib_now(),
                   "note": f"SALE SHAPE {'S1' if sc.get('s1') else 'S2'} PASS from Sourcify feed (leg1 retry): {sc}",
                   "source": "sourcify-feed", "status": "sale-shape-new"}
    elif "error" in sc:
        seen[a] = {"first_seen_wib": wib_now(), "note": f"ABI fetch error: {sc['error']}",
                   "source": "sourcify-feed", "status": "checked-abi-unavailable"}
    else:
        seen[a] = {"first_seen_wib": wib_now(),
                   "note": f"S1={sc.get('s1')} S2={sc.get('s2')} mint={sc.get('mint')} quote={sc.get('quote')} free={sc.get('free')} agent={sc.get('agent')} token={sc.get('token')}",
                   "source": "sourcify-feed", "status": "checked-not-sale-shape"}
leg1["seen_total"] = len(seen)
leg1["sale_shapes"] = sale_new
out["leg1"] = leg1
json.dump(seen, open(f"{BASE}/hot-leg-seen.json", "w"), indent=1)

# leg 3 probe only if a new sale shape appeared
leg3 = {"new_sale_shapes": sale_new, "probes": {}}
if sale_new:
    _EPS3 = ["https://bsc-dataseed.binance.org/", "https://bsc.publicnode.com"]
    def _sel3(s):
        k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
    def _call3(addr, data):
        payload = {"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                   "params": [{"to": addr, "data": data}, "latest"]}
        for ep in _EPS3:
            try:
                r = subprocess.run(["curl", "-sL", "--max-time", "10", "-X", "POST", ep,
                                    "-H", "Content-Type: application/json", "-d", json.dumps(payload)],
                                   capture_output=True, text=True, timeout=15)
                d = json.loads(r.stdout)
                if isinstance(d, dict) and "result" in d and d["result"] not in (None, "0x"):
                    return int(d["result"], 16)
                return None
            except Exception:
                continue
        return None
    for a in sale_new:
        p = {}
        for fn in ("freeClaimed()", "freeMinted()", "FREE_SUPPLY()", "FREE_SLOTS()",
                   "freeLeft()", "freeSharesRemaining()"):
            p[fn[:-2]] = _call3(a, _sel3(fn))
        p["freeClaimed_user"] = _call3(a, _sel3("freeClaimed(address)") + USER[2:].lower().rjust(64, "0"))
        p["quote_user1"] = _call3(a, _sel3("quote(address,uint256)") + USER[2:].lower().rjust(64, "0") + format(1, "064x"))
        p["age"] = "unverified-no-logs-source"
        leg3["probes"][a] = p
        pool = p.get("freeClaimed") or p.get("freeMinted")
        cap = p.get("FREE_SUPPLY") or p.get("FREE_SLOTS")
        slot_open = (p.get("freeClaimed_user") == 0) or (p.get("quote_user1") == 0)
        if pool is not None and cap and pool < cap and slot_open:
            seen[a]["status"] = "sale-shape-age-unverified-watchlist"
            seen[a]["note"] += f" | leg3 pool {pool}/{cap}, user slot open, AGE UNVERIFIED (no logs source) -> watchlist-only, never a lead."
        elif pool is not None and cap and pool >= cap:
            seen[a]["status"] = "sale-shape-sold-out"
            seen[a]["note"] += f" | leg3 pool {pool}/{cap} SOLD OUT."
        else:
            seen[a]["status"] = "sale-shape-pool-unverified"
            seen[a]["note"] += " | leg3 pool/slot reads inconclusive (views absent or RPC fail)."
        json.dump(seen, open(f"{BASE}/hot-leg-seen.json", "w"), indent=1)
out["leg3"] = leg3
out["duration_s"] = round(time.time() - T0, 1)
json.dump(out, open(f"{BASE}/hot-leg-run-{TS}.json", "w"), indent=1)
print(json.dumps(out, indent=1))
