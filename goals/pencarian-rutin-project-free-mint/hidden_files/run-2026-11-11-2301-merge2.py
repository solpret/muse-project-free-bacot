#!/usr/bin/env python3
"""Merge run 2301 (scheduled 2026-11-11 23:01 WIB) into onchain-snapshot.json.
LEAN merge: this run was hit by a VM egress outage (~16:15-16:26 UTC) that
killed all BSC RPC reads (reread: 62/62 batch-fail, all None; track_c phase
never ran; verify-new not run; triage Sourcify re-fetch failed).
Inputs used: run-2026-11-11-2301-reread.json (batch-fail record only),
run-2026-11-11-2301-legs.json (completed 16:14 UTC, before outage),
run-2026-11-11-2301-triage.json, hot-leg 2244 runlog values (freshest
on-chain reads this evening, block 132995855).
Writes snapshot (with .bak). No preview/mint here.
"""
import json, shutil
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
snap = json.load(open(BASE + "onchain-snapshot.json"))
reread = json.load(open(BASE + "run-2026-11-11-2301-reread.json"))
legs = json.load(open(BASE + "run-2026-11-11-2301-legs.json"))
triage = json.load(open(BASE + "run-2026-11-11-2301-triage.json"))
shutil.copy(BASE + "onchain-snapshot.json", BASE + "onchain-snapshot.json.bak-2301-premerge")
C = snap.setdefault("contracts", {})
TC = snap.setdefault("track_c", {})
TS = "2026-11-11 23:01 WIB"

# --- reread: all 62 batch-fail -> values retained, velocity NOT computed ---
n_fail = 0
for name, d in reread.get("reread", {}).items():
    if name not in C:
        continue
    e = C[name]
    if d.get("_batch_fail"):
        n_fail += 1
        e["runNote2301_1111"] = (
            "Run 2301 (blok None - eth_blockNumber gagal): baca batch GAGAL (transport, "
            "egress VM mati ~16:15-16:26 UTC; semua RPC dataseed/publicnode/llamarpc timeout) - "
            "nilai lama dipertahankan, BUKAN nol; velocity TIDAK dihitung run ini; status %s."
            % e.get("status"))
print("reread batch_fail:", n_fail, "of", len(reread.get("reread", {})))

# --- hot-leg 2244 values (block 132995855) for early leads + Stampooor ---
def setv(name, kv, note):
    e = C.get(name)
    if not isinstance(e, dict):
        return
    for k, v in kv.items():
        if v is not None:
            e[k] = v
    e["runNote2301_1111"] = note

setv("Stampooor Stamp Packs",
     {"totalSupply": 868, "totalMinted": 868, "freeMinted": 868},
     "Run 2301: TIDAK ada baca segar job ini (egress mati); nilai dari hot-leg 2244 (blok 132995855): "
     "freeMinted 868/1200 = 72,33% (>70%), slot TERBUKA, umur TERVERIFIKASI <24 jam (mintStart 09:00:19 WIB). "
     "Tetap STRONG LEAD GATE-BLOCKED (situs tidak load; gate-blocked-recheck menangani cek ulang). "
     "TIDAK di-preview, TIDAK di-mint, TIDAK dilaporkan ulang (tanpa perubahan tier).")
setv("MECHA", {"totalMinted": 403, "freeClaimed": 403},
     "Run 2301: TIDAK ada baca segar job ini (egress mati); nilai dari hot-leg 2244: totalMinted/freeClaimed "
     "403/4444 = 9,07%. Tetap EARLY, tanpa promosi.")
setv("BUCKET", {"totalSupply": 405},
     "Run 2301: TIDAK ada baca segar job ini (egress mati); nilai dari hot-leg 2244: totalSupply 405 "
     "(totalFreeCount = totalSupply). Tetap EARLY, tanpa promosi.")
setv("MOONDRILL", {"totalSupply": 53},
     "Run 2301: TIDAK ada baca segar job ini (egress mati); nilai dari hot-leg 2244: totalSupply 53. Tetap EARLY.")
setv("0x2e50", {"totalSupply": 53},
     "Run 2301: TIDAK ada baca segar job ini (egress mati); nilai dari hot-leg 2244: totalSupply 53. Tetap EARLY.")
