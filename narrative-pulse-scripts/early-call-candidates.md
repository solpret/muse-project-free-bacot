# Kriteria "Early Call" — definisi pengumpulan (2026-10-31)

Tugas user 2026-10-31: kumpulkan dulu data on-chain wallet-wallet
yang memang harus ditandai sebagai "early call". File ini adalah
DEFINISI + DATASET MENTAH hasil pengumpulan — BUKAN daftar
watchlist final. Promosi ke wallet-watchlist tetap butuh syarat
di bawah terpenuhi dan diverifikasi ulang.

## Definisi "early call" (kandidat)

Sebuah wallet disebut kandidat early-call untuk satu token bila:
- Membeli token itu dalam 60 MENIT PERTAMA setelah pair
  tercipta / token graduate (bukan menerima via transfer gratis),
  DAN
- Pembelian itu terjadi SEBELUM lonjakan sosial pertama token
  tersebut (sebelum trending / seruan massal), DAN
- Wallet itu BUKAN deployer/creator token tersebut.

Sebuah wallet masuk dataset early-call bila memenuhi definisi di
atas pada MINIMAL 2 token berbeda (ambang awal pengumpulan).
Ambang promosi ke wallet-watchlist lebih ketat: minimal 3 token
+ PnL terealisasi 30 hari + verifikasi bulanan (lihat
wallet-watchlist.md).

## Data yang dikumpulkan per wallet per token

- Alamat wallet
- Token + CA (terverifikasi on-chain)
- Waktu pair tercipta / graduate + waktu beli pertama wallet
  (selisih menit)
- Besarnya pembelian pertama (BNB + USD saat itu)
- Market cap saat beli pertama + market cap puncak sesudahnya
- Status kini: masih hold / sudah jual (bila terbaca)
- Tag GMGN bila ada: smart money / KOL / sniper / fresh / bundler /
  insider / whale / dev (tag vendor = data sekunder, bukan vonis)

## Yang DICORET dari dataset (bukan early call)

- Wallet deployer/creator dan wallet yang hanya menerima transfer
  (airdrop/distribusi) tanpa membeli.
- Wallet bundle yang terkoroborasi sebagai satu klaster dengan
  deployer — dicatat terpisah sebagai klaster, bukan early call.
- Wallet yang membeli awal TAPI terbukti front-running seruan
  KOL-nya sendiri — masuk ledger KOL sebagai flagged, bukan
  early call.

## Token acuan pengumpulan pertama

- BIBIAI 0x415aac3e46264c046d103c994a1da71f05c547f9 (pair V2
  0x10c139638721bb8b40cfe6434acbbb5c295d0991)
- RIKI 0xa64E9dE168981Ebfd0b4A281FAf543B95f387777 (pair V2
  0x84c72fd6a89d4cfe6bb179b57c4eb78fc3bde3ee)
- JAGENT — CA dicari dulu lewat GMGN (belum diketahui); bila
  identitas tidak terverifikasi, JAGENT dicoret dari batch ini.

## Jalur data

- Utama: halaman token GMGN (holders, traders, first buyers, tag)
  dibaca lewat browser task — read-only, tanpa login, tanpa
  connect wallet, tanpa signing.
- GMGN Agent API resmi BUTUH API key (key pair + upload public
  key di gmgn.ai/ai) — belum ada; bila user ingin koleksi
  otomatis via API nanti, itu langkah terpisah yang butuh
  persetujuan + pembuatan key oleh user.
- Cadangan: BscScan token transfers/holders (bila GMGN buntu).

## Pemetaan klaster (wajib, prinsip user 2026-10-31)

Satu smart wallet = banyak alamat; "onchain never lies" berarti
setiap wallet harus didalami sampai klasternya. Untuk tiap wallet
di dataset, kumpulkan juga:
- Wallet pendana (pengisi gas/dana pertama) + wallet turunan yang
  didanai wallet ini + rekan transfer langsung.
- Co-buyer token yang sama dalam jendela yang sama.
- Peran dalam klaster: akumulasi / distribusi / umpan / belum
  diketahui — dan PnL dinilai di level klaster, bukan alamat
  tunggal. Alamat satelit fresh bukan wallet independen.
- Keterkaitan KUAT (pendanaan bersama / transfer langsung /
  berantai) vs LEMAH (hanya co-buy) — yang lemah dicatat sebagai
  "kemungkinan klaster", bukan fakta.
- On-chain membuktikan APA dan KAPAN, bukan NIAT — jangan tulis
  "terbukti insider" dari data on-chain saja.

## Dataset mentah

### Batch 1 — GMGN, dikumpulkan 2026-10-31 ~15:51-16:00 WIB (read-only)
BATASAN PENTING: GMGN hanya menampilkan alamat TERPOTONG
(mis. 0x78...7f4f) di tabel — alamat lengkap TIDAK tersedia dari
batch ini. Dataset ini berguna untuk analisis pola/klaster, TAPI
belum bisa dipakai sebagai watchlist (butuh alamat lengkap lewat
halaman wallet GMGN per alamat, atau API key GMGN). TIDAK ADA
wallet dari batch ini yang dipromosikan ke watchlist.

### BIBIAI 0x415aac3e46264c046d103c994a1da71f05c547f9
Pair V2 0x10c139638721bb8b40cfe6434acbbb5c295d0991. Pool
dibuat 2026-10-29 17:45:32 WIB; trade pertama 21:50:43 WIB
(sel 4 jam 5 menit). 14 wallet di bawah membeli dalam 10 detik
setelah trade pertama — kohort "first-trade", BUKAN <=60 menit
setelah pair tercipta (kriteria ketat tidak terpenuhi untuk
BIBIAI). Deployer 0xe7...3e23 dikecualikan. Tax GMGN: beli 1% /
jual 2% (konsisten dengan parameter kontrak: buy 1%, sell burn
1% + keep 1%). Semua 14 sudah jual habis. Tidak ada rantai
pendanaan internal; sebagian besar didanai via Binance hot wallet.
| Wallet | Beli USD | Realisasi | Tag | Sumber dana |
| 0x78...7f4f | $14,24 | +$51,4 (+298,9%) | Baru | 0xc7...31ab |
| 0x4c...2325 | $2.170 | -$250,3 (-10,9%) | Bundler, Suspicious, Paper hand | 0xb7...054e |
| 0xf5...0239 | $365 | +$186,4 (+48%) | Bundler, Paper hand | Binance hot wallet |
| 0x3b...ee28 | $9,86 | +$19 (+178,2%) | Paper hand | 0xc6...2a71 |
| 0x4e...a874 | $182,5 | +$787,2 (+358,9%) | — | Binance hot wallet |
| 0xec...b551 | $182,5 | +$719,7 (+331,5%) | — | Binance hot wallet |
| 0xaf...236c | $730 | +$380,2 (+48,5%) | Paper hand | Binance hot wallet |
| 0x6b...7e56 | $422,6 | +$46,19 (+10,3%) | Bundler, Paper hand | Binance |
| 0x17...5636 | $422,6 | +$350,9 (+20,8%) | Bundler, Suspicious, Paper hand | 0xf5...b115 |
| 0x81...e7cb | $422,6 | -$22,64 (-5,1%) | Bundler, Paper hand | 0x24...c964 |
| 0x2e...78ed | $146 | +$187,9 (+120,4%) | Paper hand | 0x27...8d71 |
| ll k | $197,9 | +$279,2 (+86,5%) | Suspicious, Paper hand | BA |
| 0x40...729a | $197,9 | +$146,2 (+68,3%) | Paper hand | BA |
| Tu | $4.020 | +$5.380 (+121,5%) | Bundler | 0xc7...eb8c |

