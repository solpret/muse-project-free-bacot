#!/usr/bin/env python3
"""FREE BACOT run 1931 (2026-11-06 19:31 WIB) — Subagent B: Sourcify feed poll + track-C sale-shape check (S1/S2). Read-only."""
import json, urllib.request, concurrent.futures, time, os

WD = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
REG = "0x60b9262456de011f7d15a54cdd8c48baaa8b022f"
FEED_URL = "https://sourcify.dev/server/v2/contracts/56?limit=20&sort=desc"
FREE_VIEWS = ["freeSharesRemaining", "freeClaimed", "freeFor", "freeLeft", "freeUsed",
              "freeAvailable", "freeSharePoolExhausted", "freeSharesClaimed",
              "freeMinted", "freeMintedCount", "freeCardsRemaining"]
QUOTE_NAMES = {"quote", "cost", "getQuote", "mintCost", "price", "getPrice", "PRICE", "quoteSale",
               "quotePurchase", "quoteLiquidityTokens", "quoteOpeningTokens"}
GATE_NAMES = {"isAgent", "agentRegistry", "agentGate", "AgentGate", "registry", "getAgentId", "agentId"}
TOKEN_NAMES = {"name", "symbol", "decimals", "totalSupply"}

def http_json(url, timeout=20):
    req = urllib.request.Request(url, headers={"User-Agent": "free-bacot/1931"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode())

# 1. Poll feed, retry once on transient failure
feed = None
feed_error = None
for attempt in (1, 2):
    try:
        feed = http_json(FEED_URL, timeout=25)
        break
    except Exception as ex:
        feed_error = f"{type(ex).__name__}: {str(ex)[:150]}"
        time.sleep(3)
if feed is None:
    json.dump({"run": "1931", "feed_error": feed_error, "feed_count": 0, "results": []},
              open(os.path.join(WD, "run-2026-11-06-1931-sourcify-shape.json"), "w"), indent=1)
    json.dump({"run": "1931", "feed_error": feed_error, "results": []},
              open(os.path.join(WD, "run-2026-11-06-1931-sourcify-feed.json"), "w"), indent=1)
    print("FEED FAILED:", feed_error)
    raise SystemExit(1)

entries = feed.get("results", [])
json.dump({"run": "1931", "run_wib": "2026-11-06 19:31 WIB", "feed_url": FEED_URL,
           "feed_count": len(entries), "results": entries},
          open(os.path.join(WD, "run-2026-11-06-1931-sourcify-feed.json"), "w"), indent=1)
print("FEED OK:", len(entries), "entries;",
      "range", entries[-1]["verifiedAt"], "->", entries[0]["verifiedAt"] if entries else "-")

# 2. Prior checked addresses (carry-over)
prior = {}
for f in ("run-2026-11-06-1929-sourcify-shape.json", "run-2026-11-06-1901-sourcify-shape.json"):
    try:
        d = json.load(open(os.path.join(WD, f)))
        for it in d.get("results", []):
            prior[it["address"].lower()] = (f, it)
    except Exception as ex:
        print("prior load fail", f, ex)

def shape_check(addr, verified_at, match):
    try:
        meta = http_json(f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi", timeout=20)
        abi = meta.get("abi", [])
    except Exception as ex:
        return {"address": addr, "verifiedAt": verified_at, "match": match,
                "sourcify": "fetch_error", "error": f"{type(ex).__name__}: {str(ex)[:120]}",
                "S1": False, "S2": False, "verdict": "fetch_error"}
    names = [e["name"] for e in abi if e.get("type") == "function"]
    name_set = set(names)
    mint_fns = sorted({n for n in names if "mint" in n.lower()})
    quote_fns = sorted(name_set & QUOTE_NAMES)
    free_views = sorted(name_set & set(FREE_VIEWS))
    gate_fns = sorted(name_set & GATE_NAMES)
    token_fns = sorted(name_set & TOKEN_NAMES)
    # registry address in ABI text (constants rarely in ABI; also try source grep for near-passes below)
    reg_in_abi = REG in json.dumps(abi).lower()
    has_mint_fn = any(n.lower().startswith("mint") and n not in ("mintedBy", "mintedCount", "totalMinted", "totalSpotsMinted", "everMinted") for n in names) or "mint" in name_set
    has_mint_any = bool(mint_fns)
    has_quote = bool(quote_fns)
    has_free = bool(free_views)
    has_gate = bool(gate_fns) or reg_in_abi
    s1 = has_mint_fn and has_quote and has_free and has_gate
    mintfree_noarg = any(e.get("name") == "mintFree" and len(e.get("inputs", [])) == 0
                         for e in abi if e.get("type") == "function")
    s2 = (len(token_fns) == 4 and mintfree_noarg
          and bool(name_set & {"freeClaimed", "freeMinted"})
          and bool(name_set & {"FREE_SLOTS", "FREE_SUPPLY"}) and has_gate)
    verdict = "pass_S1" if s1 else ("pass_S2" if s2 else "not-sale-shape")
    near = None
    if not s1 and not s2:
        if has_mint_fn and has_quote and not has_free:
            near = "near-pass: sale template (mint+quote) but NO free-share view"
        elif mintfree_noarg and has_free and not has_gate:
            near = "near-pass: mintFree + free views but NO AgentGate/registry ref"
        elif has_mint_fn and has_quote and has_free and not has_gate:
            near = "near-pass: mint+quote+free view but NO AgentGate/registry ref"
        elif mintfree_noarg and has_free:
            near = "near-pass: mintFree + free views, missing S2 element(s)"
    res = {"address": addr, "verifiedAt": verified_at, "match": match, "sourcify": "verified",
           "functions": len(names), "mint_fns": mint_fns, "quote_fns": quote_fns,
           "free_views": free_views, "gate_fns": gate_fns, "token_fns": token_fns,
           "registry_in_abi": reg_in_abi, "S1": s1, "S2": s2,
           "verdict": verdict, "near_pass_note": near}
    return res

fresh = [e for e in entries if e["address"].lower() not in prior]
carried = [e for e in entries if e["address"].lower() in prior]
print("fresh:", len(fresh), "carried-over:", len(carried))
for e in carried:
    print("  carried:", e["address"], "from", prior[e["address"].lower()][0])

results = []
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as ex:
    futs = {ex.submit(shape_check, e["address"], e["verifiedAt"], e.get("match")): e for e in fresh}
    for fut in concurrent.futures.as_completed(futs):
        results.append(fut.result())
results.sort(key=lambda r: r["verifiedAt"], reverse=True)

# carried-over entries: reuse prior verdict, mark carried
for e in carried:
    pf, pit = prior[e["address"].lower()]
    cp = dict(pit)
    cp["carried_over_from"] = pf
    cp["verifiedAt"] = e["verifiedAt"]
    results.append(cp)
results.sort(key=lambda r: r["verifiedAt"], reverse=True)

# Source grep for registry address on near-passes (S1/S2 candidates missing only gate)
for r in results:
    if r.get("near_pass_note") and "NO AgentGate" in r["near_pass_note"]:
        try:
            src = http_json(f"https://sourcify.dev/server/v2/contract/56/{r['address']}?fields=stdJson", timeout=20)
            blob = json.dumps(src).lower()
            if REG in blob:
                r["registry_in_source"] = True
                r["gate_fns"] = r.get("gate_fns", []) + ["registry-address-in-source"]
                r["near_pass_note"] += " | UPDATED: registry address found in verified source -> gate present"
                # recompute S1/S2 with gate present
                has_mint_fn = bool(r["mint_fns"]) and any(n.lower().startswith("mint") for n in r["mint_fns"])
                if has_mint_fn and r["quote_fns"] and r["free_views"]:
                    r["S1"] = True; r["verdict"] = "pass_S1"; r["near_pass_note"] = None
            else:
                r["registry_in_source"] = False
        except Exception as ex:
            r["registry_source_check"] = f"error: {type(ex).__name__}: {str(ex)[:80]}"

s1 = [r for r in results if r.get("S1")]
s2 = [r for r in results if r.get("S2")]
near = [r for r in results if r.get("near_pass_note")]
out = {"run": "1931", "run_wib": "2026-11-06 19:31 WIB", "route": "5a sourcify recently-verified",
       "feed_file": "run-2026-11-06-1931-sourcify-feed.json",
       "feed_count": len(entries),
       "feed_verified_range_utc": f"{entries[-1]['verifiedAt']} -> {entries[0]['verifiedAt']}" if entries else None,
       "fresh_checked": len(fresh), "carried_over": len(carried),
       "strict_passes_S1": [r["address"] for r in s1],
       "strict_passes_S2": [r["address"] for r in s2],
       "near_passes": [{"address": r["address"], "note": r["near_pass_note"]} for r in near],
       "results": results}
json.dump(out, open(os.path.join(WD, "run-2026-11-06-1931-sourcify-shape.json"), "w"), indent=1)
print("S1 passes:", [r["address"] for r in s1])
print("S2 passes:", [r["address"] for r in s2])
print("near-passes:", [(r["address"], r["near_pass_note"]) for r in near])
print("sale-template (mint+quote, no free view):",
      [r["address"] for r in results if r.get("mint_fns") and r.get("quote_fns") and not r.get("free_views")])
