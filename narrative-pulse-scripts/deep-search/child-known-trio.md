# Early Buyer — Known Trio (mubarak / SKYAI / EGL1)

- Laporan: subagent read-only, BSC saja, bagian EARLY BUYER untuk Modal Bacot (riset wallet dalam). 2 Nov 2026.
- TIDAK ADA state/feed/cron yang diubah, TIDAK ADA transaksi/approval/signing/login GMGN, TIDAK ADA seed phrase/private key yang diminta. Halaman profil GMGN tidak dipakai (login-gated).
- File ini berisi alamat LENGKAP. Tidak ada alamat terpotong yang dipakai sebagai data — semua alamat di bawah berasal dari log Ankr / hasil eth_call utuh.

## Verifikasi identitas on-chain (name()/symbol()/decimals()/totalSupply())

| Koin (label tugas) | Hasil on-chain | Kesimpulan |
|---|---|---|
| mubarak `0x5c85d6c6825ab4032337f11ee92a72df936b46f6` | name = `mubarak`, symbol = `mubarak`, 18 desimal, supply 1.000.000.000 | COCOK |
| SKYAI `0x92aa03137385f18539301349dcfc9ebc923ffb10` | name = `SKYAI`, symbol = `SKYAI`, 18 desimal, supply 1.000.000.000 | COCOK — label "INFERRED" kini TERVERIFIKASI, bukan lagi inferensi |
| EGL1 `0xf4b385849f2e817e92bffbfb9aeb48f950ff4444` | name = `EGL1`, symbol = `EGL1`, 18 desimal, supply 1.000.000.000 | COCOK (identitas token); status PROVISIONAL-nya soal MCAP, lihat di bawah |

Semua selector/calldata dihitung programatik dengan `eth_utils.keccak` (bukan hand-type), via `~/workspace/.abi-venv/bin/python`.

## Catatan EGL1 — konflik MCAP 10x (PROVISIONAL, apa yang dibaca)

GeckoTerminal 2 Nov 2026 memberi angka BERBEDA per pool untuk token EGL1 yang sama (likuiditas terfragmentasi, harga implisit berbeda per pool — bukan satu angka mcap tunggal):

| Pool EGL1 | pool_created_at | FDV (USD) | MCAP (USD) |
|---|---|---|---|
| V2 WBNB `0xd950a522e376adbe485c47eab244b9e13ca71f48` (pair tugas ini) | 2025-06-05T20:50:30Z | 3.597.716,78 | 3.447.352,81 |
| USD1 0,01% `0x6d76e7bb743fee795a2f00a317760acf822ee2be` | 2025-06-04T18:42:29Z | 9.520.003,60 | 9.111.214,26 |
| WBNB 1% `0x400b4c3295d52bef0757181f84224ed8b7b4f6ea` | 2025-06-05T20:34:56Z | 15.402.589,32 | 14.766.920,06 |

Rentang yang terbaca: ~3,45 jt–14,77 jt USD (rasio ~4,3x antar-pool, bukan 10x persis). Konflik 10x sebelumnya TIDAK dapat diputuskan dari data ini: tidak ada satu pun pool yang bisa dinyatakan "mcap yang benar" tanpa sumber sirkulasi resmi. Yang dipakai di laporan ini hanyalah pair V2, dan angka di atas dicatat apa adanya.

Konteks penting EGL1: pair V2 (5 Jun 2025) BUKAN pasar pertama EGL1 — pool USD1 sudah ada 4 Jun 2025 (~26 jam lebih awal). Jadi "early buyer" EGL1 di sini = early buyer PAIR V2, bukan buyer peluncuran absolut. Hal yang sama untuk mubarak: pool `0x90a54475d512b8f3852351611c38fad30a513491` sudah ada 13 Mar 2025 09:36:13Z, ~13,75 jam SEBELUM pair V2 (23:21:07Z). Hanya SKYAI yang pair V2-nya adalah pool terawal yang tercatat di GeckoTerminal (20 Apr 2025 03:42:03Z).

## Metode (on-chain saja)

1. Pair tiap token: `getPair(token, WBNB)` pada factory PCS V2 `0xca143ce32fe78f1f7019d7d551a6402fc5350c73`, dikonfirmasi silang dengan GeckoTerminal (alamat pool + `pool_created_at` cocok persis untuk ketiga pair).
2. Blok creation pair: event `PairCreated` factory via Ankr `getLogs` (topik terfilter). Waktu = timestamp HEADER BLOK (bukan inferensi dari selisih nomor blok).
3. Early buyer: log `Transfer` token dengan topik pengirim = alamat pair (pair -> buyer = beli), via Ankr sebagai MODULE (`~/workspace/custom-connectors/custom.ankr/bin/ankr.py`, `ankr_getLogs`, pageSize 1.000/page). Chunking: 200 blok/chunk untuk mubarak & SKYAI; EGL1 dilanjut 2.000 blok/chunk karena sepi. Tidak ada chunk yang mencapai 1.000 log (maksimum 539 log/chunk di SKYAI), jadi tidak ada pemotongan halaman yang terindikasi. Tidak ada token pagination dari Ankr yang teramati pada respons (hanya `logs` + `syncStatus`).
4. Saldo sekarang: `balanceOf` via `~/workspace/fast_exec/fast_rpc.py` (rotasi endpoint, bukan race — race sempat gagal karena bug calldata lokal, lihat bawah). Blok baca: 131.227.784.
5. Tipe wallet: `eth_getCode` sekarang (EOA vs KONTRAK). Catatan: code dibaca "sekarang", bukan pada saat beli — sebuah EOA saat beli bisa saja kini menjadi kontrak? Tidak: EOA tidak bisa berubah menjadi kontrak; sebaliknya kontrak yang terdeteksi sekarang sudah kontrak sejak dibuat. Jadi label KONTRAK aman, label EOA aman.
6. `% dipegang` = saldo sekarang / total beli di window scan. Bila >100%, artinya wallet itu membeli tambahan di luar window (bukan kesalahan hitung) — dicatat eksplisit.

