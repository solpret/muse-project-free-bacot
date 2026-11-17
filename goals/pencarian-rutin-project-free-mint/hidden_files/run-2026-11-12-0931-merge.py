#!/usr/bin/env python3
"""Free-mint-search run 2026-11-12 09:31 WIB - MERGE (generic, written fresh this run).
Merges:
  1. legs 0931 (feed 20, 0 baru vs seen, 0 S1/S2/early; Boltbook EN 44107 chr/7 addr,
     ZH 42372 chr/7 addr, 0 baru; bridge 116/0; preflight Ankr 401 FAIL -> scan fast-fail)
  2. verify2.py key items (blok 133081304)
  3. tc-age 0931 (CLEPSYDRA / MoonAgent / WNO, blok 133081744)
  4. reread 0931 (63 kontrak + 21 track_c, blok 133081568)
  5. retry404: 22 alamat 404 hari ini di-retry, 4 kini terverifikasi tapi S1=S2=early=False;
     18 tetap 404.
  6. RAMRAIDERS 0x98dcfdeb...: agent-shaped terverifikasi (agentIdRegistry, freeMinted 598,
     MAX_SUPPLY 7777, mintActive 1) tapi BUKAN early lead (bukan first-seen run ini;
     sudah dibaca run 0901), free% UNVERIFIED (tanpa FREE_SUPPLY view), umur UNVERIFIED
     (Ankr 401 memblokir koroborasi first-mint via getLogs) -> ditambahkan ke snapshot
     sebagai watchlist-only-unverified, TANPA laporan.
  7. sweep web EN+ZH: 0 baru - RIGBYPASS/MOLT/STAMP/Oathbots/AgenticGangster/AGENT MAO
     semuanya sudah dikenal/dieksklusi; Medium 8-free-mints (2 Nov) hanya proyek lama.
Read-only wrt chain. Writes snapshot (+ .bak-0931) and run-2026-11-12-0931-final.json.
No preview, no mint. Crossings Stampooor 74.42% / AgentPals 100% are artefacts
(prev_pct already above threshold / minted-by-user) - NOT promotions.
"""
import json, shutil

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
snap_path = BASE + "onchain-snapshot.json"
shutil.copy(snap_path, BASE + "onchain-snapshot.json.bak-0931")
snap = json.load(open(snap_path))
legs = json.load(open(BASE + "run-2026-11-12-0931-legs.json"))
v2 = json.load(open(BASE + "run-2026-11-12-0931-verify2.json"))
tc = json.load(open(BASE + "run-2026-11-12-0931-tc-age.json"))
reread = json.load(open(BASE + "run-2026-11-12-0931-reread.json"))
retry404 = json.load(open(BASE + "run-2026-11-12-0931-retry404.json"))

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
    upd(addr, fields, block=VB2, wib="2026-11-12 09:35 WIB",
        note=f"Run 0931 (blok {VB2}): totalSupply/totalMinted {s.get('totalSupply') or s.get('totalMinted')}, "
             f"free {s.get('freeClaimed') or s.get('freeMinted')}, bal_user {s.get('balanceOf_user')}.",
        note_key="runNote0931")
# binanceai pending claim: launched stays 0
upd("0x46cb1D3efd4307506Cda7EbBa5a51be64746739E",
    {"launched": ssum("binanceai-mint").get("launched")},
    block=VB2, wib="2026-11-12 09:35 WIB",
    note="Run 0931: launched()=0 TETAP (pending claim, fase refund) - bukan kandidat.",
    note_key="runNote0931")
# RigForge: still not open
upd("0xa1cc0d7c0534f824f2cf6eeb865a8fede96c8f7d",
    {"freeClaimed": ssum("RigForge").get("freeClaimed"),
     "freeSharesLeft": ssum("RigForge").get("freeSharesLeft"),
     "openedAt": ssum("RigForge").get("openedAt")},
    block=VB2, wib="2026-11-12 09:35 WIB",
    note="Run 0931: freeClaimed 323/1000, freeSharesLeft 677, openedAt 0 (belum buka) - TETAP.",
    note_key="runNote0931")

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
    upd(d["address"], fields, block=RB, wib="2026-11-12 09:38 WIB",
        note=f"Run 0931 reread (blok {RB}):{vel} bal_user {d.get('balanceOf_user')}.",
        note_key="runNote0931")
for name, d in reread["track_c"].items():
    if not isinstance(d, dict) or not d.get("address"):
        continue
    fields = {f: d.get(f) for f in FIELDS if d.get(f) is not None}
    upd(d["address"], fields, section="track_c", block=RB, wib="2026-11-12 09:38 WIB",
        note=f"Run 0931 reread track_c (blok {RB}): freeMinted {d.get('freeMinted')}.",
        note_key="runNote0931")

