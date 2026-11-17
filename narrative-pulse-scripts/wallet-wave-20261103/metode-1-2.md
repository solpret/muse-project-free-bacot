# Wallet-Discovery Wave 2026-11-03 — Metode 1 + 2 (LAPORAN AKHIR)

**Status: SELESAI. READ-ONLY. Tidak ada transaksi, signing, approval, konek wallet,
login, layanan berbayar, atau perubahan file feed/tier-ab/cron.**
**Periode kerja: 2026-11-03 ~13:05–15:05 WIB. Metode 3 (live browser) = tugas parent berikutnya;
metode 4–6 menyusul sesudah itu.**

---

## Ringkasan eksekutif

- **Metode 1 (irisan pembeli awal koin terbentuk): SELESAI, 14/14 koin OK.**
  33 wallet jadi pembeli awal di ≥3 koin. Setelah saringan kode kontrak, tersisa
  **10 wallet EOA** — dan setelah saringan perilaku + funding, **NOL yang lolos
  ketujuh saringan "terpercaya"**. Satu-satunya yang tidak gagal bersih adalah
  **0xf16b4b87e6f214b60abc8e52e207c5009e14d019 (x4) sebagai kandidat WATCH
  (lemah)**: independen, EOA, aktif 30 hari, early x4, bukan fee receiver —
  TAPI satu flip 0,3 menit di Q + profit TEREALISASI BELUM TERVERIFIKASI
  (baca arsip harga blok lama gagal di semua RPC gratis).
- **Temuan metodologis terbesar:** irisan mentah Transfer(from=pool) didominasi
  **kontrak infrastruktur (23 dari 33)** — router/aggregator/bot contract, termasuk
  "bintang" x13 (0xb300...) dan router 1inch. Tanpa saringan eth_getCode, laporan
  ini akan mengusulkan kontrak sebagai "wallet". Saringan kode adalah WAJIB.
- **Temuan kedua:** wallet x10 teratas (0x9999...) adalah **bot** (swap atomik
  routed + flip pool 0,1–4,6 menit + ≥1000 transfer-out per 15 menit).
- **Temuan ketiga:** 4 wallet [IDOL, Q, UAI] yang tampak independen ternyata
  **SATU entitas operator (klaster bot-farm)**: funder debu bersama
  0x9b79cc64... + hub pengumpul bersama 0x4982085c... + exit tersinkron
  di blok yang sama. Mereka = 1 suara, bukan 4 — dan ditolak sebagai vote feed.
- **Irisan dengan set yang sudah ada: NOL.** Tidak satu pun dari 33 wallet
  (termasuk 10 EOA) ada di feed 6 / tier-ab 54 / Tier C / TRIO / PAIR / T7.
  Semua 10 EOA adalah BARU — tapi 9 di antaranya ditolak karena perilaku,
  1 sisanya hanya WATCH.
- **Tidak ada usulan perubahan feed dalam laporan ini** (sesuai tugas; parent
  yang menyampaikan shortlist ke user untuk diputuskan).

---

## METODE 1 — Irisan pembeli awal koin terbentuk

### Sumber koin + bukti

- **Sumber utama: GeckoTerminal trending pools BSC**
  `https://api.geckoterminal.com/api/v2/networks/bsc/trending_pools` (dibaca
  2026-11-03 ~13:10 WIB; mentah tersimpan di `gecko-trending-raw.json`).
  Set primer = 15 koin dengan `market_cap_usd` > $1M. DexScreener dipakai
  sebagai sumber kedua hanya untuk pool pengganti (lihat di bawah).
- **Koin yang dikeluarkan dari primer:** AGC (MC null, FDV $311.129 — di bawah
  $1M + area proyek user sendiri), RVV (MC $244.938), TART/ARK/AGT (MC 0,0 —
  MC tak terverifikasi meski FDV tinggi).
- **Instrumen:** Transfer log per kontrak token via modul Ankr
  `~/workspace/custom-connectors/custom.ankr/bin/ankr.py`
  (`get_logs`, address-filter [token], topics [[Transfer], [pool-padded]]).
  Definisi pembeli awal = penerima Transfer dengan topic1 (from) = alamat pool.
  Set awal per koin = 200 pembeli unik pertama kronologis (kecuali SAFU-B13B
  yang terpotong di 200 dari 366 yang ditemukan — lihat tabel).
  **Kontaminasi yang dicatat, bukan disembunyikan:** Transfer(from=pool) juga
  menangkap fee collection V3 dan liquidity removal V2; saringan kode + perilaku
  di bawah yang membersihkannya, bukan asumsi.

### Perbaikan metode selama jalan (dicatat agar tidak diulang)

1. **Ankr newest-first + pageSize 1000:** query jendela lebar mengembalikan
   1000 pembelian TERBARU, bukan paling awal. Solusi: biseksi lo/hi
   (invarian [start, lo] kosong, [start, hi] capped) — konvergen ≤30 panggilan.
   Walk-back satu halaman (cara lama) gagal di token padat (>40 iterasi).
