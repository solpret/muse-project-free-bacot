#!/usr/bin/env python3
"""Backfill triage run 2026-11-08 ~04:17 WIB, window 132268176-132271220.
Read-only on chain/state inputs; writes only backfill-triage-132268176-132271220.json
and appends newly-checked addresses to track-c-scan-checked.json.
First-seen: 0 (driver merge), so first-seen section is skipped.
Track-C 5c: merged ERC20 lists, mint_count>=10 desc, max 20 NEW, S1/S2 shape
via Sourcify ABI (curl). Transport failure recorded as such, NEVER as
not-sale-shape / not-verified.
"""
import json, subprocess, time

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
REG_HEX = "60b9262456de011f7d15a54cdd8c48baaa8b022f"
FREE_VIEWS = ["freesharesremaining", "freeclaimed", "freefor", "freeleft",
              "freeused", "freeavailable", "freesharepoolexhausted",
              "freesharesclaimed", "freeminted", "free_slots", "free_supply",
              "freeslots", "freesupply"]
QUOTE_WORDS = ["quote", "cost", "price", "getprice", "mintprice", "mintcost"]
CHUNKS = ["backfill-132268176-132270175.json", "backfill-132270176-132271220.json"]
RUN_TAG = "backfill-132268176-132271220-5c"

def fetch_abi_curl(addr):
    url = f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi"
    last = None
    for attempt in (1, 2):
        try:
            r = subprocess.run(["curl", "-s", "-m", "25", "-A", "free-bacot-backfill-triage/1.0", url],
                               capture_output=True, text=True, timeout=40)
            if r.returncode != 0:
                last = f"curl rc={r.returncode} {r.stderr[:120]}"
                time.sleep(2); continue
            return json.loads(r.stdout), None
        except Exception as e:
            last = f"{type(e).__name__}: {e}"
            time.sleep(2)
    return None, last

def abi_of(data):
    if not isinstance(data, dict):
        return None
    abi = data.get("abi")
    if abi is None and isinstance(data.get("stdJson"), dict):
        abi = data["stdJson"].get("abi")
    return abi

def shape_s1_s2(abi_list):
    fns = [e for e in abi_list if isinstance(e, dict) and e.get("type") == "function"]
    names = [f.get("name", "").lower() for f in fns]
    name_set = set(names)
    raw = json.dumps(abi_list).lower()
    mint_fns = [n for n in names if n.startswith("mint") or n in ("claim", "claimfree")]
    quote_fns = [n for n in names if any(w in n for w in QUOTE_WORDS)]
    free_views = [n for n in names if n in FREE_VIEWS]
    has_registry = REG_HEX in raw or "agentregistry" in name_set or "agentgate" in name_set
    is_token = any(n in name_set for n in ("name", "symbol", "decimals", "totalsupply"))
    noarg_free = any(f.get("name", "").lower() in ("mintfree", "claimfree", "freemint")
                     and len(f.get("inputs", [])) == 0 for f in fns)
    s1 = bool(mint_fns and quote_fns and free_views and has_registry)
    s2 = bool(is_token and noarg_free and free_views and has_registry)
    return {"mint_fns": mint_fns, "quote_fns": quote_fns, "free_views": free_views,
            "agent_gate": has_registry, "is_token": is_token,
            "noarg_free": noarg_free, "S1": s1, "S2": s2, "fn_count": len(fns),
            "fn_names": names}

checked = json.load(open(f"{BASE}/track-c-scan-checked.json"))
checked_list = checked.get("checked", [])
checked_set = {a.lower() for a in checked_list}
checked_keys = {k.lower() for k in checked.keys() if k.startswith("0x")}

merged = {}
for f in CHUNKS:
    d = json.load(open(f"{BASE}/{f}"))
    for e in d.get("erc20_mint_contracts_list", []):
        a = e["address"].lower()
        if a in merged:
            merged[a]["mint_count"] += e.get("mint_count", 0)
            merged[a]["distinct_minters"] = max(merged[a].get("distinct_minters", 0), e.get("distinct_minters", 0))
        else:
            merged[a] = dict(e)