# --- RAMRAIDERS: add as watchlist-only-unverified (agent-shaped, no tier met) ---
ram = reread["reread"].get("RAMRAIDERS", {})
snap.setdefault("contracts", {})["RAMRAIDERS"] = {
    "address": "0x98dcfdeb5e015bbb3c9aca2a90ba0ee80e35315b",
    "status": "watchlist-only-unverified-2026-11-12",
    "name": "RAMRAIDERS",
    "kind": "ERC721",
    "totalSupply": ram.get("totalSupply"),
    "freeMinted": ram.get("freeMinted"),
    "MAX_SUPPLY": ram.get("MAX_SUPPLY"),
    "mintActive": 1,
    "balanceOf_user": ram.get("balanceOf_user"),
    "userFreeUsed": None,
    "xVerified": False,
    "velocityVerified": False,
    "launchNote": ("Umur peluncuran UNVERIFIED: tidak ada waktu launch dinyatakan proyek yang "
                   "ditemukan; koroborasi first-mint via eth_getLogs TIDAK bisa jalan run ini "
                   "(Ankr 401 sejak 9 Nov; RPC publik tolak eth_getLogs)."),
    "baselineNote": ("Agent-shaped terverifikasi run 0931 (Sourcify 164 fns: agentIdRegistry, "
                     "freeMinted/freeUsed, mint, tokenURI/ownerOf). freeMinted 598, MAX_SUPPLY 7777, "
                     "tanpa view FREE_SUPPLY -> kaki free% UNVERIFIED (598/7777 = 7,7% total-supply "
                     "bukan ukuran kuota gratis). BUKAN early lead: bukan first-seen run ini "
                     "(sudah dibaca run 0901). BUKAN strong lead/kandidat: <50% dan umur unverified. "
                     "Ditambahkan ke snapshot sebagai watchlist-only; website belum dicek "
                     "(tidak diperlukan untuk watchlist-only)."),
    "lastReadBlock": RB,
    "lastReadWib": "2026-11-12 09:38 WIB",
    "runNote0931": f"Run 0931 reread (blok {RB}): totalSupply 598, freeMinted 598, mintActive 1, bal_user 0.",
}
updates["0x98dcfdeb5e015bbb3c9aca2a90ba0ee80e35315b"] = "RAMRAIDERS-ADDED-watchlist-only-unverified"

# --- tc-age: CLEPSYDRA / MoonAgent / WNO stay age-excluded ---
TCB = tc["block"]
tc_note = (
    f"Run 0931 (blok {TCB}): CLEPSYDRA startTime 2026-11-06 21:24 WIB + MoonAgent "
    f"294/800, MINT_DEADLINE 2026-11-14 11:36 WIB (tetap) -> keduanya TETAP age-excluded. "
    f"WNO totalShares 1659 (tetap) - tetap age-excluded; saldo user 1.000.000.")
if isinstance(snap.get("age_exclusions"), list):
    snap["age_exclusions"].append(tc_note)
elif isinstance(snap.get("age_exclusions"), dict):
    snap["age_exclusions"]["runNote0931"] = tc_note
else:
    snap["age_exclusions_note0931"] = tc_note

snap["last_run_wib"] = "2026-11-12 09:31 WIB"
snap["last_run_note"] = (
    "Run 0931 SILENT: 0 kandidat baru, 0 strong lead baru, 0 early lead baru, "
    "0 track-B dibuka, 0 track-C lead/kandidat baru, 0 sellout baru, 0 age-exclusion baru. "
    "Pre-flight Ankr 401 FAIL (scan fast-fail, watermark tetap 132512564). "
    "RAMRAIDERS ditambahkan watchlist-only-unverified (agent-shaped, umur + free% unverified). "
    "Retry404: 4 kini terverifikasi, 0 sale-shape. Stampooor 893/1200 (74,4%) tetap gate-blocked; "
    "AGCR 2399/2400 umur unverified; binanceai launched 0; RigForge belum buka.")

final = {
    "run": "2026-11-12 09:31 WIB",
    "decision": "SILENT",
    "preflight": "FAIL Ankr HTTP 401 (scan fast-fail; watermark tetap 132512564)",
    "legs": {"feed_n": legs["feed"]["n"], "feed_new": legs["feed_new"],
             "boltbook_en": legs["boltbook_en"], "boltbook_zh": legs["boltbook_zh"],
             "boltbook_new": legs["boltbook_new"], "bridge": legs["bridge"],
             "shapes": legs["shapes"]},
    "retry404": {"retried": retry404["retried"], "now_verified": retry404["now_verified"],
                 "still_404_n": len(retry404["still_404"])},
    "verify2_block": VB2,
    "reread_block": RB,
    "tc_age_block": TCB,
    "crossings": crossings,
    "crossing_artefacts_baseline_none": artefacts,
    "merged_updates": updates,
    "ramraiders": "added watchlist-only-unverified (agent-shaped; umur + free% UNVERIFIED; bukan early/strong lead/kandidat)",
    "sweep": "0 baru - RIGBYPASS/MOLT/STAMP/Oathbots/AgenticGangster/AGENT MAO sudah dikenal/dieksklusi; Medium 8-free-mints (2 Nov) hanya proyek lama.",
}
json.dump(final, open(BASE + "run-2026-11-12-0931-final.json", "w"), indent=1)
json.dump(snap, open(snap_path, "w"), indent=1)
print(json.dumps({"decision": "SILENT", "crossings": crossings, "artefacts": artefacts,
                  "updates": len(updates), "verify2_block": VB2, "reread_block": RB,
                  "tc_age_block": TCB}, indent=1))