## Koreksi/void yang wajib dicatat (kejujuran data)

- **Scan mubarak pertama VOID dan dibuang.** Blok creation mubarak sempat salah konversi manual dari heksadesimal (`0x2d3e8df` dibaca 47.478.591, padahal = 47.442.143). Scan dari blok yang salah itu (~30 jam setelah creation) SUDAH DIBUANG dan tidak dipakai sama sekali; scan yang dipakai di laporan ini dimulai ulang dari blok creation yang benar 47.442.143 (header 2025-03-13T23:21:07Z, cocok dengan GeckoTerminal). Blok SKYAI dan EGL1 tidak terkena kesalahan ini (dicetak sebagai integer oleh skrip, dan headernya cocok dengan GeckoTerminal).
- **Bug calldata lokal (diperbaiki sebelum hasil dipakai).** Dua skrip saldo awal memakai selector `balanceOf` yang salah (hash keccak penuh, bukan 4 byte pertama), sehingga semua `balanceOf` revert. Bug ditemukan lewat uji silang USDT/WBNB, diperbaiki (`keccak(...).hex()[:8]` = `0x70a08231`), dan SELURUH saldo dibaca ulang dengan calldata benar. Saldo di laporan ini berasal dari pembacaan ulang itu.
- **Rate limit (dihindari, bukan diterobos).** Selama pembacaan, `bsc-rpc.publicnode.com` dan `bnb.api.onfinality.io` sempat mengembalikan HTTP 429. Kedua endpoint itu TIDAK dipakai lagi dalam tugas ini; saldo dibaca lewat dataseed Binance/BNB Chain. Tidak ada retry membabi-buta terhadap endpoint yang me-rate-limit.
- **Batas metode Transfer (wajib dibaca).** Metode ini BUTA terhadap transfer BNB native dan call tanpa event — funding (siapa mendanai wallet) tidak terlihat dari log Transfer, sehingga linkage funding TIDAK dapat dinilai di sini. "Pair -> buyer" juga tidak membedakan beli swap vs penarikan likuiditas (remove liquidity juga mengirim token dari pair). Waktu JUAL tidak dihitung — hanya status akhir (saldo sekarang vs beli awal). "Proxy profit" (beli awal + jual/pegang) BUKAN PnL terealisasi: tidak ada histori harga di log, jadi TIDAK ADA klaim PnL 30 hari terverifikasi dalam laporan ini.

## Hasil filter BERSIH (coret, tapi tetap dicatat)

- **Hub funding sniper `0xf5988713400da6fc8a58ec9515e2b0df9b40b115` dan funder `0x318d2aae4c99c2e74f7b5949fa1c34df837789b8`**: TIDAK MUNCUL di daftar 25+25+14 manapun.
- **Wallet user (`0xeb237F6f9FB4e826739F0954e9768914F28b2c2E`, `0xcf3c6fc1bf670a8d3f03436395286f86dbee7418`)**: TIDAK MUNCUL — bukan kandidat, tidak ada flag yang perlu dibuat.
- **Kontrak/bot executor**: 13 dari 25 (mubarak), 2 dari 25 (SKYAI), 11 dari 14 (EGL1) — semuanya dicoret dari kandidat wallet bersih, tapi tetap tercantum lengkap di tabel dengan status hold/jualnya.
- **Pool lain yang ikut "membeli" dari pair V2**: mubarak `0x90a54475d512b8f3852351611c38fad30a513491` (pool mubarak lain, kini memegang 18.727.548,78 mubarak dari akumulasi lanjutan — BUKAN wallet) dan EGL1 `0x6d76e7bb743fee795a2f00a317760acf822ee2be` (pool USD1, kini memegang 23.589.368,69 EGL1 — BUKAN wallet). Keduanya dicoret.
- **Dump >=80% dalam ~1 jam di >=3 launch**: TIDAK DAPAT DIVERIFIKASI dari data ini (waktu jual tidak dihitung; hanya 3 launch dalam cakupan; tidak ada wallet yang muncul di ketiga launch). Satu-satunya wallet yang muncul di 2 dari 3 launch adalah kontrak `0xa01cd5b68265b972b73a713f6d824d1a6d3612b0` (mubarak + EGL1, saldo kini 0 di keduanya) — dicatat sebagai catatan, bukan disembunyikan, dan linkage-nya LEMAH.
- **Klaster insider MSX / exchange / wallet tim-vesting**: tidak ada yang teridentifikasi positif dari data ini. Klaster blok-0 SKYAI (di bawah) dicatat sebagai "perlu cek funding", BUKAN sebagai insider — kata "terbukti insider" TIDAK PERNAH dipakai.

## Linkage antar-koin (KUAT vs LEMAH)

- KUAT (shared funding/transfer langsung): TIDAK ADA yang ditemukan (metode Transfer buta terhadap funding BNB; tidak ada transfer langsung antar-buyer yang diperiksa).
- LEMAH (co-buy saja): SATU wallet — `0xa01cd5b68265b972b73a713f6d824d1a6d3612b0` (kontrak; early buyer mubarak blok 47.442.224 dan EGL1 blok 51.039.905; saldo kini 0 di keduanya). Co-buy saja, bukan bukti satu aktor yang sama.
- Selain itu: TIDAK ADA overlap antara daftar mubarak–SKYAI, maupun SKYAI–EGL1.

## Ringkasan kandidat (baca dulu — hasilnya keras)

**TIDAK ADA satu pun early buyer EOA yang masih memegang posisi berarti di ketiga koin ini.** Semua EOA di ketiga tabel kini bersaldo 0 (atau debu <1%): mubarak 12 EOA → semua 0; SKYAI 23 EOA → semua 0; EGL1 3 EOA → semua 0, dan ketiganya hanya membeli debu (1,14–2,49 token). Satu-satunya "HOLD" di tabel adalah pool/kontrak dengan akumulasi lanjutan, bukan wallet bersih. Ini wajar untuk launch Mar–Jun 2025 (8–19 bulan lalu): para early buyer sudah exit sejak lama. Jadi untuk pelacakan wallet ke depan, nilai laporan ini BUKAN "siapa masih hold", melainkan "siapa yang berperilaku sebagai early buyer" — dengan catatan perilaku itu saja, tanpa PnL terverifikasi, tidak cukup untuk promosi.

