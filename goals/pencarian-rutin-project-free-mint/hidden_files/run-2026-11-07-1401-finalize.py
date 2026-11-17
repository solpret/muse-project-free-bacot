#!/usr/bin/env python3
"""Finalize run 1401: apply reread/velocity, record PLNK gate-blocked in track_c,
age-exclude Agent Apes + AgentMiner (first-seen in seen file, never in snapshot),
run notes. Reloads snapshot at write time; atomic write."""
import json, os
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
REREAD_BLOCK = 132160258
RUN = "2026-11-07 run 1401"

re = json.load(open(f"{BASE}/run-2026-11-07-1401-reread.json"))
vel = json.load(open(f"{BASE}/run-2026-11-07-1401-velocity.json"))
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

cg = snap["contracts"].get("Conciergo")
if cg is not None:
    cg["velocityNote1401"] = ("Run 1401 (blok 132160258): +63 token, rate 2.0984/mnt, ratio 28.13x -> "
        "velocity LOLOS, TAPI TIDAK promosi: free% 5.55 (jauh di bawah 25% strong leg) + status "
        "watchlist-only-same-owner-discarded-2026-11-03 (sama seperti run 1331).")
hive = snap["contracts"].get("HIVE Agents")
if hive is not None:
    hv = vel_rows.get("HIVE Agents", {})
    hive["runNote1401"] = (f"Run 1401 (blok {REREAD_BLOCK}): semua view None (degradasi eth_call, "
        f"nilai snapshot dipertahankan); velocity {hv.get('velocityPasses')}; "
        f"balanceOf(user) tidak terbaca run ini; minted-by-user, bukan kandidat.")

# PLNK -> track_c as gate-blocked (already reported once by hot leg 09:54; no re-report)
snap.setdefault("track_c", {})["PLNK"] = {
    "sale": "0xec266bdd979b19d8a2f1266ef0610b4791dbd24b",
    "token": "0xec266bdd979b19d8a2f1266ef0610b4791dbd24b",
    "name": "PlonkraAgent",
    "symbol": "PLNK",
    "status": "gate-blocked-2026-11-07",
    "saleShape": "PASS (S1): mint(uint256) + quote(address,uint256) + freeUsed + AGENT_ID_REGISTRY()=0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F, Sourcify exact_match verifiedAt 2026-11-07T02:04:55Z",
    "sharesSold": 431, "MAX_SHARES": 1000, "FREE_PER_AGENT": 1,
    "TOKENS_PER_SHARE": 1000000000000000000000000,
    "PRICE_PER_SHARE": 1500000000000000, "AGENT_PRICE_PER_SHARE": 1000000000000000,
    "quote_user_1": {"freeShares": 1, "costBnb": 0},
    "freeUsed_user": 0, "mintedBy_user": 0, "isAgent_user": 1,
    "firstMintBlock": 132116977, "firstMintTx": "0xb025b51062f05ca2f8bf41797ff4a5c7181f292cc7d9f6de52b4a7ed02b82028",
    "firstMintWib": "2026-11-07 09:00:31",
    "ageHoursAtVerify": 6.1,
    "gateNote": ("GATE GAGAL (website wajib): dilaporkan sekali hot leg 09:54 WIB sebagai TRACK-C LEAD "
        "GATE-BLOCKED; metode (A)-(N) sudah dicoba (plonkraagent.vercel.app 404, .pages.dev unreachable, "
        ".deed.page 404; treasury sama dgn GLPX 0xf82048ff58ba63fc3904e1a3f54c0ca9e99bf8cc; name search tanpa situs). "
        "Run 1401 re-cek (G)/(M): search alamat+nama tanpa situs proyek baru (hanya AirdropBuzz Agent ID guide, "
        "FreeAgent support, PLKN Steemit, Medium roundup). TIDAK preview, TIDAK mint. Pool masih terbuka "
        "(431/1000, slot user masih 0) tapi gate tetap gagal -> tidak dilaporkan ulang."),
    "lastReadBlock": REREAD_BLOCK, "lastReadWib": RUN,
}

