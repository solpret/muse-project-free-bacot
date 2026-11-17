#!/usr/bin/env python3
"""Free-mint-search run 2026-11-12 09:01 WIB - MERGE (generic, written fresh this run).
Merges:
  1. legs 0901 (feed 20, 4 baru vs seen, 0 S1/S2/early; Boltbook EN 44551B/6 addr,
     ZH 42951B/6 addr, 1 baru 0x8773 Sourcify 404; bridge 116/0)
  2. verify2.py key items (blok 133077089)
  3. tc-age 0901 (CLEPSYDRA / MoonAgent / WNO, blok 133077668)
  4. reread 0901 (63 kontrak + 21 track_c, blok 133077372)
  5. sweep web EN+ZH + Boltbook triage: MIZU claim (fee 0.00016 BNB = PAID, excluded
     track B), Fleet Genesis sold out (excluded, confirmed), STAMP PASS/Oathbots/
     LeadLoop/PixelFox/BURN/NAOMI/AgenticGangster all already known.
Read-only wrt chain. Writes snapshot (+ .bak-0901) and run-2026-11-12-0901-final.json.
No preview, no mint. Crossings Stampooor 74.3% / AgentPals 100% are artefacts
(prev_pct None baseline), both minted-by-user - NOT promotions.
"""
import json, shutil

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
snap_path = BASE + "onchain-snapshot.json"
shutil.copy(snap_path, BASE + "onchain-snapshot.json.bak-0901")
snap = json.load(open(snap_path))
legs = json.load(open(BASE + "run-2026-11-12-0901-legs.json"))
v2 = json.load(open(BASE + "run-2026-11-12-0901-verify2.json"))
tc = json.load(open(BASE + "run-2026-11-12-0901-tc-age.json"))
reread = json.load(open(BASE + "run-2026-11-12-0901-reread.json"))

def index(section):
    out = {}
    v = snap.get(section, {})
    if isinstance(v, dict):
        for k, it in v.items():
            if isinstance(it, dict) and it.get("address"):
                out[it["address"].lower()] = (k, it)
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

# --- verify2 key items (generic field copy) ---
for name in V2:
    s = ssum(name)
    addr = (V2[name] or {}).get("address")
    if not addr:
        continue
    fields = {f: s.get(f) for f in FIELDS if s.get(f) is not None}
    upd(addr, fields, block=VB2, wib="2026-11-12 09:05 WIB",
        note=f"Run 0901 (blok {VB2}): totalSupply/totalMinted {s.get('totalSupply') or s.get('totalMinted')}, "
             f"free {s.get('freeClaimed') or s.get('freeMinted')}, bal_user {s.get('balanceOf_user')}.",
        note_key="runNote0901")
# binanceai pending claim: launched stays 0
upd("0x46cb1D3efd4307506Cda7EbBa5a51be64746739E",
    {"launched": ssum("binanceai-mint").get("launched")},
    block=VB2, wib="2026-11-12 09:05 WIB",
    note="Run 0901: launched()=0 TETAP (pending claim, fase refund) - bukan kandidat.",
    note_key="runNote0901")
# RigForge: still not open
upd("0xa1cc0d7c0534f824f2cf6eeb865a8fede96c8f7d",
    {"freeClaimed": ssum("RigForge").get("freeClaimed"),
     "freeSharesLeft": ssum("RigForge").get("freeSharesLeft"),
     "openedAt": ssum("RigForge").get("openedAt")},
    block=VB2, wib="2026-11-12 09:05 WIB",
    note="Run 0901: freeSharesLeft 678, openedAt 0 (belum buka) - TETAP.",
    note_key="runNote0901")

# --- reread: generic update for the 63 contracts + 21 track_c ---
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
    upd(d["address"], fields, block=RB, wib="2026-11-12 09:08 WIB",
        note=f"Run 0901 reread (blok {RB}):{vel} bal_user {d.get('balanceOf_user')}.",
        note_key="runNote0901")
for name, d in reread["track_c"].items():
    if not isinstance(d, dict) or not d.get("address"):
        continue
    fields = {f: d.get(f) for f in FIELDS if d.get(f) is not None}
    upd(d["address"], fields, section="track_c", block=RB, wib="2026-11-12 09:08 WIB",
        note=f"Run 0901 reread track_c (blok {RB}): freeMinted {d.get('freeMinted')}.",
        note_key="runNote0901")

# --- tc-age: CLEPSYDRA / MoonAgent / WNO stay age-excluded ---
TCB = tc["block"]
tc_note = (
    f"Run 0901 (blok {TCB}): CLEPSYDRA startTime 2026-11-06 21:24 WIB + MoonAgent "
    f"294/800, MINT_DEADLINE 2026-11-14 11:36 WIB (tetap) -> keduanya TETAP age-excluded. "
    f"WNO totalShares 1659 (was 1656) - tetap age-excluded; saldo user 1.000.000.")
if isinstance(snap.get("age_exclusions"), list):
    snap["age_exclusions"].append(tc_note)
elif isinstance(snap.get("age_exclusions"), dict):
    snap["age_exclusions"]["runNote0901"] = tc_note
else:
    snap["age_exclusions_note0901"] = tc_note

snap["last_run_wib"] = "2026-11-12 09:01 WIB"
snap["last_run_note"] = (
    "Run 0901 SILENT: 0 kandidat baru, 0 strong lead baru, 0 early lead baru, "
    "0 track-B dibuka, 0 track-C lead/kandidat baru, 0 sellout baru, 0 age-exclusion baru. "
    "Pre-flight Ankr 401 FAIL (scan fast-fail, watermark tetap 132512564). "
    "MIZU claim fee 0.00016 BNB = PAID, excluded track B. Fleet Genesis sold out (excluded).")

final = {
    "run": "2026-11-12 09:01 WIB",
    "decision": "SILENT",
    "preflight": "FAIL Ankr HTTP 401 (scan fast-fail; watermark tetap 132512564)",
    "legs": {"feed_n": legs["feed"]["n"], "feed_new": legs["feed_new"],
             "boltbook_en": legs["boltbook_en"], "boltbook_zh": legs["boltbook_zh"],
             "boltbook_new": legs["boltbook_new"], "bridge": legs["bridge"],
             "shapes": legs["shapes"]},
    "verify2_block": VB2,
    "reread_block": RB,
    "tc_age_block": TCB,
    "crossings": crossings,
    "crossing_artefacts_baseline_none": artefacts,
    "merged_updates": updates,
    "sweep": "0 baru - STAMP PASS/Oathbots/LeadLoop/PixelFox/BURN/NAOMI/AgenticGangster sudah dikenal; "
             "MIZU claim fee 0.00016 BNB (PAID, excluded track B); Fleet Genesis sisa 0 (excluded sold-out).",
}
json.dump(final, open(BASE + "run-2026-11-12-0901-final.json", "w"), indent=1)
json.dump(snap, open(snap_path, "w"), indent=1)
print(json.dumps({"decision": "SILENT", "crossings": crossings, "artefacts": artefacts,
                  "updates": len(updates), "verify2_block": VB2, "reread_block": RB,
                  "tc_age_block": TCB}, indent=1))
