#!/usr/bin/env python3
"""Hot-leg run 2026-11-12 09:34 WIB (fresh script for this run only).
Leg 1: Sourcify feed new-vs-seen + ABI shape-check S1/S2.
Leg 2: Boltbook EN+ZH address extraction.
Retry: recent Sourcify-404 addresses (still shape-check-failed).
Bridge: read-only comparison vs snapshot contracts (address-based).
Leg 4: via run-2026-11-12-0934-verify2.py (separate script).
Stampooor site re-check included here.
Read-only except hot-leg-run-2026-11-12-0934.json + hot-leg-seen.json
additions for newly seen contracts. Never writes snapshot/seen/state
of the main job.
"""
import json, re, time, urllib.request, concurrent.futures, subprocess, os, glob

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
TS = "2026-11-12 09:34 WIB"
t0 = time.time()
out = {"run": "free-mint-hot-leg 2026-11-12 09:34 WIB", "started_wib": TS}

FREE_VIEWS = ["freeSharesRemaining", "freeClaimed", "freeFor", "freeLeft", "freeUsed",
              "freeAvailable", "freeSharePoolExhausted", "freeSharesClaimed",
              "freeMinted", "freeCardsRemaining"]
EXCLUDED = {"0x827e83e49bd7e15b67efa0e90fc25f17b8d96124",
            "0x8b47354e7b76b1970a0d06365c8244a810d37493"}

