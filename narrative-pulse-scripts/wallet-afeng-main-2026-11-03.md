# Deep-dive wallet dagang utama AFeng: 0xbf004bff64725914ee36d03b87d6965b0ced4903

**Tanggal:** 2026-11-03 (WIB) — **BSC only, READ-ONLY total.**
Tidak ada login GMGN, koneksi wallet, signing, pembelian, follow, atau perubahan
state/feed/cron/snapshot apa pun. Satu-satunya file yang ditulis adalah laporan ini.
Wallet ini TIDAK ditambahkan ke set pantau mana pun oleh laporan ini — penambahan
adalah keputusan parent/user setelah membaca verdict di §7.

Laporan ini adalah kelanjutan dari investigasi @aa_AFeng 2026-11-02
(`wallet-aa-afeng-2026-11-02.md`), yang menemukan wallet dorman yang salah
(`0xbd28edf53231cd121a963b4b119d3cc4cb3a368a`) dan merekomendasikan pencarian
wallet utama yang benar. Wallet utama itu kini terkonfirmasi (lihat §1) dan diuji
di sini dengan bar kriteria yang SAMA seperti investigasi lama.

## 1. Identitas + sumber wallet

- **Akun X:** @aa_AFeng, nama tampil **阿峰_Afeng** — KOL meme BSC berbahasa Mandarin.
- **Bukti identitas (browser task OKX, 2026-11-03 ~05:38 WIB, read-only):**
  mengklik baris peringkat #1 "阿峰_Afeng" pada leaderboard OKX Web3 Smart Money
  untuk BSC (https://web3.okx.com/id/copy-trade/leaderboard/bsc) membuka langsung
  halaman analisis portofolio untuk alamat ini, dan header halaman menampilkan
  nama "阿峰_Afeng" dengan badge X terverifikasi pada alamat tersebut:
  https://web3.okx.com/id/portfolio/0xbf004bff64725914ee36d03b87d6965b0ced4903/analysis?chainIndex=56
- **Statistik baris leaderboard 7 hari saat dilihat:** PnL +$57,48K, +25,95%,
  win rate 56,40%, beli rata-rata $343,01, volume $549,12K, **1.864 transaksi**
  (cocok persis dengan data investigasi lama → baris yang sama), aktivitas
  terakhir 4 jam lalu.
- **Profil wallet 7 hari (tampilan OKX):** saldo $16,11K (23,136755 BNB),
  PnL total +$120,66K, PnL belum terealisasi −$215,95K, beli/jual 106/135,
  durasi rata-rata 2 jam. Saldo BNB OKX ini cocok PERSIS dengan pembacaan
  on-chain fresh di §2 — konfirmasi silang yang kuat bahwa ini wallet yang sama.
- **Jalur GMGN: TERBLOKIR (sesuai batasan tugas, tidak diakali).** Pencarian
  trader GMGN menemukan profil KOL "阿峰_Afeng @aa_AFeng" yang terlihat publik
  (Profit 7 Hari +$28.357,40, 37,4K pengikut), tetapi membuka halaman profilnya
  langsung memunculkan modal login wajib — tanpa login, tidak ada alamat wallet
  yang terlihat publik dari GMGN. Tidak ada login, klik login/sign up, koneksi
  wallet, atau signing yang dilakukan.

## 2. Profil fresh (dibaca ulang, bukan diasumsikan dari laporan lama)

| Item | Hasil fresh | Keterangan |
|---|---|---|
| `eth_getCode` | 23 byte: `0xef0100cc0c946eecf01a4bc76bc333ea74ceb04756f17b` | **Delegasi EIP-7702** ke `0xcc0c946eecf01a4bc76bc333ea74ceb04756f17b` |
| Kontrak delegasi | 3.834 byte, Sourcify terverifikasi | ABI: `entryPoint`, `execute`, `executeBatch`, `executeBatchAndSkipFailures`, `getNonce`, `isValidSignature`, `validateUserOp`, `supportsInterface`, handler ERC-721/1155 → **implementasi akun ERC-4337 standar** |
| Saldo BNB | **23,136755145903674 BNB** | Cocok persis dengan profil OKX ($16,11K). Laporan lama mencatat 28,253 BNB — selisih ±5,1 BNB adalah pergerakan trading ±16 jam terakhir, bukan kesalahan data |
| Txcount | **253.155** | Laporan lama: 253.030 → +125 sejak saat itu |
| Head block saat baca | 131.323.120 | — |

**Penilaian bentuk:** wallet ini adalah EOA dengan delegasi 7702 ke implementasi
smart account standar — yaitu **smart wallet pengguna**, bukan exchange, bukan
kontrak executor/bot mandiri. Catatan penting: txcount 253.155 seumur hidup dan
frekuensi di §3 berskala otomasi (lihat §7, baris "bukan bot") — data on-chain
saja tidak dapat membuktikan atau membantah pemakaian tool otomasi oleh trader.

## 3. Aktivitas 48 jam terakhir: PERDAGANGAN TOKEN, bukan transfer native saja

Sampel: 1.200 transaksi terbaru via `ankr_getTransactionsByAddress` sebagai
MODULE (paging, bukan CLI), blok 130.764.842–131.286.826,
2026-10-31 00:56 UTC s/d 2026-11-02 18:12 UTC (= 07:56 WIB 31 Okt s/d 01:12 WIB
3 Nov). Transaksi terbaru yang teramati di listing Ankr: blok 131.286.826,
01:12 WIB 3 Nov (hash `0x454c854a…`, panggilan Four.meme proxy).

Jendela 48 jam sebelum ~05:44 WIB 3 Nov (mulai 05:44 WIB 1 Nov):

| | Jumlah |
|---|---|
| Total transaksi dalam jendela | **789 dari 1.200 sampel** |
| Panggilan Four.meme Token Manager (`0x1de460f363af910f51726def188f9004276bf4bc`, selector `0x4d819a2a`) | **494** |
| Approval (`0x095ea7b3`) | **278** |
| Transfer token langsung (`0xa9059cbb`) | 8 |
| Transfer native polos | 5 |
| Token berbeda yang di-approve dalam jendela | **103** |
| Transaksi gagal (outgoing) | 0 |

**Venue utama sama persis dengan wallet dorman:** proxy Four.meme
`0x1de460f363af910f51726def188f9004276bf4bc` — 722 dari 1.200 panggilan
sampel penuh, dan 448 dari 453 approval mengarah ke proxy ini sebagai spender.
Pola aktivitas: beruntun (burst) — ada jam dengan 221 transaksi dalam satu jam
UTC (31 Okt 12:00 UTC) — konsisten dengan trader aktif yang memakai tool,
bukan perdagangan manual satu-per-satu.

**Kriteria "aktif baru-baru ini sebagai pedagang": LOLOS KUAT.**

## 4. Token yang paling banyak diperdagangkan (dari approval, bukan atribusi calldata)

Peringatan metodologi (diwarisi dari investigasi lama): atribusi token dari
posisi calldata panggilan proxy Four.meme TERBUKTI berisik — posisi yang sama
dapat berisi token quote/leg (mis. bStocks) — sehingga daftar ini memakai
target approval (`to` = kontrak token, spender = proxy), yang bersih:

| Token (approve `to`) | Approval dalam sampel |
|---|---|
| SA `0x94f952c2de8ef50aa2cefa5ce8df2f0fb5057777` | 13 |
| CTO `0xef8855e8d7451cd74050e2e26d7731ac5df87777` | 11 |
| BEPE `0x8cb6be67aaab6cdd9116fbd02f370cf494ca7777` | 10 |
| SNOWBALL `0x79b5d86089a29a65fac3278572f00c8fadc361fb` | 9 |
| ZERO `0xc8a0f114224df0ef7e425c4435e47717bea77777` | 9 |
| (237 token berbeda di-approve total dalam sampel) | 453 approval |

## 5. Saldo token saat ini: masih memegang bermakna di BANYAK token

`ankr_getAccountBalance` (MODULE): total $23.728,50 pada 252 aset.
Catatan batas: Ankr dapat melewatkan memecoin tanpa harga, jadi ini batas bawah.

| Aset | Saldo | Nilai |
|---|---|---|
| BNB | 23,136755 | $16.151,18 |
| FIST `0xc9882def23bc42d53895b8361d0b1edc7570bc6a` | 2.568,04 | $764,43 |
| 4444 `0x661af369690a8f5591cc0df7d581c83d1a6e4444` | 20.661.082,34 | $481,43 |
| BABAB `0x4ef9d3062c7f6eba4aae4990c5036598c6eff4ec` | 4,58 | $466,25 |
| ASTER `0x000ae314e2a2172a039b26378814c252734f556a` | 605,88 | $421,59 |
| ZKK `0x9f26d65b44438ec1a9ec85ea88737b04b31affff` | 1.084.365,97 | $416,34 |
| U `0xce24439f2d9c6a2289f741120fe202248b666666` | 350,12 | $350,04 |
| WISHDOG, 币安时代, KGST, AAPLB, ZEC, 脸谱, GMEB, TRX, TSLAB, SKHYB, NFLXB, EWYB, BNCB, … | masing-masing | $90–$267 |

Puluhan posisi di atas $100 — berlawanan total dengan wallet dorman (total
$11,96, 10 token teratas bersaldo 0).

**Kriteria "masih memegang bermakna di ≥1 token": LOLOS KUAT.**

## 6. Uji early-entry: 3 dari 5 token teruji terbukti lebih awal (LOLOS, tepat di ambang)

Metode: untuk tiap token, Transfer pertama token (via `ankr_getLogs` +
biseksi rentang blok — bukan `pool_created_at` GeckoTerminal, yang bisa lag
berjam-jam) dibandingkan dengan Transfer pertama yang diterima wallet
(pembelian). Selisih dalam blok; 1 jam ≈ 8.000 blok pada 0,45 dtk/blok.
"Lebih awal" = pembelian dalam hitungan menit setelah Transfer pertama token.

| Token | Transfer pertama token | Pembelian pertama wallet | Selisih | Early? |
|---|---|---|---|---|
| SA (Super-Agent) `0x94f952…` | blok 131.038.737, 2026-11-01 11:11 UTC | blok 131.038.841, 11:12 UTC | **104 blok (~1 menit)** | **YA** |
| CTO (Chief Troll Officer) `0xef8855…` | blok 131.002.014, 2026-11-01 06:35 UTC | blok 131.002.108, 06:36 UTC | **94 blok (~1 menit)** | **YA** |
| BEPE (Binance Pepe) `0x8cb6be…` | blok 131.229.059, 2026-11-02 10:59 UTC | blok 131.229.070, 10:59 UTC | **11 blok** | **YA** |
| SNOWBALL `0x79b5d860…` | blok 131.083.211, 2026-11-01 16:45 UTC | blok 131.191.363, 2026-11-02 06:16 UTC | 108.152 blok (~13,5 jam) | TIDAK |
| ZERO (ZerodriftAI) `0xc8a0f114…` | blok 89.967.903, 2026-04-01 09:13 UTC | blok 130.839.495, 2026-10-31 10:16 UTC | 40.871.592 blok (~7 bulan) | TIDAK |

Pembelian pertama SA/CTO/BEPE berasal dari proxy Four.meme/pair (pengirim
Transfer pertama: proxy `0x1de460…` untuk CTO dan BEPE; pair
`0xc3f72d14…` untuk SA) — yaitu pembelian pasar, bukan transfer dari wallet
sendiri. Tiga early-entry terverifikasi ini memenuhi syarat minimal 3.

**Kriteria "minimal 3 early-entry terverifikasi": LOLOS (tepat 3 dari 5 yang diuji tuntas).**

## 7. Uji exclusion bar (dump ≥80% dalam ±1 jam di ≥3 peluncuran)

Metode: dari log Transfer token (penerimaan vs pengiriman wallet, satuan raw
yang sama sehingga persentase valid tanpa desimal), dihitung kapan kumulatif
pengiriman mencapai 80% dari total penerimaan. "Pengiriman" = semua Transfer
keluar (termasuk transfer ke wallet lain, bukan hanya jual pasar) — jadi angka
ini mengukur exit, bukan semata-mata penjualan. Bar hanya menghitung token
yang dibeli SAAT peluncuran (early-entry); exit cepat pada token lama tidak
dihitung.

| Token | Early? | Total terjual dari yang diterima | 80% tercapai dalam | Hitung bar? |
|---|---|---|---|---|
| SA | YA | 100% (26 pengiriman, saldo kini 0) | **1,7 menit** (blok 131.039.070) | **YA — dump peluncuran** |
| CTO | YA | 87,0% (saldo kini 5.136.196,74 CTO) | **7,2 menit** (blok 131.003.064) | **YA — dump peluncuran** |
| BEPE | YA | 82,4% (saldo kini 8.298.110,59 BEPE) | 98,4 menit (blok 131.242.184) — di LUAR 1 jam | TIDAK |
| SNOWBALL | TIDAK | 74,4%, tidak pernah mencapai 80% | — | TIDAK |
| ZERO | TIDAK (token Apr 2026) | 100% dalam 6,4 menit — exit cepat, tapi BUKAN pada peluncuran | — | TIDAK |

**Hitungan bar peluncuran: 2 dari 3 yang disyaratkan → BAR TIDAK TERPICU, tetapi
sangat dekat.** BEPE lolos dari bar hanya dengan selisih 38 menit, dan hanya
5 token yang diuji tuntas dari 237 token yang di-approve — sapuan penuh bisa
saja menemukan dump peluncuran ke-3. Maka baris ini dinyatakan **"tidak terpicu
pada set uji, tidak terbukti bersih penuh"**, bukan "bersih".

**Peringatan pola (penting untuk pemakaian sinyal):** pada 2 dari 3
early-entry-nya, wallet ini keluar ≥80% dalam hitungan menit. Sinyal dari
wallet ini harus dibaca sebagai **entry cepat + exit cepat**, bukan sebagai
sinyal hold — persis pola yang mendiskualifikasi TRIO pada 2026-11-02, hanya
saja di sini hitungannya berhenti di 2, bukan 3.

## 8. Peta keterhubungan 1-hop

### 8a. Dormant 0xbd28… → main 0xbf00…: STRONG, dan KOREKSI atas laporan lama

Laporan lama mencatat "11 transaksi / 134,554299 BNB" dari wallet dorman ke
wallet ini — angka itu **terbatas sampel** (600 transaksi terbaru wallet
dorman saja). Pengecekan ulang histori PENUH wallet dorman di sini
(8.924 transaksi, paging selesai — tidak ada halaman berikut) menemukan:

- **38 transfer native dari `0xbd28…` ke `0xbf00…`, total 513,966196 BNB**,
  blok 47.542.789 (hash `0x44f03ead…`, 30 BNB) s/d 128.734.426
  (hash `0xedb916dc…`, 7,401979 BNB).
- Nilai awal cenderung bulat (30 / 48 / 35 / 20 / 13 BNB), nilai belakangan
  presisi (16,325924 / 21,422452 / 11,152950 BNB) — pola sapuan hasil.
- Koreksi ini MEMPERKUAT keterkaitan, dan kini diperkuat lagi oleh konfirmasi
  identitas OKX (§1): wallet dorman berlabel AFeng yang sama, dan wallet ini
  terkonfirmasi sebagai wallet utama AFeng. Pembacaan wajar: wallet dorman
  adalah wallet sampingan/lama yang memberi makan wallet utama — tetapi
  "operator sama" secara formal tetap diklasifikasikan **STRONG-transfer,
  bukan terbukti co-buy** (lihat §8b).

### 8b. Co-buy token meme: TIDAK DITEMUKAN

Token yang tumpang-tindih antara kedua wallet — BTCB `0x7130d2a1…`,
SPCXB `0xbe9d1568…`, QQQB `0x205812cd…`, SPYB `0x7138b48d…` — adalah
**token saham tokenisasi bStocks yang sudah mapan**, bukan meme baru, dan
muncul di panggilan proxy sebagai leg/quote swap. Bukti approval wallet utama
untuk keempatnya: masing-masing 0 / 1 / 1 / 0 dalam sampel 1.200 transaksi —
dapat diabaikan. Saldo kini wallet utama pada keempatnya hanya residu kecil
(±0,0005 BTCB; 0,177 SPCXB; 0,015 QQQB; 0,013 SPYB).
**Tidak ada satu pun meme peluncuran yang terbukti dibeli kedua wallet
bersama-sama dalam data yang diperiksa.** Transfer saja tidak cukup sebagai
bukti operator sama; co-buy tetap belum terbukti.

### 8c. Wallet terhubung lain yang muncul (transfer saja, belum diuji co-buy)

| Wallet | Bentuk | Bukti dalam sampel 1.200 tx wallet utama |
|---|---|---|
| `0x28ff6b5e8f08497a43601debcf2020920aee6150` | EOA, 8,6637 BNB, txcount 1.180 | Menerima 6 transfer token dari wallet utama; mengirim 1 transaksi masuk |
| `0xc4589d0dc9d8e4daa0026f956cb1e01ba9f52d34` | EOA, 9,9997 BNB, txcount 1.411 | Menerima 2 transfer token (termasuk FIST); mengirim 1 transaksi masuk |

Keduanya dicatat sebagai **terhubung-transfer, operator-sama tidak terbukti** —
bukan kandidat, dan tidak diuji co-buy dalam laporan ini.

### 8d. Wallet saudara lama 0x6ca69ed2…

**0 kemunculan** dalam sampel 1.200 transaksi wallet utama (sebagai pengirim
maupun penerima). Tidak ada hubungan langsung yang teramati antara wallet
utama dan wallet saudara wallet dorman itu dalam jendela ini.

## 9. Tabel kriteria (bar yang sama seperti investigasi lama)

| Kriteria "layak" | Hasil |
|---|---|
| Minimal 3 early-entry terverifikasi | **LOLOS — 3 dari 5 diuji (SA, CTO, BEPE, §6)** |
| Masih memegang bermakna di ≥1 token | **LOLOS KUAT — puluhan posisi >$100, teratas FIST $764 (§5)** |
| Bersih dari exclusion bar | **TIDAK TERPICU pada set uji (2 hit peluncuran < 3), TAPI tidak terbukti bersih penuh — hanya 5 token diuji tuntas; BEPE di luar bar hanya 38 menit (§7)** |
| Bukan exchange/kontrak/bot | **LOLOS BENTUK dengan catatan — EOA + delegasi 7702 ke implementasi akun 4337 standar, bukan exchange/executor; frekuensi (253.155 tx seumur hidup, ~480/hari dalam sampel, burst >200/jam) membuat bantuan otomasi tidak dapat dikesampingkan dari data on-chain saja (§2–§3)** |
| Aktif baru-baru ini (sebagai pedagang) | **LOLOS KUAT — 789 tx/48 jam, 494 panggilan dagang, 103 token, transaksi terbaru 01:12 WIB 3 Nov (§3)** |

## 10. Verdict: LAYAK ditambah — dengan tiga peringatan eksplisit

**Wallet dagang utama AFeng `0xbf004bff64725914ee36d03b87d6965b0ced4903`
LAYAK ditambah ke set pantau** (sebagai sumber sinyal/observasi — keputusan
penambahan dan bentuk pemakaiannya tetap di tangan parent/user; laporan ini
tidak mengubah set apa pun).

Alasan: identitas terkonfirmasi lewat OKX (badge X + 1.864 transaksi cocok
persis); 3 early-entry terverifikasi; pegangan bermakna luas; aktivitas
perdagangan intens dalam 48 jam terakhir; exclusion bar tidak terpicu.

**Peringatan yang harus ikut dalam keputusan:**

1. **Pola exit cepat (2/3 ambang bar):** pada 2 dari 3 early-entry-nya, wallet
   ini membuang ≥80% dalam hitungan menit (SA 1,7 menit; CTO 7,2 menit).
   Perlakukan panggilannya sebagai sinyal entry-cepat/exit-cepat, BUKAN
   sebagai sinyal hold. Jika sapuan penuh di kemudian hari menemukan dump
   peluncuran ke-3, verdict ini harus ditinjau ulang dan wallet
   didiskualifikasi seperti TRIO.
2. **Otomasi tidak dapat dikesampingkan:** frekuensi seumur hidup dan burst
   per jam berskala tool. Jika bar kelayakan user mensyaratkan pedagang
   manual murni, wallet ini perlu penilaian ulang — data on-chain saja tidak
   dapat memutuskannya.
3. **Wallet dorman `0xbd28…` tetap TIDAK LAYAK sebagai sinyal mandiri**
   (dorman, keluar penuh, 0 early-entry) — nilainya kini hanya sebagai bukti
   funding-link ke wallet utama (§8a), bukan sebagai kompas arah uang sendiri.

## 11. Batas & ketidakpastian (lengkap)

1. GMGN login-gated — tidak ada konfirmasi GMGN atas PnL/identitas; seluruh
   bukti identitas berasal dari jalur OKX (browser task) + verifikasi on-chain
   di sini.
2. Angka OKX (PnL, win rate, volume) berasal dari browser task 05:38 WIB dan
   tidak dibaca ulang oleh penulis laporan ini; hanya saldo BNB yang
   dikonfirmasi silang persis dengan pembacaan on-chain.
3. Sampel transaksi terbatas pada 1.200 terbaru (31 Okt–3 Nov); histori penuh
   253.155 transaksi tidak dipindai. Uji early-entry dan dump-bar hanya tuntas
   untuk 5 token — bukan sapuan penuh atas 237 token yang di-approve.
4. Matematika dump memakai Transfer keluar apa pun (termasuk transfer ke
   wallet lain), bukan hanya penjualan pasar — persentase adalah ukuran exit,
   dan arah pasarnya tidak dibedakan.
5. "Transfer pertama token" dipakai sebagai proksi peluncuran; untuk token
   yang mint awalnya tidak langsung diikuti perdagangan terbuka, selisih
   menit-ke-peluncuran bisa sedikit bergeser — tetapi selisih 11–104 blok
   untuk SA/CTO/BEPE tetap early menurut ukuran apa pun.
6. Saldo Ankr adalah batas bawah (dapat melewatkan memecoin tanpa harga);
   saldo token individual di §5–§7 dibaca ulang on-chain via `balanceOf`
   untuk token yang diuji.
7. Listing transaksi Ankr yang teramati stabil di seluruh panggilan laporan
   ini (transaksi terbaru blok 131.286.826, 01:12 WIB 3 Nov); bila ada
   transaksi lebih baru yang belum terindeks, aktivitas 48 jam hanya akan
   bertambah, bukan berkurang.
8. Keterkaitan transfer (§8) tidak membuktikan satu operator secara formal;
   klasifikasi mengikuti bukti: STRONG-transfer untuk `0xbd28…`, WEAK/
   transfer-saja untuk `0x28ff…` dan `0xc458…`, dan co-buy meme tidak
   ditemukan.
