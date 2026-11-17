#!/usr/bin/env python3
"""Finalize run 1431: apply reread/velocity, age-exclude Agent Coffee + Driftnauts
(verified first mint >48h, not sold out), record PIXEL PETS + Skynet as
age-excluded discovery items, run notes. Reloads snapshot at write time; atomic write."""
import json, os
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
REREAD_BLOCK = 132165319
RUN = "2026-11-07 run 1431"

re = json.load(open(f"{BASE}/run-2026-11-07-1431-reread.json"))
vel = json.load(open(f"{BASE}/run-2026-11-07-1431-velocity.json"))
vel_rows = {r["name"]: r for r in vel["rows"]}

snap = json.load(open(f"{BASE}/onchain-snapshot.json"))
updated = 0; none_free = 0
for name, d in re["reread"].items():
    c = snap["contracts"].get(name)
    if c is None: continue
    for k in ("totalSupply", "totalMinted", "freeClaimed", "freeMinted",
              "FREE_SUPPLY", "MAX_SUPPLY", "mintOpen"):
        if d.get(k) is not None: c[k] = d[k]
    if d.get("balanceOf_user") is not None: c["balanceOf_user"] = d["balanceOf_user"]
    if d.get("freeClaimed") is None and d.get("freeMinted") is None: none_free += 1
    c["lastReadBlock"] = REREAD_BLOCK
    c["lastReadWib"] = RUN
    updated += 1
for name, d in re.get("track_c", {}).items():
    tc = snap.get("track_c", {}).get(name)
    if isinstance(tc, dict):
        if d.get("totalSupply") is not None: tc["totalSupply"] = d["totalSupply"]
        if d.get("freeMinted") is not None: tc["freeMinted"] = d["freeMinted"]
        if d.get("freeSharesRemaining") is not None: tc["freeSharesRemaining"] = d["freeSharesRemaining"]
        tc["lastReadBlock"] = REREAD_BLOCK
        tc["lastReadWib"] = RUN

# velocity notes
alc = snap["contracts"].get("Alchemister-0xCafEEDDF")
if alc is not None:
    alc["velocityNote1431"] = ("Run 1431 (blok 132165319): 1863->2342 (+479, 12.62/mnt, ratio 3.98) -> velocity LOLOS, "
        "TAPI TIDAK promosi: free% UNVERIFIED (tidak ada free view segar maupun snapshot) + launch time di snapshot "
        "09:49:19 WIB 2026-11-07 tapi free-quota leg tidak terverifikasi; status early-lead-backfill (sudah dilaporkan "
        "sebagai EARLY, duplicate Alchemister 0x69037Db8). Bukan strong lead/kandidat.")
cg = snap["contracts"].get("Conciergo")
if cg is not None:
    cg["velocityNote1431"] = ("Run 1431 (blok 132165319): 370->398 (+28, 0.74/mnt, ratio 9.89) -> velocity LOLOS, "
        "TAPI TIDAK promosi: free% 5.55 (jauh di bawah 25% strong leg) + status watchlist-only-same-owner-discarded-2026-11-03.")
dr = snap["contracts"].get("Dronegent")
if dr is not None:
    dr["velocityNote1431"] = ("Run 1431 (blok 132165319): 5124->5145 (+21, 0.55/mnt, ratio 4.94, free% 41.44) -> velocity LOLOS, "
        "TAPI TIDAK promosi: status promotion-discarded-same-owner-2026-11-03 (TIDAK PERNAH dipromosikan) + umur "
        "terverifikasi 2026-11-03 03:17 WIB (~111 jam >48 jam, age-excluded).")
hive = snap["contracts"].get("HIVE Agents")
if hive is not None:
    hive["runNote1431"] = (f"Run 1431 (blok {REREAD_BLOCK}): totalSupply 1255 flat vs run 1401 (1255) -> velocity GAGAL; "
        "balanceOf(user)=1; free views None (degradasi eth_call, nilai snapshot dipertahankan); minted-by-user, bukan kandidat.")

