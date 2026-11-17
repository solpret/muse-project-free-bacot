# Riset Wallet Dalam 2 — Koin Terbentuk mcap > $1 Juta, Scan First-30 Lanjutan

- **Tanggal riset:** 2 November 2026, malam WIB (baca pekerja 18.32–20.55 WIB; sintesis koordinator ~21.00 WIB, head blok 131252838).
- **Perintah user:** 2 November 2026 ~18:13 WIB — "cari kandidat baru dengan metode yang menurutmu paling bagus".
- **Sifat pekerjaan:** READ-ONLY, BSC saja. TIDAK ADA transaksi, approval, signing, login GMGN, atau permintaan seed phrase/private key. TIDAK ADA file state/feed/cron/goal yang diubah: `tier-ab-watch-state.json`, `wallet_confirmation.py`, snapshot Free Bacot hanya dibaca.
- **File pekerja (bukti mentah):** `deep-search-2/child-ake-q-idol-ain-jct.md`, `deep-search-2/child-uai-beat-lab-debit-aria.md`, `deep-search-2/child-collect-aeon-esports.md` di folder yang sama dengan laporan ini.
- **Laporan sebelumnya (konteks, tidak ditimpa):** `wallet-deep-search-2026-11-02.md` (20 koin; IBS #2/BORT #8/klaster GANG tidak dipromosikan; TRIO/PAIR dicoret user; feed TRACKED_WALLETS tinggal 2).

## 1. Ringkasan eksekutif — temuan keras

**Tidak ada satu pun wallet yang lolos semua filter** (repeat early buyer ≥2 koin + masih hold bermakna + bersih + aktif 48 jam terakhir). Ini bukan karena ambang terlalu ketat — ini karena metode first-30 pair V2 ternyata instrumen yang salah untuk koin-koin terbentuk, dan itu adalah temuan metodologis utama riset ini:

1. **Semua pair V2 yang bisa dipindai BUKAN pasar pertama tokennya.** 10 dari 13 koin punya pair V2, dan kesepuluhnya dibuat berminggu-minggu sampai berbulan-bulan SETELAH pool pertama (umumnya V3/CLMM). Jadi "first-30" di sini adalah pembeli awal pair V2 yang sepi, BUKAN pembeli peluncuran. Pembeli peluncuran sesungguhnya ada di pool pertama dan TIDAK tercakup riset ini.
2. **First-30 V2 didominasi kontrak/bot executor** (AKE 22/30, Q 26/30, IDOL 28/30, AIN 24/30, Beat 26/30, ARIA 26/30, COLLECT 14/30, AEON 26/30, ESPORTS 19/30, LAB 13/17) — wajar untuk pair belakangan yang sepi (arbitrase V3↔V2 oleh bot).
3. **3 dari 13 koin TIDAK PUNYA pair V2 sama sekali** (JCT, UAI, DEBIT — getPair = 0 untuk WBNB/USDT/USDC; PairCreated nihil). Pasar pertamanya adalah V3/CLMM — di luar metode ini.
4. **Semua kandidat bersih berskala debu dalam dolar.** Nilai terbesar di seluruh riset: Q #9 ≈ $2,22; sisanya ≤ $0,38, mayoritas <$0,01 (hitung di §5, harga implisit mcap/supply).
5. **Nol aktivitas 48 jam terakhir** pada semua kandidat yang dicek (§6).
6. **Satu-satunya pola repeat-buyer adalah wallet debu** (0x29a4… di 4 koin, 0x18e3… dan 0x9b69… di 2 koin) — dan wallet 0x29a4… terbukti berfrekuensi bot (≥1.200 transaksi dalam satu irisan ~1,5 hari, §7).

**Vonis: TIDAK ADA promosi dari riset ini.** Tidak ada wallet yang memenuhi kriteria promosi penuh (≥3 token + PnL 30 hari terverifikasi), dan tidak ada pula yang layak diajukan ke konfirmasi GMGN sebagai kandidat serius — semuanya gagal di nilai pegangan dan/atau aktivitas sebelum sampai ke GMGN. "Proxy profit" (beli awal + pegang/jual) BUKAN PnL terverifikasi; tidak ada klaim PnL di laporan ini.

## 2. Universe + hasil per koin

Mcap dari GeckoTerminal 2026-11-02 17.35 WIB (angka waktu baca, bukan live). Pair V2 diverifikasi on-chain lewat factory `getPair` + log `PairCreated` (selector programatik). "Bersih" = EOA + saldo >0,5% beli awal 6 jam + bukan daftar coret + tanpa fast dump ≤1 jam.

| Koin | CA token | Pair V2 terverifikasi | Pasar pertama? | First-30 V2 | Kontrak | Bersih |
|---|---|---|---|---|---|---|
| AKE | 0x2c3a8ee94ddd97244a93bc48298f97d2c412f7db | 0x31e492e0b47ebda736b8655f6e9cb564bc9d4435 | BUKAN (V3 2025-08-20, ~2,8 hari lebih awal) | 30 | 22 | 2 |
| Q | 0xc07e1300dc138601fa6b0b59f8d0fa477e690589 | 0x8b01ff647ad15fbf9ffb43a0f84cb8bcfbab9acd | BUKAN (V3 2025-08-31, ~2 hari lebih awal) | 30 | 26 | 2 |
| IDOL | 0x3b4de3c7855c03bb9f50ea252cd2c9fa1125ab07 | 0x46377435d96be3e68799e98fd94381a061d174e5 | BUKAN (V3 2025-06-10, ~86 hari lebih awal) | 30 | 28 | 0 |
| AIN | 0x9558a9254890b2a8b057a789f413631b9084f4a3 | 0xd18ed1a49b3488550d0be01c5a010b26363c52a0 | BUKAN (V3 2025-07-04, ~1,1 hari lebih awal) | 30 | 24 | 4 |
| JCT | 0xea37a8de1de2d9d10772eeb569e28bfa5cb17707 | TIDAK ADA | GAGAL TOTAL (pasar pertama V3/CLMM, di luar metode) | — | — | 0 |
| UAI | 0x3e5d4f8aee0d9b3082d5f6da5d6e225d17ba9ea0 | TIDAK ADA | GAGAL TOTAL (pasar pertama V3 2025-11-04) | — | — | 0 |
| Beat | 0xcf3232b85b43bca90e51d38cc06cc8bb8c8a3e36 | 0x35b240d7f4b99d1d5870b1b7b27dfd6681449614 | BUKAN (pool terawal 2025-10-31, ~25 hari lebih awal) | 30 | 26 | 2 |
| LAB | 0x7ec43cf65f1663f820427c62a5780b8f2e25593a | 0x5d43403cc3869ee31989504b8eb93cd3c2d4cb9f | BUKAN (pool terawal 2025-10-13, ~11 bulan lebih awal) | 17 (hanya itu yang ada) | 13 | 1 |
| DEBIT | 0x66661c7229901f568f16bd1551b3ba826f83ce49 | TIDAK ADA | GAGAL TOTAL (pasar pertama V3 2026-08-24) | — | — | 0 |
| ARIA | 0x5d3a12c42e5372b2cc3264ab3cdcf660a1555238 | 0xbe9b3c913edd6b92cdb987510d1553d066a9e83e (pair USDT, pelengkap berlabel) | BUKAN (pool terawal 2025-08-19, ~13 hari lebih awal) | 30 | 26 | 2 |
| COLLECT | 0x4b3d30992f003c8167699735f5ab2831b2a087d3 | 0x4b5e76fe1acce763a7f23cf10a9db8a9080b5d0d | BUKAN (pool terawal 2025-12-26) | 30 | 14 | 1 |
| AEON | 0x277add739c6e0477616948357af9e79fe1ec9b80 | 0xf3fdb8a12d3543b7b0cbcdccab17a102d0d6ba69 (8 desimal) | BUKAN (pool terawal 2026-07-26) | 30 | 26 | 1 |
| ESPORTS | 0xf39e4b21c84e737df08e2c3b32541d856f508e48 | 0x7b65b50da0156542c916f04e605c6979819b7a77 | BUKAN (pool terawal 2025-07-18, ~4 hari lebih awal) | 30 | 19 | 7 |

Catatan: tanggal "pool dibuat" di laporan sebelumnya adalah tanggal pool PERTAMA, bukan tanggal pembuatan pair V2 — untuk JCT malah pool Infinity CLMM 2026-06-03, padahal pool-pool 2025-11-09/10 lebih awal. ID pair GeckoTerminal yang lebih panjang dari 20 byte tidak pernah dipakai sebagai alamat (sesuai peringatan).

## 3. Matriks repeat-buyer lintas koin (uji §2 tugas)

Kandidat serius mensyaratkan early buyer di ≥2 koin + hold bermakna di ≥1 koin + bersih. Hasil:

| Wallet | Koin (posisi first-30 V2) | Hold | Nilai implisit | Aktif 48 jam | Vonis |
|---|---|---|---|---|---|
| 0x29a4b61a493ca34ab367594594a730fddd131bfa | AKE #5, Q #10, AIN #6, ESPORTS #3 (4 koin) | 0 / 0,1598 Q / 0,0188 AIN / 0,00086 ESPORTS — semua debu | <$0,01 total | 0 incoming di keempat koin (§6) | GAGAL: debu + tidak aktif + frekuensi bot (§7). Bukan kandidat. |
| 0x18e31a59caeae97fa9a30a20df3f72a130147752 | AIN #5, ESPORTS #4 (2 koin) | 0,0257 AIN / 0,00051 ESPORTS — debu | <$0,01 total | 0 incoming di kedua koin | GAGAL: debu + tidak aktif. |
| 0x9b69b82b91d9d610d53b41fc69146d6f96101be8 | AIN #19, ESPORTS #8 (2 koin) | 22,16 AIN / 62,22 ESPORTS (mayoritas dari inflow lanjutan non-pair, bukan posisi awal) | ~$0,15 total | 0 incoming di kedua koin | GAGAL: nilai tidak bermakna + tidak aktif + posisi awal debu (0,033 AIN / 0,0025 ESPORTS). |
| (kontrak, dicoret) 0x8737a10d9c19af8bb2eae0b5e9cfe7b7276e0638 dkk. | Co-buy di COLLECT/AEON/ESPORTS (beberapa kontrak) | — | — | — | CORET: kontrak. Linkage co-buy = LEMAH saja. |

Tidak ada wallet EOA lain yang muncul di ≥2 koin. Linkage KUAT (shared funding/transfer langsung) TIDAK DITEMUKAN di antara kandidat; kata "terbukti insider" tidak pernah dipakai.

## 4. Peringkat terdekat — SEMUANYA GAGAL (tidak ada yang direkomendasikan)

Peringkat ini adalah "yang paling tidak gagal", bukan rekomendasi. Setiap baris mencantumkan alasan gagalnya; tidak satu pun boleh dipromosikan dari data ini.

| Peringkat | Wallet | Bukti per koin | Alasan gagal |
|---|---|---|---|
| 1 (terdekat) | 0x9b69b82b91d9d610d53b41fc69146d6f96101be8 | AIN #19: beli awal 6 jam 0,0333 AIN, saldo 22,1576 AIN, jual ≤1 jam 0%; ESPORTS #8: beli awal 6 jam 0,0025 ESPORTS, saldo 62,2174 ESPORTS, jual ≤1 jam 0%. EOA, bukan daftar coret. | Repeat 2 koin terpenuhi, TAPI: nilai total ~$0,15 (bukan hold bermakna); posisi awal debu (saldo dari inflow lanjutan); tidak aktif 48 jam; V2 pair bukan pasar pertama (bukan early buyer peluncuran). |
| 2 | 0x2b40f892a5b8aefdf9868317330ca0f956f70d2b | Q #9: beli awal 6 jam 56,6244 Q, saldo 86,9690 Q (153,59%), jual ≤1 jam 0%. EOA, bukan daftar coret. | Nilai terbesar riset (~$2,22) TAPI: single-coin (bukan repeat buyer); tidak aktif 48 jam; V2 pair bukan pasar pertama. |
| 3 | 0x8ecb1a8d8fe0c0b4d1ce823210d8d61a615ec9f9 | AKE #12: beli awal 6 jam 0,0107 AKE, saldo 2.700,85 AKE, jual ≤1 jam 0%. EOA, bukan daftar coret. | Nilai ~$0,38 TAPI: single-coin; saldo dari akumulasi belakangan (bukan posisi awal); tidak aktif 48 jam; V2 pair bukan pasar pertama. |
| — | 0x29a4b61a493ca34ab367594594a730fddd131bfa | Repeat 4 koin (lihat §3). | GAGAL BERAT: semua posisi debu + tidak aktif 48 jam + frekuensi transaksi bot (§7). Jangan dipakai sebagai referensi dalam kondisi apa pun dari bukti ini. |
| — | Beat #13 0xa68e2ddbfe9dce42d4f9e61c13ee404ed7979770; LAB #15 0xe92e84af6e2f80794c825ab01ab70a895cf8443f; ARIA #18 0x790a58f7bf9e4d0576618d6002139079fe142346; ARIA #29 0x0930139b38f3f2945419f1ee30ae2bdf42094c62; AEON #1 0xd05c3d496371a0ff17977c526cbd48fa9f520440; COLLECT #24 0xcb764b59f9c436ac08da3690336913ca050d6bb0; ESPORTS #12/#13/#15/#18 0x56a4b3ae3d7d0818db0ed0d88ccad0a70d8f870a / 0x7945003735c62195f0f93a623364c2118fd748ea / 0x212656945203b29a5583242ea454ff8570a23c77 / 0x4c1bbb72c8f43107904db33461910a6fd38f6836; Beat #2 0x40537c0e3362f1fa041b78a840ed987d9869ee49; AIN #21 0x3477efae0d5f9f306d857998e4ada67a2f5f7975 | Masing-masing HOLD 100% (atau PARTIAL tipis Beat #2: 0,54%) dengan saldo debu, jual ≤1 jam 0%, EOA, bukan daftar coret. | GAGAL: single-coin + nilai debu + tidak aktif 48 jam (yang dicek, §6) + V2 pair bukan pasar pertama. |

Yang butuh konfirmasi GMGN: TIDAK ADA dari riset ini yang layak diajukan — GMGN (PnL 30 hari + pola dump) hanya relevan bila ada kandidat yang lolos filter on-chain dulu. Bila parent/user tetap ingin GMGN untuk peringkat 1–3, itu keputusan mereka, bukan rekomendasi laporan ini.

## 5. Valuasi dolar (mengapa "hold bermakna" gagal)

Harga implisit = mcap GeckoTerminal 2026-11-02 17.35 WIB / totalSupply on-chain (dibaca koordinator 2026-11-02 ~21.00 WIB). Mcap bersifat waktu-baca (bukan live); valuasi ini hanya untuk uji "bermakna", bukan harga eksekusi.

| Koin | Mcap (17.35 WIB) | Supply on-chain | Harga implisit | Pegangan terbesar di daftar bersih | Nilainya |
|---|---|---|---|---|---|
| AKE | $141.006.744 | 1.000.000.000.000 | $0,000141 | 2.700,85 AKE (#12) | ~$0,38 |
| Q | $127.318.032 | 4.999.741.619 | $0,0255 | 86,97 Q (#9) | ~$2,22 |
| AIN | $50.253.463 | 1.000.000.000.000 | $0,0000503 | 22,16 AIN (#19) | ~$0,0011 |
| Beat | $37.118.398 | 1.000.000.000 | $0,0371 | <0,005 Beat (#13, tampil 0,00) | <$0,001 |
| LAB | $33.849.985 | 989.999.803 | $0,0342 | 0,12 LAB (#15) | ~$0,004 |
| ARIA | $23.347.932 | 1.000.000.000 | $0,0233 | 0,03 ARIA (#18) | ~$0,0007 |
| COLLECT | $13.350.558 | 3.000.000.000 | $0,00445 | 0,00062 COLLECT (#24) | ~$0,000003 |
| AEON | $5.908.394 | 1.000.000.000 (8 des) | $0,0059 | 0,90 AEON (#1) | ~$0,0053 |
| ESPORTS | $2.231.521 | 900.000.000 | $0,00248 | 62,22 ESPORTS (#8) | ~$0,15 |

## 6. Filter aktif 48 jam — HASIL: NOL untuk semua yang dicek

Window diukur dari header blok: head 131252838; head−384.000 blok berselisih 48,01 jam (block time terukur 0,45 detik/blok). Window: blok 130868838–131252838. Metode: Ankr `getLogs` Transfer dengan topic recipient = wallet, per token.

| Wallet | Koin dicek | Incoming 48 jam |
|---|---|---|
| 0x29a4b61a493ca34ab367594594a730fddd131bfa | AKE, Q, AIN, ESPORTS | 0 di keempatnya |
| 0x18e31a59caeae97fa9a30a20df3f72a130147752 | AIN, ESPORTS | 0 di keduanya |
| 0x9b69b82b91d9d610d53b41fc69146d6f96101be8 | AIN, ESPORTS | 0 di keduanya |
| 0x8ecb1a8d8fe0c0b4d1ce823210d8d61a615ec9f9 (AKE #12) | AKE | 0 |
| 0x2b40f892a5b8aefdf9868317330ca0f956f70d2b (Q #9) | Q | 0 |
| 0xa68e2ddbfe9dce42d4f9e61c13ee404ed7979770 (Beat #13) | Beat | 0 |
| 0xe92e84af6e2f80794c825ab01ab70a895cf8443f (LAB #15) | LAB | 0 |
| 0x790a58f7bf9e4d0576618d6002139079fe142346 (ARIA #18) | ARIA | 0 |
| 0x0930139b38f3f2945419f1ee30ae2bdf42094c62 (ARIA #29) | ARIA | 0 |
| 0xd05c3d496371a0ff17977c526cbd48fa9f520440 (AEON #1) | AEON | 0 |
| 0xcb764b59f9c436ac08da3690336913ca050d6bb0 (COLLECT #24) | COLLECT | 0 |

Batas: cek ini hanya incoming Transfer pada koin-koin tersebut; transfer BNB native dan call tanpa event tidak terlihat (keterbatasan metode Transfer yang sama seperti riset sebelumnya). "Tidak aktif" di sini = tidak ada incoming Transfer pada koin-koin itu di window itu.

## 7. Cek funding 1-hop — hanya untuk pola repeat teratas, dan hasilnya memberatkan

Karena tidak ada finalis yang lolos filter, cek funding penuh tidak dilakukan untuk semua kandidat. Yang dicek: wallet repeat 4-koin 0x29a4b61a493ca34ab367594594a730fddd131bfa, lewat endpoint riwayat transaksi Ankr (`ankr_getTransactionsByAddress`, bekerja tanpa key tambahan — temuan metode yang berguna untuk riset berikutnya).

- 12 halaman × 100 transaksi (1.200 transaksi) hanya mencakup irisan blok 63085786–63376665 (~290.000 blok ≈ 1,5 hari) — frekuensi ~800 transaksi/hari pada irisan itu. Itu pola bot, bukan wallet manusia yang sesekali trading.
- Tidak ada funder native yang teridentifikasi pada irisan itu (tidak ada transaksi dengan penerima = wallet dan nilai BNB > 0 pada 1.200 transaksi yang dipindai; kemungkinan field `to`/`value` pada respons tidak menangkap seluruh bentuk transfer — dicatat sebagai batas, bukan sebagai "tidak ada funder").
- Funding pertama wallet ini TIDAK TERCAPAI (paging dihentikan di 12 halaman karena pola bot sudah jelas dan wallet sudah gagal di semua filter lain). Linkage funding untuk wallet ini: TIDAK DITETAPKAN.
- Untuk kandidat lain: cek funding tidak dilakukan (tidak ada finalis). Bila suatu hari ada finalis sungguhan, endpoint riwayat Ankr ini adalah jalur termurah untuk 1-hop funding — dengan catatan paging sampai transaksi tertua untuk menemukan funder pertama.

## 8. Yang dicoret beserta alasannya

- **Kontrak/bot executor (cek eth_getCode):** AKE 22/30, Q 26/30, IDOL 28/30, AIN 24/30, Beat 26/30, LAB 13/17, ARIA 26/30, COLLECT 14/30, AEON 26/30, ESPORTS 19/30 — termasuk pool-pool lain yang ikut "membeli" (mis. pool COLLECT/WBNB 0,25%, pool ESPORTS/WBNB 0,01%, pool Beat/USDT, pool ARIA/USDT, pool LAB/WBNB, pair V2-USDT LAB sendiri).
- **Fast dump ≤1 jam (≥80% ke pair):** COLLECT 14, AEON 1 (#11, 99,4%), ESPORTS 4 (#10, #11, #14, #16, ~100%), plus fast dump per koin di file pekerja grup 1 dan 3. Aturan coret lintas ≥3 launch tidak terpicu dari dataset ini (tidak ada wallet yang fast-dump di ≥2 koin yang dicek sebagai EOA bersih — fast dump yang ada adalah kontrak atau single-coin).
- **Hub sniper 0xf5988713400da6fc8a58ec9515e2b0df9b40b115 dan funder 0x318d2aae4c99c2e74f7b5949fa1c34df837789b8:** exact-match NIHIL di semua baris first-30 ketiga grup (dengan satu pengecualian di bawah untuk PAIR #1).
- **Token itu sendiri / pair itu sendiri / exchange / klaster MSX / tim-vesting round-amount:** tidak ada yang teridentifikasi positif dari data Transfer saja (pekerja mencatat: daftar alamat MSX/exchange tidak dilampirkan dalam tugas; wallet round-amount hanya ditandai, bukan dicoret otomatis). Klaster MSX hanya dicek exact-match terhadap token MSX 0x23214ccbffb6ef479da64d1842b10b5525997777 (nihil).
- **SOLD (saldo ≤0,5% beli awal 6 jam):** mayoritas EOA first-30 (mis. IDOL: kedua EOA-nya SOLD; Beat #2 PARTIAL tipis 0,54% nyaris SOLD).

## 9. Temuan integritas data — alamat PAIR #1 di laporan re-screen CACAT (perlu perbaikan sumber)

String alamat PAIR #1 yang tercantum di laporan re-screen (`wallet-rescreen-2026-11-02.md` § peringkat 2) adalah `0x2fc2a32f16d683038187b87b87e0409d122da6f17d4` — **43 karakter heksadesimal, bukan 40** — sehingga bukan alamat valid. Pekerja grup 3 menangkap ini dengan benar dan menyatakan cek PAIR #1-nya TIDAK VALID (bukan NIHIL); pekerja grup 1 dan 2 memakai string yang sama sehingga cek tumpang-tindih PAIR #1 mereka juga VOID untuk alamat itu (cek TRIO, PAIR #2, IBS #2, BORT #8, GANG, hub/funder mereka tetap valid — string-string itu 40 karakter dan exact-match-nya nihil, kecuali satu koreksi di bawah).

**Perbaikan yang dilakukan koordinator:** identitas PAIR #1 diuji lewat jalur independen — token ok (0xc853d8253f0d8346ca80f3f6af53e49a763e7777, dari data holder). Kontrol positif: TRIO #1 memegang 1.009.666,14 ok (persis angka re-screen) dan PAIR #2 memegang 11.192.428,27 ok (persis angka re-screen) — token terkonfirmasi. Hasil: **semua kandidat bersih riset ini memegang 0 ok** (19 wallet dicek, termasuk ketiga wallet repeat) — sedangkan PAIR #1 menurut re-screen memegang ~10.639.412 ok. Jadi TIDAK SATU PUN kandidat bersih riset ini adalah PAIR #1 (dengan catatan saldo dapat berubah sejak re-screen; pembacaan ini 2026-11-02 ~21.00 WIB). Untuk baris first-30 non-kandidat, cek tumpang-tindih PAIR #1 tetap TERBUKA sampai alamat benarnya dipulihkan — pemulihan yang disarankan: turunkan dari pembeli token ok pada blok 130788409 (bukan menebak karakter mana yang berlebih dari string 43 karakter itu).

**Koreksi pekerja yang dihormati (VOID yang tidak dipakai):**
- Pekerja grup 2: pembacaan saldo tahap pertama VOID (selector `balanceOf` dari hash keccak penuh) — saldo final dibaca ulang dengan selector 4-byte benar; kesimpulan interim "AEON semua SOLD" dibatalkan.
- Pekerja grup 3: salinan TRIO #2 sempat 41 karakter pada pass pertama (cek VOID) — diperbaiki ke string tugas dan dicek ulang terhadap 67 wallet unik, hasil tetap NIHIL.
- Pekerja grup 1: satu batch besar sempat kena rate limit -32005; tidak ada data yang hilang dari situ (retry dicatat di file pekerja).

## 10. Batas-batas dan gagal baca

- **First-30 V2 ≠ first-30 peluncuran** untuk semua 10 koin yang terpindai (§2). Setiap klaim "early buyer" di laporan ini berarti early buyer pair V2, bukan buyer peluncuran absolut.
- **"Beli" = transfer pair→wallet** — tidak membedakan swap vs tarik likuiditas dari log Transfer saja.
- **Metode Transfer buta** terhadap transfer BNB native dan call tanpa event — funding tidak terlihat kecuali lewat endpoint riwayat (§7).
- **Gagal baca yang dicatat, bukan nol:** `eth_call` historis "missing trie node" (creation pair diambil dari log PairCreated Ankr, bukan binary search); GeckoTerminal ESPORTS halaman 11+ HTTP 401 (paginasi berhenti di 200 pool; vonis pasar-pertama tidak bergantung padanya); satu batch besar -32005 (retry); RPC burst sesekali (retry).
- **Mcaps adalah angka waktu-baca 2026-11-02 17.35 WIB** — valuasi §5 memakai angka itu; harga live saat laporan dibaca bisa berbeda.
- **Tidak ada PnL 30 hari terverifikasi untuk wallet mana pun di sini** — GMGN tidak dipakai (login browser hanya bisa lewat parent) dan tidak ada histori harga di log.

## 11. Langkah lanjut yang disarankan (bukan eksekusi)

1. **Perbaiki alamat PAIR #1 di sumber** (turunkan dari pembeli ok blok 130788409) supaya cek tumpang-tindih masa depan valid — bukan menebak karakter.
2. **Ganti instrumen untuk koin terbentuk:** pindai pool PERTAMA (V3/CLMM) bukan pair V2 — atau pakai pendekatan holder-based (siapa yang memegang banyak koin terbentuk dengan nilai bermakna sekarang, lalu telusuri kapan mereka membeli). First-30 V2 terbukti menghasilkan debu + bot.
3. **Bila tetap ingin kandidat dari riset ini untuk GMGN:** hanya peringkat 1–3 (§4) yang layak disebut, dengan catatan gagalnya — dan tetap bukan rekomendasi.
4. **Endpoint riwayat Ankr (`ankr_getTransactionsByAddress`)** terbukti bekerja — pakai untuk cek funding 1-hop finalis berikutnya, dengan paging sampai transaksi tertua.
5. **Jangan ulangi scan first-30 V2** untuk koin terbentuk lain tanpa cek pasar-pertama dulu — biayanya besar, hasilnya debu.

## 12. Sumber dan waktu baca (audit trail)

- Universe/mcap: GeckoTerminal `trending_pools` + endpoint token/pools — 2026-11-02 17.35–17.45 WIB (laporan sebelumnya §2).
- Pair V2: factory `getPair` on-chain + log `PairCreated` Ankr (selector programatik).
- First-30: Ankr `ankr_getLogs` (module, 1.000/halaman, chunk 10.000 blok; tidak ada chunk yang kena cap 1.000 log pada grup 1 dan 2; grup 3: 0 gagal pada 1.376 + 76 + 1.406 chunk).
- Saldo: `balanceOf` via `fast_rpc` batch (selector 4-byte benar; grup 2 dan 3 memperbaiki bug selector tahap pertama sebelum saldo dipakai).
- Waktu: timestamp header blok (WIB); block time terukur 0,45 detik/blok pada window 384.000 blok (48,01 jam).
- Aktivitas 48 jam: Ankr `getLogs` topic recipient, window blok 130868838–131252838.
- Funding: Ankr `ankr_getTransactionsByAddress` (12 halaman × 100 untuk 0x29a4…).
- Ok-balance kontrol: `balanceOf` token ok 0xc853d8253f0d8346ca80f3f6af53e49a763e7777 (TRIO #1 dan PAIR #2 cocok persis dengan angka re-screen).
- GMGN: tidak dipakai (login-gated; hanya lewat parent).
