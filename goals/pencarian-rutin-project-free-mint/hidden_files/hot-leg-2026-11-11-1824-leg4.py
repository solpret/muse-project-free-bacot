#!/usr/bin/env python3
"""Hot-leg 2026-11-11 18:24 WIB RECOVERY (leg 3b + leg 4 + bridge).

The main 1824 script (hot-leg-2026-11-11-1824.py) completed legs 1-2, then was
killed by its 280s timeout during the slow sequential RPC re-reads (legs 3b/4).
This recovery re-runs ONLY legs 3b/4/bridge via fast_rpc.call_many (one JSON-RPC
batch, raced endpoints) and merges the result with the killed run's artifacts
(feed/shape/boltbook already saved). Read-only except own hot-leg state files.
No preview/mint; threshold crossings are reported for a separate gate check."""
import json, os, sys, time
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import call_many, race
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
STAMP = "2026-11-11-1824"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
AGENTID = 107187496765866644729837695198686237165740365523485558112864918211974996443404
T0 = time.time()
from datetime import datetime, timezone, timedelta
NOW_ISO = datetime.now(timezone(timedelta(hours=7))).strftime("%Y-%m-%dT%H:%M:%S+07:00")

def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode()); return "0x" + k.hexdigest()[:8]
def enc_addr(a): return a.lower().replace("0x", "").rjust(64, "0")
def enc_u(n): return "%064x" % n
U = enc_addr(USER)

LEG3B = {
 "MIHAO": ("0x1f82539520a8b3d4eB7C3145f7E1EaFe4B52c4e1", [
    ("opened", "opened()", ""), ("freeMinted", "freeMinted()", ""), ("totalMinted", "totalMinted()", "")]),
 "MIHAO2": ("0x34eA49e9BC199418f121366BdBEa8fDbab10c26b", [
    ("freeMinted", "freeMinted()", ""), ("totalMinted", "totalMinted()", ""),
    ("FREE_SHARES", "FREE_SHARES()", ""), ("freePhaseActive", "freePhaseActive()", ""), ("opened", "opened()", "")]),
}
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
 "AgentRune": ("0xc1fc0bb36d2be928809e4b3e6aa94b3dd2946f53", [
    ("totalSupply", "totalSupply()", ""), ("freeMinted", "freeMinted()", ""),
    ("balanceOf_user", "balanceOf(address)", U)]),
 "RAMRAIDERS": ("0x98dcfdeb5e015bbb3c9aca2a90ba0ee80e35315b", [
    ("totalSupply", "totalSupply()", ""), ("freeMinted", "freeMinted()", ""),
    ("balanceOf_user", "balanceOf(address)", U)]),
 "0x7Eb9": ("0x7Eb92041aa3037e39baA88154F279e3D9F85c593", [
    ("totalMinted", "totalMinted()", ""), ("balanceOf_user", "balanceOf(address)", U)]),
 "STALL": ("0xe3de7fd0d12cff4a46d8bf702ab593b6f921b308", [
    ("totalSupply", "totalSupply()", ""), ("mintOpen", "mintOpen()", ""),
    ("balanceOf_user", "balanceOf(address)", U)]),
}

def decode(raw):
    if isinstance(raw, dict):
        return {"error": str(raw.get("error", raw))[:120]}
    if not isinstance(raw, str) or raw in ("0x", "", None):
        return {"error": "empty-return"}
    if len(raw) >= 66:
        try: return int(raw[2:66], 16)
        except Exception: return {"error": f"non-uint {raw[:40]}"}
    return {"error": f"short-return {raw[:40]}"}

# build one batch: leg3b then prio
meta, calls = [], []
for name, (addr, specs) in list(LEG3B.items()) + list(PRIO.items()):
    for key, sig, args in specs:
        meta.append((name, key))
        calls.append((addr, sel(sig) + args))
print("batch calls:", len(calls), flush=True)
try:
    raw = call_many(calls)
except Exception as e:
    raw = [{"error": f"call_many failed: {type(e).__name__}: {str(e)[:100]}"}] * len(calls)
print("batch returned:", len(raw), flush=True)

leg3b, prio_vals = {}, {}
for (name, key), r in zip(meta, raw):
    v = decode(r)
    (leg3b if name in LEG3B else prio_vals).setdefault(name, {})[key] = v

try:
    blk = race("eth_blockNumber", [])
    block = int(blk, 16) if isinstance(blk, str) else None
except Exception as e:
    block = {"error": f"{type(e).__name__}: {str(e)[:80]}"}
print("block:", block, flush=True)
json.dump({"block": block, "values": prio_vals},
          open(BASE + f"hot-leg-{STAMP}-prio.json", "w"), indent=1)

# ---- Bridge (read-only) ----
try:
    b = json.load(open(BASE + "scan-bridge.json"))
    cons = b.get("contracts", {})
    mtime = time.strftime("%Y-%m-%d %H:%M WIB", time.localtime(os.path.getmtime(BASE + "scan-bridge.json")))
    feed = json.load(open(BASE + f"hot-leg-{STAMP}-feed.json"))
    feed_addrs = [x.get("address") for x in feed.get("results", []) if x.get("address")]
    new_in_bridge = [a for a in feed_addrs if a.lower() in {k.lower() for k in cons}]
    disc = [k for k, v in cons.items() if isinstance(v, dict) and v.get("same_owner_discarded")]
    bridge_note = (f"scan-bridge.json read ({len(cons)} contracts, mtime {mtime}); "
                   f"new feed contracts in bridge: {new_in_bridge or 'none'}; "
                   f"same_owner_discarded in bridge: {len(disc)}; no bridge promotion/change this run")