- **mubarak — kandidat perilaku terkuat (EOA, sudah exit semua):** `0xdc1afaedbf529d1bb0c65c982308ffd1e7df5570` adalah KONTRAK (coret). Di antara EOA, pembelian awal terbesar: `0x7627022104a71782abee28b24f2e5211bc925571` (34.005,36, blok 47.442.240), `0xbc5d0f53ee314f7e143a000ad73a1d5eb9ad8956` (26.078,46, blok 47.442.222), `0x52679d733a7d2c64bcda5494f46d6a39277e6d99` (59.951,99, blok 47.442.245 — terbesar EOA). Semuanya kini 0. **Dicoret:** semua 13 kontrak (termasuk pembeli terbesar 2.068.099,24 token, `0x00000060f4f81582668faee910080649438a7c31`) + pool `0x90a54475d512b8f3852351611c38fad30a513491`.
- **SKYAI — kandidat perilaku terkuat:** klaster blok-0, 6 wallet EOA terpisah (6 tx berbeda) yang mengambil ~162,42 juta token (~16,24% supply) tepat di blok creation 48.512.772: `0xa4e67515834e0e84a30907e379545cad5390a5bb` (86.788.881,58), `0x6c9a77850fda7db7c90c3ed708114e38a40c27b0` (34.225.030,58), `0xc87b8a3288eeb450045d215bacfd50527a4c4353` (18.320.460,99), `0x19f0446b17751b21f0ab12a3a2e719f534975c25` (11.420.214,59), `0xa7fdf94a1e267e0f24d1984e879d983cfd641612` (7.795.972,61), `0x2d33193e9a4eba762da54f074bf5e9ef810f9600` (3.872.858,71). Semuanya kini 0. Mereka BUKAN kandidat bersih (ukuran blok-0 + kecepatan = perlu cek funding sebelum dipakai; funding tidak tercakup metode ini). Early buyer EOA "normal" terbesar berikutnya: `0x8ec6e31f6a87368c4edb478ae8199b355606ff59` (1.006.591,40, blok 48.512.776, kini 0) dan `0xab23d58a050a85f91109ebbd1ac068b7c8dc72e2` (355.786,31, kini 0). **Dicoret:** 2 kontrak (`0xb5cb05554867ce201b0e6feb8d6cefd3a1dd5e32`, `0x4c6f6959f93b00cddab72c1644dd50133f82f1b9`).
- **EGL1 — praktis tidak ada kandidat:** hanya 14 buyer V2 dalam ~2 hari scan, 11 di antaranya kontrak, dan 10 dari 14 membeli <100 token (debu). Pembeli terbesar, `0x7035f2bfb370c740cdc60095c75966f04c47ddff` (11.600,87 token, kontrak, kini 0). Tiga EOA (`0xd9f39f0180b544b93da0ec4f27821f380983cb48`, `0xdb92120f4ee2636cd5a866eea06665d27563fd62`, `0x4f03478022cac2c1ef2fee4278a0b34d880cd13b`) hanya membeli 1,14–2,49 token dan kini 0. **Dicoret:** semua kontrak + pool USD1 `0x6d76e7bb743fee795a2f00a317760acf822ee2be`. Rekomendasi: early buyer EGL1 yang berarti harus dicari di pool USD1 (4 Jun), BUKAN di pair V2 — itu di luar cakupan tugas ini.


## mubarak

- Token: `0x5c85d6c6825ab4032337f11ee92a72df936b46f6` — on-chain `name()`/`symbol()` = `mubarak`, decimals 18, totalSupply 1.000.000.000 (dibaca via eth_call, selector dihitung programatik dari `eth_utils.keccak`).
- Pair PCS V2 (factory `0xca143ce32fe78f1f7019d7d551a6402fc5350c73`, `getPair` on-chain): `0xb7c6f7db26cde42550e4017bb9855bbaaa20eb44`
- Pair creation: blok 47.442.143, header blok 2025-03-13T23:21:07Z — sama persis dengan `pool_created_at` GeckoTerminal untuk pool ini.
- Window scan Ankr: 47.442.143–47.442.342 (1 chunk 200 blok). 73 log pair->buyer, 45 buyer distinct; tabel = 25 pertama. Tidak ada chunk yang menyentuh batas 1.000 log/page, jadi tidak ada indikasi pemotongan halaman.
- Definisi "beli awal" = jumlah Transfer token dari pair ke buyer di dalam window scan. Saldo sekarang dibaca di blok 131.227.784 (2 Nov 2026).
- Ambang "debu": sisa <1% dari beli awal (termasuk 0). Status: HOLD ≥50%, PARTIAL 1–<50%, DUST/EXIT <1%.

