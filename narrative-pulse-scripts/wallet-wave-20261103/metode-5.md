# METODE 5 — Penyedia likuiditas awal

**Tanggal:** 2026-11-03 (WIB)
**Sifat:** READ-ONLY. Tanpa login, tanpa transaksi, tanpa signature, tanpa layanan berbayar,
tanpa menghubungi siapa pun. Tidak ada wallet yang ditambahkan ke feed, tier-ab, atau Tier C —
output di sini adalah daftar proposal untuk keputusan user saja.
**Standar kejujuran:** sama seperti `metode-1-2.md` dan `metode-4.md`. Yang tidak terverifikasi
ditulis sebagai tidak terverifikasi, bukan nol. Bacaan yang gagal ditulis sebagai gagal baca,
bukan ketiadaan. Jendela yang terpotong cap ditulis sebagai terpotong, bukan lengkap.

## Ringkasan hasil

- **14/14 pair metode 1 diperiksa** (12 pool V3 + 2 pair V2).
- **0 KANDIDAT, 0 PASS, 0 WATCH, 0 DITOLAK, daftar proposal: KOSONG.**
  Tidak ada satu pun wallet (EOA independen) yang tercatat menambah likuiditas di jam-jam
  pertama pada pair-pair ini, sehingga tidak ada subjek untuk disaring dengan 7 filter —
  tabel verdict per wallet tidak ada karena memang tidak ada wallet yang lolos definisi
  "penyedia LP awal" di luar kreator/launchpad.
- **Temuan struktural (bukan proposal): LP awal pada koin-koin terbentuk ini
  eksklusif kreator/launchpad.** Di semua 12 pool V3, satu-satunya minter posisi selama
  4 jam PERTAMA — dan bahkan selama 24 jam pertama — adalah kontrak kreator yang sama
  dengan minter pertama. Di pair V2 JAGENT, mint LP dimediasi kontrak launchpad yang
  mengirim LP ke dead + satu kontrak; di SAFU-B13B, satu-satunya mint LP dalam 4 jam
  adalah burn ke dead. Dengan kata lain: metode 5 tidak menemukan "cabal yang ikut
  menyediakan LP di awal" pada set ini — yang ada hanya kreator dan infrastrukturnya.

## 1. Metode + koreksi selama jalan

- **Definisi:** penyedia LP awal = alamat penerima mint LP (V3: `owner` posisi Mint;
  V2: penerima Transfer LP dari alamat nol) dalam **4 jam pertama** sejak mint LP
  pertama pair tersebut, **di luar** minter pertama tiap pair (dianggap kreator/LP awal),
  kontrak, dan exchange. Jendela 4 jam dihitung dari timestamp blok asli
  (batched `eth_getBlockByNumber`, bukan estimasi jumlah blok).
- **Koreksi 1 — event Mint V2 TIDAK punya field `to`.** Event V2 Pair adalah
  `Mint(address indexed sender, uint amount0, uint amount1)` — satu alamat saja.
  Query pertama dengan signature dua-alamat (`Mint(address,address,uint256,uint256)`)
  benar-benar mengembalikan 0 log untuk JAGENT/SAFU-B13B, dan itu yang memicu
  investigasi, bukan vonis "tidak ada LP". Provider V2 yang benar dibaca dari
  Transfer LP (mint token LP dari alamat nol) pada kontrak pair itu sendiri.
- **Koreksi 2 — cap Ankr 1000 + newest-first.** Query jendela pada pair sibuk
  mengembalikan hanya 1000 log TERBARU. Untuk JAGENT, jendela 4 jam punya >2000
  Transfer dari-nol (kedua paruh jendela masing-masing terpotong di 1000), jadi
  enumerasi provider jendela penuh TIDAK lengkap — yang dilaporkan adalah irisan
  1000 terbaru (518 tx, penerima hanya dead + satu kontrak) plus mint pertama
  yang terverifikasi terpisah. Kesimpulan "bukan wallet" tidak bergantung pada
  irisan yang terpotong ini, karena penerima yang terlihat pun bukan wallet.
- **Koreksi 3 — perilaku `toBlock` Ankr.** Query satu blok `[713, 713]` kosong
  padahal biseksi konvergen ke 712/713 — konsisten dengan `toBlock` eksklusif.
  Blok mint LP pertama JAGENT dicatat 130287712 (bukan 713); selisih satu blok
  tidak mengubah kesimpulan apa pun.
- **Alat:** modul Ankr `ankr.py` (`get_logs` address-filtered, topic difilter),
  `fast_rpc.batch` untuk timestamp blok, `eth_getCode` untuk filter (g).
  Semua topic/selector dihitung programatik via keccak, tidak pernah diketik.

## 2. Hasil per pair — pool V3 (12 pair)

Satu-satunya minter di jendela 4 jam DAN 24 jam adalah minter pertama (kontrak).
Angka mint = jumlah event Mint di jendela; distinct = jumlah owner berbeda.