except Exception as e:
    bridge_note = f"bridge read FAILED: {type(e).__name__}: {str(e)[:100]} - skipped, run continues"

# ---- Compare vs 18:19 baseline ----
base = json.load(open(BASE + "run-2026-11-11-1819.json"))
bv = base.get("leg4_values", {})
bv3b = base.get("leg3b_recheck", {})
changes, view_notes = [], []
for name in PRIO:
    for key, new in prio_vals.get(name, {}).items():
        old = bv.get(name, {}).get(key) if isinstance(bv.get(name), dict) else None
        if isinstance(old, dict) or isinstance(new, dict):
            if old != new:
                view_notes.append(f"{name}.{key}: view {old} -> {new} (view-status only, not a state change)")
            continue
        if old is None and new is None:
            continue
        if old != new:
            changes.append(f"{name}.{key}: {old} -> {new}")
for name in LEG3B:
    for key, new in leg3b.get(name, {}).items():
        old = bv3b.get(name, {}).get(key) if isinstance(bv3b.get(name), dict) else None
        if isinstance(old, dict) or isinstance(new, dict):
            if old != new:
                view_notes.append(f"leg3b {name}.{key}: view {old} -> {new} (view-status only)")
            continue
        if old is None and new is None:
            continue
        if old != new:
            changes.append(f"leg3b {name}.{key}: {old} -> {new}")

watch = []
ap = prio_vals.get("AgentPals", {})
if isinstance(ap.get("freeMinted"), int):
    watch.append(f"AgentPals freeMinted {ap['freeMinted']}/300 = {ap['freeMinted']/300*100:.1f}% (strong-lead needs >70% = >210; slot hasFreeMinted={ap.get('hasFreeMinted_user')})")
st = prio_vals.get("Stampooor", {})
if isinstance(st.get("freeMinted"), int) and isinstance(st.get("FREE_SUPPLY"), int):
    pct = st['freeMinted'] / st['FREE_SUPPLY'] * 100
    crossed = st['freeMinted'] > 840
    watch.append(f"Stampooor freeMinted {st['freeMinted']}/{st['FREE_SUPPLY']} = {pct:.1f}% (strong-lead needs >70% = >840; slot freeAvailable={st.get('freeAvailable_user')}; age: mintStart 1794362419 ~09:00 WIB 11 Nov, <24h; STRONG-LEAD-CROSSED={crossed})")

shapes = json.load(open(BASE + f"hot-leg-{STAMP}-shape.json"))
feed = json.load(open(BASE + f"hot-leg-{STAMP}-feed.json"))
feed_addrs = [x.get("address") for x in feed.get("results", []) if x.get("address")]
seen = json.load(open(BASE + "hot-leg-seen.json"))
seen_l = {k.lower() for k in seen}
new_feed = [a for a in feed_addrs if a.lower() not in seen_l]
run = {
 "run": "free-mint-hot-leg 2026-11-11 18:24 WIB (legs 3b/4/bridge recovered via fast_rpc batch)",
 "started_wib": NOW_ISO,
 "overrun_note": "Main 1824 script completed legs 1-2 then was killed by its 280s timeout during the slow sequential RPC re-reads (legs 3b/4); this recovery re-ran only legs 3b/4/bridge via fast_rpc.call_many batch. No leg was double-counted; seen.json already holds the 5 successful shape-checks from the main script.",
 "leg1_sourcify_feed": {"returned": len(feed_addrs),
   "verified_range": [feed["results"][-1].get("verifiedAt"), feed["results"][0].get("verifiedAt")],
   "new_shape_checked": list(shapes.keys()),
   "note": "21 shape-checks at main-script time: 9 fresh feed + 9 re-appearing 18:19 failures + 3 explicit retries (FFcF/fcD9/069E)"},
 "leg1_shapes": shapes,
 "leg1_s1_pass": [a for a, v in shapes.items() if isinstance(v, dict) and v.get("S1")],
 "leg1_s2_pass": [a for a, v in shapes.items() if isinstance(v, dict) and v.get("S2")],
 "leg2_boltbook": {"note": "EN HTTP 200 (46398B) + ZH HTTP 200 (46593B) boltbook.fun; 5 unique addresses, 0 not in hot-leg-seen.json: none; keywords EN free-share=0 ZH=0"},
 "bridge": bridge_note,
 "leg3_new_sale_shape": {},
 "leg3b_recheck": leg3b,
 "leg4_read_wib": NOW_ISO,
 "leg4_block": block,
 "leg4_values": prio_vals,
 "leg4_changes_vs_1819": changes or "NONE",
 "leg4_view_notes": view_notes or "NONE",
 "threshold_watch": watch,
 "shape_check_failed_not_kept": [a for a, v in shapes.items() if isinstance(v, dict) and "error" in v],
 "elapsed_s_recovery": round(time.time() - T0, 1),
}
json.dump(run, open(BASE + f"hot-leg-run-{STAMP}.json", "w"), indent=1)
print(json.dumps(run, indent=1))
