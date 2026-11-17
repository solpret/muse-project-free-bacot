#!/usr/bin/env python3
"""Discovery for free-mint-search run 2026-11-13 09:31: Sourcify
recently-verified feed (limit 20) + Boltbook front page EN+ZH, shape-check
only contracts new vs hot-leg-seen.json. Read-only; writes
run-2026-11-13-0931-discovery.json."""
import json, re, subprocess, time
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
def curl(url, timeout=25):
    try:
        out = subprocess.run(["curl", "-sL", "--max-time", str(timeout), url],
                             capture_output=True, text=True, timeout=timeout + 5).stdout
        return out
    except Exception as e:
        return ""
def main():
    t0 = time.time()
    out = {"started_wib": "2026-11-13T09:31+07:00"}
    seen = {}
    try:
        seen = json.load(open(BASE + "hot-leg-seen.json"))
    except Exception as e:
        out["seen_load_error"] = str(e)[:100]
    seen_addrs = set()
    if isinstance(seen, dict):
        for k in seen.keys():
            seen_addrs.add(k.lower())
        out["seen_total"] = len(seen)
    # Sourcify feed
    raw = curl("https://sourcify.dev/server/v2/contracts/56?limit=20&sort=desc", 25)
    feed_new = []
    try:
        fj = json.loads(raw)
        items = fj.get("results", fj if isinstance(fj, list) else [])
        out["feed_n"] = len(items)
        for it in items:
            a = (it.get("address") or "").lower()
            va = it.get("verifiedAt") or it.get("match", {}).get("verifiedAt")
            if a and a not in seen_addrs:
                feed_new.append({"address": it.get("address"), "verifiedAt": va})
        out["feed_new"] = feed_new
    except Exception as e:
        out["feed_error"] = str(e)[:200] + " raw_len=" + str(len(raw))
    # Shape-check feed_new via Sourcify ABI
    out["feed_shape"] = {}
    for it in feed_new:
        a = it["address"]
        try:
            meta = curl(f"https://sourcify.dev/server/v2/contract/56/{a}?fields=abi", 20)
            mj = json.loads(meta)
            abi = mj.get("abi") or (mj.get("stdJson", {}).get("output", {}).get("abi")) or []
            fns = [f.get("name") for f in abi if f.get("type") == "function"]
            src = json.dumps(mj).lower()
            has_mint = any(n in fns for n in ("mint", "claimFree", "mintFree", "claimFreeAgent"))
            has_quote = any("quote" in n.lower() or "cost" in n.lower() for n in fns)
            free_views = [n for n in fns if "free" in n.lower()]
            agent = ("0x60b9262456de011f7d15a54cdd8c48baaa8b022f" in src) or ("agent" in " ".join(fns).lower())
            out["feed_shape"][a] = {"S1": bool(has_mint and has_quote and free_views and agent),
                                    "mint": has_mint, "quote": has_quote,
                                    "free": free_views, "agent": agent, "n_fns": len(fns),
                                    "status": "checked"}
        except Exception as e:
            out["feed_shape"][a] = {"status": "shape-check-failed", "error": str(e)[:120]}
    # Boltbook EN + ZH
    out["boltbook"] = {}
    for lang, url in (("en", "https://boltbook.fun/"), ("zh", "https://boltbook.fun/?lang=zh")):
        html = curl(url, 25)
        addrs = sorted(set(re.findall(r"0x[a-fA-F0-9]{40}", html)))
        out["boltbook"][lang] = {"bytes": len(html), "addrs": addrs,
                                 "new": [a for a in addrs if a.lower() not in seen_addrs]}
    out["elapsed_s"] = round(time.time() - t0, 1)
    print(json.dumps(out, indent=1))
    json.dump(out, open(BASE + "run-2026-11-13-0931-discovery.json", "w"), indent=1)
if __name__ == "__main__":
    main()