| Koin | Pool | Mint LP pertama (blok) | Mint 4 jam | Mint 24 jam | Distinct 24 jam | Minter tunggal |
|---|---|---|---|---|---|---|
| AKE | 0x4d3bf29ba30f8bfe4624e7678709afa195689c5d | 58236590 | 1 | 1 | 1 | kreator-A |
| ARIA | 0xa5dbeaf16fc031eae92175974f8d0a439be4ad17 | 58128354 | 1 | 1 | 1 | kreator-A |
| IDOL | 0xfff4857a955b2b460c27fd431aa5a85fabca5559 | 51212206 | 1 | 14 | 1 | kreator-A |
| Q | 0x8bafe0bdd3eb9ae0539f5b32e771c1a72a189b7f | 59505725 | 1 | 1 | 1 | kreator-A |
| EVAA | 0x26deb24a2623cf54452ab5183e2c34551831d54d | 63195664 | 1 | 14 | 1 | kreator-A |
| ESPORTS | 0x83738a0b95cbd7dfd6989569a99edaed3dd704d0 | 54557588 | 1 | 1 | 1 | kreator-B |
| LYN | 0x302642976506d247c7017b85ddc89e3956f96ba1 | 63646465 | 23 | 74 | 1 | kreator-B |
| BASED | 0x07b7556Ede0f9a6a7d155A78Bc0573f531001A57 | 89551533 | 418 | 992 | 1 | kreator-B |
| JCT | 0xceC354f641Fb46b977c3a1f18B5cAf3E2Ede4C2c | 67692762 | 6 | 6 | 1 | kreator-B |
| AIN | 0xf4262c4dbf524f53851a5176bdc7d6c1e0fa82d8 | 52847146 | 2 | 8 | 1 | kreator-A |
| UAI | 0x82ED13117144344B39e5ec74d614D54465897a24 | 67232692 | 75 | 118 | 1 | kreator-B |
| COLLECT | 0x1FFEad9A221992D16f3AA02455542D2B2DA92bcf | 121394169 | 2 | 2 | 1 | kreator-B |

**Dua kontrak kreator (keduanya GAGAL filter (g), bukan wallet):**
- kreator-A `0x46a15b0b27311cedf172ab29e4f4766fbe7f4364` — minter tunggal AKE, ARIA,
  IDOL, Q, EVAA, AIN. Kode 48.934 byte.
- kreator-B `0x7b8a01b39d58278b5de7e48c8449c9f4f5170613` — minter tunggal ESPORTS, LYN,
  BASED, JCT, UAI, COLLECT. Kode 48.770 byte.
- Hash kode keduanya BERBEDA (bukan kontrak identik), tapi pola bytecode awal mirip
  dan perannya identik: kontrak penyedia posisi awal, masing-masing di 6 pair.
  Keduanya BARU — tidak ada di file m1/m4/tier-ab — tapi itu tidak relevan karena
  keduanya langsung gugur sebagai kontrak, bukan sebagai "wallet baru".
- Bahkan BASED (992 mint dalam 24 jam) dan UAI (118 mint) tetap satu owner:
  frekuensi mint tinggi di sini = aktivitas kreator, bukan banyak penyedia.

## 3. Hasil per pair — pair V2 (2 pair)

### JAGENT — pair V2 USDT `0xe6efcdef2b720d1eca2b69edb7ef357725680bea`
- Diverifikasi sebagai pair V2 asli: `token0()` = USDT, `token1()` = JAGENT,
  `factory.getPair(JAGENT, USDT)` mengembalikan alamat ini persis.
- **Mint LP pertama (blok 130287712, tx `0xb3a89c40…`): LP ke dead +
  1000 wei ke alamat nol (MINIMUM_LIQUIDITY)** = kreator membakar LP awal.
- **Jendela 4 jam `[130287712, 130319712]` (4,0 jam): >2000 Transfer dari-nol
  (terpotong cap di kedua paruh jendela).** Irisan 1000 terbaru: 518 tx, penerima
  hanya dead (518) dan kontrak `0x0ed943ce24baebf257488771759f9bf482c39706`
  (482; kode 1.362 byte = kontrak, gagal (g)).
- **Pola yang menjelaskan:** tx-tx tersebut memanggil kontrak
  `0x3643a907f875fa9b740e1c0747e91b5aa5222ab8` (kode 42.462 byte) dari banyak
  EOA berbeda — kontrak launchpad yang setiap pembelian JAGENT-nya ikut
  menambah LP, dengan LP dibakar ke dead + dikirim ke kontrak `0x0ed9…`.
  Kontrak `0x3643…` ini BUKAN temuan baru: ia sudah tercatat di metode 1 sebagai
  pembeli pertama JAGENT (blok 130287859) dan di metode 4-deep sebagai tujuan exit.
  Para EOA pemanggilnya adalah PEMBELI lewat launchpad, bukan pemegang LP —
  LP-nya tidak pernah ke wallet mereka.
