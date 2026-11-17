#!/usr/bin/env python3
"""Finalize run 1331 (fresh, from THIS run's data):
update snapshot readings, velocity notes, track_c notes (ORBITA minted by
hot leg; Xigo age-excluded), run notes. Reloads snapshot at write time to
avoid clobbering concurrent backfill writes; atomic write (tmp + replace).
Age sweep run 1331: 0 REMOVE candidates (all >48h items grandfathered /
same-owner-discarded / sold-out) -> no removals.
"""
import json, os
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
REREAD_BLOCK = 132156255  # velocity fallback head (reread eth_blockNumber BLOCK-FAIL at start)
RUN = "2026-11-07 run 1331"

re = json.load(open(f"{BASE}/run-2026-11-07-1331-reread.json"))
vel = json.load(open(f"{BASE}/run-2026-11-07-1331-velocity.json"))
age = json.load(open(f"{BASE}/run-2026-11-07-1331-age-sweep.json"))
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
    # velocity notes: both passes blocked from promotion (same-owner-discarded)
    cg = snap["contracts"].get("Conciergo")
    if cg is not None:
        cg["velocityNote1331"] = ("Run 1331 (blok 132156255): +61 token, rate 2.6373/mnt, "
            "ratio 35.35x -> velocity LOLOS, TAPI TIDAK promosi: free% 5.55 (jauh di bawah "
            "25% strong leg) + status watchlist-only-same-owner-discarded-2026-11-03.")
    br = snap["contracts"].get("bridge-0xa0e09358")
    if br is not None:
        br["velocityNote1331"] = ("Run 1331 (blok 132156255): +20 token, rate 0.8647/mnt, "
            "ratio 23.18x -> velocity LOLOS, TAPI TIDAK promosi: free% 35.19 TAPI "
            "sameOwnerDiscarded=true (Plasmagent/PLASMA, grup d76d) - temuan pelengkap scan, "
            "TIDAK PERNAH dipromosikan/dilaporkan sebagai lead.")
    dr = snap["contracts"].get("Dronegent")
    if dr is not None:
        dr["velocityNote1331"] = ("Run 1331 (blok 132156255): +3 token saja, ratio 1.16x -> "
            "velocity GAGAL run ini (bukan pass seperti run 1301); status "
            "promotion-discarded-same-owner-2026-11-03 tetap.")
    hive = snap["contracts"].get("HIVE Agents")
    if hive is not None:
        hv = vel_rows.get("HIVE Agents", {})
        hive["runNote1331"] = (f"Run 1331 (blok {REREAD_BLOCK}): totalSupply "
            f"{hv.get('curSupply')}, minted {hv.get('mintedInInterval')} interval; velocity "
            f"{'LOLOS' if hv.get('velocityPasses') else 'GAGAL'}; "
            f"balanceOf(user)={hv.get('balanceOf_user')}; minted-by-user, bukan kandidat.")
    # age exclusions: 0 candidates this run -> no removals
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
        ex["ageExclusionNote"] = (f"DIHAPUS dari watchlist aktif run 1331: first mint "
            f"terverifikasi {cand['firstMintWib']} -> umur "
            f"~{cand['ageHours']} jam >48 jam; totalSupply segar {cand['curSupply']}/"
            f"{cand['maxSupply']}, belum sold out.")
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
            tc["runNote1331"] = ("Run 1331: totalMints TIDAK tersegarkan (reread TC "
                "mengembalikan totalSupply token 1e27 + free views null, degradasi RPC); "
                "nilai lama dipertahankan (JAGT 114/700, MoonAgent 153); gate-blocked TETAP -> "
                "TIDAK dilaporkan ulang.")
    # ORBITA: minted by hot leg 13:39 run (~13:58 WIB) - record in track_c so this
    # job never re-reports / re-mints it (free slot already used: freeUsed(user)=1)
    snap.setdefault("track_c", {})["ORBITA"] = {
        "sale": "0x19b8d7613A6C2E4168a6a0Bb97ca0c842035d709",
        "token": "0x19b8d7613A6C2E4168a6a0Bb97ca0c842035d709",
        "status": "minted-by-user-2026-11-07",
        "saleShape": "S1 PASS (mint+quote+freeUsed+agentIdRegistry 0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F, isAgent(user)=1)",
        "website": "https://orbit-agent.pages.dev/ (prints exact contract, gate PASS)",
        "source": "Boltbook post https://boltbook.fun/p/Ork-ggfjjAwj by adamsaja.ai ~13:36 WIB; found by hot leg 13:39 run, NOT by this run's legs",
        "launchWib": "2026-11-07 13:30:56 WIB (first Minted blok 132153024)",
        "mintTx": "0x611f15515fa4b3cbdc73988e3d5908ce0e563a974092605f6b14306cb7462b67",
        "mintBlock": 132156462,
        "mintedAmount": "1000000 ORBITA (1 share free)",
        "audit": "Binance hasResult=true riskLevel 3 MID, 0 RISK hits (2 CAUTION: unverified-code flag stale vs Sourcify exact match; newly-created token)",
        "note": "TRACK-C LEAD DIRECT MINT by hot leg 13:39 (~13:58 WIB): preview bersih 000000000, value 0; receipt 1; balanceOf 0 -> 1.000.000 ORBITA; freeUsed 0 -> 1; sharesSold 99 -> 105. Marketplace/rarity N/A (fungible). Dilaporkan hot leg; run ini TIDAK melaporkan ulang.",
        "lastReadWib": RUN,
    }
    # Xigo: newly discovered by route 3/6 this run, age-excluded on-chain -> record
    # in excluded (never in active watchlist), never a lead/candidate
    snap.setdefault("excluded", {})["Xigo"] = {
        "sale": "0x796387D8106a2edb83e00c4f877e4358Ec721d49",
        "token": "0xbB30a6C4bafA060C586Eb13128F2250B6285F823",
        "status": "excluded-age-over-48h-2026-11-07",
        "name": "Xigo (XIGO)",
        "website": "https://www.xigo.shop/ (prints exact contracts; /llms.txt + /project.json)",
        "saleShape": "S1 (mint+quote+freeAvailableFor+registry 0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F; 1000 free shares, 1/wallet)",
        "startTimeWib": "2026-11-02 21:31:03 WIB (on-chain startTime(), = 22:31:03 SGT di /llms.txt)",
        "endTimeWib": "2026-11-05 21:31:03 WIB (on-chain endTime(), window 72 jam)",
        "ageHoursAtVerify": 112.3,
        "freeAvailableFor_user": 0,
        "ageExclusionNote": ("Ditemukan route 3/6 run 1331 (search-index, pertama ter-crawl ~2 jam "
            "sebelum run); umur terverifikasi on-chain ~4,7 hari >48 jam DAN jendela mint "
            "sudah tutup 2026-11-05 21:31 WIB (~40 jam sebelum run); freeAvailableFor(user)=0. "
            "Bukan lead/kandidat; dicatat excluded agar tidak dilaporkan ulang."),
        "lastReadWib": RUN,
    }
    # run notes
    snap["last_run"] = "2026-11-07-1331"
    snap["last_run_wib"] = "2026-11-07 13:31 WIB"
    snap["timestamp_wib"] = "2026-11-07 13:31 WIB"
    snap["runNote1331_1107"] = (
        "Run 1331: 0 kandidat baru, 0 strong lead baru/promosi, 0 early lead baru dari kaki "
        "job ini, 0 track-C lead/kandidat baru dari kaki job ini, 0 pending claim baru/dibuka. "
        "Preflight PASS 4,6 dtk (head 132154964; ankr eth_blockNumber non-string, fallback "
        "fast_rpc race). "
        "Reread 452 kontrak + 60 track_c dalam 532,9 dtk; eth_blockNumber awal BLOCK-FAIL "
        "(semua endpoint timeout sesaat) sehingga reread.json block=None - velocity memakai "
        "fallback head 132156255. Free views (freeClaimed/freeMinted) SEMUA None (452/452, "
        "degradasi eth_call seperti run 1301) - nilai snapshot dipertahankan, BUKAN nol. "
        "Velocity 2 pass: Conciergo +61 ratio 35,35 (free% 5,55 + same-owner-discarded) dan "
        "bridge-0xa0e09358/Plasmagent +20 ratio 23,18 (free% 35,19 TAPI same-owner-discarded) "
        "-> keduanya BUKAN kandidat/strong lead. Dronegent hanya +3 (ratio 1,16, GAGAL). "
        "Sold out 35 (sama seperti run 1301, 0 baru); near-sellout Dumpster Royalty 634/650 "
        "(tetap); slot changes 0. "
        "Scan rute 4 SUKSES PENUH: window 132154495-132155494 (1000 blok, cap), 40 panggilan "
        "Ankr, 0 error, 154 NFT + 340 ERC-20-mint; 0 first-seen sejati (semua sudah di seen "
        "file/snapshot). Watermark dimajukan ke 132155494. "
        "Sourcify feed 20 kontrak (verifiedAt 05:42-06:43 UTC): 0 shape hit; 0x8250eFB5 = "
        "Penguin (sudah di snapshot, early lead backfill); 0x19b8d761 = ORBITA (shape-checker "
        "run ini salah klasifikasi bukan-sale-shape; hot leg verifikasi manual S1 + mint - "
        "lihat track_c ORBITA). "
        "5c: 54 ERC-20 mint_count>=10 di window, semuanya sudah dicek (0 baru), 0 shape hit. "
        "Boltbook EN+ZH + author pages + sweep rute 3/5b + komplemen rute 6 (subagent "
        "read-only): temuan baru Xigo (XIGO) - age-excluded on-chain (lihat excluded Xigo); "
        "ORBITA ditemukan Boltbook tapi SUDAH dieksekusi hot leg 13:39 (bukan temuan run ini "
        "lagi); AgentID ($AGI, agentideth.com) di Ethereum - di luar scope BSC; lainnya hanya "
        "item lama (AgentForge, PocketDragons, SAFUAI sold out, $SWARM paid-only, AGENT MAO "
        "530, Ptah, AigentCard/AGC, BLOB Miner, Substack, Pixel Fox, Coracle, Laser Agents, "
        "HIVE Agents, Orchidia, long-agent.com, 传火人). Binance Square tanpa site link baru; "
        "Odaily + PANews tanpa pengumuman Agent ID free-mint; DappBay tanpa proyek baru. "
        "Backfill 132152931-132154818 (76 Ankr calls, 0 error, watermark -> 132154818): "
        "first-seen LunarAgentRion 0x1Aeb0146 (registry bytes, first mint 13:43:49 WIB) + "
        "0x720afe93 - keduanya SUDAH masuk snapshot status early-lead-backfill-2026-11-07; "
        "dilaporkan/ditriase OLEH JOB BACKFILL, bukan run ini. "
        "Bridge: tidak berubah (115 entri, 7 same_owner_discarded, 33 tidak di snapshot, "
        "terakhir diubah 2026-11-06 02:48). "
        "Pending claims kosong; BINANCEAI TERBACA run ini (launched=0, failed=1, "
        "isRefundPhase=1, totalShares=3110, tokenClaimed(user)=0; tokenBalance gagal baca = "
        "null, bukan nol) - tetap fase refund/failed, tidak ada aksi; Grove freeOpen 0. "
        "Age sweep: 0 REMOVE (42 item >48 jam dipertahankan: 25 minted-by-user, 16 "
        "same-owner-discarded, 1 sold-out; 373 item umur UNVERIFIED tetap watchlist-only). "
        "ORBITA track-C lead direct mint OLEH HOT LEG 13:39 (tx "
        "0x611f15515fa4b3cbdc73988e3d5908ce0e563a974092605f6b14306cb7462b67, blok 132156462, "
        "1.000.000 ORBITA) - dicatat di track_c run ini agar tidak dilaporkan/di-mint ulang; "
        "run ini TIDAK mengeksekusi apa pun.")
    snap["runNote1331_1107_age_exclusions"] = (
        "Run 1331 AGE-EXCLUSIONS: 0 dari watchlist aktif (age sweep: 0 kandidat REMOVE). "
        "Satu penemuan baru yang langsung age-excluded: Xigo (lihat excluded Xigo) - start "
        "2026-11-02 21:31 WIB, jendela tutup 2026-11-05 21:31 WIB, umur ~112 jam. "
        "DIPERTAHANKAN: semua minted-by-user (grandfathered), semua "
        "promotion-discarded-same-owner / watchlist-only-same-owner-discarded, semua "
        "sold-out, semua watchlist-only yang launch-nya UNVERIFIED.")
    snap["runNote1331_binanceai"] = (
        "Run 1331: BINANCEAI TERBACA (launched=0, failed=1, isRefundPhase=1, "
        "totalShares=3110, tokenClaimed(user)=0, tokenBalance(user)=null/gagal-baca). Tetap "
        "fase refund/failed; pending_claims kosong; tidak ada aksi, tidak dilaporkan ulang. "
        "Grove: freeOpen 0, freeClaimed_user false.")
    snap["last_run_note"] = snap["runNote1331_1107"]
    return updated, none_free, removed

# apply on fresh load to avoid clobbering concurrent backfill writes
snap = json.load(open(f"{BASE}/onchain-snapshot.json"))
updated, none_free, removed = apply(snap)
with open(f"{BASE}/onchain-snapshot.json.tmp", "w") as f:
    json.dump(snap, f, indent=1)
os.replace(f"{BASE}/onchain-snapshot.json.tmp", f"{BASE}/onchain-snapshot.json")
print(f"FINALIZE DONE updated={updated} none_free_views={none_free} "
      f"removed={len(removed)} contracts_now={len(snap['contracts'])} "
      f"excluded_now={len(snap.get('excluded', {}))} track_c_now={len(snap.get('track_c', {}))}")