# Age exclusions: Agent Apes + AgentMiner (seen-file first-seen, never in snapshot, never reported as leads)
for name, addr, first_block, first_wib, age_h, ts, ms in [
    ("Agent Apes", "0xbf18B0CfDd9e4FD138a362A92F29674197Fdb886", 131372581, "2026-11-03 11:55:51", 99.5, 4416, None),
    ("AgentMiner", "0xCe67038f8703Dff3Aadaf77d41823b4b039C9446", 131657133, "2026-11-04 23:30:32", 63.8, 5780, 5795),
]:
    snap.setdefault("excluded", {})[name] = {
        "address": addr, "track": "A", "status": "excluded-age-over-48h-2026-11-07",
        "firstMintBlock": first_block, "firstMintWib": first_wib, "ageHoursAtVerify": age_h,
        "totalSupply_at_removal": ts, "totalMinted_at_removal": ms,
        "note": (f"Age-excluded run 1401: first mint terverifikasi blok {first_block} ({first_wib} WIB, "
                 f"eth_getBlockByNumber fast_rpc) -> umur ~{age_h} jam >48 jam; mintOpen 1, belum sold out. "
                 f"Kontrak sudah di seen file sejak window itu (bukan first-seen run ini) dan tidak pernah masuk "
                 f"snapshot / tidak pernah dilaporkan sebagai early lead. Free path UNVERIFIED (Agent Apes: registry-bytes "
                 f"hit + Sourcify verified + mint/mintOpen/mintedBy, TANPA free view/fungsi; AgentMiner: data sama). "
                 f"Dicatat di excluded agar tidak dilaporkan/ditriase ulang."),
        "lastReadBlock": REREAD_BLOCK, "lastReadWib": RUN,
    }
print("EXCLUDED-ADDED: Agent Apes, AgentMiner")

snap["runNote1401_1107"] = (
    "Run 1401: 0 kandidat baru, 0 strong lead baru/promosi, 0 early lead baru dari kaki job ini, "
    "0 track-C lead/kandidat baru dari kaki job ini, 0 pending claim baru/dibuka. "
    "Preflight: percobaan 1 GAGAL (ankr eth_blockNumber non-string + fast_rpc race semua endpoint timeout), "
    "retry 20 dtk kemudian PASS 5,0 dtk (head 132160077, 208 log/50 blok). "
    "Reread 454 kontrak + 61 track_c dalam 961,9 dtk (blok 132160258); free views (freeClaimed/freeMinted) "
    "SEMUA None (454/454, degradasi eth_call seperti run 1301/1331) - nilai snapshot dipertahankan, BUKAN nol. "
    "Velocity 1 pass: Conciergo +63 ratio 28,13 (free% 5,55 + same-owner-discarded) -> BUKAN kandidat/strong lead. "
    "Sold out 35 (sama seperti run 1331, 0 baru); near-sellout Dumpster Royalty 634/650 (tetap); slot changes 0. "
    "Scan leg GAGAL SEBAGIAN: window 132159154-132160153 (1000 blok, cap), hanya 4 chunk (200 blok, "
    "132159154-132159353) selesai, lalu ERROR 'Transfer chunk 132159354-132159403: Remote end closed connection' "
    "-> loop break; 49 NFT + 109 ERC-20-mint dari 200 blok; 0 first-seen sejati. Watermark TIDAK dimajukan "
    "(tetap 132158418). Gap tak ter-scan: 132158419-132159153 (735 blok, cap-skip) + 132159354-132160153+ "
    "(800+ blok, scan break). Backfill DIMATIKAN user 2026-11-07 ~14:26 WIB (cron free-mint-backfill disabled) "
    "-> gap ini TIDAK ditutup backfill; scan rutin + hot leg hanya menutup blok baru ke depan. "
    "Sourcify feed 20 kontrak: 0 shape hit baru. 5c: 17 ERC-20 >=10, 16 sudah dicek, 1 baru dicek "
    "(0xc8D4dDAd895629a04F55934db2bf4728F3078b54, not_verified), 0 sale-shape hit. "
    "Backfill window 132156774-132158418 (selesai sebelum dimatikan): 2 first-seen ditriase run ini - "
    "Future XPIN FT-XPIN (registry False, not_verified, tanpa free shape) + Build Energy BENERGY "
    "(registry-bytes hit, Sourcify verified, AGENT_ID_REGISTRY constant, TANPA free-mint/free view; mintLand berbayar) "
    "-> keduanya BUKAN early lead, log only; keduanya ditambahkan ke seen file (10236 -> 10238). "
    "Boltbook EN+ZH + 10 post (subagent): semua item 'baru' ternyata sudah dikenal - Stickman/HIPPO/AgentX/SEAT/Cogito/"
    "Aura/Hackagent/NIGHT/Alchemister/Conciergo/LunarAgentRion sudah di snapshot (re-read, tanpa perubahan tier); "
    "AgentMiner + Agent Apes hanya di seen -> keduanya AGE-EXCLUDED run ini (lihat excluded). PLNK sudah dilaporkan "
    "hot leg 09:54 sebagai gate-blocked (lihat track_c PLNK). KALOS/Nero sudah excluded. MiniCoin COI (search-index only, "
    "Sourcify not_verified, tanpa website) -> log only. Wezards MAGES track B: distributor 0xbD70930... + token "
    "0xE12A32... (claimFree, freeClaimsOpen 1, 137/5000) TAPI user TIDAK pegang Wezards NFT (balanceOf(user)=0 pada "
    "wezardsNFT 0xe4d7ec33fcf7d93cbe7f4d46d0ef35f437956aab) -> TIDAK eligible, bukan kandidat/pending. "
    "Web sweep: ENIGMAAGENT (sudah excluded sold-out 2026-11-06; re-cek pool run ini GAGAL transport, status excluded tetap) "
    "dan M3M3-M3MO (sudah excluded age 2026-11-06) -> keduanya re-discovery, bukan lead baru. Square/Odaily/PANews/DappBay "
    "tanpa site link / pengumuman baru. Bridge: tidak berubah (115 entri, terakhir diubah 2026-11-06 02:48). "
    "Pending claims kosong; BINANCEAI TERBACA run ini (launched=0, failed=1, isRefundPhase=1, totalShares=3110, "
    "tokenClaimed(user)=0, tokenBalance(user)=0) - tetap fase refund/failed, tidak ada aksi; Grove freeOpen 0, "
    "freeClaimed_user false. Age sweep: 0 REMOVE dari watchlist aktif (42 item >48 jam dipertahankan; 373 umur UNVERIFIED). "
    "TIDAK ada eksekusi oleh run ini (tidak ada mint/preview/claim). ATURAN DIAM: tidak ada laporan ke chat utama.")
