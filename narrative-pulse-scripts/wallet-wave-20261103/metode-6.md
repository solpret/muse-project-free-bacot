# Wallet-Discovery Wave 2026-11-03 — Metode 6 (LAPORAN AKHIR)

**Status: SELESAI. READ-ONLY. Tidak ada transaksi, signing, approval, konek wallet,
login, layanan berbayar, atau perubahan file feed/tier-ab/cron.**
**Periode kerja: 2026-11-03 ~17:01–17:30 WIB. Ini metode TERAKHIR gelombang; shortlist
akhir ditulis parent, bukan di sini.**

---

## ⚠️ PEMISAH TIER — BACA DULU

**Free-NFT early minting BUKAN smart money memecoin.** Semua hasil metode 6 di sini
masuk tier TERPISAH untuk sinyal early Free Bacot saja. **Tidak satu pun wallet
metode 6 diusulkan untuk feed Modal Bacot**, dan tidak satu pun dicampur ke verdict
screening memecoin. Satu-satunya wallet yang sudah punya status di set lain
(future1001.ai, Tier C) TIDAK berubah statusnya lewat laporan ini.

---

## Ringkasan eksekutif

- **Kaki tracked-set (lengkap, 8 run scan): HANYA future1001.ai** yang punya temuan
  free-mint — 54 kontrak / 58 mint di semua run 1–8. 54 wallet tracked lainnya NOL
  mint di jendela scan. future1001 adalah satu-satunya wallet konsisten-early yang
  terkonfirmasi di set tracked — dan ia SUDAH Tier C sejak 2026-11-03 ~08:47 WIB,
  jadi tidak ada penambahan baru dari kaki ini.
- **Kaki sampel on-chain (8 kontrak, first-100 mint): 255 minter berbeda; 72 dengan
  breadth ≥3; 29 dengan breadth ≥5 (2 di antaranya breadth 6).** Semua 31 wallet
  yang disaring mendalam adalah EOA dan aktif 30 hari, dan NOL yang overlap dengan
  set mana pun yang sudah ada (feed 6, tier-ab 54, Tier C, m1 33, TRIO/PAIR/T7,
  kuartet/hub/provisioner).
- **Temuan klaster: 5 wallet breadth-5 terhubung oleh pendanaan yang sama persis**
  (triplet 0,1 + 0,0206 + 0,0001 BNB yang identik di 3 wallet, ditambah 1 wallet
  ke-4 yang didanai 2 funder yang sama) → dihitung sebagai SATU entitas, ditandai
  terkoordinasi, BUKAN 5 suara independen.
- **Identitas agen TIDAK terverifikasi untuk wallet sampel:** `handleOf` registry
  mengembalikan string kosong bahkan untuk kontrol future1001 dan masgayut, jadi
  metode itu tidak valid untuk membuktikan/membantah status .ai. Wallet sampel
  dicatat sebagai "early minter konsisten", BUKAN "wallet agen terverifikasi".
- **Vonis tier-terpisah: 0 usulan feed; 1 konfirmasi (future1001, sudah Tier C);
  29 wallet sampel = WATCHLIST tier-terpisah** menunggu verifikasi funder penuh;
  klaster 5 wallet = 1 entitas yang ditandai. **Tidak ada yang ditambahkan ke set
  mana pun.**

---

## 1. Sumber yang diperiksa

### 1a. Kaki tracked-set — state scan run 1–8 (lengkap)

Sumber: `tracked-wallet-mint-scan-state.json` (`reported_findings`, 8 run).
Hasil: **1 wallet dengan temuan, 54 wallet tanpa temuan.**

| Wallet | Label | Kontrak | Mint |
| --- | --- | --- | --- |
| `0x355ea9e542b36c645a2dee63b9df079ccb9df3db` | future1001.ai (Tier C) | 54 | 58 |

Semua 58 mint bernilai 0 BNB (gratis, gas dikecualikan). Tidak ada wallet tracked
lain yang tercatat mint satu pun di jendela run 1–8 — ini hasil lengkap, bukan
sampel. Nuansa penting: future1001 TIDAK muncul di first-100 minter 8 kontrak
sampel §1b — breadth-nya terbukti lewat banyak proyek sepanjang waktu, bukan lewat
posisi first-100 di drop-drop spesifik itu. Contoh: mint AZET-nya bernomor token
#2637, bukan nomor awal.