2. **Pool V4/Infinity tidak punya alamat:** 5 pool trending GeckoTerminal
   (BASED, AEON, UAI, COLLECT, JCT) ternyata beralamat 64-hex — itu **PoolId
   bytes32 PancakeSwap Infinity/CLMM**, bukan alamat kontrak. Instrumen
   Transfer(from=pool) TIDAK BERLAKU untuk pool V4 (swap V4 lewat PoolManager,
   bukan alamat pool). Solusi: pakai pool V2/V3 tertua dari DexScreener per
   token (tercatat per koin di bawah). **AEON DIKELUARKAN** — tidak ada venue
   V2/V3 di GeckoTerminal maupun DexScreener (semua pool-nya V4/Infinity +
   uniswap-v4); instrumen tidak dapat diterapkan (keterbatasan instrumen,
   BUKAN vonis atas koinnya).
3. **Transkripsi pool:** pool EVAA dan JCT di daftar awal terpotong/salah
   sambung (transkripsi manual); diperbaiki dari file mentah GeckoTerminal
   (EVAA) dan DexScreener (JCT). Pelajaran: jangan pernah transkripsi alamat
   dengan tangan — ambil programatik dari sumber.
4. **Bug loop tak hingga (diperbaiki):** ekspansi jendela fase-1 lama berhenti
   maju saat span mencapai cap 8M blok → loop selamanya (inilah yang membuat
   run v3 macet 14 menit di EVAA/BASED/AEON). Perbaikan: ekspansi tanpa cap
   sampai blok terbaru + guard berhenti saat ujung tidak maju + cap iterasi.
5. **Estimasi blok era-rate terlalu kasar:** tarif 0,7516 dtk/blok (rata-rata
   Jul–Nov 2025) meleset ~8 juta blok untuk EVAA (launch riil ~blok 71,1 juta
   vs estimasi 63,2 juta). Margin eskalasi ditambah ke 10M blok + ekspansi
   fase-1 sampai blok terbaru menutup celah ini.

### Tabel 14 koin final (semua OK, verifikasi launch lolos kecuali COLLECT)

| Koin | Token | Pool dipakai (sumber) | Pool dibuat | MC USD saat cek | Pembeli awal | Blok beli pertama | Verifikasi |
|---|---|---|---|---|---|---|---|
| AKE | 0x2c3a8ee94ddd97244a93bc48298f97d2c412f7db | 0x4d3bf29ba30f8bfe4624e7678709afa195689c5d (GeckoTerminal) | 2025-08-20T07:40:09Z | 107.682.169,75 | 134 | 58363009 (2025-08-21T10:00:31Z, +26 jam) | ok |
| ARIA | 0x5d3a12c42e5372b2cc3264ab3cdcf660a1555238 | 0xa5dbeaf16fc031eae92175974f8d0a439be4ad17 (GeckoTerminal) | 2025-08-19T09:07:05Z | 20.305.812,88 | 69 | 58372136 (2025-08-21T11:54:36Z, +51 jam) | ok |
| IDOL | 0x3b4de3c7855c03bb9f50ea252cd2c9fa1125ab07 | 0xfff4857a955b2b460c27fd431aa5a85fabca5559 (GeckoTerminal) | 2025-06-10T13:33:11Z | 38.570.671,62 | 94 | 51261240 (2025-06-11T09:59:10Z, +20 jam) | ok |
| Q | 0xc07e1300dc138601fa6b0b59f8d0fa477e690589 | 0x8bafe0bdd3eb9ae0539f5b32e771c1a72a189b7f (GeckoTerminal) | 2025-08-31T08:07:27Z | 135.019.380,52 | 108 | 59730044 (2025-09-02T06:53:26Z, +47 jam) | ok |
| JAGENT | 0x8e6442663a4f8c50b6132c68d42a30e7dfe4ae15 | 0xe6efcdef2b720d1eca2b69edb7ef357725680bea (GeckoTerminal, V2 USDT) | 2026-10-28T13:16:40Z | 3.283.127,32 | 113 | 130287859 (2026-10-28T13:17:46Z, +66 detik) | ok |
| EVAA | 0xaa036928c9c0df07d525b55ea8ee690bb5a628c1 | 0x26deb24a2623cf54452ab5183e2c34551831d54d (GeckoTerminal, V3 USDT — alamat diperbaiki) | 2025-10-02T09:03:49Z | 10.003.154,51 | 66 | 63304978 (2025-10-03T07:53:28Z, +23 jam) | ok |
| ESPORTS | 0xf39e4b21c84e737df08e2c3b32541d856f508e48 | 0x83738a0b95cbd7dfd6989569a99edaed3dd704d0 (GeckoTerminal) | 2025-07-19T09:08:11Z | 2.201.170,61 | 10 | 54557604 (2025-07-19T09:08:23Z, +12 detik) | ok |
| LYN | 0x302dfaf2cdbe51a18d97186a7384e87cf599877d | 0x302642976506d247c7017b85ddc89e3956f96ba1 (GeckoTerminal) | 2025-10-06T07:04:44Z | 4.371.446,74 | 49 | 63646551 (2025-10-06T07:03:40Z, −64 detik, dalam toleransi) | ok |
| BASED | 0x1d28d989f9e3ccb8b15d0cec601734514f958e4d | 0x07b7556Ede0f9a6a7d155A78Bc0573f531001A57 (DexScreener, uniswap USDT tertua — pool GeckoTerminal-nya V4 PoolId, tak terpakai) | 2026-03-30T05:09:11Z (DexScreener; GeckoTerminal V4: 2026-03-28) | 11.284.340,07 | 63 | 89574305 (2026-03-30T08:00:05Z, +2,9 jam) | ok |
| JCT | 0xea37a8de1de2d9d10772eeb569e28bfa5cb17707 | 0xceC354f641Fb46b977c3a1f18B5cAf3E2Ede4C2c (DexScreener, uniswap USDT tertua — venue asli Nov 2025, 7 bulan SEBELUM pool V4 GeckoTerminal Jun 2026) | 2025-11-10T10:29:31Z (DexScreener) | 56.337.675,20 | 45 | 67692804 (2025-11-10T10:30:03Z, +32 detik) | ok |
| SAFU-B13B | 0xdd806e436dda5588bf54061c11590c77ddc87777 | 0x13b86fcf85c9c8f5c36593822d216b8893c25450 (GeckoTerminal, V2 B13B) | 2026-10-10T18:56:06Z | 1.675.877,99 | 200 dari 366 (terpotong di 200) | 126879472 (2026-10-10T18:56:14Z, +8 detik) | ok |
| AIN | 0x9558a9254890b2a8b057a789f413631b9084f4a3 | 0xf4262c4dbf524f53851a5176bdc7d6c1e0fa82d8 (GeckoTerminal) | 2025-07-04T12:46:04Z | 46.134.185,90 | 46 | 52944078 (2025-07-05T08:57:47Z, +20 jam) | ok |
| UAI | 0x3e5d4f8aee0d9b3082d5f6da5d6e225d17ba9ea0 | 0x82ED13117144344B39e5ec74d614D54465897a24 (DexScreener, uniswap USDT tertua — pool GeckoTerminal-nya V4 PoolId, tak terpakai) | 2025-11-06T10:38:06Z (DexScreener; GeckoTerminal V4: 2025-11-04) | 36.799.987,26 | 105 | 67234444 (2025-11-06T11:00:00Z, +22 menit) | ok |
| COLLECT | 0x4b3d30992f003c8167699735f5ab2831b2a087d3 | 0x1FFEad9A221992D16f3AA02455542D2B2DA92bcf (DexScreener, uniswap USDT — pool GeckoTerminal-nya V4 PoolId, tak terpakai) | 2025-12-26T19:50:28Z (DexScreener) | 12.806.843,21 | 45 | 121414812 (2026-09-12T07:35:24Z, **+259 hari — GAGAL verifikasi**) | **TIDAK OK** |

