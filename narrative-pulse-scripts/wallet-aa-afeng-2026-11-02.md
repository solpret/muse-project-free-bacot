# Investigasi wallet referensi: @aa_AFeng (阿峰_Afeng)

**Tanggal:** 2026-11-02 (WIB) — **BSC only, READ-ONLY total.**
Tidak ada login GMGN, koneksi wallet, signing, pembelian, follow, atau perubahan
state/feed/cron/snapshot apa pun. Satu-satunya file yang ditulis adalah laporan ini.

## 1. Identitas + sumber wallet

- **Akun X:** @aa_AFeng, nama tampil **阿峰_Afeng** — KOL meme BSC berbahasa Mandarin.
  Followin.io (crawl lama, 2026-02-09): 23.868 followers.
- **twitterapi.io:** HTTP 402 "Credits is not enough" — kredit provider habis,
  jadi bio/postingan X TIDAK terverifikasi lewat API. Jalur browser dipakai sebagai gantinya.
- **Wallet yang terhubung secara publik:**
  **`0xbd28edf53231cd121a963b4b119d3cc4cb3a368a`**
  Sumber: halaman analisis portofolio OKX Wallet yang memberi label
  "阿峰_Afeng" tepat pada alamat ini:
  https://web3.okx.com/es-es/portfolio/0xbd28edf53231cd121a963b4b119d3cc4cb3a368a/analysis
  (diambil 2026-11-02 13:36 UTC). Halaman yang sama menampilkan saldo kecil
  ($2,27) dan total PnL −$2,75 pada jendela tampilannya — lihat §5 soal
  ketidakcocokan dengan leaderboard.
- **Sumber kedua (nama saja, tanpa alamat):** leaderboard OKX BSC Smart Money
  menampilkan baris "阿峰_Afeng +$49,77K (7D), +20,22%, win rate 55,93%,
  avg buy $391,67, volume $607,23K, 1.864 transaksi, aktivitas terakhir 3 jam lalu"
  (cuplikan pencarian, crawl ~4 hari sebelum 2026-11-02). Baris leaderboard ini
  TIDAK menampilkan alamat di cuplikan — keterkaitannya dengan 0xbd28… di atas
  TIDAK terbukti dari leaderboard itu sendiri, hanya dari label halaman portofolio OKX.

## 2. Profil wallet utama 0xbd28edf53231cd121a963b4b119d3cc4cb3a368a

- **EOA privat, bukan kontrak, bukan exchange:** `eth_getCode` = `0x`
  (kosong). Bukan bot/executor dari bentuknya: pola perdagangannya manual
  (approval ke banyak token, ukuran kecil, venue agregator).
- **Saldo BNB sekarang:** 0,01400042 BNB. **Nonce/txcount:** 8.525.
- **Saldo total (Ankr `ankr_getAccountBalance`):** $11,96 pada 32 aset —
  BNB 0,014 ($9,89), NOXO 5,74 ($2,02), sisanya debu (BOT $0,026, dll).
  **Catatan batas:** Ankr dapat melewatkan memecoin tanpa harga, jadi angka ini
  adalah batas bawah, bukan bukti mutlak tidak ada token lain. Namun §3
  memperkuatnya: 10 token yang paling banyak diperdagangkan semuanya bersaldo 0.
- **Sampel transaksi:** 600 transaksi terbaru via `ankr_getTransactionsByAddress`
  (12 halaman × 50), blok 112.667.218–131.197.466, 2026-07-28 s/d 2026-11-02
  07:02 UTC. 7.925 transaksi yang lebih tua (sebelum 2026-07-28) TIDAK diperiksa.
- **Venue utama:** kontrak proxy 0x1de460f363af910f51726def188f9004276bf4bc
  (TransparentUpgradeableProxy, 56 juta+ transaksi; internal tx menunjukkan
  Four.meme Token Manager) — **240 panggilan** dengan selector `0x4d819a2a`,
  total nilai 22,3375 BNB, 2026-07-28 s/d 2026-10-22. Puncak 2026-08-09 (54
  panggilan). Setelah itu meredup: 2026-09-23 = 23 panggilan (burst),
  2026-10-10 = 3, 2026-10-22 = 1 (terakhir).
  (Catatan: menganalisis venue pihak ketiga ini BUKAN menghidupkan kembali
  topik Four.meme user yang sudah dibatalkan — ini murni bukti profil.)
