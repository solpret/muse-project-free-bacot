# Screening 99 Wallet Sheet JAGENT — 2026-11-03

**Sumber:** Google Sheet `jagent_top_wallets`, rank 1–99 (dibaca publik).
**Tanggal screening:** 2026-11-03 (jendela aktivitas 48 jam terakhir ≈ 2026-11-01 ~09:00 WIB → 2026-11-03 ~09:00 WIB;
jendela 30 hari ≈ 2026-10-04 → 2026-11-03).
**Sifat:** READ-ONLY. Tidak ada transaksi, approval, sign, login, atau perubahan apa pun pada
tier-ab state, TRACKED_WALLETS, snapshot Free Bacot, maupun cron. Penambahan wallet ke set pantau
**butuh keputusan user atas daftar final ini**.
**Bahasa bukti:** semua alamat di laporan ini disalin dari file hasil ekstraksi, bukan diketik ulang.

## Ringkasan eksekutif

- **Overlap dengan set existing = 0.** Ke-99 wallet sheet adalah wallet baru: tidak satu pun sama dengan
  tier-ab 50, feed 3 (termasuk AFeng main), wallet user (main/destination), maupun klaster exclude
  (TRIO, PAIR, GANG, sniper hub `0xf5988713400da6fc8a58ec9515e2b0df9b40b115`,
  funder `0x318d2aae4c99c2e74f7b5949fa1c34df837789b8`).
- **Rekomendasi tambahan referensi screening: 4 wallet** (ranking di §A).
- **Watchlist: 13 wallet/entitas** (§B). **Ditolak: 82 wallet** (§C + lampiran 99 baris).
- **Peringatan utama:** ranking sheet **bukan** bukti smart money. Wallet rank 1 (svo.ai, Liquid $4.185)
  **ditolak** sebagai referensi: aktivitasnya hanya di ekosistem JAGENT, tanpa breadth launch lintas proyek.
  Sebaliknya 4 wallet yang direkomendasikan justru rank menengah (47–77).
- **Hold vs dump TIDAK TERVERIFIKASI** untuk semua wallet (lihat §Keterbatasan). Rekomendasi di §A
  didasarkan pada breadth partisipasi awal + aktivitas 48 jam + tidak adanya pola loop/dump yang teramati
  via proksi transfer, **bukan** pada bukti hold atau profit. Konfirmasi PnL butuh GMGN (§F).
- **Proyek panas 48 jam:** share sale AGC `0x6288dfe86f22b53eeb6886ae2d78941de7483743`
  (45 wallet sheet, 160 tx) adalah yang **benar-benar baru bagi snapshot Free Bacot** — tetapi laporan ini
  **TIDAK** mempromosikannya sebagai lead/kandidat dan **TIDAK** merekomendasikan mint. Statusnya masih
  butuh verifikasi bentuk track-C + gate website-only + umur sebelum status apa pun (§D).

## Metode (singkat)

Per wallet: EOA vs kontrak (ke-99 adalah EOA, `code 0x`), saldo BNB live, nonce/txcount live,
aktivitas kirim 48 jam + 30 hari (Ankr `ankr_getTransactionsByAddress`, terbaru dulu, cap 800 tx/wallet),
partisipasi di 168 kontrak snapshot Free Bacot, pola selector loop, funder top-5, dan fee-screen
(incoming Transfer 42 jam via Ankr `ankr_getLogs`, dari blok 131000000).
Kontrak diidentifikasi via Sourcify path tunggal + pembacaan on-chain (bukan dari nama/symbol saja).
Read failure = TIDAK TERVERIFIKASI, bukan nol/ tidak aktif (lihat §Keterbatasan).

## (a) Rekomendasi tambahan referensi screening — diranking

### 1. huy12345678.ai — rank 54, Liquid sheet $883,76
- Wallet: `0x341bed5b412968755f3dd6e9946636ac6f97457a`. BNB live 1,2407. EOA.
- **Breadth terbesar di sheet: 22 kontrak snapshot Free Bacot disentuh 30 hari** — Hachiko, PIXEL FROGS,
  Plutopop, Servobun, Xianyulo, Ghoulipop, Strawhex, Voltmohawk, Gargrowl, Glasscore, Slimelings,
  Agents NormiePunks, Critter Agent, Agent Finance, plus AZET, AgentPass, Agentical Glyphs, Anubis Agents,
  DropMiners, Gachagent, Kigae, Onimaru, Rootlinks (sebagian via selector non-mint).
- Pola: masing-masing 1 tx mint ke banyak factory pada 2026-11-01/02 — partisipasi awal berulang,
  bukan satu proyek. Kirim 48 jam: 163 tx, selector loop maksimal hanya 2× (tidak ada dominasi loop).
- Window 42 jam: 153 incoming ERC721 mint tersebar (top kontrak hanya 5×) — aktivitas mint luas,
  bukan spray satu koleksi.
- Proksi penjualan: hanya 1× `setApprovalForAll` dalam 30 hari yang terambil, tanpa `transferFrom` —
  **tidak ada bukti penjualan teramati** (proksi lemah, bukan bukti hold; lihat §Keterbatasan).
- Zero-value ERC20 incoming 42 jam: 0. Bukan fee recipient.
- Catatan: juga menyentuh kontrak-kontrak gelombang factory yang kini dibuang untuk screening baru —
  nilainya sebagai referensi adalah **pola masuk awalnya**, bukan proyek-proyek itu sendiri.

### 2. doctordefi.ai — rank 47, Liquid sheet $961,12
- Wallet: `0xd124dd5825ecaad959acdea6336926eb40aa0c9b`. BNB live 0,4590. EOA.
- **Breadth 16 kontrak snapshot** — Gargrowl, Ghoulipop, Glasscore, PIXEL FROGS, Plutopop, Servobun,
  Strawhex, Voltmohawk, Xianyulo, Agents NormiePunks, Critter Agent, Slimelings, plus AZET, AgentPass,
  Gachagent, Kigae.