# Age exclusions from active watchlist (verified first mint >48h, not sold out)
for name, addr, first_block, first_wib, age_h, ts, ms, old_status in [
    ("Agent Coffee", "0x53A3D78FF23d9c9cb14Ae8B2fd168A44391b2010", 131779892, "2026-11-05 14:51:30", 48.5, 698, None, "early-lead-reported-2026-11-05"),
    ("Driftnauts", "0x6a926234D3767F2EEb3DB12c1B4C9e2912C5589b", 131779452, "2026-11-05 14:48:12", 48.6, 860, None, "strong-lead-gate-blocked-2026-11-06"),
]:
    snap["contracts"].pop(name, None)
    snap.setdefault("excluded", {})[name] = {
        "address": addr, "track": "A", "status": "excluded-age-over-48h-2026-11-07",
        "firstMintBlock": first_block, "firstMintWib": first_wib, "ageHoursAtVerify": age_h,
        "totalSupply_at_removal": ts, "totalMinted_at_removal": ms,
        "note": (f"Age-excluded run 1431: first mint terverifikasi INDEPENDEN run ini (Ankr address-filtered getLogs + "
                 f"fast_rpc block timestamp, blok {first_block}, {first_wib} WIB, tx tercatat di run-2026-11-07-1431-ageverify.json) "
                 f"-> umur ~{age_h} jam >48 jam; totalSupply {ts}, belum sold out; status lama {old_status}. "
                 f"Perubahan ini DILAPORKAN SEKALI ke chat utama (aturan: perubahan lead dilaporkan sekali)."),
        "lastReadBlock": REREAD_BLOCK, "lastReadWib": RUN,
    }
print("EXCLUDED-REMOVED from watchlist: Agent Coffee, Driftnauts")

# Discovery items age-excluded (never in snapshot, never reported as leads)
for name, addr, first_block, first_wib, age_h, ts, extra in [
    ("PIXEL PETS", "0x85188BC437eCB8677b072529Fc80AC602A7a1465", 129828759, "2026-10-26 10:51:59", 292.4, 3944,
     "freeMinted 3748, MAX_SUPPLY 5000, mintOpen 0 (tutup); sumber @congge918 2026-10-26 11:57 UTC, window gratis s.d. ~31 Okt."),
    ("Skynet", "0x4364991B28184727CAce1ac659e53cc497a940F7", 129835573, "2026-10-26 11:43:06", 291.5, None,
     "token fungible claimFree (track-B style), totalSupply 1.482.016 SKYNET, MAX 21.000.000; balanceOf(user)=0; sumber @congge918 2026-10-26 11:57 UTC, window gratis s.d. ~28 Okt."),
]:
    snap.setdefault("excluded", {})[name] = {
        "address": addr, "track": "A", "status": "excluded-age-over-48h-2026-11-07",
        "firstMintBlock": first_block, "firstMintWib": first_wib, "ageHoursAtVerify": age_h,
        "totalSupply_at_removal": ts, "totalMinted_at_removal": None,
        "note": (f"Age-excluded run 1431 (temuan discovery legs 2/3, BARU di catatan run ini): first mint terverifikasi "
                 f"on-chain run ini (Ankr address-filtered getLogs + fast_rpc timestamp, blok {first_block}) -> umur ~{age_h} jam "
                 f">48 jam. {extra} Tidak pernah di snapshot / tidak pernah dilaporkan sebagai lead/kandidat; dicatat di excluded "
                 f"agar tidak dilaporkan/ditriase ulang."),
        "lastReadBlock": REREAD_BLOCK, "lastReadWib": RUN,
    }
print("EXCLUDED-ADDED (discovery, never reported): PIXEL PETS, Skynet")