- **Approval:** 173 approval ke 139 kontrak token berbeda — pedagang aktif
  multi-token pada masanya, bukan satu-token holder.
- **Aktivitas 48 jam terakhir: HANYA 4 transaksi, dan tidak satu pun perdagangan
  token.** Isinya transfer native kecil ke wallet saudara 0x6ca69ed2…
  (0,002941 / 0,002998 / 0,000998 BNB) plus satu inbound debu 0,00001 BNB dari
  0x6ca6118a… (wallet segar, nonce 0). **Sebagai pedagang, wallet ini TIDAK
  aktif baru-baru ini.** Transaksi terakhir: 2026-11-02 07:02 UTC (±14:02 WIB),
  ±6,5 jam sebelum laporan ini.

### Uji early-entry (1 token diuji tuntas — SPY)

Token dengan panggilan router terbanyak:
**0x7138b48df7d98d7e3cc221bfe7192d0a178182d8 = SPY (bStocks Tokenized Stock)**,
token saham tokenisasi yang sudah mapan (harga ±$763, FDV ±$19,2 jt per
GeckoTerminal) — BUKAN peluncuran meme baru.
- Transfer masuk ke wallet: 34, total 152.912.972.056.317.285 (18 desimal,
  ±0,1529 SPY); blok pertama 114.358.274.
- Transfer keluar: 2, total PERSIS sama → **saldo sekarang 0 (terverifikasi
  via `balanceOf`)**. Keluar terakhir blok 123.510.698 (2026-09-23, hari burst).
- Ukuran beli kecil (±0,0052 SPY ≈ $4 per pembelian tipikal).
- Pola jual: akumulasi berminggu-minggu lalu keluar penuh pada 2026-09-23 —
  **BUKAN dump ≤1 jam**, jadi token ini TIDAK memicu exclusion bar.
- **Early-entry terverifikasi: 0 dari 3 yang disyaratkan.** Tidak ada satu pun
  token yang pembelian pertamanya dibandingkan dengan waktu peluncurannya
  dan terbukti "lebih awal". Token-token lain yang paling banyak diperdagangkan
  (0xbe9d1568… 28 panggilan, 0x7130d2a1… 12, dst.) hanya tercatat dari sisi
  panggilan router — atribusi itu sendiri berisik (satu panggilan dapat memuat
  beberapa alamat), sehingga TIDAK diklaim sebagai early-entry.

### Uji saldo token-token teratas

`balanceOf` wallet untuk 10 token teratas dari panggilan router =
**semuanya 0**: 0x7138b48d…, 0xbe9d1568…, 0x7130d2a1…, 0x205812cd…,
0x21caef8a…, 0x02fca66c…, 0x5b1910ea…, 0x769d8211…, 0x6d33a6e2…,
0xe9337dde…. Wallet ini sudah keluar penuh dari semua token yang paling
sering diperdagangkannya, paling lambat pada burst 2026-09-23.

### Uji exclusion bar (dump ≥80% dalam ±1 jam di ≥3 launch)

**Tidak dapat dinyatakan bersih penuh** — hanya 1 token diuji tuntas (SPY,
lolos: keluar berminggu-minggu setelah akumulasi). Tidak ada bukti dump-bar
pada token yang diuji maupun pada agregat (tidak ada exit massal cepat kecuali
burst 2026-09-23 yang terjadi berminggu-minggu setelah akumulasi).
Keterbatasan ini dicatat, bukan ditutupi — dan tidak mengubah verdict, karena
kriteria lain sudah gagal (lihat §6).

## 3. Peta wallet terhubung (hingga mentok dari data yang tersedia)

### STRONG — transfer langsung berulang

