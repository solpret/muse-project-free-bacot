#!/usr/bin/env python3
"""hot-leg 2026-11-10 00:44 run: Sourcify feed + Boltbook en/zh + bridge (read-only)
+ re-read of the 48-item set vs 00:39 baseline (hot-leg-2026-11-10-0039-reread.json).
Read-only except hot-leg-seen.json (new contracts) + this run's own outputs.
Skips any leg that stalls."""
import json, re, subprocess, sys, time, urllib.request, urllib.error
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EP = "https://bsc.nodereal.io/"
NOW = "2026-11-10 00:44 WIB"
EXCLUDED = {"0x827e83e49bd7e15b67efa0e90fc25f17b8d96124",
            "0x8b47354e7b76b1970a0d06365c8244a810d37493"}
REGISTRY = "0x60b9262456de011f7d15a54cdd8c48baaa8b022f"

def fetch(url, timeout=15):
    req = urllib.request.Request(url, headers={"User-Agent": "hot-leg/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()

def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode())
    return "0x" + k.hexdigest()[:8]

def enc_addr(a): return a.lower().replace("0x", "").rjust(64, "0")
def enc_uint(n): return format(n, "064x")

NOARG = ["totalSupply", "totalMinted", "totalMints", "freeMinted", "freeClaimed",
         "freeMintedTotal", "freeLeft", "freeUsed", "FREE_CAP", "FREE_SUPPLY",
         "FREE_SHARES", "FREE_QUOTA", "FREE_PER_WALLET", "remainingFree",
         "MAX_SUPPLY", "MAX_FREE", "sharesMinted", "sold", "phase", "launched",
         "soldOut", "closed", "finalized", "mintOpen", "mintActive"]
ADDRARG = ["balanceOf", "mintedBy", "freeClaimed", "freeLeft", "freeUsed",
           "freeCount", "freeMinted", "mintedCount", "freeAvailable",
           "hasMinted", "quotaOf", "freeTakenBy", "priceFor"]
ADDRUINT = ["quote", "freeFor"]

def calldata(field):
    if field in ("address", "_batch_fail"): return None
    if field.endswith("_user1"):
        fn = field[:-6]
        if fn in ADDRUINT: return sel(f"{fn}(address,uint256)") + enc_addr(USER) + enc_uint(1)
        return None
    if field.endswith("_user"):
        fn = field[:-5]
        if fn in ADDRARG: return sel(f"{fn}(address)") + enc_addr(USER)
        return None
    if field in NOARG: return sel(f"{field}()")
    return None

def run_batch(calls):
    payload = json.dumps([{"jsonrpc": "2.0", "id": i, "method": "eth_call",
                           "params": [{"to": to, "data": data}, "latest"]}
                          for i, (to, data) in enumerate(calls)])
    p = subprocess.run(["curl", "-s", "--max-time", "30", "-X", "POST", EP,
                        "-H", "Content-Type: application/json", "--data", payload],
                       capture_output=True, text=True)
    try: return json.loads(p.stdout)
    except Exception: return {"_curl_error": p.stdout[:200] + p.stderr[:200]}

def decode(r):
    if not isinstance(r, str) or not r.startswith("0x"): return None
    try: return int(r, 16)
    except Exception: return None

out = {"run": "free-mint-hot-leg 2026-11-10 00:44 WIB (scheduled 00:44:38 WIB)"}
t0 = time.time()

# ---- Leg 1: Sourcify feed ----
seen = json.load(open(BASE + "hot-leg-seen.json"))
seen_lower = {k.lower() for k in seen}
try:
    raw = fetch("https://sourcify.dev/server/v2/contracts/56?limit=20&sort=desc", 15)
    feed = json.loads(raw)
    addrs = []
    for e in feed if isinstance(feed, list) else feed.get("results", []):
        a = e.get("address") or (e.get("contract") or {}).get("address")
        if a: addrs.append(a)
    out["leg1_feed"] = {"n": len(addrs), "addrs": addrs, "error": None}
except Exception as e:
    addrs = []
    out["leg1_feed"] = {"n": 0, "addrs": [], "error": f"{type(e).__name__}: {e}"}
new_feed = [a for a in addrs if a.lower() not in seen_lower and a.lower() != REGISTRY.lower()]
out["leg1"] = {"new": new_feed,
               "new_excluded_rediscovered": [a for a in new_feed if a.lower() in EXCLUDED],
               "shapes": {}, "seen_total": len(seen)}
# shape-check genuinely new non-excluded contracts via the 1219 shape script
to_shape = [a for a in new_feed if a.lower() not in EXCLUDED]
if to_shape:
    try:
        p = subprocess.run([sys.executable, BASE + "hot-leg-1219-shape.py"] + to_shape,
                           capture_output=True, text=True, timeout=90)
        out["leg1"]["shapes"] = json.loads(p.stdout) if p.stdout.strip().startswith("{") else {"raw": p.stdout[:500], "stderr": p.stderr[:500]}
    except Exception as e:
        out["leg1"]["shapes"] = {"error": f"{type(e).__name__}: {e}"}
for a in new_feed:
    seen[a] = {"first_seen_wib": NOW, "source": "sourcify-feed",
               "status": "checked-excluded" if a.lower() in EXCLUDED else "checked-new-0044",
               "note": "Excluded example rediscovered; recorded, not reported." if a.lower() in EXCLUDED else str(out["leg1"]["shapes"].get(a, {}))[:400]}

# ---- Leg 2: Boltbook en + zh ----
kw_en = ["free share", "first share free", "1 free share", "free mint share"]
kw_zh = ["免费份额", "首个免费", "免费铸造", "免费mint"]
bb = {}
for lang, url in (("en", "https://boltbook.fun/?lang=en"), ("zh", "https://boltbook.fun/?lang=zh")):
    try:
        html = fetch(url, 15).decode("utf-8", "ignore")
        bb[lang] = {"bytes": len(html), "err": None,
                    "addrs": sorted({m.lower() for m in re.findall(r"0x[0-9a-fA-F]{40}", html)}),
                    "kw": {k: html.lower().count(k.lower()) for k in (kw_en if lang == "en" else kw_zh)}}
    except Exception as e:
        bb[lang] = {"bytes": 0, "err": f"{type(e).__name__}: {e}", "addrs": [], "kw": {}}
all_bb = sorted(set(bb["en"]["addrs"]) | set(bb["zh"]["addrs"]))
bb_new = [a for a in all_bb if a.lower() not in seen_lower and a.lower() != REGISTRY.lower()]
out["leg2_boltbook"] = {"en_bytes": bb["en"]["bytes"], "en_err": bb["en"]["err"],
                        "zh_bytes": bb["zh"]["bytes"], "zh_err": bb["zh"]["err"],
                        "en_addrs": len(bb["en"]["addrs"]), "zh_addrs": len(bb["zh"]["addrs"]),
                        "unique_addrs": len(all_bb),
                        "keyword_hits": {**bb["en"].get("kw", {}), **bb["zh"].get("kw", {})},
                        "new_vs_seen": bb_new, "new_vs_snapshot": [], "shape_check": {}}
to_shape_bb = [a for a in bb_new if a.lower() not in EXCLUDED]
if to_shape_bb:
    try:
        p = subprocess.run([sys.executable, BASE + "hot-leg-1219-shape.py"] + to_shape_bb,
                           capture_output=True, text=True, timeout=90)
        out["leg2_boltbook"]["shape_check"] = json.loads(p.stdout) if p.stdout.strip().startswith("{") else {"raw": p.stdout[:500]}
    except Exception as e:
        out["leg2_boltbook"]["shape_check"] = {"error": f"{type(e).__name__}: {e}"}
for a in bb_new:
    seen[a] = {"first_seen_wib": NOW, "source": "boltbook-frontpage",
               "status": "checked-excluded" if a.lower() in EXCLUDED else "checked-new-0044",
               "note": "Excluded example rediscovered; recorded, not reported." if a.lower() in EXCLUDED else str(out["leg2_boltbook"]["shape_check"].get(a, {}))[:400]}
out["leg1"]["seen_total"] = len(seen)
out["leg2_boltbook"]["seen_total"] = len(seen)

# ---- Bridge leg (read-only) ----
try:
    bridge = json.load(open(BASE + "scan-bridge.json"))
    cs = bridge.get("contracts", {})
    snap = json.load(open(BASE + "onchain-snapshot.json"))
    snap_addrs = set()
    for sec in ("contracts", "track_c"):
        for e in snap.get(sec, {}).values():
            for k in ("address", "sale", "token"):
                if isinstance(e, dict) and e.get(k): snap_addrs.add(str(e[k]).lower())
    in_snap = [k for k in cs if k.lower() in snap_addrs]
    out["bridge_leg"] = {"total": len(cs),
                         "same_owner_discarded": sum(1 for v in cs.values() if v.get("same_owner_discarded")),
                         "in_snapshot_addr": len(in_snap),
                         "not_in_snapshot_addr": len(cs) - len(in_snap),
                         "note": "Bridge is read-only for this job; promotions only if a bridge contract already in snapshot newly meets a tier or changes state."}
except Exception as e:
    out["bridge_leg"] = {"error": f"{type(e).__name__}: {e}"}

# ---- Leg 4: re-read 48 items vs 00:39 baseline ----
try:
    prev = json.load(open(BASE + "hot-leg-2026-11-10-0039-reread.json"))
    items = prev["items"]
    jobs = []
    for name, entry in items.items():
        for field in entry:
            data = calldata(field)
            if data: jobs.append((name, field, entry["address"], data))
    p = subprocess.run(["curl", "-s", "--max-time", "15", "-X", "POST", EP,
                        "-H", "Content-Type: application/json",
                        "--data", '{"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}'],
                       capture_output=True, text=True)
    try: block = int(json.loads(p.stdout)["result"], 16)
    except Exception: block = None
    results, failed = {}, []
    for i in range(0, len(jobs), 25):
        chunk = jobs[i:i + 25]
        resp = run_batch([(to, data) for (_, _, to, data) in chunk])
        if isinstance(resp, dict) and "_curl_error" in resp:
            for (name, field, to, data) in chunk:
                results[(name, field)] = None; failed.append((name, field))
            continue
        if isinstance(resp, dict): resp = [resp]
        for j, item in enumerate(resp):
            name, field, to, data = chunk[j]
            if isinstance(item, dict) and "result" in item:
                results[(name, field)] = decode(item["result"])
            else:
                results[(name, field)] = None; failed.append((name, field))
    reread = {"block": block, "items": {}, "duration_sec": round(time.time() - t0, 1)}
    for name, entry in items.items():
        row = {"address": entry["address"]}
        for field in entry:
            if field == "address": continue
            row[field] = results.get((name, field))
        reread["items"][name] = row
    diffs = []
    for name, row in reread["items"].items():
        base = items.get(name, {})
        for field, val in row.items():
            if field == "address": continue
            old = base.get(field)
            if old is None and val is None: continue
            if old != val: diffs.append({"item": name, "field": field, "old": old, "new": val})
    reread["diffs_vs_0039"] = diffs
    json.dump(reread, open(BASE + "hot-leg-2026-11-10-0044-reread.json", "w"), indent=1)
    out["leg4"] = {"block": block, "prev_block": prev.get("block"), "rpc": EP,
                   "items_n": len(items), "changes": diffs,
                   "failed_call_idx": [{"item": n, "field": f} for n, f in failed],
                   "read_failed": [{"item": n, "field": f} for n, f in failed]}
except Exception as e:
    out["leg4"] = {"error": f"{type(e).__name__}: {e}"}

out["duration_sec"] = round(time.time() - t0, 1)
json.dump(seen, open(BASE + "hot-leg-seen.json", "w"), indent=1)
json.dump(out, open(BASE + "hot-leg-run-2026-11-10-0044.json", "w"), indent=1)
print(json.dumps(out, indent=1)[:6000])
