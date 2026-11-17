#!/usr/bin/env python3
"""Hot-leg 1249 recovery: legs 1-2 script was killed by an exec-service restart
after writing feed/shape/Boltbook files but before the final seen dump + legs12 log.
This script replays ONLY the bookkeeping from the already-fetched files (no re-fetch):
- records the 8 new Sourcify feed contracts into hot-leg-seen.json
- writes hot-leg-2026-11-08-1249-legs12.log so the leg4 script can do its
  Boltbook pending recheck (0xdEaD + 0x297c... left unrecorded by legs1-2 itself;
  leg4's recheck decides EOA vs contract).
"""
import json, re, time
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
TAG = "hot-leg-2026-11-08-1249"
EXCLUDED = {"0x827e83e49bd7e15b67efa0e90fc25f17b8d96124",
            "0x8b47354e7b76b1970a0d06365c8244a810d37493"}
REGISTRY = "0x60b9262456de011f7d15a54cdd8c48baaa8b022f"
seen = json.load(open(BASE + "hot-leg-seen.json"))
seen_lower = {k.lower() for k in seen}

feed = json.load(open(BASE + TAG + "-sourcify.json"))
results = feed.get("results", feed) if isinstance(feed, dict) else feed
feed_addrs = []
for e in results:
    a = e if isinstance(e, str) else (e.get("address") or (e.get("contract") or {}).get("address"))
    if a:
        feed_addrs.append(a)
shapes = json.load(open(BASE + TAG + "-sourcify-shape.json"))
shape_by_addr = {s["address"].lower(): s for s in shapes}
new1 = [a for a in feed_addrs if a.lower() not in seen_lower and a.lower() not in EXCLUDED]
excl1 = [a for a in feed_addrs if a.lower() in EXCLUDED]
for a in new1:
    s = shape_by_addr.get(a.lower(), {})
    if s.get("error") or not s.get("abi_functions"):
        continue
    fns = s.get("abi_functions") or []
    if (s.get("S1") or s.get("S2")) and "ownerOf" in fns:
        seen[a] = {"first_seen_wib": "2026-11-08T12:49:00+07:00", "source": "sourcify-feed",
                   "status": "checked-not-track-c",
                   "note": f"S1={s['S1']} S2={s['S2']} BUT ERC-721 NFT (ownerOf/tokenURI/royaltyInfo), not a fungible share sale. NFT early-lead stays with main job; never reported/previewed/minted by hot leg. fns={fns}"}
    elif s.get("S1") or s.get("S2"):
        seen[a] = {"first_seen_wib": "2026-11-08T12:49:00+07:00", "source": "sourcify-feed",
                   "status": "sale-shape-pass",
                   "note": f"S1={s['S1']} S2={s['S2']} fns={fns}"}
    else:
        seen[a] = {"first_seen_wib": "2026-11-08T12:49:00+07:00", "source": "sourcify-feed",
                   "status": "checked-not-sale-shape",
                   "note": f"S1={s['S1']} S2={s['S2']} mint={s['mint']} quote={s['quote']} free={s['free']} agent={s['agent']} token={s['token']}"}

# --- Boltbook EN/ZH from the saved html (no re-fetch) ---
snap = json.load(open(BASE + "onchain-snapshot.json"))
snap_addrs = set()
for v in snap.get("contracts", {}).values():
    if isinstance(v, dict):
        for f in ("address", "sale", "token"):
            if v.get(f):
                snap_addrs.add(v[f].lower())
KW_EN = ["free share", "first share free", "1 free share", "free mint share"]
KW_ZH = ["免费份额", "首个免费", "免费铸造", "免费mint"]
bolt = {}
for lang in ("en", "zh"):
    html = open(BASE + TAG + f"-boltbook-{lang}.html").read()
    found = sorted(set(re.findall(r"0x[0-9a-fA-F]{40}", html)))
    low = html.lower()
    kws = {k: low.count(k.lower()) for k in (KW_EN if lang == "en" else KW_ZH)}
    newfound = [a for a in found if a.lower() not in seen_lower and a.lower() not in EXCLUDED
                and a.lower() != REGISTRY]
    new_vs_snap = [a for a in newfound if a.lower() not in snap_addrs]
    bolt[lang] = {"bytes": len(html), "rc": 0, "addrs": len(found), "keyword_hits": kws,
                  "new_vs_seen": newfound, "new_vs_snapshot": new_vs_snap, "shape_check": {}}
    # legs1-2 itself records nothing from Boltbook here: 0xdEaD is the burn address
    # and 0x297c... had code 0x + ABI 0 fns (checked separately); both are left for
    # the leg4 pending recheck, exactly as the 1239 run did for its pending addrs.

log = {"run": "free-mint-hot-leg 2026-11-08 12:49:38 WIB legs1-2 (recovered bookkeeping)",
       "recovery_note": "legs1-2 script killed by exec-service restart after fetches; bookkeeping replayed from saved files, no re-fetch.",
       "leg1_feed": {"n": len(feed_addrs), "addrs": feed_addrs},
       "leg1": {"new": new1, "new_excluded_rediscovered": excl1, "shapes": shapes,
                "seen_total": len(seen)},
       "leg2_boltbook": bolt,
       "seen_total_after": len(seen)}
json.dump(seen, open(BASE + "hot-leg-seen.json", "w"), indent=1)
json.dump(log, open(BASE + TAG + "-legs12.log", "w"), indent=1)
print(json.dumps({"recorded_sourcify_new": new1, "excluded_rediscovered": excl1,
                  "boltbook": {k: {"new_vs_snapshot": v["new_vs_snapshot"], "kw": v["keyword_hits"]}
                               for k, v in bolt.items()},
                  "seen_total_after": len(seen)}, indent=1))
