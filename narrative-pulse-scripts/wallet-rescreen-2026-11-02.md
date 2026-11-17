# Screening Ulang Wallet — Free Bacot / Modal Bacot

**Tanggal laporan:** Senin 2026-11-02, sore WIB
**Sifat:** READ-ONLY. Tidak ada file state, cron, atau feed yang diubah. Satu-satunya file baru adalah laporan ini.
**Metode utama:** Ankr `ankr_getLogs` (module, bukan CLI) topik Transfer, tanpa filter address (topics-only, tervalidasi); nomor blok dan timestamp blok via `fast_rpc.py`. Waktu blok ~0,45 detik. Cutoff tidak aktif: tidak ada transfer sejak **2026-10-31 15:30 WIB** (= 2026-10-31 08:30 UTC, Unix 1793435400).
**Set terpantau:** 50 entitas di `~/workspace/narrative-pulse/tier-ab-watch-state.json` (14 Tier A/B + 35 Tier C + 1 SENSEI W1).

## Ringkasan eksekutif

- **Dibuang (12, semuanya Tier A/B):** tidak ada Transfer token dalam 400.000 blok (~50 jam, mundur sampai ~2026-10-31 13:33 WIB, melewati cutoff dengan margin ~2 jam), 0 error query. Daftar di §1.
- **Dipertahankan (38):** 2 Tier A/B yang masih aktif hari ini + seluruh 36 Tier C + W1 yang semuanya aktif. Daftar di §2.
- **Kandidat baru terbaik (independen dari Tier A):** TRIO (3 wallet, 3 kaki awal blok-identik) dan PAIR (2 wallet, 2 kaki awal blok-identik) — keduanya EOA, baru, bukan co-buyer Tier A. Keduanya tetap butuh konfirmasi PnL GMGN sebelum dipakai sebagai acuan (§3, §5).
- **KOREKSI 2026-11-03 (alamat PAIR #1):** string PAIR #1 di § Peringkat 2 di bawah ini SALAH (43 karakter heksadesimal, bukan alamat valid) — alamat benar, bukti pemulihan, dan hasil re-check deep-search-2 ada di blok koreksi di § Peringkat 2. Koreksi ini tidak mengubah keputusan apa pun atas TRIO/PAIR.
- **Co-buy Tier A: NOL.** Tidak ada kandidat baru yang membeli bersama Tier A di 11 token yang diperiksa (satu-satunya hit Tier A adalah 0x8e96… di wangcai, sudah dikenal).
- **Klaster M dan R bukan sinyal beli.** Tier C + W1 terindikasi kuat sebagai gugus alamat yang di-seed bersama (distribusi massal jumlah identik + gelombang T7 serentak), bukan 36 aktor independen dan bukan klaster kredibel. Jangan pakai sebagai acuan beli (§4).
- **Tidak ada transfer langsung antar wallet terpantau** (token, 30 hari) dan tidak ada funder bersama di Tier A/B — ke-14 Tier A/B semuanya standalone satu sama lain.
- **Peringatan sebelum mencopot 12 wallet Tier A/B dari feed:** "tidak aktif" di sini artinya tidak ada Transfer token saja (transfer BNB native dan call tanpa event tidak terlihat metode screening). Karena 12 wallet itu adalah 12 dari 14 wallet tracked feed, pencopotan harus dikonfirmasi GMGN dulu — lihat §5 dan §6.

---

## 1. Daftar buang (12 wallet Tier A/B)

**Bukti:** untuk tiap wallet, query window menurun 50.000 blok (transfer masuk + keluar) dari blok acuan 131209849 sampai 400.000 blok tercakup (~130809849, ~2026-10-31 13:33 WIB). Hasil: 0 log, 0 error, 0 struktur tak valid, tidak ada window yang menyentuh batas 1.000 log (tidak ada risiko truncasi). Seluruh periode pasca-cutoff tercakup plus margin ~2 jam.

| # | Wallet | Keterangan |
|---|---|---|
| 1 | 0x13d1e9a96eba7906e1ede348c9bb604a03e46d02 | 0 Transfer dalam 400.000 blok; juga 0 transfer token dalam 30 hari (pekerja graf) |
| 2 | 0x5b2f11cab406f580a7c6faf620ee35daaf8648a5 | 0 Transfer dalam 400.000 blok; juga 0 transfer token dalam 30 hari |
| 3 | 0x6ba79dcc05a1056e19bf1021db4fca7be18b49e7 | 0 Transfer dalam 400.000 blok; aktif dalam 30 hari (23 keluar / 74 masuk) — diam 50 jam terakhir, bukan wallet mati |
| 4 | 0x75642756e4ba4cc8fbe76df2239cada046cfc854 | 0 Transfer dalam 400.000 blok; juga 0 transfer token dalam 30 hari |
| 5 | 0x8272c61cc59cc78d5fa06f3c2c0594def2e8db6a | 0 Transfer dalam 400.000 blok; juga 0 transfer token dalam 30 hari |
| 6 | 0x892200223bdfb11d2506c5ab1cae9222ce253acc | 0 Transfer dalam 400.000 blok; aktif dalam 30 hari (24 keluar / 64 masuk) — whale holder, diam 50 jam terakhir |
| 7 | 0x93e7c78ab0db6f4961bfe7cf254422cbf7b82e1c | 0 Transfer dalam 400.000 blok |
| 8 | 0xaab80f45b97d9dc86d9bea56a3e98274ba81026e | 0 Transfer dalam 400.000 blok; hanya 2 masuk singleton dalam 30 hari |
| 9 | 0xb787a5603d20e61585e20e7a13a1c0d6c03a1462 | 0 Transfer dalam 400.000 blok; hanya 3 masuk singleton dalam 30 hari |
| 10 | 0xbe5905cf7a8bebd97fdc5d69a120b0ea720d3cdf | 0 Transfer dalam 400.000 blok; hanya 1 masuk singleton dalam 30 hari |
| 11 | 0xda91cefe240175e6fab56271110427a4195ab71f | 0 Transfer dalam 400.000 blok; aktif dalam 30 hari (11 keluar / 17 masuk) — diam 50 jam terakhir |
| 12 | 0xf6a8280c997c4b4daa606e2c8c37b5a79b8ae2cc | 0 Transfer dalam 400.000 blok; 14 masuk 0 keluar dalam 30 hari — diam 50 jam terakhir |

**Catatan penting:** "buang" di sini mengikuti aturan user (tidak aktif 48 jam) dengan metode Transfer. Empat dari 12 wallet (0x6ba7…, 0x8922…, 0xda91…, 0xf6a8…) terbukti aktif dalam 30 hari — mereka hanya diam 50 jam terakhir. Lima wallet (0x13d1…, 0x5b2f…, 0x7564…, 0x8272…, 0x93e7…) bahkan 0 transfer token dalam 30 hari penuh. Sebelum pencopotan dari `TRACKED_WALLETS` feed, konfirmasi GMGN disarankan (§5) karena metode ini buta terhadap transfer BNB native dan call tanpa event.

## 2. Daftar pertahankan (38 wallet)

### 2a. Tier A/B aktif (2)

| Wallet | Transfer terakhir | Bukti |
|---|---|---|
| 0x2325f175975abdbcde555c79cc8e63381d28551b | Blok 131207280, 2026-11-02 15:15 WIB, KELUAR, token 0xf774F6a406E2407Db1312Adb2B71f878Fe6A7777, tx 0x0536e34593972d76e4156f08f228fbe0840f2af8a8d88c6276f70a87f9079903 | Log Ankr + timestamp blok (2 titik) |
| 0x8e966a9f17beab1ea50039434c2a14ad9e09b8d6 | Blok 131205685, 2026-11-02 15:03 WIB, KELUAR, token 0xeCf912481E900aCa404876091a25AeE8ed847777 (剑来), tx 0xcf8af016f923288dbcda74bd9a7acddc52eca4ab23ac33b23f5773ffc32928a9 | Log Ankr + timestamp blok (2 titik) |

### 2b. Tier C + SENSEI W1 (36) — semuanya AKTIF

Run 2026-11-02 ~15:35–15:40 WIB, blok acuan beku 131209736. 34 wallet ditemukan di window pertama (50.000 blok terakhir); hanya 2 yang aktivitas terakhirnya lebih tua (2026-11-01 sore). Verifikasi silang: `eth_chainId` 0x38 (BSC) + 5/5 sampel receipt cocok dengan nomor blok log Ankr + timestamp header blok via RPC.

Legenda token (alamat persis dari field `address` log): T1 = 0x95E694C6927eAD3f308d2E703649814d171Cb428; T2 = 0x95817f0dA8dA9C4Ea8b1058648A167cC50277777; T3 = 0x1CA82F828d41B93cF4A463618D9E2Fa424c7A61c; T4 = 0xD3F918244b8B93f707D086115989BFF130057777; T5 = 0x753f300916cf37a4Aa406FB0141143E0e7347777; T6 = 0xe918CcBaDcDB209bcD6D65905B47425289522951; T7 = 0xB4e32E16185Ecee92c2C465F27bE799b93797777; T8 = 0xa4A9f1A5Cf0e2c7ca80AEFF59d3F0E5974fa0eF0; T9 = 0xBcaCf6D22583345FD723f003c5D6b5069F56Cf69.

| # | Wallet | Blok | Waktu WIB | Token | Arah |
|---|---|---|---|---|---|
| 1 | 0x9856bac497634a62a970233bc4b0f5bb52c844c1 | 131029703 | 2026-11-01 17:03 | T1 | keluar |
| 2 | 0x3628764a6576b8dfb31fba0aac6a333b64851423 | 131209193 | 2026-11-02 15:30 | T2 | masuk |
| 3 | 0xa0c1e94fbc1a93e39f5eb828f960aa080a9d9b9e | 131209202 | 2026-11-02 15:30 | T2 | masuk |
| 4 | 0x40a8b422f09fe7f630ccb3dbd07ea258577b784c | 131028538 | 2026-11-01 16:54 | T3 | keluar |
| 5 | 0xc7c5faa270eb2394c7bf9f411fed0d0126f2eb74 | 131209732 | 2026-11-02 15:34 | T4 | keluar |
| 6 | 0xad94ee77d0e868d299fb3e92b9d67560257f656d | 131209733 | 2026-11-02 15:34 | T5 | keluar |
| 7 | 0x38031ca8a54526f9fe90f11f07b55ae5fc01036a | 131209734 | 2026-11-02 15:34 | T4 | keluar |
| 8 | 0x7488d5da6a6097de0ff88c7492c62c2fd1e56650 | 131209667 | 2026-11-02 15:33 | T6 | masuk |
| 9 | 0xdb2d83f907965fb05ac23b8d40d3a327fc9ea52b | 131209133 | 2026-11-02 15:29 | T7 | keluar |
| 10 | 0xc621946845d0fd5d1dbc6d6beb3e22aed39d7050 | 131209197 | 2026-11-02 15:30 | T7 | keluar |
| 11 | 0xf795c5250f3d4006283a0d0dbb378dc0e69df923 | 131209169 | 2026-11-02 15:29 | T7 | keluar |
| 12 | 0x9cdd08f30188c2732cdbcac8eebf4e6e8bf0c1b2 | 131209149 | 2026-11-02 15:29 | T7 | keluar |
| 13 | 0xaa49e7fec503664a39598645c7a3fbfa0374380d | 131208933 | 2026-11-02 15:28 | T7 | keluar |
| 14 | 0x82c6085f9ec2722fd6c8fc47577368a156a25b9b | 131209355 | 2026-11-02 15:31 | T8 | masuk |
| 15 | 0x3154f6949285ee7ac1593bd2bdf974adb6731c32 | 131209007 | 2026-11-02 15:28 | T7 | keluar |
| 16 | 0xca4e67bb5737c095bd3a80f79ecc6607e5723f1a | 131209104 | 2026-11-02 15:29 | T7 | keluar |
| 17 | 0xe9ed24db105a6b15f880025ed9ad024c06783895 | 131209083 | 2026-11-02 15:29 | T7 | keluar |
| 18 | 0x3a39aa05b149141a4bfc7d73611dceb0557b39c4 | 131209100 | 2026-11-02 15:29 | T7 | keluar |
| 19 | 0xcb08c02c0a386a10773a2c6589e7089a3dd5aca3 | 131209009 | 2026-11-02 15:28 | T7 | keluar |
| 20 | 0xb940e4cd40ea9e887cbc92879062676e2bc4a924 | 131209172 | 2026-11-02 15:29 | T7 | keluar |
| 21 | 0x4522e661d9c94ec54b37e71896351a7440ec4f07 | 131209128 | 2026-11-02 15:29 | T7 | keluar |
| 22 | 0x5b4beded36c1ea380abe8c6a6a0c4408f38e5024 | 131209079 | 2026-11-02 15:29 | T7 | keluar |
| 23 | 0xc6591fde9b44aa081062c9fc6ee48e443d24ef57 | 131208631 | 2026-11-02 15:25 | T7 | keluar |
| 24 | 0x362396125a55d932a09f0a5182140cbbcaf30b70 | 131209158 | 2026-11-02 15:29 | T7 | keluar |
| 25 | 0xf9689b9d0a675ff9ad876f1d766fb460dbde7d20 | 131209032 | 2026-11-02 15:28 | T7 | keluar |
| 26 | 0x2cc8192fc62e3640de91e75582cf3dbbd571b970 | 131208979 | 2026-11-02 15:28 | T7 | keluar |
| 27 | 0x1cce4ec5a7c5e8cfc8dedd771876c61e60b8b645 | 131208979 | 2026-11-02 15:28 | T7 | keluar |
| 28 | 0xc0c84518ced6a61d2a4f4a50bc0f438e0cb1031b | 131209193 | 2026-11-02 15:30 | T7 | keluar |
| 29 | 0xc194efe22e874a3fe666b5de5a8fd369f12c32d5 | 131209215 | 2026-11-02 15:30 | T7 | keluar |
| 30 | 0xa952331ea48ea9c00c4608d8259c186021331f31 | 131209063 | 2026-11-02 15:29 | T7 | keluar |
| 31 | 0x92bc32975b0fbf1a19caf7cc6e3f9ea4092fd314 | 131209146 | 2026-11-02 15:29 | T7 | keluar |
| 32 | 0x9b519f5d52cdd03e4b10484829bc137eef1f8c1a | 131209075 | 2026-11-02 15:29 | T7 | keluar |
| 33 | 0xfdec62fde1f1dc56c0ba5e50f4cae5d6c63762bf | 131209034 | 2026-11-02 15:28 | T7 | keluar |
| 34 | 0x64e893a4c5c930b2cc68b054792cbc66344aeb9a | 131209124 | 2026-11-02 15:29 | T7 | keluar |
| 35 | 0x81c3d1b4c9433bd5e52544ca96b19cfa9eb5de36 (SENSEI W1) | 131207880 | 2026-11-02 15:20 | T9 | keluar |
| 36 | 0x97bd895f8123a7837368df410e7d308246c0b3e9 | 131208979 | 2026-11-02 15:28 | T7 | keluar |

**Observasi gelombang T7 (penting):** 26 dari 36 wallet di atas mengirim token T7 yang sama (0xB4e32E16185Ecee92c2C465F27bE799b93797777) dalam jendela sempit 2026-11-02 15:25–15:30 WIB, termasuk 3 wallet di blok yang sama 131208979. Ini konvergen dengan temuan klaster M (§4): set Tier C ini bergerak terkoordinasi, bukan independen. Identitas/nama token T7 masih pertanyaan terbuka (§5).

---

## 3. Kandidat baru berperingkat

Semua kandidat di bawah ini **BARU**: tidak ada di 50 wallet terpantau maupun di `wallet-priority-full.md`, dan semuanya EOA (dicek `eth_getCode` = `0x`) kecuali dinyatakan lain. **"Proksi untung" = beli awal + (jual / masih pegang), BUKAN PnL GMGN** — tidak ada histori harga buy-vs-sell untuk kaki-kaki ini, jadi PnL realisasi TIDAK PERNAH diklaim. Metode early buyer: penerima transfer dari sale source (pengirim tersering, di luar zero address dan kontrak token) dalam 2 jam pertama setelah transfer penjualan pertama. 11 token diproses (RIKI, BIBIAI, charity, WTB, aiPRO, wangcai, GANG, ok, COOL-flap, HI, MSX): total 12.222 buyer awal berbeda; 1.119 di ≥2 token, 317 di ≥3, 115 di ≥4, 32 di ≥5, 17 di ≥6, 2 di ≥7–8.

### Peringkat 1 — TRIO, satu unit operator, 3 wallet

`0x38E4639C235d826a243f46e4BD8B5569636e1642` + `0xA0B725C40b8353993a9501FCdE943C8445048344` + `0x5816102760793e60ebd097c344b732b0537ccb59`

Bukti koordinasi terkuat di seluruh dataset: 3 kaki awal, ketiganya di **BLOK YANG SAMA persis** untuk ketiga wallet, masing-masing tepat 1x beli (n=1).

- **RIKI** — beli pertama blok 130301036, 2026-10-28 21:56:39 WIB (+15 detik setelah transfer penjualan pair pertama 21:56:24; +18,7 menit bila memakai anchor GMGN 21:38 — tetap <1 jam di kedua anchor). Jumlah: 3.343.541,90 / 2.831.916,98 / 2.184.142,26 (urutan besar sama di semua kaki). Exit: jual 2 tranche ke pair pada 22:01 dan 22:13 WIB (~100% + tax), saldo RIKI kini **0** di ketiganya. Proksi: exit penuh cepat, PnL tidak diketahui dari log.
- **WTB** — beli pertama blok 130646624, 2026-10-30 17:09:44 WIB (+3,6 menit setelah penjualan pertama 17:06). Jumlah: 1.660.019,11 / 1.199.916,23 / 1.338.127,33, n=1. Exit: jual ~55% pada 17:17 WIB (menit yang sama untuk ketiganya); **masih pegang kini: 747.008,60 / 539.962,30 / 602.157,30**. Proksi: partial exit + hold 3 hari.
- **ok** — beli pertama blok 130791540, 2026-10-31 11:16:52 WIB (+24 menit setelah penjualan pertama 10:52:39). Jumlah: 1.009.666,14 / 996.870,36 / 984.316,40, n=1. **NOL transfer keluar sejak beli sampai kini** (dicek log keluar ok penuh); saldo kini persis sama dengan jumlah beli (peringkat holder ok #27/#28/#29). Proksi: diamond hold 100%.
- Tambahan: pegang COOL-flap kini 1.462.681,76 / 1.442.957,68 / 1.423.629,89 (peringkat #24/#25/#26) — tapi beli COOL-nya **bukan** awal (di luar window 2 jam), jadi bukan kaki ke-4.
- **Penilaian:** memenuhi bar 2–3 entri awal (tepat 3), dengan 2 kaki masih dipegang (WTB parsial, ok penuh). Realisasi untung belum terbukti — butuh konfirmasi GMGN (§5).

### Peringkat 2 — PAIR, satu unit operator, 2 wallet

`0x2fc2a32f16d683038187b87b87e0409d122da6f17d4` + `0x95e02ed458ba54fd640f5b3956ff4178aaC809d5`

> **KOREKSI 2026-11-03 — ALAMAT PAIR #1 DIPULIHKAN (string di atas INVALID, riwayat tidak dihapus).**
> String PAIR #1 di atas (`0x2fc2a32f16d683038187b87b87e0409d122da6f17d4`) berukuran **43 karakter heksadesimal, bukan 40**, sehingga BUKAN alamat valid. **Semua pengecekan PAIR #1 di laporan ini dan di deep-search-2 yang memakai string itu adalah VOID (bukan NIHIL).** Pengecekan TRIO, PAIR #2, IBS #2, BORT #8, GANG, hub/funder di laporan-laporan itu tidak terdampak (string-string itu 40 karakter).
> **Alamat PAIR #1 yang benar: `0x2fc2a32f16d683038187b87e0409d122da6f17d4`.** Perbedaan persis: string lama menggandakan segmen `b87` (…`8187b87b87e0409`… vs …`8187b87e0409`…). Alamat benar ini TIDAK ditebak — dipulihkan dari log on-chain (di bawah).
> **Bukti pemulihan (baca read-only 2026-11-03, Ankr `ankr_getLogs` sebagai module + `fast_rpc` `call_many`, token ok `0xc853d8253f0d8346ca80f3f6af53e49a763e7777`, 18 desimal):**
> 1. Log Transfer ok di **blok 130788409 persis** (blok beli pertama PAIR menurut laporan ini): tx `0xef1d6635c8c53e8dc73a3700d67dc4d4281b6b8a94e94ff073fb19d7e7623dd0` dari `0xb3dbd9e32214efade545b75093870c4237efa4a7` ke alamat benar, **5.575.561,15 ok**; di blok yang sama PAIR #2 menerima 5.911.039,47 ok (tx `0x8245ae40cedbab3891ee7ba223d5cf9d4ab893ae98ddf7cdd836a4bce6887d87`).
> 2. Saldo kini `balanceOf(ok)`: alamat benar = **10.639.412,36** (persis angka laporan ini, peringkat #7); kontrol positif cocok persis: PAIR #2 = 11.192.428,27 dan TRIO #1 = 1.009.666,14.
> 3. **24 transfer masuk ok** ke alamat benar dalam window 130788409–130804409, total persis **14.197.551,93** (persis angka laporan ini).
> 4. Transfer keluar ok dari alamat benar di ketiga blok jual laporan ini: **130792780, 130792859, 130794494** (ke pair `0xb3db…` + tax ke kontrak token).
> 5. COOL-flap (`0x21aeddf21ee854f20cb497b0430437c4ab367777`) di **blok 130800266**: alamat benar dan PAIR #2 sama-sama menerima COOL.
> **Re-check deep-search-2 (2026-11-03, atas alamat benar):** 287 baris first-30 V2 dari 10 koin (AKE/Q/IDOL/AIN/Beat/ARIA/COLLECT/AEON/ESPORTS masing-masing 30 + LAB 17), 214 alamat unik — **exact-match terhadap alamat benar: NIHIL**; substring `2fc2a32f` tidak muncul di file pekerja deep-search-2 mana pun kecuali string invalid itu sendiri. Jadi **tidak ada baris first-30 non-kandidat yang merupakan PAIR #1**, dan tidak ada kandidat baru yang muncul dari perbaikan ini. (Sapuan saldo ok atas baris-baris itu tidak diselesaikan karena proses batch RPC menggantung dan dihentikan — tidak dibutuhkan: identitas sudah diputuskan oleh exact-match, dan 19 kandidat bersih deep-search-2 sudah terverifikasi memegang 0 ok di §9 laporan itu.)
> **Status akhir:** pemulihan ini menutup temuan integritas §9 deep-search-2 untuk PAIR #1. PAIR tetap BUKAN promosi dan tidak ada perubahan feed/threshold/watch set apa pun dari koreksi ini — itu keputusan user tersendiri.

Koordinasi blok-identik di SEMUA kaki (beli dan jual, kedua wallet, kedua token).

- **ok** — beli pertama blok 130788409, 2026-10-31 10:53:23 WIB (+44 detik setelah penjualan pertama), n=24 beli dalam 2 jam, total awal 14.197.551,93 / 14.607.597,24. Jual 3 tranche pada blok 130792780, 130792859, 130794494 (11:26–11:39 WIB, blok sama untuk kedua wallet), lalu **akumulasi ulang** — saldo kini **10.639.412,36 (peringkat ok #7) / 11.192.428,27 (peringkat ok #6)**. Proksi: hold besar, belum realisasi.
- **COOL-flap** — beli pertama blok 130800266, 2026-10-31 12:22:20 WIB (+13 detik setelah penjualan pertama), n=4, total 31.382.680,78 / 33.013.159,94. Jual 100% pada blok 130800298 dan 130800490 (12:22 dan 12:24 WIB, blok sama untuk kedua wallet) — **round-trip penuh dalam ~2 menit**, saldo COOL kini **0**. Proksi: flip kilat, PnL tidak diketahui dari log.
- **Penilaian:** 2 entri awal, stake ok saat ini terbesar di antara semua kandidat baru. Bukan sniper murni (mereka menahan bag ok besar 2 hari), tapi kaki COOL-nya adalah flip 2 menit — pola exit cepat parsial, wajib ditanyakan di §5.

### Peringkat 3 — `0x9505d34c664d5f8a44bd00776d4ec500176396f9` (solo, EOA)

5 kaki awal: RIKI 2026-10-28 22:07 (n=2, total 249.844) | WTB 2026-10-30 18:08 (n=1, 62.313) | ok 2026-10-31 11:16 (n=1, 101.679) | COOL-flap 2026-10-31 12:23 (n=2, 998.119) | HI 2026-10-31 14:43 (n=2, 74.532). Saldo kini: RIKI 0, ok **917.939,29 (peringkat #31, ~9× beli pertama)**, COOL 0, HI belum dicek. Entri terbanyak kedua setelah kontrak-kontrak yang dikecualikan, tapi ukuran kecil dan tanpa tanda koordinasi blok — kandidat frekuensi, bukan kandidat koordinasi.

### Peringkat 4 — `0xc6879327aa265f77fa29da47ff410af1f3dd8371` (solo, EOA)

4 kaki awal: RIKI 2026-10-28 21:57 (n=11, total 5.252.768) | ok 2026-10-31 10:55 (n=10, 5.538.248) | COOL-flap 2026-10-31 12:23 (n=2, 3.555.799) | HI 2026-10-31 14:28 (n=1, 16.128). Saldo kini: RIKI 0, ok 0, COOL 0 (HI belum dicek). Ukuran menengah, tapi exit 100% di 3 kaki yang dicek — profil flipper.

### Peringkat 5 — `0xc605b03c97f0608c2534dcc8d057481a92df153d` (solo, EOA)

5 kaki awal: BIBIAI 2026-10-29 22:06 (n=1, 43.321.166,88) | WTB 2026-10-30 17:08 (n=6, 5.978.884,81) | ok 2026-10-31 11:03 (n=2, 3.642.264,58) | COOL-flap 2026-10-31 13:04 (n=3, 8.135.344,12) | HI 2026-10-31 (n=6, 5.321.741,93). Saldo kini: **0 di kelima token**. Exit rate 100% — flipper/sniper sampai terbukti sebaliknya lewat PnL GMGN. (Awas: alamat ini 42 karakter, berakhir `…153d`; bentuk `…153` yang terpotong sempat dipakai di satu cek awal dan hasilnya batal — hanya alamat lengkap yang dipakai.)

### Peringkat 6 — `0x671ddcc0a6786a87ee54e76579c1af5ef66307d3` (solo, EOA)

3 kaki awal, ukuran sangat kecil: RIKI 2026-10-28 22:00 (n=5, total 15.082) | ok 2026-10-31 11:05 (n=3, 35.654) | COOL-flap 2026-10-31 12:23 (n=1, 65.629). Saldo kini: RIKI 4.548,31 (pegang ~30%), ok 35.654,22, COOL 0. Kandidat kecil; bobot rendah.

### Peringkat 7 — `0x4740acfd46970970d8a590da5f05f2f31f24ebc9` dan `0xef395d6a8ef0fa4f2593ee3e10b9fd4df1fa9c2e` (solo, EOA)

- `0x4740…`: kaki awal BIBIAI (n=6) + HI (n=3); pegang kini MSX peringkat #21 (1.834.733,19) + BIBIAI peringkat #29 (4.125.321.676,19). 2 entri + 2 hold top-50.
- `0xef39…`: kaki awal WTB (n=1) + HI (n=3); pegang kini COOL-flap peringkat #5 (20.308.036,32) + WTB peringkat #50 (3.072.335,07). 2 entri + 2 hold top-50.
- Keduanya butuh cek saldo per-kaki + PnL (§5); peringkat di bawah trio/pair karena tidak ada bukti koordinasi blok.

### Peringkat 8 — `0xcc1b3182eE21Ed172216453f6fd4086b7ac34d0d` (EOA, kandidat anggota ke-4 trio — LEMAH)

Kaki awal: RIKI 2026-10-28 22:07 (n=2, 250.291) | BIBIAI 2026-10-29 21:53 (n=1, 69.591.367) | WTB 2026-10-30 18:08 (n=1, 62.880); plus COOL-flap awal via kontrak Flap 0xe2ce… pada 2026-10-31 12:23:15 (431.175,08) + 12:23:40 (541.051,42); pegang kini ok 909.251,68 (peringkat #32, beli belakangan — bukan awal) dan COOL 315.001,39 (peringkat #40, ~68% sudah dijual). **Bukan** anggota inti trio (tidak ada di blok trio mana pun, tidak pegang ok sejak awal), tapi pola multi-token + hold ok/COOL-nya mirip — asosiasi lemah, bukan bukti.

### Peringkat 9 — holder-only SKYAI/EGL1 (EOA, TANPA bukti beli awal — paling rendah)

- SKYAI peringkat #20 baru `0x6Ddd0E38852F38E21413B0d23c209Aa520E2a405` (2.129.476,56) dan #25 baru `0x586a024a61221406F1C95804C75f4155a90Ce76E` (1.510.796,82); EGL1 peringkat #1 `0x93F543808eF836b32E304939428cedF9b8260E7B` (30.000.100 — angka bulat, kemungkinan tim/vesting) dan #4 `0xd79C0766Fa1a226295441df0258119206576D236` (20.899.484,57). Keempatnya EOA, tidak ada di set awal 11 token mana pun, dan pool SKYAI/EGL1 berasal dari Apr/Jun 2025 sehingga pembeli awal sejati berada di luar window 30 hari — **tidak boleh diklaim sebagai early buyer**. Hanya prospek holder untuk konfirmasi GMGN.
- Persistensi holder SKYAI 2026-10-31 → kini (holder 88.983 → 89.857): hampir semua snapshot bertahan dengan saldo identik (0xaab8 #2 96.523.274,52; 0xb787 #8 24.845.554; 0xadff #9 21.208.860,87; 0x8922 #12 5.898.875,97; 0x93e7 #13 4.635.242,41; 0x6ba7 #14 3.198.758,64; 0x8272 #15 2.686.967,89; 0x7564 #16 2.643.589,02; 0x5b2f #17 2.637.497,82; 0xbe59 #18 2.380.266,41; 0x511d #19 2.166.973,79; 0x13d1 #22 1.677.981,56). Pengecualian: Gate Cold #1 tumbuh 172,75 jt → 244,73 jt; Bitget 33,26 jt → 33,86 jt; 0xe3d6 30,66 jt → 30,75 jt; 0x6778 turun 2.037.022 → 1.998.149; 0xe4f2 turun 1.809.419 → 1.783.435. EGL1 kini 106.844 holder. Catatan: `0x511d…` (SKYAI #19) kini juga mubarak #43 (718.483) — tapi sudah tercatat di file prioritas, jadi bukan kandidat baru.
- Alamat survivor yang dipakai (koreksi atas laporan interim yang sempat salah): SKYAI = `0x92aa03137385f18539301349dcfc9ebc923ffb10` (pool V2 `0xbc42145d5a574ede9b8860fca2a49eb7b239efa5`, pool 20 Apr 2025; status survivor INFERENSI, MCAP live ~$31,16 jt); EGL1 = `0xf4b385849f2e817e92bffbfb9aeb48f950ff4444` (PROVISIONAL — crawl indeks ~$98,6–99,89 jt vs live ~$9,55 jt, konflik 10× belum terselesaikan); mubarak = `0x5c85d6c6825ab4032337f11ee92a72df936b46f6` (BEST-SUPPORTED). 28 kontrak "SKYAI/WBNB" di `fast_discovery_state.json` adalah klon hourly 2026-11-01/02, BUKAN SKYAI survivor.

### Profil 30 hari per kandidat (proksi on-chain; PnL realisasi tidak tersedia)

| Kandidat | Entri awal (11 token) | Win rate proksi | Drawdown / rug | Frekuensi & catatan |
|---|---|---|---|---|
| TRIO (3 wallet) | 3/3 sama (RIKI, WTB, ok) | Tidak dapat dihitung tanpa harga; 2 dari 3 kaki masih dipegang (WTB ~45%, ok 100%) + COOL dipegang | Tidak ada bag rug: RIKI exit sukarela <17 menit, bukan nyangkut; semua token kaki masih punya holder | Disiplin n=1 di semua kaki; aktivitas on-chain trio terentang 1 Okt (funding WBNB pertama) → 31 Okt; **tidak ada rekam 30 hari penuh** — klaim 30 hari tidak bisa dibuat dari data ini |
| PAIR (2 wallet) | 2 (ok, COOL) | Tidak dapat dihitung; 1 hold besar (ok #6/#7), 1 flip penuh 2 menit | Tidak ada bag rug; ok diperdagangkan lalu diakumulasi ulang | 24 beli ok + 4 beli COOL dalam 2 jam — trader aktif, bukan sekali beli |
| 0x9505 | 5 (RIKI, WTB, ok, COOL, HI) | Tidak dapat dihitung; 1 hold (ok #31), 2 exit penuh (RIKI, COOL) | Tidak ada bag rug yang terbukti | Ukuran kecil; 5 kaki dalam 4 hari (28–31 Okt) |
| 0xc687 | 4 (RIKI, ok, COOL, HI) | Tidak dapat dihitung; 0 hold di 3 kaki yang dicek | Tidak ada bag rug yang terbukti | Exit penuh dominan — mirip flipper |
| 0xc605…153d | 5 (BIBIAI, WTB, ok, COOL, HI) | Tidak dapat dihitung; 0 hold di 5/5 kaki | Tidak ada bag rug yang terbukti, tapi exit 100% di semua kaki | Pola rotasi penuh — butuh PnL untuk membedakan trader terampil vs sniper |
| 0x671d | 3 (RIKI, ok, COOL) | Tidak dapat dihitung; hold parsial RIKI + ok kecil | Tidak ada | Ukuran sangat kecil |
| 0x4740 / 0xef39 | 2 + 2 (masing-masing) | Tidak dapat dihitung; keduanya masih pegang 2 top-50 | Tidak ada | Hold top-50 adalah satu-satunya proksi positif |
| 0xcc1b | 3 + COOL awal via Flap | Tidak dapat dihitung; hold ok + COOL parsial | Tidak ada | Asosiasi trio lemah |
| Holder SKYAI/EGL1 | 0 kaki awal | N/A | N/A | Hanya holder; bukan early buyer |

**Pernyataan jujur 30 hari:** tidak satu pun kandidat yang punya rekam perdagangan 30 hari yang dapat diverifikasi dari log saja. Aktivitas tertua yang terlihat adalah funding WBNB trio pada 1 Okt 2026 dan 0x95e0 pada 27 Sep 2026 — itu funding, bukan trading. Win rate proksi di atas adalah hitungan kaki (pegang/exit), bukan win rate PnL. **Semua kandidat peringkat 1–7 wajib lewat §5 sebelum dipakai sebagai acuan monitor.**

### Wallet terkait + klaster kandidat baru (strong vs weak)

**TRIO — linkage KUAT (eksekusi), LEMAH (funding):**
- KUAT: blok + detik yang sama di 3 kaki (RIKI blok 130301036; WTB blok 130646624; ok blok 130791540), n=1 di semua kaki, urutan ukuran wallet sama di semua kaki, jual WTB di menit yang sama (17:17). Ini praktis membuktikan satu operator/kontroler yang sama — bukan kebetulan.
- LEMAH (bukan bukti cabal): ketiga wallet menerima WBNB dari tiga pengirim yang sama pada 1–3 Okt 2026 (0x94f83b1eeacd0f1df1638adbddb1eb151d34516d ~0,0052 pada 1 Okt; 0xb40388d71af1ebf150a3540835ea365bd67d3f80 pada 3 Okt pagi; 0xf962f1ae65c71d7a63de18ca5729e7c2d99df398 pada 3 Okt 21:19, termasuk blok yang sama 125499176 untuk dua wallet). TAPI ketiga pengirim itu adalah distributor massal (0x94f8: 1.010 transfer ke 401 penerima; 0xb403: 384 transfer ke 240 penerima; 0xf962: 63 transfer ke 50 penerima) — kemungkinan layanan drip gas / funder bot-farm, bukan funder privat. Jadi funding bersama = **weak linkage**, bukan bukti cabal. Funder BNB-native (bukan WBNB) tidak terselesaikan (keterbatasan Ankr sent-only; lihat §6).
- Co-buyer lain: tidak ada kaitan Tier A (lihat di bawah).

**PAIR — linkage KUAT (eksekusi), TIDAK ADA (funding):**
- KUAT: blok identik di semua kaki beli dan jual (ok beli blok 130788409, jual blok 130792780/130792859/130794494; COOL beli blok 130800266, jual blok 130800298/130800490 — selalu sama untuk kedua wallet), jumlah seorde, n identik (24 dan 4). Satu operator.
- Funding: sumber WBNB pertama BERBEDA (0x2fc2 dari 0x7c00b2333da420de3b20b53e3a287a1cfc56d13c pada 6 Okt; 0x95e0 dari 0x7e07e5816bd4ff24e4814b050ca12da7a5c059b1 pada 27 Sep). Jadi keterkaitan pair adalah level eksekusi, bukan funding — tetap sangat kuat, tapi tipenya berbeda dari trio.

**Hasil co-buy vs Tier A (negatif, penting):** dari 11 set awal, **NOL wallet Tier A** muncul kecuali Tier A `0x8e96…` di wangcai (n=1, sudah diketahui: beli $4,091, 851,5K, 100% — dan kini masih pegang wangcai 851.502,39 peringkat #13 serta ok 840.175,64 peringkat #36, persis sama dengan snapshot sebelumnya). Satu-satunya wallet terpantau non-Tier-A yang muncul adalah SENSEI W1 `0x81c3d1b4c9433bd5e52544ca96b19cfa9eb5de36` di BIBIAI (n=1 — konsisten dengan scan 2026-11-01: beli awal BIBIAI +118,9%; W1 kini sudah exit SENSEI, BIBIAI, MSX, GANG, saldo BNB 0,0115 — sudah keluar dari posisi-posisi itu sejak 1 Nov). **Kesimpulan: finalis adalah populasi baru yang independen dari Tier A, bukan co-buyer Tier A.** Jalur co-buyer menghasilkan nol kandidat baru.

**Kaitan lain:**
- `0x4cad1efbfd5f0848e0c3c14fab23f92b2fa81f17` (EOA, sudah tercatat di file prioritas — BUKAN baru): mubarak #5 (28.973.509,45, tidak berubah) + EGL1 #5 (12.477.812,75) — kaitan lintas token baru yang terkonfirmasi, tapi wallet-nya sudah dikenal.
- `0x73D8bD54F7Cf5FAb43fE4Ef40A62D390644946Db`: SKYAI #5 + EGL1 #3 — ini Binance Wallet Proxy (infrastruktur exchange), BUKAN trader; kaitan lemah, dikecualikan.
- Repeat holder lintas token yang sudah dikecualikan karena kontrak: `0x4Ff1D40fb7B56665bf95D8D8e3A5320dE46709A1` (HI #9, BIBIAI #5, SENSEI #41) dan `0xD42a05157Af07F0C860a5211E03B4Eaac20412CE` (charity #2, aiPRO #4) — keduanya kontrak, bukan wallet independen. Burn `0x0000…dead` muncul di 7 token (normal, dikecualikan).
- `0xf9d4dd75034a35ba7df48a9c136b0ef36e10783` (COOL #8 + HI #44): status EOA **belum terverifikasi** (RPC dataseed gagal berulang saat cek) — single-source, masuk §5, bukan peringkat.

### Kandidat 1-hop dari Tier A (dari pekerja graf — perlu pendalaman, belum berperingkat)

Semua **terindikasi**, bukan terbukti, dan semuanya **bukan wallet terpantau**:

1. **EOA `0x8fa6a5c0f2408123ab5323c0a87f30d6357bc302` → wallet 8** (`0x8e966a9f17beab1ea50039434c2a14ad9e09b8d6`): **2 transfer native BNB plain, total 0,46091 BNB, 2026-10-29 20:53 UTC (03:53 WIB 30-Okt)** — satu-satunya funding native material di Tier A/B. Nol kemunculan di log token (single-source: hanya jalur native, tanpa koroborasi token). Kandidat penemuan #1 untuk wallet 8.
2. **Famili `0x21a7*` (5 alamat) ← wallet 2** (`0x2325f175975abdbcde555c79cc8e63381d28551b`): **42 transfer token, hanya keluar, eksklusif untuk wallet 2** (tidak berinteraksi dengan wallet terpantau lain mana pun): `0x21a73997…` 18× (12 token), `0x21a7edbe…` 12× (10 token), `0x21a7b0f6…` 8× (USDT), plus `0x21a78d90…` dan `0x21a7d79b…`. Dua yang dicek `eth_getCode` adalah EOA, satu kontrak kecil. Terindikasi gugus alamat penerima/distribusi wallet 2.
3. **Famili `0xb27a*` (7 alamat) ↔ wallet 4** (`0x6ba79dcc05a1056e19bf1021db4fca7be18b49e7`): **45 transfer, eksklusif untuk wallet 4**, termasuk **dua arah** dengan `0xb27a4273…` (4 masuk / 8 keluar) dan arus USDT dua arah (`0xb27a666c…` 9× masuk USDT, `0xb27abde4…` 8× masuk USDT; wallet 4 keluar 10× ke `0xb27abfc7…` lintas 10 token). Campuran EOA + kontrak kecil. Terindikasi gugus alamat terkait wallet 4 — satu-satunya relasi 1-hop Tier A yang dua arah + multi-token + eksklusif.
4. **Famili `0x70a1*` (2 EOA) ← wallet 8**: `0x70a15e52…` 16× keluar (8 token) + `0x70a1b9f9…` 15× keluar (14 token), **31 transfer, hanya keluar, eksklusif untuk wallet 8**. Paralel dengan pola wallet 2/wallet 4 di atas.
5. **EOA `0x7121af698e429ca5e39be444bc4b13c9e6dc5685` → wallet 14** (`0xf6a8280c997c4b4daa606e2c8c37b5a79b8ae2cc`): **6 masuk, 4 token**, termasuk token `0x5c85d6c6…` 3×. Satu-satunya funder berulang wallet 14 (yang tidak punya transfer keluar sama sekali dalam 30 hari). Single-funder, tapi berulang + multi-token.
6. **Sistem kontrak template-identik → wallet 2:** `0x66501663…` (56×), `0xa5c3a395…` (50×), `0x74a1a4f8…` (29×), `0x5e07ec95…` (9×) — **148 masuk, satu token** `0x4902c5ebc598265ed2212b559b042de8a5eeec3f`, keempatnya kontrak dengan **panjang code identik (13922)**. Ini satu sistem distributor, bukan 4 funder independen. Kandidat penemuan untuk sistem/token itu, bukan klaster wallet.
7. **Lainnya (weak, single-source, dicatat bukan dipromosikan):** wallet 2: kontrak kecil `0x1f0fafe229…` — 0,2 BNB native (2026-10-04 14:28 UTC) + 1 transfer token `0x8467b435…` (15:25 UTC hari sama); wallet 7 (`0x89220022…`): kontrak `0x2d9d6e53…` (9 masuk/9 keluar), `0x5be10189…` (3/3), `0x78e2d812…` (3/3) — pola venue/kontrak token, **bukan** kandidat wallet (awas: `0x5be10189…` ≠ funder EOA `0x5be3914f…`); wallet 13 (`0xda91cefe…`): transfer token lama dua arah dengan EOA-EOA (`0x8894e0a0…` 3 masuk, `0xe2fc31f8…` 2 masuk, `0x5b1d6401…` 3 keluar, `0x5b1d9f14…` 2 keluar), semua satu token `0x5c85d6c6…` — P2P holding lama, weak; wallet 10 (`0xaab80f45…`): EOA `0x0d070796…` 2× masuk satu token `0x92aa0313…` — weak; wallet 7 juga: dust native 7e9/1e9 wei dari `0xcaa395f4…` (kontrak kecil) dan `0xcaa314bc…` (EOA) pada menit yang sama 2026-10-13 18:42 UTC — dust, bukan funding.
- **Konteks wallet 2:** di luar yang di atas, wallet 2 punya ~50 counterparty dua arah kecil (2–10 transfer, umumnya satu token) — churn trading biasa, tidak diklasifikasi satu per satu dan tidak diangkat sebagai kandidat.

---

## 4. Klaster, keterkaitan, dan daftar dikecualikan

### 4a. Klaster M — "seeded set" 35 wallet (TERINDIKASI satu set yang di-seed bersama; BUKAN klaster kredibel)

**Anggota (35):** seluruh wallet posisi 15–50 (1-based, urutan file state) **kecuali** posisi 21 (`0x38031ca8a54526f9fe90f11f07b55ae5fc01036a`). Termasuk SENSEI W1 yang benar (`0x81c3d1b4c9433bd5e52544ca96b19cfa9eb5de36`, posisi 49) dan `0x97bd895f8123a7837368df410e7d308246c0b3e9` (posisi 50, Tier C — pekerja graf sempat salah label sebagai W1; substansi tidak berubah).

**Bukti (3 funder EOA independen, set penerima identik, hari yang sama):**
- EOA `0x1dcbb121e37b5a91dc90388e47afe618aaa98d20` → token `0xe46ee5f881ae86b238b91405ee4c14514e117252`, **35 transfer, jumlah IDENTIK** (45.366.680.000.000.000.000.000.000) ke masing-masing dari 35 wallet, 2026-11-01 01:34–09:51 UTC (08:34–16:51 WIB).
- EOA `0xb5890ee401e70aeaed6f1971497fb575c2ec15b7` → token `0x712a3e2a77097131dd165969e58fe7dc0d74e094`, **35 transfer, jumlah IDENTIK** (255.940.000.000.000.000.000) ke set yang persis sama, 2026-11-01 02:03–09:50 UTC.
- EOA `0x92b1c02633130f91911e462a4e2052e09bf7f851` → token `0xf1deb03866b3fcc3f3e1a1b94c50cae2cc462b5e`, **62 transfer (2× ke 28 wallet, 1× ke 6 wallet), jumlah IDENTIK**, ke 34 wallet (set yang sama minus posisi 18 `0x40a8b422f09fe7f630ccb3dbd07ea258577b784c`), 2026-11-01 06:12–10:54 UTC.

**Penilaian:** tiga EOA berbeda mendistribusikan tiga token berbeda dengan jumlah identik ke set penerima yang (hampir) persis sama dalam satu pagi yang sama — terindikasi kuat sebagai seeding bersama oleh satu operator/skrip, bukan tiga klaim airdrop independen yang kebetulan selaras. Namun ini **bukan bukti cabal yang kredibel**: anggotanya adalah wallet mikro/rotasi (per GMGN: trade $0,018–$0,071, holding dust), dan **riwayat untung tidak dinilai dari data ini**. Jadi: **gugus alamat, bukan klaster kredibel**. Jangan pakai sebagai sinyal beli.

### 4b. Klaster R — inti rotasi 5 wallet (TAUTAN PALING KUAT di seluruh set; tetap gugus alamat)

**Anggota inti:** `0x3628764a6576b8dfb31fba0aac6a333b64851423` (16), `0xa0c1e94fbc1a93e39f5eb828f960aa080a9d9b9e` (17), `0xc7c5faa270eb2394c7bf9f411fed0d0126f2eb74` (19), `0xad94ee77d0e868d299fb3e92b9d67560257f656d` (20), `0x38031ca8a54526f9fe90f11f07b55ae5fc01036a` (21). Perifer: `0x7488d5da6a6097de0ff88c7492c62c2fd1e56650` (22, 1×), `0x40a8b422f09fe7f630ccb3dbd07ea258577b784c` (18, 1× dari tiap funder).

**Bukti (dua funder + sinkronisasi waktu, bukan sekadar co-buy):**
- EOA `0xf23f5bdd66c39c8353c3ae7b049467891dd511bf` mengirim **2 token** (`0xf7e47286fc…` lalu `0x5c64a6b6fa…`) ke kelima wallet inti **dalam hitungan menit**: 2026-10-28 12:50:38–12:54:10 UTC untuk token pertama, 19:03:40–19:15:02 UTC untuk token kedua (plus `0x7488…` 20:10:17 UTC).
- Dua EOA `0x704066b18b9e775d65c859f1230227c1c7c0c4ab` dan `0x5be3914fcf811e9edd7e1bd6b41ae70bd8ef8a2d` sama-sama mendanai `0x3803…`, `0xa0c1…`, `0xad94…` (dan 1× `0x40a8…`) dengan **13 token berbeda tiap funder** — dan transfer pertama keduanya ke `0x3803…` hanya berselisih **15 detik** (07:10:31 vs 07:10:46 UTC, 2026-10-28), lalu keduanya lagi berselisih **3 detik** (09:22:17 vs 09:22:20 UTC). Dua funder + dua sinkronisasi detik = bukti koordinasi skrip, bukan kebetulan.
- Koroborasi (weak saja, bukan bukti klaster): pola rotasi micro-trade identik kelima wallet ini di GMGN (simbol sama, ukuran sama, waktu berdekatan).

**Penilaian:** tautan pendanaan terkuat dalam tugas ini, tetapi **tetap gugus alamat** (trade mikro dust, tanpa bukti riwayat untung). Klaster R tumpang tindih dengan Klaster M (4 dari 5 anggotanya ada di M; `0x3803…` terhubung ke M lewat R, bukan lewat distribusi massal).

### 4c. BUKAN klaster (disengaja dibedakan)

- **Self-mint token contract (sender == token):** mis. token `0xa00a038ad1d21c3edc5613f34c1a8807203e9d0e` "mengirim" ke 38 wallet terpantau — itu mint dari kontrak token itu sendiri, **bukan funder**, dan tidak dihitung sebagai linkage. Co-mint/co-buy saja = weak linkage, bukan klaster.
- **Router/venue contract:** `0x296b00198dc7ec3410e12da814d9267bb8df506a` (kontrak; 222 masuk/245 keluar untuk wallet 2, 158 token) dan `0xe2ce6ab80874fa9fa2aae65d277dd6b8e65c9de0` (kontrak; 386 masuk/369 keluar untuk wallet 8, 337 token) adalah venue trading, bukan counterparty wallet.
- **Tidak ada klaster di Tier A/B.** Tidak ada funder bersama dan tidak ada transfer langsung antar wallet Tier A/B mana pun.
- **Funder bersama + status exchange:** tidak ada funder yang memenuhi kriteria "kemungkinan exchange" (tidak ada hot wallet aktivitas sangat tinggi; tidak ada alamat hot wallet dikenal yang teridentifikasi). Jadi tidak ada yang dilabel exchange dan tidak ada yang dicoret sebagai "bukan cabal karena exchange". Semua funder bersama di atas adalah EOA/kontrak non-exchange; identitas operatornya tetap **terindikasi, bukan terbukti**. Distributor massal satu-token lainnya (puluhan EOA, masing-masing 1 token ke 27–35 wallet, mis. `0x0cddb235…` 68 transfer/27 wallet) adalah pola distribusi massal — weak sebagai bukti cabal bila berdiri sendiri. Kontrak `0xd15fe25e…` (1× tiap wallet ke wallet 2 + `0xa0c1…` + `0xad94…`, token berbeda) adalah **single-source, WEAK** — bukan bukti klaster.

### 4d. Pasangan transfer langsung antar wallet terpantau: NIHIL

Nol pasangan dalam 30 hari untuk transfer token. Ini hasil yang kuat, bukan celah cakupan: setiap wallet terpantau (50/50) IN-nya dikueri, jadi transfer token antar dua wallet terpantau pasti muncul sebagai IN di penerima. Pasangan native BNB antar wallet terpantau (Tier A/B saja) juga nihil. **Tier C + SENSEI: TIDAK ADA yang standalone** — ke-36 wallet posisi 15–50 semuanya masuk Klaster M (35 lewat 3 distributor massal; `0x3803…` lewat funder Klaster R). "Tidak standalone" di sini berarti terhubung lewat bukti distribusi/pendanaan bersama, bukan lewat transfer langsung (yang nihil).

### 4e. Daftar dikecualikan dump/rug + alasan + bukti

**Tidak satu pun finalis peringkat 1–7 yang memenuhi ambang eksklusi** (jual ≥80% dalam ~1 jam di ≥3 launch baru). Catatan: pair punya 2 kaki exit-cepat (COOL 100% dalam 2 menit; ok ~100% beli awal terjual dalam ~45 menit lalu diakumulasi ulang) dan trio punya 1 kaki exit-cepat (RIKI 100% dalam 17 menit) — itu **pola exit cepat parsial, bukan dump berulang ≥3 launch**, jadi tidak dikecualikan tapi wajib ditanyakan di §5. Yang dikecualikan:

- **Rantai sniper RIKI→HI→WTB (negatif, sudah dikenal):** buyer `0x86570adc943c6102088c0b27acd218895bf3ff88` dan `0xb3466bfccf29e3babb61ca0f1b8984fde6ed728e` — muncul di RIKI (22:01, n=2), BIBIAI (21:51, n=1), WTB (17:12, n=1), HI — selalu detik/menit yang sama dengan funder `0x612add8664aaacefbfa529633fefaf42dd16565a` dan `0xd991e396757820b97a8d100cf1b6e776d764d022` di kaki yang sama; tag GMGN Bundler + Sniper + Paper hand; semua posisi terjual. **Terindikasi** armada sniper terkoordinasi (bukan "terbukti" — tidak ada bukti deployer langsung).
- **Hub funding sniper** `0xf5988713400da6fc8a58ec9515e2b0df9b40b115` — mendanai wallet terkonfirmasi di batch 1, 2, 3, 5, 6 (12 wallet di 6 dari 8 token batch-5 saja). Filter negatif paling konsisten.
- **Funder berulang** `0x318d2aae4c99c2e74f7b5949fa1c34df837789b8` (0x31…89b8 — JANGAN dicampur dengan 0x31…21ba, suffix berbeda).
- **Kontrak/bot executor (bukan wallet):** `0x5be10189f009334aacae23d7102d64527e32bbdb` (RIKI n=1199, WTB n=571, ok n=76, BIBIAI, HI — 5 kaki, volume bot), `0xb300000b72deaeb607a12d5f54773d1c19c7028d` (executor SENSEI W2; RIKI n=363, BIBIAI n=917, WTB n=280, ok n=126, HI), `0x6ce58d1fa9c7b1d8ea29245bf9cb19dd1250f408`, `0x9775c0ad08f7ed590a33c9ee59a1307bc870d877`, `0x917edfb42d9b630c0f8fc0e2176341a5fa941a78`, `0x09ad820aac5779683b481c4674208a4e1b024afa`, `0x67c357226058b3ffc0ec1c8aaaccc271f92740ef` (semua kontrak di cek ok/COOL), `0x28e2ea090877bf75740558f6bfb36a5ffee9e9df` (GANG #11 + HI #22, kontrak len 48020), `0x4ff1…`, `0xd42a…` (di §3).
- **Insider MSX:** DEV `0x9bf522DD66438Ac30F679809391f311200b398F6` (EOA, pegang 500 jt MSX = 50% supply) + secondary insider `0x47d4db5ae9567233e3fc426e775949bfe7205598`, `0x0301b15ef5771c21e7e6afa90c24083c5a84433b`, `0xb5a5720c5423d84352b572a859810b67341fccbd` — klaster insider, bukan early caller independen.
- **Exchange (bukan trader):** Binance Cold mubarak #1 `0xf977814e90da44bfa03b6295a0616a897441acec` (582,10 jt), Gate Cold `0xc882b111a75c0c657fc507c04fbfcd2cc984f071` (mubarak #2 101,57 jt; SKYAI #1 244,73 jt), Gate Hot `0x0d0707963952f2fba59dd06f2b425ace40b492fe`, Bitget `0xed9ab5bc05a0152b9dc2f7902e8369af7bc18771` (mubarak #19→#25, SKYAI #4), Indodax Hot `0x91dca37856240e5e1906222ec79278b16420dc92`, MEXC Hot `0x4982085c9e2f89f2ecb8131eca71afad896e89cb`, Binance Proxy `0x73d8…`. Co-hold antar exchange = kaitan LEMAH, bukan klaster trader.
- **Aturan alamat terpotong:** kecocokan prefix saja (mis. 0xf5…b115 vs 0xf5…a3b7; 0xd9…b05d vs 0xd9…d022; 0x31…89b8 vs 0x31…21ba; 0xb3…398e vs 0xb3…728e) TIDAK PERNAH dihitung sebagai bukti.

---

## 5. Daftar butuh konfirmasi GMGN (aktivitas/PnL) + pertanyaan spesifik

GMGN adalah urusan parent (tidak ada browser task dibuka dalam tugas ini). Jawaban atas pertanyaan di bawah menentukan apakah kandidat naik ke set pantau atau tidak.

### 5a. TRIO (tanyakan per wallet, ketiganya)

(a) PnL realisasi 30 hari + win rate (berapa % trade profit, berapa trade total)? (b) PnL kaki RIKI (beli 21:56:39 28 Okt, jual 22:01 + 22:13 — untung atau rugi, berapa %)? (c) PnL kaki WTB (beli 17:09:44 30 Okt, jual ~55% pada 17:17 — berapa %; sisa 45% masih dipegang?) (d) Apakah ada pola dump (jual ≥80% dalam 1 jam) di launch lain di luar 11 token ini — di token apa, berapa kali? (e) Apakah ketiga wallet ini satu operator (riwayat trade identik di GMGN)? (f) Posisi COOL-flap saat ini (beli kapan, berapa, masih pegang?).

### 5b. PAIR (tanyakan per wallet)

(a) PnL realisasi 30 hari + win rate? (b) PnL flip COOL (beli 12:22:20, jual 12:22 + 12:24 31 Okt — untung/rugi berapa %; apakah ini flip tercepatnya)? (c) PnL kaki ok: jual tranche 11:26–11:39 untung/rugi berapa, lalu akumulasi ulang kapan dan di harga berapa (saldo kini 10,64 jt / 11,19 jt)? (d) Apakah ada pola dump ≥80% dalam 1 jam di ≥3 launch lain? (e) Apakah kedua wallet ini satu operator? (f) Apakah ada funding bersama di luar WBNB (funder BNB-native)?

### 5c. Solo peringkat 3–8 (per wallet)

(a) PnL realisasi 30 hari + win rate? (b) PnL per kaki yang tercantum di §3 (khusus 0x9505: HI kini masih pegang atau sudah jual? khusus 0xc687: HI kini? khusus 0x4740: saldo BIBIAI/HI kini? khusus 0xef39: saldo COOL/WTB kini? khusus 0xcc1b: apakah terkait trio — trade identik di token lain?). (c) Pola dump ≥80% dalam 1 jam — berapa launch, token apa? (d) Untuk 0xc605…153d secara spesifik: 5 kaki semua exit 0 — apakah ini rotasi disengaja yang profitabel, atau paper-hand?

### 5d. Holder-only SKYAI/EGL1 (0x6ddd…, 0x586a…, 0x93f5…, 0xd79c…)

(a) Kapan pertama kali beli SKYAI/EGL1 (apakah benar early 2025 atau beli belakangan)? (b) PnL 30 hari + win rate? (c) Apakah ada kaitan antar keempat wallet ini (funding/trade bersama)? (d) Untuk 0x93f5… (30.000.100 EGL1, angka bulat): apakah ini wallet tim/vesting?

### 5e. `0xf9d4dd75034a35ba7df48a9c136b0ef36e10783` (COOL #8 + HI #44)

(a) Konfirmasi EOA vs kontrak (cek on-chain gagal saat tugas ini)? (b) Kaki awal di token apa saja + PnL-nya? (c) Saldo COOL/HI kini?

### 5f. SENSEI W1 `0x81c3d1b4c9433bd5e52544ca96b19cfa9eb5de36` (bukan baru — pembaruan status)

Sudah exit SENSEI/BIBIAI/MSX/GANG sejak 1 Nov. Tanyakan apakah exit itu profit (khususnya BIBIAI +118,9% dari scan 1 Nov) dan apakah wallet ini masih aktif trading.

### 5g. Konfirmasi sebelum pencopotan 12 wallet Tier A/B dari feed

Untuk tiap dari 12 wallet di §1: apakah GMGN menunjukkan aktivitas (trade/transfer) dalam 48 jam terakhir yang tidak tertangkap metode Transfer token (mis. transfer BNB native, swap tanpa event Transfer yang terbaca, atau aktivitas di chain lain)? Bila ya untuk satu wallet, wallet itu keluar dari daftar buang. Bila tidak, pencopotan dari `TRACKED_WALLETS` aman — dengan catatan pencopotan 12 dari 14 wallet tracked akan meruntuhkan cakupan konfirmasi feed (threshold 13), jadi penggantinya (TRIO/PAIR bila lolos §5a–§5b) sebaiknya disiapkan dulu.

### 5h. Pertanyaan terbuka lain

- Token T7 (0xB4e32E16185Ecee92c2C465F27bE799b93797777): nama/simbol/proyek apa, dan apa peristiwa 2026-11-02 15:25–15:30 WIB yang membuat 26 wallet Tier C mengirimnya serentak?
- Funder native bersama antar wallet Tier C (celah §6 butir 1): lengkapi saat Ankr stabil — apakah ada funder BNB bersama di Tier C yang mengubah peta klaster M?

---

## 6. Keterbatasan metode (jujur, memengaruhi kesimpulan)

1. **Screening aktivitas hanya melihat event Transfer ERC-20/721/1155.** Transfer BNB native, approval, dan contract call tanpa event Transfer tidak tertangkap metode screening (§1–§2). Pekerja graf memang berhasil memakai `ankr_getTransactionsByAddress` untuk native Tier A/B (lengkap: wallet 2: 1.275 tx, wallet 8: 1.386 tx, wallet 7: 22, wallet 4: 1, wallet 13: 5, sisanya 0; hitungan direproduksi identik pada dua sweep) — tapi **detail native Tier C/SENSEI tidak lengkap** (sweep pertama baru mencapai wallet 15–17 sebelum Ankr timeout total sesaat; retry hanya mencakup Tier A/B). Akibatnya funder native bersama antar wallet Tier C, atau antara Tier A/B–Tier C, **bisa terlewat**. Kesimpulan "tidak ada funder native bersama" hanya berlaku untuk Tier A/B.
2. **Tidak ada histori harga.** Proksi untung hanya hold/exit. PnL realisasi, harga beli vs jual, dan win rate PnL TIDAK tersedia dari log — semua klaim profit di laporan ini adalah proksi, dan §5 wajib dijawab GMGN sebelum kandidat dipakai.
3. **Jumlah kasar saja.** Nilai `data` log adalah raw uint256; desimal tiap token tidak dicek, jadi angka mentah bukan nilai nominal.
4. **Heuristik sale source:** pembeli = penerima dari pengirim tersering. Untuk COOL-flap ada DUA sumber besar (0x1de4… 254 kiriman + kontrak Flap 0xe2ce… 249 kiriman); set COOL gabungan = 113 buyer (disjoint). Untuk charity (4 buyer) dan wangcai (8 buyer), sumber yang terdeteksi adalah kontrak Flap dengan sedikit kiriman — pasar utama kedua token ini kemungkinan memakai mekanisme distribusi lain, jadi repeat via charity/wangcai **undercounted**.
5. **Jangkar RIKI:** transfer pair→buyer pertama on-chain adalah 21:56:24 WIB, sementara catatan GMGN menyebut trade pertama non-dev 21:38:00 (+1 detik). Kemungkinan trade 21:38 terjadi di bonding curve sebelum pair V2, atau anchor GMGN berbeda. Trio tetap "awal" di kedua anchor (+15 detik / +18,7 menit), tapi selisih ini dicatat sebagai pertanyaan terbuka, bukan disembunyikan.
6. **Funder BNB-native tidak terselesaikan untuk kandidat baru:** Ankr `ankr_getTransactionsByAddress` hanya mengembalikan sent-only (temuan 2026-11-01); Blockscout tidak mendukung BSC (404); BscScan terblokir Cloudflare di pekerjaan sebelumnya. Proksi WBNB dipakai sebagai gantinya; alamat WBNB yang benar (`0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c`) dipulihkan dari `token1()` pair RIKI setelah string dari memori terbukti salah panjang — tidak ada alamat yang ditebak.
7. **Dataseed flapping + outage egress + restart VM:** outage 2026-11-02 ~16:0x WIB mematikan semua dataseed/Ankr; loop retry pertama terbunuh SIGTERM oleh restart VM (~68 menit) dan `/tmp` terhapus total — pekerjaan discovery dibangun ulang setelah egress pulih. Ankr sempat down total ±15 menit di tengah tugas graf, lalu pulih sendiri. Tidak ada data dari periode outage yang dipakai. Gangguan pasca-run di pekerja Tier A/B menghalangi hitung-ulang koroborasi (run utama sendiri bebas error).
8. **Guard truncasi 1000-log:** pekerja Tier C memasang guard pecah-window tapi tidak mencatat hitungan per window (jejak pemicu tidak tercatat); pekerja Tier A/B dan graf memecah window yang penuh secara rekursif. Risiko residu minimal karena verdict bertumpu pada window terbaru yang kecil, tapi untuk audit penuh hitungan per window sebaiknya dicatat di run berikutnya.
9. **Populasi bot:** 12.222 buyer awal didominasi bot/sniper (buktinya: 656 wallet di ≥2 token, 20+ wallet di ≥5 token, funders drip massal dengan ratusan penerima). Jumlah kaki saja TIDAK membedakan smart money dari sniper — karena itu peringkat mengutamakan koordinasi blok + disiplin n=1 + hold, bukan jumlah kaki.
10. **SKYAI/EGL1:** tidak ada analisis early-buyer (pool 2025, di luar window 30 hari); hanya persistensi holder. Status survivor SKYAI adalah inferensi, EGL1 provisional dengan konflik MCAP 10×.
11. **Snapshot vs early buyer:** holder top-50 saat ini BUKAN bukti beli awal — laporan ini memisahkan keduanya secara eksplisit; holder yang tidak ada di set awal dicatat sebagai holder-only.
12. **Aturan alamat:** hanya alamat lengkap 40 hex yang dipakai; kecocokan terpotong tidak pernah dihitung sebagai bukti (kasus 0xc605…153 vs …153d menjadi contoh nyata mengapa aturan ini ada).
13. **Klasifikasi kontrak terbatas:** `eth_getCode` hanya untuk alamat kunci (~40 di tugas graf + kandidat baru). Counterparty kecil yang tidak dicek berstatus "tidak terklasifikasi".
14. **Identifikasi exchange heuristik saja:** tidak ada registry hot-wallet yang dicek; penilaian "bukan pola exchange" didasarkan pada pola aktivitas (fan-out sempit, jumlah identik, satu hari) dan status code, bukan daftar resmi.
15. **Timestamp batas window adalah estimasi** (~0,45 detik/blok), bukan hasil fetch blok batas — cukup untuk kesimpulan cutoff karena margin ~2 jam, tapi bukan bukti detik-per-detik. Timestamp transfer individual sendiri diambil dari header blok via RPC (titik data kedua yang independen dari indexer Ankr).

---

## 7. Tindakan berikut yang disarankan (bukan eksekusi)

1. Parent menjalankan §5 di GMGN untuk TRIO dan PAIR dulu; bila PnL realisasi keduanya positif, keduanya layak masuk set pantau — trio untuk pola hold disiplin, pair untuk pola akumulasi ok.
2. Jangan tambahkan Klaster M/R sebagai acuan, dan jangan perlakukan distribusi bersama/co-buy mereka sebagai sinyal beli.
3. Jangan copot 12 wallet Tier A/B dari `TRACKED_WALLETS` sebelum §5g dijawab — pencopotan tanpa pengganti meruntuhkan cakupan konfirmasi feed.
4. Selidiki 1-hop Tier A (§3, akhir) sebagai jalur penemuan berikutnya, terutama funder native wallet 8 (0x8fa6…) dan famili dua arah wallet 4 (0xb27a*).
5. Bila Ankr stabil, lengkapi detail native Tier C/SENSEI untuk menutup celah §6 butir 1, dan identifikasi token T7 + peristiwa 15:25–15:30 WIB.
