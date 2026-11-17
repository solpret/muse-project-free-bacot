#!/usr/bin/env python3
"""Merge run 2001 (scheduled 2026-11-11 20:01 WIB) into onchain-snapshot.json.
Inputs: run-2026-11-11-2001-reread.json (62 contracts + 23 track_c; head block
132973050), run-2026-11-11-2001-legs.json, run-2026-11-11-2001-triage.json.
Writes snapshot (with .bak). No age-exclusion this run (next deadlines 21:28+).
No new candidate / strong lead / early lead / track-B opening / track-C lead.
NAOMI GENESIS (sweep find) free pool SOLD OUT 777/777 -> checked only.
"""
import json, shutil
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
snap = json.load(open(BASE + "onchain-snapshot.json"))
reread = json.load(open(BASE + "run-2026-11-11-2001-reread.json"))
legs = json.load(open(BASE + "run-2026-11-11-2001-legs.json"))
triage = json.load(open(BASE + "run-2026-11-11-2001-triage.json"))
shutil.copy(BASE + "onchain-snapshot.json", BASE + "onchain-snapshot.json.bak-2001-premerge")
C = snap.setdefault("contracts", {})
TC = snap.setdefault("track_c", {})
BLOCK = reread.get("block")
TS = "2026-11-11 20:01 WIB"

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
        e["runNote2001_1111"] = ("Run 2001 (blok %s): baca batch GAGAL (transport) - nilai lama "
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
        C[name]["runNote2001_1111"] = text

# --- Stampooor: still strong lead, gate blocked, no tier change -> no re-report ---
st = C.get("Stampooor Stamp Packs")
if isinstance(st, dict):
    st["status"] = "strong-lead-gate-blocked-2026-11-11"
    note("Stampooor Stamp Packs",
     "Run 2001: freeMinted 851->852/1200 = 71,00% (>70%, tetap strong lead); umur TERVERIFIKASI <24 jam "
     "(mintStart 1794362419 = 11 Nov 09:00:19 WIB; deadline ~09:00 WIB 12 Nov); slot user TERBUKA (balanceOf 0, "
     "mintOpen 1). Velocity +1/30 mnt GAGAL - tidak relevan untuk strong-lead direct mint. GATE WEBSITE tetap "
     "GAGAL (sudah dilaporkan sekali run 1901; gate-blocked-recheck menangani cek ulang situs). TIDAK di-preview, "
     "TIDAK di-mint, TIDAK dilaporkan ulang (tidak ada perubahan tier).")

note("0x7Eb9", "Run 2001: totalSupply 933->942 (+9, <20) velocity GAGAL (rate 0,3000/mnt vs prev 0,6333 = 0,47x); "
     "balanceOf(user)=0. Tetap early-lead-reported; BUKAN promosi.")
note("Kitebots", "Run 2001: totalSupply 1229->1232 (+3, <20) velocity GAGAL. Free% UNVERIFIED, umur UNVERIFIED, "
     "X/website UNVERIFIED. Tetap watchlist-only-age-unverified; TIDAK di-preview/dimint.")
note("RIMEVAULT", "Run 2001: totalSupply 1040->1043 (+3) velocity GAGAL; balanceOf=1 (minted-by-user). Deadline umur ~21:28 WIB hari ini.")
note("MYCELIX", "Run 2001: totalSupply 616->618 (+2) velocity GAGAL; balanceOf(user)=1 (minted-by-user). Deadline umur ~21:47 WIB hari ini.")
note("SOLDERCATS", "Run 2001: totalSupply 541->541 (+0) velocity GAGAL; balanceOf(user)=1. Deadline umur ~21:35 WIB hari ini.")
note("LCDSPRITE", "Run 2001: totalSupply 581->581 (+0) velocity GAGAL; balanceOf(user)=1. Deadline umur ~21:52 WIB hari ini.")
note("REWINDCLUB", "Run 2001: totalSupply 561->561 (+0) velocity GAGAL; balanceOf(user)=1. Deadline umur ~21:49 WIB hari ini.")
note("RAMRAIDERS", "Run 2001: totalSupply 559->561 (+2) velocity GAGAL; balanceOf(user)=0. "
     "Tetap EARLY lead; TIDAK di-preview/dimint. Deadline umur konservatif ~00:30 WIB 12 Nov.")
note("HANAMI BLOOM", "Run 2001: totalSupply 109->109 (+0) velocity GAGAL; balanceOf(user)=0. "
     "Tetap EARLY lead; TIDAK di-preview/dimint. Deadline umur ~12:59 WIB 12 Nov.")
note("AgentPals", "Run 2001: totalSupply 300->300 (+0); free pool SOLD OUT 300/300; balanceOf(user)=1 (#268). "
     "Status minted-by-user-2026-11-11; TIDAK dilaporkan ulang. Keputusan gate metode (I) user ~19:36 WIB tetap berlaku "
     "(pantau 3 hari s.d. 14 Nov 2026; metadata worker saja SEMENTARA TIDAK cukup sebagai bukti website).")

# --- Track C reread: store fresh values, flag material changes ---
tc_changes = []
for name, d in reread["track_c"].items():
    if name not in TC or not isinstance(TC[name], dict) or not isinstance(d, dict): continue
    e = TC[name]
    if d.get("_batch_fail"): continue
    for k in ("totalSupply","freeMinted","freeSharesRemaining","balanceOf_user","freeClaimed_user"):
        if d.get(k) is not None and e.get(k) != d[k]:
            if k in ("freeMinted","freeSharesRemaining"):
                tc_changes.append((name, k, e.get(k), d[k]))
            e[k] = d[k]
    e["lastReadBlock"] = BLOCK; e["lastReadWib"] = TS

# --- RigForge re-check (legs) ---
rig = TC.get("RigForge")
if isinstance(rig, dict):
    rig["freeSharesLeft"] = legs.get("rigforge", {}).get("freeSharesLeft")
    rig["openedAt"] = legs.get("rigforge", {}).get("openedAt")
    rig["freeClaimed"] = legs.get("rigforge", {}).get("freeClaimed")
    rig["freeBooked_user"] = 10000
    rig["lastReadBlock"] = BLOCK; rig["lastReadWib"] = TS

# --- Triaged / checked (not leads, never reported as leads) ---
C["checked-0xC7Ad-2001"] = {
    "address": "0xC7Adf8f0b49a5C1840C31636A96c6D5ed077c7E9",
    "name": "NAOMI GENESIS",
    "status": "checked-free-pool-sold-out-2026-11-11",
    "totalMinted": 782,
    "freeMinted": 777,
    "FREE_SUPPLY": 777,
    "mintOpen": 1,
    "website": "https://naomigenesis.pages.dev",
    "note": ("Run 2001 sweep EN+ZH (thecolony.ai): NAOMI GENESIS, 7.777 NFT, first 777 free 1/wallet, site "
        "naomigenesis.pages.dev mencetak kontrak persis + renderer 0x3BD2DD3630aF9087386596910d817624F2132818. "
        "TAPI free pool SUDAH HABIS: freeMinted()=777/777, totalMinted()=782 (baca ulang konfirmasi), mintOpen 1, "
        "balanceOf(user)=0. Sourcify 404 (NOT verified) meski situs mengklaim exact match. Launch age TIDAK diverifikasi "
        "karena pool sudah habis sebelum laporan pertama - EXCLUDED sebagai sold out, dicatat checked saja, TIDAK dilaporkan."),
}
C["checked-0xD6c7-2001"] = {
    "address": "0xD6c7C47453aA42fc7e51f06Ff1f3f1529bfc5de0",
    "status": "checked-no-mints-yet-2026-11-11",
    "totalSupply": 0,
    "MAX_SUPPLY": 1806,
    "mintOpen": 1,
    "note": ("Run 2001 triase feed-new: Sourcify verified, 35 fns, early_shape (is_nft + mint fn) TAPI agent_ref FALSE, "
        "free_views [] (S1/S2 False). On-chain: totalSupply 0 (BELUM ada mint pertama), MAX_SUPPLY 1806, mintOpen 1, "
        "mintStart None. BUKAN early lead (first mints belum terverifikasi). Sourcify fetch ulang triase sempat "
        "IncompleteRead (transport) - status verifikasi dari legs. Dicatat checked; cek ulang run berikut bila mint dimulai."),
}
C["checked-0xBB25-2001"] = {
    "address": "0xBB25C5e6786E76718bdEdeF14C862ED1772Ac543",
    "status": "checked-no-mints-yet-2026-11-11",
    "totalSupply": 0,
    "MAX_SUPPLY": 5555,
    "mintOpen": 1,
    "mintStart": 1794402030,
    "mintStart_wib": "2026-11-11 20:00:30 WIB",
    "note": ("Run 2001 triase feed-retry (curl): Sourcify verified, 84 fns, freeLeft view, early_shape TAPI agent_ref "
        "FALSE (S1/S2 False). On-chain: totalSupply 0 (BELUM ada mint pertama), MAX_SUPPLY 5555, mintOpen 1, "
        "mintStart 1794402030 = 11 Nov 20:00:30 WIB (baru buka ~saat run). freeLeft() mengembalikan nilai sampah "
        "(kemungkinan butuh argumen) - BUKAN counter free terverifikasi. BUKAN early lead (first mints belum "
        "terverifikasi). Dicatat checked; cek ulang run berikut bila mint dimulai."),
}

snap["last_run"] = TS
snap["last_run_wib"] = TS
snap["runNote2001"] = (
    "Run 2001 (blok %s): DIAM - 0 kandidat baru, 0 strong lead baru, 0 early lead baru, 0 track-B dibuka, "
    "0 track-C lead baru, 0 age-exclusion. Stampooor tetap strong lead gate-blocked 852/1200 = 71,00%%, slot terbuka, "
    "TIDAK dilaporkan ulang (tanpa perubahan tier). Velocity: 0 lolos (0x7Eb9 +9 <20; Stampooor +1; Kitebots +3). "
    "Batch fail: Dragon Agent, BYTEBLOOM (nilai lama dipertahankan). Foundry Faces: supply tidak terbaca. "
    "Sourcify feed 20 kontrak (verified 12:43:06-13:03:26Z), 9 baru, 0 S1/S2; early_shape 2 (0xD6c7, 0xBB25) - keduanya "
    "totalSupply 0 (belum ada mint pertama) -> BUKAN early lead; 6 alamat feed sempat IncompleteRead, triase retry curl "
    "berhasil semua (0 S1/S2). Boltbook EN 45.079 byte / ZH 43.368 byte, 7 alamat, 0 baru. Bridge: 116 kontrak, mtime "
    "2026-11-08 18:21 WIB (STALE), 0 not_in_snapshot, 7 same_owner_discarded, 0 temuan pelengkap. Track B: binanceai.fun "
    "launched()=0 - TIDAK BERUBAH (refund phase). RigForge: freeSharesLeft 687/1000 (689 pukul 19:31), openedAt 0 "
    "(pool BELUM buka), freeClaimed 313, freeBooked(wallet) = 10000 RIG utuh. Scan (route 4): FAST-FAIL pre-flight Ankr "
    "HTTP 401 Unauthorized - outage berlanjut sejak ~13:33 WIB 2026-11-09 (kuota 0%% s.d. 1 Des 2026). Watermark TIDAK "
    "dimajukan (tetap 132512564); gap ke head tumbuh (sudah dilaporkan sekali 9 Nov - DIAM). Track-C 5c dilewati (tidak "
    "ada output scan baru). Sweep EN+ZH: NAOMI GENESIS (0xC7Ad...) ditemukan via thecolony.ai TAPI free pool SUDAH HABIS "
    "777/777 (totalMinted 782) -> checked saja, TIDAK dilaporkan; Agentic Gangster free habis 111/111 (dikonfirmasi ulang); "
    "RIGBYPASS excluded (pool habis); WNO/UFO/TINY AGENTS/NOVRA sudah dikenal, bukan baru. Route 6: Odaily newsflash 0 item "
    "Agent ID/free-mint (278.096 byte); PANews 0 item (124.194 byte). AGE: tidak ada exclusion run ini; deadline berjalan: "
    "RIMEVAULT ~21:28, SOLDERCATS ~21:35, MYCELIX ~21:47, REWINDCLUB ~21:49, LCDSPRITE ~21:52 (11 Nov); RAMRAIDERS "
    "konservatif ~00:30 WIB 12 Nov; HANAMI BLOOM ~12:59 WIB 12 Nov; Stampooor ~09:00 WIB 12 Nov." % BLOCK)
snap["runNote2001_scan"] = (
    "Run 2001 scan: PRE-FLIGHT FAIL (Ankr HTTP 401 Unauthorized) - kelanjutan outage Ankr sejak 2026-11-09 ~13:33 WIB. "
    "Watermark TETAP 132512564; gap ke head tumbuh (sudah dilaporkan sekali 9 Nov - DIAM).")
snap["timestamp_wib"] = TS

with open(BASE + "onchain-snapshot.json", "w") as f:
    json.dump(snap, f, indent=1)
print("MERGE DONE vel_pass=%s vel_fail=%s batch_fail=%s tc_changes=%s" % (
    vel_pass, len(vel_fail), batch_fail, tc_changes))
print("VEL_FAIL:", vel_fail)
print("TC_CHANGES:", tc_changes)
