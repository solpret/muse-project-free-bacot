# Riset Wallet Dalam — Koin Terbentuk mcap > $1 Juta, Early Buyer yang Masih Hold dan Bersih

- **Tanggal riset:** 2 November 2026, sore WIB (baca utama 17.35–18.00 WIB).
- **Perintah user:** 2 November 2026 ~17.33 WIB — metode pencarian wallet jangan terfokus hanya pada satu-dua koin; cari koin-koin yang sudah terbentuk dengan mcap di atas $1 juta, lalu lihat early buyer, smart wallet, whale, dan cabal yang MASIH HOLD dan walletnya BERSIH, dan telusuri lebih dalam.
- **Sifat pekerjaan:** READ-ONLY, BSC saja. TIDAK ADA transaksi, approval, signing, login GMGN, atau permintaan seed phrase/private key. TIDAK ADA file state/feed/cron/goal yang diubah: `tier-ab-watch-state.json` hanya dibaca, TRACKED_WALLETS feed tetap 14, snapshot Free Bacot tidak disentuh.
- **Halaman profil GMGN terbukti login-gated** pada 2 November 2026 ~17.31 WIB, jadi seluruh riset ini on-chain saja (Ankr `ankr_getLogs` sebagai module, `fast_rpc`, API publik GeckoTerminal). Tidak ada angka PnL dari GMGN di laporan ini.
- **File pekerja (bukti mentah):** `deep-search/child-discovery.md`, `deep-search/child-known-trio.md`, `deep-search/child-other-coins.md` di folder yang sama dengan laporan ini.

## 1. Ringkasan eksekutif — temuan keras

**Tidak ada satu pun wallet yang memenuhi SEMUA kriteria sekaligus** (repeat early buyer di banyak koin terbentuk + masih hold + bersih + aktif 48 jam terakhir). Dua alasan struktural:

1. **Koin lama sudah ditinggalkan early buyer-nya.** Di trio tertua (mubarak Maret 2025, SKYAI April 2025, EGL1 Juni 2025), SEMUA early buyer EOA kini bersaldo 0. Yang masih memegang sesuatu hanyalah pool/kontrak dengan akumulasi lanjutan — bukan wallet.
2. **Kriteria "masih hold" secara alami mengarah ke koin yang lebih muda.** Satu-satunya kandidat yang masih memegang posisi berarti berasal dari koin berumur minggu–bulan (GANG ~11 hari, IBS ~6,5 bulan, BORT ~1 tahun pada waktu baca), bukan dari koin-koin tertua.

**Kandidat terbaik yang tersisa (semua BARU, tidak ada di 50 wallet terpantau):**