### 1b. Kaki sampel on-chain — first-100 minter 8 kontrak free-mint terbaru

Metode: untuk tiap kontrak, `ankr_getLogs` address-filtered dengan topics
[Transfer, from=0x0] di jendela [anchor, anchor+4000 blok], diambil 100 mint
pertama kronologis (Ankr newest-first diatasi dengan jendela 200 blok berurutan
+ split saat cap 1000). Anchor = `firstMintBlock` eksak bila ada, sonst
`firstSeenBlock` snapshot (lower bound peluncuran — mint pertama sejati bisa
mendahului jendela; definisi "early" di sini = 100 mint pertama di/after anchor,
dinyatakan apa adanya).

| Kontrak | Anchor | Jenis anchor | Mint terkumpul | Minter berbeda | Blok mint pertama–terakhir |
| --- | --- | --- | --- | --- | --- |
| Auditrix `0x13eEa6a9…` | 131393366 | firstMintBlock eksak | 34 | 31 | 131393366–131396802 |
| Synaptik `0xE5523bf6…` | 131359859 | firstSeenBlock | 82 | 82 | 131359859–131363781 |
| Robogent `0x5eA7E757…` | 131375872 | firstSeenBlock | 100 | 69 | 131375872–131377666 |
| Yydsgent `0x38CB2dF1…` | 131382200 | firstSeenBlock | 100 | 85 | 131382200–131384932 |
| Deepvane `0xDd682169…` | 131361211 | firstSeenBlock | 100 | 95 | 131361211–131364614 |
| Animora `0x150699b4…` | 131351277 | firstSeenBlock | 100 | 92 | 131351277–131354952 |
| Sentrix `0xb7dce041…` | 131342312 | firstSeenBlock | 89 | 89 | 131342312–131346252 |
| Emberforge `0x6C90D230…` | 131258343 | firstMintBlock eksak | 20 | 1 | 131258343 (satu blok) |

**Artefak Emberforge:** ke-20 mint di jendelanya berasal dari SATU alamat,
`0x72b9050747bc33d6fef0d76d49b0c7840da47e3b`, yaitu OWNER proyek (tercatat di
laporan early lead Emberforge). Itu mint owner, bukan early minter — Emberforge
menyumbang 0 minter agen ke tally dan dikeluarkan dari hitungan breadth (tidak
ada wallet lain yang mint Emberforge di jendela itu; shape PoW-nya memang lambat).

Total: **625 mint terkumpul, 255 minter berbeda.** Distribusi breadth (jumlah
kontrak sampel tempat wallet muncul di first-100): 1 kontrak: 119 wallet;
2: 64; 3: 22; 4: 21; 5: 27; 6: 2. Daftar breadth lengkap: `m6_breadth.json`;
data mentah: `m6_early.json`.

Catatan kegagalan metode yang dicatat, bukan disembunyikan: `fast_rpc.race`
eth_getLogs gagal di semua endpoint (OSError) dan `bsc-dataseed` langsung
menolak range 400–2000 blok dengan -32005 "limit exceeded" — kaki ini hanya
jalan lewat modul Ankr. Tidak ada data yang diisi dari kegagalan itu.

### 1c. Kaki Boltbook — halaman depan + profil (read-only, curl)

- **Halaman depan EN terbaca penuh:** 25 penulis post terbaru (mayoritas board
  `alpha` + `launch` memecoin, BUKAN receipt mint) — direkam di `m6_authors.json`.
- **Resolusi nama→wallet TERVERIFIKASI 100% (25/25):** `ownerOfHandle(string)`
  registry `0x60B926…` dengan handle TANPA ".ai", lowercase — kontrol
  future1001 → `0x355e…`, masgayut → `0xeb23…`, keduanya persis. Jadi jalur
  Boltbook→wallet secara teknis jalan.
- **Halaman depan ZH: ekstraksi penulis GAGAL** (markup berbeda, hanya 1 atribusi
  tertangkap) — dicatat sebagai gagal baca parsial, bukan bukti tidak ada post.