### RIKI 0xa64E9dE168981Ebfd0b4A281FAf543B95f387777
Pair V2 0x84c72fd6a89d4cfe6bb179b57c4eb78fc3bde3ee. Token
dibuat 2026-10-28 21:37:59 WIB; trade pertama non-dev 21:38:00
(+1 detik). 15 wallet membeli dalam 5 detik — MEMENUHI kriteria
<=60 menit (baik dari pair tercipta maupun trade pertama).
Deployer 0xad...2ef2 dikecualikan. Semua sudah jual habis.
Tag dominan: Bundler + Sniper + Paper hand.
RANTAI PENDANAAN TERVERIFIKASI (temuan utama batch ini):
0x8e...b086 -> 0xa0...3baa -> 0xd9...d022 -> 0x61...565a ->
0x86...ff88. Keempat wallet dalam rantai ini bertag Bundler +
Sniper, membeli di detik ke-5, sudah jual habis = SATU OPERATOR
klaster bundler/sniper. Ini klaster untuk DI-FLAG (ekstraktif),
bukan kohort early-call tepercaya.
| Wallet | Beli USD | Realisasi | Tag | Sumber dana |
| 0x31...21ba | $36,63 | +$13,27 (+33,9%) | Sniper, Paper hand | 0x99...fcb5 |
| 0x64...5884 | $41,33 | +$22,17 (+50,6%) | Bundler, Sniper, Paper hand | 0xcd...2c8e |
| 0xb0...a86f | $168,5 | +$129,1 (+71,7%) | Bundler, Sniper, Paper hand | 0x66...d6bf |
| 0xec...ffeb | $79,8 | +$38,68 (+45,8%) | Sniper, Paper hand | 0xf5...b115 |
| 0xa8...05ed | $143,1 | +$83,51 (+55,2%) | Bundler, Sniper, Paper hand | doulfiee |
| Mmmmm | $73,28 | +$106,4 (+133,2%) | Bundler, Sniper, Paper hand | 0xdd...1852 |
| 0xcf...f97f | $48,92 | +$50,5 (+96,4%) | Baru, Bundler, Sniper, Paper hand | 0x7d...a8f1 |
| 0xf9...ff6d | $73,28 | +$85,63 (+107,2%) | Bundler, Sniper, Paper hand | 0xd6...aff4 |
| 0x86...ff88 | $358,7 | +$8,99 (+2,4%) | Bundler, Sniper, Paper hand | 0x61...565a (rantai) |
| 0xb3...728e | $355 | +$37,12 (+9,9%) | Bundler, Sniper, Paper hand | 0x77...b072 |
| 0xd9...d022 | $350,4 | +$20,56 (+5,6%) | Bundler, Sniper, Paper hand | 0xa0...3baa (rantai) |
| 0x58...ae90 | $253,9 | +$87,76 (+32%) | Sniper, Paper hand | WOJAK |
| 0xa0...3baa | $355,7 | +$47,58 (+12,6%) | Bundler, Sniper, Paper hand | 0x8e...b086 (rantai) |
| 0x02...f076 | $139 | +$47,85 (+32,5%) | Sniper, Paper hand | 0xc4...ed0a |
| 0x61...565a | $330,7 | +$23,26 (+6,7%) | Bundler, Sniper, Paper hand | 0xd9...d022 (rantai) |
Tautan lintas token (BELUM terverifikasi karena alamat
terpotong): 0xf5...b115 muncul sebagai sumber dana di BIBIAI
(mendanai 0x17...5636) dan di RIKI (mendanai 0xec...ffeb).
Bisa jadi wallet yang sama, tapi dari bentuk terpotong tidak
bisa dibuktikan — dicatat sebagai kemungkinan saja.

### JAGENT 0x8e6442663a4f8c50b6132c68d42a30e7dfe4ae15
Identitas terkonfirmasi di halaman GMGN (nama/simbol JAGENT).
CATATAN: alamat ini SAMA dengan token $JAGENT dari riset
jager.live sebelumnya (0x8e64...Ae15) — jadi JAGENT = token
Jager yang sudah pernah diteliti (mint share berbayar).
Pair V2 USDT 0xe6...0bea. Token + pool dibuat 2026-10-28
17:23:16 WIB; pembelian pertama 20:17:46 WIB (+174,5 menit).
TIDAK ADA wallet yang membeli dalam 60 menit pertama — JAGENT
menghasilkan NOL kandidat early-call. 15 wallet paling awal
(dibeli ~menit ke-175, semua sudah jual kecuali sebagian kecil
masih pegang) dicatat di laporan browser, tidak disalin penuh
ke sini karena di luar kriteria. Tag dominan: mencurigakan /
curang / bundler; tidak ada rantai pendanaan internal dari tabel.

### Kesimpulan batch 1
- NOL wallet dipromosikan ke watchlist. Alasan: alamat
  terpotong (tidak bisa dilacak), kohort didominasi
  bundler/sniper yang sudah jual habis, tidak ada wallet yang
  tampil sebagai pembeli di >=2 token (hanya satu kemungkinan
  tautan pendana lintas token, belum terverifikasi).
- Satu temuan klaster KUAT: rantai bundler/sniper RIKI (di atas)
  — masuk kategori flag, bukan early-call tepercaya.
- Pertanyaan metodologi terbuka: jangkar jendela 60 menit =
  pair tercipta (ketat; BIBIAI gagal) vs trade pertama
  (praktis; BIBIAI lolos sebagai kohort first-trade). Menunggu
  keputusan user bila ingin mengubah jangkar.

### Batch 2 — GMGN, dikumpulkan 2026-10-31 ~16:04-16:22 WIB (read-only)
Token: SIREN (kontrol) + 3 graduasi BSC terbaru. Nama yang
DI-SKIP sesuai aturan (identitas tak terverifikasi): MUBARAK
(ambigu, banyak token seidentik), GIGGLE (tidak ada hasil
nama/simbol persis umur <=7 hari), "4" (satu-satunya nama
persis berumur 395 hari), Binance Life/币安人生 (tidak ada
token nama persis umur <=7 hari dengan data pembeli terbaca).

#### SIREN — kontrol GAGAL (data awal terkunci login)
Halaman GMGN resolve (harga $0,0240, MC $24,05M, holder
92.414, V3). Catatan: pekerja melaporkan anomali string
kontrak dari brief, tapi alamat yang akhirnya dipakai dan
tampil valid sama dengan alamat SIREN yang diberikan — yang
material adalah batasannya: tab Early Buyers hanya menampilkan
kohort "11d" (~20 Okt 2026), BUKAN pembeli awal Februari 2025;
kohort awal tidak dapat diakses tanpa login (tidak diakali).
Kolom Sumber Dana semuanya "--". SIREN menyumbang NOL data
early-call. Pelajaran: token lama tidak bisa dijadikan kontrol
lewat web tanpa login; kontrol batch berikut harus token muda.

