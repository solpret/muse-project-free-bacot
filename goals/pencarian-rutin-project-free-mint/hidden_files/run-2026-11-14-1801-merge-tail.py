
# --- new entries from Boltbook/probe/sweep (run 1801) ---
probe = json.load(open(BASE + "run-2026-11-14-1801-probe.json"))
snap["contracts"]["Storm Agent"] = {
 "address": "0x57cb78a895b783e210659a8b3371971641b968a3",
 "name": "Storm Agent", "kind": "ERC721",
 "status": "checked-age-excluded-2026-11-14",
 "totalSupply": 9902, "totalMinted": 9902, "MAX_SUPPLY": 10000,
 "mintedBy_user": 0, "balanceOf_user": 0,
 "lastReadBlock": BLOCK, "lastReadWib": WIB,
 "launchNote": "AGE-EXCLUDED: monitor Boltbook pertama mendeteksi 2026-11-12 03:02 WIB -> launch <= 12 Nov 03:02 -> umur >= ~63 jam saat run 18:01 14 Nov > 24 jam. Post recheck 18:00 (tungquan42.ai): 9.902/10.002 free (99,0%).",
 "baselineNote": "Probe on-chain run 1801: totalSupply 9902/10000 (cocok angka post 9.902), AGENT_ID()=registry Binance persis + registry bytes TRUE (agent-shaped TERVERIFIKASI), price 0,001 BNB (jalur berbayar), free views (freeClaimed/freeMinted/freeLeft/FREE_SUPPLY) semua revert -> free% TIDAK terverifikasi on-chain (angka 99% dari post). Slot user: mintedBy(user)=0, balanceOf=0. Sourcify UNVERIFIED. TIDAK PERNAH dilaporkan sebagai lead -> DIAM (age-excluded, belum pernah dilapor). BUKAN kandidat/strong lead.",
 "runNote1801_1114": "Run 1801: Storm Agent 0x57cb78a8 totalSupply 9902/10000, registry bytes TRUE, AGENT_ID=registry. AGE-EXCLUDED (first detection 12 Nov 03:02). TIDAK dilaporkan (belum pernah dilapor).",
}
snap["contracts"]["Sora Agent"] = {
 "address": "0x5aaa9dcae9d548cf7118b1d2c21be27313f1ae1d",
 "name": "Sora Agent", "kind": "ERC721",
 "status": "checked-age-excluded-2026-11-14",
 "totalSupply": 9900, "totalMinted": 9900, "MAX_SUPPLY": 10000,
 "mintedBy_user": 0, "balanceOf_user": 0,
 "lastReadBlock": BLOCK, "lastReadWib": WIB,
 "launchNote": "AGE-EXCLUDED: monitor Boltbook pertama mendeteksi 2026-11-03 17:47 WIB -> launch <= 3 Nov 17:47 -> umur >= ~11 hari saat run 18:01 14 Nov > 24 jam. Post recheck 17:58 (tetternice.ai): 9.900/10.000 free (99,0%).",
 "baselineNote": "Probe on-chain run 1801: totalSupply 9900/10000 (cocok angka post 9.900), AGENT_ID()=registry Binance persis + registry bytes TRUE (agent-shaped TERVERIFIKASI), price 0,001 BNB, free views semua revert -> free% TIDAK terverifikasi on-chain. Owner SAMA dengan Storm Agent (template/owner sama, code_len 6799 identik). Sourcify UNVERIFIED. TIDAK PERNAH dilaporkan sebagai lead -> DIAM. BUKAN kandidat/strong lead.",
 "runNote1801_1114": "Run 1801: Sora Agent 0x5aaa9dca totalSupply 9900/10000, registry bytes TRUE. AGE-EXCLUDED (first detection 3 Nov 17:47). TIDAK dilaporkan.",
}
snap["contracts"]["Oathbots"] = {
 "address": "0xb777c52296f0d7d3c5cab7ae0c1aaac6b014b256",
 "name": "Oathbots", "kind": "ERC721",
 "status": "checked-age-excluded-2026-11-14",
 "lastReadWib": WIB,
 "launchNote": "AGE-EXCLUDED: post Binance Square 2026-10-28 18:04 UTC (17 hari lalu) menyebut ~375 sudah termint -> launch <= 28 Okt -> umur >> 24 jam. Situs oathbots.pages.dev, 8.000 free pertama (gas-only), lalu 0,0005 BNB.",
 "baselineNote": "Ditemukan via sweep EN run 1801. TIDAK dicek on-chain lanjut karena umur sudah lewat jauh. TIDAK PERNAH dilaporkan sebelumnya -> DIAM.",
 "runNote1801_1114": "Run 1801: Oathbots 0xb777c522 (Square 28 Okt, ~375 minted saat posting). AGE-EXCLUDED, TIDAK dilaporkan.",
}
snap["contracts"]["BUGHOUND"] = {
 "address": "0x8a7be94d1c36a60bcdd155d37faf84403b8a26ae",
 "name": "BUGHOUND", "symbol": "HOUND", "kind": "ERC721",
 "status": "checked-not-agent-shaped-2026-11-14",
 "totalSupply": 265, "freeLeft": 1736, "MAX_SUPPLY": 9999, "mintOpen": 1,
 "mintedBy_user": 0, "balanceOf_user": 0,
 "lastReadBlock": BLOCK, "lastReadWib": WIB,
 "launchNote": "Post Boltbook drhmwt.ai ~17:54 WIB: 263/9.999, pace 0/mnt. Umur UNVERIFIED.",
 "baselineNote": "Probe on-chain run 1801: totalSupply 265, freeLeft 1736, MAX_SUPPLY 9999, mintOpen 1, registry bytes FALSE, AGENT_ID() null -> BUKAN agent-shaped. 265/9.999 = 2,7% (jauh di bawah 50%/70%), pace 0. BUKAN early lead (first mints bukan run ini + bukan agent-shaped), BUKAN kandidat/strong lead. Tidak masuk watchlist aktif.",
 "runNote1801_1114": "Run 1801: BUGHOUND 0x8a7be94d totalSupply 265/9999, registry FALSE -> NOT agent-shaped. Tidak dilaporkan.",
}
snap["contracts"]["CAVE"] = {
 "address": "0xF8654BB769B48fD4c619bfFD5a5fEED066d6a85F",
 "name": "CAVE", "symbol": "CAVE", "kind": "ERC721",
 "status": "checked-not-agent-shaped-2026-11-14",
 "totalMinted": 261, "mintedBy_user": 0, "balanceOf_user": 0,
 "lastReadBlock": BLOCK, "lastReadWib": WIB,
 "launchNote": "Post Boltbook yuibnb.ai ~17:50 WIB: 255/5.000, pace ~0,67/mnt. Umur UNVERIFIED.",
 "baselineNote": "Probe on-chain run 1801: totalMinted 261, registry bytes FALSE, AGENT_ID() null -> BUKAN agent-shaped. 261/5.000 = 5,2% (jauh di bawah 50%/70%). BUKAN early lead (first mints bukan run ini + bukan agent-shaped), BUKAN kandidat/strong lead. Sudah di hot-leg-seen (sourcify-feed 13:39). Tidak masuk watchlist aktif.",
 "runNote1801_1114": "Run 1801: CAVE 0xF8654BB7 totalMinted 261/5000, registry FALSE -> NOT agent-shaped. Tidak dilaporkan.",
}
for _addr, _vat in [("0xe778a8401cb1b835c806eebe7025538263195335", "2026-11-14T11:01:23Z"),
                    ("0x5a5eff4e9c5bad00e97cc33d6e6d26983509eeb8", "2026-11-14T11:01:20Z"),
                    ("0xcbbaf9b2b3393d75d2fd1ebf344af1b43ef292e8", "2026-11-14T11:00:35Z")]:
    _key = "Feed-" + _addr[2:6]
    snap["contracts"][_key] = {
     "address": _addr, "status": "checked-not-sale-shape-2026-11-14",
     "lastReadWib": WIB, "lastReadBlock": BLOCK,
     "baselineNote": "Feed Sourcify run 1801 (verifiedAt %s): shape-check S1=False S2=False, has_mint=False, has_quote=False, free_views=[], agent_ref=False, n_fns=0 (ABI kosong). BUKAN sale-shape, BUKAN agent-shaped. Tidak dilaporkan, tidak masuk watchlist aktif." % _vat,
     "runNote1801_1114": "Run 1801: feed %s S1/S2 False, ABI kosong -> bukan sale-shape." % _addr[:10],
    }

