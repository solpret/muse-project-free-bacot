# METODE 4 — Leaderboard publik lain (ulangi pola JAGENT)

**Tanggal:** 2026-11-03 (WIB)
**Sifat:** READ-ONLY. Tanpa login, tanpa transaksi, tanpa signature, tanpa layanan berbayar,
tanpa menghubungi siapa pun. Tidak ada wallet yang ditambahkan ke feed, tier-ab, atau Tier C —
output di sini adalah daftar proposal untuk keputusan user saja.
**Standar kejujuran:** sama seperti `metode-1-2.md`. Yang tidak terverifikasi ditulis sebagai
tidak terverifikasi, bukan nol. Bacaan yang gagal ditulis sebagai gagal baca, bukan ketiadaan.
Angka platform (OKX) adalah sinyal discovery saja, BUKAN verifikasi on-chain.

## Ringkasan hasil

- **13 wallet kandidat** diambil dari leaderboard OKX BSC Smart Money (7D top-14, minus baris
  AFeng yang dipakai sebagai baseline, bukan kandidat).
- **0 PASS, 0 WATCH, 13 DITOLAK.** Semua 13 gagal filter (c) — early di ≥3 coin — pada
  kedua definisi yang dipakai (early buyer di ≥3 dari 14 coin terbentuk metode 1–2, maupun
  breadth ≥3 kontrak snapshot Free Bacot dalam 30 hari). Karena (c) gagal untuk semua,
  tidak ada kandidat yang memenuhi syarat WATCH sekalipun (WATCH mensyaratkan (a)(b)(c)(f)(g)
  lolos dengan hanya (d) yang belum terverifikasi dan (e) campuran).
- **Daftar proposal: KOSONG.** Tidak ada wallet yang diusulkan ke feed, tier-ab, maupun Tier C.
- **Satu temuan klaster yang nyata (bukan proposal):** kedua wallet bernickname 西瓜🔶BNB
  adalah SATU operator — xigua-A mendanai xigua-B sebesar 5,179 BNB tepat di blok transaksi
  pertama xigua-B. Keduanya tetap ditolak (gagal (c) + (d) belum terverifikasi), tapi
  keduanya harus dihitung sebagai satu entitas, bukan dua, dalam pekerjaan lanjutan apa pun.
- **Overlap dengan set yang sudah ada: NOL** untuk ke-13 wallet terhadap feed (6), Tier C (4),
  EOA metode 1–2 yang ditolak (10), hub/provisioner klaster metode 1–2 (2), 54 alamat
  plaintext tier-ab, 125 alamat file sheet JAGENT, dan PAIR #1. Pengecualian: overlap TRIO
  tidak bisa diverifikasi dari file yang tersedia (lihat "Keterbatasan") — bukan klaim "tidak
  ada overlap TRIO".

## 1. Sumber yang diperiksa