- **Profil future1001.ai terbaca:** alamat wallet tercetak di profil
  (`0x355e…`, cocok dengan kontrol), bio: "watches Binance Agent ID launches,
  mints runestones, trades on BSC" — TAPI 0 post, 5 komentar (kolaborasi Runes).
  Jadi Boltbook mengonfirmasi identitas/bio agen yang sudah dikenal, namun TIDAK
  menghasilkan wallet konsisten-early baru: tidak ada tabel breadth receipt-post
  yang bisa dibangun dari halaman depan (post-nya alpha/launch, bukan receipt
  mint), dan histori post future1001 sendiri kosong.
- Profil penulis EN (25 nama) TIDAK dicocokkan satu per satu ke histori post —
  di luar nilai tambah setelah kaki on-chain memberi tally langsung; irisan
  penulis EN vs tally minter = 0 (tidak ada penulis halaman depan yang muncul
  di first-100 sampel — wajar, karena mereka poster alpha/launch, bukan minter
  drop NFT).

### 1d. Metode yang TIDAK dipakai

- GMGN: login-gated, dilewati, tidak ada login dicoba.
- `handleOf(address)` registry: MENGEMBALIKAN STRING KOSONG untuk kontrol
  future1001 DAN masgayut → metode tidak valid untuk reverse lookup; status .ai
  wallet sampel dinyatakan UNVERIFIED, bukan "bukan agen".
- Perpanjangan sampel ke kohort kontrak baru: tidak dilakukan (perluasan scope,
  keputusan parent/user — preseden metode 5).

---

## 2. Penyaringan 31 wallet (breadth ≥5 + 2 heavy minter)

Filter yang dipakai (adaptasi tier-terpisah): (a) operator independen — HANYA
parsial (data funder halaman-1, lihat §3); (b) aktif 30 hari; (g) bukan
exchange/kontrak (eth_getCode). Profit terealisasi (d) TIDAK diverifikasi dan
TIDAK berlaku sama untuk tier ini (mint NFT gratis; tidak ada klaim profit
memecoin). (c) diartikan sebagai breadth early-mint ≥5 kontrak sampel.
(e)/(f) tidak dijalankan per wallet karena tidak ada subjek yang lolos ke
keputusan feed — dicatat sebagai tidak dijalankan, bukan lolos.

Aktivitas 30 hari: jendela blok [125654500, 131414500] (latest saat screening),
`ankr_getTransactionsByAddress` halaman-1 (1000 tx). "cap" = halaman-1 penuh,
angka adalah batas bawah.

### Breadth 6 (2 wallet)
| `0x7136abde1976fb04612e710658be5c657a24d7a1` | 6 | Animora, Auditrix, Deepvane, Robogent, Synaptik, Yydsgent | EOA | 1000 (cap) |
| `0x8de95fbd489b57f2efead2bc1a5220e04d4f0584` | 6 | Animora, Deepvane, Robogent, Sentrix, Synaptik, Yydsgent | EOA | 169 |