**Catatan COLLECT (penting):** pool DexScreener-nya baru pertama berdagang
12 Sep 2026 — 259 hari sesudah koin dibuat. "Pembeli awal" COLLECT adalah
pedagang pertama venue itu, BUKAN pembeli awal saat formasi koin. Bobot
COLLECT dalam irisan harus diturunkan: wallet yang koin ketiganya hanya
COLLECT (0x4ff1... [ARIA, Q, COLLECT], 0x7751... [BASED, JCT, COLLECT])
mendapat flag khusus di bawah. SAFU-B13B (bukan SAFU NFT/token user) dan
SAFU-B13B vs token SAFU lain: pakai alamat persis, jangan dicampur.

**Dikeluarkan dari set final:** AEON (0x277add739c6e0477616948357af9e79fe1ec9b80)
— venue hanya V4/Infinity + uniswap-v4 (pool pertama 2026-07-26, dex
pancakeswap-infinity-clmm, PoolId 64-hex); tidak ada venue V2/V3 di
GeckoTerminal maupun DexScreener. Instrumen tidak dapat diterapkan.

**File bukti metode 1:** `m1_coins.json` (14 koin + daftar pembeli + nilai
mentah), `m1_intersection.json` (33 wallet ≥3), `m1_code_class.json`
(klasifikasi kode), `m1_exits.json` (exit 15 menit), `m1_v4.log`.

### Irisan ≥3 koin: 33 wallet → 10 EOA (23 kontrak DITOLAK)

Saringan (g) BUKAN exchange/kontrak — eth_getCode via fast_rpc, per wallet:

**DITOLAK sebagai kontrak (23):** 0xb300000b72deaeb607a12d5f54773d1c19c7028d (x13!),
0x6b3affc894b0d2d566e5ff03ad79188f1b65bfff (x8),
0x111111125421ca6dc452d289314280a0f8842a65 (x7, router 1inch),
0x4b1b2ea60cc20a171cb7eed8fe0de988f79651d2 (x6),
0xfbcb2705105e4b07b5f6aab73c4b928d941abca6 (x5),
0xac175d676d9d4027aa72f13bc9406fd05c28cf1e (x5),
0xa4d8ca843293b45cb2f61d54509186ca81a34408 (x5),
0x144d395b5562c742259932d2ee6e1d8d092a21b8 (x4),
0x081df5b08fd64abee82c34c0dee72084d01c3987 (x4),
0x28e2ea090877bf75740558f6bfb36a5ffee9e9df (x4),
0xaf7076ff9f05f2653e73aea69cf68e6ffc4ec800 (x4),
0x238a358808379702088667322f80ac48bad5e6c4 (x4),
0xf197da97df68f6e72264d340a820e8efd301e1a4 (x3),
0x690f1fc9e7658cb9345d84ddbb82e3e0526f0000 (x3),
0x2ea94a042461940fb59cc7260bb85342891fb5eb (x3),
0xba53da030f3504db8cf0309bb89791950d0ce5e6 (x3),
0xde9e4fe32b049f821c7f3e9802381aa470ffca73 (x3),
0x653b40ab9dd1d1b42845f67f2be617b2445b7ea5 (x3),
0x4ff1d40fb7b56665bf95d8d8e3a5320de46709a1 (x3),
0xedc94232a8ede362ff062459f4940b5794c5a7f4 (x3),
0x6e4141d33021b52c91c28608403db4a0ffb50ec6 (x3),
0x6d9cb7cbe8fd713bc64530ff70e440d663c15d20 (x3),
0x9a773d0749b2e6eba628b471d03485718e533681 (x3).
Semua punya bytecode runtime (awalan 0x6080604052/0x60a0/0x5f34…) — infrastruktur
router/aggregator/bot, bukan wallet. Khusus 0xb300...: x13 di 13 dari 14 koin
(hanya absen di ESPORTS yang cuma punya 10 pembeli) — "bintang" palsu yang
akan lolos tanpa saringan kode.

**LOLOS saringan kode (10 EOA — masuk evaluasi perilaku + funding):**

| Wallet | Jenis | Koin (x) |
|---|---|---|
| 0x9999b0cdd35d7f3b281ba02efc0d228486940515 | EOA + delegasi 0xef01 | x10: AKE, ARIA, Q, EVAA, ESPORTS, LYN, BASED, JCT, UAI, COLLECT |
| 0x39c837abce0976e5adcffbad06ba47e473aaec37 | EOA | x4: ARIA, IDOL, Q, EVAA |
| 0xf16b4b87e6f214b60abc8e52e207c5009e14d019 | EOA | x4: Q, EVAA, AIN, UAI |
| 0xf2164bac632ecb0ee24e6c30370d53de92d3fe4d | EOA | x3: AKE, ARIA, EVAA |
| 0xa8d7df64adaa13d303ac84cdc6ecea0e61ad54eb | EOA | x3: AKE, ARIA, Q |
| 0x874d92be9a7966805e5de651c726f2c22dfde7d2 | EOA | x3: IDOL, Q, UAI |
| 0xad066bf19d4cdf7916552139f5fbda4e7e645d02 | EOA | x3: IDOL, Q, UAI |
| 0xe12c2e198fa28153511a7322beb75086826df9a7 | EOA | x3: IDOL, Q, UAI |
| 0xb735a41cf69b03d6fef807815e52880cb75cf6c2 | EOA | x3: IDOL, Q, UAI |
| 0x77519fa2324078e75b43c1bf2f8681069100c6c0 | EOA + delegasi 0xef01 | x3: BASED, JCT, COLLECT (flag COLLECT, lihat atas) |

Catatan delegasi: 0x9999... dan 0x7751... punya kode 0xef01… (24 byte,
bukan 20-byte EIP-7702 standar — dicatat apa adanya, bukan kontrak runtime).
AFeng sendiri juga EOA + delegasi 0xef01, jadi delegasi saja bukan vonis —
yang memvonis 0x9999/0x7751 adalah perilakunya (di bawah).

### Evaluasi perilaku: exit 15 menit pasca-beli (koreksi same-tx!)

Metode: untuk tiap (wallet, koin), Transfer(from=wallet) di jendela
[blok_beli, blok_beli+2000] (~15 menit). **Koreksi penting:** transfer-out
pertama sering kali adalah TRANSAKSI YANG SAMA dengan pembelian (kaki kedua
swap atomik routed — nilai persis sama, tx sama) — itu BUKAN penjualan.
Yang dinilai adalah exit pertama dengan tx BERBEDA (real_out) dan penjualan
ke pool pertama dengan tx berbeda (real_pool).