| Sumber | Status | Keterangan |
|---|---|---|
| OKX BSC Smart Money Leaderboard — `https://web3.okx.com/copy-trade/leaderboard/bsc` | TERBACA, dipakai | Fetch teks 2026-11-03 ~16:41 WIB (halaman di-crawl 2026-11-03 09:41 UTC). Menangkap 7D top-14: nickname/alamat terpotong, 7D PnL, profit rate, win rate, avg buy, volume, jumlah tx. Baris di luar 14 dan window waktu lain TIDAK tertangkap (paginasi/JS) — ini keterbatasan tangkapan, BUKAN bukti hanya ada 14 wallet. Leaderboard ini rolling 7D: crawl 2 hari sebelumnya menampilkan nama lain di papan atas (AntPositions, 0x2757…56b4, Pasterniq) yang tidak ada di top-14 hari ini — keanggotaan berputar. |
| Halaman profil OKX — pola `https://web3.okx.com/portfolio/<alamat>/analysis?chainIndex=56` | TERBACA, dipakai | Setiap baris leaderboard menaut ke halaman profil yang URL/judulnya memuat alamat lengkap 42 karakter. Ke-13 alamat non-AFeng di-resolve dengan cara ini. Untuk 7 baris berlabel terpotong, 4 karakter awal + 4 karakter akhir cocok persis dengan alamat lengkap; untuk baris nickname, URL profil itu sendiri adalah otoritasnya. |
| DEXRabbit BSC traders — `https://dexrabbit.bitquery.io/bsc/traders` | TERBACA, GAGAL EKSTRAKSI | Halaman terbaca (50 wallet, volume 24h $375,34M saat fetch), tapi ALAMAT TRADER TIDAK ADA di teks (tabel di-render JS). Dicatat sebagai gagal ekstraksi, bukan leaderboard kosong. Tidak ada kandidat diambil dari sini. |
| OKX centralized copy-trading leaderboard | TIDAK BISA DIPAKAI | Nickname + performa internal exchange, tanpa alamat on-chain. Tidak ada kandidat. |
| CoinMarketCap DexScan Top Traders | TIDAK DIAKSES | Tidak ditemukan URL board verbatim dari pencarian (hanya artikel berita yang menyebutnya + satu halaman token). URL tidak ditebak. Dicatat sebagai belum diperiksa, bukan gagal dan bukan kosong. |
| Google Sheet "Overall Leaderboard" | DIPERIKSA, DIKECUALIKAN | Dibuka dan dibaca langsung: leaderboard poin XP/GOLD/SILVER/BRONZE, terakhir di-crawl ~250 hari lalu (2026-02-25), ~100 wallet dengan XP nyaris identik (51.850–50.750). Ini leaderboard poin, bukan leaderboard trader — tidak relevan untuk metode ini. |
| Polymarket leaderboard | DIKECUALIKAN | Venue salah: prediction market Polygon, bukan memecoin BSC. |
| Rivo.markets trader leaderboards | DIPERIKSA, DIKECUALIKAN | Muncul di pencarian, tapi tidak spesifik BSC (tidak ada filter chain yang tampak; baris memuat ID bergaya non-EVM). Bukan sumber wallet BSC. |
| GMGN | DILEWATI (login-gated) | Sesuai batas keras: tidak ada upaya login, tidak ada halaman GMGN yang dipakai. |
| OKX onchainos CLI | TIDAK DICOBA | Login CLI mustahil di VM ini (TLS egress CA) — diketahui sebelumnya, tidak diulang. Pembacaan leaderboard via teks web publik tidak memakai CLI ini. |

## 2. Kandidat: 13 wallet OKX (7D top-14 minus AFeng)

Baris 0 leaderboard adalah AFeng (baseline, bukan kandidat — AFeng main
`0xbf004bff64725914ee36d03b87d6965b0ced4903` sudah ada di feed).
Angka PnL/durasi di bawah ini adalah **angka platform OKX, bukan verifikasi on-chain**.

| # | Label leaderboard | Alamat lengkap | 7D PnL (platform) | Catatan platform 1D (tidak terverifikasi) |
|---|---|---|---|---|
| 1 | 0x87b5…69c6 | `0x87b51e0d40d413d2b7ef480e8b327a57df9769c6` | +$25,18K | Rata-rata durasi 1D 20 mnt; penjualan terakhir 19 dtk–5 mnt; FAGENT +$4,41K, GANG +$9,79K (hold 2 jam) |
| 2 | 西瓜🔶BNB (A) | `0x3472ccf6209925204b9cf352171ee150904fda7e` | +$20,82K | Rata-rata durasi 1D 7 jam; 1D PnL +33,62% |
| 3 | 0x0e1c…ce3a | `0x0e1c5ecbba12fa1cb187e3d18f1c0a58bce5ce3a` | +$17,25K | Rata-rata durasi 1D 13 jam |
| 4 | 金狗挖掘机 \| 0xDavid | `0x7a2363a401b2340c7941dd2eeff0196a5078d2e6` | +$16,42K | Rata-rata durasi 1D 10 jam; hold campuran 15 dtk–3 hari |
| 5 | 0x95e0…09d5 | `0x95e02ed458ba54fd640f5b3956ff4178aac809d5` | +$14,54K | Rata-rata durasi 1D 17 jam |
| 6 | gake (OKX) | `0x3c5083022114ea14fb3d8d06f5931c629c2bedd6` | +$13,30K | Total PnL lifetime **−$398,58K (−46,59%)**, win rate 1D 0,00%, saldo $43,19K |
| 7 | 0x5949…6993 | `0x59495c0497abb3c2a60eb7df89b6ad94df8b6993` | +$13,14K | Rata-rata durasi 1D **19 detik** (flip skala detik) |
| 8 | clukz | `0x077b9981bc8a2ca417cea41861111da63266988b` | +$12,20K | Rata-rata durasi 1D **6 detik**; total PnL lifetime hanya +$229,31 |
| 9 | 0xe60e…a4be | `0xe60e67fed34ebb3116ec03995839fdb0be2ba4be` | +$11,51K | 1D PnL −34,85%, win rate 10,71%, saldo **$3,71** (hampir kering), lifetime +$359,20 |
| 10 | 0x4a48…f460 | `0x4a48a8ab550b936aad4f3252281acac1a717f460` | +$11,04K | Rata-rata 1D 8 jam tapi penjualan terakhir mayoritas hitungan detik (25 dtk, 17 dtk, 23 dtk, 5 dtk, 4 dtk, 42 dtk, 7 dtk, 2 dtk, 4 dtk); saldo $179,68 |
| 11 | 0x杨杨｜tapeout | `0xa11e739adf417ffe34e1eba75df2031499192b66` | +$10,97K | Total PnL lifetime +$82,72K (95,94%) versi platform, saldo $251,06, pembelian 1D $0 (hanya jual) |
| 12 | 西瓜🔶BNB (B) | `0x95b998b3ebc4c04fac037ff451144af5c90eda8f` | +$10,90K | Rata-rata durasi 1D 7 jam (cermin baris 2) |
| 13 | 0x1f71…8d18 | `0x1f71ff5ead0270889d0a09badfd47ef584618d18` | +$10,67K | Volume 1D $0, 0 beli/jual dalam 1D; saldo $401,29; lifetime +$1,31K |