snap["runNote1431_1107"] = (
    "Run 1431: 0 kandidat baru, 0 strong lead baru/promosi, 0 early lead baru dari kaki job ini, "
    "0 track-C lead/kandidat baru dari kaki job ini, 0 pending claim baru/dibuka. "
    "2 PERUBAHAN dilaporkan sekali (age-exclusion lead yang sudah dilaporkan): Agent Coffee + Driftnauts (lihat runNote1431_age_exclusions). "
    "Preflight: percobaan 1 GAGAL (ankr eth_blockNumber -32601 tidak didukung + fast_rpc race semua endpoint timeout); "
    "retry +20 dtk GAGAL lagi (pola sama); preflight getLogs langsung PASS 4,3 dtk (head 132167467 via fast_rpc batch, 0 log/50 blok). "
    "Reread 455 kontrak + 62 track_c dalam 666,2 dtk (blok 132165319); free views (freeClaimed/freeMinted) SEMUA None (455/455, "
    "degradasi eth_call seperti run 1401) - nilai snapshot dipertahankan, BUKAN nol; balanceOf(user) None di 102 kontrak. "
    "Velocity 3 pass, 0 promosi: Alchemister-0xCafEEDDF +479 ratio 3,98 (free% UNVERIFIED, early-lead-backfill); Conciergo +28 ratio 9,89 "
    "(free% 5,55 + same-owner-discarded); Dronegent +21 ratio 4,94 (free% 41,44 TAPI promotion-discarded-same-owner + umur ~111 jam). "
    "Sold out 35 (identik run 1401, 0 baru); near-sellout Dumpster Royalty 635/650 (+1); slot changes 0 (terbaca). "
    "HIVE Agents totalSupply 1255 flat, balanceOf(user)=1, minted-by-user. "
    "Scan leg: window 132164586-132165585 (1000 blok, cap) chunk 20/20 selesai (0 error, 40 Ankr calls), enrichment STALL di 103/132 "
    "-> SCAN_EXIT=124 (timeout 780 dtk); 102 kontrak ter-enrich + 346 ERC-20-mint; 0 error chunk. Watermark TIDAK dimajukan (tetap 132158418). "
    "Gap tak ter-scan: 132158419-132164585 (6167 blok, cap-skip) + 29 kontrak window tidak ter-enrich (alamat tak bisa dipulihkan dari output parsial) "
    "-> ditutup backfill (DINYALAKAN LAGI user 2026-11-07 ~15:04 WIB, cron free-mint-backfill aktif lagi). "
    "Triage scan: 2 first-seen - Halcyon HLCN (registry False, not_verified, tanpa free shape) + AgentNova NOVA (registry-bytes hit, "
    "Sourcify not_verified; probe langsung: freeClaimed/freeMinted/freeLeft/FREE_SUPPLY + agentRegistry() SEMUA revert, totalSupply() revert, "
    "MAX_SUPPLY 6666, mintOpen 1 -> registry-only tanpa free view yang merespons, BUKAN early lead per preseden AGMIN/BENERGY); keduanya log only + seen file. "
    "Sourcify feed 20 kontrak: 0 shape hit baru. 5c: 57 ERC-20 >=10, 52 sudah dicek, 5 baru dicek (4 not_verified, 1 no-shape), 0 sale-shape hit. "
    "Discovery (subagent, legs 2/3/6): Boltbook EN+ZH + sweep EN+ZH + Square/Odaily/PANews/DappBay - semua item 'baru' ternyata sudah dikenal "
    "KECUALI PIXEL PETS + Skynet (keduanya dari @congge918 2026-10-26, keduanya age-excluded >290 jam, lihat excluded). "
    "Bridge: tidak berubah (115 entri, terakhir diubah 2026-11-06 02:48; 82 di snapshot, 7 same_owner_discarded, 0 promosi). "
    "Pending claims kosong; BINANCEAI TIDAK TERBACA run ini (semua view None, degradasi transport - status terakhir run 1401 dipertahankan: "
    "launched=0, failed=1, isRefundPhase=1, refund/failed, tidak ada aksi); Grove freeOpen 0, freeClaimed_user false. "
    "Age sweep: 2 REMOVE (Agent Coffee, Driftnauts - keduanya baru melewati 48 jam di antara run 1401 dan 1431); 43 dipertahankan "
    "(minted-by-user/same-owner-discarded/sold-out); 374 umur UNVERIFIED tetap watchlist-only. "
    "TIDAK ada eksekusi oleh run ini (tidak ada mint/preview/claim).")
