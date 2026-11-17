#!/usr/bin/env python3
"""Recovery for hot-leg run 2026-11-11 17:54 WIB. The main 1754 script completed
legs 1/3b/4 (feed+shape+prio saved; seen.json updated) but crashed at final
assembly because /tmp/bb_en1754.html vanished between exec calls (Boltbook
files re-fetched directly into BASE). This script redoes ONLY the lost parts:
leg-2 Boltbook parse from the BASE copies, leg-3b MIHAO/MIHAO2 re-read, bridge
read-only, baseline comparison vs 1749, threshold watch, and writes the run
JSON. No state file is rewritten except the run JSON itself."""
import json, time, urllib.request, concurrent.futures, re, os
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EP = "https://bsc.nodereal.io/"
EP2 = "https://bsc-dataseed.binance.org/"
T0 = time.time()
from datetime import datetime, timezone, timedelta
NOW_ISO = datetime.now(timezone(timedelta(hours=7))).strftime("%Y-%m-%dT%H:%M:%S+07:00")
STAMP = "2026-11-11-1754"
BASELINE = "hot-leg-run-2026-11-11-1749.json"

def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode()); return "0x" + k.hexdigest()[:8]
def enc_addr(a): return a.lower().replace("0x", "").rjust(64, "0")
def call(addr, sig, args=""):
    data = sel(sig) + args
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                       "params": [{"to": addr, "data": data}, "latest"]}).encode()
    last_err = None
    for ep in (EP, EP2):
        try:
            req = urllib.request.Request(ep, data=body, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=12) as r:
                j = json.loads(r.read().decode())
            if "error" in j: return {"error": str(j["error"])[:120]}
            raw = j["result"]
            if raw in (None, "0x"): return {"error": "empty-return"}
            if len(raw) >= 66:
                v = raw[2:66]
                if set(v) <= set("0123456789abcdef"):
                    try: return int(v, 16)
                    except Exception: return raw
            return raw
        except Exception as e:
            last_err = e
            continue
    return {"error": f"{type(last_err).__name__}: {str(last_err)[:90]}"}

def views(addr, spec):
    out = {}
    for key, sig, args in spec:
        out[key] = call(addr, sig, args)
    return out

FEED = [(a, t) for a, t in json.load(open(BASE + f"hot-leg-{STAMP}-feed.json"))]
shapes = json.load(open(BASE + f"hot-leg-{STAMP}-shape.json"))
prio = json.load(open(BASE + f"hot-leg-{STAMP}-prio.json"))
seen = json.load(open(BASE + "hot-leg-seen.json"))
seen_l = {k.lower() for k in seen}
NEW = [a for a, _ in FEED if a in json.load(open("/tmp/shapes1754.json")) and a not in
       {k for k in seen if k in [x for x, _ in FEED]}]  # placeholder, recomputed below
# NEW = feed contracts whose first-seen is this run (recorded in leg 1 before crash)
NEW = [a for a, _ in FEED if isinstance(seen.get(a), dict) and seen[a].get("first_seen_wib", "").startswith("2026-11-11T18:0")]
seen_added = NEW

# ---- Leg 2: Boltbook EN + ZH (BASE copies, fetched 18:0x WIB, HTTP 200) ----
ADDR_RE = re.compile(r"0x[0-9a-fA-F]{40}")
bb_note, bb_fresh = "", []
try:
    en = open(BASE + f"hot-leg-{STAMP}-boltbook-en.html", "rb").read()
    zh = open(BASE + f"hot-leg-{STAMP}-boltbook-zh.html", "rb").read()
    addrs = set(ADDR_RE.findall(en.decode("utf-8", "ignore"))) | set(ADDR_RE.findall(zh.decode("utf-8", "ignore")))
    bb_fresh = sorted(a for a in addrs if a.lower() not in seen_l)
    kw_en = len(re.findall(r"free share|first share free|1 free share|free mint share", en.decode("utf-8","ignore"), re.I))
    kw_zh = len(re.findall(r"免费份额|首个免费|免费铸造|免费mint", zh.decode("utf-8","ignore"), re.I))
    bb_note = (f"EN HTTP 200 ({len(en)}B) + ZH HTTP 200 ({len(zh)}B) boltbook.fun; "
               f"{len(addrs)} unique addresses, {len(bb_fresh)} not in hot-leg-seen.json: {bb_fresh or 'none'}; "
               f"keywords EN free-share={kw_en} ZH={kw_zh}")
except Exception as e:
    bb_note = f"Boltbook read FAILED: {type(e).__name__}: {str(e)[:100]} - leg skipped, retried next run"

# ---- Leg 3b: recheck MIHAO / MIHAO2 (re-run: values lost in crash) ----
U = enc_addr(USER)
LEG3B = {
 "MIHAO": ("0x1f82539520a8b3d4eB7C3145f7E1EaFe4B52c4e1", [
    ("opened", "opened()", ""), ("freeMinted", "freeMinted()", ""), ("totalMinted", "totalMinted()", "")]),
 "MIHAO2": ("0x34eA49e9BC199418f121366BdBEa8fDbab10c26b", [
    ("freeMinted", "freeMinted()", ""), ("totalMinted", "totalMinted()", ""),
    ("FREE_SHARES", "FREE_SHARES()", ""), ("freePhaseActive", "freePhaseActive()", ""), ("opened", "opened()", "")]),
}
leg3b = {}
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:
    futs = {n: ex.submit(views, a, s) for n, (a, s) in LEG3B.items()}
    for n, f in futs.items():
        try: leg3b[n] = f.result(timeout=60)
        except Exception as e: leg3b[n] = {"error": f"{type(e).__name__}: {str(e)[:80]}"}