| Wallet | Exit nyata per koin (hold → tujuan) | Penilaian |
|---|---|---|
| 0x9999... | AKE 1,2 m → pool; ARIA 2,3 m → pool; Q 0,2 m → pool; EVAA 4,6 m → pool; ESPORTS 0,6 m → pool; LYN 1,4 m → pool; BASED 0,5 m → pool; JCT 2,6 m → pool; UAI 3,7 m → pool; COLLECT 0,1 m non-pool (tanpa pool sell di jendela). n15 = 1000/1000 di 7 koin (≥1000 transfer-out per 15 menit = hiperaktif). Plus: buy+forward tx-sama di 6 koin yang dicek detail (nilai persis sama) = kaki swap atomik. | **BOT. GAGAL (e).** Flip pool sub-5-menit sistematis + hiperaktivitas + routing atomik. Bukan smart money diskresioner. |
| 0x39c837ab... | ARIA 0,0 m → pool; IDOL 0,0 m → pool (beli di blok launch 51261240, jual 6 blok kemudian); Q 0,0 m → pool; EVAA 0,0 m → pool. | **SNIPER. GAGAL (e).** Jual ke pool dalam hitungan detik/blok di semua koin. |
| 0xf2164bac... | AKE 0,1 m → pool; ARIA 0,1 m → pool; EVAA 0,0 m → pool. | **SNIPER. GAGAL (e).** |
| 0xa8d7df64... | AKE 0,7 m → pool; ARIA 0,5 m → pool; Q 0,2 m → pool. | **SNIPER. GAGAL (e).** Tambahan: **GAGAL (b)** — active30d = False (tidak ada tx 30 hari terakhir). |
| 0x874d92be... | IDOL 2,9 m → hub; Q 3,6 m → hub; UAI 3,1 m → hub. | **KLASTER (lihat metode 2). GAGAL (a) + (b)** (active30d False). |
| 0xad066bf1... | IDOL 2,9 m → hub; Q 3,7 m → hub; UAI 5,9 m → hub. | **KLASTER. GAGAL (a) + (b)** (active30d False). |
| 0xe12c2e19... | IDOL 2,9 m → hub; Q 4,8 m → hub; UAI 5,6 m → hub. | **KLASTER. GAGAL (a).** |
| 0xb735a41c... | IDOL 2,5 m → hub; Q 3,3 m → hub; UAI 3,0 m → hub. | **KLASTER. GAGAL (a).** |
| 0xf16b4b87... | Q 0,3 m → pool (FLAG); EVAA 10,5 m → EOA lain; AIN 8,2 m → pool; UAI 12,2 m → pool. | **CAMPURAN — satu-satunya WATCH.** Flip cepat hanya di Q; hold 8–12 menit di 3 koin lain. Lihat verdict akhir. |
| 0x77519fa2... | BASED 5,3 m → kontrak 0x238a...; JCT 0,0 m → pool V3 JCT lain (arbitrase antar-venue seblok); COLLECT 0,0 m → kontrak 0x238a... | **BOT-LIKE. GAGAL (e) secara spirit** (exit seblok + routing lewat kontrak) + flag COLLECT. |

"Hub" = 0x4982085c9e2f89f2ecb8131eca71afad896e89cb (EOA, diverifikasi
eth_getCode = 0x). Nilai exit kuartet vs nilai beli tunggalnya 3,6x–11,5x —
**BUKAN bukti profit** (wallet bisa memegang pembelian lain; rasio ini tidak
dipakai sebagai bukti PnL).

---

## METODE 2 — Peta funding

### Metode + bukti

Per wallet target (AFeng + 10 EOA): (1) blok tx pertama via binary search
Ankr `ankr_getTransactionsByAddress` berfilter blok (pageSize=1); (2) jendela
awal [first_tx, first_tx+200.000 blok] (~25 jam) transfer BNB native masuk/
keluar; (3) jendela 7 hari terakhir [latest−1.344.000, latest]; (4) probe
aktivitas 30 hari [latest−5.760.000, latest] + eth_getCode. Native =
input `0x`, nilai > 0. Blok terbaru saat jalan: ~131.394.000.
File: `m2_targets.json`, `m2_funding.json`, `m2_v2.log`.
Bukti AFeng (baseline, bukan kandidat): first_tx blok 47.515.127
(2025-03-16); funder awal dominan = side wallet dorman
0xbd28edf53231cd121a963b4b119d3cc4cb3a368a (176 BNB, 6 tx, dari
2025-03-21 — konsisten dengan catatan lama 38 transfer total 513,966196 BNB
seumur hidup); funder pertama 0x5353b1cb62a7f0db908bd070b7e3f2cd1bf069d5
(10,389577 BNB, 2025-03-16); aktif 30 hari = True; EOA + delegasi 0xef01;
7 hari terakhir 2.945 tx terpindai, 15 funder / 6 funded (trader sangat aktif).

### Hasil funding per kandidat (funder awal = kunci independensi)

