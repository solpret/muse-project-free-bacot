#!/usr/bin/env python3
"""Run 2026-11-06 2331 WIB — web leg retry: parse Boltbook html (fetched on retry) + fresh Sourcify feed.
Read-only except own run files. Never writes snapshot/seen/checked files."""
import json, re, subprocess, time
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TS = "2026-11-06-2331"
EXCLUDED = {"0x827e83e49bd7e15b67efa0e90fc25f17b8d96124", "0x8b47354e7b76b1970a0d06365c8244a810d37493"}
MINT = ["mint", "mintfree", "claimfree", "claim", "mintagent", "buyshare", "buyshares", "purchase"]
QUOTE = ["quote", "quotefor", "cost", "costfor", "getcost", "price", "mintprice", "feefor"]
FREE_VIEWS = ["freesharesremaining", "freeclaimed", "freefor", "freeleft", "freeused",
              "freeavailable", "freesharepoolexhausted", "freesharesclaimed",
              "freeminted", "freeremaining", "free_slots", "free_supply", "free_amount",
              "freetokens", "freeperwallet"]
GATE = ["agentid", "agent_id", "agentregistry", "agent_registry", "agentgate",
        "agent_gate", "hasagentid", "isagent"]

def curl_json(url, timeout=25):
    try:
        r = subprocess.run(["curl", "-sS", "--max-time", str(timeout), "-A", "free-mint-web/1.0", url],
                           capture_output=True, text=True, timeout=timeout + 10)
        if r.returncode != 0:
            return None, f"curl rc={r.returncode} stderr={r.stderr.strip()[:120]}"
        if not r.stdout.strip():
            return None, "empty response"
        return json.loads(r.stdout), None
    except Exception as e:
        return None, f"{type(e).__name__}: {str(e)[:120]}"

