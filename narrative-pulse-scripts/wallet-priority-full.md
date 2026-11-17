# Wallet Priority — alamat lengkap saja (INTERNAL)

Dibuat 2026-10-31. File ini HANYA berisi alamat lengkap (42 karakter, 0x + 40 hex).
Alamat terpotong DIBUANG dari file ini — jumlah alamat terpotong di file ini: 0.
File ini BUKAN daftar pantau terpercaya. `wallet-watchlist.md` tetap 0 alamat.
Tidak ada wallet di sini yang dipromosikan: promosi butuh PnL terealisasi 30 hari +
minimal 10 trade terealisasi + perilaku holding tercatat + keputusan user.
Data GMGN/DexScreener/GeckoTerminal adalah agregat sekunder, bukan bukti on-chain mentah.
On-chain menunjukkan APA dan KAPAN, bukan NIAT — tidak ada klaim insider.

## Kriteria prioritas (dari kriteria yang sudah dibuat)

1. Repeat lintas token, masih memegang, bersih dari tag Sniper/Bundler, bukan exchange.
2. Top holder satu token, masih memegang saat snapshot, bukan exchange, diurutkan
   berdasarkan porsi kepemilikan di laporan survivor.
3. Wallet dengan data PnL sekunder (GMGN) yang menguntungkan, tapi belum terukur
   penuh — tetap di bawah Tier A karena pengukurannya belum memenuhi syarat promosi.
4. NEGATIF / jangan diikuti: klaster sniper, funder sniper hub, funder tidak aktif
   dengan flag phishing — dicatat sebagai filter negatif, bukan sinyal follow.
5. Belum terklasifikasi: alamat lengkap lain yang perannya belum terverifikasi
   (bisa wallet trader, bisa alamat lain) — JANGAN dipakai sebelum dicek.
6. Dikecualikan: kontrak token, kontrak pool, burn, dan wallet exchange/kustodian.

## Tier A — Prioritas tertinggi, repeat / top holder masih memegang (13 alamat)

Wallet 0x8e966a9f17beab1ea50039434c2a14ad9e09b8d6 adalah satu-satunya kandidat early-call dengan 2 kaki masih memegang 100% (ok + 旺财). KOREKSI AUDIT LINKAGE 2026-10-31: repeat survivor yang dulu dicatat sebagai non-exchange (0xed9ab5bc05a0152b9dc2f7902e8369af7bc18771) ternyata adalah wallet exchange Bitget menurut OKLink, jadi SUDAH dipindah ke Tier E dan TIDAK dihitung sebagai monitor independen. Tier A di file ini sekarang hanya berisi wallet EOA privat. Sisanya adalah top holder survivor privat, diurutkan alfabetis di file ini; urutan porsi ada di laporan survivor.

- 0x13d1e9a96eba7906e1ede348c9bb604a03e46d02
- 0x5b2f11cab406f580a7c6faf620ee35daaf8648a5
- 0x6ba79dcc05a1056e19bf1021db4fca7be18b49e7
- 0x75642756e4ba4cc8fbe76df2239cada046cfc854
- 0x8272c61cc59cc78d5fa06f3c2c0594def2e8db6a
- 0x892200223bdfb11d2506c5ab1cae9222ce253acc
- 0x8e966a9f17beab1ea50039434c2a14ad9e09b8d6
- 0x93e7c78ab0db6f4961bfe7cf254422cbf7b82e1c
- 0xaab80f45b97d9dc86d9bea56a3e98274ba81026e
- 0xb787a5603d20e61585e20e7a13a1c0d6c03a1462
- 0xbe5905cf7a8bebd97fdc5d69a120b0ea720d3cdf
- 0xda91cefe240175e6fab56271110427a4195ab71f
- 0xf6a8280c997c4b4daa606e2c8c37b5a79b8ae2cc

## Tier B — Data sekunder menguntungkan, belum terukur penuh (1 alamat)

