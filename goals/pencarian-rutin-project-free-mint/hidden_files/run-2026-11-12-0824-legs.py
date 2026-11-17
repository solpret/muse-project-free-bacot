#!/usr/bin/env python3
"""Hot-leg run 2026-11-12 08:24 WIB (fresh script for this run only).
Leg 1: Sourcify feed new-vs-seen + ABI shape-check S1/S2.
Leg 2: Boltbook EN+ZH address extraction.
Bridge: read-only comparison vs snapshot contracts (address-based).
Read-only except run-2026-11-12-0824-*.json outputs in this dir.
Never writes snapshot/seen/state of the main job.
"""
import json, re, time, urllib.request, concurrent.futures

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
TS = "2026-11-12 08:24 WIB"
t0 = time.time()
out = {"started_wib": TS}

FREE_VIEWS = ["freeSharesRemaining", "freeClaimed", "freeFor", "freeLeft", "freeUsed",
              "freeAvailable", "freeSharePoolExhausted", "freeSharesClaimed",
              "freeMinted", "freeCardsRemaining"]
REGISTRY = "0x60b9262456de011f7d15a54cdd8c48baaa8b022f"

def get(url, timeout=20):
    req = urllib.request.Request(url, headers={"User-Agent": "free-bacot/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode(errors="replace")

feed = json.load(open("/tmp/run0824-feed.json"))
items = feed.get("results", [])
out["feed"] = {"n": len(items),
               "newest_verifiedAt": items[0].get("verifiedAt") if items else None,
               "oldest_verifiedAt": items[-1].get("verifiedAt") if items else None}

seen = set()
try:
    hl = json.load(open(BASE + "hot-leg-seen.json"))
    if isinstance(hl, dict):
        seen |= {k.lower() for k in hl.keys()}
    elif isinstance(hl, list):
        seen |= {str(x).lower() for x in hl}
except Exception as e:
    out["seen_error"] = str(e)[:120]
out["seen_total"] = len(seen)
new_addrs = [it.get("address") for it in items
             if str(it.get("address", "")).lower() not in seen and it.get("address")]
out["feed_new"] = new_addrs
json.dump(new_addrs, open(BASE + "run-2026-11-12-0824-feed-new.json", "w"), indent=1)

def addrs_from(path):
    try:
        txt = open(path, errors="replace").read()
    except Exception as e:
        return {"error": str(e)[:120]}
    found = sorted(set(a for a in re.findall(r"0x[a-fA-F0-9]{40}", txt)))
    return {"n_bytes": len(txt), "n_addrs": len(found), "addrs": found}

en = addrs_from("/tmp/run0824-bb-en.html")
zh = addrs_from("/tmp/run0824-bb-zh.html")
out["boltbook_en"] = en
out["boltbook_zh"] = zh
bb_new = [a for a in set(en.get("addrs", []) + zh.get("addrs", []))
          if a.lower() not in seen]
out["boltbook_new"] = bb_new

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

targets = sorted(set(new_addrs + bb_new))
shapes = []
if targets:
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as ex:
        shapes = list(ex.map(shape, targets))
out["shapes"] = shapes
out["elapsed_s"] = round(time.time() - t0, 1)

try:
    bridge = json.load(open(BASE + "scan-bridge.json"))
    baddrs = bridge if isinstance(bridge, list) else bridge.get("contracts", bridge.get("items", []))
    if isinstance(baddrs, list) and baddrs and isinstance(baddrs[0], dict):
        baddrs = [str(x.get("address", x.get("contract", ""))) for x in baddrs]
    baddrs = [str(a) for a in baddrs if a]
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
    not_in_snap = [a for a in baddrs if a.lower() not in snap_addrs]
    discarded = []
    if isinstance(bridge, dict):
        for k, v in bridge.items():
            if isinstance(v, dict) and v.get("same_owner_discarded"):
                discarded.append(k)
    out["bridge"] = {"n": len(baddrs), "not_in_snapshot": not_in_snap,
                     "same_owner_discarded": discarded}
except Exception as e:
    out["bridge"] = {"error": f"{type(e).__name__}: {str(e)[:150]}"}

json.dump(out, open(BASE + "run-2026-11-12-0824-legs.json", "w"), indent=1)
print(json.dumps(out, indent=1)[:7000])
print("ELAPSED", round(time.time() - t0, 1))
