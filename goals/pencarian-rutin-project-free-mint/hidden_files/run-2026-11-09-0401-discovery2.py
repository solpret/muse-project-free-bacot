#!/usr/bin/env python3
"""Run 2026-11-09 04:01 WIB — fix-up: Boltbook addr diff + Sourcify feed (results[])
+ shape-check new contracts. Read-only vs snapshot.
"""
import json, re, time, urllib.request
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TS = "2026-11-09-0401"
T0 = time.time()
out = {}

# Boltbook addrs from curl-saved HTML
ADDR_RE = re.compile(r"0x[0-9a-fA-F]{40}")
en = open(f"{BASE}/run-{TS}-boltbook-en.html").read()
zh = open(f"{BASE}/run-{TS}-boltbook-zh.html").read()
en_a = sorted(set(ADDR_RE.findall(en))); zh_a = sorted(set(ADDR_RE.findall(zh)))
all_bb = sorted(set(en_a) | set(zh_a))
snap = json.load(open(f"{BASE}/onchain-snapshot.json"))
snap_addrs = {str(v.get("address", "")).lower() for v in snap.get("contracts", {}).values() if isinstance(v, dict)}
seen = json.load(open(f"{BASE}/onchain-scan-seen.json"))
seen_low = {k.lower() for k in seen}
new_bb = [a for a in all_bb if a.lower() not in snap_addrs and a.lower() not in seen_low]
out["boltbook"] = {"en_bytes": len(en), "zh_bytes": len(zh), "en_addrs": len(en_a),
                   "zh_addrs": len(zh_a), "unique": len(all_bb),
                   "new_vs_snapshot_seen": new_bb}
print(f"BOLTBOOK en={len(en)} zh={len(zh)} unique={len(all_bb)} new={new_bb}", flush=True)

# Sourcify feed, proper parse
def get_json(url, timeout=25):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    return json.loads(urllib.request.urlopen(req, timeout=timeout).read())

feed = get_json("https://sourcify.dev/server/v2/contracts/56?limit=20&sort=desc")
results = feed.get("results", []) if isinstance(feed, dict) else feed
addrs = [r.get("address") for r in results if isinstance(r, dict) and r.get("address")]
out["sourcify_feed"] = {"n": len(addrs), "addrs": addrs,
                        "verifiedAt": [r.get("verifiedAt") for r in results if isinstance(r, dict)][:5]}
print("SOURCIFY feed:", len(addrs), flush=True)

# diff vs hot-leg seen (its sourcify.json holds last feed addrs)
hl_seen = set()
try:
    hl = json.load(open(f"{BASE}/hot-leg-seen.json"))
    hl_seen = {k.lower() for k in hl} if isinstance(hl, dict) else set()
except Exception:
    pass
# hot-leg sourcify files: latest
import glob
latest_feed = None
for f in sorted(glob.glob(f"{BASE}/hot-leg-*-sourcify.json"), reverse=True):
    try:
        latest_feed = json.load(open(f)); break
    except Exception:
        continue
prev_feed = set(a.lower() for a in latest_feed) if isinstance(latest_feed, list) else set()
new_feed = [a for a in addrs if a.lower() not in prev_feed and a.lower() not in snap_addrs]
out["sourcify_new_vs_hotleg"] = new_feed
print("SOURCIFY new vs hot-leg feed:", new_feed, flush=True)

# shape-check new feed contracts (S1/S2 sale shape + agent-mint shape)
REG = "60b9262456de011f7d15a54cdd8c48baaa8b022f"
def shape_check(addr):
    try:
        d = get_json(f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi", timeout=15)
    except Exception as e:
        return {"address": addr, "sourcify": f"error:{type(e).__name__}"}
    abi = d.get("abi") or []
    fns = set()
    for e in abi:
        if isinstance(e, dict) and e.get("type") == "function":
            fns.add(e.get("name", ""))
    has = lambda *names: any(n in fns for n in names)
    s1 = has("mint") and has("quote", "priceOf", "costOf", "price") and has(
        "freeSharesRemaining", "freeClaimed", "freeFor", "freeLeft", "freeUsed",
        "freeAvailable", "freeSharePoolExhausted", "freeSharesClaimed", "freeMinted")
    s2 = has("mintFree", "claimFree") and has("freeClaimed", "freeMinted")
    agent = has("agentId", "agentRegistry", "registry", "AGENT_ID", "isAgent", "agentGate")
    return {"address": addr, "sourcify": "verified", "fns": sorted(fns),
            "S1": bool(s1), "S2": bool(s2), "agent_fn": bool(agent),
            "mint_fn": has("mint", "mintFree", "claimFree"),
            "free_view": has("freeClaimed", "freeMinted", "freeLeft", "freeSharesRemaining", "freeFor", "freeAvailable")}
shapes = {}
for a in new_feed:
    shapes[a] = shape_check(a)
    print("SHAPE", a, {k: v for k, v in shapes[a].items() if k != "fns"}, flush=True)
    time.sleep(0.5)
out["sourcify_shapes"] = shapes
out["duration_s"] = round(time.time() - T0, 1)
json.dump(out, open(f"{BASE}/run-{TS}-discovery2.json", "w"), indent=1)
print("DONE", out["duration_s"], "s", flush=True)
