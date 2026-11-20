# RINGKASAN KAKI ON-CHAIN — run free-mint-search 2026-11-08 1031 WIB

- Skrip: salinan run 1001 → 1031 (reread, velocity, age-sweep, binanceai). Baseline velocity = run 1001 (blok 132318075).
- Re-read: blok 132323930, interval 43,91 mnt (5.855 blok × 0,45 dtk), durasi ~830 dtk, exit 0.
- Snapshot TIDAK ditulis oleh kaki ini (read-only); snapshot/state/watermark/seen/track-c-checked tidak disentuh. Tidak ada preview/mint/eksekusi.

## 1. Re-read
- Kontrak di-re-read: **473** (run 1001: 471). Baru vs 1001: **NovaAgent** 0xa6909af663637cd988e712efbc2e73f7076d9154 (4.900/5.000, sisa 100, freePct null, balance user 0, belum ada baseline velocity) dan **Zigzoo** 0x09ada5a12293c30d75b97c56e34967e8a4326a3c (1.066/5.000, freePct null, balance user 0). Keduanya sudah ada di snapshot (ditambahkan parent merge antar-run); kaki ini hanya membaca ulang, bukan menemukan.
- 5 entri snapshot TIDAK ter-re-read (kondisi lama, bukan gagal baru): Mummyhive, LuckyBox-d08e, SnailMail, Jolly, AgentGlyph — semuanya tanpa field `address` di snapshot sehingga skrip re-read melewatinya.
- Track_c di-re-read: **70** (sama seperti 1001).