| # | Buyer (alamat lengkap) | Blok beli awal | Waktu beli awal (header blok) | Beli awal (token) | Saldo sekarang | % dipegang | Status | Tipe | Catatan kebersihan |
|---|---|---|---|---|---|---|---|---|---|
| 1 | `0x0000000d94514cbcf9455c0be85541e5d45cf1f5` | 47,442,149 | 2025-03-13 23:21:25 UTC | 1,318.14 | 0.00 | 0.0% | DUST/EXIT | KONTRAK | KONTRAK (eth_getCode sekarang) — coret dari kandidat wallet bersih; Sisa debu (<1% dari beli awal) |
| 2 | `0xd84129917fb529c9621364c6294cea6a4ce3e88d` | 47,442,167 | 2025-03-13 23:22:19 UTC | 9,707.85 | 0.00 | 0.0% | DUST/EXIT | EOA | Saldo sekarang 0 — sudah jual penuh (waktu jual tidak dihitung; metode Transfer tidak memberi histori harga) |
| 3 | `0xca29cd653f18c702156aaac27528dc5f4db1f2c4` | 47,442,189 | 2025-03-13 23:23:25 UTC | 1,474.60 | 0.00 | 0.0% | DUST/EXIT | KONTRAK | KONTRAK (eth_getCode sekarang) — coret dari kandidat wallet bersih; Saldo sekarang 0 — sudah jual penuh (waktu jual tidak dihitung; metode Transfer tidak memberi histori harga) |
| 4 | `0x4b5da7cb0bc003912380654170f7c4ded65e1ea8` | 47,442,191 | 2025-03-13 23:23:31 UTC | 9,113.47 | 0.00 | 0.0% | DUST/EXIT | EOA | Saldo sekarang 0 — sudah jual penuh (waktu jual tidak dihitung; metode Transfer tidak memberi histori harga) |
| 5 | `0x00000060f4f81582668faee910080649438a7c31` | 47,442,218 | 2025-03-13 23:24:52 UTC | 2,068,099.24 | 0.00 | 0.0% | DUST/EXIT | KONTRAK | KONTRAK (eth_getCode sekarang) — coret dari kandidat wallet bersih; Saldo sekarang 0 — sudah jual penuh (waktu jual tidak dihitung; metode Transfer tidak memberi histori harga) |
| 6 | `0x99a037a231b63f531b528361fae9dc5ecbc20312` | 47,442,221 | 2025-03-13 23:25:01 UTC | 15,719.49 | 0.00 | 0.0% | DUST/EXIT | EOA | Saldo sekarang 0 — sudah jual penuh (waktu jual tidak dihitung; metode Transfer tidak memberi histori harga) |
| 7 | `0x3f1f68c678e76c5999adbab76db8b9130d95f5af` | 47,442,221 | 2025-03-13 23:25:01 UTC | 735.30 | 0.00 | 0.0% | DUST/EXIT | EOA | Saldo sekarang 0 — sudah jual penuh (waktu jual tidak dihitung; metode Transfer tidak memberi histori harga) |
| 8 | `0xbc5d0f53ee314f7e143a000ad73a1d5eb9ad8956` | 47,442,222 | 2025-03-13 23:25:04 UTC | 26,078.46 | 0.00 | 0.0% | DUST/EXIT | EOA | Saldo sekarang 0 — sudah jual penuh (waktu jual tidak dihitung; metode Transfer tidak memberi histori harga) |
| 9 | `0xa01cd5b68265b972b73a713f6d824d1a6d3612b0` | 47,442,224 | 2025-03-13 23:25:10 UTC | 58,995.11 | 0.00 | 0.0% | DUST/EXIT | KONTRAK | Juga early buyer di koin lain trio ini (mubarak+EGL1) — linkage LEMAH (co-buy saja); KONTRAK (eth_getCode sekarang) — coret dari kandidat wallet bersih; Sisa debu (<1% dari beli awal) |
| 10 | `0x90a54475d512b8f3852351611c38fad30a513491` | 47,442,225 | 2025-03-13 23:25:13 UTC | 10,845.90 | 18,727,548.78 | 172,669.4% | HOLD* (>100%: akumulasi lanjutan) | KONTRAK | POOL mubarak lain (V3-style, GeckoTerminal 2025-03-13T09:36:13Z) — BUKAN wallet, coret |
| 11 | `0xb66ba3d7e42360ca225430ccc0ce706266380fee` | 47,442,226 | 2025-03-13 23:25:16 UTC | 57,198.45 | 0.00 | 0.0% | DUST/EXIT | KONTRAK | KONTRAK (eth_getCode sekarang) — coret dari kandidat wallet bersih; Saldo sekarang 0 — sudah jual penuh (waktu jual tidak dihitung; metode Transfer tidak memberi histori harga) |
| 12 | `0x7627022104a71782abee28b24f2e5211bc925571` | 47,442,240 | 2025-03-13 23:25:58 UTC | 34,005.36 | 0.00 | 0.0% | DUST/EXIT | EOA | Saldo sekarang 0 — sudah jual penuh (waktu jual tidak dihitung; metode Transfer tidak memberi histori harga) |
| 13 | `0xd035df6eedb7e7bc7be9766c6903070dac1e686b` | 47,442,243 | 2025-03-13 23:26:07 UTC | 2,721.43 | 0.00 | 0.0% | DUST/EXIT | KONTRAK | KONTRAK (eth_getCode sekarang) — coret dari kandidat wallet bersih; Saldo sekarang 0 — sudah jual penuh (waktu jual tidak dihitung; metode Transfer tidak memberi histori harga) |
| 14 | `0xdc1afaedbf529d1bb0c65c982308ffd1e7df5570` | 47,442,244 | 2025-03-13 23:26:10 UTC | 282,173.31 | 0.00 | 0.0% | DUST/EXIT | KONTRAK | KONTRAK (eth_getCode sekarang) — coret dari kandidat wallet bersih; Saldo sekarang 0 — sudah jual penuh (waktu jual tidak dihitung; metode Transfer tidak memberi histori harga) |
| 15 | `0x28e2ea090877bf75740558f6bfb36a5ffee9e9df` | 47,442,244 | 2025-03-13 23:26:10 UTC | 1,179.77 | 4,034.67 | 342.0% | HOLD* (>100%: akumulasi lanjutan) | KONTRAK | KONTRAK (eth_getCode sekarang) — coret dari kandidat wallet bersih |
| 16 | `0x52679d733a7d2c64bcda5494f46d6a39277e6d99` | 47,442,245 | 2025-03-13 23:26:13 UTC | 59,951.99 | 0.00 | 0.0% | DUST/EXIT | EOA | Saldo sekarang 0 — sudah jual penuh (waktu jual tidak dihitung; metode Transfer tidak memberi histori harga) |
| 17 | `0xf6721a488e6a12552a30c59c9a96af1b139ebba6` | 47,442,245 | 2025-03-13 23:26:13 UTC | 33,655.25 | 0.00 | 0.0% | DUST/EXIT | KONTRAK | KONTRAK (eth_getCode sekarang) — coret dari kandidat wallet bersih; Saldo sekarang 0 — sudah jual penuh (waktu jual tidak dihitung; metode Transfer tidak memberi histori harga) |
| 18 | `0xb0006e5ab631818a2896f99fa62e2dc9a5280aae` | 47,442,247 | 2025-03-13 23:26:19 UTC | 126,391.44 | 0.00 | 0.0% | DUST/EXIT | KONTRAK | KONTRAK (eth_getCode sekarang) — coret dari kandidat wallet bersih; Saldo sekarang 0 — sudah jual penuh (waktu jual tidak dihitung; metode Transfer tidak memberi histori harga) |
| 19 | `0xb18fffbf51b4c6a933befc5616e7deb9d2377f79` | 47,442,249 | 2025-03-13 23:26:25 UTC | 14,900.08 | 0.00 | 0.0% | DUST/EXIT | EOA | Saldo sekarang 0 — sudah jual penuh (waktu jual tidak dihitung; metode Transfer tidak memberi histori harga) |
| 20 | `0xbf170eb80747e8d0a882a5f18eaa679457b5ddd4` | 47,442,253 | 2025-03-13 23:26:37 UTC | 40,338.14 | 0.00 | 0.0% | DUST/EXIT | EOA | Saldo sekarang 0 — sudah jual penuh (waktu jual tidak dihitung; metode Transfer tidak memberi histori harga) |
| 21 | `0x4a50dfa71ef3dac520a685427a1bb8bbe30608a6` | 47,442,254 | 2025-03-13 23:26:40 UTC | 38,870.74 | 1.58 | 0.0% | DUST/EXIT | KONTRAK | KONTRAK (eth_getCode sekarang) — coret dari kandidat wallet bersih; Sisa debu (<1% dari beli awal) |
| 22 | `0xd3ac4584c2966da9101b7c950d0daf69645a680a` | 47,442,258 | 2025-03-13 23:26:52 UTC | 93,664.99 | 20.49 | 0.0% | DUST/EXIT | KONTRAK | KONTRAK (eth_getCode sekarang) — coret dari kandidat wallet bersih; Sisa debu (<1% dari beli awal) |
| 23 | `0xb23a659ba5abca81095ea07608ca6bc262f18bce` | 47,442,258 | 2025-03-13 23:26:52 UTC | 13,446.76 | 0.00 | 0.0% | DUST/EXIT | EOA | Saldo sekarang 0 — sudah jual penuh (waktu jual tidak dihitung; metode Transfer tidak memberi histori harga) |
| 24 | `0x0ff74c65ed7439c025197bc2044f61a520915629` | 47,442,258 | 2025-03-13 23:26:52 UTC | 39,881.68 | 0.00 | 0.0% | DUST/EXIT | EOA | Saldo sekarang 0 — sudah jual penuh (waktu jual tidak dihitung; metode Transfer tidak memberi histori harga) |
| 25 | `0x3df3696ac88e09ade55aa56abc8bccf5eef5c7f4` | 47,442,263 | 2025-03-13 23:27:07 UTC | 47,154.67 | 0.00 | 0.0% | DUST/EXIT | EOA | Saldo sekarang 0 — sudah jual penuh (waktu jual tidak dihitung; metode Transfer tidak memberi histori harga) |