**Dua peringatan identitas nickname (jangan digabung berdasarkan nickname):**
- Baris 2 dan 12 berbagi nickname 西瓜🔶BNB tetapi adalah **wallet BERBEDA**
  (`0x3472…fda7e` vs `0x95b9…eda8f`). Daftar trade terakhir OKX keduanya nyaris identik
  (token sama — 歌利亚远征, 차르, 황제, 网上南宁, DPRKaptcha, PONZI, Capytistas, GENESIS —
  pada ukuran ~$170 yang nyaris identik). Itu memunculkan pertanyaan klaster, dan pemeriksaan
  funder (§4a) MENJAWABNYA: satu operator (lihat §5).
- "gake" OKX (`0x3c50…bedd6`) **bukan** gake di sheet JAGENT
  (`0xd898c86c9eedaa2583317563d53f64dd02259717`, ditolak sebagai bot spray-mint).
  Nickname sama, alamat berbeda — perlakukan sebagai wallet terpisah.

**Kaveat transkripsi (dinyatakan plain):** alamat-alamat di atas ditranskripsi dari judul/URL
halaman profil OKX (output browser.open), bukan diekstrak secara programatik dari API.
Mitigasi yang diterapkan: validasi panjang/hex di skrip, kecocokan 4-awal + 4-akhir untuk
ketujuh baris berlabel terpotong, dan otoritas URL profil untuk baris nickname. Tidak ada file
mentah yang bisa dipakai untuk koreksi silang seperti pada metode 1–2, jadi kaveat ini tetap
berdiri.

## 3. Metode screening on-chain

- Modul Ankr `~/workspace/custom-connectors/custom.ankr/bin/ankr.py` (`get_logs` address-filtered,
  `ankr_getTransactionsByAddress`); `eth_getCode` via RPC BSC untuk filter (g).
- Blok terbaru saat screening: **131.410.983**. Window 30 hari = [terbaru − 5.760.000, terbaru].
- Filter (c) definisi metode 1–2: keanggotaan di set early-buyer `m1_coins.json` (14 coin
  terbentuk). Filter (c) sekunder pola JAGENT: breadth = jumlah kontrak snapshot Free Bacot
  berbeda yang disentuh dalam 30 hari (set snapshot = 321 alamat dari contracts + track_c
  sale/token + pending_claims mint/token).
- Filter (e) on-chain: log Transfer token dalam [blok_beli, blok_beli+2000] (~15 menit),
  exit pertama yang memakai tx BERBEDA dari tx beli (kaki kedua same-tx dari swap routed
  atomik bukan penjualan, sesuai preseden metode 1–2).
