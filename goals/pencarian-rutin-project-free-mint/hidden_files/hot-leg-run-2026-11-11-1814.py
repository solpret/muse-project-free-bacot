#!/usr/bin/env python3
"""free-mint-hot-leg 2026-11-11 18:14 WIB. Legs: (1) Sourcify feed limit 20 (fetched
18:18 WIB, verifiedAt 11:09:31-11:17:51Z) + shape-check 6 genuinely new contracts
(shape via curl, urllib IncompleteRead-prone, bypassed this run);
(2) Boltbook EN+ZH boltbook.fun (fetched 18:18); (3b) recheck MIHAO/MIHAO2;
(4) leg4 re-read of the prio set vs 17:54 baseline; bridge read-only.
Read-only except own hot-leg state files. No preview/mint unless a prio item
crosses a strong-lead threshold AND passes the mandatory website gate (checked
separately after this script). Shape-check failures are NOT kept in
hot-leg-seen.json (retry next run)."""
import json, time, urllib.request, concurrent.futures, re, os, shutil
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
AGENTID = 107187496765866644729837695198686237165740365523485558112864918211974996443404
EP = "https://bsc.nodereal.io/"
EP2 = "https://bsc-dataseed.binance.org/"
T0 = time.time()
from datetime import datetime, timezone, timedelta
NOW_ISO = datetime.now(timezone(timedelta(hours=7))).strftime("%Y-%m-%dT%H:%M:%S+07:00")
RUN = "2026-11-11 18:14 WIB"
STAMP = "2026-11-11-1814"
BASELINE = "hot-leg-run-2026-11-11-1754.json"

def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode()); return "0x" + k.hexdigest()[:8]
def enc_addr(a): return a.lower().replace("0x", "").rjust(64, "0")
def enc_u(n): return ("%064x" % n)
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

def block_number():
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}).encode()
    for ep in (EP, EP2):
        try:
            req = urllib.request.Request(ep, data=body, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=10) as r:
                return int(json.loads(r.read().decode())["result"], 16)
        except Exception:
            continue
    return None

def views(addr, spec):
    out = {}
    for key, sig, args in spec:
        out[key] = call(addr, sig, args)
    return out

# ---- Leg 1: Sourcify feed (fetched 18:18 WIB, HTTP 200) ----
FEED = [(a, t) for a, t in json.load(open("/tmp/feed1814_list.json"))]
seen = json.load(open(BASE + "hot-leg-seen.json"))
seen_l = {k.lower() for k in seen}
NEW = [a for a, _ in FEED if a.lower() not in seen_l]
shapes = json.load(open("/tmp/shapes1814.json"))
json.dump(shapes, open(BASE + f"hot-leg-{STAMP}-shape.json", "w"), indent=1)
json.dump(FEED, open(BASE + f"hot-leg-{STAMP}-feed.json", "w"), indent=1)

# record newly seen (only successful shape-checks; failures NOT kept, retry next run)
seen_added = []
for a in NEW:
    sh = shapes.get(a, {})
    if "error" in sh:
        continue
    seen[a] = {"first_seen_wib": NOW_ISO, "source": f"sourcify-feed-{STAMP[-4:]}",
               "note": f"S1={sh['S1']} S2={sh['S2']} mint={sh['mint']} quote={sh['quote']} free={sh['free']} agent={sh['agent']} token={sh['token']}",
               "status": "checked-not-sale-shape" if not (sh["S1"] or sh["S2"]) else "SALE-SHAPE"}
    seen_added.append(a)
if seen_added:
    json.dump(seen, open(BASE + "hot-leg-seen.json", "w"), indent=1)