def fetch_abi(addr):
    last_err = ""
    for attempt in (1, 2):
        d, err = curl_json(f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi", timeout=20)
        if d is not None:
            abi = d.get("abi")
            if isinstance(abi, list):
                return abi, "verified", f"attempt {attempt}"
            return None, "not_verified", f"attempt {attempt}: no abi field"
        last_err = err or "unknown"
        if "404" in last_err:
            return None, "not_verified", last_err
        time.sleep(1.0)
    return None, "transport-failed", last_err

def classify(abi):
    ns = [e.get("name", "").lower() for e in abi if isinstance(e, dict) and e.get("type") == "function"]
    fn_names = [e.get("name", "") for e in abi if isinstance(e, dict) and e.get("type") == "function"]
    has_mint = any(any(m in n for m in MINT) for n in ns)
    has_quote = any(any(q in n for q in QUOTE) for n in ns)
    has_free = any(any(fv in n for fv in FREE_VIEWS) for n in ns)
    has_gate = any(any(g in n for g in GATE) for n in ns)
    has_token = all(any(t in n for n in ns) for t in ["name", "symbol", "decimals", "totalsupply"])
    noarg_free = any(f.lower() in ("mintfree", "claimfree") for f in fn_names)
    return {"mint": has_mint, "quote": has_quote, "free_view": has_free, "agent_gate": has_gate,
            "is_token": has_token, "noarg_free": noarg_free,
            "S1": bool(has_mint and has_quote and has_free and has_gate),
            "S2": bool(has_token and noarg_free and has_free and has_gate),
            "mint_fns": [f for f in fn_names if "mint" in f.lower()],
            "quote_fns": [f for f in fn_names if f.lower() in QUOTE or f.lower().startswith(("quote", "cost"))],
            "free_views": [f for f in fn_names if f.lower() in FREE_VIEWS],
            "gate_fns": [f for f in fn_names if any(g in f.lower() for g in GATE)],
            "fn_count": len(fn_names)}

def shape_check(addr):
    abi, status, detail = fetch_abi(addr)
    rec = {"address": addr, "sourcify": status, "detail": detail}
    if status == "verified":
        rec.update(classify(abi))
        rec["verdict"] = "SALE-SHAPE-HIT" if (rec["S1"] or rec["S2"]) else "not-sale-shape"
    elif status == "not_verified":
        rec.update({"S1": False, "S2": False, "verdict": "not-sale-shape"})
    else:
        rec.update({"S1": None, "S2": None, "verdict": "shape-check-failed-transport"})
    return rec

snap = json.load(open(f"{BASE}/onchain-snapshot.json"))
snap_addrs = set()
for v in snap.get("contracts", {}).values():
    if isinstance(v, dict) and v.get("address"):
        snap_addrs.add(v["address"].lower())
for v in snap.get("track_c", {}).values():
    if isinstance(v, dict):
        for k in ("sale", "token", "address"):
            if v.get(k):
                snap_addrs.add(str(v[k]).lower())
for v in snap.get("excluded", {}).values():
    if isinstance(v, dict):
        for k in ("address", "sale", "token"):
            if v.get(k):
                snap_addrs.add(str(v[k]).lower())
seen = json.load(open(f"{BASE}/onchain-scan-seen.json"))
seen_contracts = {k.lower() for k in seen.get("contracts", {}).keys()}
hl = json.load(open(f"{BASE}/hot-leg-seen.json"))
hl_keys = {k.lower() for k in hl.keys()}

# --- Boltbook parse ---
en = open(f"{BASE}/boltbook-2026-11-06-2331-en.html").read()
zh = open(f"{BASE}/boltbook-2026-11-06-2331-zh.html").read()
addr_re = re.compile(r"0x[a-fA-F0-9]{40}")
en_addrs = sorted(set(addr_re.findall(en)))
zh_addrs = sorted(set(addr_re.findall(zh)))
all_addrs = sorted(set(en_addrs) | set(zh_addrs))
def snippets(html, addr):
    out_s = []
    for m in re.finditer(re.escape(addr), html, flags=re.I):
        s = re.sub(r"<[^>]+>", " ", html[max(0, m.start()-400):m.end()+400])
        out_s.append(re.sub(r"\s+", " ", s).strip()[:400])
    return out_s
kw = ["free share", "first share free", "1 free share", "free mint share",
      "免费份额", "首个免费", "免费铸造", "免费mint"]
text_low = (en + zh).lower()
kw_hits = {k: text_low.count(k.lower()) for k in kw if k.lower() in text_low}
new_bolt = [a for a in all_addrs if a.lower() not in snap_addrs]
bolt_shapes = []
for a in new_bolt:
    s = shape_check(a)
    s["snippets"] = snippets(en + zh, a)[:2]
    bolt_shapes.append(s)
    print("BOLT", a, s["verdict"], s.get("S1"), s.get("S2"), s["sourcify"], flush=True)
bolt_out = {"run": TS, "checked_wib": "2026-11-06T23:31:00+07:00 (html refetched ~23:50 WIB after first fetch rc=28 timeout)",
            "en_bytes": len(en), "en_rc": 200, "zh_bytes": len(zh), "zh_rc": 200,
            "en_addrs": len(en_addrs), "zh_addrs": len(zh_addrs),
            "unique_addrs": len(all_addrs), "keyword_hits": kw_hits,
            "all_addrs": all_addrs, "new_vs_snapshot": new_bolt,
            "in_snapshot": [a for a in all_addrs if a.lower() in snap_addrs],
            "shape_checks": bolt_shapes,
            "hits": [s for s in bolt_shapes if s.get("S1") or s.get("S2")]}
json.dump(bolt_out, open(f"{BASE}/run-{TS}-boltbook.json", "w"), indent=1)
print("BOLTBOOK DONE en", len(en), "zh", len(zh), "unique", len(all_addrs),
      "new", len(new_bolt), "hits", len(bolt_out["hits"]), flush=True)

# --- Fresh Sourcify feed (already fetched to file on retry) ---
feed = json.load(open(f"{BASE}/run-{TS}-sourcify-feed.json"))
items = feed.get("results", feed) if isinstance(feed, dict) else feed
feed_addrs, feed_items = [], []
for it in items:
    a = it.get("address") if isinstance(it, dict) else None
    if a:
        feed_addrs.append(a)
        feed_items.append({"address": a, "verifiedAt": it.get("verifiedAt")})
feed_new = [a for a in feed_addrs if a.lower() not in snap_addrs and a.lower() not in seen_contracts
            and a.lower() not in hl_keys and a.lower() not in EXCLUDED]
feed_excluded = [a for a in feed_addrs if a.lower() in EXCLUDED]
shapes = []
for a in feed_new:
    s = shape_check(a)
    s["source"] = "feed-new"
    shapes.append(s)
    print("FEED", a, s["verdict"], s.get("S1"), s.get("S2"), s["sourcify"], flush=True)
# merge with earlier retry results (already in sourcify-shape.json)
prev = json.load(open(f"{BASE}/run-{TS}-sourcify-shape.json"))
merged_shapes = prev.get("shapes", []) + shapes
feed_out = {"run": TS, "checked_wib": "2026-11-06T23:31:00+07:00 (feed refetched ~23:50 WIB after first fetch timeout)",
            "feed_error_first_attempt": prev.get("feed_error"),
            "feed_count": len(feed_addrs), "feed": feed_items,
            "feed_new": feed_new, "feed_excluded_rediscovered": feed_excluded,
            "retries": prev.get("retries", []),
            "shapes": merged_shapes,
            "hits": [s for s in merged_shapes if s.get("S1") or s.get("S2")],
            "transport_failed": [s["address"] for s in merged_shapes if s["verdict"] == "shape-check-failed-transport"]}
json.dump(feed_out, open(f"{BASE}/run-{TS}-sourcify-shape.json", "w"), indent=1)
print("FEED DONE count", len(feed_addrs), "new", len(feed_new), "checked_total", len(merged_shapes),
      "hits", len(feed_out["hits"]), "transport_failed", feed_out["transport_failed"], flush=True)
print("RETRY DONE")
