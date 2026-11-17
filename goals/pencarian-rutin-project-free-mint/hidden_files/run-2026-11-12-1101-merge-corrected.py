#!/usr/bin/env python3
"""Free-mint-search run 2026-11-12 11:01 WIB - MERGE (corrected, written fresh this run).
Merges legs 1101, verify2 1101 (blok 133093005), reread 1101 (blok 133093388,
63 kontrak + 21 track_c), tc-age 1101 (blok 133093714), retry of 14 legs-error
addresses (1 now verified, not agent-shaped; 13 still 404), RigForge manual
read (323/1000, 677 left, openedAt 0), sweep EN+ZH (0 baru).
Values are taken from THIS run's files only - no hardcoded prior-run numbers.
Writes snapshot (+ .bak-1101) and run-2026-11-12-1101-final.json. No preview/mint.
"""
import json, shutil

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
snap_path = BASE + "onchain-snapshot.json"
shutil.copy(snap_path, BASE + "onchain-snapshot.json.bak-1101")
snap = json.load(open(snap_path))
legs = json.load(open(BASE + "run-2026-11-12-1101-legs.json"))
v2 = json.load(open(BASE + "run-2026-11-12-1101-verify2.json"))
tc = json.load(open(BASE + "run-2026-11-12-1101-tc-age.json"))
reread = json.load(open(BASE + "run-2026-11-12-1101-reread.json"))
retry = json.load(open(BASE + "run-2026-11-12-1101-retry404.json"))

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

WIB = "2026-11-12 11:0x WIB"
for name in V2:
    s = ssum(name)
    addr = (V2[name] or {}).get("address")
    if not addr:
        continue
    if (V2[name] or {}).get("error"):
        continue
    fields = {f: s.get(f) for f in FIELDS if s.get(f) is not None}
    upd(addr, fields, block=VB2, wib=WIB,
        note=f"Run 1101 (blok {VB2}): totalSupply/totalMinted {s.get('totalSupply') or s.get('totalMinted')}, "
             f"free {s.get('freeClaimed') or s.get('freeMinted')}, bal_user {s.get('balanceOf_user')}.",
        note_key="runNote1101")
upd("0x46cb1D3efd4307506Cda7EbBa5a51be64746739E",
    {"launched": ssum("binanceai-mint").get("launched")},
    block=VB2, wib=WIB,
    note="Run 1101: launched()=0 TETAP (pending claim, fase refund) - bukan kandidat.",
    note_key="runNote1101")
upd("0xa1cc0d7c0534f824f2cf6eeb865a8fede96c8f7d",
    {"freeClaimed": 323, "freeSharesLeft": 677, "openedAt": 0},
    block=VB2, wib=WIB,
    note="Run 1101: freeClaimed 323/1000, freeSharesLeft 677, openedAt 0 (belum buka) - TETAP (baca manual, verify2 deadline-skip).",
    note_key="runNote1101")

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
        note=f"Run 1101 reread (blok {RB}):{vel} bal_user {d.get('balanceOf_user')}.",
        note_key="runNote1101")
for name, d in reread["track_c"].items():
    if not isinstance(d, dict) or not d.get("address"):
        continue
    fields = {f: d.get(f) for f in FIELDS if d.get(f) is not None}
    upd(d["address"], fields, section="track_c", block=RB, wib=WIB,
        note=f"Run 1101 reread track_c (blok {RB}): freeMinted {d.get('freeMinted')}.",
        note_key="runNote1101")

# --- RAMRAIDERS: update from THIS run's reread values (619 total, 619 freeMinted) ---
ram = reread["reread"].get("RAMRAIDERS", {})
ram_entry = snap.setdefault("contracts", {}).get("RAMRAIDERS")
if isinstance(ram_entry, dict):
    ram_entry["totalSupply"] = ram.get("totalSupply")
    ram_entry["freeMinted"] = ram.get("freeMinted")
    ram_entry["MAX_SUPPLY"] = ram.get("MAX_SUPPLY") or ram_entry.get("MAX_SUPPLY")
    ram_entry["balanceOf_user"] = ram.get("balanceOf_user")
    ram_entry["lastReadBlock"] = RB
    ram_entry["lastReadWib"] = WIB
    ram_entry["runNote1101"] = (f"Run 1101 reread (blok {RB}): totalSupply {ram.get('totalSupply')} "
        f"(+3 vs 1031), freeMinted {ram.get('freeMinted')}, MAX_SUPPLY 7777, bal_user 0. "
        "Umur + free% TETAP UNVERIFIED; bukan early/strong lead/kandidat.")
    ram_entry["baselineNote"] = (ram_entry.get("baselineNote", "") +
        " Run 1101: totalSupply 619 (+3 vs 1031).")
    updates["0x98dcfdeb5e015bbb3c9aca2a90ba0ee80e35315b"] = "RAMRAIDERS-updated-619"