- Filter (a): pemeriksaan funder native window awal gaya `m2_funding.py` (binary search blok
  tx pertama, lalu transfer native masuk/keluar di window awal, cap 3 halaman).
- Skrip: `m4_screen.py` + `m4_screen.json`; pemeriksaan lanjutan: `m4_deep.py` + `m4_deep.json`.

## 4. Bukti per filter

### (a) Operator independen (funder berbeda — satu operator dihitung sekali)

Diperiksa untuk 6 wallet (sisanya: tidak diperiksa — penolakan tidak bergantung padanya,
bukan klaim "independen" dan bukan "gagal"):

| Wallet | Blok tx pertama | Funder utama window awal | Putusan (a) |
|---|---|---|---|
| 87b5 | 122.407.165 | `0x4bcb85ac9918ad298339af23b1f1ffe38d0c49bc` — 32,136 BNB (3 tx, di blok pertama) + 4,0 BNB dari `0xbaa9cdb39fc7ef9282e340f6dd8ccd78b82c20a0`; ping dust 1e-8–6,4e-8 BNB dari alamat `0x06c0…`, `0x06ca…`, `0x70ae…` (pola dust-ping yang sama seperti di sheet JAGENT — BUKAN bukti klaster); 87b5 sendiri mendanai `0x06c9…` (2,0 BNB) dan `0x70ae983c…` (24,1 BNB; prefix 0x70ae yang sama muncul di pengirim dust — prefix saja bukan bukti identitas, tidak diklaim sebagai klaster) | Funder berbeda dari 5 wallet lain yang diperiksa |
| 95e0 | 122.942.339 | `0x3c783c21a0383057d128bae431894a5c19f9cf06` — 126,81 BNB (1 tx, blok 122.942.603) + 8,5e-06 BNB dari `0x8ab5…` | Funder berbeda |
| 4a48 | 113.323.864 | `0x515b72ed8a97f42c568d6a143232775018f133c8` — 1,49999 BNB (1 tx, di blok pertama) | Funder berbeda |
| xigua-A | 53.436.843 | `0x30f1e138eb61ccdc4b87413508f65e7b41a1845c` — 0,0405 BNB (di blok pertama) + 0,00864 BNB dari `0xdf33…` (hanya 2 tx native di window awal) | Funder berbeda dari wallet lain — TAPI lihat xigua-B |
| xigua-B | 122.239.053 | **xigua-A (`0x3472…fda7e`) — 5,179 BNB (1 tx, TEPAT di blok pertama xigua-B)** + 0,196 BNB dari `0xeb742d…` + transfer kecil dari beberapa alamat prefix `0xeb74…` (4,6e-06–8e-08 BNB); xigua-B juga mendanai `0xeb742d…` 0,1 BNB | **SATU OPERATOR dengan xigua-A** — hitung sekali |
| gake-okx | 42.384.761 | `0xcdd37ada79f589c15bd4f8fd2083dc88e34a2af2` — 7,3246 BNB (1 tx, di blok pertama); gake-okx mendanai `0xb099…` 0,04 BNB × 2 | Funder berbeda |

Tidak satu pun dari 6 funder yang diperiksa cocok dengan hub/provisioner klaster metode 1–2
(`0x4982…`, `0x9b79…`) maupun funder kuartet chesenas sheet JAGENT (`0x1fd6…`).
**Untuk 7 wallet lainnya (0e1c, david, 5949, clukz, e60e, yangyang, 1f71), funder TIDAK
DIPERIKSA — penolakan mereka tidak bergantung pada (a).**

### (b) Aktif 30 hari terakhir: LULUS untuk ke-13 wallet

`ankr_getTransactionsByAddress` window 30 hari, halaman pertama saja (pageSize 1000).
9 wallet mencapai cap 1000 tx (87b5, xigua-A, 0e1c, david, 95e0, 5949, 4a48, xigua-B, 1f71) —
aktivitas terbukti, tapi hitungan halaman pertama adalah batas bawah. Tidak mencapai cap:
gake-okx 88, clukz 458, e60e 880, yangyang 183.

### (c) Early di ≥3 coin: GAGAL untuk ke-13 wallet (kedua definisi)

