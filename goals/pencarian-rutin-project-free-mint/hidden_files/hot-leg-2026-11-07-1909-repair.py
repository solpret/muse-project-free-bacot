#!/usr/bin/env python3
"""Repair for hot-leg 2026-11-07 19:09: re-shape-check 17 feed contracts with ?fields=abi
(correct Sourcify endpoint) + retry Boltbook.fun leg via curl. Updates hot-leg-seen.json
with REAL results; un-fetchable ABIs marked shape-check-failed (retry next run)."""
import json, re, subprocess, sys
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TS = "2026-11-07-1909"
REGISTRY = "0x60b9262456de011f7d15a54cdd8c48baaa8b022f"
EXCLUDED = {"0x827e83e49bd7e15b67efa0e90fc25f17b8d96124", "0x8b47354e7b76b1970a0d06365c8244a810d37493"}
FREE_VIEWS = ["freeSharesRemaining", "freeClaimed", "freeFor", "freeLeft", "freeUsed",
              "freeAvailable", "freeSharePoolExhausted", "freeSharesClaimed", "freeMinted"]

def curl(url, timeout=20):
    for _ in range(2):
        try:
            r = subprocess.run(["curl", "-sS", "--max-time", str(timeout), "-A", "Mozilla/5.0", url],
                               capture_output=True, text=True, timeout=timeout + 5)
            if r.returncode == 0 and r.stdout.strip():
                return r.stdout
        except Exception:
            pass
    return None