- Kirim 48 jam: 66 tx, loop maksimal 2×. Window 42 jam: 354 incoming ERC721 mint (lihat anomali di bawah),
  22 ERC20 (nol zero-value).
- Proksi penjualan: **nol** `setApprovalForAll`/`transferFrom`/`safeTransferFrom` dalam window terambil.
- **Anomali yang harus dicatat (bukan alasan tolak):** 303 dari 354 incoming mint 42 jam berasal dari
  satu kontrak tak dikenal `0xb61b93704ae5c1d1d48cd97a18d78f23a4912b07`. Breadth 16 di atas berasal dari
  tx **kirim** mint yang terverifikasi, jadi tidak dibatalkan oleh anomali ini — tetapi sumber mass-mint
  `0xb61b...` belum diidentifikasi; bila ternyata airdrop pasif ke wallet ini, breadth kirim tetap valid,
  namun profil "selektivitas" wallet ini perlu konfirmasi GMGN sebelum promosi final.

### 3. huawubairihong.ai — rank 77, Liquid sheet $734,88
- Wallet: `0x5cf3f945620ba1a3cc9065a2086bfc728b172a0f`. BNB live 0,9705. EOA.
- **Breadth 9 kontrak snapshot** — Ghoulipop, Gondolux, PIXEL FROGS, Plutopop, SeanceSociety, Servobun,
  Voltmohawk, Xianyulo, AZET.
- Kirim 48 jam: 121 tx, loop maksimal 2×. Window 42 jam: 52 incoming ERC721 mint tersebar, 8 ERC20
  (nol zero-value).
- Proksi penjualan: 4× `safeTransferFrom` + 1× `setApprovalForAll` — ada transfer keluar teramati
  (tujuan tidak dianalisis; bisa penjualan atau pemindahan). Ini satu-satunya noda di profilnya;
  tetap direkomendasikan peringkat 3 karena breadth + tidak ada loop, dengan catatan transfer tersebut
  perlu konfirmasi GMGN.

### 4. future1001.ai — rank 49, Liquid sheet $920,22
- Wallet: `0x355ea9e542b36c645a2dee63b9df079ccb9bf3db`. BNB live 0,9146. EOA.
- **Breadth 7 kontrak snapshot** — Gargrowl, Glasscore, Agent Raccoons, Anubis Agents, Neural Frogs,
  Prompt Dogs, AgentPass.
- Kirim 48 jam: 69 tx, loop maksimal 5×. Window 42 jam: 64 incoming ERC721 mint (termasuk 13 BWOLF),
  39 ERC20 (nol zero-value).
- Proksi penjualan: 2× `setApprovalForAll`, tanpa `transferFrom` teramati.
- Peringkat 4 karena breadth lebih kecil dari tiga di atas; tetap memenuhi ambang ≥3 launch + aktif 48 jam
  + bukan loop/bot/fee-recipient.

## (b) Watchlist (bukan rekomendasi; butuh bukti tambahan)

- **nofomok.ai** (rank 46, Liquid $974,76, breadth 14): breadth besar (Hachiko, PIXEL FROGS, Slimelings,
  Gondolux 3×, HIVE, Ioforge, PIXEL BOYZ, dll.) TAPI **deployer AICAT** — `owner()` kontrak AICAT
  `0x62f80fd6bbdb9dcd3f3969e500bb2e25fd4d63fc` adalah wallet ini sendiri, dan 46 tx ke AICAT dalam
  30 hari (loop 48 jam 45×). Aktivitas AICAT-nya adalah self-interest, bukan sinyal independen.
  Watchlist saja; jangan jadikan referensi untuk AICAT. Window 42 jam: 87 mint tersebar, 88 ERC20,
  nol zero-value; proksi penjualan nol.
- **folio.ai** (rank 78, Liquid $729,70, breadth 4): Agentical Glyphs, Gondolux, HIVE, SeanceSociety.
  Memenuhi ambang minimum, tapi tipis; window 42 jam: 30 mint yang terkonsentrasi (10+10+10 dari
  3 kontrak) — batch minting, bukan breadth luas. Proksi penjualan nol. Naik ke rekomendasi hanya bila
  GMGN menunjukkan PnL/hold yang baik.
- **0xjl1222.ai** (rank 72, Liquid $754,00, breadth 3): AZET, GrimHarvest, NightshadeClub. Kirim 48 jam
  264 tx dengan loop claim 38× ke `0xb0d5...` + aktivitas difus (115 kontrak berbeda) — pola claim-loop
  berat. Watchlist, bukan referensi bersih.
- **0xzed.ai** (rank 64, Liquid $815,57, breadth 6): DropMiners, Gachagent, Gargrowl, Glasscore, Onimaru,
  Plaguelume. TAPI loop 34× ke 0agent Card + miner Pearl (34 tx) + 34 incoming ERC20 zero-value 42 jam
  — semuanya dari kontrak Pearl `0x7e2da878217eb995f9e5d36ed32c9cea52442681`, yaitu aliran yang terikat
  aktivitas mining-nya sendiri, **bukan** fee pasif dari pihak ketiga. Tetap watchlist karena loop.
- **owenx.ai** (rank 71, Liquid $769,20, breadth 2): Gondolux, HIVE. Di bawah ambang ≥3; aktif 48 jam
  (13 tx, loop 1×). Watchlist — promosi hanya bila breadth bertambah.
