#!/usr/bin/env python3
"""Merge run 2201 (scheduled 2026-11-11 22:01 WIB) into onchain-snapshot.json.
Inputs: run-2026-11-11-2201-reread.json (62 contracts + 23 track_c; head block
132989060), run-2026-11-11-2201-legs.json, run-2026-11-11-2201-triage.json,
run-2026-11-11-2201-verify-new.json. Writes snapshot (with .bak).
0 kandidat baru, 0 strong lead baru, 0 track-B dibuka, 0 track-C lead baru.
0 early lead BARU dari job ini. Early leads MECHA/BUCKET/MOONDRILL/0x2e50/
CRTSAINTS naik tipis (max BUCKET 8,37%) - jauh dari 50% / >70%.
Age: MYCELIX (~21:47), REWINDCLUB (~21:49), LCDSPRITE (~21:52) melewati
deadline 24 jam run ini TAPI status minted-by-user (sudah dimiliki) -> tetap
dilacak seperti HIVE/Bubblebruin/Zapcourier/RIMEVAULT/SOLDERCATS (praktik
mapan: age-exclusion berlaku untuk watchlist aktif, bukan holdings).
NAOMI GENESIS: verifikasi segar freeMinted 777/777 = tetap SOLD OUT
(artikel thecolony '338 remain' basi); status checked tidak berubah.
"""
import json, shutil
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
snap = json.load(open(BASE + "onchain-snapshot.json"))
reread = json.load(open(BASE + "run-2026-11-11-2201-reread.json"))
legs = json.load(open(BASE + "run-2026-11-11-2201-legs.json"))
triage = json.load(open(BASE + "run-2026-11-11-2201-triage.json"))
verify = json.load(open(BASE + "run-2026-11-11-2201-verify-new.json"))
shutil.copy(BASE + "onchain-snapshot.json", BASE + "onchain-snapshot.json.bak-2201-premerge")
C = snap.setdefault("contracts", {})
TC = snap.setdefault("track_c", {})
BLOCK = reread.get("block")
TS = "2026-11-11 22:01 WIB"

def vel(name, new_supply, interval=30.0):
    e = C.get(name)
    if not isinstance(e, dict): return None
    old = e.get("totalSupply")
    if old is None or new_supply is None: return None
    diff = new_supply - old
    prev_rate = e.get("currentRatePerMin")
    rate = round(diff / interval, 4)
    e["previousTotalSupply"] = old
    e["totalSupply"] = new_supply
    e["mintedInInterval"] = diff
    e["intervalMinutes"] = interval
    e["previousRatePerMin"] = prev_rate
    e["currentRatePerMin"] = rate
    ratio = round(rate / prev_rate, 2) if prev_rate and prev_rate > 0 else None
    e["velocityRatio"] = ratio
    e["velocityLegPasses"] = bool(ratio is not None and ratio >= 1.5 and diff >= 20)
    e["lastReadBlock"] = BLOCK
    e["lastReadWib"] = TS
    return diff, rate, ratio

vel_pass, vel_fail, batch_fail = [], [], []
for name, d in reread["reread"].items():
    if name not in C: continue
    e = C[name]
    if d.get("_batch_fail"):
        batch_fail.append(name)
        e["runNote2201_1111"] = ("Run 2201 (blok %s): baca batch GAGAL (transport) - nilai lama "
            "dipertahankan, BUKAN nol; velocity TIDAK dihitung run ini; status %s." % (BLOCK, e.get("status")))
        continue
    ns = d.get("totalSupply")
    if ns is None and d.get("totalMinted") is not None: ns = d.get("totalMinted")
    if ns is not None:
        r = vel(name, ns)
        if r and e.get("velocityLegPasses"): vel_pass.append((name, r))
        elif r: vel_fail.append((name, r))
    else:
        e["lastReadBlock"] = BLOCK; e["lastReadWib"] = TS
    for k in ("totalMinted","freeMinted","freeClaimed","FREE_SUPPLY","MAX_SUPPLY","mintOpen","balanceOf_user","freeClaimed_user"):
        if d.get(k) is not None: e[k] = d[k]
    if d.get("totalSupply") is not None: e["totalSupply"] = d["totalSupply"]

