#!/usr/bin/env python3
"""Run 2026-11-09 04:01 WIB — route 2 (Boltbook EN+ZH) + route 5a (Sourcify feed)
+ bridge read-only check. Read-only vs snapshot; writes run-2026-11-09-0401-discovery.json.
"""
import json, re, time, urllib.request
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TS = "2026-11-09-0401"
T0 = time.time()
out = {"run": TS}

# --- Route 2: Boltbook ---
ADDR_RE = re.compile(r"0x[0-9a-fA-F]{40}")
bb = {}
for lang, url in (("en", "https://boltbook.fun/"), ("zh", "https://boltbook.fun/?lang=zh")):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        html = urllib.request.urlopen(req, timeout=25).read().decode("utf-8", "replace")
        open(f"{BASE}/run-{TS}-boltbook-{lang}.html", "w").write(html)
        addrs = sorted(set(ADDR_RE.findall(html)))
        bb[lang] = {"bytes": len(html), "addrs": addrs}
        print(f"BOLTBOOK {lang}: {len(html)} bytes, {len(addrs)} addrs", flush=True)
    except Exception as e:
        bb[lang] = {"error": f"{type(e).__name__}: {e}"}
        print(f"BOLTBOOK {lang} ERROR {e}", flush=True)
out["boltbook"] = bb
all_bb = sorted(set(bb.get("en", {}).get("addrs", [])) | set(bb.get("zh", {}).get("addrs", [])))
out["boltbook_unique_addrs"] = all_bb
snap = json.load(open(f"{BASE}/onchain-snapshot.json"))
snap_addrs = {str(v.get("address", "")).lower() for v in snap.get("contracts", {}).values() if isinstance(v, dict)}
seen = json.load(open(f"{BASE}/onchain-scan-seen.json"))
new_bb = [a for a in all_bb if a.lower() not in snap_addrs and a.lower() not in {k.lower() for k in seen}]
out["boltbook_new_vs_snapshot_seen"] = new_bb
print("BOLTBOOK new vs snapshot+seen:", new_bb, flush=True)

# --- Route 5a: Sourcify recently-verified feed ---
try:
    req = urllib.request.Request("https://sourcify.dev/server/v2/contracts/56?limit=20&sort=desc",
                                 headers={"User-Agent": "Mozilla/5.0"})
    feed = json.loads(urllib.request.urlopen(req, timeout=25).read())
    addrs = [c.get("address") for c in feed if isinstance(c, dict) and c.get("address")]
    out["sourcify_feed"] = {"n": len(addrs), "addrs": addrs}
    print("SOURCIFY feed:", len(addrs), addrs, flush=True)
except Exception as e:
    out["sourcify_feed"] = {"error": f"{type(e).__name__}: {e}"}
    print("SOURCIFY ERROR", e, flush=True)

# --- Bridge (read-only) ---
import os
try:
    bridge = json.load(open(f"{BASE}/scan-bridge.json"))
    bc = bridge.get("contracts", bridge) if isinstance(bridge, dict) else {}
    if isinstance(bc, dict) and bc and isinstance(next(iter(bc.values())), dict):
        not_in = [k for k in bc if k.lower() not in snap_addrs]
        out["bridge"] = {"total": len(bc),
                         "same_owner_discarded": sum(1 for v in bc.values() if isinstance(v, dict) and v.get("same_owner_discarded")),
                         "not_in_snapshot": not_in,
                         "mtime": time.strftime("%Y-%m-%d %H:%M UTC", time.gmtime(os.path.getmtime(f"{BASE}/scan-bridge.json")))}
    else:
        out["bridge"] = {"note": "bridge shape unexpected", "keys": list(bc)[:5] if isinstance(bc, dict) else str(type(bc))}
    print("BRIDGE:", json.dumps(out["bridge"])[:600], flush=True)
except Exception as e:
    out["bridge"] = {"error": f"{type(e).__name__}: {e}"}
    print("BRIDGE ERROR", e, flush=True)

out["duration_s"] = round(time.time() - T0, 1)
json.dump(out, open(f"{BASE}/run-{TS}-discovery.json", "w"), indent=1)
print("DISCOVERY DONE", out["duration_s"], "s", flush=True)
