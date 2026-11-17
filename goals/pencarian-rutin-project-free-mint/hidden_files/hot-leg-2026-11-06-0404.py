#!/usr/bin/env python3
"""Hot-leg run 2026-11-06 04:04 WIB. Leg 1 (Sourcify feed + shape) + Leg 2 (Boltbook API).
Writes only its own run files + hot-leg-seen.json. Never touches main snapshot."""
import json, urllib.request, subprocess, re, time
from concurrent.futures import ThreadPoolExecutor

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TS = "2026-11-06-0404"
NOW = "2026-11-06 04:04 WIB"
REG = "60b9262456de011f7d15a54cdd8c48baaa8b022f"
FREE = ["freeSharesRemaining", "freeClaimed", "freeFor", "freeLeft", "freeUsed",
        "freeAvailable", "freeSharePoolExhausted", "freeSharesClaimed"]

# ---- Leg 1: Sourcify feed ----
try:
    req = urllib.request.Request(
        "https://sourcify.dev/server/v2/contracts/56?limit=20&sort=desc",
        headers={"User-Agent": "curl"})
    with urllib.request.urlopen(req, timeout=20) as r:
        feed = json.load(r)
    json.dump(feed, open(f"{BASE}/hot-leg-{TS}-sourcify.json", "w"), indent=1)
    results = feed.get("results", [])
    print("FEED OK", len(results), "verified",
          results[0].get("verifiedAt") if results else None, "->",
          results[-1].get("verifiedAt") if results else None, flush=True)
except Exception as e:
    print("FEED FAIL", repr(e), flush=True)
    feed = {"results": []}

seen = json.load(open(f"{BASE}/hot-leg-seen.json"))
seen_l = {k.lower() for k in seen}
addrs = [x["address"] for x in feed.get("results", [])]
new = [a for a in addrs if a.lower() not in seen_l]
excluded = ["0x827e83e49bd7e15b67efa0e90fc25f17b8d96124",
            "0x8b47354e7b76b1970a0d06365c8244a810d37493"]
new_ne = [a for a in new if a.lower() not in excluded]
print("FEED", len(addrs), "NEW", len(new), new, flush=True)

def abi_of(a):
    for getter in ("urllib", "curl"):
        try:
            if getter == "urllib":
                req = urllib.request.Request(
                    f"https://sourcify.dev/server/v2/contract/56/{a}?fields=abi",
                    headers={"User-Agent": "curl"})
                with urllib.request.urlopen(req, timeout=15) as r:
                    d = json.load(r)
            else:
                out = subprocess.run(["curl", "-s", "--max-time", "15",
                                      f"https://sourcify.dev/server/v2/contract/56/{a}?fields=abi"],
                                     capture_output=True, text=True, timeout=20)
                d = json.loads(out.stdout)
            return d.get("abi") or d.get("stdJson", {}).get("abi") or []
        except Exception:
            continue
    return {"error": "abi-unavailable"}

def shape_of(a):
    abi = abi_of(a)
    if isinstance(abi, dict):
        return {"error": abi.get("error", "abi-unavailable"), "S1": False, "S2": False,
                "mint": False, "quote": False, "free": [], "agent": False, "token": False}
    fns = sorted({f.get("name") for f in abi if f.get("type") == "function" and f.get("name")})
    has_mint = any(n.startswith("mint") for n in fns)
    has_quote = "quote" in fns
    free = [f for f in fns if any(x in f for x in FREE)]
    agent = ("agentRegistry" in fns or "AGENT_REGISTRY" in fns or "registry" in fns
             or REG in json.dumps(abi).lower())
    is_token = all(x in fns for x in ("name", "symbol", "decimals", "totalSupply"))
    has_mintfree = "mintFree" in fns
    s1 = has_mint and has_quote and bool(free) and agent
    s2 = is_token and has_mintfree and ("freeClaimed" in fns or "freeMinted" in fns) \
        and ("FREE_SLOTS" in fns or "FREE_SUPPLY" in fns) and agent
    nft = ("ownerOf" in fns or "tokenURI" in fns)
    return {"abi_functions": fns, "S1": s1, "S2": s2, "mint": has_mint,
            "quote": has_quote, "free": free, "agent": agent, "token": is_token, "nft": nft}

shape = {}
with ThreadPoolExecutor(max_workers=4) as ex:
    for a, sh in zip(new_ne, ex.map(shape_of, new_ne)):
        shape[a] = sh
        print("SHAPE", a, "S1", sh["S1"], "S2", sh["S2"], "mint", sh["mint"], "quote", sh["quote"],
              "free", sh["free"], "agent", sh["agent"], "token", sh["token"], "nft", sh.get("nft"),
              sh.get("error", ""), flush=True)
json.dump(shape, open(f"{BASE}/run-{TS}-sourcify-shape.json", "w"), indent=1)
for a in new:
    if a.lower() in excluded:
        seen[a] = {"first_seen": NOW, "status": "excluded"}
    else:
        sh = shape.get(a, {})
        if sh.get("S1") or sh.get("S2"):
            if sh.get("nft"):
                seen[a] = {"first_seen": NOW, "status": "checked-not-track-c",
                           "note": "S1/S2 literal pass BUT ERC-721 NFT (ownerOf/tokenURI), not a fungible share sale, so NOT a track-C lead. NFT early-lead stays with main job; never reported/previewed/minted."}
            else:
                seen[a] = {"first_seen": NOW, "status": "sale-shape-new",
                           "S1": sh["S1"], "S2": sh["S2"]}
        elif sh.get("error"):
            seen[a] = {"first_seen": NOW, "status": "checked-abi-unavailable"}
        else:
            seen[a] = {"first_seen": NOW, "status": "checked-not-sale-shape"}
json.dump(seen, open(f"{BASE}/hot-leg-seen.json", "w"), indent=1)
print("SEEN total", len(seen), flush=True)

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