def note(name, text):
    if isinstance(C.get(name), dict):
        C[name]["runNote2201_1111"] = text

st = C.get("Stampooor Stamp Packs")
if isinstance(st, dict):
    st["status"] = "strong-lead-gate-blocked-2026-11-11"
    note("Stampooor Stamp Packs",
     "Run 2201: freeMinted 860->866/1200 = 72,17% (>70%, tetap strong lead); umur TERVERIFIKASI <24 jam "
     "(mintStart 1794362419 = 11 Nov 09:00:19 WIB; deadline ~09:00 WIB 12 Nov); slot user TERBUKA (balanceOf 0, "
     "mintOpen 1). Velocity tidak relevan untuk strong-lead direct mint. GATE tetap gagal (situs tidak load; "
     "gate-blocked-recheck menangani cek ulang). TIDAK di-preview, TIDAK di-mint, TIDAK dilaporkan ulang (tanpa perubahan tier).")

note("AgentPals",
     "Run 2201 (blok 132989060): freeMinted 300/300 (free pool SOLD OUT), totalMinted 301 (+1 di luar cap, tercatat bukan perubahan tier/slot); balanceOf user 1. TIDAK dilaporkan ulang.")
note("MYCELIX",
     "Run 2201: totalSupply 621->622 (+1, velocity GAGAL). DEADLINE UMUR 24 JAM LEWAT run ini (mintStart 1794322052 = 10 Nov 21:47:32 WIB -> deadline ~21:47 WIB 11 Nov). "
     "TETAP DILACAK: status minted-by-user (sudah dimiliki, bukan kandidat aktif) - age-exclusion berlaku untuk watchlist aktif, bukan holdings (praktik mapan).")
note("REWINDCLUB",
     "Run 2201: totalSupply 562->563 (+1, velocity GAGAL). DEADLINE UMUR 24 JAM LEWAT run ini (mintStart 1794322145 = 10 Nov 21:49:05 WIB -> deadline ~21:49 WIB 11 Nov). "
     "TETAP DILACAK: status minted-by-user - age-exclusion berlaku untuk watchlist aktif, bukan holdings.")
note("LCDSPRITE",
     "Run 2201: totalSupply 582->583 (+1, velocity GAGAL). DEADLINE UMUR 24 JAM LEWAT run ini (mintStart 1794322332 = 10 Nov 21:52:12 WIB -> deadline ~21:52 WIB 11 Nov). "
     "TETAP DILACAK: status minted-by-user - age-exclusion berlaku untuk watchlist aktif, bukan holdings.")
note("RIMEVAULT",
     "Run 2201: totalSupply 1065->1068 (+3, velocity GAGAL). Deadline 24 jam sudah lewat run 2131; status minted-by-user -> TETAP DILACAK.")
note("SOLDERCATS",
     "Run 2201: totalSupply 546->548 (+2, velocity GAGAL). Deadline 24 jam sudah lewat run 2131; status minted-by-user -> TETAP DILACAK.")
han = C.get("HANAMI BLOOM")
if isinstance(han, dict):
    note("HANAMI BLOOM",
     "Run 2201: SEMUA view gagal baca (totalSupply/balanceOf None) - degradasi RPC, BUKAN nol; nilai lama (totalSupply 110) dipertahankan, velocity TIDAK dihitung. "
     "Status early-lead-reported-2026-11-11; deadline ~12:59 WIB 12 Nov. TIDAK di-preview/dimint.")
note("RAMRAIDERS",
     "Run 2201: totalSupply 565->568 (+3, velocity GAGAL); freeMinted 568/7777 = 7,30%. Umur masih UNVERIFIED; X/website UNVERIFIED. Tetap EARLY, tanpa promosi.")
note("STALL",
     "Run 2201: totalSupply 1983->1987 (+4, velocity GAGAL). Free% UNVERIFIED, umur UNVERIFIED, X/website UNVERIFIED. Tetap EARLY.")