# LumenFindings: genesis opened 13 Nov 08:43 WIB -> age >24h -> AGE-EXCLUDED
lum = snap["contracts"]["LumenFindings"]
lum.update({"status": "age-excluded-2026-11-14", "totalSpecimens": 2969,
            "currentExperiment": 12, "genesisStart": 1794534187, "genesisOpen": 1,
            "lastReadBlock": BLOCK, "lastReadWib": WIB})
lum["launchNote"] = ("Launch TERVERIFIKASI: genesisStart() on-chain 1794534187 = 2026-11-13 08:43:07 WIB "
                     "(konsisten baca 1701/1731/1801); umur ~33 jam saat run 1801 > 24 jam -> AGE-EXCLUDED.")
lum["runNote1801_1114"] = ("Run 1801: totalSpecimens 2958->2969 (+11, velocity GAGAL). genesisStart 1794534187 = 13 Nov 08:43:07 WIB "
                           "(baca 0801 'genesisStart 0' adalah artefak GAGAL BACA, bukan belum dibuka - baca 1701/1731/1801 konsisten). "
                           "Umur ~33 jam > 24 jam -> AGE-EXCLUDED. TIDAK PERNAH dilaporkan sebagai lead -> DIAM.")

# NOISE / Entr0pic: 259 already minted by 05:32 13 Nov -> age >24h -> AGE-EXCLUDED
nz = snap["contracts"].setdefault("NOISE", {})
nz.update({"address": "0xBA5352A3A05Ec637394810D791a412E78A349247",
           "name": "Entr0pic Living Noise", "symbol": "NOISE", "kind": "ERC721",
           "status": "age-excluded-2026-11-14",
           "lastReadBlock": BLOCK, "lastReadWib": WIB})