#### 咯咯 / "Cluck cluck" (Giggle Academy) 0x53e32932382fcc2ec3e921c3d6ba3598d0e57777
Pair V2 0xffc63f327c3e3080e2def90ed18954b9673128ab. Token
dibuat 2026-10-26 22:15:39; waktu pair TIDAK tampil; First Buy
hanya granularitas hari ("4d" ~27 Okt) — menit tak
terverifikasi, dicatat sebagai kohort hari peluncuran. DEV
0x92...035e dikecualikan. 15 pembeli paling awal, semua sudah
jual habis. Alamat lengkap 5 teratas via href (bukan tebakan):
0xacc3aad53b8b13759921c62cba7f52c9a36d7ac4 (beli $109,1,
+$46,08, funder 0xf5...b115),
0xd8b9199a1723fa70d8c11cb21913ce3ddaa142ef (beli $430,6,
-$59,81), 0x7f72a5f832e5f63a1616e2b72874cf2e31d2bb67 (beli
$19,02, -$38,3, jual > beli = buy-vs-transfer sebagian tak
terverifikasi), 0x6632c78efd535035f5492c8ae54e6f84a063c2d6
(beli $1.424, -$0,33), 0xf380e9dd74f26b5922ff81b7a9de6a9b8bdf564a
(beli $70,8, -$12,24). Klaster: funder 0xf5...b115 mendanai
#1; label bursa Binance H/W mendanai beberapa (bukan wallet
individu); klaster internal 幸运的马骝; tanpa rantai
multi-langkah.

#### HI / Hack Inu 0x1a700335ece5c42834d6dd1f74204eec8e194444
Pair V2 0xf4da82c411c1e2038abd4fb71eb6dd8835581fa6. Token
dibuat 2026-10-31 12:40:02; pool 14:02:47; First Buy
granularitas jam ("3h") — kohort jam peluncuran, menit tak
terverifikasi. DEV 0x94...b8fe dikecualikan (funder
0xf5...b115). 15 pembeli paling awal, semua sudah jual.
TEMUAN CROSS-BATCH TERKUAT: pembeli HI #1 = 0x86...ff88
(RIKI batch 1, full 0x86570adc943c6102088c0b27acd218895bf3ff88,
beli $138,6, -$6,82, funder 0x61...565a); pembeli HI #2 =
0xb3...728e (RIKI batch 1, full
0xb3466bfccf29e3babb61ca0f1b8984fde6ed728e, beli $135,5,
+$4,55). Pasangan funder->pembeli 0x61...565a -> 0x86...ff88
BERULANG PERSIS seperti rantai batch 1. Funder 0xf5...b115
mendanai HI #3 (Krishna, full
0xb65657592791652a2c50006615ae6d7ac64f59f7), #9, #33, DEV.
Klaster lain: shuaksn mendanai #6-#8 (durasi pegang sama 19
detik); klaster bundler #21-#23; funder berulang 0x31...89b8
(BUKAN 0x31...21ba — sufiks berbeda, jangan dicampur),
0xe2...775c, 0xf7...dbef.

#### MSX 0x23214ccbffb6ef479da64d1842b10b5525997777
Pair V2 0x03bfbc28960f93641729070a1a94fbcf7f3e365a. Token +
pool dibuat 2026-10-31 13:47:50; seluruh kohort "2h"
terverifikasi IN-WINDOW (0-33 menit setelah pair, batas jam).
DEV 0x9b...98f6 dikecualikan — MEMEGANG 83,29% ($321,4K),
tag Pembuat Token + Akun Sekunder + Top Holder + Paus +
Bundler + Sniper. 3 pembeli bertag "Akun Sekunder Pembuat
Token" + Bundler + Sniper (0x47...5598 full
0x47d4db5ae9567233e3fc426e775949bfe7205598; 0x03...433b
full 0x0301b15ef5771c21e7e6afa90c24083c5a84433b; 0xb5...ccbd
full 0xb5a5720c5423d84352b572a859810b67341fccbd) = klaster
INSIDER, bukan early-caller independen. Funder bersama
0x31...89b8 mendanai 0x93...1a52 dan 0x4e...1549 (+$301,2).
Pembeli BIBIAI batch 1 0x3b...ee28 muncul di baris 20 (di
luar 15 teratas, -$5,46) — possible repeat.

#### Cross-batch batch 1 <-> batch 2 (bentuk terpotong = POSSIBLE, bukan bukti)
- Funder 0xf5...b115: TERKONFIRMASI alamat lengkap
  0xf5988713400da6fc8a58ec9515e2b0df9b40b115. Mendanai
  pembeli di BIBIAI, RIKI, 咯咯 #1, HI #3/#9/#33/DEV.
  Ini HUB pendanaan lintas token yang paling konsisten.
- 0x86...ff88 dan 0xb3...728e (RIKI) muncul lagi sebagai
  pembeli paling awal HI, dengan alamat lengkap terkonfirmasi.
- 0x61...565a (rantai RIKI) mendanai lagi 0x86...ff88 di HI.
- 0xb0...a86f dan 0x31...21ba (RIKI) muncul di urutan default
  咯咯 (possible repeat).
- 0x3b...ee28 (BIBIAI) muncul di kohort MSX baris 20.
- BUKAN match (sufiks berbeda, dicatat pekerja agar tidak
  dicampur): 0x31...89b8 vs 0x31...21ba; 0xd9...b05d vs
  0xd9...d022; 0xf5...7b33 vs 0xf5...b115; 0x4e...14a1 vs
  0x4e...a874; dan sejenisnya.

#### Kesimpulan batch 2
- Klaster sniper/bundler RIKI TERBUKTI AKTIF LAGI hari ini
  (HI, 31 Okt): wallet yang sama, funder yang sama, pola
  yang sama (beli detik-menit awal, jual habis dalam
  hitungan menit, tag Paper hand). Ini klaster untuk
  DI-FLAG sebagai sinyal negatif, BUKAN untuk diikuti.
- Funder 0xf5988713400da6fc8a58ec9515e2b0df9b40b115 adalah
  hub lintas token — kandidat pertama untuk dipelajari
  lebih dalam (riwayat 30 hari + klaster turunannya),
  TAPI statusnya tetap "hub pendanaan", bukan "smart
  money terverifikasi": ia mendanai sniper, jadi nilainya
  sebagai sinyal justru terbalik (keramaian sniper).
- TIDAK ADA wallet akumulator (beli awal + hold + PnL 30
  hari) yang muncul di batch 1 maupun 2 — tabel early
  buyers GMGN secara sistematis menampilkan sniper duluan.
  Batch berikut harus memfilter ke pembeli awal yang HOLD,
  bukan sekadar pembeli pertama.
- Tetap NOL promosi ke watchlist dari batch 2. Alamat
  lengkap yang terkonfirmasi dicatat di atas untuk batch 3
  dan untuk pengukuran PnL 30 hari bila API key tersedia.

### Batch 3 — GMGN, dikumpulkan 2026-10-31 ~16:26-16:33 WIB (read-only)
FILTER BARU: hanya pembeli awal yang MASIH HOLD (holding
>0 material); jual habis, Bundler/Sniper/dev-secondary
dicoret; anggota klaster sniper batch 1-2 dicoret + di-flag
terpisah. Keterbatasan umum batch ini: waktu pembuatan pair
tidak terbaca di SI/COOL/ok; waktu trade pertama UNVERIFIED
di semua token; TIDAK ADA alamat lengkap dari href kali ini
(semua terpotong) sehingga TIDAK ADA confirmed repeat;
buy-vs-transfer unverified di semua baris.