# ---- Leg 2: Boltbook EN + ZH (fetched 18:18 WIB via curl -L) ----
ADDR_RE = re.compile(r"0x[0-9a-fA-F]{40}")
bb_note, bb_fresh = "", []
try:
    en = open("/tmp/bb_en1814.html", "rb").read()
    zh = open("/tmp/bb_zh1814.html", "rb").read()
    shutil.copy("/tmp/bb_en1814.html", BASE + f"hot-leg-{STAMP}-boltbook-en.html")
    shutil.copy("/tmp/bb_zh1814.html", BASE + f"hot-leg-{STAMP}-boltbook-zh.html")
    addrs = set(ADDR_RE.findall(en.decode("utf-8", "ignore"))) | set(ADDR_RE.findall(zh.decode("utf-8", "ignore")))
    bb_fresh = sorted(a for a in addrs if a.lower() not in seen_l)
    kw_en = len(re.findall(r"free share|first share free|1 free share|free mint share", en.decode("utf-8","ignore"), re.I))
    kw_zh = len(re.findall(r"免费份额|首个免费|免费铸造|免费mint", zh.decode("utf-8","ignore"), re.I))
    bb_note = (f"EN HTTP 200 ({len(en)}B) + ZH HTTP 200 ({len(zh)}B) boltbook.fun; "
               f"{len(addrs)} unique addresses, {len(bb_fresh)} not in hot-leg-seen.json: {bb_fresh or 'none'}; "
               f"keywords EN free-share={kw_en} ZH={kw_zh}")
except Exception as e:
    bb_note = f"Boltbook read FAILED: {type(e).__name__}: {str(e)[:100]} - leg skipped, retried next run"

# ---- Leg 3b: recheck MIHAO / MIHAO2 ----
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

# ---- Leg 4: prio re-read vs 17:54 baseline ----
PRIO = {
 "AgentPals": ("0xD265a929D0E50bD5ee4675e4E97F38D8380802E2", [
    ("totalMinted", "totalMinted()", ""), ("freeMinted", "freeMinted()", ""),
    ("hasFreeMinted_user", "hasFreeMinted(address)", U), ("balanceOf_user", "balanceOf(address)", U)]),
 "HANAMI": ("0x8A742EcE2a8C1dCc5dE792A062dbEe9C00A74640", [
    ("totalSupply", "totalSupply()", ""), ("freeMinted", "freeMinted()", ""),
    ("balanceOf_user", "balanceOf(address)", U)]),
 "ABYSSCABLE": ("0xd2e9242b0d7c0186cc181a5fc8534541dad278a2", [
    ("totalSupply", "totalSupply()", ""), ("agentFreeUsed", "agentFreeUsed()", ""),
    ("mintOpen", "mintOpen()", ""), ("balanceOf_user", "balanceOf(address)", U)]),
 "Stampooor": ("0x467696af8c2206B977B24081445104632dc1D459", [
    ("totalMinted", "totalMinted()", ""), ("freeMinted", "freeMinted()", ""),
    ("FREE_SUPPLY", "FREE_SUPPLY()", ""), ("mintOpen", "mintOpen()", ""),
    ("freeAvailable_user", "freeAvailable(address)", U), ("balanceOf_user", "balanceOf(address)", U)]),
 "LOWB": ("0x00487ED061C77A1dd5085ef3a2D593366f9C6B35", [
    ("opened", "opened()", ""), ("totalFreeMinted", "totalFreeMinted()", ""),
    ("totalMinted", "totalMinted()", "")]),
 "SHINE": ("0xDDc2352d1ceC10b42e05A297232f5328902C6c2C", [
    ("startTime", "startTime()", ""), ("launched", "launched()", ""),
    ("freeClaimed_user", "freeClaimed(address)", U)]),
 "UFO": ("0xE4059eA596392AcA14100af6CDC9481c330E2728", [
    ("FREE_SHARES", "FREE_SHARES()", ""), ("freeClaimed_user", "freeClaimed(address)", U)]),
 "RigForge": ("0xa1cc0d7c0534f824f2cf6eeb865a8fede96c8f7d", [
    ("SALE_START", "SALE_START()", ""), ("FREE_SHARES", "FREE_SHARES()", ""),
    ("freeSharesLeft", "freeSharesLeft()", ""), ("openedAt", "openedAt()", ""),
    ("freeTaken_agentId", "freeTaken(uint256)", enc_u(AGENTID))]),
 "BotFighters": ("0x58a704d9e02FE11c0A61683AE7F606E4366F13eb", [
    ("FREE_CAP", "FREE_CAP()", ""), ("freeMinted", "freeMinted()", ""),
    ("balanceOf_user", "balanceOf(address)", U)]),
 "BHTB": ("0xffcA030c6C69A5b75392AAfaF5BF1980c0ed0467", [
    ("freeRemaining", "freeRemaining()", "")]),
 "AgentGrid": ("0x651302C0043040D48EaAF85605E12F0549aD6D89", [
    ("freeUsed", "freeUsed()", "")]),
 "SUDOSAINTS": ("0x869d330bb48e7ab32da16745ef9a36a69d34f12f", [
    ("totalSupply", "totalSupply()", ""), ("freeMinted", "freeMinted()", ""),
    ("mintActive", "mintActive()", ""), ("freeUsed_user", "freeUsed(address)", U),
    ("balanceOf_user", "balanceOf(address)", U)]),
 "binanceai": ("0x46cb1D3efd4307506Cda7EbBa5a51be64746739E", [
    ("launched", "launched()", "")]),
}
prio = {"block": block_number(), "values": {}}
with concurrent.futures.ThreadPoolExecutor(max_workers=6) as ex:
    futs = {n: ex.submit(views, a, s) for n, (a, s) in PRIO.items()}
    for n, f in futs.items():
        try: prio["values"][n] = f.result(timeout=60)
        except Exception as e: prio["values"][n] = {"error": f"{type(e).__name__}: {str(e)[:80]}"}