| Wallet | Bukti | Penilaian |
|---|---|---|
| **0x6ca69ed23e657f3d5ddeb9d38211adf2a5c55eba** (saudara) | EOA, txcount 36, saldo 0,1782 BNB. Menerima **26,624226 BNB dari wallet utama dalam 19 transaksi** (sampel). Dalam 100 transaksi terbarunya, inbound dari wallet utama 17×; outbound ke 0x3508dca9… (17×) dan 0x7a465899… (6×). Pola pass-through. | **STRONG linkage** (transfer langsung berulang). Operator sama vs independen: TIDAK terbukti — tidak ada bukti co-buy token (sampelnya hanya transfer), jadi ini dicatat sebagai wallet terhubung kuat, BUKAN sebagai "operator yang sama terbukti". |

### WEAK — pendanaan bersama / pola bersama / kemiripan, BUKAN bukti operator sama

| Wallet | Bukti | Penilaian |
|---|---|---|
| **0x786a0c878875c1b83362c707f56b5c40f93bbf63** (sumber dana terbesar) | EOA, txcount 119.057, saldo 205,79 BNB. Mengirim **189,39871 BNB ke wallet utama dalam 18 transaksi**. Polanya payout massal kecil ke banyak alamat berbeda (halaman BscScan-nya penuh transfer kecil ke penerima acak). | **WEAK untuk operator sama.** Ini terlihat seperti dompet distributor/layanan (payout), bukan funder pribadi. Dana dari sumber yang melayani banyak penerima TIDAK membuktikan satu operator. |
| **0xbf004bff64725914ee36d03b87d6965b0ced4903** (tujuan cash-out) | Menerima **134,554299 BNB dari wallet utama dalam 11 transaksi** (dan mengirim balik 9,83633 BNB, 4×). Txcount 253.030, kode hanya 23 byte, saldo 28,253 BNB. Label BscScan TIDAK didapat (HTTP 403, tidak diulang). | **WEAK.** Tujuan cash-out bervolume tinggi yang tak teridentifikasi — konsisten dengan deposit layanan/bursa, tapi identitasnya TIDAK dikonfirmasi, jadi tidak diklaim. |
| **Klaster 0xbf00…** (0xbf009ae4…, 0xbf0e8f87…, 0xbf003b08…, 0xbf0058bd…, 0xbf017d07…) | Berulang kali berinteraksi dengan wallet utama DAN wallet saudara, sebagian besar transaksi 0-value/debu (mis. 0x6ca67980… 6×, 0xbf003b08… 11× ke wallet utama; 0xbf009ae4… 23× dan 0xbf0e8f87… 13× ke wallet saudara). | **WEAK.** Pola awalan bersama + interaksi dengan kedua wallet, tapi identitas layanan di balik klaster ini TIDAK terkonfirmasi. Bukan bukti satu operator. |
| **0xbd2810cd327ddecbe5b011ee4060f82ebac8368a** | Mendanai wallet saudara 6× dalam sampel 100 transaksi. Berbagi awalan `bd28` dengan wallet utama. | **WEAK (hanya kemiripan awalan + dana ke saudara).** TIDAK ada transfer langsung yang teramati antara alamat ini dan wallet utama, jadi keterhubungan ke wallet utama tidak terbukti. |

### Tidak ditemukan

- **Co-buy:** tidak ada bukti co-buy token antara wallet utama dan wallet
  terhubung mana pun (sampel wallet saudara hanya berisi transfer, bukan
  perdagangan). Tidak diklaim ke arah mana pun.
- **Wallet terhubung lain:** tidak ada lagi yang muncul dari 600 transaksi
  terbaru wallet utama + 100 transaksi wallet saudara. Graf mentok di titik
  ini: asal dana pertama wallet utama (sebelum 2026-07-28) dan identitas
  layanan di balik klaster 0xbf00… / 0x786a… tidak terjangkau dari sumber
  yang dipakai — dicatat sebagai batas, bukan diisi dugaan.

## 4. Fakta yang TIDAK ditulis

- Tidak ada klaim "terbukti insider" di mana pun dalam laporan ini — semua
  keterhubungan diklasifikasikan STRONG/WEAK sesuai bukti di atas.