nz["launchNote"] = ("Launch TERVERIFIKASI (batas atas): post Boltbook nanomind.ai run ini: 259 termint pada 05:32 WIB 13 Nov "
                    "-> launch <= 13 Nov 05:32 -> umur >= ~36,5 jam saat run 1801 > 24 jam. Situs resmi https://entr0pic.com (dari post). "
                    "totalMinted 1.158/3.333, pace ~0,62/mnt (cooling).")
nz["runNote1801_1114"] = ("Run 1801: totalMinted 1146->1163 (+17, velocity GAGAL <20). AGE-EXCLUDED "
                          "(259 sudah termint 05:32 13 Nov). TIDAK PERNAH dilaporkan sebagai lead -> DIAM.")

snap["runNote1801_1114"] = (
 "Run 1801: reread 41/41 OK blok 133532820 (204,6 dtk, interval ~30,1 mnt vs run 1731). "
 "Velocity LOLOS 0 item. Close-fail: [('PIXEL FROGS', 40, 1.329, 1.06)] - free 200/3000=6,7%%, gate FAILED, BUKAN promosi. "
 "WoozCode +48 (1,59/mnt, 0,42x vs prev 3,75) velocity GAGAL; free%% UNVERIFIED. Ledgera +18 (<20) velocity GAGAL; free 2535/5000=50,7%% (<70%%). "
 "RaceAgents +3, freeMinted 566/1000=56,6%% - velocity belum terhitung (baseline 1701 None), umur/website/X unverified -> BUKAN kandidat/strong lead. "
 "AgentBubble free 1564 totalSupply, velocity GAGAL (+1). HIVE 1263 FLAT, minted-by-user. "
 "AgentZENITH 527 / AgentNOVA 516 / SPARKS 485 / OTV 577 (freeMintsLeft 0) / RAVE 249 / SKRR 523 terbaca lagi run ini setelah gagal di 1731; Zero/PX24 masih gagal baca. "
 "PIXEL FROGS 162->202, free 200/3000=6,7%% - bukan promosi (gate FAILED, sudah dilaporkan 15:35). "
 "HAPPE totalMinted 237->239, free pool tetap HABIS 222/222. "
 "LumenFindings AGE-EXCLUDED run ini (genesisStart 13 Nov 08:43 WIB, umur ~33 jam). NOISE/Entr0pic AGE-EXCLUDED run ini (259 termint 05:32 13 Nov). "
 "Storm Agent + Sora Agent 99%% free TAPI age-excluded (first detection 12 Nov / 3 Nov) - TIDAK dilaporkan. "
 "DragonAgents +12 (age-excluded, moot). WANGCAI/YUANBAO tetap sold out 188/188. "
 "0 kandidat baru, 0 strong lead baru, 0 early lead baru, 0 track-B, 0 track-C lead/kandidat baru, 0 eksekusi/preview.")