### Breadth 5 (27 wallet)
| `0x09a872ac07c19f81d52475e1042778221b29eaa9` | 5 | Auditrix, Deepvane, Robogent, Synaptik, Yydsgent | EOA | 1000 (cap) |
| `0x0a20797e4b059ed4171f4aba49daf8ecea86e240` | 5 | Animora, Deepvane, Robogent, Synaptik, Yydsgent | EOA | 1000 (cap) |
| `0x1e1841599384d8b0d96d8cdb2184d2f36dbd0558` | 5 | Animora, Deepvane, Robogent, Synaptik, Yydsgent | EOA | 328 |
| `0x28fad1df6485aadce7f81c08c9db440fb99da09e` | 5 | Animora, Deepvane, Robogent, Sentrix, Synaptik | EOA | 1000 (cap) |
| `0x2d4f0cd7f4cb32e6813eb290d20455e15fc7b953` | 5 | Animora, Deepvane, Robogent, Synaptik, Yydsgent | EOA | 1000 (cap) |
| `0x3130313d23e4ceb53e111dfb65d568ada79b3f00` | 5 | Animora, Deepvane, Robogent, Synaptik, Yydsgent | EOA | 150 |
| `0x3ace3160faa4aa2cf4bd920097a13d9ae26609f3` | 5 | Animora, Deepvane, Robogent, Synaptik, Yydsgent | EOA | 1000 (cap) |
| `0x434368fd4151f9203dc4ce5a427ddcc44c5b84cc` | 5 | Auditrix, Deepvane, Robogent, Synaptik, Yydsgent | EOA | 1000 (cap) |
| `0x730d1c42469084210443188c56ab9d586becb4ea` | 5 | Auditrix, Deepvane, Robogent, Synaptik, Yydsgent | EOA | 1000 (cap) |
| `0x73c9eb9672d0afabe4d592501b4b98a6d341302e` | 5 | Animora, Deepvane, Robogent, Sentrix, Synaptik | EOA | 1000 (cap) |
| `0x7e81ef37b2a16657a67fb29493d4f219e775d74c` | 5 | Animora, Deepvane, Robogent, Synaptik, Yydsgent | EOA | 163 |
| `0xa0ba13c28212a47d6fb41de951ca6d9941938286` | 5 | Animora, Deepvane, Robogent, Sentrix, Synaptik | EOA | 1000 (cap) |
| `0xa20fb499dee4815d43665202f6729c69477ecc91` | 5 | Animora, Deepvane, Robogent, Synaptik, Yydsgent | EOA | 1000 (cap) |
| `0xa974e1ea5ffb85eddaa81eb33bfec2e3396e1330` | 5 | Animora, Deepvane, Robogent, Synaptik, Yydsgent | EOA | 1000 (cap) |
| `0xb322d9acb2d393e33d728a95d9d33af3761c78e6` | 5 | Animora, Deepvane, Robogent, Synaptik, Yydsgent | EOA | 1000 (cap) |
| `0xb76ca08681e3b68ba578f838e0819a483be0a386` | 5 | Animora, Deepvane, Robogent, Sentrix, Synaptik | EOA | 1000 (cap) |
| `0xbe2aff3c77e5947908d50f9db5024a57d5cac20a` | 5 | Auditrix, Deepvane, Robogent, Synaptik, Yydsgent | EOA | 1000 (cap) |
| `0xc54e30053bc5f95d323b4013ccdf579c448eff4b` | 5 | Animora, Deepvane, Robogent, Sentrix, Synaptik | EOA | 1000 (cap) |
| `0xc855c1bf0b2a7b75112c2f60787757ce82846a3a` | 5 | Animora, Deepvane, Robogent, Synaptik, Yydsgent | EOA | 1000 (cap) |
| `0xce34b5257b6e2174a1e1ca219d0c0f3175e6532f` | 5 | Animora, Deepvane, Robogent, Synaptik, Yydsgent | EOA | 150 |
| `0xd833762dddf4cb3d608810dfda5846665b282ff3` | 5 | Animora, Deepvane, Robogent, Synaptik, Yydsgent | EOA | 1000 (cap) |
| `0xdb5d735ca8f5285d8c28d51a71c8bec05b222fc3` | 5 | Animora, Deepvane, Robogent, Synaptik, Yydsgent | EOA | 1000 (cap) |
| `0xdbe747d877f81661ead1ca440d636a99bbce837f` | 5 | Auditrix, Deepvane, Robogent, Synaptik, Yydsgent | EOA | 1000 (cap) |
| `0xe6fb57b0459b9ba51cc6f46a08acabaab5ee5476` | 5 | Animora, Deepvane, Robogent, Synaptik, Yydsgent | EOA | 1000 (cap) |
| `0xf008eddbfc6871a2b82d5b2bd50164de7dba7c98` | 5 | Animora, Deepvane, Robogent, Synaptik, Yydsgent | EOA | 1000 (cap) |
| `0xfc1f7ccf5541e3bb4d18bc4ce39c12fffbf19340` | 5 | Animora, Deepvane, Robogent, Sentrix, Synaptik | EOA | 1000 (cap) |
| `0xfcc6573084a4e059cec1ca47a7b7ecd3d998b81c` | 5 | Animora, Deepvane, Robogent, Synaptik, Yydsgent | EOA | 147 |


Dua heavy minter tambahan yang disaring (bukan breadth ≥5, tapi volume mint
mencolok di sampel):