json.dump(prio, open(BASE + f"hot-leg-{STAMP}-prio.json", "w"), indent=1)

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

# ---- Compare vs 17:54 baseline ----
base = json.load(open(BASE + BASELINE))
bv = base.get("leg4_values", {})
b3 = base.get("leg3b_recheck", {})
changes, view_notes = [], []
for name in PRIO:
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
    watch.append(f"AgentPals freeMinted {ap['freeMinted']}/300 = {ap['freeMinted']/300*100:.1f}% (strong-lead needs >70% = >210; slot open={ap.get('hasFreeMinted_user')}; website UNVERIFIED per snapshot - gate blocks any mint)")
else:
    watch.append(f"AgentPals UNREAD this run (whole-contract read error: {ap}) - last known 116/300 = 38.7% at 17:54/18:01; no promotion determinable")
st = prio["values"].get("Stampooor", {})
if isinstance(st.get("freeMinted"), int) and isinstance(st.get("FREE_SUPPLY"), int):
    pct = st['freeMinted']/st['FREE_SUPPLY']*100
    watch.append(f"Stampooor freeMinted {st['freeMinted']}/{st['FREE_SUPPLY']} = {pct:.1f}% (strong-lead needs >70% = >840; slot freeAvailable={st.get('freeAvailable_user')}; age: mintStart 1794362419 ~09:00 WIB 11 Nov, <24h; website UNVERIFIED per snapshot - gate blocks any mint)")
elif isinstance(st.get("freeMinted"), int):
    watch.append(f"Stampooor freeMinted {st['freeMinted']}/1200 (FREE_SUPPLY read failed this run, last known 1200) = {st['freeMinted']/1200*100:.1f}% (strong-lead needs >70% = >840; slot freeAvailable={st.get('freeAvailable_user')}; age <24h; website UNVERIFIED - gate blocks any mint)")
else:
    watch.append(f"Stampooor UNREAD this run: {st} - last known 828/1200 = 69.0% at 18:01; no promotion determinable")

run = {
 "run": f"free-mint-hot-leg {RUN}",
 "started_wib": NOW_ISO,
 "leg1_sourcify_feed": {"returned": len(FEED),
   "verified_range": [FEED[-1][1], FEED[0][1]],
   "new": NEW, "already_seen": len(FEED) - len(NEW)},
 "leg1_shapes": shapes,
 "leg2_boltbook_en": {"bytes": len(open('/tmp/bb_en1814.html','rb').read()), "note": bb_note},
 "leg2_boltbook_zh": {"bytes": len(open('/tmp/bb_zh1814.html','rb').read())},
 "bridge": bridge_note,
 "leg3_new_sale_shape": {a: shapes[a] for a in NEW if isinstance(shapes.get(a), dict) and (shapes[a].get("S1") or shapes[a].get("S2"))},
 "leg3b_recheck": leg3b,
 "leg4_read_wib": NOW_ISO,
 "leg4_block": prio["block"],
 "leg4_values": prio["values"],
 "leg4_changes_vs_1754": changes or "NONE",
 "leg4_view_notes": view_notes or "NONE",
 "threshold_watch": watch,
 "seen_added": seen_added,
 "shape_check_failed_not_kept": [a for a in NEW if isinstance(shapes.get(a), dict) and "error" in shapes[a]],
 "elapsed_s": round(time.time() - T0, 1),
}
json.dump(run, open(BASE + f"hot-leg-run-{STAMP}.json", "w"), indent=1)
print(json.dumps(run, indent=1))
