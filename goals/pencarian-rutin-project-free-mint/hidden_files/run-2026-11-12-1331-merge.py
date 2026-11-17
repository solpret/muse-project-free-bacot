#!/usr/bin/env python3
"""Free-mint-search run 2026-11-12 13:31 WIB - MERGE (rewritten fresh this run).
Merges legs 1331, verify2 1331, reread 1331, tc-age 1331, retry-legs 1331,
RigForge manual read 1331. Fixes vs 1201 merge: RigForge updated in track_c
from rigforge.json values (not hardcoded); binanceai_claim updated at top
level (not via contracts index); RAMRAIDERS delta computed vs snapshot prev;
last_run_note built from THIS run's files only; no re-adding of 1201 findings
(WUMPO / checked-0xfa1715 already in snapshot).
Writes snapshot (+ .bak-1331) and run-2026-11-12-1331-final.json. No preview/mint.
"""
import json, shutil, os

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
snap_path = BASE + "onchain-snapshot.json"
shutil.copy(snap_path, BASE + "onchain-snapshot.json.bak-1331")
snap = json.load(open(snap_path))
legs = json.load(open(BASE + "run-2026-11-12-1331-legs.json"))
v2 = json.load(open(BASE + "run-2026-11-12-1331-verify2.json"))
# 1331: verify2 transport-failed (first 8 targets None, rest deadline-skipped);
# supplement (curl transport, lean views) re-read the same targets - prefer it
# wherever verify2 has no summary.
try:
    _supp = json.load(open(BASE + "run-2026-11-12-1331-verify2-supplement.json"))
    for _nm, _rd in _supp.get("reads", {}).items():
        _cur = v2.get("reads", {}).get(_nm) or {}
        if not (_cur.get("summary")) and _rd.get("summary"):
            v2.setdefault("reads", {})[_nm] = _rd
    if _supp.get("block"):
        v2["block"] = _supp["block"]
except Exception as _e:
    print("SUPPLEMENT MERGE FAILED", _e)
tc = json.load(open(BASE + "run-2026-11-12-1331-tc-age.json"))
reread = json.load(open(BASE + "run-2026-11-12-1331-reread.json"))
retry = json.load(open(BASE + "run-2026-11-12-1331-retry-legs.json"))
rig = json.load(open(BASE + "run-2026-11-12-1331-rigforge.json"))
pre = {}
try:
    pre = json.load(open(BASE + "run-2026-11-12-1331-preflight.json"))
except Exception:
    pre = {"preflight": "FAIL", "error": "preflight json unreadable"}

def index(section):
    out = {}
    v = snap.get(section, {})
    if isinstance(v, dict):
        for k, it in v.items():
            if isinstance(it, dict):
                # track_c entries often store the address under "sale"/"token"
                for a in (it.get("address"), it.get("sale"), it.get("token")):
                    if a and isinstance(a, str) and a.startswith("0x"):
                        out[a.lower()] = (k, it)
    return out

cidx = index("contracts")
tidx = index("track_c")
updates = {}
crossings = []
artefacts = []

FIELDS = ["totalSupply", "totalMinted", "freeClaimed", "freeMinted", "FREE_SUPPLY",
          "MAX_SUPPLY", "mintOpen", "balanceOf_user", "freeClaimed_user",
          "freeUsed_user", "mintedBy_user", "freeMintedBy_user",
          "freeAvailable_user", "launched", "freeSharesLeft", "openedAt",
          "FREE_SHARES", "PRICE", "price", "mintStart", "saleStart", "saleEnd"]

def upd(addr, fields, section="contracts", block=None, wib=None, note=None, note_key=None):
    idx = cidx if section == "contracts" else tidx
    key = idx.get(addr.lower())
    if key is None:
        updates[addr] = "NOT-IN-SNAPSHOT"
        return
    k, it = key
    for f, val in fields.items():
        if val is not None:
            it[f] = val
    if block:
        it["lastReadBlock"] = block
    if wib:
        it["lastReadWib"] = wib
    if note and note_key:
        it[note_key] = note
    updates[addr] = k