#### MSX revisit 0x23214ccbffb6ef479da64d1842b10b5525997777
Keempat partial holder batch 2 MASIH HOLDING pada observasi
~16:27 WIB (kohort launch-hour "2h", menit UNVERIFIED):
- 0x52...708a: beli $98,78 @ $81,1K; jual $97,65; holding
  $238,4 (0,06%), sisa ~49,7%; unrealized +$188,3 (+376%);
  realized +$46,23; funder 0xc3...9859.
- 0xca...1ad8: beli $34,75 @ $58,7K; jual $126,3; holding
  $115,8 (0,03%), sisa 50%; unrealized +$98,21 (+556%);
  realized +$105,8; funder 0x82...bfda.
- 0xd3...8727: beli $20,85 @ $82,7K; jual $0; holding
  $98,75 (0,03%), sisa 100%; unrealized +$77,46 (+364%);
  funder 0x4e...6e11.
- 0x93...1a52: beli $34,75 @ $83,1K; jual $0; holding
  $163,9 (0,04%), sisa 100%; unrealized +$128,5 (+363%);
  funder 0x31...89b8.
Apakah mereka menjual lebih banyak sejak batch 2 TIDAK
DAPAT DITENTUKAN (tidak ada baseline batch 2 di sesi ini).
Tidak ada kecocokan klaster sniper di MSX. Catatan: MSX
tetap token insider-heavy (DEV 83,29%) — hold di sini
menarik tapi bukan bukti smart money.

#### SI / SAFU INU 0x2782c6e901126ba18a8c5c0caacf5a1563167777
Token dibuat 2026-10-30 18:59:55; pair time tidak terbaca.
Hasil: NOL kandidat holder. Semua pembeli kohort peluncuran
sudah jual habis. Dua wallet holding >0 (baris 33 $118,7;
baris 34 $125,2 bertag Bundler) first buy ~1 jam lalu,
BUKAN kohort peluncuran — dicoret. Eksklusi sniper: baris
59 (0x8d...3aa3), funder 0xf5...b115, sudah jual habis.
Funder 0x31...89b8 mendanai baris 10, 21, 25, 33, 34.

#### COOL / flap.cool 0x21aeddf21ee854f20cb497b0430437c4ab367777
Token dibuat 2026-10-31 12:22:05; pair time tidak terbaca.
Hasil: 1 kandidat holder — baris 50, 0xcc...4d0d: beli
$13,77 @ $14,1K; jual $20,64; holding $3,583 (0,03%), sisa
~32,4%; realized +$10,65 (+106,6%); unrealized -21,7%;
durasi hold ~4 jam; funder "Binance: H..."; tanpa tag
Bundler/Sniper; bukan klaster sniper. Semua baris 1-49
holding $0. Eksklusi sniper: baris 45 (0x26...a88a),
funder 0xf5...b115, sudah jual habis. Catatan keamanan:
klik kartu COOL sempat membuka flap.sh — GMGN sendiri
menampilkan peringatan flap.sh mungkin di-hack; tab
ditutup, semua data dari halaman GMGN, tidak ada
connect/sign.

#### ok 0xc853d8253f0d8346ca80f3f6af53e49a763e7777
Token dibuat 2026-10-31 10:46:55; pair time tidak terbaca;
seluruh 60 baris First Buy "5h" (kohort launch-hour/day,
menit UNVERIFIED). Hasil: 5 kandidat holder (batas 5,
semua terpotong saja, buy-vs-transfer unverified):
- Baris 37, 0x8e...b8d6: beli $4,131 @ $4,91K; jual $0;
  holding $8,246 (0,08%), sisa 100%; unrealized +94%;
  funder "Bitget 3".
- Baris 42, 0x43...f622: beli $75,72 @ $5,93K; jual $0/0 TX;
  holding $60,34 (0,61%), sisa 100%; unrealized +26,5%;
  realized +$632,9 TERCATAT APA ADANYA meski 0 TX jual
  (inkonsistensi tampilan); funder "Binance: W...".
  Bukan DEV (DEV = 0x43...48a4).
- Baris 43, 0x75...0488: beli $75,72 @ $5,35K; jual $683,5
  (JUAL > BELI — transfer masuk / pembelian tak tercatat,
  unverified); holding $38,43 (0,39%); realized +$419,9;
  unrealized -80,6%; funder tidak teramati.
- Baris 45, 0x60...0ee3: beli $75,72 @ $5,16K; jual $637,6
  (jual > beli, sama); holding $38,39 (0,39%); realized
  +$402; funder 0x78...bf63.
- Baris 46, 0xa9...165f: beli $75,72 @ $6,74K; jual $785,3
  (jual > beli); holding $67,85 (0,69%); realized +$582,4;
  funder "Cilzy" — CATATAN: Cilzy adalah wallet baris 41
  bertag Bundler; wallet ini sendiri tak bertag sehingga
  tetap kandidat sesuai huruf filter, dengan koneksi
  Bundler dicatat eksplisit.
Holder tambahan di luar batas 5: baris 47 ($67,42, funder
Cilzy), 48 ($67,23, funder 0x78...bf63), 49 ($69,3, funder
Binance W), 59 ($52,31, sisa ~30%, terakhir aktif 2h),
60 ($63,31, sisa ~31%, terakhir aktif 2h). Dicoret meski
holding >0: baris 40 (Bundler, $39,48), baris 41 (Cilzy,
Bundler, $60,97); baris 35 dust remnant ($0,835, sisa ~1%).
Eksklusi sniper: baris 21 (0xc7...3cbf) dan baris 51
(0xc2...77ad), keduanya funder 0xf5...b115, sudah jual
habis.

#### Cross-batch 3 + lintas batch
- Funder 0x31...89b8 muncul di KEEMPAT token batch 3 (MSX
  4 wallet, SI 5, COOL 1, ok baris 19) — POSSIBLE repeat
  (terpotong saja, bukan bukti). JANGAN dicampur dengan
  0x31...21ba batch 1 (sufiks berbeda).
- Funder "jsonfiko" muncul di MSX (baris 11) dan SI
  (baris 13) — POSSIBLE repeat.
- Eksklusi klaster sniper (funder hub 0xf5...b115) di
  batch 3: SI baris 59, COOL baris 45, ok baris 21 dan 51
  — semuanya sudah jual habis.
- Tidak ada kecocokan dengan 0x86...ff88, 0xb3...728e,
  atau 0x61...565a di batch 3.
- Klaster internal ok: Cilzy (Bundler, baris 41) mendanai
  baris 46 dan 47; funder 0x78...bf63 dipakai bersama
  baris 45 dan 48.

#### Kesimpulan batch 3
- TOTAL kandidat holder: 10 (MSX 4 + COOL 1 + ok 5); SI
  NOL. Ini kandidat holder PERTAMA yang lolos filter hold
  — tetapi tetap NOL promosi ke watchlist: ambang promosi
  (≥3 token + PnL 30 hari + re-verifikasi) belum terpenuhi
  siapa pun; kandidat tertua di batch ini baru berumur
  hitungan jam, bukan 30 hari.
- Kualitas data batch 3 lebih lemah dari batch 2 untuk
  ok (jual > beli, tampilan inkonsisten, alamat terpotong
  saja) — kandidat ok perlu verifikasi ulang sebelum
  dianggap serius; kandidat MSX (4 holder, data bersih)
  adalah yang terkuat sejauh ini, dengan catatan token
  MSX sendiri insider-heavy.
- Funder 0x31...89b8 adalah funder berulang baru yang
  paling konsisten di batch 3 — kandidat untuk dipelajari
  sebagai hub, BUKAN sebagai wallet yang diikuti.

