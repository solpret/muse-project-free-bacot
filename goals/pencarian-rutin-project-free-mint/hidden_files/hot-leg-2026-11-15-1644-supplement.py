#!/usr/bin/env python3
"""Hot-leg 16:44 WIB supplement: re-run leg1+leg2 with corrected Sourcify
feed parse (endpoint now returns {"results": [...]} not {"contracts": [...]}).
Shape-checks only contracts not in hot-leg-seen.json; records them there."""
import json, time, re, urllib.request, urllib.error
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
REGISTRY = "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F"
EXCLUDED = {"0x827E83E49Bd7E15b67efa0e90fC25f17b8D96124",
            "0x8b47354E7b76B1970a0D06365c8244a810d37493"}
t0 = time.time()
run = {"run": "hot-leg 2026-11-15 16:44 WIB supplement", "started_wib": "2026-11-15T16:44+07:00"}

def http_get(url, timeout=25):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return True, r.read(), None
    except urllib.error.HTTPError as e:
        try: partial = e.read()
        except Exception: partial = b""
        return False, partial, f"HTTPError {e.code} ({len(partial)} bytes read)"
    except Exception as e:
        return False, b"", f"{type(e).__name__}: {str(e)[:120]}"

ok, data, err = http_get("https://sourcify.dev/server/v2/contracts/56?limit=20&sort=desc")
feed = []
if ok:
    try:
        parsed = json.loads(data)
        feed = parsed.get("results") or parsed.get("contracts") or (parsed if isinstance(parsed, list) else [])
    except Exception as e:
        err = f"parse: {e}"
feed_addrs = [c.get("address") for c in feed if isinstance(c, dict) and c.get("address")]
run["sourcify_feed"] = {"ok": ok, "count": len(feed_addrs), "error": err,
    "top": feed_addrs[0] if feed_addrs else None,
    "top_verifiedAt": feed[0].get("verifiedAt") if feed and isinstance(feed[0], dict) else None,
    "feed_key": "results" if ok and isinstance(json.loads(data), dict) and "results" in json.loads(data) else "contracts/other"}

def fetch_boltbook(lang):
    url = "https://boltbook.fun/" + ("?lang=zh" if lang == "zh" else "")
    ok2, d2, e2 = http_get(url)
    addrs = sorted(set(re.findall(r"0x[a-fA-F0-9]{40}", d2.decode("utf-8", "ignore")))) if d2 else []
    return {"ok": ok2, "bytes": len(d2), "error": e2,
            "full_address_contracts": len(addrs), "addrs": addrs}
run["boltbook_en"] = fetch_boltbook("en")
run["boltbook_zh"] = fetch_boltbook("zh")

seen = json.load(open(BASE + "hot-leg-seen.json"))
seen_lower = {k.lower() for k in seen}
def is_seen(a): return a.lower() in seen_lower
new_feed = [a for a in feed_addrs if a and not is_seen(a) and a.lower() not in {e.lower() for e in EXCLUDED} and a.lower() != REGISTRY.lower()]
bb_addrs = sorted(set(run["boltbook_en"]["addrs"] + run["boltbook_zh"]["addrs"]))
new_bb = [a for a in bb_addrs if not is_seen(a) and a.lower() not in {e.lower() for e in EXCLUDED}]
targets = []
for a in new_feed + new_bb:
    if a not in targets: targets.append(a)
run["new_contracts"] = {"sourcify": new_feed, "boltbook": new_bb, "targets": targets}

FREE_VIEWS = ["freeSharesRemaining","freeClaimed","freeFor","freeLeft","freeUsed",
              "freeAvailable","freeSharePoolExhausted","freeSharesClaimed","freeMinted"]
def shape_check(addr):
    ok3, d3, e3 = http_get(f"https://sourcify.dev/server/v2/contracts/56/{addr}")
    if not ok3:
        return {"address": addr, "status": "abi-fetch-failed", "error": e3}
    try:
        meta = json.loads(d3)
        abi = meta.get("abi") or meta.get("stdJson", {}).get("abi") or []
    except Exception as e:
        return {"address": addr, "status": "abi-parse-failed", "error": str(e)[:120]}
    fns = [f.get("name","") for f in abi if isinstance(f, dict) and f.get("type")=="function"]
    fnset = set(fns)
    has_mint = any(n.startswith("mint") for n in fnset)
    has_quote = any(("quote" in n.lower() or "cost" in n.lower() or "price" in n.lower()) for n in fnset)
    free_views = [v for v in FREE_VIEWS if v in fnset]
    agent_ref = any(("agent" in n.lower() or "AgentGate" in n or "registry" in n.lower()) for n in fnset) or REGISTRY.lower() in json.dumps(meta).lower()
    is_token = bool({"name","symbol","decimals","totalSupply"} <= fnset)
    s1 = has_mint and has_quote and bool(free_views) and agent_ref
    s2 = is_token and ("mintFree" in fnset) and bool({"freeClaimed","freeMinted"} & fnset) and bool({"FREE_SLOTS","FREE_SUPPLY"} & fnset) and agent_ref
    return {"address": addr, "S1": s1, "S2": s2, "has_mint": has_mint,
            "has_quote": has_quote, "free_views": free_views, "agent_ref": agent_ref,
            "is_token": is_token, "n_fns": len(fnset), "status": "checked",
            "verifiedAt": next((c.get("verifiedAt") for c in feed if isinstance(c, dict) and c.get("address","").lower()==addr.lower()), None)}
run["shape_check"] = [shape_check(a) for a in targets]
run["shape_hits"] = [s for s in run["shape_check"] if s.get("S1") or s.get("S2")]
now_wib = "2026-11-15T16:44+07:00"
for s in run["shape_check"]:
    a = s["address"]
    if a not in seen:
        seen[a] = {"first_seen_wib": now_wib,
                   "note": f"S1={s.get('S1')} S2={s.get('S2')} mint={s.get('has_mint')} quote={s.get('has_quote')} free={s.get('free_views')} agent={s.get('agent_ref')} token={s.get('is_token')}",
                   "source": "hot-leg-1644-supplement", "status": "checked-not-sale-shape" if not (s.get("S1") or s.get("S2")) else "sale-shape"}
json.dump(seen, open(BASE + "hot-leg-seen.json", "w"), indent=1)
run["elapsed_s"] = round(time.time() - t0, 1)
json.dump(run, open(BASE + "run-hot-leg-2026-11-15-1644-supplement.json", "w"), indent=1)
print(json.dumps(run, indent=1))