snap["runNote1801_1114_scan"] = (
 "Scan leg FAST-FAIL run 1801: pre-flight ankr_getLogs HTTP 401 Unauthorized dalam 9,3 dtk "
 "(head 133532399 via dataseed). Scan TIDAK dijalankan; watermark tetap 132512564; track-C 5c dilewati (tanpa output scan). "
 "Outage Ankr 401 sejak 2026-11-09 berlanjut; perlu reconnect kredensial Ankr (di luar scope job ini).")
snap["runNote1801_1114_feedshape"] = (
 "Feed Sourcify run 1801 (limit 20, top verifiedAt 2026-11-14T11:01:23Z 0xe778a840): 3 benar-benar baru vs hot-leg 1759 "
 "(0xe778a840, 0x5a5eff4e, 0xcbbaf9b2) - ketiganya dicek run ini: S1=False S2=False, has_mint=False, has_quote=False, free_views=[], "
 "agent_ref=False, n_fns=0 (ABI kosong) -> BUKAN sale-shape, BUKAN agent-shaped. 6 kontrak hot-leg 1759 sudah di-shape-check di sana (0 S1/S2). "
 "0 early lead baru dari feed.")
snap["runNote1801_1114_boltbook"] = (
 "Boltbook EN+ZH run 1801 (fetch ~18:0x WIB, EN 46.437 byte, ZH 46.132 byte, 29 post EN). Alamat baru vs snapshot+hot-leg-seen: 3. "
 "(1) Storm Agent 0x57cb78a8 (post tungquan42.ai 18:00, 9.902/10.002 free 99,0%) - probe on-chain: totalSupply 9902 cocok, AGENT_ID=registry, "
 "TAPI first detection 12 Nov 03:02 -> AGE-EXCLUDED, tidak dilaporkan. "
 "(2) Sora Agent 0x5aaa9dca (post tetternice.ai 17:58, 9.900/10.000 free 99,0%, kontrak dari halaman post) - probe: totalSupply 9900 cocok, "
 "AGENT_ID=registry, TAPI first detection 3 Nov 17:47 -> AGE-EXCLUDED, tidak dilaporkan. "
 "(3) BUGHOUND 0x8a7be94d (263/9.999, pace 0) - probe: registry FALSE -> NOT agent-shaped, tidak dilaporkan. "
 "CAVE 0xF8654BB7 (255/5.000, pace ~0,67/mnt) - probe: registry FALSE -> NOT agent-shaped, tidak dilaporkan. "
 "Entr0pic/NOISE (post nanomind.ai): 259 termint 05:32 13 Nov -> AGE-EXCLUDED run ini. PIXEL FROGS recheck Boltbook 186/3.000 vs bacaan sendiri 202/3.000. "
 "0 early lead baru dari Boltbook run ini.")
snap["runNote1801_1114_sweep"] = (
 "Sweep EN+ZH run 1801: 0 baru yang lolos. EN: Oathbots 0xb777c522 (Square 28 Okt, ~375 minted) -> AGE-EXCLUDED, dicatat di snapshot, DIAM; "
 "Agentic Gangster (di snapshot, free pool exhausted); Meow Cards / STAMP PASS / RIGBYPASS (di snapshot, excluded). "
 "ZH: KOMA (track_c age-excluded 13 Nov); First-Dollar Grove + AGENT COSMOS (di snapshot, age-excluded); Subsonic Tribe (sold out). "
 "Komplemen 6a Square tercakup sweep (tanpa proyek baru). 6b Odaily/PANews + 6c DappBay: tidak ada gate-check yang dibutuhkan run ini, dilewati.")