## SKYAI

- Token: `0x92aa03137385f18539301349dcfc9ebc923ffb10` — on-chain `name()`/`symbol()` = `SKYAI`, decimals 18, totalSupply 1.000.000.000 (dibaca via eth_call, selector dihitung programatik dari `eth_utils.keccak`).
- Pair PCS V2 (factory `0xca143ce32fe78f1f7019d7d551a6402fc5350c73`, `getPair` on-chain): `0xbc42145d5a574ede9b8860fca2a49eb7b239efa5`
- Pair creation: blok 48.512.772, header blok 2025-04-20T03:42:03Z — sama persis dengan `pool_created_at` GeckoTerminal untuk pool ini.
- Window scan Ankr: 48.512.772–48.512.971 (1 chunk 200 blok). 539 log pair->buyer, 378 buyer distinct; tabel = 25 pertama. Tidak ada chunk yang menyentuh batas 1.000 log/page, jadi tidak ada indikasi pemotongan halaman.
- Definisi "beli awal" = jumlah Transfer token dari pair ke buyer di dalam window scan. Saldo sekarang dibaca di blok 131.227.784 (2 Nov 2026).
- Ambang "debu": sisa <1% dari beli awal (termasuk 0). Status: HOLD ≥50%, PARTIAL 1–<50%, DUST/EXIT <1%.

