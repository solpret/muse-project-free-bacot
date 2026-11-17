# First-30 early buyer — UAI, Beat, LAB, DEBIT, ARIA (BSC, read-only)

Waktu laporan: 2026-11-02 malam WIB. Saldo dibaca pada pass retry terakhir (file bukti diperbarui 2026-11-02 20:51 WIB); waktu beli pertama memakai timestamp header blok (eth_getBlockByNumber), BUKAN inferensi dari nomor blok. Semua alamat di bawah adalah alamat lengkap 42 karakter yang disalin dari log/RPC — tidak ada alamat terpotong. Tidak ada transaksi, approval, signing, wallet connect, GMGN, atau browser task. Tidak ada file state/feed/cron/goal yang diubah.

## Ringkasan eksekutif

| Koin | Pair yang dipindai (PCS V2, factory) | Pasar pertama? | Hasil pindai | Bersih (EOA + bukan coret + pegang >0,5%) |
|---|---|---|---|---|
| UAI | TIDAK ADA pair V2 (lihat §UAI) | BUKAN V2 — pool terawal Gecko adalah V3 UAI/BNB 2025-11-04 | GAGAL TOTAL untuk pindai V2 — tidak ada tabel yang dikarang | — |
| Beat | 0x35b240d7f4b99d1d5870b1b7b27dfd6681449614 (V2-WBNB) | BUKAN — pool terawal Gecko 2025-10-31, pair V2 dibuat 2025-11-25 | 30 pembeli pertama | 2 wallet (Beat #2 PARTIAL, Beat #13 HOLD) |
| LAB | 0x5d43403cc3869ee31989504b8eb93cd3c2d4cb9f (V2-WBNB) | BUKAN — pool terawal Gecko 2025-10-13, pair V2 dibuat 2026-09-06 | HANYA 17 pembeli distinct sampai blok terbaru yang dipindai — TIDAK mencapai 30 | 1 wallet (LAB #15 HOLD) |
| DEBIT | TIDAK ADA pair V2 (lihat §DEBIT) | BUKAN V2 — pool terawal Gecko adalah V3 DEBIT/USDT 2026-08-24 | GAGAL TOTAL untuk pindai V2 — tidak ada tabel yang dikarang | — |
| ARIA | 0xbe9b3c913edd6b92cdb987510d1553d066a9e83e (V2-USDT, PELENGKAP — V2-WBNB tidak ada) | BUKAN — pool terawal Gecko 2025-08-19, pair V2-USDT dibuat 2025-09-01 | 30 pembeli pertama | 2 wallet (ARIA #18 HOLD, ARIA #29 HOLD) |

Temuan headline:
- Ketiga pair V2 yang bisa dipindai SAMA SEKALI BUKAN pasar pertama tokennya: semuanya dibuat berminggu-minggu sampai berbulan-bulan SETELAH pool pertama di GeckoTerminal. Jadi tabel di bawah adalah '30 pembeli pertama PADA PAIR V2 TERSEBUT', BUKAN pembeli peluncuran token (launch buyers). Jangan pakai tabel ini sebagai bukti early-buyer peluncuran.
- Pair-pair V2 ini sangat sepi dan didominasi kontrak: Beat 26/30 kontrak, ARIA 26/30 kontrak, LAB 13/17 kontrak. Mayoritas pembeli pertama adalah kontrak/bot executor atau pool lain yang berarbitrase antar pair — bukan wallet EOA ritel.
- TIDAK ADA satu pun pembeli di ketiga tabel yang cocok (exact-match) dengan: 50 wallet terpantau (tier-ab-watch-state.json), TRIO, PAIR #2, IBS #2, BORT #8, klaster GANG, hub sniper 0xf598…, funder 0x318d…, kontrak token MSX, maupun wallet user (utama/kedua) — DENGAN SATU PENGECUALIAN: PAIR #1 TIDAK DAPAT DICEK karena string yang diterima dalam tugas berukuran 43 karakter heks, bukan alamat Ethereum valid (40 karakter); pengecekan untuk wallet itu dinyatakan TIDAK VALID (bukan NIHIL) sampai koordinator mengonfirmasi alamat PAIR #1 yang benar. Jadi TIDAK ADA kandidat 'baru' dari pindai ini yang terhubung ke set terpantau — dan tidak ada pula yang terkonfirmasi sebagai bagian dari daftar coret bernama tersebut (di luar PAIR #1 yang belum bisa dicek).
- TIDAK ADA klaim PnL, TIDAK ADA klaim 'terbukti insider' untuk apa pun. 'Proxy profit' (beli awal + pegang/jual) BUKAN PnL terverifikasi. Co-buy antar koin di bawah adalah linkage LEMAH saja; linkage KUAT (shared funding/transfer langsung) TIDAK dinilai di sini (tugas koordinator).

## Metode (on-chain saja)

- Pair PCS V2: `getPair(token, quote)` pada factory 0xca143ce32fe78f1f7019d7d551a6402fc5350c73, selector dihitung programatik dengan `eth_utils.keccak` (dipotong 4 byte; bukan hand-type). Semua token 18 desimal (dibaca on-chain). WBNB = 0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c, USDT = 0x55d398326f99059fF775485246999027B3197955, USDC = 0x8AC76a51cc950d9822D68b83fE1ad97B32Cd4E1e.
- Blok creation pair: log `PairCreated` factory lewat Ankr sebagai module (`ankr_getLogs`, topik dihitung programatik), BUKAN dari ID pool GeckoTerminal (ID-ID itu lebih panjang dari 20 byte dan tidak dipakai sebagai alamat). Percobaan `eth_call` historis (getPair pada nomor blok lama) GAGAL di semua endpoint dataseed ('missing trie node') — dicatat sebagai GAGAL BACA, bukan dipakai sebagai bukti apa pun.
- Status pasar-pertama: tanggal `pool_created_at` terawal dari endpoint GeckoTerminal `networks/bsc/tokens/<CA>/pools` (5 halaman pertama; Beat/LAB/DEBIT/ARIA masing-masing mencapai 100 pool pada batas ambil ini, UAI 92 pool total) dibandingkan dengan waktu creation pair V2 on-chain. Bila ada pool Gecko yang lebih awal dari creation pair V2, pair V2 dinyatakan BUKAN pasar pertama. ID pool Gecko TIDAK pernah dipakai mentah-mentah sebagai alamat pair.
- Pembeli pertama: log `Transfer` token dengan pengirim = pair (topik Ankr: Transfer + pengirim=pair), chunk 10.000 blok dari blok creation pair ke depan, diurutkan naik menurut (blok, logIndex). Bila satu chunk mengembalikan tepat 1.000 log, chunk dipecah — pada pindai berfilter-topik ini TIDAK ADA chunk yang mencapai 1.000 log, jadi tidak ada pemecahan yang terpicu (split_hit=false untuk ketiganya). Pindai berhenti setelah 30 pembeli distinct ditemukan DAN timestamp blok sudah melewati beli pertama pembeli ke-30 + 6 jam (Beat: chunk ke-400 karena pemeriksaan stop dilakukan per batch 200 chunk; ARIA: chunk ke-3200). LAB dipindai sampai blok terbaru yang dipakai (131.231.846) dan tetap hanya 17 pembeli distinct.
- Beli awal 6 jam = total Transfer pair→wallet dalam 6 jam sejak beli pertama wallet itu (filter timestamp header blok). Jual ke pair ≤1 jam = total Transfer wallet→pair dalam 1 jam sejak beli pertama wallet itu (rentang pindai sell: blok pertama + 30.000 blok, difilter timestamp header). Saldo sekarang = `balanceOf` via fast_rpc (rotasi endpoint tunggal, bukan batch besar — lihat Gagal baca). Ambang debu: saldo ≤0,5% beli awal 6 jam = SOLD. Status: HOLD ≥50%, PARTIAL >0,5% s.d. <50%, SOLD ≤0,5%. Saldo >100% berarti akumulasi/transfer masuk lanjutan, BUKAN posisi awal murni.
- EOA/kontrak: `eth_getCode` — kode non-kosong = kontrak/bot executor = CORET (tetap dicatat di tabel dengan alasan). Daftar coret lain (exact-match): hub sniper 0xf5988713400da6fc8a58ec9515e2b0df9b40b115, funder 0x318d2aae4c99c2e74f7b5949fa1c34df837789b8, kontrak token itu sendiri, pair/pair lain yang diketahui, dan pool lain yang terkonfirmasi on-chain (token0/token1). Klaster insider MSX: daftar anggota klaster TIDAK disertakan dalam tugas ini, jadi yang bisa dicek hanya exact-match terhadap kontrak token MSX 0x23214ccbffb6ef479da64d1842b10b5525997777 (hasil: nihil) — ketidakcocokan ini TIDAK membuktikan tidak ada anggota klaster MSX di tabel. Exchange dan wallet tim/vesting: tidak ada yang teridentifikasi dari data Transfer saja — tidak diklaim ada maupun tidak ada; pembelian berjumlah round-amount saja TIDAK dijadikan bukti tim/vesting.
- 'Bersih' di laporan ini = EOA (bukan kontrak) + bukan daftar coret + saldo >0,5% beli awal (HOLD atau PARTIAL). Fast dump (jual ke pair ≤1 jam ≥80% beli awal) dicatat sebagai catatan pada barisnya, BUKAN coret otomatis lintas koin (aturan coret lintas ≥3 launch tidak dapat diverifikasi dari dataset ini).
- BATAS METODE: (1) Metode Transfer buta terhadap transfer BNB native dan call tanpa event — funding BNB tidak terlihat. (2) `balanceOf` mencakup token yang masuk lewat transfer non-pair juga, jadi % masih dipegang adalah proxy, bukan rekonstruksi posisi pair-buy yang eksak. (3) Jual ke pair >100% beli awal berarti wallet itu menjual token yang didapat dari luar pair — dicatat, bukan dianggap kesalahan hitung. (4) Waktu jendela memakai timestamp header untuk semua blok yang masuk ke perhitungan buy6/sell1 dan blok beli pertama; log di luar jendela memakai timestamp Ankr (pada semua blok yang dicek keduanya, timestamp Ankr = timestamp header, mismatch 0 blok).

## UAI (UnifAI) — GAGAL TOTAL untuk pindai V2

- Token (CA persis dari tugas): 0x3e5d4f8aee0d9b3082d5f6da5d6e225d17ba9ea0 — 18 desimal. MCap dari GeckoTerminal 2026-11-02 17:35 WIB: ~$40,3 juta (angka tugas, tidak dibaca ulang).
- Verifikasi pair V2 lewat factory `getPair`: (token, WBNB) = 0x0000000000000000000000000000000000000000 (nol), (token, USDT) = nol, (token, USDC) = nol. Log `PairCreated` factory untuk pasangan WBNB, USDT, dan USDC: masing-masing 0 log. Kesimpulan: TIDAK ADA pair PCS V2 untuk UAI dengan quote WBNB/USDT/USDC.
- Status pasar-pertama: pair V2 tidak ada, jadi tidak ada 'pair V2 pertama' yang bisa dibandingkan. Pool terawal GeckoTerminal: UAI / BNB 0.007% dibuat 2025-11-04T07:08:50Z (pool V3 ber-fee tier, bukan V2).
- Hasil: TIDAK ADA tabel first-30 untuk UAI. Apa pun yang mengklaim '30 pembeli pertama UAI di pair V2' dari data ini adalah karangan. Pembeli pertama UAI yang sebenarnya ada di pool V3 2025-11-04 — di luar cakupan tugas ini (tugas menetapkan pair V2 sebagai definisi pembeli).

## Beat — pair V2-WBNB (tasked)

- Token (CA persis dari tugas): 0xcf3232b85b43bca90e51d38cc06cc8bb8c8a3e36 — 18 desimal. MCap tugas: ~$37,1 juta.
- Pair PCS V2 (factory getPair token,WBNB): 0x35b240d7f4b99d1d5870b1b7b27dfd6681449614. PairCreated: blok 69396703, 2025-11-25 12:34:58 WIB, tx 0xfb9d547dcb393672340361fe56ce75ab8a17b48ab401f31ab4975f890dab519f.
- Status pasar-pertama: BUKAN. Pool terawal GeckoTerminal: Beat / USDT 0.007% dibuat 2025-10-31T09:06:14Z — 25 hari SEBELUM pair V2-WBNB dibuat. Pair V2 lain: Beat/USDT 0x7f59e7a917c06d68d8ef15f3e8605b7c6299e27d dibuat 2026-01-04 (juga setelah pool pertama).
- Pindai log pair: blok 69396703 s.d. 73396702 (400 chunk × 10.000 blok; split tidak terpicu). Log Transfer pair→ yang ditemukan dalam pindaian: 1.560 (termasuk log di luar jendela 6 jam pembeli ke-30, karena pemeriksaan stop per batch 200 chunk); pembeli distinct dalam pindaian: 97 (hanya dalam rentang pindai, bukan total pembeli token). Tabel di bawah = 30 pembeli pertama kronologis.
- Pembeli pair pertama: blok 69401200 — 2025-11-25 13:31:10 WIB. Pembeli ke-30: blok 71969064 — 2025-12-17 20:39:21 WIB. Jadi 30 pembeli pertama pair ini tersebar selama ~22 hari (pair sangat sepi), bukan dalam hitungan detik seperti peluncuran pada umumnya. Dari 30 baris: 26 kontrak, 4 EOA; HOLD 7, PARTIAL 2, SOLD 21.

| # | Wallet (lengkap) | Beli pertama (blok — WIB) | Beli awal 6j | Saldo sekarang | % dipegang | Status | Jual ke pair ≤1j | Catatan |
|---|---|---|---|---|---|---|---|---|
| 1 | `0x2ea94a042461940fb59cc7260bb85342891fb5eb` | 69401200 — 2025-11-25 13:31:10 WIB | 0.33 | 0.00 | 0.36% | SOLD | 0.00% (0.00) | CORET: kontrak/bot executor |
| 2 | `0x40537c0e3362f1fa041b78a840ed987d9869ee49` | 69402518 — 2025-11-25 13:47:39 WIB | 99.55 | 0.53 | 0.54% | PARTIAL | 0.00% (0.00) | bersih dalam cakupan cek ini (EOA, bukan daftar coret, pegang >0,5%) |
| 3 | `0x85822c78bafe85fd0807dd3ccf55290ebbaf90c0` | 69402519 — 2025-11-25 13:47:40 WIB | 0.00 | 0.00 | 0.00% | SOLD | 100.00% (0.00) | catatan: fast dump ≤1j 100.00% |
| 4 | `0x8737a10d9c19af8bb2eae0b5e9cfe7b7276e0638` | 69402519 — 2025-11-25 13:47:40 WIB | 0.01 | 0.02 | 132.51% | HOLD | 0.00% (0.00) | CORET: kontrak/bot executor |
| 5 | `0x426603bac5e0ea73fd13aecad7a80c9f963f6eac` | 69402521 — 2025-11-25 13:47:41 WIB | 0.00 | 0.17 | 16872.92% | HOLD | 0.00% (0.00) | CORET: kontrak/bot executor |
| 6 | `0x173e6f719b1deb322f349f87f993c67ecfd21835` | 69402552 — 2025-11-25 13:48:04 WIB | 0.00 | 0.00 | 100.00% | HOLD | 0.00% (0.00) | CORET: kontrak/bot executor |
| 7 | `0x9418d0025f75201fc74f159e0c9b705156a1983e` | 69502715 — 2025-11-26 10:40:09 WIB | 0.30 | 0.00 | 0.00% | SOLD | 0.00% (0.00) | CORET: kontrak/bot executor |
| 8 | `0xea56b9b9716e9f28b969c1308da46fc3331438b0` | 69682919 — 2025-11-28 00:14:29 WIB | 51.56 | 0.00 | 0.00% | SOLD | 0.00% (0.00) | CORET: kontrak/bot executor |
| 9 | `0xb5cb0555942cb5b5555f7b87fb605db2f86818a9` | 69682921 — 2025-11-28 00:14:30 WIB | 0.00 | 0.00 | 0.00% | SOLD | 0.00% (0.00) | CORET: kontrak/bot executor |
| 10 | `0x0b04d2eb5da34d118d8b5c31cef911b67d806c88` | 69683698 — 2025-11-28 00:24:13 WIB | 51.53 | 0.00 | 0.00% | SOLD | 0.00% (0.00) | CORET: kontrak/bot executor |
| 11 | `0x927f64c33f48de56577fb08c87b58c66a038f53e` | 69688517 — 2025-11-28 01:24:27 WIB | 100.27 | 0.00 | 0.00% | SOLD | 0.00% (0.00) | CORET: kontrak/bot executor |
| 12 | `0x33c37cd8b78c521d21b17db4d52a016e963c0e41` | 69689878 — 2025-11-28 01:41:28 WIB | 50.24 | 0.01 | 0.01% | SOLD | 0.00% (0.00) | CORET: kontrak/bot executor |
| 13 | `0xa68e2ddbfe9dce42d4f9e61c13ee404ed7979770` | 70721917 — 2025-12-07 00:45:22 WIB | 0.00 | 0.00 | 186.08% | HOLD | 0.00% (0.00) | bersih dalam cakupan cek ini (EOA, bukan daftar coret, pegang >0,5%) saldo > beli awal → akumulasi/transfer masuk lanjutan |
| 14 | `0x4f9308463e8694d311ce287b43ec1c1b75d49e3d` | 70812492 — 2025-12-07 19:37:44 WIB | 0.00 | 0.00 | 100.00% | HOLD | 0.00% (0.00) | CORET: kontrak/bot executor |
| 15 | `0xeb36184afa41db2fde6a7d5e4fef37c27c79fe6c` | 71041104 — 2025-12-09 19:15:38 WIB | 0.00 | 0.00 | 0.00% | SOLD | 0.00% (0.00) | CORET: kontrak/bot executor |
| 16 | `0xb80ccaa913d36757fe7b6251333113e650a11867` | 71100517 — 2025-12-10 07:38:20 WIB | 0.00 | 0.00 | 0.00% | SOLD | 0.00% (0.00) | CORET: kontrak/bot executor |
| 17 | `0xf4ba66394f00aa68af4c2de2cd4d0ea2b7615816` | 71169418 — 2025-12-10 21:59:38 WIB | 0.00 | 0.00 | 0.00% | SOLD | 0.00% (0.00) | CORET: kontrak/bot executor |
| 18 | `0x40d28781302172e131d35031a485895800c03866` | 71424919 — 2025-12-13 03:14:41 WIB | 0.00 | 0.00 | 0.00% | SOLD | 0.00% (0.00) | CORET: kontrak/bot executor |
| 19 | `0x0ebb1e9985501f244363dd01c744f6232a2a698b` | 71443608 — 2025-12-13 07:08:17 WIB | 0.00 | 0.00 | 0.00% | SOLD | 0.00% (0.00) | CORET: kontrak/bot executor |
| 20 | `0xe5f1395efce39a2ac238b63f79dbc5d524c85dcc` | 71463383 — 2025-12-13 11:15:30 WIB | 0.01 | 310,511.23 | 4774986288.11% | HOLD | 0.00% (0.00) | CORET: pool lain — pool Beat/USDT (terkonfirmasi on-chain token0=USDT, token1=Beat; ID pool GeckoTerminal Beat/USDT 1%, dibuat 2025-11-01T07:33:16Z) |
| 21 | `0xf5647a353608b4f5496da27ac0165f335bacada7` | 71628997 — 2025-12-14 21:45:47 WIB | 0.00 | 0.00 | 0.00% | SOLD | 0.00% (0.00) | CORET: kontrak/bot executor |
| 22 | `0x687b1d4a9070f40c3540aac46a7478759ac391b9` | 71717210 — 2025-12-15 16:09:47 WIB | 0.00 | 0.00 | 0.00% | SOLD | 0.00% (0.00) |  |
| 23 | `0xb4c3277ccad9a74ae7fbcb1688367c2ef73b2786` | 71717211 — 2025-12-15 16:09:48 WIB | 0.00 | 0.13 | 35973.60% | HOLD | 0.00% (0.00) | CORET: kontrak/bot executor |
| 24 | `0x000000000000fb06f868b46876350c37f5c86610` | 71717607 — 2025-12-15 16:14:45 WIB | 0.00 | 0.00 | 0.00% | SOLD | 0.00% (0.00) | CORET: kontrak/bot executor |
| 25 | `0x57c2a7aefb6e21a745ec579a1e585da8352a3cf6` | 71870682 — 2025-12-17 00:08:21 WIB | 0.00 | 0.00 | 0.00% | SOLD | 0.00% (0.00) | CORET: kontrak/bot executor |
| 26 | `0x452244f592eff4cde9deaeb8907bca9b64c44947` | 71937163 — 2025-12-17 13:59:22 WIB | 0.03 | 0.00 | 0.00% | SOLD | 0.00% (0.00) | CORET: kontrak/bot executor |
| 27 | `0xa01cd5b68265b972b73a713f6d824d1a6d3612b0` | 71941852 — 2025-12-17 14:58:00 WIB | 0.07 | 0.00 | 0.00% | SOLD | 0.00% (0.00) | CORET: kontrak/bot executor |
| 28 | `0x9999b0cdd35d7f3b281ba02efc0d228486940515` | 71943876 — 2025-12-17 15:23:18 WIB | 0.08 | 0.00 | 0.65% | PARTIAL | 0.00% (0.00) | CORET: kontrak/bot executor |
| 29 | `0x77519fa2324078e75b43c1bf2f8681069100c6c0` | 71952931 — 2025-12-17 17:16:33 WIB | 0.06 | 0.00 | 0.00% | SOLD | 0.00% (0.00) | CORET: kontrak/bot executor |
| 30 | `0xd48648d2c58117d3e82fdb74a557498952181e36` | 71969064 — 2025-12-17 20:39:21 WIB | 0.02 | 0.00 | 0.00% | SOLD | 0.00% (0.00) | CORET: kontrak/bot executor |

- Daftar coret Beat: 26 kontrak/bot executor (semua baris dengan EOA/kontrak = kontrak, termasuk Beat #20 pool Beat/USDT) + 0 dari daftar coret bernama (sniper/funder/trio/dll nihil). Beat #20 dicoret sebagai pool lain, BUKAN sebagai bot executor semata — ia adalah pool Beat/USDT yang bertransaksi di pair V2-WBNB.
- Daftar bersih Beat (EOA + bukan coret + pegang >0,5%):
  1. Beat #2 `0x40537c0e3362f1fa041b78a840ed987d9869ee49` — PARTIAL tipis (sedikit di atas ambang debu 0,5%; angka persis di tabel), jual ≤1j 0%. EOA, tanpa flag tumpang tindih. Catatan: pegangan nyaris habis — ini BUKAN holder kuat.
  2. Beat #13 `0xa68e2ddbfe9dce42d4f9e61c13ee404ed7979770` — HOLD 186,14% (saldo jauh di atas beli awal 6 jam → sebagian besar saldo sekarang berasal dari akumulasi/transfer masuk lanjutan, bukan posisi awal murni), jual ≤1j 0%. EOA, tanpa flag tumpang tindih.
- EOA Beat lainnya (bukan bersih karena SOLD): 2 wallet EOA dengan saldo ≤0,5% — lihat tabel (baris EOA berstatus SOLD).

## LAB — pair V2-WBNB (tasked) — HANYA 17 PEMBELI

- Token (CA persis dari tugas): 0x7ec43cf65f1663f820427c62a5780b8f2e25593a — 18 desimal. MCap tugas: ~$33,8 juta.
- Pair PCS V2 (factory getPair token,WBNB): 0x5d43403cc3869ee31989504b8eb93cd3c2d4cb9f. PairCreated: blok 120327737, 2026-09-06 22:37:32 WIB, tx 0xeee09a6cef56fc5a268a07fd9dafca4d0b012dc66a78ca34dd7ac6640b937bd4.
- Status pasar-pertama: BUKAN — dengan jarak yang sangat besar. Pool terawal GeckoTerminal: LAB / USDT 0.007% dibuat 2025-10-13T09:20:50Z — hampir 11 bulan SEBELUM pair V2-WBNB dibuat (2026-09-06). Pair V2 lain: LAB/USDT 0x236d5e1fbe5c037fe409a239363dd04eac60846c dibuat 2026-04-26 (juga setelah pool pertama, sebelum pair WBNB). Pair V2-WBNB LAB ini adalah pair yang dibuat belakangan, bukan venue peluncuran.
- Pindai log pair: blok 120327737 s.d. 131231846 (1.091 chunk × 10.000 blok, sampai blok terbaru yang dipakai; split tidak terpicu). Log Transfer pair→ yang ditemukan: 45; pembeli distinct: HANYA 17. Pair ini tidak pernah mencapai 30 pembeli distinct sampai blok terbaru yang dipindai — jadi tabel di bawah berisi 17 baris, bukan 30, dan itu adalah FAKTA pindai, bukan kekurangan data yang boleh ditambal dari pair lain.
- Pembeli pair pertama: blok 120860954 — 2026-09-09 17:18:37 WIB. Pembeli terakhir yang ditemukan (ke-17): blok 129396422 — 2026-10-24 04:47:21 WIB. Dari 17 baris: 13 kontrak, 4 EOA; HOLD 8, PARTIAL 0, SOLD 9.

| # | Wallet (lengkap) | Beli pertama (blok — WIB) | Beli awal 6j | Saldo sekarang | % dipegang | Status | Jual ke pair ≤1j | Catatan |
|---|---|---|---|---|---|---|---|---|
| 1 | `0x238a358808379702088667322f80ac48bad5e6c4` | 120860954 — 2026-09-09 17:18:37 WIB | 0.01 | 9,261,309.57 | 68377366483.65% | HOLD | 0.00% (0.00) | CORET: kontrak/bot executor |
| 2 | `0x3679fcb44596729a9bd52f4f3e6f735020a7a346` | 121310295 — 2026-09-12 01:31:00 WIB | 0.08 | 210,615.48 | 274208469.69% | HOLD | 0.00% (0.00) | CORET: pool lain — pool LAB/WBNB (terkonfirmasi on-chain token0=LAB, token1=WBNB; ID pool GeckoTerminal LAB/WBNB 1%, dibuat 2025-10-14T10:39:47Z) |
| 3 | `0x6b35e4c1a8a2a126d46f2b9755d02736baf04933` | 121358329 — 2026-09-12 07:31:20 WIB | 0.39 | 0.00 | 0.00% | SOLD | 100.00% (0.39) | catatan: fast dump ≤1j 100.00% |
| 4 | `0x09768173d795a0ad6c959a59dd9d7ef930aeeabd` | 121359571 — 2026-09-12 07:40:39 WIB | 0.39 | 817.71 | 209565.79% | HOLD | 0.00% (0.00) | CORET: pool lain — pool LAB/WBNB (terkonfirmasi on-chain token0=LAB, token1=WBNB; ID pool GeckoTerminal LAB/WBNB 0.3%, dibuat 2026-07-08T20:07:32Z) |
| 5 | `0x381083f4f854191d96547b74d1b3cfc1818d5373` | 121553674 — 2026-09-13 07:57:05 WIB | 0.01 | 0.01 | 244.80% | HOLD | 0.00% (0.00) | CORET: kontrak/bot executor |
| 6 | `0x9c7047e96edc79885b03f872ef9a7e3fb327c7db` | 121647101 — 2026-09-13 19:38:03 WIB | 0.40 | 0.00 | 0.00% | SOLD | 100.00% (0.40) | catatan: fast dump ≤1j 100.00% |
| 7 | `0x236d5e1fbe5c037fe409a239363dd04eac60846c` | 121647155 — 2026-09-13 19:38:27 WIB | 0.13 | 0.00 | 0.00% | SOLD | 0.00% (0.00) | CORET: pool/pair lain — pair PCS V2 LAB/USDT 0x236d5e1fbe5c037fe409a239363dd04eac60846c (terverifikasi lewat factory getPair) |
| 8 | `0x81cc18c087b4a0e43dadcd60ddf274869d8f2164` | 121647195 — 2026-09-13 19:38:45 WIB | 0.07 | 29.52 | 42204.84% | HOLD | 0.00% (0.00) | CORET: kontrak/bot executor |
| 9 | `0xb585639ff3d61de1187d960cc18924d033f2768f` | 121738632 — 2026-09-14 07:04:47 WIB | 1,957.25 | 0.00 | 0.00% | SOLD | 0.00% (0.00) | CORET: kontrak/bot executor |
| 10 | `0x9999b0cdd35d7f3b281ba02efc0d228486940515` | 122194388 — 2026-09-16 16:04:20 WIB | 230.40 | 0.00 | 0.00% | SOLD | 0.00% (0.00) | CORET: kontrak/bot executor |
| 11 | `0x55367cc72a98f452ed4f28834a038e97575d9ade` | 122547454 — 2026-09-18 12:13:34 WIB | 0.46 | 0.46 | 100.00% | HOLD | 0.00% (0.00) | CORET: kontrak/bot executor |
| 12 | `0x0000000000367715a1c746bd336b65e5954c7660` | 122547456 — 2026-09-18 12:13:35 WIB | 0.00 | 0.00 | 0.00% | SOLD | 0.00% (0.00) | CORET: kontrak/bot executor |
| 13 | `0xba9ddc447285c6460f001dc983c5ed7b46a18428` | 123547468 — 2026-09-23 17:16:18 WIB | 0.03 | 0.00 | 0.00% | SOLD | 0.00% (0.00) | CORET: kontrak/bot executor |
| 14 | `0x220794f72f4b079a1d32469a3dffeda26b8651d8` | 127571783 — 2026-10-14 16:36:31 WIB | 0.17 | 0.45 | 258.62% | HOLD | 0.00% (0.00) | CORET: kontrak/bot executor |
| 15 | `0xe92e84af6e2f80794c825ab01ab70a895cf8443f` | 128527292 — 2026-10-19 16:06:10 WIB | 0.12 | 0.12 | 100.00% | HOLD | 0.00% (0.00) | bersih dalam cakupan cek ini (EOA, bukan daftar coret, pegang >0,5%) |
| 16 | `0xd66829e7288159010ad5b90e8f85c25192ca671f` | 128897441 — 2026-10-21 14:23:37 WIB | 0.00 | 0.00 | 0.00% | SOLD | 100.00% (0.00) | catatan: fast dump ≤1j 100.00% |
| 17 | `0x6ff74903bbe5e885ce071926f9921b2d93e860f7` | 129396422 — 2026-10-24 04:47:21 WIB | 0.00 | 0.00 | 0.00% | SOLD | 0.00% (0.00) | CORET: kontrak/bot executor |

- Daftar coret LAB: 13 kontrak/bot executor, termasuk LAB #2 (pool LAB/WBNB), LAB #4 (pool LAB/WBNB), dan LAB #7 (pair PCS V2 LAB/USDT 0x236d5e1fbe5c037fe409a239363dd04eac60846c — pair lain yang 'membeli' di pair WBNB). 0 dari daftar coret bernama.
- Daftar bersih LAB (EOA + bukan coret + pegang >0,5%): hanya 1 wallet:
  1. LAB #15 `0xe92e84af6e2f80794c825ab01ab70a895cf8443f` — HOLD 100,00%, jual ≤1j 0%. EOA, tanpa flag tumpang tindih. Satu-satunya holder bersih di pair ini.
- EOA LAB lainnya (bukan bersih karena SOLD): 3 wallet EOA berstatus SOLD — lihat tabel.

## DEBIT (Teller) — GAGAL TOTAL untuk pindai V2

- Token (CA persis dari tugas): 0x66661c7229901f568f16bd1551b3ba826f83ce49 — 18 desimal. MCap tugas: ~$24,1 juta.
- Verifikasi pair V2 lewat factory `getPair`: (token, WBNB) = nol, (token, USDT) = nol, (token, USDC) = nol. Log `PairCreated` factory untuk pasangan WBNB, USDT, dan USDC: masing-masing 0 log. Kesimpulan: TIDAK ADA pair PCS V2 untuk DEBIT dengan quote WBNB/USDT/USDC.
- Status pasar-pertama: pair V2 tidak ada. Pool terawal GeckoTerminal: DEBIT / USDT 0.007% dibuat 2026-08-24T12:56:22Z (pool V3 ber-fee tier).
- Hasil: TIDAK ADA tabel first-30 untuk DEBIT. Pembeli pertama DEBIT yang sebenarnya ada di pool V3 2026-08-24 — di luar cakupan tugas ini.

## ARIA — pair V2-USDT (PELENGKAP, bukan tasked WBNB)

- Token (CA persis dari tugas): 0x5d3a12c42e5372b2cc3264ab3cdcf660a1555238 — 18 desimal. MCap tugas: ~$23,3 juta.
- Pair V2-WBNB (tasked): TIDAK ADA — factory `getPair` (token, WBNB) = nol dan log `PairCreated` WBNB = 0 log. Sebagai pelengkap yang diberi label jelas (BUKAN pengganti definisi tugas), dipindai pair V2 lain yang terverifikasi: V2-USDT 0xbe9b3c913edd6b92cdb987510d1553d066a9e83e (factory getPair token,USDT). PairCreated V2-USDT: blok 59638540, 2025-09-01 18:49:33 WIB, tx 0x8be9d73668e1513c907b7cbd997b1f2eb2a9e880533df712757583041acd2b97.
- Status pasar-pertama: BUKAN. Pool terawal GeckoTerminal: ARIA / USDT 0.01% dibuat 2025-08-19T09:07:05Z — 13 hari SEBELUM pair V2-USDT dibuat. Jadi tabel ARIA di bawah pun BUKAN pembeli peluncuran.
- Pindai log pair: blok 59638540 s.d. 91638539 (3.200 chunk × 10.000 blok; split tidak terpicu). Log Transfer pair→ yang ditemukan dalam pindaian: 104; pembeli distinct dalam pindaian: 32 (hanya dalam rentang pindai). Tabel di bawah = 30 pembeli pertama kronologis.
- Pembeli pair pertama: blok 59641027 — 2025-09-01 19:20:38 WIB (catatan: pembeli pertama ini adalah pool ARIA/USDT lain — lihat coret). Pembeli ke-30: blok 89840106 — 2026-04-01 00:14:44 WIB. Jadi 30 pembeli pertama pair ini tersebar selama ~7 bulan. Dari 30 baris: 26 kontrak, 4 EOA; HOLD 9, PARTIAL 1, SOLD 20.

| # | Wallet (lengkap) | Beli pertama (blok — WIB) | Beli awal 6j | Saldo sekarang | % dipegang | Status | Jual ke pair ≤1j | Catatan |
|---|---|---|---|---|---|---|---|---|
| 1 | `0xa5dbeaf16fc031eae92175974f8d0a439be4ad17` | 59641027 — 2025-09-01 19:20:38 WIB | 36.63 | 3,961,724.01 | 10815254.45% | HOLD | 0.00% (0.00) | CORET: pool lain — pool ARIA/USDT (terkonfirmasi on-chain token0=USDT, token1=ARIA; ID pool GeckoTerminal ARIA/USDT 0.01%, dibuat 2025-08-19T09:07:05Z — pool terawal ARIA) |
| 2 | `0x2ea94a042461940fb59cc7260bb85342891fb5eb` | 59641110 — 2025-09-01 19:21:40 WIB | 8.92 | 0.01 | 0.09% | SOLD | 0.00% (0.00) | CORET: kontrak/bot executor |
| 3 | `0xb5cb05550357a4ac6c095d96a19bce513ba5ac04` | 59645707 — 2025-09-01 20:19:08 WIB | 9.58 | 0.00 | 0.00% | SOLD | 0.00% (0.00) | CORET: kontrak/bot executor |
| 4 | `0x19accfce512408755cd0d0e0f6c2b2254cee49b7` | 59647264 — 2025-09-01 20:38:36 WIB | 5,711.12 | 0.00 | 0.00% | SOLD | 0.00% (0.00) | CORET: kontrak/bot executor |
| 5 | `0x814d08d784b8c3e8ecaf478f92c7d2fe0f482a5a` | 59647306 — 2025-09-01 20:39:07 WIB | 3,120.83 | 0.00 | 0.00% | SOLD | 0.00% (0.00) | CORET: kontrak/bot executor |
| 6 | `0x426603bac5e0ea73fd13aecad7a80c9f963f6eac` | 59647308 — 2025-09-01 20:39:09 WIB | 0.01 | 0.07 | 607.37% | HOLD | 0.00% (0.00) | CORET: kontrak/bot executor |
| 7 | `0xb21a7d6b07ad608202c5c057031a034bf4166b38` | 59647321 — 2025-09-01 20:39:18 WIB | 0.03 | 0.09 | 340.42% | HOLD | 0.00% (0.00) | CORET: kontrak/bot executor |
| 8 | `0x60aecaf099040486763e7a87374bebc104f55617` | 59660694 — 2025-09-01 23:26:29 WIB | 0.00 | 0.00 | 0.00% | SOLD | 0.00% (0.00) | CORET: kontrak/bot executor |
| 9 | `0xef7a7efed84809fe4395be8b36eacd682e862d44` | 59865022 — 2025-09-03 18:00:50 WIB | 0.01 | 5.75 | 39843.82% | HOLD | 0.00% (0.00) | CORET: kontrak/bot executor |
| 10 | `0x38fd39dce70c83a05f6d4de08e6ec56f732f4b09` | 60899076 — 2025-09-12 17:29:42 WIB | 0.01 | 0.00 | 0.00% | SOLD | 0.00% (0.00) | CORET: kontrak/bot executor |
| 11 | `0xdf82debfd3304e33979b4d790aaaf89eb70c8ff0` | 66518304 — 2025-10-31 12:47:12 WIB | 0.00 | 0.00 | 0.00% | SOLD | 0.00% (0.00) | CORET: kontrak/bot executor |
| 12 | `0xe495450a331d06c3fd6173184c0cb4e671a40b11` | 68153843 — 2025-11-14 17:34:27 WIB | 0.00 | 0.00 | 0.00% | SOLD | 0.00% (0.00) | CORET: kontrak/bot executor |
| 13 | `0x840574b48eb11261bb000e36da5b63fbf7163376` | 68410000 — 2025-11-16 22:56:42 WIB | 0.02 | 0.00 | 0.00% | SOLD | 0.00% (0.00) |  |
| 14 | `0x000000000000fb06f868b46876350c37f5c86610` | 68410000 — 2025-11-16 22:56:42 WIB | 1.96 | 0.00 | 0.00% | SOLD | 0.00% (0.00) | CORET: kontrak/bot executor |
| 15 | `0xb4c3277ccad9a74ae7fbcb1688367c2ef73b2786` | 68410001 — 2025-11-16 22:56:42 WIB | 0.01 | 0.40 | 2740.92% | HOLD | 0.00% (0.00) | CORET: kontrak/bot executor |
| 16 | `0x8737a10d9c19af8bb2eae0b5e9cfe7b7276e0638` | 68410001 — 2025-11-16 22:56:42 WIB | 0.03 | 0.35 | 1155.18% | HOLD | 0.00% (0.00) | CORET: kontrak/bot executor |
| 17 | `0xf5647a353608b4f5496da27ac0165f335bacada7` | 73253941 — 2025-12-29 00:23:12 WIB | 0.00 | 0.00 | 0.00% | SOLD | 0.00% (0.00) | CORET: kontrak/bot executor |
| 18 | `0x790a58f7bf9e4d0576618d6002139079fe142346` | 73253942 — 2025-12-29 00:23:13 WIB | 0.03 | 0.03 | 100.00% | HOLD | 0.00% (0.00) | bersih dalam cakupan cek ini (EOA, bukan daftar coret, pegang >0,5%) |
| 19 | `0x606f715327eca4d3952687f2bd77ae6a0ba455cb` | 74930585 — 2026-01-12 13:44:43 WIB | 0.02 | 0.00 | 0.00% | SOLD | 100.00% (0.02) | catatan: fast dump ≤1j 100.00% |
| 20 | `0x9f21a3ea051fef7934b76e9162ef62eb920369f4` | 85794730 — 2026-03-10 21:43:29 WIB | 0.02 | 0.00 | 0.00% | SOLD | 10.00% (0.00) | CORET: kontrak/bot executor |
| 21 | `0xb14ac40b0f85621631f61612abc31631c7c0e749` | 86138424 — 2026-03-12 16:42:02 WIB | 0.04 | 0.00 | 0.00% | SOLD | 0.00% (0.00) | CORET: kontrak/bot executor |
| 22 | `0xb5cb0555942cb5b5555f7b87fb605db2f86818a9` | 86144587 — 2026-03-12 17:28:17 WIB | 0.00 | 0.00 | 0.00% | SOLD | 0.00% (0.00) | CORET: kontrak/bot executor |
| 23 | `0x93b4150114fd96377feab30fd4597405b9f0ce33` | 86144611 — 2026-03-12 17:28:28 WIB | 0.02 | 0.00 | 0.00% | SOLD | 0.00% (0.00) | CORET: kontrak/bot executor |
| 24 | `0xd48648d2c58117d3e82fdb74a557498952181e36` | 86144612 — 2026-03-12 17:28:28 WIB | 0.06 | 0.00 | 1.44% | PARTIAL | 0.00% (0.00) | CORET: kontrak/bot executor |
| 25 | `0xc10ee9031f2a0b84766a86b55a8d90f357910fb4` | 87005163 — 2026-03-17 05:21:19 WIB | 0.00 | 0.00 | 0.00% | SOLD | 0.00% (0.00) | CORET: kontrak/bot executor |
| 26 | `0xb80ccaa913d36757fe7b6251333113e650a11867` | 88022821 — 2026-03-22 12:54:54 WIB | 0.00 | 0.00 | 0.00% | SOLD | 0.00% (0.00) | CORET: kontrak/bot executor |
| 27 | `0xb5cb0550811d3ded8203b64a51b8c6781644df4e` | 88022905 — 2026-03-22 12:55:32 WIB | 0.00 | 0.00 | 0.00% | SOLD | 0.00% (0.00) | CORET: kontrak/bot executor |
| 28 | `0xf55416ef2afc34360d12cd952bde8eb9a14461c8` | 88122742 — 2026-03-23 01:24:48 WIB | 0.00 | 0.00 | 100.00% | HOLD | 0.00% (0.00) | CORET: kontrak/bot executor |
| 29 | `0x0930139b38f3f2945419f1ee30ae2bdf42094c62` | 88457611 — 2026-03-24 19:17:44 WIB | 0.00 | 0.00 | 93.91% | HOLD | 0.00% (0.00) | bersih dalam cakupan cek ini (EOA, bukan daftar coret, pegang >0,5%) |
| 30 | `0x6cd7aaa1987a4677488f7a6459f13629928e48f8` | 89840106 — 2026-04-01 00:14:44 WIB | 0.00 | 0.00 | 0.00% | SOLD | 16.21% (0.00) | CORET: kontrak/bot executor |

- Daftar coret ARIA: 26 kontrak/bot executor, termasuk ARIA #1 (pool ARIA/USDT). 0 dari daftar coret bernama.
- Daftar bersih ARIA (EOA + bukan coret + pegang >0,5%):
  1. ARIA #18 `0x790a58f7bf9e4d0576618d6002139079fe142346` — HOLD 100,00%, jual ≤1j 0%. EOA, tanpa flag tumpang tindih.
  2. ARIA #29 `0x0930139b38f3f2945419f1ee30ae2bdf42094c62` — HOLD 93,90% (angka persis di tabel), jual ≤1j 0%. EOA, tanpa flag tumpang tindih.
- EOA ARIA lainnya (bukan bersih karena SOLD): 2 wallet EOA berstatus SOLD — lihat tabel.

## Tumpang tindih antar koin dalam dataset ini (linkage LEMAH saja)

Wallet yang sama muncul sebagai pembeli pair di ≥2 koin dari ketiga tabel di atas. Ini adalah co-buy — sinyal LEMAH, BUKAN bukti linkage KUAT, BUKAN bukti insider, dan BUKAN rekomendasi. Funding TIDAK dicek di sini.

- `0x000000000000fb06f868b46876350c37f5c86610` — Beat #24, ARIA #14 — kontrak di semua kemunculan.
- `0x2ea94a042461940fb59cc7260bb85342891fb5eb` — Beat #1, ARIA #2 — kontrak di semua kemunculan.
- `0x426603bac5e0ea73fd13aecad7a80c9f963f6eac` — Beat #5, ARIA #6 — kontrak di semua kemunculan.
- `0x8737a10d9c19af8bb2eae0b5e9cfe7b7276e0638` — Beat #4, ARIA #16 — kontrak di semua kemunculan.
- `0x9999b0cdd35d7f3b281ba02efc0d228486940515` — Beat #28, LAB #10 — kontrak di semua kemunculan.
- `0xb4c3277ccad9a74ae7fbcb1688367c2ef73b2786` — Beat #23, ARIA #15 — kontrak di semua kemunculan.
- `0xb5cb0555942cb5b5555f7b87fb605db2f86818a9` — Beat #9, ARIA #22 — kontrak di semua kemunculan.
- `0xb80ccaa913d36757fe7b6251333113e650a11867` — Beat #16, ARIA #26 — kontrak di semua kemunculan.
- `0xd48648d2c58117d3e82fdb74a557498952181e36` — Beat #30, ARIA #24 — kontrak di semua kemunculan.
- `0xf5647a353608b4f5496da27ac0165f335bacada7` — Beat #21, ARIA #17 — kontrak di semua kemunculan.

## Tumpang tindih dengan set terpantau & daftar coret bernama (exact-match)

- 50 wallet terpantau (tier-ab-watch-state.json: tier_a_private, tier_b_private, monitored_private_entities): NIHIL di ketiga tabel (0/77 baris). Semua baris yang tidak berflag pool adalah 'baru' dalam arti tidak terpantau — tetapi 'baru' di sini TIDAK berarti kandidat bagus: hampir semuanya kontrak atau SOLD.
- TRIO (0x38E4639C235d826a243f46e4BD8B5569636e1642, 0xA0B725C40b8353993a9501FCdE943C8445048344, 0x5816102760793e60ebd097c344b732b0537ccb59): NIHIL.
- PAIR: PAIR #2 (0x95e02ed458ba54fd640f5b3956ff4178aaC809d5): NIHIL. PAIR #1: TIDAK DAPAT DICEK — string yang diterima dalam tugas (`0x2fc2a32f16d683038187b87b87e0409d122da6f17d4`) berukuran 43 karakter heks, bukan alamat valid 40 karakter; string ini dikutip apa adanya sebagai bukti masukan yang bermasalah, BUKAN sebagai alamat, dan TIDAK ada alamat koreksi yang ditebak. Pengecekan exact-match PAIR #1 harus diulang oleh koordinator setelah alamat yang benar dikonfirmasi.
- IBS #2 (0xac739056e611d639abeb0b9a87da38bd297ba00e): NIHIL. BORT #8 (0xcd06af254d0da9dbf95f62a75361c4cab182f13b): NIHIL.
- Klaster GANG (0xf5c318532169bb28ea41f19fc54c224818cba3b7, 0xb756710f115e5e928f387ee13f5ace52ebc31c06, 0x66c60bdb0f4b510a444dbcd2d172e3978f63b4e1): NIHIL.
- Hub sniper 0xf5988713400da6fc8a58ec9515e2b0df9b40b115: NIHIL. Funder 0x318d2aae4c99c2e74f7b5949fa1c34df837789b8: NIHIL.
- Kontrak token MSX 0x23214ccbffb6ef479da64d1842b10b5525997777: NIHIL (daftar anggota klaster MSX tidak tersedia dalam tugas, jadi ini hanya pengecekan terhadap kontrak token itu sendiri).
- Wallet user (utama 0xeb237F6f9FB4e826739F0954e9768914F28b2c2E, kedua 0xcf3c6fc1bf670a8d3f03436395286f86dbee7418): NIHIL di ketiga tabel.
- Kontrak token itu sendiri sebagai pembeli: NIHIL di ketiga tabel (tidak ada token contract yang muncul sebagai penerima pair→).

## Semua gagal baca (tidak pernah ditulis sebagai nol/tidak ada)

1. `eth_call` historis (getPair pada nomor blok lama): GAGAL di semua endpoint dataseed dengan 'missing trie node' (termasuk untuk nomor blok terbaru yang ditulis eksplisit, bukan 'latest'). Dampak: blok creation pair TIDAK dicari lewat binary search getPair historis; sebagai gantinya dipakai log PairCreated Ankr yang terverifikasi (blok + timestamp + tx di atas).
2. Pass RPC pertama untuk `balanceOf` (77 wallet): SEMUA gagal — penyebabnya bug selector pada pass itu (hash keccak penuh 32 byte dipakai sebagai data, bukan 4 byte pertama). Pass retry dengan selector 4 byte yang benar (`balanceOf(address)`[:4] via eth_utils.keccak) memulihkan SEMUA 77 saldo (0 gagal tersisa). Saldo di tabel adalah hasil pass retry, BUKAN hasil pass pertama.
3. Satu batch `call_many` besar di awal (40 eth_call) sempat kena rate limit endpoint ('method eth_call in batch triggered rate limit', -32005) dan fallback race-nya timeout di semua endpoint. Dampak: tidak ada data yang dipakai dari percobaan itu; semua pembacaan berikutnya memakai batch kecil (≤8) atau rotasi endpoint tunggal dengan jeda. Juga: dua endpoint (bsc.drpc.org, bnb.api.onfinality.io) sempat menjawab HTTP 429 pada satu pemeriksaan diagnostik — pemeriksaan itu bukan sumber data tabel.
4. Pindai Ankr: tidak ada chunk yang gagal total. Satu pindai sekuensial awal (tanpa filter topik, chunk 10.000 blok token Beat) sempat mengembalikan tepat 1.000 log pada chunk pertama dan berjalan sangat lambat — pindai itu DIBATALKAN dan diganti pindai berfilter topik (pengirim=pair) sesuai definisi tugas; data final berasal dari pindai berfilter topik yang direplikasi (Beat/LAB/ARIA direplikasi dengan hasil yang konsisten: LAB 45 log/17 distinct pada kedua run; ARIA 104 log/32 distinct pada kedua run; Beat first-30 ditentukan oleh urutan (blok, logIndex) yang sama pada kedua run).
5. GeckoTerminal: endpoint pools hanya diambil 5 halaman pertama per token (Beat/LAB/DEBIT/ARIA masing-masing 100 pool pada batas itu; UAI 92 pool total). Bila ada pool yang lebih awal di luar 5 halaman pertama, status pasar-pertama di atas bisa berubah — tetapi untuk Beat/LAB/ARIA, pool terawal yang ditemukan SUDAH lebih awal dari creation pair V2, jadi verdict 'BUKAN pasar pertama' tidak bergantung pada kelengkapan halaman; untuk UAI/DEBIT, verdict 'tidak ada pair V2' berasal dari factory + PairCreated on-chain, bukan dari Gecko.
6. Tidak ada GAGAL BACA lain pada data final: header blok untuk semua blok yang masuk perhitungan (Beat 43 blok, ARIA 40 blok, LAB 25 blok) berhasil dibaca; 0 blok dengan mismatch antara timestamp Ankr dan timestamp header; `eth_getCode` berhasil untuk semua 77 baris; `balanceOf` final berhasil untuk semua 77 baris.
7. Kesalahan salin pada pass pengecekan pertama: alamat TRIO #2 sempat tersalin keliru (41 karakter heks) sehingga pengecekan exact-match pertamanya VOID. Setelah diperbaiki ke string tugas yang benar (0xA0B725C40b8353993a9501FCdE943C8445048344, 40 karakter) dan dicek ulang terhadap ke-67 wallet unik di tabel, hasilnya tetap NIHIL. Semua pengecekan bernama lainnya diulang dari string tugas dan hasilnya NIHIL, kecuali PAIR #1 (lihat §Tumpang tindih) yang memang tidak bisa dicek karena string masukannya sendiri tidak valid.

## Catatan untuk koordinator

- Daftar bersih FINAL dari pindai ini (untuk cek funding lanjutan oleh koordinator, BUKAN rekomendasi): Beat #2 `0x40537c0e3362f1fa041b78a840ed987d9869ee49` (PARTIAL tipis — lemah), Beat #13 `0xa68e2ddbfe9dce42d4f9e61c13ee404ed7979770` (HOLD dengan akumulasi lanjutan), LAB #15 `0xe92e84af6e2f80794c825ab01ab70a895cf8443f` (HOLD 100%), ARIA #18 `0x790a58f7bf9e4d0576618d6002139079fe142346` (HOLD 100%), ARIA #29 `0x0930139b38f3f2945419f1ee30ae2bdf42094c62` (HOLD 93,90%).
- PERINGATAN UTAMA: kelima wallet bersih ini adalah pembeli pertama PADA PAIR V2 YANG DIBUAT BELAKANGAN, bukan pembeli peluncuran token. Nilai mereka sebagai 'smart money' jauh lebih lemah daripada early buyer peluncuran — koordinator perlu menimbang apakah mereka layak masuk cek funding, atau apakah pindai peluncuran (pool V3 pertama) yang sebenarnya dibutuhkan untuk UAI/Beat/LAB/DEBIT/ARIA.
- UAI dan DEBIT TIDAK PUNYA pair V2 sama sekali: bila koordinator tetap membutuhkan first-30 untuk keduanya, definisi pair harus diubah (mis. pool V3 pertama) lewat tugas baru — bukan dengan memaksakan tabel V2.
- LAB V2-WBNB hanya punya 17 pembeli distinct sepanjang sejarahnya sampai blok 131.231.846: pair ini praktis mati sebagai venue. Jangan extrapolasi 'first-30 LAB' dari pair ini.
