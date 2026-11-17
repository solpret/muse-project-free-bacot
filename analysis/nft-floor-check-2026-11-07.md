# Cek Floor NFT — Market Proyek Sendiri (On-Chain, Read-Only)

Tanggal cek: 2026-11-07 (malam WIB)
Wallet agent: 0xeb237F6f9FB4e826739F0954e9768914F28b2c2E
Blok saat scan: 132228192 (awal) – 132229079 (akhir)
BNB: $693,99 (DexScreener, saat cek)
Metode: eth_call batch ke BSC RPC publik (bsc-dataseed1.ninicoin.io, bsc-dataseed.binance.org, bsc-dataseed1.bnbchain.org, bsc-dataseed1.defibit.io). TIDAK ada sign, transaksi, approve, atau connect wallet. Element dan OpenSea TIDAK dipakai (terblokir tanpa API key) — tidak ada angka dari sana di laporan ini.
Kepemilikan diverifikasi ulang di blok 132227099 (ownerOf/balanceOf = wallet agent untuk semua NFT di bawah).

Definisi floor di laporan ini: harga listing AKTIF terendah yang tercatat on-chain di market proyek sendiri. Floor ikut diverifikasi: penjual floor dicek masih memegang tokennya (ownerOf/balanceOf) — kecuali DIGG, lihat catatan.

## Ringkasan

| NFT | Floor live (own market) | Listing kita | Selisih vs floor | Posisi listing kita |
|---|---|---|---|---|
| AlienID #3333 / #3684 | 0,001 BNB | 0,001 BNB | = floor (0%) | #1 dari 991 (seri floor) |
| SAFU Bots #3073 | 0,000096 BNB | 0,0001425 BNB | +0,0000465 (+48,4%) | #12 dari 66 |
| Brutes #3967 | 0,000069 BNB | 0,000076 BNB | +0,000007 (+10,1%) | #56 dari 239 |
| Hirelings #3927 / #4342 | 0,00001 BNB | 0,000133 BNB | +0,000123 (+1.230%) | #210 dari 516 |
| Agent Cards #1720 | 0,00001 BNB | 0,00085 BNB | +0,00084 (+8.400%) | #246 dari 1.826 |
| TRACE #2256 | 0,000495 BNB | 0,000495 BNB | = floor (0%) | #1 dari 73 |
| O2 #1021 (LabMarket) | 0,00016 BNB (id 1021) | 0,000171 BNB | +0,000011 (+6,9%) | #6 dari 25 (id 1021) |
| DIGG Copper id 2 | TIDAK ADA floor valid | tidak ter-listing (hold manual) | — | — |
| AgentsEstates #4611 | TIDAK BISA diverifikasi on-chain | 0,0035 BNB (order off-chain) | — | — |
| BOBBIE #4023 | — (belum ter-listing) | belum ter-listing | — | — |
| INKOI #712, NULLRAID #503, Vault-Crack #752, CRACK #792 | tidak ada own market | — | — | — |

Total kotor bila semua listing kita terjual pada harga kita sekarang: 0,0075005 BNB (~$5,21).
Total kotor bila semua terjual pada floor (tanpa AgentsEstates yang floornya tak terverifikasi, tanpa DIGG yang tak ada floor valid): 0,00285 BNB (~$1,98).

## 1. AlienID — market 0x8336317f0f05e840209c4f8f3d05f9fe8c045bc9