| Wallet | Breadth | Total early mint di sampel | EOA | Tx 30 hari |
| --- | --- | --- | --- | --- |
| `0x9ea96d42cdcb4fc5c8ded51f3a711a996679b95e` | 3 (Auditrix, Robogent, Yydsgent) | 16 | EOA | 1000 (cap) |
| `0x075c1bed7dcca884dd990737b6df734b651c1c65` | 2 (Animora, Deepvane) | 15 | EOA | 275 |

**Hasil saringan: 31/31 EOA; 31/31 aktif 30 hari; 0/31 overlap dengan set mana
pun** (feed 6, tier-ab 54, Tier C, m1 33, TRIO/PAIR/T7, kuartet/hub/provisioner).
Data saringan: `m6_screen.json`. Breadth 4 (21 wallet) dan breadth 3 (22 wallet)
TIDAK disaring per wallet — hanya dihitung di distribusi; mereka bukan subjek
keputusan laporan ini.

---

## 3. Temuan klaster: 5 wallet = 1 entitas (bukan 5 suara)

Tiga wallet breadth-5 memiliki funders native 30-hari yang IDENTIK PERSIS
(ketiganya uncapped — histori 30 hari penuh terlihat, jadi ini bukan artefak
sampling halaman-1):

| Wallet | Funder 1 | Funder 2 | Funder 3 |
| --- | --- | --- | --- |
| `0x3130313d23e4ceb53e111dfb65d568ada79b3f00` | `0xe6fb57b0…` 0,1 BNB | `0xc551851c…` 0,0206 BNB | `0xdb9c6383…` 0,0001 BNB |
| `0xce34b5257b6e2174a1e1ca219d0c0f3175e6532f` | `0xe6fb57b0…` 0,1 BNB | `0xc551851c…` 0,0206 BNB | `0xdb9c6383…` 0,0001 BNB |
| `0xfcc6573084a4e059cec1ca47a7b7ecd3d998b81c` | `0xe6fb57b0…` 0,1 BNB | `0xc551851c…` 0,0206 BNB | `0xdb9c6383…` 0,0001 BNB |

Dua wallet breadth-5 lain terhubung ke keluarga funder yang sama:

- `0x7e81ef37b2a16657a67fb29493d4f219e775d74c` didanai `0xe6fb57b0…` 0,1 BNB
  DAN `0xdb9c6383…` 0,141 BNB (3 tx).
- `0xe6fb57b0459b9ba51cc6f46a08acabaab5ee5476` sendiri breadth-5 — ia adalah
  funder, bukan hanya minter.

**Kesimpulan: 5 wallet ini = 1 keluarga funding → hitung SEKALI, ditandai
terkoordinasi.** Ini preseden yang sama dengan xigua (metode 4) dan kuartet
(metode 1): funding script yang sama = satu operator, bukan 5 agen independen.
Yang TIDAK diklaim: kemiripan prefix `0xce34…` pada 2 funder dust e6fb57
(dicatat saja — prefix + dust saja bukan bukti). Yang juga TIDAK diklaim:
independensi wallet breadth-5/6 lainnya — data funder mereka hanya halaman-1
(banyak yang capped di 1000 tx) dan sebagian besar hanya dust (nilai tampil
0,0 setelah pembulatan 4 desimal) — dust ping BUKAN bukti klaster (pelajaran
metode 4), dan absennya funder bersama di halaman-1 BUKAN bukti independen.
Verifikasi funder penuh (histori lengkap + first-funder) masih terbuka untuk
watchlist ini.

---

## 4. Daftar proposal (tier-terpisah)

**KOSONG untuk feed Modal Bacot — sesuai aturan tier.**

- **Dikonfirmasi, tanpa perubahan status:** future1001.ai
  (`0x355ea9e542b36c645a2dee63b9df079ccb9df3db`) — konsisten-early
  terkonfirmasi lewat kaki tracked-set (54 kontrak / 58 mint, run 1–8). Sudah
  Tier C sejak 2026-11-03 ~08:47 WIB. Laporan ini tidak menambah, tidak
  mengubah, dan tidak mengusulkan promosi apa pun untuknya.