| # | Buyer (alamat lengkap) | Blok beli awal | Waktu beli awal (header blok) | Beli awal (token) | Saldo sekarang | % dipegang | Status | Tipe | Catatan kebersihan |
|---|---|---|---|---|---|---|---|---|---|
| 1 | `0xa4e67515834e0e84a30907e379545cad5390a5bb` | 48,512,772 | 2025-04-20 03:42:03 UTC | 86,788,881.58 | 0.00 | 0.0% | DUST/EXIT | EOA | Klaster blok-0 (6 tx terpisah, total klaster ~162,42 jt = ~16,24% supply di blok creation) — bukan kandidat bersih; Saldo sekarang 0 — sudah jual penuh (waktu jual tidak dihitung; metode Transfer tidak memberi histori harga) |
| 2 | `0x6c9a77850fda7db7c90c3ed708114e38a40c27b0` | 48,512,772 | 2025-04-20 03:42:03 UTC | 34,225,030.58 | 0.00 | 0.0% | DUST/EXIT | EOA | Klaster blok-0 (6 tx terpisah, total klaster ~162,42 jt = ~16,24% supply di blok creation) — bukan kandidat bersih; Saldo sekarang 0 — sudah jual penuh (waktu jual tidak dihitung; metode Transfer tidak memberi histori harga) |
| 3 | `0xc87b8a3288eeb450045d215bacfd50527a4c4353` | 48,512,772 | 2025-04-20 03:42:03 UTC | 18,320,460.99 | 0.00 | 0.0% | DUST/EXIT | EOA | Klaster blok-0 (6 tx terpisah, total klaster ~162,42 jt = ~16,24% supply di blok creation) — bukan kandidat bersih; Saldo sekarang 0 — sudah jual penuh (waktu jual tidak dihitung; metode Transfer tidak memberi histori harga) |
| 4 | `0x19f0446b17751b21f0ab12a3a2e719f534975c25` | 48,512,772 | 2025-04-20 03:42:03 UTC | 11,420,214.59 | 0.00 | 0.0% | DUST/EXIT | EOA | Klaster blok-0 (6 tx terpisah, total klaster ~162,42 jt = ~16,24% supply di blok creation) — bukan kandidat bersih; Saldo sekarang 0 — sudah jual penuh (waktu jual tidak dihitung; metode Transfer tidak memberi histori harga) |
| 5 | `0xa7fdf94a1e267e0f24d1984e879d983cfd641612` | 48,512,772 | 2025-04-20 03:42:03 UTC | 7,795,972.61 | 0.00 | 0.0% | DUST/EXIT | EOA | Klaster blok-0 (6 tx terpisah, total klaster ~162,42 jt = ~16,24% supply di blok creation) — bukan kandidat bersih; Saldo sekarang 0 — sudah jual penuh (waktu jual tidak dihitung; metode Transfer tidak memberi histori harga) |
| 6 | `0x2d33193e9a4eba762da54f074bf5e9ef810f9600` | 48,512,772 | 2025-04-20 03:42:03 UTC | 3,872,858.71 | 0.00 | 0.0% | DUST/EXIT | EOA | Klaster blok-0 (6 tx terpisah, total klaster ~162,42 jt = ~16,24% supply di blok creation) — bukan kandidat bersih; Saldo sekarang 0 — sudah jual penuh (waktu jual tidak dihitung; metode Transfer tidak memberi histori harga) |
| 7 | `0xa1df4d3b771b8bca9bff8e339f3b2a8bb9ce1e69` | 48,512,773 | 2025-04-20 03:42:06 UTC | 14,029.85 | 0.00 | 0.0% | DUST/EXIT | EOA | Saldo sekarang 0 — sudah jual penuh (waktu jual tidak dihitung; metode Transfer tidak memberi histori harga) |
| 8 | `0xf90e5f9d2b472c7ad566369d82c2759affa10fed` | 48,512,773 | 2025-04-20 03:42:06 UTC | 47,059.88 | 0.00 | 0.0% | DUST/EXIT | EOA | Saldo sekarang 0 — sudah jual penuh (waktu jual tidak dihitung; metode Transfer tidak memberi histori harga) |
| 9 | `0x53c0d7391d5f8823e79454d0c432c14a5a69ea51` | 48,512,773 | 2025-04-20 03:42:06 UTC | 35,564.38 | 0.00 | 0.0% | DUST/EXIT | EOA | Saldo sekarang 0 — sudah jual penuh (waktu jual tidak dihitung; metode Transfer tidak memberi histori harga) |
| 10 | `0xc9ea99d8c7e4e6b409656b25ff26a6d17bfb2d32` | 48,512,773 | 2025-04-20 03:42:06 UTC | 106,120.97 | 0.00 | 0.0% | DUST/EXIT | EOA | Sisa debu (<1% dari beli awal) |
| 11 | `0x99a5eaf1377b8128264a447ece0f12895caca68f` | 48,512,773 | 2025-04-20 03:42:06 UTC | 13,958.16 | 0.00 | 0.0% | DUST/EXIT | EOA | Saldo sekarang 0 — sudah jual penuh (waktu jual tidak dihitung; metode Transfer tidak memberi histori harga) |
| 12 | `0x11c8cfb2365a79e140f4991e3fd9f73c82efd2f3` | 48,512,773 | 2025-04-20 03:42:06 UTC | 108,517.75 | 0.00 | 0.0% | DUST/EXIT | EOA | Saldo sekarang 0 — sudah jual penuh (waktu jual tidak dihitung; metode Transfer tidak memberi histori harga) |
| 13 | `0x77d3b6281087e64a68e46018e246780adb7714e8` | 48,512,773 | 2025-04-20 03:42:06 UTC | 41,154.85 | 0.00 | 0.0% | DUST/EXIT | EOA | Saldo sekarang 0 — sudah jual penuh (waktu jual tidak dihitung; metode Transfer tidak memberi histori harga) |
| 14 | `0x75e1bb79ffaed83fb860a8171e19d5953b79e52e` | 48,512,773 | 2025-04-20 03:42:06 UTC | 179,490.86 | 0.00 | 0.0% | DUST/EXIT | EOA | Saldo sekarang 0 — sudah jual penuh (waktu jual tidak dihitung; metode Transfer tidak memberi histori harga) |
| 15 | `0xb976d3d076a5ad9fc3b9ee2a6499526701b939c3` | 48,512,774 | 2025-04-20 03:42:09 UTC | 53,635.19 | 0.00 | 0.0% | DUST/EXIT | EOA | Saldo sekarang 0 — sudah jual penuh (waktu jual tidak dihitung; metode Transfer tidak memberi histori harga) |
| 16 | `0xab23d58a050a85f91109ebbd1ac068b7c8dc72e2` | 48,512,774 | 2025-04-20 03:42:09 UTC | 355,786.31 | 0.00 | 0.0% | DUST/EXIT | EOA | Sisa debu (<1% dari beli awal) |
| 17 | `0xb5cb05554867ce201b0e6feb8d6cefd3a1dd5e32` | 48,512,776 | 2025-04-20 03:42:15 UTC | 159,288.31 | 0.00 | 0.0% | DUST/EXIT | KONTRAK | KONTRAK (eth_getCode sekarang) — coret dari kandidat wallet bersih; Saldo sekarang 0 — sudah jual penuh (waktu jual tidak dihitung; metode Transfer tidak memberi histori harga) |
| 18 | `0x8ec6e31f6a87368c4edb478ae8199b355606ff59` | 48,512,776 | 2025-04-20 03:42:15 UTC | 1,006,591.40 | 0.00 | 0.0% | DUST/EXIT | EOA | Saldo sekarang 0 — sudah jual penuh (waktu jual tidak dihitung; metode Transfer tidak memberi histori harga) |
| 19 | `0xd4d9978695ccf9aff3d1ba2d74cbaa48591daea1` | 48,512,776 | 2025-04-20 03:42:15 UTC | 13,032.08 | 0.00 | 0.0% | DUST/EXIT | EOA | Saldo sekarang 0 — sudah jual penuh (waktu jual tidak dihitung; metode Transfer tidak memberi histori harga) |
| 20 | `0xb1600230d6a7dd29b7cfb15988d6fc543bccd444` | 48,512,776 | 2025-04-20 03:42:15 UTC | 17,773.71 | 0.00 | 0.0% | DUST/EXIT | EOA | Saldo sekarang 0 — sudah jual penuh (waktu jual tidak dihitung; metode Transfer tidak memberi histori harga) |
| 21 | `0x2fb3f8f45361c2b71e908104380625a4b8be056d` | 48,512,776 | 2025-04-20 03:42:15 UTC | 39,002.11 | 0.00 | 0.0% | DUST/EXIT | EOA | Saldo sekarang 0 — sudah jual penuh (waktu jual tidak dihitung; metode Transfer tidak memberi histori harga) |
| 22 | `0x6981ea056937f75052802bbcab67752840afa565` | 48,512,779 | 2025-04-20 03:42:24 UTC | 78,494.91 | 0.00 | 0.0% | DUST/EXIT | EOA | Saldo sekarang 0 — sudah jual penuh (waktu jual tidak dihitung; metode Transfer tidak memberi histori harga) |
| 23 | `0x92705e928ef7b8ae660651dbb215ec735ad91fb9` | 48,512,780 | 2025-04-20 03:42:27 UTC | 13,084.78 | 0.00 | 0.0% | DUST/EXIT | EOA | Saldo sekarang 0 — sudah jual penuh (waktu jual tidak dihitung; metode Transfer tidak memberi histori harga) |
| 24 | `0x4c6f6959f93b00cddab72c1644dd50133f82f1b9` | 48,512,780 | 2025-04-20 03:42:27 UTC | 13,075.34 | 0.00 | 0.0% | DUST/EXIT | KONTRAK | KONTRAK (eth_getCode sekarang) — coret dari kandidat wallet bersih; Saldo sekarang 0 — sudah jual penuh (waktu jual tidak dihitung; metode Transfer tidak memberi histori harga) |
| 25 | `0xd6ae44f52152481a719aad1e8672cb8d4c5b9d99` | 48,512,781 | 2025-04-20 03:42:30 UTC | 2,612.62 | 0.00 | 0.0% | DUST/EXIT | EOA | Saldo sekarang 0 — sudah jual penuh (waktu jual tidak dihitung; metode Transfer tidak memberi histori harga) |