- **afeng123.ai** (rank 2, Liquid $3.414,60) + **afeng456.ai** (rank 27, Liquid $1.321,86): **JEBAKAN NAMA —
  keduanya BUKAN wallet utama AFeng** `0xbf004bff64725914ee36d03b87d6965b0ced4903` maupun dormant
  `0xbd28edf53231cd121a963b4b119d3cc4cb3a368a`. Bukti linkage pendanaan **ADA**: wallet utama AFeng
  mengirim total 14,6 BNB ke keduanya (ke afeng123: 5,0 BNB 2026-10-28; 2,5 + 2,0 BNB 2026-10-25;
  0,1 BNB 2026-10-21; ke afeng456: 1,0 + 2,0 + 2,0 BNB 2026-10-27). Identitas operator **BELUM terbukti**
  (pendanaan ≠ operator sama). Keduanya breadth snapshot 0, aktivitas 48 jam didominasi Pearl mining
  (afeng123: 20× Pearl; afeng456: 10× Pearl) + BWOLF. Watchlist sebagai **satu pertanyaan untuk user**
  (apakah keduanya milik AFeng / layak digabung?), bukan dua referensi independen, dan bukan bagian
  dari entitas AFeng main sebelum user memutuskan.
- **Kuartet chesenas.ai / chesenas1.ai / rukia.ai / xiyu3.ai** (rank 74/52/56/50): masing-masing ~47–48×
  selector `0x379607f5` ke kontrak unverified `0xab1f...` dalam 48 jam + funder bersama yang sama
  (`0x1fd6dc06a2608c12d91cbeb28bddaf91523728a3`, nonce 50 — alamat ini disalin programatik dari data;
  verifikasi awal sempat salah ketik dan sudah dikoreksi). **Hitung sebagai 1 entitas kandidat, bukan 4.**
  Watchlist sebagai satu entitas; promosi butuh identifikasi `0xab1f...` + konfirmasi bukan satu operator
  yang sama dengan pola dump.
- **cx1988.ai** (rank 70, breadth 1: Glasscore) dan **latte.ai** (rank 76, breadth 1: Agentical Glyphs):
  breadth di bawah ambang; latte juga funder-sharing dengan klaster `0x161b...` (lihat §Keterbatasan).
  Watchlist ringan.

## (c) Ditolak + alasan (ringkas; tabel lengkap 99 wallet di Lampiran)

- **Tidak aktif 48 jam terakhir (12):** aabbccdd.ai, baizhou.ai, zec777.ai, eric.ai, marco888.ai,
  luckycat.ai, henson.ai (breadth 1, tidak aktif), 918918.ai, btc59.ai, chaorenqifei.ai, k20.ai,
  jiang8888.ai. Catatan: aabbccdd + baizhou berbagi satu pengirim dust-level `0xc14a...`, keduanya
  BNB live tinggal 0,0002 (dari ~4,5 di sheet) — tautan lemah (dust, bukan pendanaan riil) + keduanya
  tidak promotable karena tidak aktif + terkuras.
- **Loop-bot / miner / trader loop (10):** ianever.ai (675× Pearl/48 jam), qifeiba.ai (212× 0agent Card
  + 198× Pearl), a9julebu.ai (413× 0agent Card + 194× Pearl + 1.328 log incoming 42 jam),
  101111.ai (709× selector `0xa04914ff` ke `0x789e...`), skyxinchen.ai (500× selector yang sama),
  0xfatdog.ai (800 tx terambil/48 jam tersebar di 772 kontrak berbeda — difus ekstrem, sangat dicurigai bot),
  vivian0610.ai (loop buy launchpad 57× + 107 incoming WBNB = trader, bukan early holder),
  czheyi.ai (119× loop `0xbd85...` + konsentrasi BWOLF 126 incoming), kkuhn.ai (42× loop `0xbd85...`),
  zhangdapao.ai (41× loop `0xbd85...` + 41 incoming BWOLF).
- **Terhubung sniper hub yang sudah diexclude (3):** dokss.ai, sjnsn.ai, answer.ai — terhubung ke
  `0xf5988713400da6fc8a58ec9515e2b0df9b40b115` (dan funder bersama `0x5072...`). Flag/exclude,
  bukan referensi.
- **Spray-mint bot (1):** gake.ai (breadth 3: AZET, DelegateDAO, HIVE) — 174 tx kirim/48 jam difus +
  104 incoming ERC721 mint 42 jam yang hampir semuanya dari kontrak berbeda (top 1×) — pola spray
  massal, bukan partisipasi selektif.
- **JAGENT-only / tanpa breadth launch (56 sisanya, termasuk rank 1):** breadth snapshot 0 dan aktivitas
  48 jam terkonsentrasi di infra JAGENT (diamond proxy `0xb300...`, sale `0x3643...`, token JAGENT),
  token yang sudah dikenal (FIST/FAGENT, Ptah, Pearl, BWOLF), atau loop token tak dikenal — tanpa
  partisipasi awal berulang di ≥3 launch. Termasuk **svo.ai (rank 1, Liquid $4.185,58)** — rank-nya
  mencerminkan kepemilikan JAGENT, bukan skill lintas launch; breadth 0, kirim 48 jam hanya 24 tx.
  Juga termasuk yuki888.ai (265 tx tapi loop JAGENT 32× + tanpa breadth), mr1617.ai (138 tx, tanpa breadth),
  8785.ai (187 tx, tanpa breadth), dan 53 wallet lainnya di Lampiran.
- **Pola dump ≥80% dalam hitungan menit di ≥2 launch: TIDAK ADA yang terverifikasi** dalam screening ini
  — karena hold/dump tidak dapat dibaca (lihat §Keterbatasan), tidak ada wallet yang dilabel "dump"
  maupun "terbukti dump". Label "terindikasi" pun tidak diberikan tanpa bukti transfer keluar yang terukur.

## (d) Proyek baru yang ramai/laku — 48 jam terakhir wallet sheet

Ranking berdasarkan jumlah distinct wallet sheet yang ikut (tx kirim). Label cross-check terhadap
snapshot Free Bacot (168 kontrak). **Bukan sinyal Free Bacot** (set sheet belum masuk set terkumpul
dan jendela ini retrospektif) dan **bukan rekomendasi mint**.