Wallet ini tercatat di review GMGN dengan PnL 7 hari positif dan win rate tinggi, tapi itu data agregat sekunder, bukan PnL terealisasi 30 hari + 10 trade yang disyaratkan promosi. Tetap di bawah Tier A.

- 0x2325f175975abdbcde555c79cc8e63381d28551b

## Tier C — NEGATIF, jangan diikuti (6 alamat)

Klaster sniper / funder sniper hub / funder tidak aktif. Dicatat hanya sebagai filter negatif.

- 0x318d2aae4c99c2e74f7b5949fa1c34df837789b8
- 0x612add8664aaacefbfa529633fefaf42dd16565a
- 0xb3466bfccf29e3babb61ca0f1b8984fde6ed728e
- 0xd392967fc834d718f4f9627fc5552881d1048727
- 0xd9c03f53044bb1dc3b4d59622ce631ceb307a54d
- 0xf5988713400da6fc8a58ec9515e2b0df9b40b115

## Tier D — Belum terklasifikasi, verifikasi dulu sebelum dipakai (30 alamat)

Alamat lengkap dari koleksi lama yang perannya belum terverifikasi. Jangan dipakai sebagai sinyal follow sampai dicek: apakah wallet trader atau alamat lain, riwayat trade, dan PnL terealisasi.

- 0x01c12cea3f3a6ae4e93518e0cb7eb57f69ce5730
- 0x0301b15ef5771c21e7e6afa90c24083c5a84433b
- 0x03bfbc28960f93641729070a1a94fbcf7f3e365a
- 0x0f93496909e0f93424a9db8cfa141b1094c9abb3
- 0x10c139638721bb8b40cfe6434acbbb5c295d0991
- 0x1a700335ece5c42834d6dd1f74204eec8e194444
- 0x2012e372d1661652a664655e5d5f318e7ae7ffff
- 0x222d44bf7c03c0f16a40047c820a2af3d4fca27a
- 0x2782c6e901126ba18a8c5c0caacf5a1563167777
- 0x47d4db5ae9567233e3fc426e775949bfe7205598
- 0x4a258513cbd14b53cc8dbd98f2364f14f2128a3b
- 0x53e32932382fcc2ec3e921c3d6ba3598d0e57777
- 0x5de0cb7101d0c7a841c3d4023c253a94dd35bf48
- 0x6632c78efd535035f5492c8ae54e6f84a063c2d6
- 0x7f72a5f832e5f63a1616e2b72874cf2e31d2bb67
- 0x84c72fd6a89d4cfe6bb179b57c4eb78fc3bde3ee
- 0x86570adc943c6102088c0b27acd218895bf3ff88
- 0x8894e0a0c962cb723c1976a4421c95949be2d4e3
- 0x8e6442663a4f8c50b6132c68d42a30e7dfe4ae15
- 0xa64E9dE168981Ebfd0b4A281FAf543B95f387777
- 0xabb9e7a54edf65c223724c5eb1c201d664750003
- 0xacc3aad53b8b13759921c62cba7f52c9a36d7ac4
- 0xb5a5720c5423d84352b572a859810b67341fccbd
- 0xb65657592791652a2c50006615ae6d7ac64f59f7
- 0xd8b9199a1723fa70d8c11cb21913ce3ddaa142ef
- 0xda45a79fec65b7eeb2d62c0df3282c29c5849494
- 0xf380e9dd74f26b5922ff81b7a9de6a9b8bdf564a
- 0xf4da82c411c1e2038abd4fb71eb6dd8835581fa6
- 0xfaad602aa5a1149a775e276a872944a790b71001
- 0xffc63f327c3e3080e2def90ed18954b9673128ab

## Tier E — Dikecualikan (kontrak / pool / burn / exchange) (48 alamat)

Bukan wallet trader individu. Disimpan di sini hanya agar pengecualiannya bisa diaudit, bukan untuk diikuti.