## EGL1

- Token: `0xf4b385849f2e817e92bffbfb9aeb48f950ff4444` — on-chain `name()`/`symbol()` = `EGL1`, decimals 18, totalSupply 1.000.000.000 (dibaca via eth_call, selector dihitung programatik dari `eth_utils.keccak`).
- Pair PCS V2 (factory `0xca143ce32fe78f1f7019d7d551a6402fc5350c73`, `getPair` on-chain): `0xd950a522e376adbe485c47eab244b9e13ca71f48`
- Pair creation: blok 50.941.764, header blok 2025-06-05T20:50:30Z — sama persis dengan `pool_created_at` GeckoTerminal untuk pool ini.
- Window scan Ankr: 50.941.764–51.053.763 (chunk 200 blok lalu 2.000 blok). 38 log pair->buyer, 14 buyer distinct; tabel = SEMUA 14. Tidak ada chunk yang menyentuh batas 1.000 log/page, jadi tidak ada indikasi pemotongan halaman.
- Definisi "beli awal" = jumlah Transfer token dari pair ke buyer di dalam window scan. Saldo sekarang dibaca di blok 131.227.784 (2 Nov 2026).
- Ambang "debu": sisa <1% dari beli awal (termasuk 0). Status: HOLD ≥50%, PARTIAL 1–<50%, DUST/EXIT <1%.