| # | Kontrak | Wallet sheet | Bukti / label |
|---|---------|--------------|---------------|
| 1 | `0xb300000b72deaeb607a12d5f54773d1c19c7028d` (proxy Diamond JAGENT) | 56 / 296 tx | Infrastruktur JAGENT (dikenal). Satu-satunya selector 30 hari: `0x810c705b` (3.677 tx, 96/99 wallet). Facet `0xb415...` unverified → nama fungsi TIDAK terverifikasi. |
| 2 | **`0x6288dfe86f22b53eeb6886ae2d78941de7483743` (share sale AGC)** | **45 / 160 tx** | **Benar-benar baru bagi snapshot Free Bacot.** Token "Agentic Coin"/AGC 18 desimal `0x63dea5acdbe1f27c968907d08610a5f0a0284ba6`, harga 0,002 BNB/share, MAX_SHARES 1.650.000, totalShares 71.732 (4,35%), pair AGC/WBNB `0xe56041cddbb46db01c67b7a62684f428a04db8c6`, fundedStage 1, tidak pause, B_QUOTA 5, MAX_BATCH 50, registry = registry Agent ID yang dikenal. Aktivitas sheet pertama 2026-11-02 19:31 WIB, puncak 20:00 WIB (45 tx/jam), bump kedua 2026-11-03 07:00 WIB (29 tx). **BUKAN lead/kandidat, TIDAK ada rekomendasi mint** — butuh verifikasi bentuk track-C + gate website-only + umur. Jumlah share per wallet TIDAK TERVERIFIKASI (input tx tidak disimpan; `userInfo`/`freePositionCount` gagal total). |
| 3 | USDT / PCS V2 router / WBNB | 33 / 31 / 22 | Infrastruktur (transfer/swap/wrap), bukan proyek. |
| 4 | FIST `0xc988...` (30 wallet) + FIST Agent `0x0c87...` (22) | 30 / 22 | Token yang sudah dikenal (FIST/FAGENT), bukan launch baru. |
| 5 | `0x50c64d3931ef5d7704b4b324b344d052d051320e` | 28 / 40 tx | **Benar-benar baru bagi snapshot.** Satu selector: `mint(uint256,uint256)` 40×. Kontrak unverified. Aktivitas pertama 2026-11-01 19:01 WIB (mr1617.ai). Bentuk sale/mint belum diverifikasi — bukan lead. |
| 6 | Pearl mining `0x7e2d...` | 20 / 1.297 tx | Proyek dikenal (mining loop; kuota hari berjalan, rollover 18:08 WIB). Bukan launch. |
| 7 | `0x673a2506f95f66fa65a0bb7a4ce8b0d32d728cf2` (BWOLF) | 19 | Tidak ada di snapshot; token/NFT yang sudah ramai (approve + fungsi tak dikenal). Status gate tidak dicek di tugas ini — bukan temuan baru yang diverifikasi. |
| 8 | `0x7fcd981a1e48b3fb488c2e21d987156b2a4df48a` | 19 | **Benar-benar baru bagi snapshot.** Unverified, aktivitas pertama 2026-11-02 14:53 WIB (latte.ai), selector campuran tak dikenal. Bukan lead. |
| 9 | `0x7c0d...` (mint ShaLingGou) | 17 | **Dikenal — topik dijeda user ("Lupakan saja" 2026-11-02). Label saja, jangan dikejar.** |
| 10 | `0xbd85cf75e784b921728e027547d78577cfe72e2b` | 15 / 566 tx | Tidak ada di snapshot; loop berat (374× + 161× dua selector). Unverified. Bukan launch terverifikasi. |
| 11 | `0x15cfd2dc8278fb87a1783ef42111618e20874365` + launchpad `0x7703...` | 15 / 10 | Tidak ada di snapshot; keluarga launchpad bonding-curve (owner bersama `0x2866...` untuk `0x15cf...`+`0x1b8f...`+`0x7703...`). Aktivitas trading (buy/sell), bukan free mint. |
| 12 | `0xfd7c...` (sale HONGBAO) | 11 | **Sudah di-mint user — bukan baru.** |
| 13 | `0x7de1606230aa70802caecf1a3e90039a6265b1c4` | 11 | **Benar-benar baru bagi snapshot.** Aktivitas pertama 2026-11-02 22:46 WIB (mr1617.ai), 32× selector tak dikenal. Bukan lead. |
| 14 | `0xb0d5f3108af164f5f7046f53ab59fd2779812d10` (claim) | 12 / 57× `claim()` | Tidak ada di snapshot; kontrak claim sejak 2026-10-22. Bukan launch baru. |
| 15 | `0x24df7874ca006bc34898e779412f7b3c6b511693` (claimFree) | 11 / 10× `claimFree` | Tidak ada di snapshot; klaim gratis sejak 2026-11-01 19:49 WIB. Bukan lead terverifikasi. |
| 16 | `0xb995508476dec1ff929d91a6f0400892ae2a71c9` (AIC token) | 13 | Tidak ada di snapshot; mint 30× + fungsi kedua 20×. Terkait AICAT? Tidak diverifikasi — jangan disamakan. |
| 17 | `0xfd5fc1f863bf25170801de45a48968611db2c824`, `0xa255...`, `0xc7df...`, `0x2b8b...`, `0x5c9a...`, `0x5052...`, `0x5883...`, `0xfd97...` | 11–14 | Tidak ada di snapshot; aktivitas loop/campuran tak dikenal, pertama 2026-10-31 s.d. 2026-11-01. Bukan temuan baru yang diverifikasi. |

Pace 48 jam (gambaran): gelombang masuk terbesar terjadi 2026-11-01 siang–sore WIB (factory mints)
dan 2026-11-02 malam WIB (sale AGC). Tidak ada proyek di daftar ini yang dipromosikan sebagai
kandidat Free Bacot oleh laporan ini.

## (e) Overlap dengan set existing

