#!/usr/bin/env python3
"""Hot-leg run 2026-11-06 07:19 WIB. Leg 1 (Sourcify feed + shape via
feed_shape_0001) + Leg 2 (Boltbook API). Same pattern as 07:14 run.
Writes only its own run files + hot-leg-seen.json. Never touches main snapshot."""
import json, urllib.request, subprocess, re, time, sys
sys.path.insert(0, "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files")
from feed_shape_0001 import sourcify_abi, classify

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TS = "2026-11-06-0719"
NOW = "2026-11-06T07:19:00+07:00"
EXCLUDED = ["0x827e83e49bd7e15b67efa0e90fc25f17b8d96124",
            "0x8b47354e7b76b1970a0d06365c8244a810d37493"]

# ---- Leg 1: Sourcify feed ----
feed = {"results": []}
try:
    req = urllib.request.Request(
        "https://sourcify.dev/server/v2/contracts/56?limit=20&sort=desc",
        headers={"User-Agent": "curl"})
    with urllib.request.urlopen(req, timeout=20) as r:
        feed = json.load(r)
    print("FEED OK urllib", len(feed.get("results", [])), flush=True)
except Exception as e:
    print("FEED FAIL urllib", repr(e), flush=True)
    try:
        out = subprocess.run(["curl", "-s", "--max-time", "20",
                              "https://sourcify.dev/server/v2/contracts/56?limit=20&sort=desc"],
                             capture_output=True, text=True, timeout=25)
        feed = json.loads(out.stdout)
        print("FEED OK via curl", len(feed.get("results", [])), flush=True)
    except Exception as e2:
        print("FEED FAIL curl", repr(e2), flush=True)
        feed = {"results": []}
json.dump(feed, open(f"{BASE}/run-{TS}-sourcify-feed.json", "w"), indent=1)
results = feed.get("results", [])
if results:
    print("FEED range", results[0].get("verifiedAt"), "->", results[-1].get("verifiedAt"), flush=True)

seen = json.load(open(f"{BASE}/hot-leg-seen.json"))
seen_l = {k.lower() for k in seen}
addrs = [x["address"] for x in results]
new = [a for a in addrs if a.lower() not in seen_l]
print("FEED", len(addrs), "NEW", len(new), new, flush=True)
vat = {it["address"].lower(): it.get("verifiedAt") for it in results}

shape_out = []
sale_shapes = []
for a in new:
    if a.lower() in EXCLUDED:
        seen[a] = {"first_seen_wib": NOW, "source": "sourcify-feed", "status": "excluded"}
        print(a, "EXCLUDED", flush=True)
        continue
    status, abi = sourcify_abi(a)
    r = {"address": a, "verifiedAt": vat.get(a.lower()), "sourcify": status}
    if abi is not None:
        r.update(classify(abi))
    else:
        r["S1"] = False; r["S2"] = False
    shape_out.append(r)
    print(a, status, "S1=", r.get("S1"), "S2=", r.get("S2"),
          "mint=", r.get("mint_fns"), "quote=", r.get("quote_fns"),
          "free=", r.get("free_views"), "agent=", r.get("gate_fns"),
          "token=", r.get("token_fns"), flush=True)
    if r.get("S1") or r.get("S2"):
        nft = r.get("nft_fns") or ("ownerOf" in str(r.get("abi_functions", [])))
        if r.get("nft"):
            seen[a] = {"first_seen_wib": NOW, "source": "sourcify-feed",
                       "status": "checked-not-track-c",
                       "note": f"Sourcify verifiedAt {vat.get(a.lower())}. S1/S2 literal pass BUT ERC-721 NFT, not a fungible share sale, so NOT a track-C lead. NFT early-lead stays with main job; never reported/previewed/minted."}
        else:
            seen[a] = {"first_seen_wib": NOW, "source": "sourcify-feed",
                       "status": "sale-shape-new", "S1": r.get("S1"), "S2": r.get("S2")}
            sale_shapes.append(a)
    elif abi is None:
        seen[a] = {"first_seen_wib": NOW, "source": "sourcify-feed",
                   "status": "checked-abi-unavailable",
                   "note": f"Sourcify verifiedAt {vat.get(a.lower())}. ABI fetch failed; no sale-shape evidence."}
    else:
        seen[a] = {"first_seen_wib": NOW, "source": "sourcify-feed",
                   "status": "checked-not-sale-shape",
                   "note": (f"Sourcify verifiedAt {vat.get(a.lower())}. "
                            f"S1={r.get('S1')} S2={r.get('S2')} mint={r.get('mint_fns')} "
                            f"quote={r.get('quote_fns')} free={r.get('free_views')} "
                            f"agent={r.get('gate_fns')} token={r.get('token_fns')}".replace("'", ""))}
json.dump(shape_out, open(f"{BASE}/run-{TS}-sourcify-shape.json", "w"), indent=1)
json.dump(seen, open(f"{BASE}/hot-leg-seen.json", "w"), indent=1)
print("SEEN total", len(seen), "SALE-SHAPES", sale_shapes, flush=True)

# ---- Leg 2: Boltbook via Lemmy API ----
try:
    req = urllib.request.Request(
        "https://boltbook.ai/api/v3/post/list?type_=All&sort=New&limit=50",
        headers={"User-Agent": "curl"})
    with urllib.request.urlopen(req, timeout=20) as r:
        bb = json.load(r)
    json.dump(bb, open(f"{BASE}/hot-leg-{TS}-boltbook-api.json", "w"), indent=1)
    posts = bb.get("posts", [])
    print("BOLTBOOK OK", len(posts), "newest",
          posts[0]["post"].get("published") if posts else None, flush=True)
    kws_en = ["free share", "first share free", "1 free share", "free mint share", "free mint"]
    kws_zh = ["免费份额", "首个免费", "免费铸造", "免费mint"]
    hits = []
    addr_re = re.compile(r"0x[a-fA-F0-9]{40}")
    addrs_found = set()
    for p in posts:
        post = p.get("post", {})
        text = ((post.get("name") or "") + " " + (post.get("body") or "")).lower()
        if any(k in text for k in kws_en + kws_zh):
            hits.append((post.get("id"), post.get("name"), post.get("ap_id")))
        for m in addr_re.findall(post.get("name", "") + " " + (post.get("body") or "")):
            addrs_found.add(m)
    print("BOLTBOOK keyword hits:", len(hits), hits, flush=True)
    print("BOLTBOOK addresses in 50 posts:", sorted(addrs_found), flush=True)
    for m in sorted(addrs_found):
        print("  addr in seen:", m.lower() in seen_l, m, flush=True)
except Exception as e:
    print("BOLTBOOK FAIL", repr(e), flush=True)
print("DONE", time.strftime("%H:%M:%S"), flush=True)
