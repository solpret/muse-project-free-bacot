#!/usr/bin/env python3
"""curl-based retry of the 18 shape-checks that failed in the v2-route
correction pass (urllib IncompleteRead on large metadata + 2 RemoteDisconnected).
Route: GET /v2/contract/56/{addr}?fields=metadata. Records real shape results
in hot-leg-seen.json; probes (leg 3) any new sale shape."""
import json, time, datetime, subprocess
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
T0 = time.time()
WIB = datetime.timezone(datetime.timedelta(hours=7))

def wib_now():
    return datetime.datetime.now(WIB).isoformat(timespec="seconds")

seen = json.load(open(f"{BASE}/hot-leg-seen.json"))
fix = json.load(open(f"{BASE}/hot-leg-run-2026-11-09-2119-shapefix.json"))
targets = [a for a, s in fix["results"].items()
           if "error" in s and ("IncompleteRead" in s["error"] or "RemoteDisconnected" in s["error"])]
FREE_VIEWS = ["freeSharesRemaining", "freeClaimed", "freeFor", "freeLeft", "freeUsed",
              "freeAvailable", "freeSharePoolExhausted", "freeSharesClaimed", "freeMinted"]

def shape_check_curl(addr):
    try:
        r = subprocess.run(["curl", "-sL", "--max-time", "25", "-A", "Mozilla/5.0",
                            f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=metadata"],
                           capture_output=True, text=True, timeout=30)
        if r.returncode != 0:
            return {"error": f"curl rc={r.returncode}"}
        d = json.loads(r.stdout)
        if "metadata" not in d:
            return {"error": f"no metadata field (keys={list(d.keys())[:6]})"}
        meta = d.get("metadata") or {}
        abi = (meta.get("output") or {}).get("abi") or []
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
                "free": free_hits, "agent": has_agent, "token": is_token,
                "route": "v2/contract?fields=metadata via curl"}
    except Exception as e:
        return {"error": f"{type(e).__name__}: {e}"}

out = {"run": "hot-leg 2026-11-09 21:19 shape-check curl retry",
       "started_wib": wib_now(), "targets": len(targets), "results": {}, "sale_shapes": []}
sale_new = []
for a in targets:
    sc = shape_check_curl(a)
    out["results"][a] = sc
    prev_src = seen[a].get("source", "sourcify-feed") if isinstance(seen.get(a), dict) else "sourcify-feed"
    prev_first = seen[a].get("first_seen_wib", wib_now()) if isinstance(seen.get(a), dict) else wib_now()
    if sc.get("s1") or sc.get("s2"):
        sale_new.append(a)
        seen[a] = {"first_seen_wib": prev_first,
                   "note": f"SALE SHAPE {'S1' if sc.get('s1') else 'S2'} PASS (v2 curl retry): {sc}",
                   "source": prev_src, "status": "sale-shape-new"}
    elif "error" in sc:
        seen[a]["note"] = f"ABI fetch error (v2 curl retry): {sc['error']}"
        seen[a]["status"] = "checked-abi-unavailable"
    else:
        seen[a] = {"first_seen_wib": prev_first,
                   "note": f"S1={sc.get('s1')} S2={sc.get('s2')} mint={sc.get('mint')} quote={sc.get('quote')} free={sc.get('free')} agent={sc.get('agent')} token={sc.get('token')} (v2 curl retry)",
                   "source": prev_src, "status": "checked-not-sale-shape"}
    json.dump(seen, open(f"{BASE}/hot-leg-seen.json", "w"), indent=1)
    time.sleep(0.3)

out["sale_shapes"] = sale_new
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
json.dump(out, open(f"{BASE}/hot-leg-run-2026-11-09-2119-shapefix-curl.json", "w"), indent=1)
print(json.dumps({"targets": len(targets), "sale_shapes": sale_new,
                  "errors": [a for a, s in out["results"].items() if "error" in s],
                  "duration_s": out["duration_s"]}, indent=1))
for a, s in out["results"].items():
    print(a, s)