snap["runNote1431_scan"] = (
    "Run 1431 SCAN: preflight getLogs PASS (head 132167467). Window 132164586-132165585 (1000 blok, cap) chunk 20/20 SELESAI "
    "(0 error, 40 Ankr calls; 96+ ERC721 / 4 ERC1155 / 346 ERC-20-mint). Enrichment STALL di 103/132 (dataseed timeout berulang saat "
    "name/symbol/Sourcify) -> timeout 780 dtk, SCAN_EXIT=124. 102 kontrak ter-enrich, 29 kontrak window tidak ter-enrich (alamat tidak "
    "terpulihkan dari output parsial). Watermark TIDAK dimajukan (132158418). Gap 132158419-132164585 (6167 blok) + window parsial "
    "ditutup backfill (aktif lagi 15:04 WIB).")
snap["runNote1431_age_exclusions"] = (
    "Run 1431 AGE-EXCLUSIONS (dilaporkan sekali ke chat utama): Agent Coffee 0x53A3... (first mint 2026-11-05 14:51:30 WIB, "
    "blok 131779892, umur 48,5 jam, 698/4444, early lead dilaporkan 2026-11-05) dan Driftnauts 0x6a92... (first mint 2026-11-05 "
    "14:48:12 WIB, blok 131779452, umur 48,6 jam, ~860/4000, strong lead gate-blocked dilaporkan 2026-11-06) - keduanya baru melewati "
    "48 jam di antara run 1401 (~47,2 jam) dan run 1431; keduanya belum sold out -> DIHAPUS dari watchlist aktif per aturan umur 48 jam. "
    "Discovery items PIXEL PETS + Skynet (umur ~292 jam) juga dicatat excluded, TIDAK dilaporkan sebagai lead (tidak pernah dilaporkan). "
    "DIPERTAHANKAN: semua minted-by-user (grandfathered), semua promotion-discarded-same-owner / watchlist-only-same-owner-discarded, "
    "semua sold-out, semua watchlist-only yang launch-nya UNVERIFIED.")
snap["runNote1431_binanceai"] = (
    "Run 1431: BINANCEAI TIDAK TERBACA (semua view None - degradasi transport race() semua endpoint timeout; BUKAN nol). "
    "Status terakhir run 1401 dipertahankan: launched=0, failed=1, isRefundPhase=1, totalShares=3110, tokenClaimed(user)=0, "
    "tokenBalance(user)=0 - tetap fase refund/failed; pending_claims kosong; tidak ada aksi. Grove: freeOpen 0, freeClaimed_user false.")
snap["last_run"] = "2026-11-07-1431"
snap["timestamp_wib"] = "2026-11-07 15:35 WIB"
snap["last_run_note"] = snap["runNote1431_1107"]
snap["last_run_wib"] = "2026-11-07 15:35 WIB"

with open(f"{BASE}/onchain-snapshot.json.tmp", "w") as f:
    json.dump(snap, f, indent=1)
os.replace(f"{BASE}/onchain-snapshot.json.tmp", f"{BASE}/onchain-snapshot.json")
print(f"FINALIZE DONE updated={updated} none_free_views={none_free} "
      f"contracts_now={len(snap['contracts'])} excluded_now={len(snap.get('excluded', {}))} "
      f"track_c_now={len(snap.get('track_c', {}))}")