Definisi metode 1–2 (early buyer di ≥3 dari 14 coin terbentuk): hanya dua hit tunggal —
**95e0 di JAGENT** (beli blok 130.288.713, tx
`0xc460793665114cba7e8d6cfc940e1cb190f6c5bcc11817b2285cfc4a4e1ae5cd`, pool
`0xe6efcdef2b720d1eca2b69edb7ef357725680bea`, token
`0x8e6442663a4f8c50b6132c68d42a30e7dfe4ae15`) dan **4a48 di SAFU-B13B** (beli blok
126.879.531, tx `0xefb75462af739d8a8a690f3b1165dcaed7ae22e017a6f1380d42f42c546f80c7`, pool
`0x13b86fcf85c9c8f5c36593822d216b8893c25450`, token
`0xdd806e436dda5588bf54061c11590c77ddc87777`). 11 wallet lainnya: 0.
Kaveat: set early SAFU-B13B terpotong di 200/366 — ketidakhadiran di 200 pertama bukan bukti
tidak pernah membeli.

Definisi sekunder pola JAGENT (breadth ≥3 kontrak snapshot dalam 30 hari): hanya dua wallet
menyentuh apa pun, masing-masing tepat 1 kontrak — 87b5 dan e60e sama-sama menyentuh **BOLT
`0xbbdd8c7720d1eeb1d63738eaabb584a4b72c7777`** (ERC20, status snapshot
`non-lead-platform-token-2026-11-03` — token platform, bukan launch, jadi sentuhan tunggal ini
pun lemah). 11 wallet lainnya: 0. Kaveat cap halaman pertama yang sama berlaku untuk 9 wallet
yang mencapai cap.

### (d) REALIZED profit terverifikasi: BELUM TERVERIFIKASI untuk ke-13 wallet

Status yang sama seperti metode 1–2. Angka PnL OKX di §2 adalah angka platform yang
dilaporkan OKX — sinyal discovery saja, dan TIDAK disajikan sebagai verifikasi on-chain.
Tidak ada upaya baca harga arsip yang dilakukan (metode 1–2 sudah membuktikan baca arsip blok
lama gagal di semua RPC gratis, dan tidak ada kandidat yang lolos (c) sehingga rekonstruksi
on-chain per-trade tidak dapat dibenarkan).

### (e) Bukan dumper (tidak ada dump skala menit)

Diperiksa on-chain untuk 2 hit early metode 1–2; sisanya mengandalkan angka platform atau
tidak diperiksa (penolakan tidak bergantung padanya):

- **95e0 → JAGENT: GAGAL (e).** Exit pertama yang mengarah ke pool dengan tx berbeda dari
  tx beli: blok 130.288.765, selisih **52 blok (~2,6 menit pada 3 dtk/blok)** dari blok beli
  130.288.713, tx `0x527cf61a1e900c4d5eba5f343efa4ae9b2ddf4b4ba7ef664f5fa6ef86ca073f7`.
  Total 5 tx exit berbeda dalam window 15 menit; tiap tx exit memuat kaki pool + kaki ke
  `0x3643a907f875fa9b740e1c0747e91b5aa5222ab8` + burn ke `0x000…dead` (mekanika tax/burn
  token — kaki tax tersebut bukan bukti wallet ini fee receiver; wallet ini adalah pengirim,
  bukan penerima).
- **4a48 → SAFU-B13B: tidak ada exit skala menit pada observasi ini.** Exit pertama ke pool
  dengan tx berbeda: blok 126.880.122, selisih **591 blok (~29,6 menit)** dari blok beli
  126.879.531, tx `0xe062c140b2f46c4dd6c27c1023db83d8a656c37f61deaf448b657669d9e16821`.
  Catatan: 112 tx exit berbeda dalam window 15 menit — frekuensi churn tinggi, tapi exit
  pertama bukan skala menit, jadi (e) dalam arti sempit ("tidak ada dump skala menit") lolos
  untuk observasi tunggal ini. Tetap ditolak karena (c) + (d).
- **5949 / clukz: (e) hanya dari angka platform** — rata-rata durasi 1D 19 detik / 6 detik
  (skala detik, konsisten dengan flip). Alamat token profil mereka terpotong, jadi tidak ada
  timing exit on-chain yang dibuat-buat untuk mereka.
- **Wallet lain: (e) tidak diperiksa on-chain** — penolakan tidak bergantung padanya.

### (f) Bukan passive fee receiver

