#!/usr/bin/env python3
"""Hot-leg 2026-11-11 22:19 WIB — legs 1+2 only (RPC degraded tonight).
Leg 1: Sourcify feed limit 20, shape-check new vs hot-leg-seen.json.
Leg 2: Boltbook EN+ZH front pages, extract addresses, check new.
Writes hot-leg-2026-11-11-2219-feed.json + -boltbook-en/-zh.html + run json.
Read-only except hot-leg-seen.json (own file) + own run files."""
import json, re, subprocess, time, os
from datetime import datetime, timezone

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
TAG = "2026-11-11-2219"
T0 = time.time()
now_wib = datetime.now(timezone.utc).astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S+07:00")
out = {"run": "free-mint-hot-leg 2026-11-11 22:19 WIB", "started_wib": now_wib}

def curl(url, timeout=12):
    try:
        r = subprocess.run(["curl", "-s", "-m", str(timeout), "-A", "Mozilla/5.0",
                            url], capture_output=True, timeout=timeout + 5)
        return r.stdout
    except Exception as e:
        return b""

def curl_json(url, timeout=12):
    raw = curl(url, timeout)
    try:
        return json.loads(raw.decode(errors="replace"))
    except Exception:
        return None

# ---- Leg 1: Sourcify feed ----
feed = curl_json("https://sourcify.dev/server/v2/contracts/56?limit=20&sort=desc", 15)
seen = json.load(open(BASE + "hot-leg-seen.json"))
feed_addrs, feed_meta = [], {}
if isinstance(feed, dict):
    items = feed.get("results") or feed.get("contracts") or []
    for it in items:
        a = (it.get("address") or "").strip()
        if a:
            feed_addrs.append(a)
            feed_meta[a] = it.get("verifiedAt") or it.get("creationMatch") or ""
elif isinstance(feed, list):
    for it in feed:
        a = (it.get("address") or "").strip()
        if a:
            feed_addrs.append(a)
            feed_meta[a] = it.get("verifiedAt") or ""
out["leg1_feed"] = {"returned": len(feed_addrs),
                    "verified_range": (min(feed_meta.values()), max(feed_meta.values())) if feed_meta else None,
                    "ok": bool(feed_addrs)}
new = [a for a in feed_addrs if a.lower() not in {k.lower() for k in seen}]
out["leg1_new"] = new
json.dump({"addrs": feed_addrs, "meta": feed_meta}, open(BASE + f"hot-leg-{TAG}-feed.json", "w"), indent=1)

# ---- shape-check new contracts ----
FREE_VIEWS = {"freesharesremaining", "freeclaimed", "freefor", "freeleft", "freeused",
              "freeavailable", "freesharepoolexhausted", "freesharesclaimed",
              "freeamount", "free_supply", "free_supply()", "freeslots", "free_slots",
              "freeminted", "freemint", "freesupply"}
REGISTRY = "0x60b9262456de011f7d15a54cdd8c48baaa8b022f"
EXCLUDED = {"0x827e83e49bd7e15b67efa0e90fc25f17b8d96124",
            "0x8b47354e7b76b1970a0d06365c8244a810d37493"}
shape = {}
for a in new:
    al = a.lower()
    if al in EXCLUDED or al == REGISTRY:
        shape[a] = {"status": "excluded-or-registry"}
        continue
    abi_j = curl_json(f"https://sourcify.dev/server/v2/contract/56/{a}?fields=abi", 12)
    abi = None
    if isinstance(abi_j, dict):
        abi = abi_j.get("abi") or (abi_j.get("stdJson") or {}).get("abi")
    if not abi:
        shape[a] = {"status": "shape-check-failed", "note": "ABI unfetchable"}
        continue
    names = set()
    for fn in abi:
        if isinstance(fn, dict) and fn.get("type") in ("function", None):
            names.add((fn.get("name") or "").lower())
    has_mint = any("mint" in n for n in names)
    has_quote = any(("quote" in n or n in ("cost", "price", "mintprice", "getprice")) for n in names)
    free_views = sorted(n for n in names if n in FREE_VIEWS or "free" in n)
    agent = any(("agent" in n and ("registry" in n or "gate" in n or "id" in n)) or n in
                ("agentregistry", "agentgate", "agent_id_registry", "registry") for n in names)
    src = json.dumps(abi).lower()
    agent = agent or ("agent_id_registry" in src) or ("agentgate" in src) or (REGISTRY[2:].lower() in src)
    is_token = all(n in names for n in ("name", "symbol", "decimals", "totalsupply"))
    has_mintfree = "mintfree" in names
    s1 = has_mint and has_quote and bool(free_views) and agent
    s2 = is_token and has_mintfree and bool(free_views) and agent
    shape[a] = {"status": "checked", "S1": s1, "S2": s2, "mint": has_mint, "quote": has_quote,
                "free": free_views, "agent": agent, "n_fns": len(names)}
    time.sleep(0.2)
out["leg1_shape"] = shape
out["leg1_s1_pass"] = [a for a, s in shape.items() if s.get("S1")]
out["leg1_s2_pass"] = [a for a, s in shape.items() if s.get("S2")]

# record newly seen (own file only)
for a in new:
    if a not in seen:
        s = shape.get(a, {})
        seen[a] = {"first_seen_wib": now_wib, "source": "sourcify-feed",
                   "status": s.get("status", "checked"),
                   "note": f"S1={s.get('S1')} S2={s.get('S2')} mint={s.get('mint')} quote={s.get('quote')} free={s.get('free')} agent={s.get('agent')}"}
json.dump(seen, open(BASE + "hot-leg-seen.json", "w"), indent=1)
out["seen_count"] = len(seen)

# ---- Leg 2: Boltbook EN + ZH ----
def boltbook(lang):
    url = "https://boltbook.fun/" + ("?lang=zh" if lang == "zh" else "")
    raw = curl(url, 15)
    open(BASE + f"hot-leg-{TAG}-boltbook-{lang}.html", "wb").write(raw)
    return raw.decode(errors="replace")

addrs = set()
kw = {}
for lang in ("en", "zh"):
    html = boltbook(lang)
    found = set(re.findall(r"0x[a-fA-F0-9]{40}", html))
    addrs |= found
    kw[lang] = {"bytes": len(html),
                "free-share": html.lower().count("free share"),
                "first-share-free": html.lower().count("first share free"),
                "free-mint-share": html.lower().count("free mint share"),
                "free-mint": html.lower().count("free mint"),
                "zh-free-share": html.count("免费份额"),
                "zh-first-free": html.count("首个免费"),
                "zh-free-mint": html.count("免费铸造") + html.count("免费mint")}
    time.sleep(0.3)
seen_keys = {k.lower() for k in seen}
bb_new = sorted(a for a in addrs if a.lower() not in seen_keys)
out["leg2_boltbook"] = {"unique_addrs": len(addrs), "new_vs_seen": bb_new, "keywords": kw}
# record boltbook-new addresses as seen (checked-not-sale-shape pending shape check next leg if any)
for a in bb_new:
    if a not in seen:
        seen[a] = {"first_seen_wib": now_wib, "source": "boltbook-en" if lang == "en" else "boltbook",
                   "status": "boltbook-mention-unchecked", "note": "Boltbook mention, shape-check pending"}
json.dump(seen, open(BASE + "hot-leg-seen.json", "w"), indent=1)

out["elapsed_s"] = round(time.time() - T0, 1)
json.dump(out, open(BASE + f"hot-leg-run-{TAG}-legs12.json", "w"), indent=1)
print(json.dumps(out, indent=1))
print("ELAPSED", out["elapsed_s"])