- 0x000000000000000000000000000000000000dead
- 0x0529ea5885702715e83923c59746ae8734c553b7
- 0x0b35285fe783dd3441573b84be4fbdb743457777
- 0x0c6302401aa5325c2e36f170f52c00b1d220b405
- 0x0d0707963952f2fba59dd06f2b425ace40b492fe
- 0x17a30350771d02409046a683b18fe1c13ccfc4a8
- 0x21aeddf21ee854f20cb497b0430437c4ab367777
- 0x23214ccbffb6ef479da64d1842b10b5525997777
- 0x2e8f79ad740de90dc5f5a9f0d8d9661a60725e64
- 0x338041378692867363672fd0dcf8544ac159eaed
- 0x3b056facce631561be371e0bc14f07d826737777
- 0x415aac3e46264c046d103c994a1da71f05c547f9
- 0x43684d03d81d3a4c70da68febdd61029d426f042
- 0x481f5963bf10cba972d52f138740155b2cda7059
- 0x4982085c9e2f89f2ecb8131eca71afad896e89cb
- 0x4cad1efbfd5f0848e0c3c14fab23f92b2fa81f17
- 0x504ce9e51e508c85a161058c12e970a903d482fc
- 0x511dfe9e248c887e32ca8bf9d1cb76f101965060
- 0x5a1e5b56aa33c056ed7bb93b88b1774a456f6694
- 0x5a52e96bacdabb82fd05763e25335261b270efcb
- 0x5c85d6c6825ab4032337f11ee92a72df936b46f6
- 0x636858d62f2e81deb7fd563621faef1a6a14d6c5
- 0x6778c3cd69892c372ca482c09f627fb271b635c5
- 0x69be413d648ae00f0fbd9856f1355e22b36ee5e0
- 0x6b2ce31a577d92f73516c7a91febc7672247e694
- 0x6d76e7bb743fee795a2f00a317760acf822ee2be
- 0x73d8bd54f7cf5fab43fe4ef40a62d390644946db
- 0x76219fbdc228a84ad19637ffbb6cdaa95a227777
- 0x872c29369d8446dda5916156403f6a7491847777
- 0x8dac80ce96f69f9762bc450faa4d7fbd5891ae18
- 0x90a54475d512b8f3852351611c38fad30a513491
- 0x91dca37856240e5e1906222ec79278b16420dc92
- 0x92aa03137385f18539301349dcfc9ebc923ffb10
- 0x98adef6f2ac8572ec48965509d69a8dd5e8bba9d
- 0x9d01d9ca91703b881dc0e585c6b746085b8f7777
- 0xadfffc33cdc9970349cbcea3d73ec343d6ed116d
- 0xbc42145d5a574ede9b8860fca2a49eb7b239efa5
- 0xbfc26980d8068ae744f5405d3abf6e7df02e11b3
- 0xc853d8253f0d8346ca80f3f6af53e49a763e7777
- 0xc882b111a75c0c657fc507c04fbfcd2cc984f071
- 0xd2dd7b597fd2435b6db61ddf48544fd931e6869f
- 0xe3d6871190d7143ea3e14c680f7b9fdd6bdc25a1
- 0xe4f2bc32d1018e165a657b098fd8c51f2cccf8e8
- 0xe61aad11bf4282fd5a8c584baa4ff2c9c50c7777
- 0xed9ab5bc05a0152b9dc2f7902e8369af7bc18771
- 0xf4b385849f2e817e92bffbfb9aeb48f950ff4444
- 0xf977814e90da44bfa03b6295a0616a897441acec
- 0xffba9d0f281193de9ee4e9050a5561ff9e08ae7b

## Total

Total alamat lengkap unik di file ini: 98
Tier A: 13, Tier B: 1, Tier C: 6, Tier D: 30, Tier E: 48
Alamat terpotong di file ini: 0
