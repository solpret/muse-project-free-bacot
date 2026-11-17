#!/usr/bin/env python3
"""Finalize run 1301 (fresh, from THIS run's data - NOT the 1231 copy):
update snapshot readings, velocity notes, age exclusions (Smeltbots,
Tumblebots), track_c notes, run notes. Reloads snapshot at write time to
avoid clobbering concurrent backfill writes; atomic write (tmp + replace)."""
import json, os
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
REREAD_BLOCK = 132153171
RUN = "2026-11-07 run 1301"

re = json.load(open(f"{BASE}/run-2026-11-07-1301-reread.json"))
vel = json.load(open(f"{BASE}/run-2026-11-07-1301-velocity.json"))
age = json.load(open(f"{BASE}/run-2026-11-07-1301-age-sweep.json"))
vel_rows = {r["name"]: r for r in vel["rows"]}

def apply(snap):
    updated = 0
    none_free = 0
    for name, d in re["reread"].items():
        c = snap["contracts"].get(name)
        if c is None:
            continue
        for k in ("totalSupply", "totalMinted", "freeClaimed", "freeMinted",
                  "FREE_SUPPLY", "MAX_SUPPLY", "mintOpen"):
            if d.get(k) is not None:
                c[k] = d[k]
        if d.get("balanceOf_user") is not None:
            c["balanceOf_user"] = d["balanceOf_user"]
        if d.get("freeClaimed") is None and d.get("freeMinted") is None:
            none_free += 1
        c["lastReadBlock"] = REREAD_BLOCK
        c["lastReadWib"] = RUN
        updated += 1
    for name, d in re.get("track_c", {}).items():
        tc = snap.get("track_c", {}).get(name)
        if isinstance(tc, dict):
            if d.get("totalSupply") is not None:
                tc["totalSupply"] = d["totalSupply"]
            if d.get("freeMinted") is not None:
                tc["freeMinted"] = d["freeMinted"]
            if d.get("freeSharesRemaining") is not None:
                tc["freeSharesRemaining"] = d["freeSharesRemaining"]
            tc["lastReadBlock"] = REREAD_BLOCK
            tc["lastReadWib"] = RUN
    # velocity notes on the two passes (both discarded -> no promotion)
    cg = snap["contracts"].get("Conciergo")
    if cg is not None:
        cg["velocityNote1301"] = ("Run 1301 (blok 132153171): +39 token, rate 1.1431/mnt, "
            "ratio 15.32x -> velocity LOLOS, TAPI TIDAK promosi: free% 5.55 (jauh di bawah "
            "25% strong leg) + status watchlist-only-same-owner-discarded-2026-11-03.")
    dr = snap["contracts"].get("Dronegent")
    if dr is not None:
        dr["velocityNote1301"] = ("Run 1301 (blok 132153171): +36 token, rate 1.0552/mnt, "
            "ratio 9.43x -> velocity LOLOS, TAPI TIDAK promosi: free% 41.44 TAPI status "
            "promotion-discarded-same-owner-2026-11-03 + umur first mint 2026-11-03 03:17 WIB "
            "(>48 jam) -> bukan kandidat/strong lead.")
    hive = snap["contracts"].get("HIVE Agents")
    if hive is not None:
        hv = vel_rows.get("HIVE Agents", {})
        hive["runNote1301"] = (f"Run 1301 (blok {REREAD_BLOCK}): totalSupply "
            f"{hv.get('curSupply')}, minted {hv.get('mintedInInterval')} interval; velocity "
            f"{'LOLOS' if hv.get('velocityPasses') else 'GAGAL'}; "
            f"balanceOf(user)={hv.get('balanceOf_user')}; minted-by-user, bukan kandidat.")
    # age exclusions
    removed = []
    for cand in age["candidates"]:
        name = cand["name"]
        c = snap["contracts"].get(name)
        if c is None:
            print("SKIP (not in contracts):", name)
            continue
        ex = dict(c)
        ex["status"] = "excluded-age-over-48h-2026-11-07"
        ex["status_before"] = c.get("status")
        ex["firstMintWib"] = cand["firstMintWib"]
        ex["ageHoursAtVerify"] = cand["ageHours"]
        ex["totalSupply_at_removal"] = cand["curSupply"]
        ex["ageExclusionNote"] = (f"DIHAPUS dari watchlist aktif run 1301: first mint "
            f"terverifikasi {cand['firstMintWib']} (blok {c.get('firstMintBlock')}) -> umur "
            f"~{cand['ageHours']} jam >48 jam; totalSupply segar {cand['curSupply']}/"
            f"{cand['maxSupply']}, belum sold out; free views gagal dibaca run ini (degradasi "
            f"RPC, nilai snapshot dipertahankan); balanceOf(user)=0.")
        ex["lastReadBlock"] = REREAD_BLOCK
        ex["lastReadWib"] = RUN
        snap.setdefault("excluded", {})[name] = ex
        del snap["contracts"][name]
        removed.append(name)
    print("REMOVED:", len(removed), removed)
    # track_c JAGT / MoonAgent: totalMints not refreshable this run
    for key in ("JupiterAgent-JAGT", "MoonAgent-MOAGT"):
        tc = snap.get("track_c", {}).get(key)
        if isinstance(tc, dict):
            tc["runNote1301"] = ("Run 1301: totalMints TIDAK tersegarkan (reread TC "
                "mengembalikan totalSupply token 1e27 + free views null, degradasi RPC); "
                "nilai lama dipertahankan (JAGT 114/700, MoonAgent 153); freeLeft(user)=1, "
                "quote(user,1)=0 (nilai lama); gate-blocked TETAP -> TIDAK dilaporkan ulang.")
    # run notes
    snap["last_run"] = "2026-11-07-1301"
    snap["last_run_wib"] = "2026-11-07 13:01 WIB (dieksekusi ~13:18-13:50 WIB)"
    snap["timestamp_wib"] = "2026-11-07 13:01 WIB"
    snap["runNote1301_1107"] = (
        "Run 1301: 0 kandidat baru, 0 strong lead baru/promosi, 0 early lead baru dari kaki "
        "job ini, 0 track-C lead/kandidat baru, 0 pending claim baru/dibuka. "
        "Preflight PASS 13,3 dtk (head 132151582; ankr eth_blockNumber mengembalikan "
        "non-string, fallback fast_rpc race). "
        "Reread 452 kontrak + 60 track_c, blok 132153171 (resume pasca-timeout 900 dtk pada "
        "reread pertama: 375/454 selesai sebelum timeout; resume +77 kontrak + 60 track_c "
        "dalam 198,6 dtk); 5 kontrak tanpa field address di snapshot (Mummyhive, "
        "LuckyBox-d08e, SnailMail, Jolly, AgentGlyph) TIDAK terbaca - nilai lama "
        "dipertahankan; free views (freeClaimed/freeMinted) mayoritas None (degradasi "
        "eth_call, sama seperti run 1131/1201/1231) - nilai snapshot dipertahankan, BUKAN nol. "
        "Velocity 2 pass: Conciergo +39 ratio 15,32 (free% 5,55 + same-owner-discarded) dan "
        "Dronegent +36 ratio 9,43 (free% 41,44 TAPI promotion-discarded-same-owner + umur "
        ">48 jam) -> keduanya BUKAN kandidat/strong lead, hanya catatan run log. "
        "Sold out 35 (sama seperti run 1231, 0 baru); near-sellout Dumpster Royalty (tetap); "
        "slot changes 0. "
        "Scan rute 4 PARTIAL: window 132150664-132151663 (1000 blok, cap), hanya 200 blok "
        "ter-cover (chunk 132150664-132150863) lalu ERROR Transfer chunk 132150864-132150913 "
        "'Remote end closed connection without response' -> loop berhenti; chunk "
        "TransferSingle 132150814-132150863 juga error (tapi lanjut). 45 NFT + 103 ERC-20 "
        "mint di 200 blok; 0 first-seen sejati (semua 45 sudah di seen file). Gap "
        "132148738-132150663 + 132150864-132151663 belum ter-cover main scan, milik backfill "
        "(backfill sudah di 132150401-132152930 saat run ini). Watermark TIDAK dimajukan "
        "(tetap milik backfill). "
        "Sourcify feed 20 kontrak (verifiedAt 05:01-06:14 UTC): 0 shape hit; 5 ABI gagal "
        "fetch (timeout, termasuk KALOS + JAGT yang sudah dikenal); 0xf100c608 = Pathwyrm, "
        "sudah EARLY lead run 1201 (bukan baru); 0x0343B150 = Agent Souls, S1 tapi "
        "same-owner-discarded run 1201 (log only). "
        "5c: 15 ERC-20 mint_count>=10 di window parsial, 0 baru (semua sudah di "
        "track-c-scan-checked.json), 0 shape hit. "
        "Boltbook EN+ZH + author pages + sweep rute 3/5b + komplemen rute 6 (subagent "
        "read-only): 22 proyek Boltbook dicek parent - semuanya sudah dikenal/ditriase: "
        "9 sudah di snapshot (ONI-d576, Mossminds, Abyssagent, AgentVOLT, HUNT PASS, "
        "Deltavane, BOT-UNIT, SYNAPSE-6886, WHALE-B); Orchidia paid-only (PRICE 0,00005 "
        "BNB); BAOracle + Tacotron + Lumenhold age-excluded; AGENT888 A/B bukan "
        "agent-shaped + paid-only; PLNK bukan sale-shape; EOND + HATCHIEggy bukan "
        "agent-shaped (triase Nov 6); Yokai bukan sale-shape; WHALE-A sold out; Subsonic "
        "Oct 26 (>48 jam); DragonEgg RISK FLAG (hidden approval, tanpa alamat - sudah "
        "diketahui run 0901); Oni#1 0x852f80B9 diverifikasi parent: ABI tanpa free view "
        "tanpa registry -> bukan agent-shaped, log only. "
        "Temuan backfill 132148738-132150400 (3 EARLY lead: N1007, V11, V12 - registry "
        "bytes, first mint 13:03-13:10 WIB, free path UNVERIFIED) DILAPORKAN OLEH JOB "
        "BACKFILL (preseden addendum run 0131: temuan backfill dilaporkan backfill, bukan "
        "run ini); ZeBroker + 0xfde98853 first-seen backfill bukan agent-shaped. "
        "Bridge: tidak berubah (115 entri, 7 same_owner_discarded, 33 tidak di snapshot, "
        "terakhir diubah 2026-11-06 02:48). "
        "Pending claims kosong; BINANCEAI GAGAL dibaca run ini (semua endpoint RPC timeout, "
        "EXIT=124; nilai null BUKAN nol) - state run 1231 dipertahankan (launched=0, "
        "failed=1, isRefundPhase=1, totalShares=3110); Grove tidak terbaca (skrip sama "
        "mati timeout). "
        "JAGT/MoonAgent totalMints tidak tersegarkan run ini (lihat runNote1301 masing-"
        "masing); gate-blocked TETAP -> tidak dilaporkan ulang.")
    snap["runNote1301_1107_age_exclusions"] = (
        "Run 1301 AGE-EXCLUSIONS (2 item, dilaporkan sekali sebagai perubahan): Smeltbots "
        "(first mint terverifikasi 2026-11-05 13:10:38 WIB blok 131766451, tx "
        "0x8f6c28f72ecf23e4d831b29bf704dd7608273f0bda031bf8c21e32c59f7e8d19, 670/4000) "
        "dan Tumblebots (first mint terverifikasi 2026-11-05 13:10:49 WIB blok 131766475, tx "
        "0x50fb641bc171317dd5af2e879f32a170de25dc7526dfb70d8637c9993aefd40a, 738/4000) - "
        "keduanya umur ~48,6 jam >48 jam, belum sold out, status strong-lead-gate-blocked "
        "(bukan minted-by-user, bukan same-owner-discarded) -> DIHAPUS dari kontrak aktif, "
        "dipindah ke excluded (status excluded-age-over-48h-2026-11-07). "
        "DIPERTAHANKAN: semua minted-by-user (grandfathered), semua "
        "promotion-discarded-same-owner / watchlist-only-same-owner-discarded (penanda "
        "discard-suppression), semua sold-out, semua watchlist-only yang launch-nya "
        "UNVERIFIED (42 item >48 jam berdasar first-mint terverifikasi tapi berstatus "
        "keep - lihat age-sweep).")
    snap["runNote1301_binanceai"] = (
        "Run 1301: BINANCEAI GAGAL dibaca (semua endpoint RPC timeout; skrip mati "
        "timeout 120 dtk, EXIT=124; semua nilai null = GAGAL BACA, bukan nol). State run "
        "1231 dipertahankan: launched=0, failed=1, isRefundPhase=1, totalShares=3110, "
        "tokenClaimed(user)=0, tokenBalance(user)=0 - tetap refund/failed, pending_claims "
        "kosong, tidak dilaporkan ulang.")
    snap["last_run_note"] = snap["runNote1301_1107"]
    return updated, none_free, removed

# apply on fresh load to avoid clobbering concurrent backfill writes
snap = json.load(open(f"{BASE}/onchain-snapshot.json"))
updated, none_free, removed = apply(snap)
with open(f"{BASE}/onchain-snapshot.json.tmp", "w") as f:
    json.dump(snap, f, indent=1)
os.replace(f"{BASE}/onchain-snapshot.json.tmp", f"{BASE}/onchain-snapshot.json")
print(f"FINALIZE DONE updated={updated} none_free_views={none_free} "
      f"removed={len(removed)} contracts_now={len(snap['contracts'])} "
      f"excluded_now={len(snap.get('excluded', {}))}")