| Wallet | first_tx | Funder awal (jendela awal) | 7 hari terakhir | active30d | Kesimpulan funding |
|---|---|---|---|---|---|
| 0x9999... | 54.183.867 | **TIDAK TERSELESAIKAN (capped)** — jendela awal DAN 7 hari masing-masing terpindai 3.000 tx (cap 3 halaman) tanpa satu pun transfer native (semuanya contract call = bot hiperaktif); funder terkubur di luar cap. | capped, 0/0 | True | Funder tak terverifikasi — TAPI verdict bot sudah berdiri dari perilaku; funding tidak dibutuhkan untuk menolaknya. |
| 0x39c837ab... | 41.316.812 | 0x73f5ebe9... (19,3982 BNB) + 0x1fbe2ace... (19,3363 BNB), 2024-08-13 — dua funder substansial, berbeda dari semua kandidat lain. | 0 tx native | True | Independen ✓ (tapi sudah ditolak perilaku sniper). |
| 0xf16b4b87... | 34.145.653 | 0x71b28530fb7b7ad49187704e87f5c9ddcbf66e3e (1,0 BNB, 2023-12-07) + debu 0,0001 BNB. **0x71b28530... adalah juga tujuan exit EVAA-nya** — konsisten satu operator dua wallet (sumber + trading) atau pengembalian dana ke sumber. Berbeda dari semua funder kandidat lain. | 0 tx native | True | **Independen ✓** (satu-satunya kandidat lolos (a) + (b) + (c) + (f) + (g)). |
| 0xf2164bac... | 52.607.745 | 0x8e159dd0... (0,3512 BNB) + 3 kecil lain, Jul 2025 — berbeda dari yang lain. | 2 funder / 1 funded kecil | True | Independen ✓ (tapi sudah ditolak sniper). |
| 0xa8d7df64... | 44.669.723 | 0xc7ef36f9... + 0x2b26c287... (masing-masing 0,10 BNB debu, Des 2024) — berbeda dari yang lain. | 0 tx native | **False** | Independen, tapi tidak aktif 30 hari. |
| 0x874d92be... | 47.892.853 | **0x9b79cc64cd3e5ec86d951acb27ddbd9ed660cd07 (0,005 BNB debu, 2025-03-29) — SATU-SATUNYA funder.** | 0 tx native | **False** | **KLASTER — funder bersama.** |
| 0xad066bf1... | 51.157.929 | **0x9b79cc64... (0,005 BNB debu, 2025-06-09) — SATU-SATUNYA funder.** | 0 tx native | **False** | **KLASTER — funder bersama.** |
| 0xe12c2e19... | 46.251.290 | **0x9b79cc64... (0,005 BNB debu, 2025-01-31) — SATU-SATUNYA funder.** | 1 funded: hub 0x4982085c... (0,0033 BNB, 2026-10-31) | True | **KLASTER — funder bersama + terhubung ke hub.** |
| 0xb735a41c... | 40.550.340 | **0x4982085c... (0,005 BNB debu, 2024-07-17) — SATU-SATUNYA funder (= hub pengumpul).** | 0 tx native | True | **KLASTER — didanai langsung oleh hub.** |
| 0x77519fa2... | 60.311.816 | 0x136c40a4... (0,012 BNB debu x3, Sep 2025) — SATU-SATUNYA funder, berbeda dari yang lain. | 2.547 tx terpindai, 0/0 native (semua contract call = hiperaktif) | True | Independen secara funder, tapi perilaku bot-like + delegasi; ditolak perilaku. |

### Verdict klaster kuartet [IDOL, Q, UAI] — SATU ENTITAS, BUKAN 4 VOTE

Bukti konvergen (4 kaki, semua on-chain):
1. **Set koin identik** [IDOL, Q, UAI] pada keempatnya.
2. **Exit tersinkron:** IDOL keluar di blok 51261642–51261646 (rentang 4 blok);
   Q di 59730925–59730927 (rentang 2 blok); UAI di 67235266 (tiga wallet di
   blok PERSIS sama) dan 67235269.
3. **Tujuan exit sama:** keempatnya mengirim ke EOA hub
   0x4982085c9e2f89f2ecb8131eca71afad896e89cb di SEMUA koin.
4. **Funder bersama:** 3 dari 4 didanai debu 0,005 BNB oleh
   0x9b79cc64cd3e5ec86d951acb27ddbd9ed660cd07 (provisioning bot-farm khas);
   yang ke-4 didanai langsung oleh hub itu sendiri; satu anggota (e12c)
   masih mengirim ke hub pada 2026-10-31 (hubungan hidup).
Hub dan provisioner keduanya BARU (tidak ada di tier-ab/feed). Klaster ini
dicatat sebagai **satu entitas operator (bot-farm sniper)**, bukan 4 wallet
independen — dan sebagai entitas pun ia ditolak (exit 2,5–5,9 menit +
provisioning debu). Analogi preseden: sama seperti klaster T7 (koordinasi,
bukan konfirmasi independen) — bedanya, klaster ini terikat funder, bukan
hanya jendela waktu.

---

## VERDICT AKHIR PER SARINGAN "TERPERCAYA"

Saringan: (a) operator independen, (b) aktif 30 hari, (c) early ≥3 koin,
(d) profit TEREALISASI, (e) BUKAN dumper, (f) BUKAN fee receiver pasif,
(g) BUKAN exchange/kontrak.