### Batch 5 — GMGN, dikumpulkan 2026-10-31 ~16:45-17:02 WIB (read-only)
KOLEKSI LUAS atas instruksi user "kumpulkan sebanyak mungkin
wallet dari berbagai koin yang sedang ramai". BSC saja; token
dipilih LIVE dari GMGN BSC trending + graduasi baru; 10 token
batch 1-4 di-SKIP (BIBIAI, RIKI, JAGENT, SIREN, 咯咯, HI, MSX,
SI, COOL, ok). Per token DUA kohort: ~15 early buyers + ~15
holder material (deployer/pool/Bundler/Sniper dikecualikan dan
dicatat terpisah). TOTAL: 8 token, 211 baris wallet valid.
Keterbatasan umum: first trade UNVERIFIED di semua token;
waktu pair UNVERIFIED di WTB, 慈善天使, 币安AI PRO; menit
setelah pair UNVERIFIED di semua token (granularitas GMGN
hanya jam/hari, kecuali 狙姬 "1h" dan MSX-like bounds tidak
ada di batch ini); buy-vs-transfer unverified kecuali baris
dengan Total Pembelian $0 (transfer-in, dapat dibedakan);
hampir semua alamat hanya terpotong — bentuk terpotong =
POSSIBLE, bukan bukti. Tidak ada login/connect/sign.
Token ke-9 (旺财) dan ke-10 (HN / Hack Neko) terlihat di
Trenches tapi TIDAK dibuka karena keterbatasan waktu — bukan
diblokir, hanya tidak tercakup. Beberapa baris holder hilang
karena lompatan scroll tabel virtual (狙姬 peringkat 10-11,
共进 peringkat 10, GANG peringkat 8-14 tidak tertangkap penuh).

#### 1. 狙姬 / Sniper Girl 0x481f5963bf10cba972d52f138740155b2cda7059
URL GMGN: https://gmgn.ai/bsc/token/0x481f5963bf10cba972d52f138740155b2cda7059
Metadata ~16:47-16:49 WIB: MC $157,02K, liq $37K->$42,9K, vol
24h $282,8K->$346,3K, supply 1B, tax 0,25%/0,25%, holder
712->799, Top 10 15,39%, DEV 1%, Sniper 0,2%, Phishing 29,1%,
Bundler 9,3%, pool Pancake V2 95% dibakar. Token created
2026-10-31 15:14:16; pool created 2026-10-31 16:32:15; pair
0x04...8336. DEV 0x22...a27a (1,1 BNB), lengkap
0x222d44bf7c03c0f16a40047c820a2af3d4fca27a; funder DEV
0xfa...1001, lengkap 0xfaad602aa5a1149a775e276a872944a790b71001.
Early buyers (15, semua First Buy "1h"): 14 sudah jual habis;
SATU early+holder: 0x6a...476f — beli $35,82, hold $314
(0,2%), unreal +$306,8, funder 0x13...714e. Klaster dalam
token: funder 0x4a...8a3b (lengkap
0x4a258513cbd14b53cc8dbd98f2364f14f2128a3b) mendanai early
baris 1 dan 6. Holders (15 valid): terbesar 0x3c...edd6 $2,66K
(1,69%, funder 0xa9...635a 401d TF 0,528); 0xcb...b810 $1,67K
(tag suspicious, beli $0 transfer-in, funder Binance H 292d
TF 9,992 — LIHAT GANG: possible repeat); 0x27...6e9b $1,66K
(funder Bitget 3 41d TF 15,11 — LIHAT GANG: possible repeat).
Dikecualikan: pool ($16,7K); 0xa2...105d tag Bundler ($1,63K).

#### 2. 共进 / Join in 0x76219fbdc228a84ad19637ffbb6cdaa95a227777
Metadata ~16:50-16:52 WIB: MC $18,42K, liq $9,44K-$10K, vol
24h $52,9K->$53,8K, supply 1B, tax 3%/3% (panel Basic Data
tampil 2%/2%), holder 2.259-2.266, Top 10 13,78%, DEV 0%,
Phishing 16,3%, Bundler 11,7%. Token + pool created
2026-10-31 15:12:47; pair 0x76...7777. DEV 0xda...9494 (1 BNB),
lengkap 0xda45a79fec65b7eeb2d62c0df3282c29c5849494; funder
DEV 大豪 🔶 BNB = 0xab...0003, lengkap
0xabb9e7a54edf65c223724c5eb1c201d664750003.
Early buyers (15): DUA early+holder — 0xac...2cc8 hold $124,5
(0,68%), funder 0x54...fa09; 0x97...66d0 hold $100,3 (0,54%),
funder 0x82...425a. FLAG SNIPER (funder hub terkonfirmasi):
early 0x0d...07ab dan 0x2e...4423 — dikesampingkan. Funder
0x31...89b8 (lengkap dari href
0x318d2aae4c99c2e74f7b5949fa1c34df837789b8, 229d TF 0,12)
mendanai early baris 11 (0x15...6708, sold) — POSSIBLE
repeat funder batch 3 (bukan 0x31...21ba). Holders (14 valid):
terbesar 0x7e...3078 $423,7; satu early+holder tambahan baris
22 early: 0xbb...1d68 $155,6. FLAG SNIPER holder: 0x00...503e
$279,8 (funder hub terkonfirmasi) — dikesampingkan, LIHAT
WTB (repeat lintas token). Dikecualikan: Flap.sh LP pool
($7,4K); burn 0x00...dead ($157,7); 0x7a...6a5d Bundler ($153,6).
Catatan: holder 0x7b...717d funder 0xb3...398e — BUKAN
0xb3...728e, jangan dikacaukan.

#### 3. WTB / We Trust Binance 0x3b056facce631561be371e0bc14f07d826737777
Metadata ~16:53-16:54 WIB: MC $29,02K, liq $17,3K, vol 24h
$797,5K, supply 1B, tax 0,25%/1,25%, usia 23h, holder 1.357,
Top 10 23,22%, DEV 0%, Phishing 11,8%, Bundler 8,8%, pool
Pancake V2 95% dibakar. Token created 2026-10-30 17:01:02;
pool created UNVERIFIED; pair 0x1f...7336. DEV 0x0f...abb3
(21,1 BNB), lengkap 0x0f93496909e0f93424a9db8cfa141b1094c9abb3;
funder DEV 0x88...d4e3, lengkap
0x8894e0a0c962cb723c1976a4421c95949be2d4e3.
Early buyers (15): SATU early+holder — 金狗挖掘机 | 0xDav...
hold $110,7 (0,38%), funder Bitget 3. FLAG / KLASTER SNIPER
LAMA MUNCUL LAGI: 0x86...ff88 (beli $258,1, jual $501,7,
SOLD; funder 0x61...565a lengkap
0x612add8664aaacefbfa529633fefaf42dd16565a), 0xb3...728e
(beli $269,1, jual $571,6, SOLD; funder 0x77...b072),
0xd9...d022, 0xa0...3baa, 0x61...565a (beli $271, SOLD;
funder 0xd9...d022) — rantai terpotong
0x8e...b086 -> 0xa0...3baa -> 0xd9...d022 -> 0x61...565a ->
0x86...ff88 berulang persis seperti batch 1; semua SOLD di
WTB, jadi NOL dari mereka jadi kandidat holder. Bentuk
terpotong cocok dengan alamat lengkap batch 1-2, formal
POSSIBLE (alamat lengkap dompet WTB tidak tersedia).
FLAG SNIPER hub: early 烧鸭饭饭🍚 (funder hub terkonfirmasi).
Holders (15 valid): terbesar 0xfd...6413 $972,6. FLAG SNIPER
holder: 0xe9...9e33 $843,3 dan 0x00...503e $707,2 — keduanya
funder hub terkonfirmasi; 0x00...503e SAMA (terpotong+funder)
dengan holder 共进 — repeat lintas token, dikesampingkan.
Klaster dalam token: funder 0xf7...dbef mendanai holder #6
dan #7; holder #11 (0x0f...fce0) = funder holder #10.