| Set | Jumlah | Overlap |
|-----|--------|---------|
| Tier-ab watch (50 wallet) | 50 | **0** |
| Feed TRACKED_WALLETS (3, termasuk AFeng main `0xbf00...`) | 3 | **0** |
| Wallet user main `0xeb237F6f9FB4e826739F0954e9768914F28b2c2E` | 1 | **0** (dan tidak pernah dijadikan kandidat) |
| Wallet user destination `0xcf3c6fc1bf670a8d3f03436395286f86dbee7418` | 1 | **0** |
| Klaster exclude (TRIO, PAIR, GANG, sniper hub `0xf598...`, funder `0x318d...`) | — | **0** (3 wallet sheet terhubung ke sniper hub sebagai *counterparty*, bukan anggota klaster: dokss/sjnsn/answer — tetap ditolak, lihat §C) |

Seluruh 99 wallet sheet adalah entitas baru bagi sistem pantau.

## (f) Daftar butuh konfirmasi GMGN (login-gated; TIDAK dicoba login)

Halaman wallet GMGN login-gated sejak 2026-11-02 ~23:29 WIB; tidak ada login yang dicoba dalam tugas ini.
Wallet berikut **tidak dipromosikan** sampai PnL-nya terkonfirmasi via GMGN (atau sumber setara):

- Ke-4 rekomendasi §A (huy12345678, doctordefi, huawubairihong, future1001) — konfirmasi hold/profit
  sebelum ditambahkan ke set pantau.
- Watchlist §B yang promosinya bergantung pada PnL: nofomok, folio, 0xjl1222, 0xzed, kuartet chesenas
  (sebagai 1 entitas), afeng123/afeng456 (plus pertanyaan identitas operator).
- Trader yang keputusannya sepenuhnya bergantung pada PnL: vivian0610, czheyi, kkuhn, zhangdapao,
  yuki888, mr1617, 8785.
- Catatan: GMGN juga tidak dapat mengonfirmasi hold NFT snapshot (bukan PnL trading) — untuk itu
  dibutuhkan pembacaan `balanceOf` yang saat ini gagal (lihat §Keterbatasan).

## Keterbatasan & hal yang TIDAK TERVERIFIKASI (baca sebelum bertindak)

1. **Hold vs dump tidak terbaca.** Dua metode gagal: (i) `balanceOf` via JSON-RPC langsung gagal
   transport (kemungkinan TLS egress) untuk semua 90 pasangan bridge-wallet × kontrak; (ii) Ankr
   `getNFTsByOwner` mengembalikan 0 aset untuk ke-13 bridge wallet (kemungkinan cakupan indeks BSC NFT
   yang tidak mencakup koleksi-koleksi ini) — hasil ini **bukan** bukti saldo 0. Proksi yang tersisa
   (tidak adanya `transferFrom`/`setApprovalForAll` dalam window terambil) adalah bukti lemah:
   penjualan via order off-chain tetap mungkin. **Jangan klaim wallet mana pun "hold" atau "dump".**
2. **Riwayat 30 hari terpotong untuk 19 wallet** yang mencapai cap 800 tx (bot ekstrem). Irisan 48 jam
   lengkap untuk semua wallet kecuali bot ekstrem tersebut; kesimpulan 48 jam tidak terpengaruh.
3. **Pengirim dust `0xb0d0277fe089bee3fc7879cac889d2d5091d2d10` (24–28 wallet): BUKAN bukti klaster.**
   Transfernya bernilai 1,6e-8 BNB dengan input kosong (contoh: 2 tx ke svo.ai) — ping dust level platform,
   bukan pendanaan operator. Ke-28 wallet **tidak** digabung menjadi satu entitas atas dasar ini.
4. **Funder `0x161ba15a5f335c9f06bb5bbb0a9ce14076fbb645` (9 wallet: ny1, bigsht, kisskisskiss,
   onlyouyouyou, czheyi, k20, tat, latte, wyxcl): identitas belum teridentifikasi.** Jumlah riil
   (total 5,69 BNB ke 10 wallet pada cek detail, 0,0005–1,354 BNB per wallet) tetapi nonce yang terbaca
   34.696.251 (terverifikasi dua kali, tidak masuk akal untuk EOA) + saldo ~0,115 BNB yang seragam di
   beberapa alamat sejenis — anomali belum terjelaskan. Wallet-wallet ini **tidak** digabung atas dasar
   ini; semuanya sudah ditolak/watchlist karena alasan lain.
5. **Sale AGC `0x6288...`:** jumlah share per wallet, `userInfo`, dan `freePositionCount` gagal dibaca
   (OSError total) — laporkan sebagai unverified, bukan nol. `EPOCH 150000` adalah nilai mentah yang
   belum ditafsirkan (bukan tanggal). Tidak ada rekomendasi mint.
6. **Kontrak unverified Sourcify** (`0x50c6...`, `0xbd85...`, `0x15cf...`, `0x7fcd...`, `0xab1f...`,
   `0x1994...`, `0xb0d5...`, facet `0xb415...`) artinya **nama fungsi tidak terverifikasi**, bukan bukti
   proyek jahat atau proyek bagus.
7. **Lonjakan nonce sejak snapshot sheet** (txcount live jauh di atas nonce sheet) terbesar: a9julebu
   +1.781, 0xjl1222 +1.881, qifeiba +1.351, ianever +1.221, 101111 +1.150, 0xfatdog +1.060 — konsisten
   dengan pola loop/bot, bukan dengan aktivitas manusia selektif.

## Lampiran — disposisi 99 wallet (digenerasi dari data; kolom: rank, agent, wallet, disposisi, kirim-48j, breadth snapshot-30h, Liquid sheet $)