- **WATCHLIST tier-terpisah (sinyal early Free Bacot saja, bukan referensi
  memecoin):** 29 wallet breadth ≥5 di §2, DIKURANGI klaster §3 yang dihitung
  sekali → 25 entitas watchlist (29 wallet − 4 duplikasi klaster). Status:
  EOA + aktif 30 hari terverifikasi; operator independen BELUM terverifikasi
  penuh; status .ai UNVERIFIED; profit TIDAK diverifikasi. Naik dari watchlist
  hanya bila verifikasi funder penuh + (bila relevan) identitas agen
  terkonfirmasi — keputusan parent/user, bukan laporan ini.
- **Entitas klaster §3:** 1 entitas terkoordinasi (5 wallet) — dicatat sebagai
  satu baris watchlist yang ditandai, bukan 5.
- **Heavy minter §2:** dicatat sebagai observasi volume, bukan watchlist
  (breadth di bawah ambang 5).
- **Tidak ada yang ditambahkan ke feed, tier-ab, atau Tier C.**

---

## 5. Temuan yang layak dibawa ke depan (bukan proposal)

1. **Early minter drop NFT ≠ kumpulan kecil.** 72 wallet muncul di ≥3 dari 7
   drop efektif (Emberforge dikeluarkan) — ekosistem minter awal itu ramai dan
   berulang, bukan segelintir agen. Breadth saja tidak membedakan agen
   independen dari farm yang menjalankan script mint-per-drop.
2. **Pola "1 mint per drop" mendominasi breadth tinggi:** sebagian besar wallet
   breadth 5–6 punya tepat 5–6 mint (1 per kontrak) — konsisten dengan agen
   yang mint sekali tiap drop ATAU farm sybil yang mint sekali tiap drop.
   Funder-lah pembedanya, dan funder baru terverifikasi untuk 1 klaster.
3. **future1001 bukan first-100 minter di drop-drop terbaru.** Breadth
   sepanjang waktu ≠ posisi paling awal di tiap drop. Untuk sinyal early Free
   Bacot, future1001 tetap referensi breadth, sementara first-100 sampel memberi
   kandidat kecepatan yang berbeda — keduanya tier-terpisah, tidak dicampur.
4. **Metode resolusi Boltbook→wallet sudah valid** (`ownerOfHandle` tanpa ".ai",
   25/25) dan profil Boltbook mencetak alamat wallet — jalur ini siap dipakai
   bila suatu saat ada receipt-post yang perlu diatribusikan ke wallet.
   Sebaliknya `handleOf` tidak bisa dipakai reverse lookup (gagal di kontrol).
5. **Sumber data log yang andal di VM ini = modul Ankr.** `fast_rpc` dan
   `bsc-dataseed` eth_getLogs gagal total di tugas ini; semua enumerasi log
   metode 6 lewat Ankr.

---

## 6. Keterbatasan (dinyatakan plain)

- Sampel = 8 kontrak (7 efektif), first-100 mint, anchor campuran eksak +
  firstSeenBlock — bukan sensus semua drop; breadth di luar sampel tidak
  diketahui.
- Data funder = halaman-1 Ankr 30 hari (1000 tx); 22 dari 31 wallet screened
  capped — funder bersama di luar halaman-1 tidak terlihat; independensi TIDAK
  terbukti untuk wallet non-klaster.
- Status .ai wallet sampel UNVERIFIED (kegagalan kontrol `handleOf`); tidak ada
  klaim "bukan agen" maupun "agen" untuk mereka.
- (d) profit, (e) dumper, (f) fee receiver TIDAK dijalankan untuk tier ini —
  tidak ada verdict atas ketiganya.
- Halaman depan ZH Boltbook gagal ekstraksi penulis; histori post penulis EN
  tidak ditelusuri satu per satu.
- Breadth 3–4 (43 wallet) hanya dihitung, tidak disaring.
- Aktivitas setelah blok 131414500 tidak tercakup.

---

## File pendukung (direktori gelombang yang sama)

- `m6_early.json` — mint first-100 per kontrak (625 mint).
- `m6_breadth.json` — breadth per wallet (255 wallet).
- `m6_screen.json` — hasil saringan 31 wallet (EOA, tx 30 hari, funders).
- `m6_authors.json` — resolusi 25 penulis halaman depan EN Boltbook.
- `m6_early3.py`, `m6_screen.py` — script yang dipakai (read-only).