cands = [e for e in merged.values() if e.get("mint_count", 0) >= 10]
cands.sort(key=lambda e: -e["mint_count"])
new = [e for e in cands
       if e["address"].lower() not in checked_set and e["address"].lower() not in checked_keys][:20]
print(f"5c: merged erc20={len(merged)} mint_count>=10: {len(cands)}; already checked: {len(cands)-len(new)}; to check: {len(new)}")

results5c, transport_failed = [], []
for e in new:
    addr = e["address"]
    data, err = fetch_abi_curl(addr)
    if data is None:
        results5c.append({"address": addr, "mint_count": e["mint_count"],
                          "distinct_minters": e.get("distinct_minters"), "verdict": "transport-failed", "error": err})
        transport_failed.append(addr)
        print(f"  {addr} mint_count={e['mint_count']} TRANSPORT-FAILED {err}")
        continue
    abi = abi_of(data)
    if abi is None:
        results5c.append({"address": addr, "mint_count": e["mint_count"],
                          "distinct_minters": e.get("distinct_minters"), "verdict": "not_verified",
                          "sourcify_match": data.get("match")})
        print(f"  {addr} mint_count={e['mint_count']} NOT_VERIFIED")
        continue
    sh = shape_s1_s2(abi)
    verdict = "SALE-SHAPE" if (sh["S1"] or sh["S2"]) else "not-sale-shape"
    results5c.append({"address": addr, "mint_count": e["mint_count"],
                      "distinct_minters": e.get("distinct_minters"), "verdict": verdict,
                      "sourcify": "verified", **{k: v for k, v in sh.items() if k != "fn_names"}})
    print(f"  {addr} mint_count={e['mint_count']} {verdict} S1={sh['S1']} S2={sh['S2']} "
          f"registry={sh['agent_gate']} mint={bool(sh['mint_fns'])} quote={bool(sh['quote_fns'])} free={bool(sh['free_views'])} token={sh['is_token']}")
    time.sleep(0.5)

# record newly checked (only those with a definitive Sourcify answer; transport-failed stays unrecorded)
added_list, added_keys = 0, 0
for r in results5c:
    if r["verdict"] == "transport-failed":
        continue
    addr = r["address"]
    if r["verdict"] == "not_verified":
        status, note = "not_verified", ""
    elif r["verdict"] == "SALE-SHAPE":
        status, note = "SALE-SHAPE", f"S1={r['S1']} S2={r['S2']}"
    else:
        status = "checked-not-sale-shape"
        note = (f"S1={r['S1']} S2={r['S2']} (registry={r['agent_gate']} mint={bool(r['mint_fns'])} "
                f"quote={bool(r['quote_fns'])} free={bool(r['free_views'])} token={r['is_token']})")
    if addr.lower() not in checked_set:
        checked_list.append(addr); added_list += 1
    if addr not in checked:
        checked[addr] = {"source": RUN_TAG, "status": status,
                         "mint_count": r["mint_count"], "note": note}
        added_keys += 1
checked["checked"] = checked_list
json.dump(checked, open(f"{BASE}/track-c-scan-checked.json", "w"), indent=1)
print(f"track-c-scan-checked: list +{added_list}, keys +{added_keys}")

out = {"run": "backfill 2026-11-08 ~04:17 WIB", "window": [132268176, 132271220],
       "first_seen_triage": [], "early_leads": [],
       "track_c_5c": {"merged_erc20": len(merged), "ge10": len(cands),
                      "new_checked": len(new), "transport_failed": transport_failed,
                      "results": results5c},
       "sale_shape_hits": [r for r in results5c if r.get("verdict") == "SALE-SHAPE"]}
json.dump(out, open(f"{BASE}/backfill-triage-132268176-132271220.json", "w"), indent=1)
print("WROTE backfill-triage-132268176-132271220.json")
print("sale_shape_hits:", len(out["sale_shape_hits"]))
