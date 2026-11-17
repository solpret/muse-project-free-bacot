#!/usr/bin/env python3
"""Hot-leg run 2026-11-08 00:19 WIB. Legs 1-3 + bridge. Read-only except own hot-leg state files. Never writes main snapshot."""
import json, re, subprocess, urllib.request, time, os
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone, timedelta

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TS = "2026-11-08-0019"
WIB = timezone(timedelta(hours=7))
NOW = datetime.now(WIB).strftime("%Y-%m-%dT%H:%M:%S+07:00")
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
REG = "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F"
EXCLUDED = {"0x827e83e49bd7e15b67efa0e90fc25f17b8d96124", "0x8b47354e7b76b1970a0d06365c8244a810d37493"}
FREE_VIEWS = ["freeSharesRemaining", "freeClaimed", "freeFor", "freeLeft", "freeUsed", "freeAvailable",
              "freeSharePoolExhausted", "freeSharesClaimed", "freeMinted", "freeCardsRemaining"]
out = {"run": "free-mint-hot-leg 2026-11-08 00:19:38 WIB"}
t0 = time.time()

def shape_check(addr):
    try:
        p = subprocess.run(["curl", "-sS", "--max-time", "20", "-A", "hot-leg/1.0",
                            f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi"],
                           capture_output=True, text=True, timeout=25)
        if p.returncode != 0:
            return {"address": addr, "error": f"curl rc={p.returncode}: {p.stderr.strip()[:100]}"}
        meta = json.loads(p.stdout)
        abi = meta.get("abi", [])
        fns = {}
        for e in abi:
            if e.get("type") == "function":
                fns.setdefault(e["name"], []).append(e)
        names = set(fns)
        has_mint = any(n.lower().startswith("mint") for n in names)
        has_quote = bool(names & {"quote", "cost", "getQuote", "mintCost", "price", "getPrice"})
        free_views = sorted(names & set(FREE_VIEWS))
        agent_ref = bool(names & {"agentId", "agentRegistry", "registry", "getAgentId", "agentGate", "AgentGate", "AGENT_ID", "agentIdRegistry", "isAgent"})
        is_token = bool(names & {"name", "symbol", "decimals", "totalSupply"})
        mintfree = "mintFree" in fns and any(len(e.get("inputs", [])) == 0 for e in fns["mintFree"])
        s1 = has_mint and has_quote and bool(free_views) and agent_ref
        s2 = is_token and mintfree and bool(names & {"freeClaimed", "freeMinted"}) and bool(names & {"FREE_SLOTS", "FREE_SUPPLY"}) and agent_ref
        return {"address": addr, "abi_functions": sorted(names), "S1": s1, "S2": s2,
                "mint": has_mint, "quote": has_quote, "free": free_views, "agent": agent_ref, "token": is_token}
    except Exception as e:
        return {"address": addr, "error": f"{type(e).__name__}: {str(e)[:100]}"}

# ---------- Leg 1: Sourcify feed ----------
seen = json.load(open(f"{BASE}/hot-leg-seen.json"))
feed_addrs = []
try:
    cp = subprocess.run(["curl", "-sS", "--max-time", "25", "-A", "hot-leg/1.0",
                         "https://sourcify.dev/server/v2/contracts/56?limit=20&sort=desc"],
                        capture_output=True, text=True, timeout=30)
    data = json.loads(cp.stdout)
    items = data.get("results", data) if isinstance(data, dict) else data
    for it in items:
        a = it.get("address") or it.get("contractAddress")
        if a:
            feed_addrs.append(a)
    out["leg1_feed"] = {"n": len(feed_addrs), "addrs": feed_addrs}
    json.dump(data, open(f"{BASE}/hot-leg-{TS}-sourcify.json", "w"), indent=1)
except Exception as e:
    out["leg1_feed"] = {"error": f"{type(e).__name__}: {e}"}
    feed_addrs = []

new_addrs = [a for a in feed_addrs if a not in seen and a.lower() not in EXCLUDED and a.lower() != REG.lower()]
new_excluded = [a for a in feed_addrs if a.lower() in EXCLUDED]
shapes = []
if new_addrs:
    with ThreadPoolExecutor(max_workers=10) as ex:
        shapes = list(ex.map(shape_check, new_addrs))
    for s in shapes:
        if s.get("error"):
            seen[s["address"]] = {"first_seen_wib": NOW,
                "note": f"shape-check failed on transport ({s.get('error')}) - NOT verified as not-sale-shape; retry next run",
                "source": "sourcify-feed", "status": "shape-check-failed-transport"}
            continue
        seen[s["address"]] = {"first_seen_wib": NOW,
            "note": f"S1={s.get('S1')} S2={s.get('S2')} mint={s.get('mint')} quote={s.get('quote')} free={s.get('free')} agent={s.get('agent')} token={s.get('token')}",
            "source": "sourcify-feed", "status": "checked-not-sale-shape" if not (s.get("S1") or s.get("S2")) else "sale-shape"}
    json.dump(seen, open(f"{BASE}/hot-leg-seen.json", "w"), indent=1)
    json.dump(shapes, open(f"{BASE}/hot-leg-{TS}-sourcify-shape.json", "w"), indent=1)
out["leg1"] = {"new": new_addrs, "new_excluded_rediscovered": new_excluded, "shapes": shapes, "seen_total": len(seen)}
sale_shapes = [s for s in shapes if s.get("S1") or s.get("S2")]

# ---------- Leg 2: Boltbook EN + ZH ----------
def fetch_boltbook(url):
    try:
        p = subprocess.run(["curl", "-sS", "-L", "--max-time", "15", "-A", "hot-leg/1.0", url],
                           capture_output=True, text=True, timeout=20)
        return p.stdout or "", p.returncode
    except Exception as e:
        return "", f"ERR {e}"

en, en_rc = fetch_boltbook("https://boltbook.fun/?lang=en")
zh, zh_rc = fetch_boltbook("https://boltbook.fun/?lang=zh")
open(f"{BASE}/hot-leg-{TS}-boltbook-en.html", "w").write(en)
open(f"{BASE}/hot-leg-{TS}-boltbook-zh.html", "w").write(zh)
addr_re = re.compile(r"0x[a-fA-F0-9]{40}")
en_addrs = sorted(set(addr_re.findall(en)))
zh_addrs = sorted(set(addr_re.findall(zh)))
all_addrs = sorted(set(en_addrs) | set(zh_addrs))
kw_en = ["free share", "first share free", "1 free share", "free mint share"]
kw_zh = ["免费份额", "首个免费", "免费铸造", "免费mint"]
text_low = (en + zh).lower()
kw_hits = {k: text_low.count(k.lower()) for k in kw_en + kw_zh if k.lower() in text_low}
snap = json.load(open(f"{BASE}/onchain-snapshot.json"))
snap_addr_set = {v.get("address", "").lower() for v in snap.get("contracts", {}).values() if isinstance(v, dict)}
for v in snap.get("track_c", {}).values():
    if isinstance(v, dict):
        for k in ("sale", "token", "address"):
            if v.get(k):
                snap_addr_set.add(str(v[k]).lower())
new_bolt = [a for a in all_addrs if a not in seen]
new_bolt_not_snap = [a for a in all_addrs if a.lower() not in snap_addr_set and a not in seen]
bolt_shapes = {}
for a in new_bolt_not_snap:
    s = shape_check(a)
    if s.get("error"):
        note = f"shape-check failed on transport ({s['error']}) - NOT verified as not-sale-shape; retry next run"
        status = "shape-check-failed-transport"
    else:
        note = (f"S1={s.get('S1')} S2={s.get('S2')} mint={s.get('mint')} quote={s.get('quote')} "
                f"free={s.get('free')} agent={s.get('agent')} token={s.get('token')}")
        status = "sale-shape" if (s.get("S1") or s.get("S2")) else "checked-not-sale-shape"
    bolt_shapes[a] = {"note": note, "shape": s}
    seen[a] = {"first_seen_wib": NOW, "note": note, "source": "boltbook-en" if a in en_addrs else "boltbook-zh",
               "status": status}
in_snap_bolt = [a for a in new_bolt if a.lower() in snap_addr_set]
for a in in_snap_bolt:
    bolt_shapes[a] = {"note": "already in snapshot"}
if new_bolt:
    json.dump(seen, open(f"{BASE}/hot-leg-seen.json", "w"), indent=1)
out["leg2_boltbook"] = {"en_bytes": len(en), "en_rc": en_rc, "zh_bytes": len(zh), "zh_rc": zh_rc,
                        "en_addrs": len(en_addrs), "zh_addrs": len(zh_addrs), "unique_addrs": len(all_addrs),
                        "keyword_hits": kw_hits, "new_vs_seen": new_bolt, "new_vs_snapshot": new_bolt_not_snap,
                        "shape_check": bolt_shapes, "seen_total": len(seen)}
bolt_sale_shapes = [a for a, v in bolt_shapes.items() if isinstance(v, dict) and v.get("shape", {}).get("S1") or isinstance(v, dict) and v.get("shape", {}).get("S2")]

# ---------- Leg 3: only for new sale shapes ----------
out["leg3_new_sale_shapes"] = sale_shapes + bolt_sale_shapes
out["leg3_verify"] = "None - no new sale-shape contract" if not (sale_shapes or bolt_sale_shapes) else "SEE leg4/reread-verify script if needed; age verification via main job"

# ---------- Pending claims ----------
out["pending_claims"] = snap.get("pending_claims") or "snapshot pending_claims empty at run start - nothing to re-read"

# ---------- Bridge leg (read-only) ----------
bridge = json.load(open(f"{BASE}/scan-bridge.json"))
bcontracts = bridge.get("contracts", {})
discarded = [a for a, v in bcontracts.items() if v.get("same_owner_discarded")]
in_snap = [a for a in bcontracts if a.lower() in snap_addr_set]
not_in_snap = [a for a in bcontracts if a.lower() not in snap_addr_set]
snap_text = json.dumps(snap).lower()
in_snap_text = [a for a in not_in_snap if a.lower() in snap_text]
mtime = time.strftime("%Y-%m-%d %H:%M UTC", time.gmtime(os.path.getmtime(f"{BASE}/scan-bridge.json")))
out["bridge_leg"] = {"total": len(bcontracts), "same_owner_discarded": len(discarded),
                     "in_snapshot_addr": len(in_snap), "not_in_snapshot_addr": len(not_in_snap),
                     "not_in_addr_but_in_snapshot_text": len(in_snap_text), "mtime": mtime,
                     "note": "Bridge is read-only for this job; promotions only if a bridge contract already in snapshot newly meets a tier or changes state."}
out["duration_s"] = round(time.time() - t0, 1)
json.dump(out, open(f"{BASE}/hot-leg-{TS}.json", "w"), indent=1)
print(json.dumps(out, indent=1, default=str))