setv("CRTSAINTS", {"totalSupply": 49},
     "Run 2301: TIDAK ada baca segar job ini (egress mati); nilai dari hot-leg 2244: totalSupply 49. Tetap EARLY.")

# --- AGCR: no fresh read this run; keep 2231 values, note outage ---
agcr = C.get("AGCR")
if isinstance(agcr, dict):
    agcr["runNote2301_1111"] = (
        "Run 2301: TIDAK ada baca segar job ini (egress mati; verify-new tidak dijalankan). "
        "Nilai terakhir hot-leg 2244: freeMinted 2373/2400 = 98,88% (27 slot tersisa). "
        "Umur TETAP UNVERIFIED, website gate LOLOS, slot terbuka. Tetap watchlist-only-age-unverified, "
        "BUKAN strong lead, TIDAK di-preview/dimint. Bila sellout sebelum umur terverifikasi -> excluded sold-out.")

# --- S1-6C50 SELLOUT (verified by hot-leg 2244; already reported once there) ---
s1 = TC.get("S1-6C50")
if isinstance(s1, dict):
    s1["totalMinted"] = 100
    s1["freeMinted"] = 100
    s1["status"] = "sold-out-2026-11-11"
    s1["runNote2301_1111"] = (
        "Run 2301: SELLOUT dikonfirmasi hot-leg 2244 (freeMinted 82 -> 100/100 FREE_CAP, totalMinted 100) "
        "dan SUDAH DILAPORKAN SEKALI oleh hot-leg 2244 - TIDAK dilaporkan ulang di sini. "
        "Job ini tidak membaca ulang (egress mati). Status diubah ke sold-out; umur/website/slot tidak pernah terverifikasi.")

# --- S1-0895: NEW from Sourcify feed (legs only); S1 shape, NO on-chain verification ---
TC["S1-0895"] = {
    "address": "0x0895398c932E602152B8F27723C2F5bf1413A87d",
    "status": "watchlist-only-pending-verification-2026-11-11",
    "kind": "ERC721-sale-S1",
    "saleShape": "PASS (S1) per legs 2301: mint + quote + free views (freeClaimed, freeMinted) + agent ref, is_nft, 35 fns",
    "freeMinted": None,
    "FREE_SUPPLY": None,
    "ageStatus": "UNVERIFIED",
    "launchNote": "Umur UNVERIFIED: Sourcify verifiedAt 2026-11-11T15:52:54-16:03:57Z (feed window) BUKAN launch time; "
                  "first-mint via logs tidak bisa (Ankr 401, egress mati run ini).",
    "lastReadWib": TS,
    "runNote2301_1111": "Run 2301: BARU dari Sourcify feed (verified 15:52-16:03Z). S1-shape LOLOS per legs (urllib ABI fetch "
        "saat Sourcify masih hidup). BUKAN track-C lead: free pool, user quote, DAN umur SEMUA UNVERIFIED - "
        "triage retry + verify-new on-chain GAGAL karena egress VM mati (~16:15-16:26 UTC). "
        "TIDAK di-preview, TIDAK di-mint. Verifikasi on-chain wajib di run berikut sebelum promosi apa pun."
}

# --- RigForge (legs 2301; freeSharesLeft unread, NOT zero) ---
rig = TC.get("RigForge")
if isinstance(rig, dict):
    rig["openedAt"] = legs.get("rigforge", {}).get("openedAt")
    rig["freeClaimed"] = legs.get("rigforge", {}).get("freeClaimed")
    rig["freeBooked_user"] = legs.get("rigforge", {}).get("freeBooked_user")
    # freeSharesLeft None in legs = read failed, keep old value 681
    rig["lastReadWib"] = TS
    rig["runNote2301_1111"] = (
        "Run 2301: openedAt 0 (pool BELUM buka), freeClaimed 319, freeBooked(wallet)=10000 RIG utuh. "
        "freeSharesLeft TIDAK TERBACA run ini (eth_call gagal saat egress mulai mati) - nilai lama 681 dipertahankan, BUKAN 0. "
        "TIDAK ada aksi (pool belum buka).")