snap["runNote1801_1114_binanceai"] = (
 "Run 1801: binanceai.fun TIDAK BERUBAH - launched()=0, failed()=1, isRefundPhase()=1, totalShares=3110, "
 "tokenClaimed(user)=0 (blok 133532820). Status pending/refund; sudah dilaporkan sekali (fase refund), DIAM.")
snap["runNote1801_1114_bridge"] = (
 "Run 1801: bridge file dibaca read-only (mtime 2026-11-08 18:21 UTC, tidak berubah). 116 kontrak, 0 benar-benar belum ada di snapshot "
 "(cek kehadiran aktual, bukan flag stale in_freebacot_snapshot), 7 same_owner_discarded. "
 "Job ini tidak menulis bridge; temuan pelengkap scan tidak ada yang naik tier.")
snap["runNote1801_1114_pixelfrogs"] = (
 "PIXEL FROGS (PXFRG) 0x454054e55FA2D7Ba37df7F3ceA269696f19037dF - run 1801: totalSupply 162->202, freeMinted 200/3000 = 6,7%%, "
 "freeLeft 2800, mintOpen 1, slot user terbuka (freeClaimed(user)=0). Launch TERVERIFIKASI 2026-11-14 15:29:57 WIB, umur ~2,5 jam, "
 "deadline 24 jam 2026-11-15 15:29:57 WIB. Website tetap UNVERIFIED (gate FAILED, sudah dilaporkan sekali 15:35). "
 "BUKAN strong lead (6,7%% < 70%%), BUKAN kandidat. Tetap watchlist-only; promosi hanya bila free%% menembus 70%% + gate lolos.")
snap["runNote1801_1114_happe"] = (
 "HAPPE AGENTS (HAPPE) 0x72c14121681F1133545947B0735563835CC07B67 - run 1801: totalMinted 237->239, free pool tetap HABIS 222/222, "
 "paid 17, mintOpen 1, isEligible(user)=1. Status early-lead-reported-sold-out-2026-11-14 (dilaporkan sekali run 1701); "
 "BUKAN kandidat/strong lead; TIDAK PERNAH di-preview/di-mint; jangan laporkan ulang.")
snap["runNote1801_1114_storm_sora"] = (
 "Storm Agent 0x57cb78a895b783e210659a8b3371971641b968a3 + Sora Agent 0x5aaa9dcae9d548cf7118b1d2c21be27313f1ae1d - run 1801: "
 "keduanya 99%% free menurut post Boltbook DAN totalSupply on-chain cocok (9902/10000 dan 9900/10000), AGENT_ID()=registry Binance persis, "
 "owner sama, code_len 6799 identik (template sama). TAPI keduanya AGE-EXCLUDED: Storm first detection 12 Nov 03:02 (umur >=63 jam), "
 "Sora first detection 3 Nov 17:47 (umur >=11 hari). Free views revert (free%% tidak terverifikasi on-chain), Sourcify UNVERIFIED. "
 "TIDAK PERNAH dilaporkan sebagai lead -> DIAM. Dicatat di snapshot sebagai checked-age-excluded-2026-11-14.")
snap["runNote1801_1114_lumen_noise"] = (
 "LumenFindings + NOISE/Entr0pic AGE-EXCLUDED run 1801. LumenFindings: genesisStart() on-chain 1794534187 = 13 Nov 08:43:07 WIB "
 "(konsisten 1701/1731/1801; 'genesisStart 0' di baseline 0801 adalah artefak gagal baca), umur ~33 jam. "
 "NOISE/Entr0pic: post Boltbook nanomind.ai - 259 termint 05:32 WIB 13 Nov, situs resmi https://entr0pic.com, totalMinted 1.158/3.333, "
 "pace ~0,62/mnt cooling; umur >= ~36,5 jam. Keduanya TIDAK PERNAH dilaporkan sebagai lead -> DIAM, hanya dicatat di snapshot.")
snap["last_run_wib"] = WIB
snap["last_run_note"] = snap["runNote1801_1114"]
snap["timestamp_wib"] = WIB

json.dump(snap, open(BASE + "onchain-snapshot.json", "w"), indent=1)
print("merged. velocity LOLOS:", vel_pass)
print("velocity close-fail:", vel_fail_close)
print("interval prev/cur min:", round(INT_PREV, 2), round(INT_CUR, 2))
