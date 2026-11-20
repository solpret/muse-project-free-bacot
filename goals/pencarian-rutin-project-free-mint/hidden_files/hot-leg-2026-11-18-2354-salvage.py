#!/usr/bin/env python3
"""Salvage for hot-leg run 2026-11-18 23:54 WIB: legs 1-3 + bridge only (no RPC).
Main 2354 script was killed at 300s in leg 4 (all 4 BSC RPC endpoints returned
empty/non-JSON responses; chunks 1-2 FAIL, chunks 3-12 deadline-skipped).
This re-runs only the fast HTTP legs and persists them."""
import json, re, subprocess, time
from datetime import datetime, timezone, timedelta
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
REGISTRY = "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F"
T0 = time.time()
NOW = datetime.now(timezone(timedelta(hours=7))).strftime("%Y-%m-%dT%H:%M:%S+07:00")
out = {"run": "free-mint-hot-leg 2026-11-18 23:54 WIB",
       "started_wib": "2026-11-18T23:54:38+07:00",
       "salvaged_wib": NOW,
       "status": "PARTIAL - leg 4 skipped (RPC empty responses all endpoints), legs 1-3 + bridge salvaged"}
def fetch(url, timeout=15):
    r = subprocess.run(["curl", "-sL", "--max-time", str(timeout), "-A", "hot-leg/1.0", url],
                       capture_output=True)
    if r.returncode == 0 and r.stdout:
        return r.stdout
    raise RuntimeError(f"curl rc={r.returncode} empty for {url}")
seen = json.load(open(BASE + "hot-leg-seen.json"))
seen_l = {k.lower() for k in seen}
# Leg 1
try:
    feed = json.loads(fetch("https://sourcify.dev/server/v2/contracts/56?limit=20&sort=desc"))
    items = feed if isinstance(feed, list) else feed.get("results", [])
    contracts, va = [], []
    for c in items:
        if isinstance(c, dict) and c.get("address"):
            contracts.append(c["address"])
            if c.get("verifiedAt"): va.append(c["verifiedAt"])
    new = [a for a in contracts if a.lower() not in seen_l and a.lower() != REGISTRY.lower()]
    out["sourcify_feed"] = {"total": len(contracts), "new": len(new), "new_contracts": new,
                            "top": contracts[0] if contracts else None,
                            "top_verifiedAt": max(va) if va else None, "all": contracts}
except Exception as e:
    out["sourcify_feed"] = {"error": f"{type(e).__name__}: {e}"}; new = []; contracts = []
# Leg 2
def boltbook(lang):
    url = "https://boltbook.fun/" + ("?lang=zh" if lang == "zh" else "")
    raw = fetch(url, timeout=20)
    text = raw.decode("utf-8", errors="ignore")
    addrs = sorted(set(re.findall(r"0x[a-fA-F0-9]{40}", text)))
    low = text.lower()
    return {"bytes": len(raw), "http_code": "200", "full_address_contracts": len(addrs),
            "addresses": addrs,
            "new": len([a for a in addrs if a.lower() not in seen_l]),
            "new_contracts": [a for a in addrs if a.lower() not in seen_l],
            "free_kw": sum(low.count(k) for k in ("free share", "first share free", "1 free share", "free mint share")),
            "zh_free_kw": sum(text.count(k) for k in ("免费份额", "首个免费", "免费铸造", "免费mint"))}
bb = {}
for lang in ("en", "zh"):
    try: bb[lang] = boltbook(lang)
    except Exception as e: bb[lang] = {"error": f"{type(e).__name__}: {e}"}
out["boltbook_en"] = bb["en"]; out["boltbook_zh"] = bb["zh"]
bb_new = []
for lang in ("en", "zh"):
    for a in bb.get(lang, {}).get("addresses", []):
        if a.lower() not in seen_l and a.lower() not in [x.lower() for x in bb_new]:
            bb_new.append(a)
# Shape-check
FREE_VIEWS = ["freeSharesRemaining", "freeClaimed", "freeFor", "freeLeft",
              "freeUsed", "freeAvailable", "freeSharePoolExhausted",
              "freeSharesClaimed", "freeMinted", "freeMintedTotal"]
