# Daftar NFT Wallet Utama — dipelihara

- Wallet: `0xeb237F6f9FB4e826739F0954e9768914F28b2c2E`
- Terakhir diperbarui: 2026-11-08 ~16:30 WIB
- Total: 71 baris tabel saat ini (6 item terkonfirmasi ownerOf live 2026-11-02 — Coracle #897/#898, Botmolt #2628, drop.ai #2193, SOLVD #869/#2137 — masih belum masuk tabel, menunggu enumerasi penuh).
- Metode verifikasi 2026-11-02: enumerasi Ankr `ankr_getNFTsByOwner` (70 aset, 2 halaman, pageSize 50) + verifikasi live `balanceOf`/`ownerOf` per kontrak untuk SEMUA item. Hasilnya cocok penuh, dengan 3 pengecualian Ankr yang basi: Ankr masih menampilkan BAO-NFT #4292 (padahal sudah dibakar, balanceOf live = 0), MORI #3573 (ownerOf live revert = token mati), dan tidak menampilkan DIGG Ore (ERC-1155, balanceOf live id 2 = 1). Yang berlaku selalu bacaan live, bukan Ankr.
- Aturan update: file ini diperbarui setiap ada NFT MASUK (mint/beli/terima) atau KELUAR (jual/transfer/burn) yang terkonfirmasi on-chain. Nomor urutan menyesuaikan bila ada perubahan.
- Rarity: kata proyek sendiri verbatim, tidak pernah dikonversi. Tanpa trait Rarity/Tier = "tier tidak terverifikasi", bukan tebakan.
- Pasar: prioritas (1) market proyek sendiri, (2) Element. Element API saat ini butuh x-api-key tanpa jalur anonim, jadi floor Element di bawah adalah TERAKHIR TERCATAT 2026-10-31, bukan live hari ini. Market sendiri SAFU/AlienID/Brutes/Hirelings/DIGG tidak mempublikasikan counter bid/volume di kontrak — di sana bid/volume ditulis tidak tersedia, bukan nol. Di mana tertulis "tidak ada venue live", berarti floor, bid, dan volume ketiganya tidak tersedia di venue terverifikasi.

| No | NFT | Kontrak | Rarity | Floor | Bid | Volume | Status |
|----|-----|---------|--------|-------|-----|--------|--------|
| 1 | Agent Periodic Lab O₂ #1021 (ERC-1155, 1 unit) | 0xfE5Ab5ce9b1D86a55d70E7D0573a14D559029C18 | tier tidak terverifikasi | own LabMarket live, fee 2% (291 listing total) | tidak tersedia | tidak tersedia | TER-LISTING 0,000171 BNB (listing 291, LabMarket) |
| 2 | Agent Punks #741 | 0x3B2C00e1dFe1a1B45F93E990fFe56C5dCa4670b7 | tier tidak terverifikasi | Element 31 Okt 0,000247 BNB | tidak tersedia | tidak tersedia | tidak ter-listing |
| 3 | AgentsEstates #4611 | 0x439643cfd023c247519518B7F73D06823E1F2fCe | tier tidak terverifikasi | market live 0,0003 BNB (blok 131151950) | tertinggi market 0,001 BNB (bukan khusus #4611) | total 3,108 BNB; 24j 2,469 BNB; penjualan 1.625 | TER-LISTING 0,0035 BNB (expiry 2026-12-01T23:27:20Z; verifikasi on-chain 2026-11-06 ~07:56 WIB) |
| 4 | AlienID #3333 | 0xd12C42935F06B37337588B9169ba1593b534eB86 | Common | own 30 Okt 0,001 BNB; Element 31 Okt 0,0004 BNB | tidak tersedia | tidak tersedia | TER-LISTING 0,001 BNB |
| 5 | AlienID #3684 | 0xd12C42935F06B37337588B9169ba1593b534eB86 | Common | own 30 Okt 0,001 BNB; Element 31 Okt 0,0004 BNB | tidak tersedia | tidak tersedia | TER-LISTING 0,001 BNB |
| 6 | Brutes #3967 | 0x44aB9F4687d5D6cd2454266b1E548552FB924908 | tier tidak terverifikasi | own 30 Okt 0,00008 BNB; Element 31 Okt 0,00045 BNB | tidak tersedia | tidak tersedia | TER-LISTING 0,000076 BNB |
| 7 | Bubblebruin #757 | 0xc205F8c74733D914776D66cBc4Cf10BF701D96Aa | tier tidak terverifikasi | tidak ada venue live | tidak tersedia | tidak tersedia | tidak ter-listing |
| 8 | Cathodex #421 | 0x0AC5591d1B980C7bE16861d722E59E21E2624868 | tier tidak terverifikasi | tidak ada venue live | tidak tersedia | tidak tersedia | tidak ter-listing |
| 9 | CharMasks #1529 | 0xf197F509137db1eb45b17a362bc446D48E6dAC4f | tier tidak terverifikasi (non-transferable) | tidak ada venue live | tidak tersedia | tidak tersedia | tidak ter-listing |
| 10 | Crop Pals #5449 | 0xd43f328560aE9bA09B27375d1b83F7FA7A0d091b | tier tidak terverifikasi (trading terkunci s.d. 10.000 minted) | tidak ada venue live | tidak tersedia | tidak tersedia | tidak ter-listing |
| 11 | Cryonyx #407 | 0x787b522d48084A83b8B1b0C206aA4A12B1FD1cc2 | tier tidak terverifikasi | tidak ada venue live | tidak tersedia | tidak tersedia | tidak ter-listing |
| 12 | DIGG Copper Ore (ERC-1155, 1 unit, id 2) | 0xB6407991b76E712d15EdEF06e125abcC730364F7 | Tier Copper | Copper fresh 2026-11-02 0,35 USDT (32 listing aktif) | topOffer 31 Okt null | total 31 Okt 0,739386 BNB; hari 0,285116 BNB; daySales 229 | TIDAK ter-listing (listing pernah diblokir 351803) |
| 13 | Gearotter #204 | 0xF25E1c4dBE48383e93f5992B2E7FE7331B5a9AD0 | tier tidak terverifikasi | tidak ada venue live | tidak tersedia | tidak tersedia | tidak ter-listing |
| 14 | Gelede #540 | 0xA06427Fb1c58fE5313696630383d8A875Eb2a7dE | tier tidak terverifikasi | tidak ada venue live | tidak tersedia | tidak tersedia | tidak ter-listing |
| 15 | Ghoulipop #541 | 0xb2d236EC0473792eC6727e5bf41084Df3eA0137F | tier tidak terverifikasi | tidak ada venue live | tidak tersedia | tidak tersedia | tidak ter-listing |
| 16 | Hachiko #839 | 0x48c977d13ef156475F086F907D8da9583E1E072E | tier tidak terverifikasi (tanpa atribut) | tidak ada venue live | tidak tersedia | tidak tersedia | tidak ter-listing |
| 17 | HashDroids #5782 | 0x0EED2C5e866A3792f587CAf0839941EA57fe6915 | tier tidak terverifikasi (soulbound) | tidak ada venue live | tidak tersedia | tidak tersedia | tidak ter-listing |
| 18 | Hirelings #3927 | 0x6b1D77D3DeDE3FC775ca8C7BDe08C2C2EAAb9BEA | tier tidak terverifikasi (reveal pending) | own 30 Okt 0,00014 BNB; Element 31 Okt 0,0005 BNB | tidak tersedia | tidak tersedia | TER-LISTING 0,00001 BNB (live 11 Nov) |
| 19 | Hirelings #4342 | 0x6b1D77D3DeDE3FC775ca8C7BDe08C2C2EAAb9BEA | tier tidak terverifikasi (reveal pending) | own 30 Okt 0,00014 BNB; Element 31 Okt 0,0005 BNB | tidak tersedia | tidak tersedia | TER-LISTING 0,00001 BNB (live 11 Nov) |
| 20 | HIVE Agents #808 | 0x1458b0C132Fb51BDC65B1Ca7a3BE484BCd9A2f77 | tier tidak terverifikasi | tidak ada venue live | tidak tersedia | tidak tersedia | tidak ter-listing |
| 21 | Hotpotsage #398 | 0xEbAdb5Be9692b0BF25E8A5F3351C35DdC58f195d | tier tidak terverifikasi | tidak ada venue live | tidak tersedia | tidak tersedia | tidak ter-listing |
| 22 | Ioforge #486 | 0x259b5Da3f44a44C89bcA5EE2297582c41c758d0F | tier tidak terverifikasi | tidak ada venue live | tidak tersedia | tidak tersedia | tidak ter-listing |
| 23 | Kirinova #377 | 0x68a971C9D2b54Ae86dAF59CD665E40f3E087fb7F | tier tidak terverifikasi | tidak ada venue live | tidak tersedia | tidak tersedia | tidak ter-listing |
| 24 | Lensorb #392 | 0x1edfd1e6c6b132e88f5b09b1dbe025037b5b0539 | tier tidak terverifikasi | tidak ada venue live | tidak tersedia | tidak tersedia | tidak ter-listing |
| 25 | Lumen Genesis #2321 | 0xC996A35D6dA945519eF5d3572C5A8cdc845AE842 | Rare (Prism, per rarity.json proyek) | own market situs ada tapi belum ada listing live (Listed —, Floor —, No sales yet) | tidak tersedia | tidak tersedia | tidak ter-listing |
| 26 | Mars Nexus #1448 | 0xC4059D2F9F6F86695896e68F3E73E1e6cC3791c8 | MINER (project's own Tier trait; Miner 60%, 1x mining power, Power Units 100) | orderbook situs pernah ada 2026-10-31 (USDT, fee 8%) tapi sell listings belum dibuka saat itu; status hari ini belum dicek ulang | tidak tersedia | tidak tersedia | tidak ter-listing |
| 27 | Mummibo #216 | 0x666830a348414D3E8B2d341D1ec9D562211034af | tier tidak terverifikasi | tidak ada venue live | tidak tersedia | tidak tersedia | tidak ter-listing |
| 28 | Neijuanbo #697 | 0xcc67bDae1457f8B0914FBFD3fD93b4b1831F0401 | tier tidak terverifikasi | tidak ada venue live | tidak tersedia | tidak tersedia | tidak ter-listing |
| 29 | Neonkoi #273 | 0x3ADfBBa26d3674477aA21B0CF2E4C2BC643ff85b | tier tidak terverifikasi | tidak ada venue live | tidak tersedia | tidak tersedia | tidak ter-listing |
| 30 | Neonraven #370 | 0xcc5608A7F5A5Bc8F1bEABcD010A8C0066a0243Ae | tier tidak terverifikasi | tidak ada venue live | tidak tersedia | tidak tersedia | tidak ter-listing |
| 31 | Neptuno #203 | 0x6e2dFd975dA6A54d18d1816029C6657454E61c9a | tier tidak terverifikasi | tidak ada venue live | tidak tersedia | tidak tersedia | tidak ter-listing |
| 32 | NianNian #1195 | 0x4A2bb7B24C39CA548b050aD0C0aFfea5e6e04aF2 | tier tidak terverifikasi (Type Ordinary, locked 100.000 token, VIP dividend No) | tidak ada venue live (trading token buka saat total 10.000; totalMintedShares ~1.171 saat mint) | tidak tersedia | tidak tersedia | tidak ter-listing |
| 33 | Phoenixi #207 | 0x0c4370EdE2500511Ec9FD5a7c69c47e7EE4118E4 | tier tidak terverifikasi | tidak ada venue live | tidak tersedia | tidak tersedia | tidak ter-listing |
| 34 | Plutopop #516 | 0xE4cA7AaA82253717C0d897C10d58D59821631509 | tier tidak terverifikasi | tidak ada venue live | tidak tersedia | tidak tersedia | tidak ter-listing |
| 35 | Ptah POA #29643 | 0xD87ADb2E47979d6cb323896B1A9320E0dd132213 | tier tidak terverifikasi | tidak ada venue live | tidak tersedia | tidak tersedia | tidak ter-listing |
| 36 | Qilinora #689 | 0x952B7C0b8e63B3dB965d49ec91d4Eb73D8BBC264 | tier tidak terverifikasi | tidak ada venue live | tidak tersedia | tidak tersedia | tidak ter-listing |
| 37 | SAFU Bots #3073 | 0x763aaD3528b408bc42300DBab4Ec755cdE1D0192 | Rare | own 30 Okt 0,00014 BNB (61 listing); Element 31 Okt 0,000059 BNB | tidak tersedia | tidak tersedia | TER-LISTING 0,0961 BNB (live 11 Nov — 685× floor, tidak akan laku; reprice ke floor menunggu keputusan user) |
| 38 | SeanceSociety #326 | 0x8F8705A91cb8af615CE35179B0D33200AdE71DAb | tier tidak terverifikasi | tidak ada venue live | tidak tersedia | tidak tersedia | tidak ter-listing |
| 39 | Servobun #517 | 0xbd297cb5158F4DcA02C336A59556FDBfa6609A70 | tier tidak terverifikasi | tidak ada venue live | tidak tersedia | tidak tersedia | tidak ter-listing |
| 40 | SEVY Genesis #9841 | 0xF054C8Ca0119A2955FeF43669Ee68e7d2ab7e49A | tier tidak terverifikasi (hak redeem 100 SEVY) | tidak ada venue live | tidak tersedia | tidak tersedia | tidak ter-listing |
| 41 | SEVY Genesis #9843 | 0xF054C8Ca0119A2955FeF43669Ee68e7d2ab7e49A | tier tidak terverifikasi (hak redeem 100 SEVY) | tidak ada venue live | tidak tersedia | tidak tersedia | tidak ter-listing |
| 42 | SEVY Genesis #9845 | 0xF054C8Ca0119A2955FeF43669Ee68e7d2ab7e49A | tier tidak terverifikasi (hak redeem 100 SEVY) | tidak ada venue live | tidak tersedia | tidak tersedia | tidak ter-listing |
| 43 | SEVY Genesis #9846 | 0xF054C8Ca0119A2955FeF43669Ee68e7d2ab7e49A | tier tidak terverifikasi (hak redeem 100 SEVY) | tidak ada venue live | tidak tersedia | tidak tersedia | tidak ter-listing |
| 44 | SEVY Genesis #9848 | 0xF054C8Ca0119A2955FeF43669Ee68e7d2ab7e49A | tier tidak terverifikasi (hak redeem 100 SEVY) | tidak ada venue live | tidak tersedia | tidak tersedia | tidak ter-listing |
| 45 | Strawhex #628 | 0x61C360b0fA3fef5c61728756e0fb574c66D73663 | tier tidak terverifikasi | tidak ada venue live | tidak tersedia | tidak tersedia | tidak ter-listing |
| 46 | SynapseSquad #184 | 0xD65913933ada0b429de8f17eDBAdf5FA24aa94E2 | tier tidak terverifikasi | tidak ada venue live | tidak tersedia | tidak tersedia | tidak ter-listing |
| 47 | Tempestara #656 | 0xDAA48EED214eDBcf1fF76A9540C819b8afe4BED7 | tier tidak terverifikasi | tidak ada venue live | tidak tersedia | tidak tersedia | tidak ter-listing |
| 48 | TRACE Genesis #2256 | 0xe5E2c43746F3A5E713C246592095D7cf82E808Cc | tier tidak terverifikasi | own market live, floor live 0,000495 BNB (verifikasi on-chain 2026-11-06 ~08:39 WIB, 87 listing aktif dari 94) | tidak tersedia | tidak tersedia | TER-LISTING 0,000495 BNB (market TRACE 0x30cAc2eA33fA5B06EDC44fF01f9B8c768D8DFEB3, fee 1%; approve tx 0x2f0c36b48cc0b7e1f48ba573abaf80d2b6b7e099f35e8a176ee86c086be585b3 blok 131923274; list tx 0x31dbf97f4631cfe68a4c1841d59e4f29af56d05dda74197dd81503ada7ff722d blok 131923341, verifikasi on-chain 2026-11-06 ~08:52 WIB) |
| 49 | Voltmohawk #936 | 0x06aB825D14454174819E1c08a6E72C4b5bBF78fE | tier tidak terverifikasi | tidak ada venue live | tidak tersedia | tidak tersedia | tidak ter-listing |
| 50 | Veyanth #938 | 0x3f73b5A2B56a16E4204053C6a2CD51f2b3E4188E | tier tidak terverifikasi | tidak ada venue live | tidak tersedia | tidak tersedia | tidak ter-listing |
| 51 | Veyanth #939 | 0x3f73b5A2B56a16E4204053C6a2CD51f2b3E4188E | tier tidak terverifikasi | tidak ada venue live | tidak tersedia | tidak tersedia | tidak ter-listing |
| 52 | Veyanth #940 | 0x3f73b5A2B56a16E4204053C6a2CD51f2b3E4188E | tier tidak terverifikasi | tidak ada venue live | tidak tersedia | tidak tersedia | tidak ter-listing |
| 53 | Xianyulo #507 | 0x5bF46eF8E5e09fFFfd928e30077b4d4674CBA4b0 | tier tidak terverifikasi | tidak ada venue live | tidak tersedia | tidak tersedia | tidak ter-listing |
| 54 | Zapcourier #387 | 0x672c1dF4F7121DaCBD3504995441C47d2fAbCdDC | tier tidak terverifikasi | tidak ada venue live | tidak tersedia | tidak tersedia | tidak ter-listing |
| 55 | DigDown #5361 | 0xF464550f1d744793893C0ce09b89269Ed726d796 | tier tidak terverifikasi | situs hanya halaman mint; Element tertera di situs (listing live belum terverifikasi) | tidak tersedia | tidak tersedia | tidak ter-listing |
| 56 | Agentic Bull #322 | 0xcd4472Af68801DE87E970A333C71da5d12E825A3 | Legendary (Tier, per metadata proyek) | belum dicek | tidak tersedia | tidak tersedia | tidak ter-listing |
| 57 | Merith #1144 | 0x3dF52d687a7a5F79Fc1BE45fECD1B2Ec1Df622A7 | tier tidak terverifikasi (Edition Open, Sun Setting) | situs hanya halaman mint, tidak ada venue live | tidak tersedia | tidak tersedia | tidak ter-listing |
| 58 | Merith #1145 | 0x3dF52d687a7a5F79Fc1BE45fECD1B2Ec1Df622A7 | tier tidak terverifikasi (Edition Open, Sun High) | situs hanya halaman mint, tidak ada venue live | tidak tersedia | tidak tersedia | tidak ter-listing |
| 59 | Merith #1146 | 0x3dF52d687a7a5F79Fc1BE45fECD1B2Ec1Df622A7 | tier tidak terverifikasi (Edition Open, Sun Low) | situs hanya halaman mint, tidak ada venue live | tidak tersedia | tidak tersedia | tidak ter-listing |
| 60 | Merith #1147 | 0x3dF52d687a7a5F79Fc1BE45fECD1B2Ec1Df622A7 | tier tidak terverifikasi (Edition Open, Sun High) | situs hanya halaman mint, tidak ada venue live | tidak tersedia | tidak tersedia | tidak ter-listing |
| 61 | Merith #1148 | 0x3dF52d687a7a5F79Fc1BE45fECD1B2Ec1Df622A7 | tier tidak terverifikasi (Edition Open, Sun Setting) | situs hanya halaman mint, tidak ada venue live | tidak tersedia | tidak tersedia | tidak ter-listing |
| 62 | Vault-Crack #752 | 0x1a7a8BbB49e3e8Cf951996789Fd69d4C7524A2B4 | Locker (Vault, per metadata proyek) | situs hanya halaman mint, tidak ada venue live | tidak tersedia | tidak tersedia | tidak ter-listing |
| 63 | Agent Cards #1720 | 0x19f125dA1985033f102CA7746Cbd1F6f512CFACd | Common (Sun Guardian, South, Warrior, Level 1, P51/D71/S47/L57, Series Genesis, Holo No) | 0,00047 BNB (market proyek sendiri, 200 listing, cek 21:36 WIB) | tidak tersedia | tidak tersedia | TER-LISTING @ 0,00001 BNB (live 11 Nov) |
| 64 | Ghost Frog #22 | 0x29EE92a8D6Dc62035D0C2b4D53B5df504D3Ebe91 | tier tidak terverifikasi (metadata host mati) | tidak tersedia | tidak tersedia | tidak tersedia | tidak ter-listing |
| 65 | Agent Oil Rig #1977 | 0xF00D595F9fbb8308Fb03eeEC7406e6883B157413 | Free (tier proyek sendiri, rarityOf on-chain = 0, origin free) | belum terverifikasi dari sumber independen | tidak tersedia | tidak tersedia | STAKED pool 6 (custody OilDrilling sejak 2026-11-04, bisa unstake) |
| 66 | The Orzo #6702 | 0x39f61c0a379f132d66fb8c2adab293e6a7595b0a | tier tidak terverifikasi (proyek menyatakan semua piece setara, hanya nomor edisi berbeda) | tidak ada venue live terverifikasi | tidak tersedia | tidak tersedia | soulbound — sudah klaim 13.333 ORZO 2026-11-04, tidak bisa dipindah |

## Di luar nomor (bukan NFT koleksi / bukan wallet utama)

- SPACE ID Agent ID (masgayut.ai) — token identitas, soulbound, tidak dihitung sebagai koleksi. Kontrak registry 0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F.
- NFT wallet tujuan (0xcf3c6fc1bf670a8d3f03436395286f86dbee7418) tidak masuk daftar ini: Onchain Crystals #4169/#4170, Fragment #4155, HALLU #4170/#4171, Robotic #5349, HALCYX #1992/#1993, QUOGENT #3279, Agent Koi #3596, LeadLoop #5555/#5556, PIXEL SHIBA #5076, Ascension #2326, Worldygg Tree #7081, dan lain-lain. Runestone #5634 SUDAH TIDAK di wallet tujuan sejak 2026-10-30 (lihat "Sudah keluar").
- DigiWarriors #4104 — dulu wallet utama, kini owner pihak ketiga (per pengecekan 2026-11-01), tidak masuk daftar.

## Sudah keluar dari wallet utama (dihapus dari daftar saat terkonfirmasi)

- MORI #3573 — mati (ownerOf live revert 2026-11-02), tidak lagi dihitung.
- BAOracle #4292 — dibakar 2026-11-02 (balanceOf live = 0).
- CIOW #480 — terjual 2026-11-01 (balanceOf live = 0).
- HashOre #7451 — terjual (per catatan 2026-11-01).
- Runestone #5634 — keluar dari wallet tujuan 2026-10-30 21.41 WIB ke 0x89dC856Befb2728227451aA3a67FCe430B01e54A (aksi BscScan "Fill Batch Signed…", tx 0x94be0aa6990b08d8e878a8a347c932e3f1e2e243ab9b9d8dbff14f3be8e387c6), lalu ke 0xcee9c651b23587843a73aa4ae908acd3ed956ba3 pada 2026-10-31 05.48 WIB (tx 0x3332f92d89177e9078604a54d04cca384b492b41b4ab23b8c8f7ebb7460672eb); riwayat lengkap BscScan 2026-11-04, 4 transfer, pemilik saat ini 0xcee9… (bukan wallet utama maupun wallet tujuan).

## Koreksi dari daftar ini (2026-11-02)

- Coracle #897/#898 dan Botmolt #2628 — inventaris 2026-10-29 menaruhnya di wallet tujuan, tetapi ownerOf live 2026-11-02 membuktikan keduanya di wallet UTAMA. Koreksi ini yang berlaku.
- drop.ai #2193 dan SOLVD #869/#2137 — tidak ada di inventaris sebelumnya; ditemukan lewat enumerasi Ankr dan dikonfirmasi ownerOf live. Rarity SOLVD: Tier T2/T4 verbatim proyek, Rare: none. drop.ai: tanpa trait Rarity/Tier.

| 67 | Agentic Node #1391 | 0x0691Dd61f84bda232BcD0bd80F6559EcC2c00131 | tier tidak terverifikasi dari metadata (tokenURI kosong; edisi Starter = tier 0 gratis dari parameter mint + situs) | tidak ada venue live terverifikasi | tidak tersedia | tidak tersedia | tidak ter-listing |
| 68 | ACAT #1817 | 0x28a38A372639E8C481aD41B9B16E52c3c6366ACC | Uncommon (Havana Brown, Domestic breed, United Kingdom, 18/31, reward klaim 40.000 ACN sekali) | market proyek sendiri live (ACATMarket 0x3424De685702E8d63BaAC20BB67d1a205db89427, 5 listing, floor 24.000 ACN, fee 5%) | tidak tersedia | tidak tersedia | tidak ter-listing (TAHAN per pilihan user 2026-11-04 ~18:52 — klaim 40.000 ACN SUDAH diklaim 2026-11-04, tx 0x08997b31bef35c8ab3f216ee829c931daf426bc2cc77b8cda11e5d7ed5d17c27) |
| 69 | HACKED #1395 | 0xCD355D1191Ce9849B3A935C821A66d9DF37cFE77 | tier tidak terverifikasi (tanpa trait Rarity/Tier; background indigo, hatch diagonal, body white, shackle white, eyes dot, mouth flat, accessory horn, emblem none, frame red) | tidak ada venue live terverifikasi | tidak tersedia | tidak tersedia | tidak ter-listing (mint gratis 2026-11-05, override gate kasus ini saja) |
| 70 | HACKED #1396 | 0xCD355D1191Ce9849B3A935C821A66d9DF37cFE77 | tier tidak terverifikasi (tanpa trait Rarity/Tier; background indigo, hatch grid, body green, shackle red, eyes scan, mouth glitch, accessory horn, emblem bolt, frame red) | tidak ada venue live terverifikasi | tidak tersedia | tidak tersedia | tidak ter-listing (mint gratis 2026-11-05, override gate kasus ini saja) |
| 71 | 402 #174 | 0xd80D0095746999c93AE837B1DE1569d5814405dC | tier tidak terverifikasi (metadata generik bersama, tanpa traits/attributes) | tidak ada venue live terverifikasi | tidak tersedia | tidak tersedia | tidak ter-listing (mint gratis 2026-11-08, strong lead; paid lane belum buka) |

## Listing aktif saat ini (ringkas)

- SAFU #3073 @ 0,0961 BNB (live 11 Nov — 1000× floor, reprice menunggu keputusan user); AlienID #3333 + #3684 @ 0,001 BNB; Brutes #3967 @ 0,000076 BNB; Hirelings #3927 + #4342 @ 0,00001 BNB (live 11 Nov); AgentsEstates #4611 @ 0,0035 BNB (expiry 2026-12-01T23:27:20Z; verifikasi on-chain 2026-11-06 ~07:56 WIB); Agent Periodic Lab O₂ #1021 @ 0,000171 BNB (LabMarket, fee 2%); Agent Cards #1720 @ 0,00001 BNB (live 11 Nov); TRACE Genesis #2256 @ 0,000495 BNB (market TRACE, fee 1%; list 2026-11-06 ~08:52 WIB, verifikasi on-chain). Total bila semua terjual ≈ 0,1024 BNB (sebelum fee market masing-masing).