note("BYTEBLOOM",
     "Run 2201: totalSupply 834->842 (+8, 0,267/mnt vs prev 0,1333 = 2,0x) TAPI <20 token -> velocity GAGAL. Status minted-by-user-2026-11-10; tanpa perubahan.")

# --- verify-new early leads ---
v = verify.get("verify", {})
def vnote(name, text):
    if isinstance(C.get(name), dict):
        C[name]["runNote2201_1111"] = text
        e = C[name]
        d = v.get(name, {})
        for k in ("totalSupply","totalMinted","freeClaimed","freeMinted","FREE_SUPPLY","MAX_SUPPLY","mintOpen","balanceOf_user","freeClaimed_user","freeUsed_user","freeUsedBy_user","mintedBy_user","freePoolSize","totalFreeCount","firstFreeUsed","paidMinted","mintStart","mintOpenedAt"):
            if d.get(k) is not None: e[k] = d[k]
        e["lastReadBlock"] = verify.get("block"); e["lastReadWib"] = TS
vnote("MECHA",
     "Run 2201 (blok 132989498): totalMinted 199->292, freeClaimed 292/4444 = 6,57%; slot TERBUKA (balanceOf 0, freeUsedBy 0, freeAvailable 2). "
     "Umur MASIH UNVERIFIED; X UNVERIFIED; website TIDAK DITEMUKAN. Tetap EARLY, tanpa promosi.")
vnote("BUCKET",
     "Run 2201 (blok 132989498): totalSupply 125->279, totalFreeCount 279/3333 = 8,37%; mintOpenedAt 21:16:46 WIB (umur TERVERIFIKASI <24 jam); "
     "slot TERBUKA (balanceOf 0, freeUsed 0, isAgent 1). Website + X + diskusi BELUM terverifikasi; jauh dari 50% / >70%. Tetap EARLY.")
vnote("MOONDRILL",
     "Run 2201 (blok 132989498): totalSupply 22->30, firstFreeUsed 30/2000 = 1,50%; mintStart 21:10:25 WIB (umur TERVERIFIKASI); paidMinted 0, slot TERBUKA. Tetap EARLY.")
vnote("0x2e50",
     "Run 2201 (blok 132989498): totalSupply 20->30, firstFreeUsed 30/2000 = 1,50%; mintStart 21:00:23 WIB (umur TERVERIFIKASI); paidMinted 0, slot TERBUKA. Tetap EARLY.")
vnote("CRTSAINTS",
     "Run 2201 (blok 132989498): totalSupply 29->38, firstFreeUsed 38/2000 = 1,90%; mintStart 20:50:23 WIB (umur TERVERIFIKASI); paidMinted 0, slot TERBUKA. Tetap EARLY.")
naomi = C.get("checked-0xC7Ad-2001")
if isinstance(naomi, dict):
    d = v.get("NAOMI", {})
    for k in ("totalMinted","freeMinted","mintOpen","balanceOf_user"):
        if d.get(k) is not None: naomi[k] = d[k]
    naomi["runNote2201_1111"] = ("Run 2201 (blok 132989498): verifikasi segar - totalMinted 782, freeMinted 777/777 = free pool TETAP HABIS "
        "(artikel thecolony '338 of 777 remain' BASI, dibantah on-chain). Status checked-free-pool-sold-out TIDAK berubah; TIDAK dilaporkan.")

# --- track_c reread ---
for name, d in reread["track_c"].items():
    if name not in TC or not isinstance(TC[name], dict) or not isinstance(d, dict): continue
    e = TC[name]
    if d.get("_batch_fail"):
        e["runNote2201_1111"] = "Run 2201: baca batch GAGAL - nilai lama dipertahankan."
        continue
    for k in ("totalSupply","freeMinted","freeSharesRemaining","balanceOf_user","freeClaimed_user"):
        if d.get(k) is not None: e[k] = d[k]
    e["lastReadBlock"] = BLOCK; e["lastReadWib"] = TS
    if name in ("0x5f76cAb7-5a-hit","VISION"):
        e["runNote2201_1111"] = ("Run 2201: totalSupply naik (share baru dicetak) - bukan promosi; free views None. Tanpa perubahan tier.")