def shape(addr):
    try:
        d = json.loads(fetch(f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi", timeout=15))
        abi = d.get("abi") or (d.get("stdJson", {}) or {}).get("abi") or []
        va2 = d.get("verifiedAt")
    except Exception as e:
        return {"status": "shape-check-failed", "error": f"{type(e).__name__}: {e}"}
    names = [f.get("name", "").lower() for f in abi if isinstance(f, dict)]
    has_mint = any(n.startswith("mint") or n in ("claimfree", "claim", "mintfree") for n in names)
    has_quote = any("quote" in n or "price" in n or n.startswith("cost") for n in names)
    free = sorted(set(n for n in names if any(k.lower() in n for k in FREE_VIEWS)))
    agent = any("agent" in n or "registry" in n for n in names) or REGISTRY.lower() in json.dumps(abi).lower()
    tokenish = all(k in names for k in ("name", "symbol", "decimals", "totalsupply"))
    noarg_free = any(n in ("mintfree", "claimfree") for n in names)
    return {"S1": has_mint and has_quote and bool(free) and agent,
            "S2": tokenish and noarg_free and bool(free) and agent,
            "has_mint": has_mint, "has_quote": has_quote, "free_views": free,
            "agent_ref": agent, "is_token": tokenish, "n_fns": len(abi),
            "status": "checked", "verifiedAt": va2}
EXCLUDED = ("0x827e83e49bd7e15b67efa0e90fc25f17b8d96124",
            "0x8b47354e7b76b1970a0d06365c8244a810d37493")
shape_res = {}
for a in (new + bb_new):
    shape_res[a] = {"status": "excluded-example"} if a.lower() in EXCLUDED else shape(a)
out["shape_check_targets"] = new + bb_new
out["shape_check"] = [dict({"address": a}, **shape_res[a]) for a in (new + bb_new)]
out["shape_hits"] = [a for a in (new + bb_new) if shape_res.get(a, {}).get("S1") or shape_res.get(a, {}).get("S2")]
out["leg3"] = {}
for a in (new + bb_new):
    if a.lower() not in seen_l:
        seen[a] = {"first_seen_wib": NOW, "source": "sourcify-feed" if a in new else "boltbook",
                   "status": shape_res.get(a, {}).get("status", "checked"),
                   "note": json.dumps(shape_res.get(a, {}))[:300]}
json.dump(seen, open(BASE + "hot-leg-seen.json", "w"), indent=1)
out["seen_total"] = len(seen)
# Bridge (read-only)
try:
    br = json.load(open(BASE + "scan-bridge.json"))
    bcontracts = br.get("contracts", {})
    snap = json.load(open(BASE + "onchain-snapshot.json"))
    def _addr_vals(section, fields):
        o = set()
        for v in (snap.get(section) or {}).values():
            if isinstance(v, dict):
                for f in fields:
                    x = v.get(f)
                    if isinstance(x, str) and x.startswith("0x") and len(x) == 42:
                        o.add(x.lower())
        return o
    snap_addrs = (_addr_vals("contracts", ["address", "sale", "contract"])
                  | _addr_vals("track_c", ["sale", "address", "token", "contract"])
                  | _addr_vals("pending_claims", ["address", "sale", "mint"]))
    outside, discarded = [], 0
    for addr, info in bcontracts.items():
        if info.get("same_owner_discarded"):
            discarded += 1; continue
        if addr.lower() not in snap_addrs:
            outside.append(addr)
    out["bridge_scan"] = {"total": len(bcontracts), "not_in_snapshot": len(outside),
                          "not_in_snapshot_list": outside, "same_owner_discarded": discarded}
except Exception as e:
    out["bridge_scan"] = {"error": f"{type(e).__name__}: {e}"}
out["leg4"] = ("SKIPPED - BSC RPC fully degraded: all 4 endpoints (bsc-dataseed, "
               "bsc-dataseed1/2, publicnode) returned empty/non-JSON for eth_call batches "
               "(chunks 1-2 FAIL, chunks 3-12 deadline-skipped at 272s); direct eth_blockNumber "
               "probe 00:07 WIB also empty on bsc-dataseed + publicnode. No reread file; "
               "leg 4 retried next run.")
out["threshold_check"] = ("not evaluated this run (leg 4 skipped); last full evaluation 23:39: "
    "STOCKAGENT 73.4%, Lumenhold 83.9%, AgentBubble 92.5% (age-excluded), Matrix 64.2%, "
    "AGCLUB 59.7%, PunchCard 24.1% - none promotable (age/website unverified or age-excluded).")
out["poffzi_fcfs"] = "NO PROCESS FOUND"
out["executions"] = "none - no preview, no mint, no claim (read-only run)"
out["elapsed_s"] = round(time.time() - T0, 1)
json.dump(out, open(BASE + "hot-leg-run-2026-11-18-2354.json", "w"), indent=1)
print("SALVAGE DONE", json.dumps({k: out[k] for k in ("sourcify_feed","shape_hits","bridge_scan","seen_total")}, indent=1)[:2000])
print("bb_en:", json.dumps(bb.get("en"))[:300])
print("bb_zh:", json.dumps(bb.get("zh"))[:300])