## 2. Velocity (5 pass, 0 promotable)
Pass (rate ≥1,5x + ≥20 token dalam interval):
| Nama | Minted | Rate/mnt | Rasio | freePct | Alasan TIDAK promotable |
|---|---|---|---|---|---|
| Zhenzhu 0x7e2da878217eb995f9e5d36ed32c9cea52442681 | 13.317.855.874.544 | 303.281.659.539,86 | 3,42 | null | free% unverified; supply skala token (21,4 kuadriliun) — artefak ERC-20, bukan counter free-mint NFT |
| Weldagent 0x30F3626Dc29a4d8F7A6Fe873Ad3e61cFE69BfbED | 40 | 0,9109 | 75,28 | 6,86% | free% <25% (bukan strong) dan <50% (bukan kandidat); status same-owner-discarded |
| NULLRAID First Breach 0xdec01cdfb41e7871fb7ca7b12b1572ce292743c0 | 38 | 0,8654 | 6,51 | null | sudah minted-by-user 2026-11-07; free% unverified |
| WAR3-1aa9 0x1Aa9797cC762b838388566Daa45A56b1709F4Bbe | 24 | 0,5465 | 2,83 | null | sudah minted-by-user 2026-11-08 (#2511); free% unverified |
| Lambdwyn 0xCa7A3faa22AC4ABBf5528B41AC7d12B28651AA6B | 20 | 0,4555 | 1,64 | null | free% unverified; umur peluncuran unverified (launchNote kosong) |

- 5 pass run 1001 (Alchemister, BOT-UNIT, Gourdmare, UNKNOWN-1Aeb, Vesperfang) semuanya TIDAK pass lagi di run ini.
- HIVE Agents 0x1458b0C132Fb51BDC65B1Ca7a3BE484BCd9A2f77: 0 mint dalam interval (1.256/10.000), balance user 1, freePct null — tidak ada perubahan.

## 3. Sellout / slot
- SoldOut total: **35** — set SAMA PERSIS dengan run 1001; **0 soldout baru**, 0 yang lepas dari soldout.
- Near-sellout: 0. Slot berubah: **0** (balanceOf_user tidak berubah di kontrak mana pun).

## 4. Age-sweep
- REMOVE: **0**. Kept: 56 (mayoritas minted-by-user / same-owner-discarded, umur 150–156 jam). Launch unverified: 410 entri (tidak ada aksi; tetap watchlist-only).
- Tidak ada item watchlist yang melewati 48 jam dan belum sold out di luar status keep di atas.

## 5. Track-B — binanceai (re-check)
- Blok 132325785, durasi 30,2 dtk. MINT 0x46cb1D3efd4307506Cda7EbBa5a51be64746739E, TOKEN 0x209173F09aFbCA053C0de9e9763f503e9fb54a3c, pair 0x903ACC22B9BABCD427bfb9AF2C27a27a5aC7c698.
- **TIDAK BERUBAH vs run 1001 / status terakhir**: launched=0, failed=1, isRefundPhase=1, totalShares 3.110, tokenClaimed_user=0, token balance user 0, pair reserves 0/0. Tetap closed-refund-phase-2026-11-07. Bukan perubahan penting.

## 6. Track_C
- 70 item di-re-read; 6 berubah hanya pada totalSupply (tanpa sinyal free pool/slot — freeMinted/freeClaimed null di semua):
  - CHTCI 261.000 → 262.000; Crack 3.716 → 3.725 (balance user tetap 1); ORBITA 896 jt → 913 jt (balance user tetap 1 jt); PLNK 601 jt → 607 jt; Draco Coin 4.000.000 → 4.025.000; PHNX 3.225.000 → 3.250.000.
- **BNBbaby** sale 0xbb7ed59ca41ea03cf20084a8c9de94244b7b2637: bacaan jalur re-read ini null semua (totalSupply/freeMinted/freeClaimed/balance user — sama seperti run 1001; artefak jalur baca, bukan perubahan state). Data snapshot tetap acuan: status minted-by-user-2026-11-02, first mint terverifikasi 2026-11-01 19:33 WIB → umur kini ~159 jam (>48 jam). **Temuan tercatat**: umur >48 jam dan belum pernah dilaporkan sebagai age-excluded — NAMUN statusnya minted-by-user (grandfathered; age-sweep KEEP_STATUSES mencakup minted-by-user), jadi BUKAN kandidat REMOVE; parent yang memutuskan. Tidak ada perubahan free pool/slot yang terverifikasi dari kaki ini.
- Item track_c aktif lain: tidak ada perubahan free pool, user slot, atau umur yang terverifikasi.

## 7. Scan-bridge (read-only)
- scan-bridge.json: 115 kontrak; **33 belum ada di snapshot/track_c** — dicatat sebagai "temuan pelengkap scan", BUKAN lead baru job ini, tidak dilaporkan sebagai early lead.
- Dari 33 itu: 1 same_owner_discarded (Krillfarm 0x0aa11f327313682cdf072affff26d0dffc804483 — tidak pernah dipromosikan); 2 dengan website terverifikasi via pointer (MonkeAgents 0xd06518ea638cab567328ccd7b67e43a119c275e0 → https://monkeagents.xyz; PixelTrump 0x3054a5530f1852c33bd2749bfaf7155f162a581b → https://pixeltrump.pages.dev); 3 ber-flag seeded `in_freebacot_snapshot=true` (flag basi — alamatnya tidak ada di snapshot saat ini).
- Semua 33 first_seen 2026-11-03 s.d. 2026-11-06 → umur semuanya >48 jam kini; tidak ada yang promotable sebagai early lead walau ditambahkan ke watchlist. Tidak ada kontrak bridge baru sejak run 1001 (file bridge terakhir diubah 2026-11-06).

## 8. Catatan file
- run-2026-11-08-1031-reread.py / .json / .log (blok 132323930)
- run-2026-11-08-1031-velocity.py / .json (passes=5, soldOut=35, slotChanged=0)
- run-2026-11-08-1031-age-sweep.py / .json (remove=0, kept=56, unverified-launch=410)
- run-2026-11-08-1031-binanceai.py / .json (blok 132325785, tidak berubah)
- run-2026-11-08-1031-grove-check.json/.py adalah cek Agent Grove (bukan binanceai) — TIDAK dipakai ulang untuk binanceai; binanceai di-re-check dengan skrip sendiri seperti di atas.

## KESIMPULAN
**TIDAK ADA perubahan yang butuh dilaporkan ke chat utama**: 0 kandidat baru, 0 strong lead baru, 0 early lead baru, 0 sellout baru, 0 age-exclusion baru, 0 slot hilang, track-B dan track-C tidak berubah. Satu-satunya temuan tercatat: BNBbaby track_c berumur >48 jam (grandfathered minted-by-user) dan 33 temuan pelengkap scan dari bridge (semuanya berumur >48 jam, bukan lead baru).