Tidak ada pola fee receiver yang tampak di window yang diperiksa. Tidak ada full fee screen
(getLogs menyeluruh) yang dijalankan untuk ke-13 wallet, karena tidak ada kandidat yang lolos
(c) sehingga screen penuh tidak dapat dibenarkan. Dicatat sebagai "tidak ada pola fee
receiver di window yang diperiksa; screen penuh tidak dijalankan karena (c) sudah gagal" —
bukan sebagai lolos (f) penuh.

### (g) Bukan exchange atau contract

- 8 EOA murni (code `0x`): 87b5, 0e1c, 95e0, 5949, clukz, e60e, 4a48, 1f71.
- 5 wallet terdelegasi (code `0xef01` + delegate 20 byte, total 48 karakter): xigua-A, david,
  gake-okx, yangyang, xigua-B. Sesuai preseden metode 1–2, delegasi saja BUKAN putusan
  (AFeng sendiri adalah EOA + delegasi 0xef01).
- Detail delegasi (terverifikasi): xigua-A, gake-okx, dan xigua-B berbagi code IDENTIK
  `0xef010063c0c19a282a1b52b07dd5a65b58948a07dae32b` (delegate
  `0x0063c0c19a282a1b52b07dd5a65b58948a07dae32b`); david mendelegasikan ke
  `0x00e40ccb2d94975c51bff0c004efdfd9b3a5796fa4`; yangyang ke
  `0x006c35fbcf24e57e5aa2e3aa2ca82e052499d02cf8`. Delegate contract yang dibagi adalah
  **infrastruktur bersama, bukan bukti operator** — tidak dilaporkan sebagai temuan klaster
  dengan sendirinya. (Klaster xigua dibuktikan oleh pendanaan langsung, §4a, bukan oleh
  delegate bersama.)

## 5. Wallet yang ditolak, dengan alasan

Semua 13 ditolak terutama karena **(c) gagal + (d) belum terverifikasi**. Alasan sekunder
membedakan mereka:

| Wallet | Alasan penolakan |
|---|---|
| 87b5 | (c) 0/14 + breadth 1 (BOLT, token platform) + (d) belum terverifikasi. Durasi platform campuran (beberapa penjualan hitungan detik) dicatat tapi bukan dasar penolakan. |
| xigua-A + xigua-B (SATU operator) | (c) 0/14 + breadth 0 + (d) belum terverifikasi. Dihitung sekali karena pendanaan langsung A→B. Daftar trade platform yang nyaris identik konsisten dengan satu operator. |
| 0e1c | (c) 0/14 + breadth 0 + (d) belum terverifikasi. Durasi platform lebih panjang (13 jam) tidak menyelamatkan (c). |
| david | (c) 0/14 + breadth 0 + (d) belum terverifikasi. Hold platform campuran tidak menyelamatkan (c). |
| 95e0 | (c) 1/14 (hanya JAGENT) + (d) belum terverifikasi + **(e) GAGAL — exit pertama ~2,6 menit setelah beli**. Penolakan multi-alasan. |
| gake-okx | (c) 0/14 + breadth 0 + (d) belum terverifikasi + total PnL lifetime platform NEGATIF −$398,58K (−46,59%) + win rate 1D 0,00%. Bukan gake sheet JAGENT. |
| 5949 | (c) 0/14 + breadth 0 + (d) belum terverifikasi + durasi platform skala detik (rata-rata 19 dtk). |
| clukz | (c) 0/14 + breadth 0 + (d) belum terverifikasi + durasi platform skala detik (rata-rata 6 dtk) + total PnL lifetime platform hanya +$229,31 (tipis). |
| e60e | (c) 0/14 + breadth 1 (BOLT, token platform) + (d) belum terverifikasi + saldo platform $3,71 (hampir kering) + 1D PnL platform −34,85%. |
| 4a48 | (c) 1/14 (hanya SAFU-B13B) + (d) belum terverifikasi. (e) lolos sempit (exit pertama ~29,6 menit) dan saldo platform tipis ($179,68) + penjualan platform hitungan detik dicatat, tapi bukan dasar penolakan — (c) sudah cukup. |
| yangyang | (c) 0/14 + breadth 0 + (d) belum terverifikasi. Total PnL lifetime platform +$82,72K tidak dihitung sebagai profit terverifikasi; pembelian 1D $0 (hanya jual) dicatat. |
| 1f71 | (c) 0/14 + breadth 0 + (d) belum terverifikasi + aktivitas terakhir tipis (volume 1D $0, 0 beli/jual 1D, saldo $401,29). |