# --- threshold-crossing check on reread (free% vs FREE_SUPPLY, vs snapshot prev) ---
for name, d in reread["reread"].items():
    if not isinstance(d, dict) or not d.get("address"):
        continue
    key = cidx.get(d["address"].lower())
    if key is None:
        continue
    k, it = key
    fm = d.get("freeMinted") if d.get("freeMinted") is not None else it.get("freeClaimed")
    cap = d.get("FREE_SUPPLY") if d.get("FREE_SUPPLY") is not None else it.get("FREE_SUPPLY")
    if fm is not None and cap:
        pct = 100.0 * fm / cap
        prev = it.get("freeClaimed")
        prev_cap = it.get("FREE_SUPPLY")
        prev_pct = (100.0 * prev / prev_cap) if (prev is not None and prev_cap) else None
        if pct >= 50 and (prev_pct is None or prev_pct < 50):
            (artefacts if prev_pct is None else crossings).append(
                f"{name}: {prev_pct}% -> {pct:.1f}% (cross 50%)")
        if pct > 70 and (prev_pct is None or prev_pct <= 70):
            (artefacts if prev_pct is None else crossings).append(
                f"{name}: {prev_pct}% -> {pct:.1f}% (cross 70%)")

VB2 = v2["block"]
V2 = v2["reads"]
def ssum(name):
    return (V2.get(name) or {}).get("summary") or {}

WIB = "2026-11-12 13:31 WIB"
for name in V2:
    s = ssum(name)
    if not s:
        continue  # deadline-hit-skipped - no junk note
    addr = (V2[name] or {}).get("address")
    if not addr:
        continue
    if (V2[name] or {}).get("error"):
        continue
    fields = {f: s.get(f) for f in FIELDS if s.get(f) is not None}
    upd(addr, fields, block=VB2, wib=WIB,
        note=f"Run 1331 (blok {VB2}): totalSupply/totalMinted {s.get('totalSupply') or s.get('totalMinted')}, "
             f"free {s.get('freeClaimed') or s.get('freeMinted')}, bal_user {s.get('balanceOf_user')}.",
        note_key="runNote1331")

# --- binanceai pending claim: top-level binanceai_claim, NOT contracts ---
bc = snap.get("binanceai_claim")
if isinstance(bc, dict):
    lv = ssum("binanceai-mint").get("launched")
    if lv is not None:
        bc["launched"] = lv
    bc["lastReadBlock"] = VB2
    bc["lastReadWib"] = WIB
    bc["runNote1331"] = f"Run 1331: launched()={lv} TETAP (pending claim, fase refund) - bukan kandidat."
    updates["0x46cb1D3efd4307506Cda7EbBa5a51be64746739E"] = "binanceai_claim"

# --- RigForge: lives in track_c; values from THIS run's rigforge.json ---
rv = (rig.get("RigForge") or {}).get("views") or {}
if rv:
    upd("0xa1cc0d7c0534f824f2cf6eeb865a8fede96c8f7d",
        {"freeClaimed": rv.get("freeClaimed"), "freeSharesLeft": rv.get("freeSharesLeft"),
         "openedAt": rv.get("openedAt"), "freeBooked_user": rv.get("freeBooked_user")},
        section="track_c", block=VB2, wib=WIB,
        note=(f"Run 1331: freeClaimed {rv.get('freeClaimed')}/1000, freeSharesLeft {rv.get('freeSharesLeft')}, "
              f"openedAt {rv.get('openedAt')}, freeBooked(user) {rv.get('freeBooked_user')} - baca manual, verify2 deadline-skip."),
        note_key="runNote1331")

RB = reread["block"]
for name, d in reread["reread"].items():
    if not isinstance(d, dict) or not d.get("address"):
        continue
    fields = {f: d.get(f) for f in FIELDS if d.get(f) is not None}
    key = cidx.get(d["address"].lower())
    vel = ""
    if key is not None:
        k, it = key
        prev_ts = it.get("totalSupply")
        cur_ts = d.get("totalSupply")
        if prev_ts is not None and cur_ts is not None:
            vel = f" totalSupply {prev_ts}->{cur_ts} (+{cur_ts - prev_ts})."
    upd(d["address"], fields, block=RB, wib=WIB,
        note=f"Run 1331 reread (blok {RB}):{vel} bal_user {d.get('balanceOf_user')}.",
        note_key="runNote1331")
for name, d in reread["track_c"].items():
    if not isinstance(d, dict) or not d.get("address"):
        continue
    fields = {f: d.get(f) for f in FIELDS if d.get(f) is not None}
    upd(d["address"], fields, section="track_c", block=RB, wib=WIB,
        note=f"Run 1331 reread track_c (blok {RB}): freeMinted {d.get('freeMinted')}.",
        note_key="runNote1331")