| # | Buyer (alamat lengkap) | Blok beli awal | Waktu beli awal (header blok) | Beli awal (token) | Saldo sekarang | % dipegang | Status | Tipe | Catatan kebersihan |
|---|---|---|---|---|---|---|---|---|---|
| 1 | `0x6d76e7bb743fee795a2f00a317760acf822ee2be` | 50,941,789 | 2025-06-05 20:51:08 UTC | 97.55 | 23,589,368.69 | 24,182,053.8% | HOLD* (>100%: akumulasi lanjutan) | KONTRAK | POOL EGL1 lain (USD1, GeckoTerminal 2025-06-04T18:42:29Z) — BUKAN wallet, coret; Pembelian debu (<100 token) |
| 2 | `0xaaaa2d1b30c03683f44a1d36643201a9c4544e74` | 50,941,919 | 2025-06-05 20:54:23 UTC | 1,090.26 | 0.00 | 0.0% | DUST/EXIT | KONTRAK | KONTRAK (eth_getCode sekarang) — coret dari kandidat wallet bersih; Saldo sekarang 0 — sudah jual penuh (waktu jual tidak dihitung; metode Transfer tidak memberi histori harga) |
| 3 | `0xda006dcb8ab8b670c98fe5103340a16387187d7e` | 50,941,929 | 2025-06-05 20:54:38 UTC | 470.56 | 0.00 | 0.0% | DUST/EXIT | KONTRAK | KONTRAK (eth_getCode sekarang) — coret dari kandidat wallet bersih; Saldo sekarang 0 — sudah jual penuh (waktu jual tidak dihitung; metode Transfer tidak memberi histori harga) |
| 4 | `0x7035f2bfb370c740cdc60095c75966f04c47ddff` | 50,941,970 | 2025-06-05 20:55:39 UTC | 11,600.87 | 0.00 | 0.0% | DUST/EXIT | KONTRAK | KONTRAK (eth_getCode sekarang) — coret dari kandidat wallet bersih; Saldo sekarang 0 — sudah jual penuh (waktu jual tidak dihitung; metode Transfer tidak memberi histori harga) |
| 5 | `0x426603bac5e0ea73fd13aecad7a80c9f963f6eac` | 50,941,973 | 2025-06-05 20:55:44 UTC | 0.33 | 3.28 | 1,003.2% | HOLD* (>100%: akumulasi lanjutan) | KONTRAK | KONTRAK (eth_getCode sekarang) — coret dari kandidat wallet bersih; Pembelian debu (<100 token) |
| 6 | `0xd9f39f0180b544b93da0ec4f27821f380983cb48` | 50,944,291 | 2025-06-05 21:53:41 UTC | 2.49 | 0.00 | 0.0% | DUST/EXIT | EOA | Pembelian debu (<100 token); Saldo sekarang 0 — sudah jual penuh (waktu jual tidak dihitung; metode Transfer tidak memberi histori harga) |
| 7 | `0xd39b62d6a6ff06fd8329a6f9c27aedcc6a3c0140` | 50,944,293 | 2025-06-05 21:53:44 UTC | 6.75 | 0.00 | 0.0% | DUST/EXIT | KONTRAK | KONTRAK (eth_getCode sekarang) — coret dari kandidat wallet bersih; Pembelian debu (<100 token); Saldo sekarang 0 — sudah jual penuh (waktu jual tidak dihitung; metode Transfer tidak memberi histori harga) |
| 8 | `0xb300000b72deaeb607a12d5f54773d1c19c7028d` | 50,958,743 | 2025-06-06 03:55:03 UTC | 4.81 | 223.28 | 4,640.2% | HOLD* (>100%: akumulasi lanjutan) | KONTRAK | KONTRAK (eth_getCode sekarang) — coret dari kandidat wallet bersih; Pembelian debu (<100 token) |
| 9 | `0x7178075578ef38530cdf032da102a796a590b4c8` | 50,969,410 | 2025-06-06 08:21:46 UTC | 1.31 | 0.00 | 0.0% | DUST/EXIT | KONTRAK | KONTRAK (eth_getCode sekarang) — coret dari kandidat wallet bersih; Pembelian debu (<100 token); Saldo sekarang 0 — sudah jual penuh (waktu jual tidak dihitung; metode Transfer tidak memberi histori harga) |
| 10 | `0xdb92120f4ee2636cd5a866eea06665d27563fd62` | 50,971,185 | 2025-06-06 09:06:09 UTC | 2.47 | 0.00 | 0.0% | DUST/EXIT | EOA | Pembelian debu (<100 token); Saldo sekarang 0 — sudah jual penuh (waktu jual tidak dihitung; metode Transfer tidak memberi histori harga) |
| 11 | `0xbbcc6cb70b58fad60f282212bfd7e852adb53b9a` | 50,971,729 | 2025-06-06 09:19:46 UTC | 1.14 | 0.00 | 0.0% | DUST/EXIT | KONTRAK | KONTRAK (eth_getCode sekarang) — coret dari kandidat wallet bersih; Pembelian debu (<100 token); Saldo sekarang 0 — sudah jual penuh (waktu jual tidak dihitung; metode Transfer tidak memberi histori harga) |
| 12 | `0x779a74436eda060911b2c4f209d34ea155f3df09` | 50,974,718 | 2025-06-06 10:34:29 UTC | 1.97 | 0.00 | 0.0% | DUST/EXIT | KONTRAK | KONTRAK (eth_getCode sekarang) — coret dari kandidat wallet bersih; Pembelian debu (<100 token); Saldo sekarang 0 — sudah jual penuh (waktu jual tidak dihitung; metode Transfer tidak memberi histori harga) |
| 13 | `0x4f03478022cac2c1ef2fee4278a0b34d880cd13b` | 50,986,435 | 2025-06-06 15:27:39 UTC | 1.36 | 0.00 | 0.0% | DUST/EXIT | EOA | Pembelian debu (<100 token); Sisa debu (<1% dari beli awal) |
| 14 | `0xa01cd5b68265b972b73a713f6d824d1a6d3612b0` | 51,039,905 | 2025-06-07 13:44:36 UTC | 45.12 | 0.00 | 0.0% | DUST/EXIT | KONTRAK | Juga early buyer di koin lain trio ini (mubarak+EGL1) — linkage LEMAH (co-buy saja); KONTRAK (eth_getCode sekarang) — coret dari kandidat wallet bersih; Pembelian debu (<100 token); Sisa debu (<1% dari beli awal) |
---

## Penutup metode & batas

- Jumlah buyer yang dilaporkan: mubarak 25 pertama dari 45 distinct (window 200 blok / ~10 menit), SKYAI 25 pertama dari 378 distinct (window 200 blok / ~10 menit), EGL1 SEMUA 14 distinct (window 50.941.764–51.053.763).
- "Beli awal" dihitung hanya dari log pair->buyer di window scan; pembelian lanjutan di luar window tidak dihitung dalam "beli awal" (itulah mengapa % bisa >100%).
- Tidak ada GMGN, tidak ada login, tidak ada klaim PnL. Semua angka saldo adalah hasil `balanceOf` on-chain di blok 131.227.784; semua waktu adalah timestamp header blok (UTC).