## 6. Daftar proposal

**KOSONG — tidak ada wallet yang diusulkan.**

- 0 PASS (lolos semua 7 filter).
- 0 WATCH. Standar WATCH metode 1–2 mensyaratkan (a)(b)(c)(f)(g) lolos dengan hanya (d) yang
  belum terverifikasi dan (e) campuran — di sini (c) gagal untuk semua, jadi tidak ada
  kandidat yang memenuhi syarat WATCH apa pun.
- Tidak ada yang ditambahkan ke feed, tier-ab, atau Tier C. Tidak ada tindak lanjut eksekusi
  yang diminta dari laporan ini.

## 7. Temuan yang layak dibawa ke depan (bukan proposal)

1. **Pasangan xigua = satu operator, terbukti lewat pendanaan.** Bila salah satu muncul lagi
   di sumber lain, keduanya harus diperlakukan sebagai satu entitas. Ini satu-satunya temuan
   klaster baru metode 4.
2. **Leaderboard OKX adalah jendela 7D yang berputar.** Papan atas hari ini ≠ papan atas 2
   hari lalu. Satu tangkapan bukan daftar referensi yang stabil — pengulangan metode ini di
   hari lain akan menghasilkan kandidat yang berbeda.
3. **Rank/penghasilan platform OKX bukan bukti smart money.** Rank 7D teratas sekalipun
   (87b5, +$25,18K) tidak memiliki satu pun early record di 14 coin terbentuk, dan satu
   kandidat dengan angka platform kuat (95e0) terbukti exit dalam ~2,6 menit secara on-chain.
   Pola yang sama seperti sheet JAGENT: rank platform ≠ bukti.
4. **Pola dust-ping berulang.** Ping dust skala 1e-8 BNB muncul lagi di sekitar 87b5 dan
   xigua-B, seperti di sheet JAGENT — konsisten dengan pelajaran: dust ping BUKAN bukti
   klaster.
5. **DEXRabbit dan DexScan belum menghasilkan kandidat.** DEXRabbit gagal ekstraksi alamat
   (JS); DexScan belum diakses karena tidak ada URL board verbatim. Keduanya tetap menjadi
   sumber yang belum tergarap untuk pengulangan metode ini, bukan sumber yang sudah
   dibuktikan kosong.

## 8. Keterbatasan (dinyatakan plain)

- Alamat kandidat ditranskripsi dari judul/URL profil OKX, bukan dari API (lihat kaveat §2).
- Hanya 7D top-14 yang tertangkap; baris di luar 14 dan window lain tidak tertangkap.
- Hitungan tx 30 hari adalah halaman pertama saja; 9 dari 13 mencapai cap 1000 (batas bawah).
- Set early SAFU-B13B terpotong di 200/366; ketidakhadiran bukan bukti tidak pernah membeli.
- (d) belum terverifikasi untuk semua — tidak ada upaya baca harga arsip yang dilakukan
  (sudah terbukti gagal di metode 1–2; tidak ada kandidat yang lolos (c)).
- (a) hanya diperiksa untuk 6 wallet; (e) on-chain hanya untuk 2 hit early; (f) tanpa screen
  penuh — semua karena (c) sudah menggagalkan semua kandidat, bukan karena kelalaian yang
  disembunyikan.
- **Overlap TRIO tidak dapat diverifikasi dari file yang tersedia** (alamat anggota TRIO tidak
  ada di file yang dikonsultasikan). Klaim "nol overlap" di laporan ini TIDAK mencakup TRIO.
- Blok terbaru screening 131.410.983; aktivitas setelah blok itu tidak tercakup.

## 9. File kerja

- `m4_screen.py`, `m4_screen.json` (screening 13 wallet: code, tx 30 hari, breadth snapshot)
- `m4_deep.py`, `m4_deep.json` (probe funder 6 wallet; log exit 2 hit early)
- Sumber: `metode-1-2.md`, `m1_coins.json`, `m2_funding.py`,
  `wallet-sheet-screening-2026-11-03.md`, `tier-ab-watch-state.json`, snapshot Free Bacot