# --- RAMRAIDERS: delta vs snapshot prev (computed, not hardcoded) ---
ram = reread["reread"].get("RAMRAIDERS", {})
ram_entry = snap.get("contracts", {}).get("RAMRAIDERS")
if isinstance(ram_entry, dict) and ram.get("totalSupply") is not None:
    prev_ts = ram_entry.get("totalSupply")
    delta = ram["totalSupply"] - prev_ts if prev_ts is not None else None
    ram_entry["totalSupply"] = ram.get("totalSupply")
    ram_entry["freeMinted"] = ram.get("freeMinted")
    ram_entry["MAX_SUPPLY"] = ram.get("MAX_SUPPLY") or ram_entry.get("MAX_SUPPLY")
    ram_entry["balanceOf_user"] = ram.get("balanceOf_user")
    ram_entry["lastReadBlock"] = RB
    ram_entry["lastReadWib"] = WIB
    ram_entry["runNote1331"] = (f"Run 1331 reread (blok {RB}): totalSupply {ram.get('totalSupply')} "
        f"(+{delta} vs {prev_ts} run 1231), freeMinted {ram.get('freeMinted')}, MAX_SUPPLY 7777, bal_user 0. "
        "Umur + free% TETAP UNVERIFIED; bukan early/strong lead/kandidat.")
    updates["0x98dcfdeb5e015bbb3c9aca2a90ba0ee80e35315b"] = "RAMRAIDERS"

# --- tc-age note (WNO prev read from snapshot age note is unreliable; use tc values only) ---
TCB = tc["block"]
wno_ts = tc.get("WNO", {}).get("totalShares")
moa = tc.get("MoonAgent", {})
tc_note = (
    f"Run 1331 (blok {TCB}): CLEPSYDRA startTime 2026-11-06 21:24 WIB + MoonAgent "
    f"{moa.get('totalMints')}/800, MINT_DEADLINE 2026-11-14 11:36 WIB (tetap) -> keduanya TETAP age-excluded. "
    f"WNO totalShares {wno_ts} - tetap age-excluded; saldo user 1.000.000.")
if isinstance(snap.get("age_exclusions"), list):
    snap["age_exclusions"].append(tc_note)
elif isinstance(snap.get("age_exclusions"), dict):
    snap["age_exclusions"]["runNote1331"] = tc_note
else:
    snap["age_exclusions_note1331"] = tc_note

feed = legs.get("feed", {})
pre_txt = "OK" if pre.get("preflight") == "OK" else f"FAIL ({pre.get('error', 'unknown')})"
snap["last_run_wib"] = "2026-11-12 13:31 WIB"
snap["last_run_note"] = (
    "Run 1331 SILENT (pending final sweep check): pre-flight " + pre_txt + " (scan fast-fail, watermark tidak dimajukan). "
    f"Legs: feed {feed.get('n')} (verified {feed.get('oldest_verifiedAt')} s.d. {feed.get('newest_verifiedAt')}), "
    f"{len(legs.get('feed_new', []))} baru vs hot-leg-seen, {len(legs.get('boltbook_new', []))} baru Boltbook; "
    f"shapes S1/S2/early dihitung dari legs.json. Retry-legs {retry.get('retried')} alamat. "
    f"Verify2 blok {VB2}; reread blok {RB}; tc-age blok {TCB}. "
    "Detail sweep + keputusan akhir di run-2026-11-12-1331-runlog.md.")

final = {
    "run": "2026-11-12 13:31 WIB",
    "decision": "PENDING-SWEEP",
    "preflight": pre,
    "legs": {"feed_n": legs["feed"]["n"], "feed_new": legs["feed_new"],
             "boltbook_en": legs["boltbook_en"], "boltbook_zh": legs["boltbook_zh"],
             "boltbook_new": legs["boltbook_new"], "bridge": legs["bridge"],
             "shapes": legs["shapes"]},
    "retry_legs_errors": {"retried": retry["retried"], "now_verified": retry["now_verified"],
                          "still_error_n": len(retry["still_error"])},
    "verify2_block": VB2,
    "reread_block": RB,
    "tc_age_block": TCB,
    "crossings": crossings,
    "crossing_artefacts_baseline_none": artefacts,
    "merged_updates": updates,
}
json.dump(final, open(BASE + "run-2026-11-12-1331-final.json", "w"), indent=1)
json.dump(snap, open(snap_path, "w"), indent=1)
print(json.dumps({"decision": "PENDING-SWEEP", "crossings": crossings, "artefacts": artefacts,
                  "updates": len(updates), "verify2_block": VB2, "reread_block": RB,
                  "tc_age_block": TCB}, indent=1))