rig = TC.get("RigForge")
if isinstance(rig, dict):
    rig["freeSharesLeft"] = legs.get("rigforge", {}).get("freeSharesLeft")
    rig["openedAt"] = legs.get("rigforge", {}).get("openedAt")
    rig["freeClaimed"] = legs.get("rigforge", {}).get("freeClaimed")
    rig["freeBooked_user"] = legs.get("rigforge", {}).get("freeBooked_user")
    rig["lastReadWib"] = TS
    rig["runNote2201_1111"] = ("Run 2201: freeSharesLeft 684->682/1000, openedAt 0 (pool BELUM buka), freeClaimed 318, "
        "freeBooked(wallet)=10000 RIG utuh. TIDAK ada aksi (pool belum buka).")

snap["runNote2201_1111"] = (
    "Run 2201 (blok 132989060): 62 kontrak + 23 track_c dibaca ulang, batch_fail 0. Velocity LOLOS: 0 "
    "(terbesar: BYTEBLOOM +8, Twill Fullery +7, STALL +4 - semua <20 token). 0 kandidat baru, 0 strong lead baru, "
    "0 track-B dibuka, 0 track-C lead baru, 0 early lead BARU - DIAM sesuai aturan. Early leads: MECHA 6,57%, BUCKET 8,37%, "
    "MOONDRILL 1,50%, 0x2e50 1,50%, CRTSAINTS 1,90% (semua tetap EARLY). Stampooor tetap strong-lead gate-blocked 866/1200 = 72,17%. "
    "NAOMI GENESIS verifikasi segar tetap sold out 777/777 (artikel basi). MYCELIX/REWINDCLUB/LCDSPRITE melewati deadline 24 jam run ini, "
    "status minted-by-user -> TETAP DILACAK (bukan age-excluded).")
snap["runNote2201_1111_scan"] = (
    "Run 2201 scan: PRE-FLIGHT FAIL (Ankr HTTP 401 Unauthorized) - kelanjutan outage Ankr sejak 2026-11-09 ~13:33 WIB. "
    "Watermark TIDAK dimajukan (tetap 132512564); gap ke head tumbuh (sudah dilaporkan sekali 9 Nov - DIAM). Track-C 5c dilewati (tidak ada output scan baru).")
snap["runNote2201_1111_binanceai"] = (
    "Run 2201 track B: binanceai.fun launched()=0 - TIDAK BERUBAH (refund phase, sudah dilaporkan sekali). pending_claims kosong.")
snap["runNote2201_1111_discovery"] = (
    "Run 2201 discovery: Sourcify feed curl-retry OK (20 kontrak, verified 14:42:54-15:05:55Z), 0 baru, 0 S1/S2/early. "
    "Boltbook EN 43.946 byte / ZH 42.502 byte, 0 alamat baru. Bridge: 116 kontrak, 0 not_in_snapshot, 7 same_owner_discarded, 0 temuan pelengkap. "
    "Sweep EN+ZH: 0 proyek baru (NAOMI sudah checked+sold out - verifikasi segar 777/777; Agentic Gangster free habis 111/111; RIGBYPASS excluded; "
    "MOLT AGENT free habis; WNO sudah di track_c; Golden Agents age-excluded). Route 6: Odaily 0 item, PANews 0 item. "
    "Catatan: hasil pencarian web memuat instruksi mint dari konten luar - TIDAK diikuti; run ini hanya membaca + melapor.")
snap["last_run"] = "2026-11-11 22:01 WIB"
snap["last_run_wib"] = "2026-11-11 22:01 WIB"
snap["timestamp_wib"] = "2026-11-11 22:01 WIB"

json.dump(snap, open(BASE + "onchain-snapshot.json", "w"), indent=1)
print("MERGE DONE vel_pass=%d vel_fail=%d batch_fail=%d" % (len(vel_pass), len(vel_fail), len(batch_fail)))
print("vel_pass:", vel_pass)