| Peringkat | Wallet | Bukti singkat |
|---|---|---|
| 1 | `0xac739056e611d639abeb0b9a87da38bd297ba00e` (IBS #2) | Satu-satunya yang masih hold + AKTIF 48 jam terakhir (≥1.000 incoming IBS, terbaru mendekati head). Catatan: saldo jauh di atas beli awal → mostly akumulasi lanjutan. |
| 2 | `0xcd06af254d0da9dbf95f62a75361c4cab182f13b` (BORT #8) | PARTIAL bersih terbaik 43,8% + memegang mubarak 12.000. Tidak aktif 48 jam terakhir (di 8 koin yang dicek). |
| 3–5 | Klaster GANG #5/#6/#7 | PARTIAL bersih 21,6% / 22,0% / 13,7%, pola beli identik (blok sama, jumlah mirip) — sinyal klaster LEMAH, bukan bukti satu aktor. Tidak aktif 48 jam terakhir. |
| 6–7 | Perilaku saja, sudah exit | EOA beli awal terbesar mubarak dan SKYAI normal — bukan kandidat pantau, hanya referensi perilaku. |
| 8 | Klaster blok-0 SKYAI (6 wallet, satu unit) | Mengambil ~16,24% supply di blok creation — PERLU cek funding sebelum dipakai apa pun; semua sudah exit. Bukan kandidat bersih. |
| 9–10 | KOSONG | Tidak ada wallet lain yang memenuhi ambang. NIAN dan MAME: nol holder bersih. EGL1: praktis nol kandidat. |

**Bukan rekomendasi beli, bukan sinyal beli.** "Proxy profit" (beli awal + pegang/jual) BUKAN PnL terealisasi — tidak ada histori harga di log, jadi laporan ini tidak mengklaim PnL 30 hari terverifikasi untuk wallet mana pun. Promosi ke feed tetap butuh keputusan user dan, bila memungkinkan, konfirmasi GMGN yang sah.

## 2. Universe koin — 20 koin terbentuk mcap > $1 juta

Discovery (GeckoTerminal `trending_pools`, baca 2 November 2026 17.35 WIB) menghasilkan 15 koin; pekerja koin-lain menambahkan 5 koin dari halaman trending yang sama (baca ~17.35–17.45 WIB). Semua mcap di bawah adalah angka endpoint pada waktu baca, bukan angka live saat laporan dibaca.

| Koin | CA token | Pair PCS V2 (factory, diverifikasi on-chain) | Pool dibuat | Mcap USD (waktu baca) |
|---|---|---|---|---|
| AKE | `0x2c3a8ee94ddd97244a93bc48298f97d2c412f7db` | lihat file discovery | 2025-08-20 | 141.006.743,89 |
| Q (Quack AI) | `0xc07e1300dc138601fa6b0b59f8d0fa477e690589` | lihat file discovery | 2025-08-31 | 127.318.031,99 |
| IDOL (MEET48) | `0x3b4de3c7855c03bb9f50ea252cd2c9fa1125ab07` | lihat file discovery | 2025-06-10 | 57.938.868,48 |
| AIN (Infinity Ground) | `0x9558a9254890b2a8b057a789f413631b9084f4a3` | lihat file discovery | 2025-07-04 | 50.253.462,64 |
| JCT (JANCTION) | `0xea37a8de1de2d9d10772eeb569e28bfa5cb17707` | lihat file discovery | 2026-06-03 | 46.582.462,90 |
| mubarak | `0x5c85d6c6825ab4032337f11ee92a72df936b46f6` | `0xb7c6f7db26cde42550e4017bb9855bbaaa20eb44` | 2025-03-13 23:21:07 UTC | 43.829.274,25 |
| UAI (UnifAI) | `0x3e5d4f8aee0d9b3082d5f6da5d6e225d17ba9ea0` | lihat file discovery | 2025-11-04 | 40.339.760,43 |
| Beat | `0xcf3232b85b43bca90e51d38cc06cc8bb8c8a3e36` | lihat file discovery | 2025-11-19 | 37.118.398,18 |
| LAB | `0x7ec43cf65f1663f820427c62a5780b8f2e25593a` | lihat file discovery | 2025-10-13 | 33.849.985,18 |
| SKYAI | `0x92aa03137385f18539301349dcfc9ebc923ffb10` | `0xbc42145d5a574ede9b8860fca2a49eb7b239efa5` | 2025-04-20 03:42:03 UTC | 30.304.224,39 |
| DEBIT (Teller) | `0x66661c7229901f568f16bd1551b3ba826f83ce49` | lihat file discovery | 2026-08-24 | 24.079.749,76 |
| ARIA | `0x5d3a12c42e5372b2cc3264ab3cdcf660a1555238` | lihat file discovery | 2025-08-19 | 23.347.932,17 |
| COLLECT | `0x4b3d30992f003c8167699735f5ab2831b2a087d3` | lihat file discovery | 2025-12-26 | 13.350.557,84 |
| AEON | `0x277add739c6e0477616948357af9e79fe1ec9b80` | lihat file discovery | 2026-07-26 | 5.908.393,98 |
| ESPORTS (Yooldo) | `0xf39e4b21c84e737df08e2c3b32541d856f508e48` | lihat file discovery | 2025-07-19 | 2.231.520,55 |
| GANG | `0x0c6302401aa5325c2e36f170f52c00b1d220b405` | `0x0bd5ded695d61c2db15c703c345d57e039fd0b6d` | 2026-10-22 16:57:27 WIB | 2.286.276 |
| 年年 (NIAN) | `0xf4d5765e448774ed9482870420da7c3c4c787777` | `0x3568b85ca64dce06dc08d1d65042aa737276eb41` (pasangan B13B) | 2026-10-15 20:21:00 WIB | 3.285.792 |
| IBS | `0x255e746abb8d9acac00d6d023e5e63e3b8dfa7cd` | `0x2a4b99a9c4544d35e8d266111c50b67fea01d53d` (pasangan USDT) | 2026-04-22 12:58:29 WIB | 5.202.558 |
| MAME | `0x39d9b36aa0e7a1fee97d6ff614420f7308ba7777` | `0xf75cdee96765c6d230528c247fc21d11f9f3927a` (pasangan B13B) | 2026-09-24 23:11:24 WIB | 1.494.420 |
| BORT | `0x2a846aaaf896ef393ccb76398c1d96ea97374444` | `0x76c42dda1de814ac60951c2c89c77dbecfb86ffb` | 2025-11-04 23:45:10 WIB | 1.202.619 |

Catatan universe:
- **EGL1 TIDAK masuk tabel** (`0xf4b385849f2e817e92bffbfb9aeb48f950ff4444`): identitas token terverifikasi on-chain (`EGL1`/`EGL1`, 18 desimal, supply 1.000.000.000), tapi endpoint token GeckoTerminal mengembalikan 404 pada bacaan 17.36 WIB — mcap/pair tidak terverifikasi dari sumber itu. Dari pool-pool Gecko yang terbaca terpisah, mcap EGL1 terfragmentasi: V2 $3.447.352,81 vs USD1 $9.111.214,26 vs WBNB 1% $14.766.920,06 (rasio ~4,3x, bukan 10x persis) — konflik 10x sebelumnya TIDAK terputuskan. Status tetap PROVISIONAL.
- **SKYAI kini TERVERIFIKASI** on-chain (name/symbol `SKYAI`, 18 desimal, supply 1.000.000.000) — label INFERRED-nya gugur. Pair V2-nya memang pool terawal yang tercatat (20 April 2025).
- **Pair V2 bukan pasar pertama** untuk mubarak (pool lain ~13,75 jam lebih awal, 13 Maret 2025 09:36 UTC) dan EGL1 (pool USD1 ~26 jam lebih awal, 4 Juni 2025). "Early buyer" keduanya di laporan ini = early buyer pair V2, bukan buyer peluncuran absolut. Early buyer EGL1 yang berarti harus dicari di pool USD1 (di luar cakupan tugas ini).
- **Pool dibuat ≠ perdagangan dimulai:** NIAN tanpa transfer pair selama ~130.000 blok (~16 jam) setelah pool dibuat, lalu 30 pembeli pertama dalam 35 detik; IBS sebaliknya — 30 pembeli pertama tersebar ~68 jam (trickle lalu burst).
- **ID pair GeckoTerminal yang lebih panjang dari alamat 20-byte** (UAI, JCT, COLLECT, Beat) dikutip verbatim dari field `id` endpoint — untuk kerja lanjutan, pair harus diverifikasi ulang lewat factory `getPair`, bukan memakai ID itu mentah-mentah.
- Dicoret di tahap discovery: TART (mcap terbaca 0,0 meski FDV ~$13,4 juta — lag/tidak tersedia), LITY/JAGENT (mcap null), ARK (mcap 0), SAFU/B13B ($498.283 < $1 juta), Hachiko ($758.737 < $1 juta), IAO/ZIG (pool 19 Oktober–1 November 2026, terlalu baru untuk kriteria "terbentuk" di discovery).

## 3. Metode dan batas (wajib dibaca sebelum memakai peringkat)

- **Early buyer** = penerima Transfer token yang pengirimnya alamat pair, di window awal (trio: 200 blok pertama untuk mubarak/SKYAI, ~2 hari untuk EGL1 yang sepi; 5 koin lain: 30 pembeli pertama kronologis, beli awal dihitung 6 jam setelah beli pertama wallet itu). Semua selector dihitung programatik (`eth_utils.keccak`), bukan hand-type. Semua waktu dari timestamp header blok.
- **Masih hold** = `balanceOf` sekarang > 0 yang bermakna. Ambang debu: trio <1% dari beli awal; 5 koin lain ≤0,5% dari beli awal 6 jam = SOLD. Saldo > beli awal berarti ada akumulasi/transfer masuk lanjutan — dicatat, bukan dianggap posisi awal murni.
- **Bersih** = bukan kontrak/bot executor (cek `eth_getCode`), bukan hub funding sniper / funder sniper / klaster insider MSX / exchange / wallet tim-vesting, dan tanpa fast dump (jual ≥80% ke pair dalam ≤1 jam). Aturan coret lintas ≥3 launch TIDAK dapat diverifikasi dari dataset ini (tidak ada wallet yang fast-dump di ≥2 koin yang dicek, apalagi ≥3) — yang dilaporkan adalah fast dump per koin.
- **Linkage:** KUAT = shared funding / transfer langsung; LEMAH = co-buy saja. Tidak ada linkage KUAT yang ditemukan dalam cakupan ini, dan kata "terbukti insider" tidak pernah dipakai.
- **Batas metode Transfer (jujur):** buta terhadap transfer BNB native dan call tanpa event — funding tidak terlihat dari log Transfer, sehingga linkage funding TIDAK dapat dinilai di sini; `pair → buyer` tidak membedakan beli swap vs tarik likuiditas; waktu jual (kecuali jual ke pair ≤1 jam di 5 koin lain) tidak dihitung; tidak ada histori harga di log → tidak ada klaim PnL.
- **Cakupan aktivitas 48 jam (deep-dive koordinator):** incoming Transfer pada 8 token (GANG, NIAN, IBS, MAME, BORT, mubarak, SKYAI, EGL1) di window blok 130.847.216 (≈31 Oktober 2026 18:14 WIB) s.d. head 131.229.109 (2 November 2026 17:59:32 WIB) — ≈47,75 jam. Ini TIDAK mencakup jual keluar, transfer BNB native, atau token lain. "Tidak aktif" di laporan ini selalu berarti "tidak ada incoming Transfer pada 8 token itu di window itu".
- **Dua void yang dicatat pekerja dan dihormati di sini:** satu scan mubarak dari blok creation yang salah konversi dibuang total dan diulang dari blok benar (47.442.143); satu string pool IBS yang salah salin dinyatakan void, pair factory dipakai dan dikonfirmasi ulang. Satu bug selector `balanceOf` (hash penuh, bukan 4 byte) diperbaiki sebelum saldo dipakai — saldo trio dibaca ulang di blok 131.227.784.

## 4. Peringkat kandidat — bukti per wallet

### Peringkat 1 — `0xac739056e611d639abeb0b9a87da38bd297ba00e` (IBS #2) — BARU

- **Early buy:** IBS, blok 94.019.033, 22 April 2026 19:18:04 WIB, beli awal 6 jam 22,96 IBS.
- **Status sekarang:** saldo 26.554,05 IBS — HOLD secara angka, TETAPI saldo ~1.156x beli awal. Sebagian besar saldo sekarang berasal dari akumulasi/transfer masuk lanjutan, bukan posisi awal murni. Jual ke pair ≤1 jam: 0%.
- **Kebersihan:** EOA (bukan kontrak), bukan daftar coret, tanpa fast dump, bukan wallet user, bukan hub/funder sniper.
- **Deep-dive koordinator:** matriks saldo 21 koin menunjukkan ia HANYA memegang IBS (tidak memegang koin terbentuk lain). Tetapi ia satu-satunya yang AKTIF 48 jam terakhir: ≥1.000 incoming Transfer IBS di window (cap 1.000/page Ankr tercapai, jadi angka pastinya ≥1.000, bukan tepat 1.000), blok incoming 131.110.509–131.228.977, terbaru mendekati head. Nol incoming pada 7 token lain yang dicek.
- **Catatan terbuka:** frekuensi incoming setinggi itu (≥1.000 transfer dalam ~48 jam) belum dijelaskan — bisa akumulasi agresif, bisa juga peran mirip market-maker/router, bisa juga spam transfer masuk. Perlu pemeriksaan level transaksi (swap vs transfer masuk biasa) sebelum menjadikannya referensi. Bukan bukti "smart money" murni dari posisi awal.
- **Keputusan:** kandidat pantau terkuat yang tersedia, DENGAN catatan di atas. Bukan promosi otomatis.

### Peringkat 2 — `0xcd06af254d0da9dbf95f62a75361c4cab182f13b` (BORT #8) — BARU

- **Early buy:** BORT, blok 67.031.685, 4 November 2025 23:45:12 WIB, beli awal 6 jam 313.737,68 BORT.
- **Status sekarang:** saldo 137.264,53 BORT = 43,8% PARTIAL — PARTIAL bersih terbaik di seluruh riset. Jual ke pair ≤1 jam 56,2% (di bawah ambang fast dump 80%).
- **Kebersihan:** EOA, bukan daftar coret, tanpa fast dump.
- **Deep-dive koordinator:** memegang koin terbentuk lain — mubarak 12.000,0012 (plus debu IDOL di bawah 0,0001, diabaikan). Waktu beli mubarak-nya TIDAK ditelusuri di sini, dan ia BUKAN anggota 25 early buyer mubarak pertama — jadi ini multi-coin holder, BUKAN repeat early buyer yang terbukti. Nol incoming Transfer pada 8 token yang dicek di window 48 jam → pegangan ini lebih tua dari 48 jam, dan ia tidak aktif (di token-token itu) belakangan ini.
- **Keputusan:** kandidat pantau kedua. Kelemahan: tidak aktif 48 jam terakhir; bukti repeat-early-buyer belum ada.

### Peringkat 3–5 — Klaster GANG #5/#6/#7 — BARU (satu unit klaster, bukan 3 kandidat independen)

| Wallet | Beli awal (blok — WIB) | Beli awal 6 jam | Saldo sekarang | % dipegang | Jual ≤1 jam |
|---|---|---|---|---|---|
| `0xf5c318532169bb28ea41f19fc54c224818cba3b7` (#5) | 129.109.863 — 22 Okt 2026 16:57:30 WIB | 3.552.628,29 GANG | 766.439,37 | 21,6% PARTIAL | 0% |
| `0xb756710f115e5e928f387ee13f5ace52ebc31c06` (#6) | 129.109.863 — 22 Okt 2026 16:57:30 WIB | 3.530.317,01 GANG | 778.343,19 | 22,0% PARTIAL | 0% |
| `0x66c60bdb0f4b510a444dbcd2d172e3978f63b4e1` (#7) | 129.109.863 — 22 Okt 2026 16:57:30 WIB | 3.525.074,21 GANG | 483.630,74 | 13,7% PARTIAL | 0% |

- **Kebersihan:** ketiganya EOA, bukan daftar coret, tanpa fast dump.
- **Sinyal klaster (LEMAH, observasi saja):** blok beli sama persis, jumlah beli awal hampir identik (~3,53 juta), dan pekerja mencatat pola 13 buy yang mirip. Ini konsisten dengan satu operator ATAU tiga bot/strategi yang sama — tanpa shared funding/transfer langsung, tidak dapat dibedakan, dan tidak diklaim sebagai satu aktor.
- **Deep-dive koordinator:** ketiganya HANYA memegang GANG (tidak memegang koin terbentuk lain dari 21 yang dicek). Nol incoming Transfer pada 8 token yang dicek di window 48 jam → tidak aktif belakangan ini (di token-token itu).
- **Keputusan:** kandidat pantau sebagai satu unit klaster. Kelemahan: single-coin, tidak aktif 48 jam, sudah menjual sebagian besar (lewat jalur setelah 1 jam dan/atau transfer non-pair).

### Peringkat 6 — `0x52679d733a7d2c64bcda5494f46d6a39277e6d99` (mubarak, EOA beli awal terbesar) — BARU, PERILAKU SAJA

- Early buy mubarak blok 47.442.245, 13 Maret 2025 23:26:13 UTC, 59.951,99 token. Saldo sekarang 0. Deep-dive: tidak memegang satu pun dari 21 koin terbentuk yang dicek; nol incoming pada 8 token di window 48 jam. Bukan kandidat pantau — hanya bukti bahwa wallet ini pernah berperilaku sebagai early buyer mubarak. EOA beli awal mubarak terbesar berikutnya: `0x7627022104a71782abee28b24f2e5211bc925571` (34.005,36) dan `0xbc5d0f53ee314f7e143a000ad73a1d5eb9ad8956` (26.078,46) — keduanya juga kini 0.

### Peringkat 7 — `0x8ec6e31f6a87368c4edb478ae8199b355606ff59` (SKYAI, EOA "normal" terbesar) — BARU, PERILAKU SAJA

- Early buy SKYAI blok 48.512.776, 20 April 2025 03:42:15 UTC, 1.006.591,40 token. Saldo sekarang 0. Deep-dive: tidak memegang satu pun dari 21 koin terbentuk yang dicek; nol incoming pada 8 token di window 48 jam. Bukan kandidat pantau — hanya referensi perilaku. (EOA normal terbesar berikutnya: `0xab23d58a050a85f91109ebbd1ac068b7c8dc72e2` — 355.786,31, kini 0.)

### Peringkat 8 — Klaster blok-0 SKYAI (6 wallet, satu unit) — BARU, PERLU CEK FUNDING, BUKAN KANDIDAT BERSIH

- 6 EOA terpisah, 6 transaksi berbeda, mengambil total ~162,42 juta SKYAI (~16,24% supply) tepat di blok creation 48.512.772 (20 April 2025 03:42:03 UTC):
  - `0xa4e67515834e0e84a30907e379545cad5390a5bb` (86.788.881,58)
  - `0x6c9a77850fda7db7c90c3ed708114e38a40c27b0` (34.225.030,58)
  - `0xc87b8a3288eeb450045d215bacfd50527a4c4353` (18.320.460,99)
  - `0x19f0446b17751b21f0ab12a3a2e719f534975c25` (11.420.214,59)
  - `0xa7fdf94a1e267e0f24d1984e879d983cfd641612` (7.795.972,61)
  - `0x2d33193e9a4eba762da54f074bf5e9ef810f9600` (3.872.858,71)
- Semuanya kini bersaldo 0. Ukuran blok-0 + kecepatan = pola yang WAJIB dicek funding-nya sebelum dipakai apa pun; funding tidak tercakup metode Transfer di sini, jadi klaster ini dicatat sebagai "perlu cek funding", BUKAN sebagai insider dan BUKAN sebagai kandidat bersih.

### Peringkat 9–10 — KOSONG

Tidak ada wallet lain yang memenuhi ambang (hold bermakna + bersih). NIAN dan MAME: nol holder bersih di antara 30 pembeli pertama (satu-satunya PARTIAL di masing-masing adalah kontrak token itu sendiri — dicoret). EGL1: praktis nol kandidat (14 buyer V2, 11 kontrak, 10 beli debu <100 token; 3 EOA hanya membeli 1,14–2,49 token dan kini 0).

## 5. Klaster lain yang dicatat (observasi, bukan bukti linkage KUAT)

- **GANG #26/#27:** `0x174e7ad54e17d02a6fa019cdafff1b5e902c98ec` dan `0xcb44eaad62cd6763c15c3a726f98bc466026e291` — 7 buy, ~1,19 juta, sold ≤1 jam 57,2% identik. Keduanya sudah SOLD (saldo 0). Observasi pola identik saja.
- **BORT #29/#30:** `0x88240079221a8b66f9202979bbdd8523cd631292` dan `0xb4d2a713df19c906fe9e0fb0412396f44319e6d8` — 17 buy, ~148,47 ribu, sold ≤1 jam 72,1%, saldo sama persis 26,87. Observasi pola identik saja; keduanya SOLD (debu).
- **Co-buy antar koin (LEMAH):** kontrak `0x1231deb6f5749ef6ce6943a275a1d3e7486f4eae` (NIAN #20 + BORT #22, kontrak di keduanya, fast dump 126,9% di BORT) → CORET; juga terlihat sebagai penerima transfer pair GANG di chunk uji (bukan anggota 30 pertama GANG) — observasi, bukan keanggotaan. Kontrak `0xa01cd5b68265b972b73a713f6d824d1a6d3612b0` (mubarak + EGL1, saldo kini 0 di keduanya) → CORET, linkage LEMAH (co-buy) saja.
- **Linkage KUAT (shared funding / transfer langsung): TIDAK ADA yang ditemukan** dalam cakupan ini — dan tidak ada yang diklaim.

## 6. Yang dicoret — beserta alasannya

- **Kontrak/bot executor (dicoret, tetap tercantum di file pekerja):** mubarak 13 dari 25; SKYAI 2 dari 25; EGL1 11 dari 14; GANG 2 dari 30; NIAN 9 dari 30 (termasuk kontrak token sendiri); IBS 11 dari 30; MAME 6 dari 30 (termasuk kontrak token sendiri); BORT 10 dari 30. Termasuk pembeli terbesar mubarak (`0x00000060f4f81582668faee910080649438a7c31`, kontrak, 2.068.099,24 token, kini 0) dan pembeli terbesar EGL1 (`0x7035f2bfb370c740cdc60095c75966f04c47ddff`, kontrak, 11.600,87 token, kini 0).
- **Pool lain yang ikut "membeli" dari pair V2 (BUKAN wallet, dicoret):** pool mubarak `0x90a54475d512b8f3852351611c38fad30a513491` (kini 18.727.548,78 mubarak dari akumulasi lanjutan) dan pool USD1 EGL1 `0x6d76e7bb743fee795a2f00a317760acf822ee2be` (kini 23.589.368,69 EGL1).
- **Fast dump ≤1 jam (dicatat per koin, bukan coret lintas launch karena aturan ≥3 launch tidak terpicu):** GANG 14; NIAN 19 (mayoritas tepat 97,0% — pola seragam yang mencurigakan, dicatat sebagai observasi); IBS 3; MAME 2; BORT 14. Total 150 baris (149 wallet unik) di 5 koin lain: HOLD 2 (1 bersih + 1 kontrak), PARTIAL 7 (4 bersih + 3 kontrak/debu-edge), SOLD 141.
- **Hub funding sniper `0xf5988713400da6fc8a58ec9515e2b0df9b40b115` dan funder `0x318d2aae4c99c2e74f7b5949fa1c34df837789b8`:** TIDAK MUNCUL sebagai buyer di satu pun dari 214 baris (64 trio + 150 koin lain; pengecekan exact-match oleh pekerja). Kedua alamat itu hanya disebut di kalimat pengecekan, bukan sebagai data buyer.
- **Wallet user** (`0xeb237F6f9FB4e826739F0954e9768914F28b2c2E`, `0xcf3c6fc1bf670a8d3f03436395286f86dbee7418`): TIDAK MUNCUL di daftar mana pun — bukan kandidat, tidak ada flag yang perlu dibuat.
- **Klaster insider MSX / exchange / wallet tim-vesting:** tidak ada yang teridentifikasi positif dari data ini. Pembelian kontrak berukuran 5–13% supply dicatat sebagai kontrak, bukan diklaim sebagai tim.

## 7. Cross-check terhadap set terpantau (50 wallet)

- **NOL tumpang tindih.** Dari 232 alamat yang muncul di file pekerja (buyer + token + pair + factory), tidak satu pun yang sama dengan 50 wallet di `tier-ab-watch-state.json`. Semua kandidat peringkat 1–8 di atas adalah BARU (kategori (a)), bukan konfirmasi atas wallet yang sudah terpantau (kategori (b) = tidak ada).
- Implikasi: bila user memutuskan promosi, kandidat ini MENAMBAH cakupan, bukan mengonfirmasi yang lama. Tetapi promosi tetap butuh keputusan user — laporan ini tidak mengubah feed.

## 8. Deep-dive koordinator — matriks hold lintas koin + aktivitas 48 jam

- **Matriks saldo (dibaca koordinator, `balanceOf` via `fast_rpc`, 21 token × 7 wallet, desimal dibaca on-chain — semua 18 kecuali AEON 8):**
  - IBS #2: HANYA IBS 26.554,05.
  - BORT #8: BORT 137.264,53 + mubarak 12.000,0012 (+ debu IDOL <0,0001).
  - GANG #5/#6/#7: HANYA GANG masing-masing.
  - mubarak-EOA terbesar dan SKYAI-normal terbesar: TIDAK MEMEGANG satu pun dari 21 koin.
- **Aktivitas 48 jam (incoming Transfer, 8 token, blok 130.847.216–131.229.109):**
  - IBS #2 → IBS: ≥1.000 (cap halaman Ankr; blok 131.110.509–131.228.977). Token lain: 0.
  - BORT #8, GANG #5/#6/#7, mubarak-EOA, SKYAI-normal: 0 di semua 8 token.
- **Waktu blok lokal yang terukur dari header:** 0,4501 detik/blok pada window 384.000 blok — dipakai untuk menentukan blok ~48 jam, bukan asumsi.

## 9. Pertanyaan terbuka dan langkah lanjut yang disarankan (bukan eksekusi)

1. **Sifat ≥1.000 incoming IBS pada wallet peringkat 1:** periksa level transaksi (swap vs transfer masuk biasa, pengirim dominan) — apakah ini akumulasi smart atau peran mirip router/market-maker.
2. **Funding klaster blok-0 SKYAI:** cek 1-hop native funding (di luar metode Transfer — butuh sumber riwayat transaksi, bukan log) sebelum klaster itu dipakai apa pun.
3. **Early buyer EGL1 yang berarti:** cari di pool USD1 (4 Juni 2025), bukan pair V2 — itu pasar pertamanya.
4. **Waktu beli mubarak wallet peringkat 2 (BORT #8):** telusuri kapan 12.000 mubarak itu dibeli — bila ternyata beli awal juga, ia naik menjadi repeat-early-buyer yang sesungguhnya.
5. **Repeat-buyer scan di luar window first-30:** kandidat peringkat 1–5 hanya terbukti di satu koin masing-masing dalam window yang dicek; scan first-30 di koin terbentuk lain (AKE, Q, IDOL, AIN, JCT, UAI, Beat, LAB, DEBIT, ARIA, COLLECT, AEON, ESPORTS) dapat menguji apakah mereka repeat buyer — pekerjaan lanjutan yang disarankan, bukan klaim saat ini.
6. **Keputusan promosi:** tidak ada wallet di laporan ini yang memenuhi kriteria promosi penuh (≥3 token + PnL 30 hari terverifikasi). Bila user ingin menambah referensi, peringkat 1 dan 2 adalah kandidat diskusi pertama — dengan catatan masing-masing — dan pencatatan feed tetap menunggu perintah user.

## 10. Sumber dan waktu baca (audit trail)

- Discovery: API GeckoTerminal `networks/bsc/trending_pools` + endpoint token/pools — 2 November 2026 17.35–17.36 WIB.
- Trio: Ankr `ankr_getLogs` (module, 1.000/page, chunk 200 blok mubarak/SKYAI, 2.000 blok EGL1) + `balanceOf` ulang blok 131.227.784; pair via factory `getPair` on-chain; header blok = waktu.
- 5 koin lain: GeckoTerminal trending hal. 1–8 (~17.35–17.45 WIB) + Ankr `ankr_getLogs` (paging `pageToken`, chunk 10.000 blok) + `balanceOf` via `fast_rpc.call_many`; IBS endpoint pool Gecko sempat 404 (pair dari factory on-chain).
- Deep-dive koordinator: `fast_rpc` race/batch (head 131.229.109, 2 November 2026 17:59:32 WIB; window 48 jam dari blok 130.847.216) + Ankr `get_logs` topic-filter (Transfer + recipient).
- GMGN: tidak dipakai (login-gated, 2 November 2026 ~17.31 WIB).
