#!/usr/bin/env python3
"""Hot-leg 21:54 retry: legs 1-2 failed on egress flapping (Sourcify remote
closed; Boltbook IncompleteRead). One curl-based retry round only; if still
failing, legs stay skipped for next run. Updates run-hot-leg-2026-11-15-2154.json
and hot-leg-seen.json for any recovered new contracts."""
import json, re, subprocess, time
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
SEEN_P = BASE + "hot-leg-seen.json"
REG = "0x60b9262456de011f7d15a54cdd8c48baaa8b022f"
EXCLUDED = {"0x827e83e49bd7e15b67efa0e90fc25f17b8d96124",
            "0x8b47354e7b76b1970a0d06365c8244a810d37493"}
t0 = time.time()
out = json.load(open(BASE + "run-hot-leg-2026-11-15-2154.json"))

def curl(url, timeout=25):
    r = subprocess.run(["curl", "-sL", "--max-time", str(timeout), "-A", "Mozilla/5.0", url],
                       capture_output=True, text=True, timeout=timeout + 10)
    if r.returncode != 0 or not r.stdout:
        raise RuntimeError(f"curl rc={r.returncode} out={len(r.stdout)} err={r.stderr[:100]}")
    return r.stdout

# Sourcify retry
feed_addrs, feed_ok = [], False
try:
    feed = json.loads(curl("https://sourcify.dev/server/v2/contracts/56?limit=20&sort=desc", 25))
    items = feed if isinstance(feed, list) else feed.get("results", [])
    feed_addrs = [it.get("address") for it in items if it.get("address")]
    out["sourcify_feed"] = {"total": len(feed_addrs), "top": feed_addrs[0] if feed_addrs else None,
                            "top_verifiedAt": items[0].get("verifiedAt") if items else None,
                            "new": 0, "error": None, "recovered": "curl-retry"}
    out["legs"]["sourcify-retry"] = {"ok": True, "count": len(feed_addrs)}
    feed_ok = True
except Exception as e:
    out["legs"]["sourcify-retry"] = {"ok": False, "error": str(e)[:120]}

# Boltbook retry
bb_addrs = set()
for lang, url in (("en", "https://boltbook.fun/?lang=en"),
                  ("zh", "https://boltbook.fun/?lang=zh")):
    try:
        html = curl(url, 25)
        a = set(re.findall(r"0x[a-fA-F0-9]{40}", html))
        bb_addrs |= a
        out[f"boltbook_{lang}"] = {"bytes": len(html), "full_address_contracts": len(a),
                                   "error": None, "new": 0, "recovered": "curl-retry"}
        out["legs"][f"boltbook-{lang}-curl-retry"] = {"ok": True, "bytes": len(html), "addrs": len(a)}
    except Exception as e:
        out["legs"][f"boltbook-{lang}-curl-retry"] = {"ok": False, "error": str(e)[:120]}

seen = json.load(open(SEEN_P))
seen_keys = {k.lower() for k in seen}
new = [a for a in (feed_addrs + sorted(bb_addrs))
       if a.lower() not in seen_keys and a.lower() not in EXCLUDED]
new = list(dict.fromkeys(new))
out["new_contracts"] = new
out["sourcify_feed"]["new"] = sum(1 for a in feed_addrs if a.lower() not in seen_keys)

FREE_VIEWS = {"freesharesremaining", "freeclaimed", "freefor", "freeleft",
              "freeused", "freeavailable", "freesharepoolexhausted",
              "freesharesclaimed", "freeminted", "freeremaining"}
shape_hits = []
for addr in new:
    info = {"address": addr}
    try:
        data = json.loads(curl(
            f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi,metadata", 25))
        abi = data.get("abi") or []
        fns = [f.get("name", "").lower() for f in abi if f.get("type") == "function"]
        has_mint = any("mint" in f or "claim" in f for f in fns)
        has_quote = any("quote" in f or "cost" in f or "price" in f for f in fns)
        free = [f for f in fns if f in FREE_VIEWS]
        meta = json.dumps(data.get("metadata") or data)
        agent = REG in meta.lower() or "agentgate" in meta.lower() or any("agent" in f for f in fns)
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
    seen[addr] = {"first_seen_wib": "2026-11-15T21:54:38+07:00",
                  "source": "hot-leg-2154-retry", "status": info.get("status"),
                  "note": json.dumps(info)[:500]}
    out["shape"].append(info)
out["shape_check_targets"] = new
out["n_new_targets"] = len(new)
out["shape_hits"] = shape_hits
out["seen_added"] = new
out["seen_n"] = len(seen)
if new:
    json.dump(seen, open(SEEN_P, "w"), indent=1)
out["elapsed_s"] = round(time.time() - t0 + out.get("elapsed_s", 0), 1)
json.dump(out, open(BASE + "run-hot-leg-2026-11-15-2154.json", "w"), indent=1)
print(json.dumps({k: out[k] for k in ("sourcify_feed", "boltbook_en", "boltbook_zh",
      "new_contracts", "shape_hits", "seen_n")}, indent=1))
print("RETRY ELAPSED", round(time.time() - t0, 1))