snap["runNote1401_scan"] = (
    "Run 1401 SCAN: preflight retry PASS (head 132160077). Window 132159154-132160153 (1000 blok, cap) "
    "GAGAL SEBAGIAN: 4/20 chunk selesai (132159154-132159353, 200 blok), ERROR chunk 132159354-132159403 "
    "'Remote end closed connection without response' -> break. Ankr calls 8, errors 1. 49 NFT + 109 ERC-20-mint, "
    "0 first-seen sejati. Watermark TIDAK dimajukan (132158418). Gap 132158419-132159153 (735) + 132159354-132160153+ "
    "(800+) tidak ter-scan; backfill disabled user 14:26 WIB sehingga gap tidak ditutup.")
snap["runNote1401_1107_age_exclusions"] = (
    "Run 1401 AGE-EXCLUSIONS: 0 dari watchlist aktif (age sweep: 0 kandidat REMOVE). "
    "2 item seen-file yang baru dieksklusi run ini: Agent Apes 0xbf18... (first mint 2026-11-03 11:55:51 WIB, umur 99,5 jam) "
    "dan AgentMiner 0xCe67... (first mint 2026-11-04 23:30:32 WIB, umur 63,8 jam) - keduanya belum sold out (mintOpen 1), "
    "tidak pernah di snapshot / tidak pernah dilaporkan sebagai lead. "
    "DIPERTAHANKAN: semua minted-by-user (grandfathered), semua promotion-discarded-same-owner / "
    "watchlist-only-same-owner-discarded, semua sold-out, semua watchlist-only yang launch-nya UNVERIFIED.")
snap["runNote1401_binanceai"] = (
    "Run 1401: BINANCEAI TERBACA (launched=0, failed=1, isRefundPhase=1, totalShares=3110, "
    "tokenClaimed(user)=0, tokenBalance(user)=0). Tetap fase refund/failed; pending_claims kosong; tidak ada aksi, "
    "tidak dilaporkan ulang. Grove: freeOpen 0, freeClaimed_user false.")
snap["runNote1401_wezards"] = (
    "Run 1401 WEZARDS MAGES (track B, temuan Boltbook): distributor 0xbD709301473aC208f1bc4be598aE53295d311459 "
    "(claimFree, freeClaimsOpen=1, freeClaimsCompleted=137/5000, claimsPermanentlyEnded=0) + token "
    "0xE12A32c9E92f0584ede944465960D97238013107 (claimFree, hasClaimed, remainingFreeClaims). Entitlement = Wezards NFT "
    "0xe4d7ec33fcf7d93cbe7f4d46d0ef35f437956aab; balanceOf(user)=0 -> user TIDAK pegang entitlement -> BUKAN kandidat "
    "track B (freeClaimedNFT(user) gagal baca transport, moot karena entitlement 0). MAGES balanceOf(user)=0. "
    "Tidak masuk pending_claims, tidak dilaporkan.")
snap["last_run"] = "2026-11-07-1401"
snap["timestamp_wib"] = "2026-11-07 15:30 WIB"
snap["last_run_note"] = snap["runNote1401_1107"]
snap["last_run_wib"] = "2026-11-07 15:30 WIB"

with open(f"{BASE}/onchain-snapshot.json.tmp", "w") as f:
    json.dump(snap, f, indent=1)
os.replace(f"{BASE}/onchain-snapshot.json.tmp", f"{BASE}/onchain-snapshot.json")
print(f"FINALIZE DONE updated={updated} none_free_views={none_free} "
      f"contracts_now={len(snap['contracts'])} excluded_now={len(snap.get('excluded', {}))} "
      f"track_c_now={len(snap.get('track_c', {}))}")