#### 4. GANG 0x0c6302401aa5325c2e36f170f52c00b1d220b405
Metadata ~16:54 WIB: MC $3,50M, liq $252,3K->$253,2K, vol 24h
$1,4M, supply 999,4M, tax 0,25%/0,25%, usia 8d, holder
6.823-6.824, Top 10 14,54%, DEV 0%, Phishing 39,5%, pool
Pancake V2 95% dibakar. Token created 2026-10-22 00:20:53;
pool created 2026-10-22 16:57:27; pair 0x0b...0b6d. DEV
0x4e...19d3 (0,08 BNB); funder 0x63...5df4 (lengkap belum
diekstrak). Early buyers (15, semua First Buy "8d"): LIMA
early+holder — 0x87...69c6 hold $3,49K (0,1%),
0xf5...a3b7 hold $3,68K (0,11%, BUKAN sniper hub — jangan
dikacaukan), 0xb7...1c06 hold $3,74K (0,11%),
0x66...b4e1 hold $2,32K (0,07%), 0x27...6e9b hold $330,4
(kecil, funder Bitget 3 41d TF 15,11 — POSSIBLE repeat dari
holder 狙姬 #11, funder usia+TF identik). Klaster dalam
token: baris 12 (0x7f...647a) dan 14 (0x91...d7ec) saling
mendanai. Holders (15 valid): terbesar 0x6f...b72c $86,1K;
0xcb...b810 $31,1K (transfer-in, funder Binance H 292d TF
9,992 — POSSIBLE repeat dari holder 狙姬 #9, alamat+funder
usia+TF identik); 0x04...8199 $31,3K (funder --, LIHAT
Gangstar: possible repeat, lemah). Dikecualikan: pool
($126,1K); 0xb0...9c6f Bundler ($31,4K); burn ($25,6K).
Catatan: holder GANG #11 funder 0xa2...105d = Bundler yang
dikecualikan di 狙姬.

#### 5. Gangstar 0x6b2ce31a577d92f73516c7a91febc7672247e694
BERBEDA dari GANG token 4. Metadata ~16:55 WIB: MC $74,61K,
liq $27,7K, vol 24h $46,4K, supply 1B, tax 0,25%/0,25%, usia
4d, holder 898, Top 10 17,19%, DEV 0%, Phishing 27,8%,
Bundler 0,3%, pool Pancake V2 (pasangan Gangstar/GANG, bukan
BNB — dicatat apa adanya). Token created 2026-10-25
16:51:23; pool created 2026-10-27 12:16:52; pair
0xb6...3330. DEV 0x3c...dbfd (0,73 BNB); funder 0x3e...829c
(lengkap belum diekstrak). Early buyers (15, First Buy
6d/5d): SATU early+holder — 0x1a...9f12 hold $223,8 (0,3%).
Klaster dalam token: funder 0x0c...9600 mendanai early
baris 7 dan 8. Holders (15 valid): terbesar 0xec...21d9
$1,87K; TIGER $1,56K (funder 0xa9...635a 389d TF 3,709 —
POSSIBLE shared funder dengan holder 狙姬 #1, tapi TF
berbeda jauh 0,528 vs 3,709, jadi bukan CONFIRMED);
0x86...c7d2 BUKAN 0x86...ff88; 0xa9...0628 bukan 0xa9...635a
maupun 0xa9...165f. FLAG SNIPER holder: 0x4a...526d $1,29K
(funder hub terkonfirmasi) — dikesampingkan. Di luar cap:
0x04...8199 $801,8 (tag FOMO+suspicious, funder -- —
POSSIBLE repeat dari holder GANG #8, lemah).

#### 6. 慈善天使 / Charity Angel 0x872c29369d8446dda5916156403f6a7491847777
Metadata ~16:59-17:00 WIB: MC $25,50K, liq $14,5K-$14,6K, vol
24h $89,5K, supply 1B, tax 3,25%/3,25%, holder 2.304-2.306,
Top 10 15,3%, DEV 0,07%, Sniper 0,07%, Phishing 31,4%,
Bundler 2,4%, pool Pancake V2 95% dibakar. Token created
2026-10-30 03:13:06; pool created UNVERIFIED; pair
0x82...fddc. DEV 0xd9...a54d (0,01 BNB), lengkap
0xd9c03f53044bb1dc3b4d59622ce631ceb307a54d; funder DEV
0x01...5730, lengkap 0x01c12cea3f3a6ae4e93518e0cb7eb57f69ce5730.
Early buyers (15, semua First Buy "1d"): DUA early+holder —
0xe1...ff1f hold $223,2 (0,88%), funder 0xd5...bfb6;
0x5b...45ad hold $35,31 (0,14%), funder 0xf8...9d6b. FLAG
SNIPER: early 0x3e...206c (funder hub terkonfirmasi);
0xf3...1143 (terpotong cocok hub, href tidak diverifikasi —
POSSIBLE). Baris 21 di luar cap: 0x1d...8eb0, funder
0x31...89b8 (28d TF 0,05) — POSSIBLE repeat funder batch 3.
Holders (9 valid tertangkap, baris ke-9 terpotong):
terbesar 0xd4...12ce $1,35K (5,3%, funder 0xfe...2c80 —
LIHAT 币安AI PRO holder #2, funder sama). Dikecualikan:
pool Pancake V2 ($7,24K, 28,4%).

#### 7. 币安AI PRO / Binance AI PRO 0xe61aad11bf4282fd5a8c584baa4ff2c9c50c7777
Metadata ~17:00-17:01 WIB: MC $102,97K, liq $29K, vol 24h
$65,8K, supply 1B, tax 3,25%/3,25%, holder 13.257, Top 10
28,75%, DEV 0%, Sniper 0%, Phishing 60,6%, Bundler 0%, pool
Pancake V2 95% dibakar. Token created 2026-10-30 16:58:32;
pool created UNVERIFIED; pair 0xa6...2088. DEV 0x5d...bf48
(0 BNB), lengkap 0x5de0cb7101d0c7a841c3d4023c253a94dd35bf48;
funder DEV 0xb6...2320 (0,02, 79d). Early buyers (15):
TIGA early+holder — 0x1a...3255 hold $105,8 (0,1%),
0xbb...0fe0 hold $181,9 (0,18%), 0x0f...6387 hold $112,3
(0,11%). FLAG SNIPER: early 0x99...a1c0, 0xcc...2d75,
0x6f...218d — ketiganya funder hub terkonfirmasi.
Holders (8 valid tertangkap): terbesar 0x39...938e $19,8K
(19,32%, beli hanya $0,678 — anomali/transfer-in tak
terjelaskan, dicatat apa adanya); 0xd4...12ce $1,4K (funder
0xfe...2c80 — sama dengan holder 慈善天使 #1, klaster
dalam-dua-token lemah karena funder umum? dicatat sebagai
possible saja, bukan repeat wallet); funder 0x2e...1d25
mendanai holder #3 dan #6 (klaster dalam token).
Dikecualikan: pool ($14,5K, 14,09%).

#### 8. 币安社区 / Binance Community 0x0b35285fe783dd3441573b84be4fbdb743457777
Metadata ~17:01 WIB: MC $12,98K, liq $7,1K, vol 24h $45K,
supply 1B, tax 4%/4%, progres 31,70%, holder 5.225, Top 10
18,8%, DEV 0%, Sniper 0%, Phishing 4,3%, Bundler 0%, pool
95% dibakar. Token created 2026-10-30 19:35:43; pool created
2026-10-30 19:35:43; pair 0x0b...7777. DEV 0x23...3f2e
(0,01 BNB); funder 0x8a...0f23 (lengkap belum diekstrak).
Early buyers (7 tertangkap, semua First Buy "21h"): SATU
early+holder — 0xe2...f4ff hold $149 (1,15%), funder
0xfa...2e8e. FLAG SNIPER: 2 baris early buyer dengan funder
hub terkonfirmasi via href, detail baris tidak tertangkap
penuh karena keterbatasan waktu — dikesampingkan.
Holders (8 valid): terbesar 0x7c...b537 $362 (2,79%).
Dikecualikan: Flap.sh LP pool ($6,48K, 49,93%).

#### Cross-batch 5
- HUB SNIPER TERKONFIRMASI (alamat lengkap
  0xf5988713400da6fc8a58ec9515e2b0df9b40b115): mendanai
  12 dompet TERKONFIRMASI + 1 POSSIBLE di 6 dari 8 token
  batch 5 (共进 3, WTB 3, Gangstar 1, 慈善天使 1+1 possible,
  币安AI PRO 3, 币安社区 2) — semuanya dikesampingkan dari
  kandidat holder. Tidak ditemukan di 狙姬 dan GANG pada
  baris yang tercatat. Ini konfirmasi ke-5 kalinya hub ini
  muncul (batch 1, 2, 3, 5 + eksklusi batch 4).
- REPEAT DALAM BATCH 5 (2 token, semua POSSIBLE karena
  terpotong, NOL yang mencapai ambang 3 token):
  1. 0x00...503e — holder 共进 + holder WTB, keduanya
     funder hub terkonfirmasi — DIKESAMPINGKAN (sniper).
  2. 0xcb...b810 — holder 狙姬 ($1,67K) -> holder GANG
     ($31,1K); funder Binance H usia 292d + TF 9,992
     identik — POSSIBLE (kuat).
  3. 0x27...6e9b — holder 狙姬 ($1,66K) -> early buyer
     GANG (hold $330,4); funder Bitget 3 usia 41d + TF
     15,11 identik — POSSIBLE (kuat).
  4. 0x04...8199 — holder GANG ($31,3K) -> holder Gangstar
     ($801,8); funder -- di keduanya — POSSIBLE (lemah).
- KECOCOKAN VS BATCH SEBELUMNYA: buyer sniper 0x86...ff88
  dan 0xb3...728e muncul lagi sebagai early buyer WTB
  (keduanya SOLD — bukan kandidat holder); funder
  0x61...565a muncul lagi di WTB (funder + dompet, SOLD);
  funder 0x31...89b8 muncul lagi di 共进 dan 慈善天使
  (keduanya sold) — lengkap terkonfirmasi
  0x318d2aae4c99c2e74f7b5949fa1c34df837789b8 dari href
  共进, formal POSSIBLE vs identifier batch 3 yang hanya
  terpotong. 10 KANDIDAT HOLDER BATCH 3: NOL yang muncul
  kembali di 8 token batch 5 (0x52...708a, 0xca...1ad8,
  0xd3...8727, 0x93...1a52, 0xcc...4d0d, 0x8e...b8d6,
  0x43...f622, 0x75...0488, 0x60...0ee3, 0xa9...165f tidak
  ditemukan). Bentuk mirip tapi BERBEDA, jangan dikacaukan:
  0xa9...635a (funder) vs 0xa9...0628 vs 0xa9...165f;
  0x93...648f vs 0x93...1a52; 0xb3...398e vs 0xb3...728e;
  0x86...c7d2 vs 0x86...ff88; 0xf5...a3b7 vs 0xf5...b115.
- EARLY+HOLDER BARU BATCH 5 (satu token saja, dicatat di
  sini, TIDAK ditambahkan ke holder-watchlist karena
  watchlist itu khusus re-check 10 kandidat batch 3;
  penambahan butuh instruksi user): 狙姬 0x6a...476f;
  共进 0xac...2cc8, 0x97...66d0, 0xbb...1d68; WTB
  金狗挖掘机; GANG 0x87...69c6, 0xf5...a3b7, 0xb7...1c06,
  0x66...b4e1, 0x27...6e9b; Gangstar 0x1a...9f12; 慈善天使
  0xe1...ff1f, 0x5b...45ad; 币安AI PRO 0x1a...3255,
  0xbb...0fe0, 0x0f...6387; 币安社区 0xe2...f4ff.
  Semuanya 1/3 menuju ambang pola — belum notable (2+)
  kecuali 0x27...6e9b yang 2/3 lewat repeat di atas.

#### Kesimpulan batch 5
- Tetap NOL promosi ke watchlist. Alasan: tidak ada wallet
  yang mencapai ≥3 token + PnL 30 hari; repeat terkuat
  baru 2 token dan masih bentuk terpotong (POSSIBLE);
  menit setelah pair UNVERIFIED di semua token sehingga
  status "early" batch ini lebih lemah dari batch 2 (MSX)
  dan batch 3 (filter hold); holder batch 5 sebagian besar
  bukan early buyer (beli belakangan) sehingga kohort
  holder saja bukan bukti early-call.
- Temuan terbesar batch ini BUKAN smart money, melainkan
  konfirmasi ulang skala hub sniper: 12 dompet terkonfirmasi
  di 6 token dalam satu batch — hub ini adalah filter
  negatif paling konsisten sejauh ini, dan kemunculannya
  di token baru bisa dipakai sebagai sinyal "keramaian
  sniper" di screening berikutnya (bukan untuk diikuti).
- Klaster sniper lama RIKI (0x86...ff88 / 0xb3...728e /
  0x61...565a) TERBUKTI masih aktif di WTB (30 Okt) —
  pola beli ~$255-$271, jual 21 TX, durasi 3 menit di
  batch 1 berulang sebagai beli $258-$271 di WTB.
- Dataset batch 5 menutup koleksi luas tahap ini: total
  token tercakup batch 1-5 = 18 token (BIBIAI, RIKI,
  JAGENT, SIREN, 咯咯, HI, MSX, SI, COOL, ok + 8 batch 5).
  Langkah berikut yang masuk akal (butuh instruksi user):
  batch 6 untuk 旺财 + HN yang terlewat, atau re-check
  holder batch 5 setelah tenggang waktu, atau pendalaman
  klaster 0xcb...b810 / 0x27...6e9b (2 token) lewat
  halaman wallet GMGN per alamat untuk alamat lengkap.

## Batch 6 — 2026-10-31 ~17:35–17:43 WIB (GMGN read-only, 2 token terlewat batch 5)

Kedua token TERVERIFIKASI identitasnya live dari GMGN (BSC); tidak ada yang dilewati. Keduanya pool bonding PRA-GRADUASI (bukan PCS V2/V3). Menit-setelah-pair TIDAK TERVERIFIKASI untuk keduanya (granularitas GMGN hanya jam). Tidak ada login/connect/sign/pembelian. Tidak ada tab flap.sh dibuka.

### HN / Hack Neko — 0x2012e372d1661652a664655e5d5f318e7ae7ffff (Four.meme)
Token+pool created 2026-10-31 14:38:39 WIB. Progres bonding 23.00%. Harga $0.0₅475, MC $4.75K, liq $1.42K→$1.09K (drift), vol 24h ~$47.4K, tax beli 1% / jual 2%, Top 10 12.26%, DEV 0%, holders 55→52, Sniper/Insider/Phishing/Bundler 0% (metrik), pool burn 95%, Renounced, NoHoneypot, Open Source. DEV 0xad...2ef2 (2.6 BNB; funder 0xa1...d947). Pair column menampilkan 0x20...ffff = keanehan tampilan (potongan alamat token), bukan alamat pair independen.
- Early buyers (15 pertama): SEMUA sudah jual habis (pegang $0/0%). Termasuk DEV (anomali: pegang 0% meski jual $0 — transfer-out tak tercatat). Sniper-hub exclusion: 江湖鳮哥 (EB #5, hub via href). Funder 0x31...89b8 (penuh 0x318d2aae4c99c2e74f7b5949fa1c34df837789b8) mendanai EB #9/#11/#12. Baris #20 0xb9...25e3: jual >> beli = bukti transfer-in. Anomali PnL: Mmmmm beli $46.37 jual $47.04 tapi PnL real. -$23.01.
- Holders (material, ekskl. pool+deployer): 0x57...6830 ($90.34), 0xfd...88a5 ($76.01), 0x32...d403 ($60.78), 0x23...551b ($52.05; juga funder holder #3, alamat penuh 0x2325f175975abdbcde555c79cc8e63381d28551b), 0x43...0df2 ($50.74), 0xca...8833 ($33.75), 0x1f...9493 ($28.83), 0x09...ab90 ($27.44), 西瓜🔶BNB ($24.15 + $20.66, dua baris), 0x59...9e26 ($18.17), 0x23...2372 ($16.19), 0x3a...afd2 ($13.63), plus baris 18–27 ($12.57 ke bawah). Sniper-hub exclusions di holder: 0x7a...a9c9 (#2, via href), 0x06...482c (#11, truncated persis), 0x81...2fde (#22), 0x13...c71a (#24).
- HN menyumbang NOL kandidat early+holder (semua early buyer sudah keluar) — seperti SI di batch 3.

### 旺财 / Wangcai — 0x9d01d9ca91703b881dc0e585c6b746085b8f7777 (Flap)
Nama terverifikasi: 旺财 Fortune / Wangcai; dipilih dari pencarian yang cocok kartu Trenches (Tax 2%, FXION, Fortune, 15h, 0x9d...7777); token lain bernama sama dengan akhiran berbeda (0x55...7777, 0x74...7777, 0xcf...7777, 0x88...7777, 0xb4...ffff, dll.) TIDAK dipilih. Token+pool created 2026-10-31 01:58:19 WIB. Progres bonding 20.58%. Harga $0.0₅780, MC $7.80K, liq $3.93K, vol 24h $67.2K, tax beli 1% / jual 1%, Top 10 26.86%, DEV 0%, holders 62, Sniper/Insider 0%, Phishing 0.5%, Bundler 0% (metrik) — TAPI 3 early buyer bertag "Bundler" (Ochouso 🦈, 0x64...3180, 0xbb...8e6c): diskrepansi dicatat. Pool 旺财/FXION (58.78 FXIon). DEV 0xf2...ee2d (0.16 BNB; funder 0x7a...5151). Pair column 0x9d...7777 = keanehan tampilan yang sama.
- Early buyers (15 pertama): DEV 0xf2...ee2d (jual habis); sniper-hub exclusions: 0xcf...8f7c (#3, via href), 0xf3...1143 (#8, via href); Bundler exclusions: Ochouso 🦈 (#9), 0x64...3180 (#10). Masih hold dari 15 pertama: uv ($255.2, beli $118.2), 0xf3...7304 ($240, beli $118.2), 张五哥 ($8.878 sisa, beli $30.99), 0x8e...b8d6 ($6.646, beli $4.091, 100% — lihat cross-check). Baris notable di luar 15: #20 0xfa...d383 (FOMO, $792.7 beli), #22 0xbb...8e6c (Bundler — eksklusi), #23 0x50...2e07 (hold $175.3), #27 0x06...f3ce (hold $270), #35 0xf0...b105 (funder hub — eksklusi sbg pemegang), #41 0xa4...2333 (juga EB HN #2).
- Holders (material, ekskl. pool+deployer): 0x06...f3ce ($270), uv ($255.2), 0xf3...7304 ($240), 0xf7...2608 ($235.8), 0xca...9602 ($232), tuna ($193), 0x3d...d435 ($183.8), 0x50...2e07 ($175.3), 0x6c...1bd0 ($128.1), Ed_x區塊日記🇭🇰 ($120.8), 0xa0...c3fb ($112.5), 0xf3...73a5 ($90.85). Sniper-hub exclusions di holder: 0x20...e802 (#9, truncated persis), 0xf0...b105 (#14, via href). Tidak ada tag Bundler/Sniper pada baris holder.

### Batch 6 — baris early+holder baru (dicatat di sini SAJA, bukan holder-watchlist — file itu khusus re-check 10 kandidat batch 3)
Semua 1/3 kecuali yang ditandai: uv (旺财, $255.2), 0xf3...7304 (旺财, $240), 0x06...f3ce (旺财, $270), 0x50...2e07 (旺财, $175.3), 张五哥 (旺财, $8.878 sisa — plus trader di Aktivitas HN, kehadiran lintas token lemah, bukan EB HN terkonfirmasi), 0xa4...2333 (EB HN #2 + EB 旺财 #41 = 2/3 POSSIBLE, truncated saja), 0x8e...b8d6 (lihat cross-check: 2/3, alamat penuh terverifikasi).

### Batch 6 — cross-check
- Batch-3: SATU COCOK — 0x8e...b8d6 (EB 旺财 #13, penuh 0x8e966a9f17beab1ea50039434c2a14ad9e09b8d6 via href) = kandidat "ok" batch 3 → kini 2/3 (NOTABLE, ambang pola 3 belum tercapai; tetap di holder-watchlist sebagai kandidat, BUKAN promosi). 9 kandidat batch-3 lain: NOL kecocokan. Catatan bukan-kecocokan: 0x60...b5ea (funder 旺财 #48) ≠ 0x60...0ee3.
- Sniper hub 0xf5988713400da6fc8a58ec9515e2b0df9b40b115: 9 dompet dieksklusi (HN 5: EB #5, holder #2 via href, holder #11/#22/#24 truncated persis; 旺财 4: EB #3/#8 via href, holder #9 truncated persis, holder #14 via href). Ini penampilan hub di batch ke-6 (batch 1, 2, 3, 4-eksklusi, 5, 6) — filter negatif paling konsisten sejauh ini.
- Klaster RIKI: NOL kecocokan (0x86...ff88, 0xb3...728e tidak terlihat; funder 0x61...8517 di 旺财 #28 ≠ 0x61...565a).
- Repeat batch-5 0xcb...b810 dan 0x27...6e9b: TIDAK terlihat di kedua token (0x27...8353 di aktivitas 旺财 ≠ 0x27...6e9b).
- Total token tercakup batch 1–6: 20 token. Promosi: NOL.
