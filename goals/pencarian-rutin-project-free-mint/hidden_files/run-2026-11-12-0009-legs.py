#!/usr/bin/env python3
"""Hot-leg run 2026-11-12 00:09 WIB: legs 1-3 (Sourcify feed + shape-check,
Boltbook EN+ZH, bridge read-only, stampooor site).
Writes run-2026-11-12-0009-*.json/html + updates hot-leg-seen.json (backup first).
Never writes snapshot/seen-state/watermark of the main job.
"""
import json, re, time, urllib.request, concurrent.futures, subprocess as sp, shutil, os

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
TS = "2026-11-12 00:09 WIB"
PFX = "run-2026-11-12-0009-"
t0 = time.time()
out = {"started_wib": TS}

FREE_VIEWS = ["freeSharesRemaining", "freeClaimed", "freeFor", "freeLeft", "freeUsed",
              "freeAvailable", "freeSharePoolExhausted", "freeSharesClaimed",
              "freeMinted", "freeCardsRemaining"]
REGISTRY = "0x60b9262456de011f7d15a54cdd8c48baaa8b022f"

def get(url, timeout=25, headers=None):
    req = urllib.request.Request(url, headers=headers or {"User-Agent": "free-bacot/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode(errors="replace")

def curl_get(url, timeout=30):
    r = sp.run(["curl", "-sL", "--max-time", str(timeout), url], capture_output=True, text=True, timeout=timeout + 5)
    return r.stdout if r.stdout else None

# --- 1. Sourcify feed ---
feed_raw = None
try:
    feed_raw = get("https://sourcify.dev/server/v2/contracts/56?limit=20&sort=desc")
except Exception as e:
    print("FEED urllib fail:", e, "-> curl retry", flush=True)
    try:
        feed_raw = curl_get("https://sourcify.dev/server/v2/contracts/56?limit=20&sort=desc")
    except Exception as e2:
        print("FEED curl fail:", e2, flush=True)
items = []
if feed_raw:
    try:
        feed = json.loads(feed_raw)
        json.dump(feed, open(BASE + PFX + "feed.json", "w"), indent=1)
        items = feed.get("results", [])
        out["feed"] = {"n": len(items), "newest_verifiedAt": items[0].get("verifiedAt") if items else None,
                       "oldest_verifiedAt": items[-1].get("verifiedAt") if items else None}
    except Exception as e:
        out["feed"] = {"error": f"parse {type(e).__name__}: {str(e)[:120]}"}
else:
    out["feed"] = {"error": "urllib+curl failed"}

seen = {}
try:
    seen = json.load(open(BASE + "hot-leg-seen.json"))
    if not isinstance(seen, dict):
        seen = {}
except Exception:
    seen = {}
seen_l = {k.lower() for k in seen.keys()}
for _prevf in ("run-2026-11-11-2359-feed.json", "run-2026-11-11-2359-feed-retry.json",
               "run-2026-11-11-2331-feed.json", "run-2026-11-11-2301-feed.json"):
    try:
        prev = json.load(open(BASE + _prevf))
        for it in prev.get("results", []):
            seen_l.add(str(it.get("address", "")).lower())
    except Exception:
        pass
new_addrs = [it.get("address") for it in items if str(it.get("address", "")).lower() not in seen_l and it.get("address")]
json.dump(new_addrs, open(BASE + PFX + "feed-new.json", "w"), indent=1)
out["feed_new"] = new_addrs

def fetch_abi(addr):
    url = f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi"
    try:
        meta = json.loads(get(url, timeout=25))
        abi = meta.get("abi", [])
        fns = {}
        for e in abi:
            if e.get("type") == "function":
                fns.setdefault(e["name"], []).append(e)
        names = set(fns)
        has_mint = any(n.lower().startswith("mint") for n in names)
        lnames = {n.lower() for n in names}
        has_quote = bool(lnames & {"quote", "cost", "getquote", "mintcost", "price", "getprice", "mintprice"})
        free_views = sorted(names & set(FREE_VIEWS))
        agent_ref = bool(lnames & {"agentid", "agentregistry", "registry", "getagentid", "agentgate", "agentidregistry"})
        is_token = bool(names & {"name", "symbol", "decimals", "totalSupply"})
        mintfree = "mintFree" in fns and any(len(e.get("inputs", [])) == 0 for e in fns["mintFree"])
        s1 = has_mint and has_quote and bool(free_views) and agent_ref
        s2 = is_token and mintfree and bool(names & {"freeClaimed", "freeMinted"}) and bool(names & {"FREE_SLOTS", "FREE_SUPPLY"}) and agent_ref
        is_nft = bool(names & {"tokenURI", "ownerOf", "safeTransferFrom"}) or "uri" in names
        free_mint_fn = bool(names & {"freeMint", "mintFree", "claimFree", "mint"}) or any(n.lower().startswith("freemint") for n in names)
        early_shape = is_nft and (agent_ref or free_mint_fn)
        return {"address": addr, "S1": s1, "S2": s2, "early_shape": early_shape,
                "has_mint": has_mint, "has_quote": has_quote, "free_views": free_views,
                "agent_ref": agent_ref, "is_token": is_token, "is_nft": is_nft,
                "fn_count": len(names)}
    except Exception as ex:
        return {"address": addr, "error": f"{type(ex).__name__}: {str(ex)[:120]}"}

shapes = []
if new_addrs:
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as ex:
        shapes = list(ex.map(fetch_abi, new_addrs))
out["feed_shape"] = {"s1_pass": [s["address"] for s in shapes if s.get("S1")],
                     "s2_pass": [s["address"] for s in shapes if s.get("S2")],
                     "early_shape": [s["address"] for s in shapes if s.get("early_shape")],
                     "shapes": shapes}
print("FEED", out["feed"], "NEW", len(new_addrs), "S1", out["feed_shape"]["s1_pass"],
      "S2", out["feed_shape"]["s2_pass"], "EARLY", out["feed_shape"]["early_shape"], flush=True)

# --- 2. Boltbook EN + ZH ---
ADDR_RE = re.compile(r"0x[0-9a-fA-F]{40}")
for lang, url in (("en", "https://boltbook.fun/"), ("zh", "https://boltbook.fun/?lang=zh")):
    html = None
    try:
        html = get(url, timeout=30)
    except Exception as e:
        try:
            c = curl_get(url, timeout=30)
            if c and len(c) > 1000:
                html = c
                print(f"BOLTBOOK {lang}: urllib fail ({e}); curl OK", flush=True)
        except Exception as e2:
            print(f"BOLTBOOK {lang}: curl also fail {e2}", flush=True)
    if html:
        addrs = sorted(set(a for a in ADDR_RE.findall(html)))
        out[f"boltbook_{lang}"] = {"bytes": len(html), "addrs": addrs, "n": len(addrs)}
        open(BASE + PFX + f"boltbook-{lang}.html", "w").write(html)
        print(f"BOLTBOOK {lang}: {len(html)} bytes, {len(addrs)} addrs", flush=True)
    else:
        out[f"boltbook_{lang}"] = {"bytes": 0, "error": "urllib+curl failed", "addrs": []}
        print(f"BOLTBOOK {lang}: FAIL", flush=True)

bb_new = []
for lang in ("en", "zh"):
    for a in out.get(f"boltbook_{lang}", {}).get("addrs", []):
        if a.lower() not in seen_l and a not in bb_new:
            bb_new.append(a)
out["boltbook_new"] = bb_new
print("BOLTBOOK NEW", bb_new, flush=True)

# --- bridge (read-only) ---
try:
    br = json.load(open(BASE + "scan-bridge.json"))
    contracts = br.get("contracts", {})
    snap = json.load(open(BASE + "onchain-snapshot.json"))
    snap_addrs = set()
    for sec in ("contracts", "track_c", "pending_claims"):
        v = snap.get(sec)
        if isinstance(v, dict):
            for item in v.values():
                if isinstance(item, dict) and item.get("address"):
                    snap_addrs.add(item["address"].lower())
                if isinstance(item, dict) and item.get("sale"):
                    snap_addrs.add(str(item["sale"]).lower())
    not_in_snap = [a for a in contracts if a.lower() not in snap_addrs]
    sod = [a for a, c in contracts.items() if isinstance(c, dict) and c.get("same_owner_discarded")]
    out["bridge"] = {"total": len(contracts), "not_in_snapshot": not_in_snap,
                     "same_owner_discarded": sod}
except Exception as e:
    out["bridge"] = {"error": f"{type(e).__name__}: {str(e)[:120]}"}
print("BRIDGE", out["bridge"], flush=True)

# --- stampooor site (gate-blocked strong lead) ---
def curl_code(url, timeout=15):
    try:
        r = sp.run(["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}", "--max-time", str(timeout), url],
                   capture_output=True, text=True, timeout=timeout + 5)
        return r.stdout.strip()
    except Exception:
        return "000"

out["stampooor_site"] = {
    "root": curl_code("https://stampoor.xyz/"),
    "packs": curl_code("https://stampoor.xyz/packs"),
}
print("STAMPOOOR SITE", out["stampooor_site"], flush=True)

# --- update hot-leg-seen.json with newly seen feed contracts (backup first) ---
added = 0
try:
    for s in shapes:
        a = s["address"]
        if a not in seen:
            note = (f"S1={s.get('S1')} S2={s.get('S2')} early={s.get('early_shape')} "
                    f"mint={s.get('has_mint')} quote={s.get('has_quote')} free={s.get('free_views')} "
                    f"agent={s.get('agent_ref')} token={s.get('is_token')} nft={s.get('is_nft')} (shape-feed 0009)")
            if s.get("error"):
                note = f"S1=None S2=None early=None (shape-feed 0009) ERR: {s['error']}"
            seen[a] = {"first_seen_wib": "2026-11-12T00:09:00+07:00", "note": note,
                       "source": "sourcify-feed-0009",
                       "status": "checked-not-sale-shape" if not (s.get("S1") or s.get("S2")) else "sale-shape-pass"}
            added += 1
    for a in bb_new:
        if a not in seen:
            seen[a] = {"first_seen_wib": "2026-11-12T00:09:00+07:00",
                       "note": "new from Boltbook front page, shape-check pending next run",
                       "source": "boltbook-0009", "status": "seen-boltbook"}
            added += 1
    if added:
        shutil.copy(BASE + "hot-leg-seen.json", BASE + "hot-leg-seen.json.bak-0009")
        json.dump(seen, open(BASE + "hot-leg-seen.json", "w"), indent=1)
    out["seen_added"] = added
except Exception as e:
    out["seen_update_error"] = f"{type(e).__name__}: {str(e)[:120]}"
print("SEEN ADDED", out.get("seen_added"), flush=True)

out["elapsed_s"] = round(time.time() - t0, 1)
json.dump(out, open(BASE + PFX + "legs.json", "w"), indent=1)
print("LEGS DONE", out["elapsed_s"], "s", flush=True)
