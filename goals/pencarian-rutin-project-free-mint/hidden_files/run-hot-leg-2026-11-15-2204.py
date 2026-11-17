#!/usr/bin/env python3
"""Hot-leg run 2026-11-15 22:04 WIB. Light: Sourcify feed + Boltbook EN/ZH +
shape-check new contracts only + bridge (read-only). Leg 4 re-read is a
separate script (hot-leg-2026-11-15-2204-reread.py), diffed vs 21:49 baseline.
Read-only except hot-leg-seen.json (own file). No preview/mint.
Short timeouts; skip on stall."""
import json, re, time, urllib.request

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
SEEN_P = BASE + "hot-leg-seen.json"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
REG = "0x60b9262456de011f7d15a54cdd8c48baaa8b022f"
EXCLUDED = {"0x827e83e49bd7e15b67efa0e90fc25f17b8d96124",
            "0x8b47354e7b76b1970a0d06365c8244a810d37493"}
t0 = time.time()
out = {"run": "free-mint-hot-leg 2026-11-15T22:04+07:00",
       "started_wib": "2026-11-15T22:04+07:00", "legs": {},
       "new_contracts": [], "shape": [], "leg4": {"deferred": "reread script"},
       "bridge": {}, "elapsed_s": 0}

def fetch(url, timeout=20):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", "replace")

def addrs(text):
    return set(a for a in re.findall(r"0x[a-fA-F0-9]{40}", text))

out["sourcify_feed"] = {"total": 0, "top": None, "top_verifiedAt": None, "new": 0, "error": None}
# Leg 1: Sourcify feed
try:
    feed = json.loads(fetch("https://sourcify.dev/server/v2/contracts/56?limit=20&sort=desc", 20))
    items = feed if isinstance(feed, list) else feed.get("results", [])
    feed_addrs = [it.get("address") for it in items if it.get("address")]
    out["sourcify_feed"] = {"total": len(feed_addrs), "top": feed_addrs[0] if feed_addrs else None,
                            "top_verifiedAt": items[0].get("verifiedAt") if items else None,
                            "new": 0, "error": None}
    out["legs"]["sourcify"] = {"ok": True, "count": len(feed_addrs)}
except Exception as e:
    out["legs"]["sourcify"] = {"ok": False, "error": str(e)[:120]}
    out["sourcify_feed"]["error"] = str(e)[:120]
    feed_addrs = []

# Leg 2: Boltbook EN + ZH
bb_addrs = set()
for lang, url in (("en", "https://boltbook.fun/?lang=en"),
                  ("zh", "https://boltbook.fun/?lang=zh")):
    try:
        html = fetch(url, 20)
        a = addrs(html)
        bb_addrs |= a
        out[f"boltbook_{lang}"] = {"bytes": len(html), "full_address_contracts": len(a),
                                   "error": None}
        out["legs"][f"boltbook-{lang}"] = {"ok": True, "bytes": len(html), "addrs": len(a)}
    except Exception as e:
        out[f"boltbook_{lang}"] = {"bytes": 0, "full_address_contracts": 0, "error": str(e)[:120]}
        out["legs"][f"boltbook-{lang}"] = {"ok": False, "error": str(e)[:120]}
for lang, url in (("en", "https://boltbook.fun/?lang=en"),
                  ("zh", "https://boltbook.fun/?lang=zh")):
    if not out["legs"].get(f"boltbook-{lang}", {}).get("ok"):
        try:
            html = fetch(url, 20)
            bb_addrs |= addrs(html)
            out["legs"][f"boltbook-{lang}-retry"] = {"ok": True, "bytes": len(html)}
            out[f"boltbook_{lang}"]["bytes"] = len(html)
            out[f"boltbook_{lang}"]["error"] = None
        except Exception as e:
            out["legs"][f"boltbook-{lang}-retry"] = {"ok": False, "error": str(e)[:120]}

seen = json.load(open(SEEN_P))
seen_keys = {k.lower() for k in seen}
new = [a for a in (feed_addrs + sorted(bb_addrs))
       if a.lower() not in seen_keys and a.lower() not in EXCLUDED]
new = list(dict.fromkeys(new))
out["new_contracts"] = new
out["sourcify_feed"]["new"] = sum(1 for a in feed_addrs if a.lower() not in seen_keys)
out["boltbook_en"]["new"] = 0
out["boltbook_zh"]["new"] = 0

FREE_VIEWS = {"freesharesremaining", "freeclaimed", "freefor", "freeleft",
              "freeused", "freeavailable", "freesharepoolexhausted",
              "freesharesclaimed", "freeminted", "freeremaining"}
shape_hits = []
for addr in new:
    info = {"address": addr}
    try:
        data = json.loads(fetch(
            f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi,metadata", 20))
        abi = data.get("abi") or []
        fns = [f.get("name", "").lower() for f in abi if f.get("type") == "function"]
        has_mint = any("mint" in f or "claim" in f for f in fns)
        has_quote = any("quote" in f or "cost" in f or "price" in f for f in fns)
        free = [f for f in fns if f in FREE_VIEWS]
        meta = json.dumps(data.get("metadata") or data)
        agent = REG in meta.lower() or "agentgate" in meta.lower() or \
            any("agent" in f for f in fns)
        s1 = has_mint and has_quote and bool(free) and agent
        is_token = any(f in fns for f in ("name", "symbol", "decimals", "totalsupply"))
        s2 = ("mintfree" in fns or "claimfree" in fns) and bool(free) and agent and is_token
        info.update({"S1": s1, "S2": s2, "has_mint": has_mint, "has_quote": has_quote,
                     "free_views": free, "agent_ref": agent, "is_token": is_token,
                     "n_fns": len(fns), "status": "checked",
                     "verifiedAt": data.get("verifiedAt")})
        if s1 or s2:
            shape_hits.append(addr)
    except Exception as e:
        info.update({"status": "shape-check-failed", "error": str(e)[:120]})
    seen[addr] = {"first_seen_wib": "2026-11-15T22:04:38+07:00",
                  "source": "hot-leg-2204", "status": info.get("status"),
                  "note": json.dumps(info)[:500]}
    out["shape"].append(info)

out["shape_check_targets"] = new
out["n_new_targets"] = len(new)
out["shape_hits"] = shape_hits
out["seen_added"] = new
out["seen_n"] = len(seen)
if new:
    json.dump(seen, open(SEEN_P, "w"), indent=1)

# Bridge (read-only)
try:
    br = json.load(open(BASE + "scan-bridge.json"))
    cons = br.get("contracts", {})
    snap = json.load(open(BASE + "onchain-snapshot.json"))
    snap_addrs = set()
    for sec in ("contracts", "track_c", "pending_claims"):
        for k, v in snap.get(sec, {}).items():
            a = v.get("address") if isinstance(v, dict) else k
            if a:
                snap_addrs.add(str(a).lower())
    not_in = [a for a, v in cons.items() if a.lower() not in snap_addrs]
    disc = [a for a, v in cons.items() if isinstance(v, dict) and v.get("same_owner_discarded")]
    out["bridge"] = {"ok": True, "contracts": len(cons),
                     "same_owner_discarded": len(disc),
                     "not_in_snapshot": len(not_in), "not_in_snapshot_list": not_in}
except Exception as e:
    out["bridge"] = {"ok": False, "error": str(e)[:120]}

out["elapsed_s"] = round(time.time() - t0, 1)
json.dump(out, open(BASE + "run-hot-leg-2026-11-15-2204.json", "w"), indent=1)
print(json.dumps(out, indent=1)[:4500])
print("ELAPSED", out["elapsed_s"])