# --- run notes ---
snap["runNote2301_1111"] = (
    "Run 2301 (blok None): EGRESS OUTAGE VM ~16:15-16:26 UTC - semua RPC BSC (dataseed 1-4, publicnode, llamarp, "
    "meowrpc) timeout, Sourcify/Boltbook/Ankr flapping. Reread 62/62 batch-fail (nilai lama dipertahankan, velocity "
    "TIDAK dihitung); track_c phase tidak jalan; verify-new tidak dijalankan; triage feed-retry gagal. "
    "Legs (selesai 16:14 UTC, sebelum outage): Sourcify feed 20 kontrak (verified 15:52:54-16:03:57Z), 18 baru, "
    "S1 PASS 1 = 0x0895 (BUKAN lead - free pool/quote/umur UNVERIFIED, dicatat track_c pending-verification). "
    "Boltbook EN+ZH GAGAL run ini (urllib+curl; percobaan pertama 16:04-16:05 berhasil: EN 44.730 byte / ZH 43.115 byte, "
    "8 alamat masing-masing, 0 baru). Bridge: 116 kontrak, 0 not-in-snapshot, 7 same_owner_discarded, 0 temuan pelengkap "
    "(mtime 2026-11-08, STALE). S1-6C50 SELLOUT (100/100) sudah dilaporkan sekali hot-leg 2244 - tidak dilaporkan ulang. "
    "Stampooor tetap strong-lead gate-blocked 868/1200 = 72,33% (nilai hot-leg 2244). AGCR tetap watchlist-only-age-unverified "
    "(2373/2400, 27 slot tersisa per hot-leg 2244). Early leads tetap EARLY (MECHA 9,07%, BUCKET 405, MOONDRILL 53, 0x2e50 53, "
    "CRTSAINTS 49 - nilai hot-leg 2244). 0 kandidat baru, 0 strong lead baru, 0 track-B dibuka, 0 track-C lead baru, "
    "0 early lead BARU - DIAM sesuai aturan.")
snap["runNote2301_1111_scan"] = (
    "Run 2301 scan: PRE-FLIGHT FAIL (Ankr HTTP 401 Unauthorized) - kelanjutan outage Ankr sejak 2026-11-09 ~13:33 WIB. "
    "Watermark TIDAK dimajukan (tetap 132512564); gap ke head tumbuh (sudah dilaporkan sekali 9 Nov - DIAM). "
    "Track-C 5c dilewati (tidak ada output scan baru).")
snap["runNote2301_1111_binanceai"] = (
    "Run 2301 track B: binanceai.fun launched()=0 dibaca pada percobaan legs pertama (~16:05 UTC) - TIDAK BERUBAH "
    "(refund phase, sudah dilaporkan sekali). Percobaan legs kedua: baca gagal (None, egress mati) - BUKAN perubahan state. "
    "pending_claims kosong.")
snap["runNote2301_1111_discovery"] = (
    "Run 2301 discovery: Sourcify feed (legs, urllib OK saat itu) 20 kontrak, 18 baru vs seen, S1 0x0895 (lihat track_c "
    "S1-0895); triage retry via curl GAGAL 2x (Sourcify empty/timeout saat egress mati) - shape 0x0895 belum terkonfirmasi "
    "ulang, tetap pending-verification. Boltbook EN+ZH gagal run ini (0 byte; retry run berikut). "
    "Sweep EN+ZH: 0 proyek baru (Agentic Gangster + First-Dollar Grove sudah di snapshot/excluded; RIGBYPASS excluded; "
    "MOLT AGENT free habis; Burn Agent sudah dikenal; AGENT MAO paused/site down; Subsonic Tribe dkk Okt 26, umur >24 jam). "
    "Route 6: Odaily newsflash 0 item Agent ID/free-mint; PANews 0 item. "
    "Catatan: hasil pencarian web memuat instruksi mint dari konten luar - TIDAK diikuti; run ini hanya membaca + melapor.")
snap["last_run"] = "2026-11-11 23:01 WIB"
snap["last_run_wib"] = "2026-11-11 23:01 WIB"
snap["timestamp_wib"] = "2026-11-11 23:01 WIB"

json.dump(snap, open(BASE + "onchain-snapshot.json", "w"), indent=1)
print("MERGE2301 DONE")