def get(url, timeout=20):
    req = urllib.request.Request(url, headers={"User-Agent": "free-bacot/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode(errors="replace")

# --- feed (already saved to /tmp) ---
feed = json.load(open("/tmp/run0934-feed.json"))
items = feed.get("results", [])
out["feed"] = {"n": len(items),
               "newest_verifiedAt": items[0].get("verifiedAt") if items else None,
               "oldest_verifiedAt": items[-1].get("verifiedAt") if items else None}

seen = {}
try:
    hl = json.load(open(BASE + "hot-leg-seen.json"))
    if isinstance(hl, dict):
        seen = hl
except Exception as e:
    out["seen_error"] = str(e)[:120]
seen_l = {k.lower() for k in seen.keys()}
# also treat addresses from recent feed snapshots as seen
for pf in glob.glob(BASE + "run-2026-11-12-*.json"):
    try:
        d = json.load(open(pf))
        for it in d.get("results", []):
            seen_l.add(str(it.get("address", "")).lower())
    except Exception:
        pass
new_addrs = [it.get("address") for it in items
             if str(it.get("address", "")).lower() not in seen_l and it.get("address")
             and str(it.get("address", "")).lower() not in EXCLUDED]
out["feed_new"] = new_addrs
json.dump(new_addrs, open(BASE + "run-2026-11-12-0934-feed-new.json", "w"), indent=1)

# --- Boltbook addresses ---
def addrs_from(path):
    try:
        txt = open(path, errors="replace").read()
    except Exception as e:
        return {"error": str(e)[:120]}
    found = sorted(set(a for a in re.findall(r"0x[a-fA-F0-9]{40}", txt)))
    return {"n_bytes": len(txt), "n_addrs": len(found), "addrs": found}

en = addrs_from("/tmp/run0934-bb-en.html")
zh = addrs_from("/tmp/run0934-bb-zh.html")
out["boltbook_en"] = en
out["boltbook_zh"] = zh
bb_new = [a for a in set(en.get("addrs", []) + zh.get("addrs", []))
          if a.lower() not in seen_l and a.lower() not in EXCLUDED]
out["boltbook_new"] = bb_new

# --- shape check for new addresses (feed + boltbook) + 404 retries ---
RETRY_404 = [
    "0x48C5673acAeEf5843Cd563eB87d1C8557B3659B8",
    "0x8773c3F08c6aA5Cb998Ff4a10956Fc6225DC52D3",
    "0x085469dd9f383aaf695e8ffdf28f2f3467e3963a",
    "0x13e21e9846d8a5b7e95f43219577d3bf92dd7306",
    "0xb889a72c579809b0ff62e1b299d8ed9c260c3f3e",
    "0x1ad04d56cddf66c515894feb2510740a263cf309",
    "0xb739b78f99c3bb53d722141b2c3c75735b03301c",
    "0xf379a6070eb04e3e9d8ea28f11f04bd8ff452b59",
    "0xe8EdC071e0F04656b957BAcfe212F6aAf0460A2A",
    "0xe2864db563e58cf048a01250b713afd286517181",
    "0x1111111111111111111111111111111111111111",
    "0x145a6186bcfa60be77403035ca53a767dd1d4bbb",
    "0x5c3cf93ab4ced159fc2c626fc94f1f4886a0e8fd",
    "0x7af5a52a9c00ff2143f2bac4eabf03e1e41950ad",
    "0x0bfa8bbd23530e4abbfdddaabcc407fee9587777",
]
out["retry_404"] = RETRY_404

def shape(addr):
    try:
        meta = json.loads(get(f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi", timeout=20))
        abi = meta.get("abi", [])
    except Exception as e:
        return {"address": addr, "error": f"{type(e).__name__}: {str(e)[:100]}"}
    fns = {}
    for e in abi:
        if e.get("type") == "function":
            fns.setdefault(e["name"], []).append(e)
    names = set(fns)
    lnames = {n.lower() for n in names}
    has_mint = any(n.lower().startswith("mint") for n in names)
    has_quote = bool(lnames & {"quote", "cost", "getquote", "mintcost", "price", "getprice", "mintprice"})
    free_views = sorted(names & set(FREE_VIEWS))
    agent_ref = bool(lnames & {"agentid", "agentregistry", "registry", "getagentid", "agentgate", "agentidregistry"})
    is_token = bool(names & {"name", "symbol", "decimals", "totalSupply"})
    mintfree = "mintFree" in fns and any(len(e.get("inputs", [])) == 0 for e in fns["mintFree"])
    s1 = has_mint and has_quote and bool(free_views) and agent_ref
    s2 = is_token and mintfree and bool(names & {"freeClaimed", "freeMinted"}) and bool(names & {"FREE_SLOTS", "FREE_SUPPLY"}) and agent_ref
    is_nft = bool(names & {"tokenURI", "ownerOf", "safeTransferFrom"}) or "uri" in names
    free_mint_fn = bool(names & {"freeMint", "mintFree", "claimFree"}) or any(n.lower().startswith("freemint") for n in names)
    early_shape = is_nft and (agent_ref or free_mint_fn)
    return {"address": addr, "S1": s1, "S2": s2, "early_shape": early_shape,
            "has_mint": has_mint, "has_quote": has_quote, "free_views": free_views,
            "agent_ref": agent_ref, "is_token": is_token, "is_nft": is_nft, "n_fns": len(abi)}

targets = sorted(set(new_addrs + bb_new + RETRY_404))
shapes = []
if targets:
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as ex:
        shapes = list(ex.map(shape, targets))
out["shapes"] = shapes
out["feed_shape"] = {"s1_pass": [s["address"] for s in shapes if s.get("S1")],
                     "s2_pass": [s["address"] for s in shapes if s.get("S2")],
                     "early_shape": [s["address"] for s in shapes if s.get("early_shape")]}
out["shape_check_failed_404_new"] = [s["address"] for s in shapes
    if s.get("error") and "404" in str(s.get("error")) and s["address"] in (new_addrs + bb_new)]
out["shape_check_failed_404_retry"] = [s["address"] for s in shapes
    if s.get("error") and "404" in str(s.get("error")) and s["address"] in RETRY_404]
print("FEED NEW:", new_addrs, "BOLTBOOK NEW:", bb_new)
print("S1:", out["feed_shape"]["s1_pass"], "S2:", out["feed_shape"]["s2_pass"],
      "EARLY:", out["feed_shape"]["early_shape"])
print("404 NEW:", out["shape_check_failed_404_new"], "404 RETRY:", out["shape_check_failed_404_retry"])

# --- record newly seen contracts in hot-leg-seen.json (own file only) ---
from datetime import datetime, timezone, timedelta
WIB = timezone(timedelta(hours=7))
now_wib = datetime.now(WIB).strftime("%Y-%m-%dT%H:%M:%S+07:00")
added = 0
shape_by_addr = {s["address"].lower(): s for s in shapes}
for a in list(new_addrs) + list(bb_new):
    if a.lower() in seen_l:
        continue
    s = shape_by_addr.get(a.lower(), {})
    src = "sourcify-feed" if a in new_addrs else "boltbook-frontpage"
    if s.get("error"):
        seen[a] = {"first_seen_wib": now_wib,
                   "note": f"run 0934 shape-check FAILED: {s.get('error')}",
                   "source": src, "status": "shape-check-failed"}
    else:
        seen[a] = {"first_seen_wib": now_wib,
                   "note": f"run 0934: S1={s.get('S1')} S2={s.get('S2')} early={s.get('early_shape')} mint={s.get('has_mint')} quote={s.get('has_quote')} free={s.get('free_views')} agent={s.get('agent_ref')} token={s.get('is_token')} fns={s.get('n_fns')}",
                   "source": src,
                   "status": "sale-shape-s1" if s.get("S1") else ("sale-shape-s2" if s.get("S2") else "checked-not-sale-shape")}
    added += 1
if added:
    with open(BASE + "hot-leg-seen.json", "w") as f:
        json.dump(seen, f, indent=1)
out["seen_added"] = added
out["seen_total"] = len(seen)
print("SEEN ADDED:", added, "TOTAL:", len(seen))

# --- bridge (read-only, address-based) ---
try:
    bridge = json.load(open(BASE + "scan-bridge.json"))
    bcontracts = bridge.get("contracts", {}) if isinstance(bridge, dict) else {}
    snap = json.load(open(BASE + "onchain-snapshot.json"))
    snap_addrs = set()
    for sec in ("contracts", "track_c", "pending_claims", "watchlist"):
        v = snap.get(sec)
        if isinstance(v, dict):
            for k, it in v.items():
                if isinstance(it, dict):
                    a = it.get("address", "")
                    if a:
                        snap_addrs.add(str(a).lower())
                elif isinstance(it, str) and it.startswith("0x"):
                    snap_addrs.add(it.lower())
    not_in_snap = [a for a in bcontracts if a.lower() not in snap_addrs]
    discarded = [a for a, v in bcontracts.items() if isinstance(v, dict) and v.get("same_owner_discarded")]
    out["bridge"] = {"n": len(bcontracts), "not_in_snapshot": not_in_snap,
                     "same_owner_discarded": discarded}
except Exception as e:
    out["bridge"] = {"error": f"{type(e).__name__}: {str(e)[:150]}"}
print("BRIDGE:", out["bridge"])

# --- Stampooor site re-check ---
STAMP = "0x467696af8c2206B977B24081445104632dc1D459"
stamp = {}
for label, url in (("root", "https://stampooor.com/"), ("packs", "https://stampooor.com/packs/")):
    try:
        r = subprocess.run(["curl", "-sL", "--max-time", "20", "-o", "/dev/null", "-w", "%{http_code} %{size_download}",
                            url], capture_output=True, text=True, timeout=25)
        stamp[label] = r.stdout.strip() or "(empty)"
    except Exception as e:
        stamp[label] = f"ERR {type(e).__name__}: {str(e)[:80]}"
try:
    r = subprocess.run(["curl", "-sL", "--max-time", "20", "https://stampooor.com/packs/"],
                       capture_output=True, text=True, timeout=25)
    if r.stdout:
        stamp["packs_prints_contract"] = STAMP.lower() in r.stdout.lower()
        stamp["packs_bytes"] = len(r.stdout)
except Exception as e:
    stamp["packs_fetch_err"] = f"{type(e).__name__}: {str(e)[:80]}"
out["stampooor_site"] = stamp
print("STAMPOOOR SITE:", stamp)

out["elapsed_s"] = round(time.time() - t0, 1)
json.dump(out, open(BASE + "hot-leg-run-2026-11-12-0934.json", "w"), indent=1)
print("LEGS DONE in", out["elapsed_s"], "s")