- **Kesimpulan JAGENT: 0 wallet kandidat.** Penerima LP = dead (burn) + kontrak.

### SAFU-B13B — pair V2 B13B `0x13b86fcf85c9c8f5c36593822d216b8893c25450`
- **Tepat 1 mint LP dalam jendela 4 jam** (tidak terpotong cap, hasil lengkap):
  pada blok first-buy 126879472, LP ke dead. Tidak ada penambahan LP lain
  dalam 4 jam pertama.
- **Kesimpulan SAFU-B13B: 0 wallet kandidat.** Satu-satunya LP awal dibakar.

## 4. Screening (7 filter) — tidak ada subjek

- Provider non-kreator, non-kontrak, non-burn dari ke-14 pair: **0 alamat**.
  Provider total setelah mengecualikan minter pertama tiap pair = 0
  (`m5_screen.json`: `providers_total = 0`, `candidates = 0`, blok terbaru
  saat screening 131413081).
- Karena tidak ada kandidat, filter (a) independen, (b) aktif 30 hari,
  (c) early ≥3 koin, (e) bukan dumper, (f) bukan fee receiver tidak dijalankan
  per wallet — tidak ada yang bisa diloloskan atau ditolak. Ini dicatat sebagai
  "tidak ada subjek", BUKAN sebagai "semua lolos" dan bukan "semua ditolak".
- Filter (d) profit terealisasi: tidak berlaku (tidak ada kandidat); keterbatasan
  arsip harga RPC gratis yang sama seperti metode 1–2 dan 4 tetap berdiri untuk
  kandidat masa depan.
- Filter (g) sudah diterapkan pada semua alamat yang muncul: kedua kontrak
  kreator V3, kontrak `0x0ed9…`, kontrak launchpad `0x3643…`, dead, dan alamat nol
  — semuanya bukan wallet.

## 5. Verdict

| Kategori | Jumlah |
|---|---|
| PASS (lolos 7 filter) | 0 |
| WATCH (watchlist dulu, profit berulang belum terbukti) | 0 |
| DITOLAK | 0 (tidak ada subjek wallet) |
| **Daftar proposal watchlist** | **KOSONG** |

Tidak ada wallet yang ditambahkan ke set mana pun dari metode 5.

## 6. Keputusan perpanjangan yang TIDAK diambil sendiri

Tugas metode 5 mengizinkan perpanjangan ke koin terbentuk lain dari periode yang
sama bila set 14 pair menghasilkan terlalu sedikit provider. Pemeriksaan:
file mentah GeckoTerminal yang sama (`gecko-trending-raw.json`, 20 pool) adalah
PERSIS universe metode 1 (14 dipakai + AEON dikeluarkan + AGC/RVV/TART/ARK/AGT
dikeluarkan) — tidak ada koin terbentuk periode-sama tambahan di data yang ada.
Kohort baru berarti tarikan trending baru (era berbeda) + pass discovery baru,
yaitu perluasan scope — jadi TIDAK dijalankan sendiri; diserahkan sebagai
keputusan parent/user. Demikian juga kedatangan provider kedua di luar 24 jam
tidak diprobe (filter topic tidak bisa menyatakan "bukan kreator", sehingga
waktu kedatangan kedua tidak bisa dibiseksi langsung) — dicatat sebagai
keterbatasan, bukan sebagai "tidak pernah ada provider kedua".

## 7. Keterbatasan (jujur)

- Jendela 4 jam JAGENT terpotong cap (enumerasi penuh tidak tersedia); kesimpulan
  JAGENT bertumpu pada mint pertama (burn) + irisan 1000 terbaru (dead + kontrak)
  + pola caller launchpad — ketiganya konvergen, tapi enumerasi lengkap tidak ada.
- V3: provider kedua di luar 24 jam tidak diprobe (lihat §6).
- COLLECT tetap berbobot rendah (venue 259 hari pasca-formasi, sama seperti
  metode 1) — tidak berpengaruh di sini karena COLLECT juga hanya punya
  kreator-B sebagai minter.
- Semua alamat di laporan ini disalin dari output tool/file, bukan diketik.

## File bukti

- `m5_mints.py` + `m5_mints.json` — 12 pair V3: mint pertama, jendela 4 jam
  (timestamp blok asli), provider per pair.
- `m5_v2.py` + `m5_v2.json` — 2 pair V2 via Transfer LP dari-nol.
- `m5_v3_24h.py` + `m5_v3_24h.json` — uji sensitivitas 24 jam V3 (distinct tetap 1).
- `m5_screen.py` + `m5_screen.json` — screening: 0 provider, 0 kandidat.
- `m5_probe.py` — probe awal (trik PairCreated + beda topic V2/V3).