| rank | agent | wallet | disposisi | kirim 48j | breadth snapshot | Liquid $ |
|---|---|---|---|---|---|---|
| 1 | svo.ai | `0x1c67a90145673a9fbecb2f4e01583781f1e54dd0` | TOLAK (tanpa breadth launch) | 24 | 0 | 4185.53 |
| 2 | afeng123.ai | `0xc8a7e53b9f785a3747fe0b562087fa796002871b` | WATCHLIST | 65 | 0 | 3414.6 |
| 3 | aabbccdd.ai | `0x2c17da9b66eef551eaa2be715fcc549fa1a0c667` | TOLAK (tidak aktif 48j) | 0 | 0 | 3180.84 |
| 4 | bigdick.ai | `0xa1c93ac37eebeedbafdadb757f76715f3c9f9ed4` | TOLAK (tanpa breadth launch) | 15 | 0 | 2695.32 |
| 5 | baizhou.ai | `0x010301282df31641eab4bdd907caebe739ad81df` | TOLAK (tidak aktif 48j) | 0 | 0 | 2680.49 |
| 6 | mapleleaf.ai | `0x56d6531497d2c4a2659e36fbde057880b03d1b70` | TOLAK (tanpa breadth launch) | 18 | 0 | 2648.82 |
| 7 | xzz.ai | `0x357ece9ba52fd66126a1f0a31640da5e0846a4ea` | TOLAK (tanpa breadth launch) | 59 | 0 | 2274.94 |
| 8 | fuckcrypto.ai | `0xa2f8299316b7b6d1297dd454397e089a1482d7c2` | TOLAK (tanpa breadth launch) | 36 | 0 | 2220.55 |
| 9 | zhangdapao.ai | `0x843c3a176fde9e71372a295dd93ff72b775b297f` | TOLAK (loop) | 83 | 0 | 2045.83 |
| 10 | zec777.ai | `0xb700879a92a22ad53daaede32280d03764984e55` | TOLAK (tidak aktif 48j) | 0 | 0 | 1977.85 |
| 11 | czheyi.ai | `0xab3436bc55755048eab7f07d62bef6eadc7d3dd9` | TOLAK (loop) | 210 | 0 | 1969.24 |
| 12 | 8785.ai | `0x058b68b28537c31630a7201d50c460d3399dc509` | TOLAK (tanpa breadth launch) | 187 | 0 | 1961.12 |
| 13 | vvxxc.ai | `0x109707e32e2906b093b20d34132f75e90fc43c65` | TOLAK (tanpa breadth launch) | 9 | 0 | 1888.92 |
| 14 | kisskisskiss.ai | `0x9aec85a0db856183d425f4d4c7e6f275c17627d9` | TOLAK (tanpa breadth launch) | 33 | 0 | 1871.23 |
| 15 | xiaopeng.ai | `0x2fe0088c80919f40529e0d0adc68140651445044` | TOLAK (tanpa breadth launch) | 15 | 0 | 1839.66 |
| 16 | eric.ai | `0xebe7e5d0d40881d71ef229f56f9d0ddaeb3c8122` | TOLAK (tidak aktif 48j) | 0 | 0 | 1814.8 |
| 17 | dashabi.ai | `0x98818274649e449f248154112cffa5bc98563e09` | TOLAK (tanpa breadth launch) | 18 | 0 | 1737.16 |
| 18 | xyhh.ai | `0x3db7a83d41db7f8b15cc7df9e13cc6a29b8e5643` | TOLAK (tanpa breadth launch) | 33 | 0 | 1737.0 |
| 19 | liangbanxian.ai | `0x76913c25fd0cac3fb7e90762d313bd2887682641` | TOLAK (tanpa breadth launch) | 2 | 0 | 1694.21 |
| 20 | ny1.ai | `0x2c12b2935372808cdf7e1b548f8e390d7ed5a44a` | TOLAK (tanpa breadth launch) | 27 | 0 | 1679.73 |
| 21 | a9julebu.ai | `0x5548e8c99e77e2f8142f72dc1dc3dbf89172768b` | TOLAK (loop) | 799 | 0 | 1661.82 |
| 22 | vivian0610.ai | `0x5a1f729475838ab4e7c11d1718e58040b608ecc3` | TOLAK (loop) | 373 | 0 | 1464.54 |
| 23 | alingling.ai | `0x2d88b64804f67b30c441887d42c394946064ccb5` | TOLAK (tanpa breadth launch) | 14 | 0 | 1423.23 |
| 24 | axi.ai | `0xc11676f5b9a2ee311507bdf244f85602c204c8a5` | TOLAK (tanpa breadth launch) | 6 | 0 | 1360.5 |
| 25 | aeaeaero.ai | `0xe2f05a60cb610f182dea8ed3a645e3eea41ba70d` | TOLAK (tanpa breadth launch) | 18 | 0 | 1349.31 |
| 26 | asiangenius.ai | `0x5a51e3d19bb947123c7f30e1bb148a7b5a309eaa` | TOLAK (tanpa breadth launch) | 2 | 0 | 1341.48 |
| 27 | afeng456.ai | `0x5836b532e67a316ff727b39167a9c6bd7d9a484f` | WATCHLIST | 87 | 0 | 1321.86 |
| 28 | onlyouyouyou.ai | `0xa80adf52941a2b98027eb42d6f06ef8a748f49a4` | TOLAK (tanpa breadth launch) | 32 | 0 | 1273.87 |
| 29 | marco888.ai | `0x2b1e4b7a1bada98236f0d1c74666b4a69544cb4e` | TOLAK (tidak aktif 48j) | 0 | 0 | 1239.31 |
| 30 | 0589.ai | `0xfb89b6d12d54c724359ca025dea123187df395f0` | TOLAK (tanpa breadth launch) | 10 | 0 | 1184.36 |
| 31 | kkuhn.ai | `0xa159c1c36fcd6699923db199b7dcc42a9cc72c9b` | TOLAK (loop) | 151 | 0 | 1182.2 |
| 32 | woaiai.ai | `0x05f4814083e6d1319c53c61205a76d9fa680d00d` | TOLAK (tanpa breadth launch) | 1 | 0 | 1174.21 |
| 33 | yuesheng.ai | `0x43e68ad2412ec52ce3e4b0b895051a931e0ee743` | TOLAK (tanpa breadth launch) | 12 | 0 | 1142.51 |
| 34 | yuki888.ai | `0x16b3038c7a85709ed55c5eba05872d1bc3b3511c` | TOLAK (tanpa breadth launch) | 265 | 0 | 1118.12 |
| 35 | lovemili.ai | `0xd3293ba2bb8218b815c7e2ba195dddcb313aa298` | TOLAK (tanpa breadth launch) | 19 | 0 | 1117.93 |
| 36 | hu8888.ai | `0xeb6ba4f9bff15e4a18c820a16fcd99a427492813` | TOLAK (tanpa breadth launch) | 3 | 0 | 1109.46 |
| 37 | ianever.ai | `0x1a916e7036db5e4710e9d523eee49525fffa9f12` | TOLAK (loop) | 796 | 0 | 1081.07 |
| 38 | 0xshenyuan.ai | `0x7bd58464589f45a12c6bb958fb813cdedb4991d7` | TOLAK (tanpa breadth launch) | 45 | 0 | 1069.78 |
| 39 | proustygg.ai | `0x436a52a3a936cf026fc1e40561691d78c80695fe` | TOLAK (tanpa breadth launch) | 10 | 0 | 1061.04 |
| 40 | biekkkk.ai | `0x5d567dc141014886080f7e8c7f3460a87da18004` | TOLAK (tanpa breadth launch) | 6 | 0 | 1060.08 |
| 41 | bigj8.ai | `0x19b51354900eb64042b6145f39377584299e712d` | TOLAK (tanpa breadth launch) | 62 | 0 | 1047.76 |
| 42 | pipi888.ai | `0x500f79f9d96b3509b69388ac7871ee1a59183df7` | TOLAK (tanpa breadth launch) | 28 | 0 | 1008.79 |
| 43 | 0xfatdog.ai | `0x6c1d2a8fd2c19f0904a74aada178281da0d3d5f9` | TOLAK (loop) | 800 | 0 | 992.59 |
| 44 | wymask.ai | `0xe2699abcb4568fa0bb338788a666f9267ca45687` | TOLAK (tanpa breadth launch) | 2 | 0 | 976.03 |
| 45 | bigsht.ai | `0x6e500110281032b42be94e130b2ddc4e9d5b16ea` | TOLAK (tanpa breadth launch) | 70 | 0 | 975.02 |
| 46 | nofomok.ai | `0xc20a6f15b2d0e7cdd900cbabe070a052e457a7f4` | WATCHLIST | 261 | 14 | 974.76 |
| 47 | doctordefi.ai | `0xd124dd5825ecaad959acdea6336926eb40aa0c9b` | LAYAK | 66 | 16 | 961.12 |
| 48 | luckycat.ai | `0x26b2f6536dc89f6b7aa3eaa32f7fda3ee4d443a6` | TOLAK (tidak aktif 48j) | 0 | 0 | 936.26 |
| 49 | future1001.ai | `0x355ea9e542b36c645a2dee63b9df079ccb9bf3db` | LAYAK | 69 | 7 | 920.22 |
| 50 | xiyu3.ai | `0xd65b2cf01a15f94bc3150e87e800305aee519172` | WATCHLIST | 147 | 0 | 906.2 |
| 51 | mr1617.ai | `0x3fd842204a3d033f1b3e2834f98ca1fb59471997` | TOLAK (tanpa breadth launch) | 138 | 0 | 902.68 |
| 52 | chesenas1.ai | `0x8f4f535563f9b659913f23625bd48f96fba68a04` | WATCHLIST | 141 | 0 | 895.29 |
| 53 | henson.ai | `0xf10ea88456f144cc9710766103c65ba7e362d2bd` | TOLAK (tidak aktif 48j) | 0 | 1 | 887.05 |
| 54 | huy12345678.ai | `0x341bed5b412968755f3dd6e9946636ac6f97457a` | LAYAK | 163 | 22 | 883.76 |
| 55 | 918918.ai | `0xe8bdb64fa1fc5d1d6ef1a4fd6e149c5db236d3e4` | TOLAK (tidak aktif 48j) | 0 | 0 | 883.49 |
| 56 | rukia.ai | `0xacfda39f2be2986ddcb4e718c81f82d506fffc6e` | WATCHLIST | 148 | 0 | 878.17 |
| 57 | guguji.ai | `0x3f8e9b9f7707ca553caf5709c8c40d8009e1075e` | TOLAK (tanpa breadth launch) | 1 | 0 | 871.45 |
| 58 | btc59.ai | `0x8405a058a0aae1ae7c5f54b01864becde685d726` | TOLAK (tidak aktif 48j) | 0 | 0 | 861.74 |
| 59 | zane6.ai | `0x7864b017df283fe7200519df14486858f482c418` | TOLAK (tanpa breadth launch) | 1 | 0 | 849.57 |
| 60 | chaorenqifei.ai | `0x1edeeba861d1c4171176194f2c4b89150274b874` | TOLAK (tidak aktif 48j) | 0 | 0 | 849.31 |
| 61 | k20.ai | `0xae7cc36aa3eda382d6f766d02b512eb3ced74537` | TOLAK (tidak aktif 48j) | 0 | 0 | 841.6 |
| 62 | gake.ai | `0xd898c86c9eedaa2583317563d53f64dd02259717` | TOLAK (spray) | 174 | 3 | 833.9 |
| 63 | xiaoxiaowang.ai | `0x6836938725e10e11f009ba6292db1f72906ffe1a` | TOLAK (tanpa breadth launch) | 21 | 0 | 815.91 |
| 64 | 0xzed.ai | `0xf392f2504dbbb595423128d3286791528bd55c10` | WATCHLIST | 84 | 6 | 815.57 |
| 65 | song000.ai | `0xbd704ce345a86a6ba1854cc6eef7ddffd47cbb29` | TOLAK (tanpa breadth launch) | 17 | 0 | 815.1 |
| 66 | tat.ai | `0xba64a3ccc5051bf403718789e3a6d8272d9b2c0b` | TOLAK (tanpa breadth launch) | 1 | 0 | 810.22 |
| 67 | kk1314.ai | `0x3433536e398b18d18e11c5097316206b659a9ad9` | TOLAK (tanpa breadth launch) | 2 | 0 | 803.94 |
| 68 | wyxcl.ai | `0xca031d4489bae77c1733d9970e4febba95bca65b` | TOLAK (tanpa breadth launch) | 8 | 0 | 798.25 |
| 69 | ljljl.ai | `0x9356d3ec186f46f6b44764a564f7ee58ed6fc4b4` | TOLAK (tanpa breadth launch) | 10 | 0 | 785.0 |
| 70 | cx1988.ai | `0x8d3c379e8efcaf45b6fa7bb88f0acbf7c42faaa6` | WATCHLIST | 43 | 1 | 782.39 |
| 71 | owenx.ai | `0x0447f8770fa7e505710132beb84ef5552558dba7` | WATCHLIST | 13 | 2 | 769.2 |
| 72 | 0xjl1222.ai | `0xb24a87c78dc7b0a19c32e45c6c6901750ea07a31` | WATCHLIST | 264 | 3 | 754.0 |
| 73 | 077.ai | `0x141509edfab631e22000da55ec7dab8e3857932e` | TOLAK (tanpa breadth launch) | 3 | 0 | 746.64 |
| 74 | chesenas.ai | `0x24b45415e4f49394fb61ff18fd5a3c259ea059f0` | WATCHLIST | 182 | 0 | 743.17 |
| 75 | qifeiba.ai | `0xc56d3272d5fd91af3af017b012d0450059253383` | TOLAK (loop) | 578 | 0 | 741.13 |
| 76 | latte.ai | `0xbe00a83228a6e37dae35b5efc9de78198376c450` | WATCHLIST | 21 | 1 | 735.74 |
| 77 | huawubairihong.ai | `0x5cf3f945620ba1a3cc9065a2086bfc728b172a0f` | LAYAK | 121 | 9 | 734.88 |
| 78 | folio.ai | `0x9355eef9273f051f1be83ec1ba11000cedf02e69` | WATCHLIST | 103 | 4 | 729.7 |
| 79 | yihebnb.ai | `0x53e9d84a4d021010f5e92153ecbbe554513d43be` | TOLAK (tanpa breadth launch) | 93 | 0 | 717.72 |
| 80 | jiang8888.ai | `0xa916956fd6afa5a09e3c93120cdd25a271de6206` | TOLAK (tidak aktif 48j) | 0 | 0 | 716.49 |
| 81 | sjnsn.ai | `0xb746b786f7facc2509d13e86b68fb89a629b209a` | TOLAK (sniper-hub) | 41 | 0 | 711.97 |
| 82 | minhlinh96.ai | `0xc7eb668d483420acd6d1e2b67698d4f4908c0f69` | TOLAK (tanpa breadth launch) | 11 | 0 | 707.14 |
| 83 | skyxinchen.ai | `0x6d57470f2fb9c4b52af3403d9c8a05fc66d52c56` | TOLAK (loop) | 539 | 0 | 706.18 |
| 84 | erenncc.ai | `0x1ef8266ca4679d73ab6e073d6098ab5190b0c202` | TOLAK (tanpa breadth launch) | 41 | 0 | 705.81 |
| 85 | 66666.ai | `0x9e07a0272fa968e2d7fc1c42fe35a679359fd7bb` | TOLAK (tanpa breadth launch) | 12 | 0 | 704.18 |
| 86 | x08.ai | `0xd3d18998a909bf60112e4628f08010ecb5a81593` | TOLAK (tanpa breadth launch) | 1 | 0 | 702.1 |
| 87 | yich.ai | `0x31bd3e80c855991b9804a05dfbe69ed33c9513f6` | TOLAK (tanpa breadth launch) | 8 | 0 | 701.89 |
| 88 | wangdayou.ai | `0x2ade611e4b135b77ae682d81ac88f279e80740da` | TOLAK (tanpa breadth launch) | 5 | 0 | 701.78 |
| 89 | 152597.ai | `0x0758991012977354a9ab19d84e880188ded33a54` | TOLAK (tanpa breadth launch) | 10 | 0 | 700.18 |
| 90 | dokss.ai | `0x6a13773ba217a86bdb1fe761f280b676476ff449` | TOLAK (sniper-hub) | 35 | 0 | 694.1 |
| 91 | swarm.ai | `0x3e30b96ca1add665db85c3b01f5b258a7bfe8bc2` | TOLAK (tanpa breadth launch) | 3 | 0 | 693.02 |
| 92 | r1yan.ai | `0xd87a9e01129e070663c9f0100c6262d3ae4b8ebb` | TOLAK (tanpa breadth launch) | 108 | 0 | 692.42 |
| 93 | 101111.ai | `0xc43744ee088aa50189353f0a0b1b71bf323e62e7` | TOLAK (loop) | 799 | 0 | 688.72 |
| 94 | 0xzero.ai | `0x233b2d270ae552a759c79236cafca762346c84e6` | TOLAK (tanpa breadth launch) | 18 | 0 | 682.48 |
| 95 | 1518.ai | `0xd329c33b0f9ea340bba95227883ee4dd4798cb68` | TOLAK (tanpa breadth launch) | 58 | 0 | 676.96 |
| 96 | maka.ai | `0xa596047e12f9fabc42ee491fe263b1b71b004da7` | TOLAK (tanpa breadth launch) | 84 | 0 | 676.8 |
| 97 | 16u.ai | `0xc46b52fccbceb44f0523b59def23b3274deb9053` | TOLAK (tanpa breadth launch) | 15 | 0 | 668.85 |
| 98 | answer.ai | `0x00d7e319ce53eb2aabb928c88ff05e68febd47c5` | TOLAK (sniper-hub) | 4 | 0 | 662.57 |
| 99 | auteman.ai | `0xb0b97e52f3da69555e65f8bdd87ccb182dfdcca2` | TOLAK (tanpa breadth launch) | 15 | 0 | 660.39 |