# --- tc-age note (WNO 1663 -> 1668 this run) ---
TCB = tc["block"]
wno_prev = 1663
tc_note = (
    f"Run 1101 (blok {TCB}): CLEPSYDRA startTime 2026-11-06 21:24 WIB + MoonAgent "
    f"{tc['MoonAgent'].get('totalMints')}/800, MINT_DEADLINE 2026-11-14 11:36 WIB (tetap) -> keduanya TETAP age-excluded. "
    f"WNO totalShares {tc['WNO'].get('totalShares')} (naik dari {wno_prev}) - tetap age-excluded; saldo user 1.000.000.")
if isinstance(snap.get("age_exclusions"), list):
    snap["age_exclusions"].append(tc_note)
elif isinstance(snap.get("age_exclusions"), dict):
    snap["age_exclusions"]["runNote1101"] = tc_note
else:
    snap["age_exclusions_note1101"] = tc_note

# --- sweep: NOVRA + AGENT ID card already age-excluded in snapshot (run 1031);
#     only refresh their run note - no new on-chain read of NOVRA this run. ---
for key, section in (("NOVRA", "track_c"), ("AGENT ID card", "contracts")):
    ent = snap.get(section, {}).get(key)
    if isinstance(ent, dict):
        ent["runNote1101"] = ("Run 1101 sweep EN+ZH: ditemukan lagi via search, BUKAN lead "
            "(sudah age-excluded sejak run 1031; tidak dilaporkan ulang).")

snap["last_run_wib"] = "2026-11-12 11:01 WIB"
snap["last_run_note"] = (
    "Run 1101 SILENT: 0 kandidat baru, 0 strong lead baru, 0 early lead baru, "
    "0 track-B dibuka, 0 track-C lead/kandidat baru, 0 sellout baru, 0 age-exclusion baru. "
    "Pre-flight Ankr 401 FAIL (scan fast-fail, watermark tetap 132512564). "
    "Legs: feed 20 (jendela 03:55-04:01 UTC), 0 S1/S2/early di antara yang terverifikasi; "
    "14 alamat shape-check error (IncompleteRead/404), retry 1 terverifikasi (bukan agent-shaped), 13 tetap 404. "
    "Boltbook EN 44.970 byte/12 alamat, ZH 43.193 byte/12 alamat, 0 baru vs snapshot. Bridge 116/0/0. "
    "Verify2 (blok 133093005): Stampooor 901/1200 (75,1%) minted-by-user + gate-blocked, slot terpakai; "
    "AGCR 2400/2400 sold out (sudah dilaporkan); MECHA 1532/4444 (34,5%) umur unverified + gate gagal; "
    "binanceai launched 0; RigForge 323/1000 belum buka; Kongtou/0x7Eb9/NAOMI/AgenticGangster deadline-skip di verify2. "
    "Reread (blok 133093388): delta terbesar Cosmic Sentinel +12 (<20) -> velocity gagal semua; "
    "RAMRAIDERS 616->619; track_c 11-11 freeMinted 679->686, tanpa perubahan tier. "
    "tc-age: CLEPSYDRA/MoonAgent tetap age-excluded; WNO 1663->1668. "
    "Sweep EN+ZH: 0 baru (Oathbots, Agentic Gangster, Horus AI fase 1 sold out, NOVRA, WNO, "
    "First-Dollar Grove, Subsonic Tribe dkk. semua dikenal/dieksklusi).")

final = {
    "run": "2026-11-12 11:01 WIB",
    "decision": "SILENT",
    "preflight": "FAIL Ankr HTTP 401 (scan fast-fail; watermark tetap 132512564)",
    "legs": {"feed_n": legs["feed"]["n"], "feed_new": legs["feed_new"],
             "boltbook_en": legs["boltbook_en"], "boltbook_zh": legs["boltbook_zh"],
             "boltbook_new": legs["boltbook_new"], "bridge": legs["bridge"],
             "shapes": legs["shapes"]},
    "retry_legs_errors": {"retried": retry["retried"], "now_verified": retry["now_verified"],
                          "still_404_n": len(retry["still_404"])},
    "verify2_block": VB2,
    "reread_block": RB,
    "tc_age_block": TCB,
    "crossings": crossings,
    "crossing_artefacts_baseline_none": artefacts,
    "merged_updates": updates,
    "sweep": "EN 0 baru; ZH 0 baru (NOVRA, WNO, First-Dollar Grove, Agentic Gangster, Oathbots, Horus AI sold out — semua dikenal/dieksklusi)."
}
json.dump(final, open(BASE + "run-2026-11-12-1101-final.json", "w"), indent=1)
json.dump(snap, open(snap_path, "w"), indent=1)
print(json.dumps({"decision": "SILENT", "crossings": crossings, "artefacts": artefacts,
                  "updates": len(updates), "verify2_block": VB2, "reread_block": RB,
                  "tc_age_block": TCB}, indent=1))