# ---- Bridge (read-only) ----
bridge_note = ""
try:
    b = json.load(open(BASE + "scan-bridge.json"))
    cons = b.get("contracts", {})
    mtime = time.strftime("%Y-%m-%d %H:%M WIB", time.localtime(os.path.getmtime(BASE + "scan-bridge.json")))
    new_addrs = [a for a, _ in FEED] + bb_fresh
    new_in_bridge = [a for a in new_addrs if a.lower() in {k.lower() for k in cons}]
    disc = [k for k, v in cons.items() if isinstance(v, dict) and v.get("same_owner_discarded")]
    bridge_note = (f"scan-bridge.json read ({len(cons)} contracts, mtime {mtime}); "
                   f"new feed/Boltbook contracts in bridge: {new_in_bridge or 'none'}; "
                   f"same_owner_discarded in bridge: {len(disc)}; no bridge promotion/change this run")
except Exception as e:
    bridge_note = f"bridge read FAILED: {type(e).__name__}: {str(e)[:100]} - skipped, run continues"

# ---- Compare vs 17:49 baseline ----
base = json.load(open(BASE + BASELINE))
bv = base.get("leg4_values", {})
b3 = base.get("leg3b_recheck", {})
changes, view_notes = [], []
PRIO_NAMES = list(prio["values"].keys())
for name in PRIO_NAMES:
    for key, new in prio["values"].get(name, {}).items():
        old = bv.get(name, {}).get(key) if isinstance(bv.get(name), dict) else None
        if isinstance(old, dict) or isinstance(new, dict):
            if old != new:
                view_notes.append(f"{name}.{key}: view {old} -> {new} (view-status only, not a state change)")
            continue
        if old != new:
            changes.append(f"{name}.{key}: {old} -> {new}")
for name in LEG3B:
    for key, new in leg3b.get(name, {}).items():
        old = b3.get(name, {}).get(key) if isinstance(b3.get(name), dict) else None
        if isinstance(old, dict) or isinstance(new, dict):
            if old != new:
                view_notes.append(f"leg3b {name}.{key}: view {old} -> {new} (view-status only)")
            continue
        if old != new:
            changes.append(f"leg3b {name}.{key}: {old} -> {new}")

# ---- Threshold watch (strong lead = age <24h + >70% free claimed + slot open) ----
watch = []
ap = prio["values"].get("AgentPals", {})
if isinstance(ap.get("freeMinted"), int):
    watch.append(f"AgentPals freeMinted {ap['freeMinted']}/300 = {ap['freeMinted']/300*100:.1f}% (strong-lead needs >70% = >210; slot open={ap.get('hasFreeMinted_user')})")
else:
    watch.append(f"AgentPals UNREAD this run (whole-contract read error: {ap}) - last known 116/300 = 38.7% at 17:49; no promotion determinable")
st = prio["values"].get("Stampooor", {})
if isinstance(st.get("freeMinted"), int) and isinstance(st.get("FREE_SUPPLY"), int):
    watch.append(f"Stampooor freeMinted {st['freeMinted']}/{st['FREE_SUPPLY']} = {st['freeMinted']/st['FREE_SUPPLY']*100:.1f}% (strong-lead needs >70% = >840; slot freeAvailable={st.get('freeAvailable_user')}; age: mintStart 1794362419 ~09:00 WIB 11 Nov, <24h)")
elif isinstance(st.get("freeMinted"), int):
    watch.append(f"Stampooor freeMinted {st['freeMinted']}/1200 (FREE_SUPPLY read failed this run, last known 1200) = {st['freeMinted']/1200*100:.1f}% (strong-lead needs >70% = >840; slot freeAvailable={st.get('freeAvailable_user')}; age: mintStart 1794362419 ~09:00 WIB 11 Nov, <24h)")

run = {
 "run": "free-mint-hot-leg 2026-11-11 17:54 WIB",
 "started_wib": NOW_ISO,
 "recovery_note": "Main 1754 script crashed at final assembly (FileNotFoundError /tmp/bb_en1754.html - /tmp Boltbook files vanished between exec calls); legs 1/3b/4 results recovered from saved files, leg-2 re-fetched directly into BASE, leg-3b re-read fresh. Leg-4 prio values are from the original 1754 run (block 132956845).",
 "leg1_sourcify_feed": {"returned": len(FEED),
   "verified_range": [FEED[-1][1], FEED[0][1]],
   "new": NEW, "already_seen": len(FEED) - len(NEW)},
 "leg1_shapes": shapes,
 "leg2_boltbook_en": {"bytes": len(open(BASE + f'hot-leg-{STAMP}-boltbook-en.html','rb').read()), "note": bb_note},
 "leg2_boltbook_zh": {"bytes": len(open(BASE + f'hot-leg-{STAMP}-boltbook-zh.html','rb').read())},
 "bridge": bridge_note,
 "leg3_new_sale_shape": {a: shapes[a] for a in NEW if isinstance(shapes.get(a), dict) and (shapes[a].get("S1") or shapes[a].get("S2"))},
 "leg3b_recheck": leg3b,
 "leg4_read_wib": NOW_ISO,
 "leg4_block": prio["block"],
 "leg4_values": prio["values"],
 "leg4_changes_vs_1749": changes or "NONE",
 "leg4_view_notes": view_notes or "NONE",
 "threshold_watch": watch,
 "seen_added": seen_added,
 "shape_check_failed_not_kept": [a for a in NEW if isinstance(shapes.get(a), dict) and "error" in shapes[a]],
 "elapsed_s": round(time.time() - T0, 1),
}
json.dump(run, open(BASE + f"hot-leg-run-{STAMP}.json", "w"), indent=1)
print(json.dumps(run, indent=1))
