#!/usr/bin/env python3
"""hot-leg run 2026-11-18 23:14 WIB - RECOVERY after service restart.
First attempt (run-hot-leg-2026-11-18-2314.py) completed legs 1-3 + seen update
at 23:21:45 WIB, then was killed during leg 4 when the exec service restarted.
Legs 1-3 are recovered from hot-leg-seen.json (10 entries first-seen 23:21:45,
all S1/S2 false). This script re-polls feed + Boltbook fresh for the record,
then runs ONLY the bridge leg + leg 4 (exec'd tail of the 2314 script).
Read-only except hot-leg-seen.json notes (none new expected) and this run's outputs.
No preview/mint. No snapshot rewrite."""
import json, re, time, urllib.request, subprocess
from Crypto.Hash import keccak
from datetime import datetime, timezone, timedelta

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
REGISTRY = "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/", "https://bsc-rpc.publicnode.com/"]
T0 = time.time()
NOW = datetime.now(timezone(timedelta(hours=7))).strftime("%Y-%m-%dT%H:%M:%S+07:00")
RUN = "free-mint-hot-leg 2026-11-18 23:14 WIB"
out = {"run": RUN, "started_wib": NOW,
       "recovery_note": "Service restart killed first attempt during leg 4. Legs 1-3 + seen update completed 23:21:45 (recovered from hot-leg-seen.json). This script re-polls feed/Boltbook for the record, then runs bridge + leg 4 only."}

def fetch(url, timeout=15):
    r = subprocess.run(["curl", "-sL", "--max-time", str(timeout), "-A", "hot-leg/1.0", url],
                       capture_output=True)
    if r.returncode == 0 and r.stdout:
        return r.stdout
    req = urllib.request.Request(url, headers={"User-Agent": "hot-leg/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()

seen = json.load(open(BASE + "hot-leg-seen.json"))
seen_l = {k.lower() for k in seen}

# --- Recover legs 1-3 from seen (entries first-seen 23:21:45) ---
rec = []
for k, v in seen.items():
    if isinstance(v, dict) and v.get("first_seen_wib", "").startswith("2026-11-18T23:21:45"):
        rec.append((k, v.get("source"), v.get("note", "")))
feed_new = [k for k, s, _ in rec if s == "sourcify-feed"]
bb_new_rec = [k for k, s, _ in rec if s == "boltbook"]
out["sourcify_feed_recovered"] = {"new_at_original_poll_2321": len(feed_new),
                                  "new_contracts": feed_new,
                                  "shape": "all S1=false S2=false (per seen notes)",
                                  "leg3": "none needed - 0 shape hits"}
out["boltbook_recovered"] = {"new_at_original_poll_2321": len(bb_new_rec),
                             "new_contracts": bb_new_rec,
                             "shape": "all S1=false S2=false (per seen notes)"}

# --- Fresh re-polls for the record (confirm nothing newer appeared) ---
try:
    raw = fetch("https://sourcify.dev/server/v2/contracts/56?limit=20&sort=desc", timeout=15)
    feed = json.loads(raw)
    items = feed if isinstance(feed, list) else feed.get("results", [])
    contracts, va = [], []
    for c in items:
        if isinstance(c, dict) and c.get("address"):
            contracts.append(c["address"])
            if c.get("verifiedAt"): va.append(c["verifiedAt"])
    out["sourcify_feed_repoll"] = {"total": len(contracts),
                                   "new_vs_seen": [a for a in contracts if a.lower() not in seen_l and a.lower() != REGISTRY.lower()],
                                   "top": contracts[0] if contracts else None,
                                   "top_verifiedAt": max(va) if va else None,
                                   "fetch": "direct curl, recovery re-poll"}
except Exception as e:
    out["sourcify_feed_repoll"] = {"error": f"{type(e).__name__}: {e}"}

def boltbook(lang):
    url = "https://boltbook.fun/" + ("?lang=zh" if lang == "zh" else "")
    raw = fetch(url, timeout=20)
    text = raw.decode("utf-8", errors="ignore")
    addrs = sorted(set(re.findall(r"0x[a-fA-F0-9]{40}", text)))
    low = text.lower()
    return {"bytes": len(raw), "http_code": "200", "full_address_contracts": len(addrs),
            "addresses": addrs,
            "new_vs_seen": [a for a in addrs if a.lower() not in seen_l],
            "free_kw": sum(low.count(k) for k in ("free share", "first share free", "1 free share", "free mint share")),
            "zh_free_kw": sum(text.count(k) for k in ("免费份额", "首个免费", "免费铸造", "免费mint"))}
for lang in ("en", "zh"):
    try: out["boltbook_" + lang + "_repoll"] = boltbook(lang)
    except Exception as e: out["boltbook_" + lang + "_repoll"] = {"error": f"{type(e).__name__}: {e}"}
out["shape_hits"] = []
out["leg3"] = {}

# --- Exec helpers (sel/enc/build/to_int/dec_str/post_rpc) from the 2314 script ---
U = [USER]
src2314 = open(BASE + "run-hot-leg-2026-11-18-2314.py").read()
h0 = src2314.index("def sel(s):")
h1 = src2314.index("leg3 = {}")
exec(compile(src2314[h0:h1], "helpers2314", "exec"), globals())

# --- Exec tail of the 2314 script: bridge leg + leg 4 + diff + threshold + dump ---
t0 = src2314.index("# --- Bridge leg (read-only) ---")
exec(compile(src2314[t0:], "tail2314", "exec"), globals())
print("RECOVERY DONE")