- Alamat 0xbd28… TIDAK disamakan dengan pedagang leaderboard OKX — lihat §5.

## 5. Ketidakcocokan identitas (temuan terpenting kedua)

Profil on-chain 0xbd28… **bertentangan** dengan profil pedagang leaderboard
OKX yang memakai nama yang sama:

| | Leaderboard OKX (nama 阿峰_Afeng) | Wallet 0xbd28… (on-chain) |
|---|---|---|
| Transaksi | 1.864 dalam 7 hari | 4 dalam 48 jam terakhir; 0 perdagangan token |
| Volume | $607,23K / 7 hari | ±22,34 BNB nilai panggilan router dalam 3 bulan sampel |
| Aktivitas terakhir | 3 jam lalu (saat crawl) | Perdagangan terakhir 2026-10-22; transaksi terakhir transfer debu |
| Saldo | — (tidak tampil) | $11,96 total |

Kemungkinan penjelasannya: (a) label OKX pada halaman portofolio adalah label
komunitas yang tidak terverifikasi sebagai pernyataan diri; atau (b) 0xbd28…
adalah wallet sampingan, sementara wallet perdagangan utama AFeng berbeda dan
tidak terhubung publik di sumber yang diperiksa. **Keduanya tidak dapat
dibedakan dari data ini — dan keduanya meruntuhkan alasan menambahkan alamat
ini sebagai kompas arah uang.**

## 6. Verdict: TIDAK LAYAK ditambah

| Kriteria "layak" | Hasil |
|---|---|
| Minimal 3 early-entry terverifikasi | **GAGAL — 0 terverifikasi** |
| Masih memegang bermakna di ≥1 token | **GAGAL — 10 token teratas bersaldo 0; total Ankr $11,96** |
| Bersih dari exclusion bar | **Tidak terbukti penuh** (1 token diuji, lolos; sisanya tidak diuji tuntas) |
| Bukan exchange/kontrak/bot | Lolos bentuknya (EOA privat, pola manual) |
| Aktif baru-baru ini (sebagai pedagang) | **GAGAL — perdagangan terakhir 2026-10-22; 48 jam terakhir hanya transfer debu** |

**Rekomendasi: JANGAN tambahkan 0xbd28… ke set pantau (observasi saja
sekalipun).** Wallet ini adalah pedagang kecil yang sudah berhenti berdagang
dan sudah keluar penuh — bukan kompas arah uang yang hidup.

**Langkah lanjut bila user tetap ingin melacak AFeng:** cari wallet perdagangan
utama yang benar — yaitu wallet di balik baris leaderboard OKX (klik baris
leaderboard sampai alamat tampil) atau profil GMGN AFeng. Pekerjaan itu butuh
browser (tugas parent) dan BUKAN dilakukan di sini; tanpa alamat itu, tidak
ada rekomendasi penambahan apa pun.

## 7. Batas & ketidakpastian (lengkap)

1. twitterapi.io HTTP 402 (kredit habis) — bio/postingan X tidak terverifikasi
   via API; identifikasi bersandar pada label halaman portofolio OKX +
   cuplikan pencarian.
2. Label OKX bisa saja label komunitas, bukan pernyataan diri AFeng.
3. BscScan mengembalikan HTTP 403 untuk 0xbf004bff… — labelnya tidak didapat
   dan TIDAK dicoba ulang.
4. Ankr `ankr_getAccountBalance` dapat melewatkan memecoin tanpa harga.
5. 7.925 transaksi wallet utama sebelum 2026-07-28 tidak diperiksa; atribusi
   panggilan router per token berisik (satu panggilan dapat memuat beberapa
   alamat) sehingga tidak dipakai untuk klaim early-entry.
6. Uji dump-bar hanya tuntas untuk 1 token (SPY); exclusion bar tidak
   dinyatakan bersih penuh.
7. Asal dana pertama dan identitas layanan klaster 0xbf00…/0x786a… tidak
   terjangkau dari sumber yang dipakai.
8. Harga/angka leaderboard berasal dari cuplikan pencarian (crawl ±4 hari),
   bukan pembacaan langsung saat ini.