- NFT: 0xd12c42935f06b37337588b9169ba1593b534eb86, totalMinted 7.000 (totalSupply() revert — non-standar).
- Fungsi baca: listings(uint256) -> (seller, price, active). Scan penuh token 1–7.000 (7.000 call; 81 error baca awal, semua berhasil di-retry — cakupan 100%).
- Listing aktif: 991. Floor: 0,001 BNB (token #39, penjual 0x62a377b9f15e0dfea42a0ad451ab91ae58375516 — ownerOf terverifikasi masih pegang #39).
- 853 dari 991 listing aktif berada tepat di floor 0,001 BNB (86%). Harga lain paling umum: 0,005 (19), 0,002 (18), 0,0015 (15). Termahal 0,2 BNB (#3817).
- Listing kita: #3333 dan #3684 @ 0,001 BNB, seller = wallet agent, active = true. Keduanya PERSIS di floor — tidak ada listing yang lebih murah. Rank #1 (seri dengan 852 listing lain di harga yang sama).
- Catatan: AlienID #1 dan #2 tidak ter-listing (seller 0x0, price 0).

## 2. SAFU Bots — market 0x85d03dc8e84fd6ed316beaec09538e8488fd0f59

- NFT: 0x763aad3528b408bc42300dbab4ec755cde1d0192, totalSupply 4.444.
- Fungsi baca: listings(uint256) -> (seller, price) — 2 field saja (tanpa flag active; listing dianggap aktif bila seller != 0x0 dan price > 0). Ditemukan lewat curl langsung: panggilan awal gagal karena decoder mengharapkan 3 field. Scan penuh token 1–4.444 (0 error).
- Listing aktif: 66 — sama persis dengan listedCount() = 66 (konsisten).
- Floor: 0,000096 BNB (token #2784, penjual 0x56bd77c00322e12a5df5cd0ae2237b90fc7436b2 — ownerOf terverifikasi masih pegang #2784).
- 5 termurah: #2784 @ 0,000096; #2436 @ 0,0001; #3069 @ 0,0001; #3804 @ 0,000125; #4242 @ 0,000125. Termahal 0,1 BNB (3 token).
- Listing kita: #3073 @ 0,0001425 BNB, seller = wallet agent. 11 listing lebih murah, 54 lebih mahal — rank #12 dari 66. Di atas floor +48,4% (+0,0000465 BNB).
- Market ini juga punya sistem offer on-chain (getTokenOffers) — hasil cek offer terpisah: 0 offer untuk #3073.

## 3. Brutes — market 0x2199ea11ac7d11f5ef50c8d8e30c256b51bdbed4

- NFT: 0x44ab9f4687d5d6cd2454266b1e548552fb924908, totalSupply 5.555.
- Fungsi baca: listings(uint256) -> (seller, price) — 2 field, sama seperti SAFU. Scan penuh token 1–5.555 (0 error).
- Listing aktif: 239. Floor: 0,000069 BNB (token #1382, penjual 0x5b9eb47a4bde9bda3eea5a7ad65650f51b75e649 — ownerOf terverifikasi masih pegang #1382). 5 termurah semuanya @ 0,000069 (#1382, #1383, #1384, #2606, #2607).
- Harga paling umum: 0,00008 (33), 0,001 (25), 0,000074 (24), 0,00007 (21). Termahal 0,1 BNB (#1, #106).
- Listing kita: #3967 @ 0,000076 BNB, seller = wallet agent. 55 listing lebih murah, 177 lebih mahal — rank #56 dari 239. Di atas floor +10,1% (+0,000007 BNB).

## 4. Hirelings — market menempel di kontrak NFT 0x6b1d77d3dede3fc775ca8c7bde08c2c2eaab9bea

- NFT: 0x6b1d77d3dede3fc775ca8c7bde08c2c2eaab9bea, totalMinted 10.000 (totalSupply() revert — non-standar). ABI Sourcify exact_match (86 fungsi).
- KOREKSI ALAMAT: kunci Hirelings di ~/workspace/asset-sell-watch/markets.json tertulis 0x6b1d77d3dedefc775ca8c7bde08c2c2eaab9bea (41 karakter — TIDAK VALID, kekurangan satu karakter "3" setelah "dede"). Alamat benar: 0x6b1d77d3dede3fc775ca8c7bde08c2c2eaab9bea (terverifikasi via Ankr getNFTsByOwner: HIRELING #3927 dan #4342).
- Fungsi baca: listing(uint256) -> uint256 (harga langsung; 0 = tidak ter-listing). Scan penuh token 1–10.000 (0 error).
- Listing aktif: 516. Floor: 0,00001 BNB (token #329 — ownerOf terverifikasi masih pegang #329). 23 token di harga floor 0,00001.
- Harga paling umum: 0,001 (30), 0,00001 (23), 0,0005 (22). Ada 2 listing absurd @ 1.000 BNB (#7699, #7700). Termahal wajar lain: 1 BNB (#4548, #4549).
- Listing kita: #3927 dan #4342 @ 0,000133 BNB. 209 listing lebih murah, 305 lebih mahal — rank #210 dari 516. Di atas floor +1.230% (+0,000123 BNB, 13,3x floor).

## 5. Agent Cards — harga menempel di kontrak NFT 0x19f125dA1985033f102CA7746Cbd1F6f512CFACd

- NFT: 0x19f125dA1985033f102CA7746Cbd1F6f512CFACd, totalSupply 7.888. ABI Sourcify exact_match (83 fungsi).
- Fungsi baca: priceOf(uint256) -> uint256 (0 = tidak ter-listing). Scan penuh token 1–7.888 (2 error baca awal, semua berhasil di-retry — cakupan 100%).
- Ter-listing (price > 0): 1.826. Floor: 0,00001 BNB (token #568 — ownerOf terverifikasi masih pegang #568; juga #1934, #3667, #3670, #7831 di harga yang sama).
- 10 termurah: #568, #1934, #3667, #3670, #7831 @ 0,00001; #3697 @ 0,00002; #1114 @ 0,00003; #1445, #2438 @ 0,000035; #5323 @ 0,000069.
- Harga paling umum: 0,01 (166), 0,005 (142), 0,002 (94), 0,001 (83), 0,02 (60). Termahal 1 BNB (#803, #1330).
- Listing kita: #1720 @ 0,00085 BNB. 245 listing lebih murah, 1.576 lebih mahal — rank #246 dari 1.826. Di atas floor 85x (+0,00084 BNB).
- Catatan perubahan harga: #99 yang pada 2026-11-03 tercatat 0,02 BNB kini 0,004 BNB; #798 tetap 0,02 BNB; #116 @ 0,1 BNB; #1 @ 0,15 BNB.

## 6. TRACE Genesis — market 0x30cAc2eA33fA5B06EDC44fF01f9B8c768D8DFEB3

- NFT: 0xe5e2c43746f3a5e713c246592095d7cf82e808cc, totalSupply 2.728.
- Fungsi baca: listings(uint256) -> 5 field (seller, price, +3 field lain). Scan penuh token 1–2.728 (0 error).
- Listing aktif: 73. Floor: 0,000495 BNB — dan itu LISTING KITA SENDIRI (#2256, seller = wallet agent, ownerOf terverifikasi). Rank #1 dari 73, tidak ada yang lebih murah.
- 5 termurah: #2256 @ 0,000495 (kita); #2635 @ 0,0005; #2620 @ 0,00093; #2623 @ 0,00093; #2077 @ 0,00094.
- Harga paling umum: 0,00095 (16), 0,001 (15). Termahal 1,43887 BNB (#2117).

## 7. Agent Periodic Lab O2 — LabMarket 0xD69e644DD0DbC22cE20448E1F8646D95e097ccDd

- NFT: 0xfe5ab5ce9b1d86a55d70e7d0573a14d559029c18 (ERC-1155, token id 1021, balance wallet agent = 1). ABI Sourcify match (24 fungsi).
- Fungsi baca: getActiveListings(offset, limit) -> (ids, items[seller, id, amount, pricePerUnit, createdAt], available). activeCount() = 391 saat cek awal; enumerasi mengembalikan 392 listing (1 listing baru muncul selama scan).
- Total listing aktif di market: 392, mencakup 28 token id berbeda. Floor keseluruhan market: 0,00013 BNB (token id 1005, listingId 170).
- Khusus id 1021 (O2 kita): 25 listing. Floor id 1021: 0,00016 BNB (4 listing: listingId 437, 479, 481, 485). Penjual floor listingId 437 (0xc117bce178c8307ba2c2e9e54c9b00dcf30b237c) terverifikasi masih memegang 1 unit id 1021.
- Listing kita: listingId 291, seller = wallet agent, id 1021, amount 1, price 0,000171 BNB, available 1. 5 listing id 1021 lebih murah (4 @ 0,00016 + 1 @ 0,00017) — rank #6 dari 25. Di atas floor id 1021 +6,9% (+0,000011 BNB).
- Token id lain yang paling banyak ter-listing: id 1006 (47), id 1001 (45), id 1005 (44), id 1003 (42), id 1014 (42).

## 8. DIGG Copper (id 2) — market 0xA66BC88D14543c11044F9876471738FAc5BD637e

- NFT: 0xb6407991b76e712d15edef06e125abcc730364f7 (ERC-1155, id 2 = Copper, balance wallet agent = 1). Market ABI Sourcify match (23 fungsi).
- Fungsi baca: listings(listingId) -> (seller, collection, tokenId, amount, price, is1155, active). nextListingId() = 282 — enumerasi penuh listingId 0–281 (0 error).
- Listing untuk Copper id 2: 52 total, 37 aktif. Harga nominal terendah aktif: 0,25 BNB (listingId 93).
- TEMUAN PENTING: SEMUA 37 listing aktif Copper adalah BASI — penjualnya sudah tidak memegang token id 2 (balanceOf = 0 untuk ke-37 penjual, dicek satu per satu; fungsi balanceOf terverifikasi bekerja karena balance wallet agent sendiri terbaca 1). 8 termurah yang dicek dulu: listingId 93 @ 0,25; 127 @ 0,29; 172/186/193 @ 0,35; 18 @ 0,37115; 157/36 @ 0,38115 — semuanya saldo 0.
- KESIMPULAN: DIGG Copper TIDAK PUNYA floor yang valid di market sendiri — tidak ada satu pun listing aktif yang bisa dibeli (pembelian akan gagal karena penjual tidak memegang token). Angka 0,25 BNB hanyalah harga listing basi terendah, bukan floor yang bisa dieksekusi.
- Listing kita: TIDAK ADA (DIGG hold manual — sesuai aturan, tidak di-listing).
- Total listing aktif di market DIGG (semua koleksi/tier): 215.

## 9. AgentsEstates #4611 — market 0x1EeA3629C7505Dcf8c8d247558F6E244D19C60dE

- NFT: 0x439643cfd023c247519518b7f73d06823e1f2fce, totalSupply 6.665. Market ABI Sourcify exact_match (23 fungsi) — market berbasis orderbook EIP-712 OFF-CHAIN.
- Floor TIDAK BISA diverifikasi on-chain: tidak ada fungsi view yang mengembalikan daftar listing; offer/order hanya ada di server proyek (halaman agentsestates.app/nft/4611 mengembalikan 403 dari sini; Element/OpenSea terblokir tanpa API key).
- Status order kita (on-chain, blok 132227237): nonceUsed(wallet agent, nonce 1793575640096485677) = false — order BELUM terpakai/terisi; paused() = 0 (market tidak pause). Harga order kita 0,0035 BNB, expiry 2026-12-01.
- Yang bisa dikatakan: order kita masih valid dan belum terjual. Floor market ini TIDAK DIKETAHUI dari data on-chain — jangan pakai angka dari sumber tak terverifikasi.

## 10. BOBBIE #4023 — BELUM TER-LISTING

- NFT: 0x3BF121dC4c5a1Ba567F3eE801d0e447601726207. Market proyek sendiri: BobbieMarketV4 0xfA239D919Db60E1b497E9E8CA26CA79689a180AF (ABI Sourcify exact_match).
- listings(4023) = kosong (seller 0x0, price 0, version 0). saleFinalized() = 0 (false) — sale belum finalized, transfer masih terkunci. Status dicatat, BUKAN floor.
- Pantauan listing otomatis @ 0,0075 BNB tetap berjalan via cron bobbie-listing-watch (akan approve satu token + list sesudah saleFinalized = true).

## 11. Tanpa own market terverifikasi — TIDAK ADA floor

- INKOI #712 (0xbd4B4e7189ae9356514664146b0eD683601200A9, totalSupply 858)
- NULLRAID First Breach #503 (0xdEC01cDfb41E7871FB7Ca7B12B1572cE292743C0, totalSupply 758)
- Vault-Crack #752 (0x1a7a8BbB49e3e8Cf951996789Fd69d4C7524A2B4, totalSupply 4.023)
- CRACK #792 (0xaea1433dbd9e7ede0914d996c2dad692e6e01e09, totalSupply 3.537)
- Keempatnya tidak punya market proyek sendiri yang terverifikasi — satu-satunya jalur jual adalah Element/OpenSea (keduanya terblokir tanpa API key), jadi floor tidak bisa diverifikasi. Bukan berarti nilainya nol — hanya tidak ada harga pasar on-chain yang bisa dibaca.

## Catatan metode & batasan

- Cakupan scan: AlienID 7.000, SAFU 4.444, Brutes 5.555, TRACE 2.728, Agent Cards 7.888, Hirelings 10.000, DIGG 282 listingId, LabMarket 392 listing aktif. Total ~37.900 eth_call + verifikasi lanjutan. Error baca awal (AlienID 81, Agent Cards 2) semuanya berhasil di-retry — cakupan akhir 100% untuk semua koleksi.
- Floor = listing aktif terendah tercatat on-chain; penjual floor diverifikasi masih memegang token (kecuali DIGG — semua basi, lihat bagian 8). Listing bisa berubah sewaktu-waktu; angka ini snapshot blok 132228192–132229079.
- Listing "aktif" dihitung dari data market (seller != 0 dan price > 0, plus flag active bila ada). Listing basi (penjual sudah tidak pegang token) HANYA dicek untuk floor tiap koleksi dan untuk seluruh Copper DIGG — listing lain di atas floor tidak dicek satu per satu kepemilikannya, jadi ada kemungkinan sebagian listing di atas floor juga basi.
- SAFU dan Brutes: listings() mengembalikan 2 field (seller, price) tanpa flag active — ditemukan lewat curl langsung setelah decoder 3-field gagal. Brutes dan SAFU TIDAK terverifikasi di Sourcify; fungsi diidentifikasi dari dispatcher bytecode (selector listings(uint256) = 0xde74e57b ada di keduanya) + hasil call langsung.
- Data scan mentah (per tokenId) tersimpan sementara di /tmp/floor_scan/ (alienid.json, safu.json, brutes.json, trace.json, agentcards.json, hirelings.json, digg.json, labmarket.json) — /tmp tidak persisten; bila perlu arsip, salin ke ~/workspace.
- Laporan cek offer terpisah: ~/workspace/nft-offer-check-2026-11-07.md (0 offer live terverifikasi).