| Wallet | (a) | (b) | (c) | (d) | (e) | (f) | (g) | VERDICT |
|---|---|---|---|---|---|---|---|---|
| 0x9999... (x10) | ? (capped) | ✓ | ✓ | ✗ unverified | **✗ FAIL** (flip 0,1–4,6 m + routing atomik + hiperaktif) | bot, bukan fee receiver | ✓ (EOA delegasi) | **DITOLAK — bot** |
| 0x39c837ab... (x4) | ✓ | ✓ | ✓ | ✗ unverified | **✗ FAIL** (jual pool 0,0 m semua koin) | ✓ | ✓ | **DITOLAK — sniper** |
| 0xf2164bac... (x3) | ✓ | ✓ | ✓ | ✗ unverified | **✗ FAIL** (jual pool 0,0–0,1 m) | ✓ | ✓ | **DITOLAK — sniper** |
| 0xa8d7df64... (x3) | ✓ | **✗ FAIL** | ✓ | ✗ unverified | **✗ FAIL** (jual pool 0,2–0,7 m) | ✓ | ✓ | **DITOLAK — sniper + tidak aktif** |
| 0x874d92be... (x3) | **✗ FAIL** (klaster) | **✗ FAIL** | ✓ | ✗ unverified | ✗ (exit klaster 2,9–3,6 m) | klaster | ✓ | **DITOLAK — klaster** |
| 0xad066bf1... (x3) | **✗ FAIL** (klaster) | **✗ FAIL** | ✓ | ✗ unverified | ✗ (exit klaster 2,9–5,9 m) | klaster | ✓ | **DITOLAK — klaster** |
| 0xe12c2e19... (x3) | **✗ FAIL** (klaster) | ✓ | ✓ | ✗ unverified | ✗ (exit klaster 2,9–5,6 m) | klaster | ✓ | **DITOLAK — klaster** |
| 0xb735a41c... (x3) | **✗ FAIL** (klaster) | ✓ | ✓ | ✗ unverified | ✗ (exit klaster 2,5–3,3 m) | klaster | ✓ | **DITOLAK — klaster** |
| 0xf16b4b87... (x4) | ✓ | ✓ | ✓ | **? UNVERIFIED** | **~ CAMPURAN** (Q 0,3 m = flag; AIN 8,2 m, EVAA 10,5 m, UAI 12,2 m = hold multi-menit) | ✓ | ✓ | **WATCH (lemah) — satu-satunya yang tidak gagal bersih** |
| 0x77519fa2... (x3) | ✓ | ✓ | ✓ (+flag COLLECT) | ✗ unverified | **✗ FAIL** (exit seblok + routing kontrak) | bot-like | ✓ (EOA delegasi) | **DITOLAK — bot-like** |

**Tentang (d) profit TEREALISASI — GAGAL BACA, bukan nol:** upaya verifikasi
harga via slot0 V3 / reserves V2 pada blok beli-vs-jual (untuk penjualan pool
f16b di AIN dan Q) **gagal di SEMUA endpoint RPC gratis** — eth_call
bertag blok lama (blok 2025) ditolak/tidak dilayani (kemungkinan tidak ada
state arsip). token0/token1/decimals pada blok terbaru terbaca normal
(AIN pool: token0 USDT, token1 AIN, desimal 18/18; Q pool: token0 USDT,
token1 Q, desimal 18/18). Jadi (d) = **belum terverifikasi untuk SEMUA
kandidat**, bukan "tidak profit". Penjualan ke pool teramati (f16b: AIN
8,2 m, Q 0,3 m; para sniper: banyak) membuktikan adanya exit, bukan
profitabilitasnya. Verifikasi (d) butuh RPC arsip berbayar atau sumber harga
historis lain — di luar kondisi "selama gratis" gelombang ini.

**Tentang (f) fee receiver:** tidak satu pun dari 10 EOA yang menunjukkan
pola fee receiver (banyak inflow kecil dari banyak sumber + minim outflow).
Pola yang ditemukan malah sebaliknya: bot hiperaktif (9999, 7751) dan
sniper/klaster. (f) = lolos untuk semua EOA non-bot; untuk bot, label yang
tepat adalah "bot", bukan "fee receiver".

**Tentang (b) untuk 39c8/f16b/f2164/e12c/b735/7751/9999:** active30d = True
via probe tx (untuk 39c8/f16b, aktivitas 30 hari terakhirnya adalah
contract call, bukan transfer native — jendela native 7 hari mereka 0 tx;
tetap dihitung aktif karena probe tx mencakup semua jenis tx).

### Daftar SUDAH DIKENAL (iris dengan set yang ada) — HASIL: NOL

- Feed 6 wallet: tidak ada yang muncul di 33 wallet irisan.
- Tier-ab 54 wallet: tidak ada yang muncul.
- Tier C (4 wallet): tidak ada yang muncul.
- TRIO (3 alamat) / PAIR (2 alamat): tidak ada yang muncul.
- Klaster T7 (31 sender jendela eksak): tidak ada yang muncul.
- Hub klaster baru 0x4982085c... dan provisioner 0x9b79cc64... juga BARU
  (tidak ada di tier-ab/feed).
- AFeng muncul sebagai baseline metode 2 saja (bukan kandidat baru).

### Daftar DITOLAK (ringkas, dengan alasan)

- **23 kontrak** (daftar di atas): bukan wallet — router/aggregator/bot
  contract, gagal (g). Termasuk 0xb300... (x13) dan 1inch (x7).
- **0x9999...**: bot (routing atomik + flip sub-5-menit + hiperaktif).
- **0x39c837ab..., 0xf2164bac..., 0xa8d7df64...**: sniper (jual pool
  0,0–0,7 menit); a8d7 juga tidak aktif 30 hari.
- **Kuartet 0x874d.../0xad06.../0xe12c.../0xb735...**: satu entitas klaster
  bot-farm (funder debu bersama + hub bersama + exit tersinkron); 874d/ad06
  juga tidak aktif 30 hari.
- **0x77519fa2...**: bot-like (routing kontrak + exit seblok) + koin
  ketiganya COLLECT berbobot rendah (venue 259 hari pasca-formasi).
- **AEON**: dikeluarkan dari set koin (bukan ditolak sebagai wallet) —
  instrumen tidak berlaku (venue V4 saja).

---

## UNTUK METODE 3 (parent, live browser) — DAFTAR TARGET

