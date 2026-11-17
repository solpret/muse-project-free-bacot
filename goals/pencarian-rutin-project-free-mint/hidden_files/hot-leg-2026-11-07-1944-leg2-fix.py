#!/usr/bin/env python3
"""Leg-2补 for hot-leg 2026-11-07 19:44 WIB: Boltbook EN+ZH HTML was fetched and saved
(1944-boltbook-fun-en/zh.html) but leg 2 crashed on legacy non-dict seen entries before
shape-check. Re-run leg 2 from the saved HTML + retry all shape-check-failed entries."""
import json, re, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TS = "2026-11-07-1944"
RUN_WIB = "2026-11-07T19:44:38+07:00"
REGISTRY = "0x60b9262456de011f7d15a54cdd8c48baaa8b022f"
EXCLUDED = {"0x827e83e49bd7e15b67efa0e90fc25f17b8d96124", "0x8b47354e7b76b1970a0d06365c8244a810d37493"}
FREE_VIEWS = ["freeSharesRemaining", "freeClaimed", "freeFor", "freeLeft", "freeUsed",
              "freeAvailable", "freeSharePoolExhausted", "freeSharesClaimed", "freeMinted"]

def curl(url, timeout=12):
    try:
        r = subprocess.run(["curl", "-sS", "-L", "--max-time", str(timeout), "-A", "Mozilla/5.0", url],
                           capture_output=True, text=True, timeout=timeout + 5)
        if r.returncode == 0 and r.stdout.strip():
            return r.stdout
    except Exception:
        pass
    return None

seen = json.load(open(f"{BASE}/hot-leg-seen.json"))
seen_l = {k.lower(): v for k, v in seen.items()}

def shape_check(addr):
    abi = None; match = None
    raw = curl(f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi", timeout=12)
    if raw:
        try:
            d = json.loads(raw); match = d.get("match"); abi = d.get("abi")
        except Exception:
            pass
    if abi is None:
        for kind in ("full_match", "partial_match"):
            raw = curl(f"https://repo.sourcify.dev/contracts/{kind}/56/{addr}/metadata.json", timeout=12)
            if raw:
                try:
                    m = json.loads(raw); abi = m.get("output", {}).get("abi")
                    if abi: match = kind; break
                except Exception:
                    continue
    if not abi:
        return {"match": match, "error": "no-abi"}
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

def record_seen(addr, note, source, status):
    first = seen.get(addr, {}).get("first_seen_wib") if isinstance(seen.get(addr), dict) else None
    seen[addr] = {"first_seen_wib": first or RUN_WIB, "note": note, "source": source, "status": status}

KW = ["free share", "first share free", "1 free share", "free mint share",
      "免费份额", "首个免费", "免费铸造", "免费mint"]
pages = {}
for lang in ("en", "zh"):
    pages[lang] = open(f"{BASE}/hot-leg-{TS}-boltbook-fun-{lang}.html").read()
all_addrs = set()
for html in pages.values():
    all_addrs |= set(re.findall(r"0x[0-9a-fA-F]{40}", html))
kw_hits = {k: sum(p.lower().count(k.lower()) for p in pages.values()) for k in KW}
new_bb = [a for a in sorted(all_addrs) if a.lower() not in seen_l and a.lower() not in EXCLUDED]
retry_bb = [a for a, v in seen.items() if isinstance(v, dict) and v.get("status") == "shape-check-failed"]
check = sorted(set(new_bb) | set(retry_bb))
shapes = {}
if check:
    with ThreadPoolExecutor(max_workers=5) as ex:
        res = list(ex.map(shape_check, check))
    for a, sc in zip(check, res):
        shapes[a] = sc
        if "error" in sc:
            record_seen(a, f"shape-check FAILED (ABI unfetchable): match={sc.get('match')} - retry next run, NOT verified not-sale-shape",
                        "boltbook-fun", "shape-check-failed")
        else:
            note = (f"S1={sc['S1']} S2={sc['S2']} mint={sc['mint']} quote={sc['quote']} "
                    f"free={sc['free_views']} agent={sc['registry']} fns={sc['fns']}")
            record_seen(a, note, "boltbook-fun", "sale-shape" if (sc.get("S1") or sc.get("S2")) else "checked-not-sale-shape")
json.dump({"addrs": sorted(all_addrs), "kw": kw_hits, "new": new_bb, "retry": retry_bb, "shapes": shapes},
          open(f"{BASE}/hot-leg-{TS}-boltbook-shape.json", "w"), indent=1)
json.dump(new_bb, open(f"{BASE}/hot-leg-{TS}-boltbook-new.json", "w"))
json.dump(seen, open(f"{BASE}/hot-leg-seen.json", "w"), indent=1)
sale = [a for a, s in shapes.items() if s.get("S1") or s.get("S2")]
run = json.load(open(f"{BASE}/hot-leg-run-{TS}.json"))
run["leg2_boltbook"] = {"status": "COMPLETED-via-curl (rerun from saved HTML after guard fix)", "addrs": len(all_addrs),
    "new": new_bb, "retry": retry_bb,
    "kw_hits": kw_hits, "shapes": {a: (s.get("S1"), s.get("S2")) for a, s in shapes.items()},
    "sale_shape_new": sale}
run["leg3_new_contracts"] = f"{len(sale)} S1/S2 new: {sale}" if sale else "No S1/S2 hits from feed or Boltbook.fun - no leg-3 on-chain verification needed."
run["seen_total"] = len(seen)
json.dump(run, open(f"{BASE}/hot-leg-run-{TS}.json", "w"), indent=1)
print(json.dumps(run["leg2_boltbook"], indent=1))
print("sale_shape_new:", sale)
print("seen_total:", len(seen))