def shape_check(addr):
    abi = None; match = None
    raw = curl(f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi")
    if raw:
        try:
            d = json.loads(raw)
            match = d.get("match")
            abi = d.get("abi")
        except Exception:
            pass
    if abi is None:
        for kind in ("full_match", "partial_match"):
            raw = curl(f"https://repo.sourcify.dev/contracts/{kind}/56/{addr}/metadata.json")
            if raw:
                try:
                    m = json.loads(raw)
                    abi = m.get("output", {}).get("abi")
                    if abi:
                        match = kind; break
                except Exception:
                    continue
    if not abi:
        return {"match": match, "error": "no-abi-after-retry"}
    fns = [f.get("name") for f in abi if f.get("type") == "function" and f.get("name")]
    names = set(fns)
    has_mint = any(n.startswith("mint") for n in names)
    has_quote = any(("quote" in n.lower() or "cost" in n.lower() or "price" in n.lower()) for n in names)
    free = [v for v in FREE_VIEWS if v in names]
    rawj = json.dumps(abi).lower()
    agent = REGISTRY.lower() in rawj or "agentgate" in rawj or "agentregistry" in rawj or "agent_id" in rawj
    tokenish = bool({"name", "symbol", "decimals", "totalSupply"} <= names)
    s1 = has_mint and has_quote and bool(free) and agent
    s2 = tokenish and "mintFree" in names and ("freeClaimed" in names or "freeMinted" in names) and \
        bool({"FREE_SLOTS", "FREE_SUPPLY", "FREE_AMOUNT"} & names) and agent
    return {"match": match, "fns": len(fns), "fn_names": sorted(names), "mint": has_mint,
            "quote": has_quote, "free_views": free, "registry": agent, "S1": s1, "S2": s2}

seen = json.load(open(f"{BASE}/hot-leg-seen.json"))
run = json.load(open(f"{BASE}/hot-leg-run-{TS}.json"))
feed = json.load(open(f"{BASE}/hot-leg-{TS}-feed.json"))
addrs = [r["address"] for r in feed.get("results", [])]
seen_l = {k.lower() for k in seen}
new = [a for a in addrs if a.lower() not in seen_l or seen.get(a, {}).get("status") == "checked-not-sale-shape"
       and "S1=None" in str(seen.get(a, {}).get("note", ""))]
# Only re-check the 17 recorded with the failed note in this run
new = [a for a in addrs if a in seen and "S1=None" in str(seen[a].get("note", ""))]
print("re-checking", len(new), flush=True)
shapes = {}
for a in new:
    sc = shape_check(a)
    shapes[a] = sc
    if "error" in sc:
        seen[a] = {"first_seen_wib": "2026-11-07T19:09:38+07:00",
                   "note": f"shape-check FAILED (ABI unfetchable after retry): match={sc.get('match')} - retry next run, NOT verified not-sale-shape",
                   "source": "sourcify-feed", "status": "shape-check-failed"}
        print(a[:12], "FAILED", sc.get("match"), flush=True)
    else:
        note = (f"S1={sc['S1']} S2={sc['S2']} mint={sc['mint']} quote={sc['quote']} "
                f"free={sc['free_views']} agent={sc['registry']} token=fns{sc['fns']}")
        seen[a] = {"first_seen_wib": "2026-11-07T19:09:38+07:00", "note": note,
                   "source": "sourcify-feed",
                   "status": "sale-shape" if (sc["S1"] or sc["S2"]) else "checked-not-sale-shape"}
        print(a[:12], f"S1={sc['S1']} S2={sc['S2']} fns={sc['fns']} free={sc['free_views']} agent={sc['registry']}", flush=True)
json.dump(shapes, open(f"{BASE}/hot-leg-{TS}-sourcify-shape.json", "w"), indent=1)

# ---- Leg 2 retry: Boltbook.fun via curl ----
KW = ["free share", "first share free", "1 free share", "free mint share",
      "\u514d\u8d39\u4efd\u989d", "\u9996\u4e2a\u514d\u8d39", "\u514d\u8d39\u94f8\u9020", "\u514d\u8d39mint"]
bb = {}
try:
    pages = {}
    for lang, url in (("en", "https://boltbook.fun/"), ("zh", "https://boltbook.fun/?lang=zh")):
        html = curl(url, timeout=25)
        if html:
            pages[lang] = html
            open(f"{BASE}/hot-leg-{TS}-boltbook-fun-{lang}.html", "w").write(html)
    if pages:
        all_addrs = set()
        for html in pages.values():
            all_addrs |= set(re.findall(r"0x[0-9a-fA-F]{40}", html))
        kw_hits = {k: sum(p.lower().count(k.lower()) for p in pages.values()) for k in KW}
        new_bb = [a for a in sorted(all_addrs)
                  if a.lower() not in {k.lower() for k in seen} and a.lower() not in EXCLUDED]
        shapes_bb = {}
        for a in new_bb:
            sc = shape_check(a)
            shapes_bb[a] = sc
            if "error" in sc:
                seen[a] = {"first_seen_wib": "2026-11-07T19:09:38+07:00",
                           "note": "shape-check FAILED (ABI unfetchable) - retry next run",
                           "source": "boltbook-fun", "status": "shape-check-failed"}
            else:
                note = (f"S1={sc['S1']} S2={sc['S2']} mint={sc['mint']} quote={sc['quote']} "
                        f"free={sc['free_views']} agent={sc['registry']}")
                seen[a] = {"first_seen_wib": "2026-11-07T19:09:38+07:00", "note": note,
                           "source": "boltbook-fun",
                           "status": "sale-shape" if (sc["S1"] or sc["S2"]) else "checked-not-sale-shape"}
        bb = {"status": "COMPLETED-via-curl-retry", "addrs": len(all_addrs), "new": new_bb,
              "kw_hits": kw_hits, "shapes": {a: (s.get("S1"), s.get("S2")) for a, s in shapes_bb.items()}}
        json.dump({"addrs": sorted(all_addrs), "kw": kw_hits, "new": new_bb, "shapes": shapes_bb},
                  open(f"{BASE}/hot-leg-{TS}-boltbook-shape.json", "w"), indent=1)
        json.dump(new_bb, open(f"{BASE}/hot-leg-{TS}-boltbook-new.json", "w"))
        print("boltbook OK:", len(all_addrs), "addrs,", len(new_bb), "new, kw:", kw_hits, flush=True)
    else:
        bb = {"status": "FAILED-both-fetches", "error": "curl returned empty for EN+ZH", "skipped": True}
except Exception as e:
    bb = {"status": "FAILED", "error": str(e), "skipped": True}

sale_new = [a for a, s in shapes.items() if s.get("S1") or s.get("S2")]
run["leg1_feed"] = {"n": len(addrs), "new": new,
    "shapes": "; ".join(f"{a[:10]} S1={s.get('S1')} S2={s.get('S2')} fns={s.get('fns')} free={s.get('free_views')} agent={s.get('registry')}" for a, s in shapes.items()),
    "note": "CORRECTED after repair: first pass used v2 endpoint without ?fields=abi (no ABI returned); re-checked with ?fields=abi + repo fallback."}
run["leg2_boltbook"] = bb
run["leg3_new_contracts"] = f"{len(sale_new)} S1/S2 new: {sale_new}" if sale_new else "No S1/S2 hits from feed or Boltbook.fun - no leg-3 on-chain verification needed."
run["seen_total"] = len(seen)
json.dump(seen, open(f"{BASE}/hot-leg-seen.json", "w"), indent=1)
json.dump(run, open(f"{BASE}/hot-leg-run-{TS}.json", "w"), indent=1)
print(json.dumps({"leg1": run["leg1_feed"], "leg2": bb, "leg3": run["leg3_new_contracts"], "seen_total": len(seen)}, indent=1)[:4000])