**Instruksi baca:** untuk tiap koin di bawah, buka halaman Holders di BscScan
(token → Holders), dan cari:
1. **Top holder yang muncul di BANYAK koin sekaligus** (irisan holder antar
   koin — analog metode 1 tapi untuk holder SAAT INI, bukan pembeli awal).
   Prioritas: holder yang ada di top-50 di ≥3 koin dari daftar ini.
2. **Status holding kandidat metode 1:** apakah 0xf16b... (WATCH) masih
   memegang koin-koinnya? Apakah 0x9999... / kuartet masih memegang?
   (Menguji apakah "early buyer" masih holder = keyakinan vs flip.)
3. **Hub/provisioner klaster:** apakah 0x4982085c... / 0x9b79cc64... muncul
   sebagai top holder di IDOL/Q/UAI (mengukur skala operator klaster)?
4. **YANG DIABAIKAN di halaman holder:** alamat kontrak (router, pool,
   locker, tim), exchange, dan 23 alamat kontrak dari daftar tolak metode 1
   di atas; TRIO/PAIR/T7 (sudah dikecualikan); wallet feed/tier-ab yang
   sudah dikenal (hanya catat bila muncul, jangan laporkan sebagai baru).
5. **Untuk COLLECT:** holder page mencerminkan venue Sep 2026, bukan formasi
   Des 2025 — bobotkan lebih rendah, sama seperti di metode 1.

**Daftar koin target (14 + 1 bonus):**

| Koin | Token (BscScan) | Catatan holder page |
|---|---|---|
| AKE | 0x2c3a8ee94ddd97244a93bc48298f97d2c412f7db | — |
| ARIA | 0x5d3a12c42e5372b2cc3264ab3cdcf660a1555238 | — |
| IDOL | 0x3b4de3c7855c03bb9f50ea252cd2c9fa1125ab07 | Cek hub 0x4982085c... di sini |
| Q | 0xc07e1300dc138601fa6b0b59f8d0fa477e690589 | Cek hub 0x4982085c... di sini |
| JAGENT | 0x8e6442663a4f8c50b6132c68d42a30e7dfe4ae15 | Pool V2 USDT 0xe6efcdef2b720d1eca2b69edb7ef357725680bea |
| EVAA | 0xaa036928c9c0df07d525b55ea8ee690bb5a628c1 | Pool V3 USDT 0x26deb24a2623cf54452ab5183e2c34551831d54d |
| ESPORTS | 0xf39e4b21c84e737df08e2c3b32541d856f508e48 | Hanya 10 pembeli awal — holder page kecil, cepat dibaca |
| LYN | 0x302dfaf2cdbe51a18d97186a7384e87cf599877d | — |
| BASED | 0x1d28d989f9e3ccb8b15d0cec601734514f958e4d | — |
| JCT | 0xea37a8de1de2d9d10772eeb569e28bfa5cb17707 | — |
| SAFU-B13B | 0xdd806e436dda5588bf54061c11590c77ddc87777 | BUKAN SAFU NFT/token user — pakai alamat persis |
| AIN | 0x9558a9254890b2a8b057a789f413631b9084f4a3 | Cek apakah f16b masih hold (jual pool 8,2 m tercatat) |
| UAI | 0x3e5d4f8aee0d9b3082d5f6da5d6e225d17ba9ea0 | Cek hub 0x4982085c... di sini |
| COLLECT | 0x4b3d30992f003c8167699735f5ab2831b2a087d3 | Bobot rendah (venue Sep 2026) |
| AEON (BONUS, hanya metode 3) | 0x277add739c6e0477616948357af9e79fe1ec9b80 | Tidak terukur di metode 1 (venue V4 saja) — tapi holder page tidak butuh alamat pool, jadi BISA dibaca di metode 3. Pool V4 pertama: PoolId 0x25042161f871a34e77a7af1aff74aa1a0dc9b4c661fd53c7504948ad97f8d13f (pancakeswap-infinity-clmm, dibuat 2026-07-26). |

**Yang TIDAK perlu dibaca di metode 3:** halaman holder 23 kontrak tolak
(mereka bukan wallet); halaman pool V4 (tidak ada holder page per-pool
untuk Infinity — holder page token sudah cukup).

---

## Catatan keterbatasan (jujur)

- (d) profit tidak terverifikasi untuk siapa pun (arsip harga blok lama
  tidak tersedia di RPC gratis). Ini membatasi verdict terkuat menjadi WATCH.
- SAFU-B13B early set terpotong di 200/366 (cap metode) — irisan untuk
  SAFU-B13B hanya memakai 200 pertama; wallet peringkat 201–366 tidak
  terhitung (potensi kandidat terlewat, bukan kesalahan positif).
- COLLECT berbobot rendah (venue 259 hari pasca-formasi).
- 9999 funder tidak terselesaikan (cap 3.000 tx) — verdict bot-nya tidak
  bergantung pada funder.
- GMGN login-gated: tidak ada kaki yang butuh login yang dijalankan;
  tidak ada yang dicatat "terblokir" selain (d) arsip harga di atas dan
  AEON (instrumen V4).
- Semua alamat di laporan ini disalin dari output tool/file, bukan
  diketik — kecuali yang secara eksplisit ditandai sebagai transkripsi
  lama yang sudah diperbaiki (pool EVAA/JCT).
