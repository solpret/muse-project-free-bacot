# Cek Offer NFT — 2026-11-07 ~22:35 WIB (READ-ONLY)

Pertanyaan user: "Cek NFT kita apakah ada offer yang bisa kita terima?"
Hasil singkat: **TIDAK ADA offer live yang terverifikasi di venue mana pun yang bisa dicek.** Nol offer. Yang tidak bisa dicek: Element, OpenSea, dan offer off-chain AgentsEstates #4611 (ketiganya terblokir aksesnya, lihat bawah).

## 1. Kepemilikan live (blok 132222695, RPC ninicoin)

Semua NFT ter-listing + paling bernilai MASIH dimiliki wallet agent 0xeb237F6f9FB4e826739F0954e9768914F28b2c2E (ownerOf live):

- AgentsEstates #4611 — YA
- AlienID #3333, #3684 — YA
- SAFU Bots #3073 — YA
- Brutes #3967 — YA
- Hirelings #3927, #4342 — YA
- Agent Cards #1720 — YA
- TRACE #2256 — YA
- INKOI #712 — YA
- BOBBIE #4023 — YA
- NULLRAID #503 — YA
- Vault-Crack #752 — YA (kontrak 0x1a7a8BbB49e3e8Cf951996789Fd69d4C7524A2B4)
- CRACK #792 — YA (kontrak 0xaea1433dbd9e7ede0914d996c2dad692e6e01e09, terverifikasi di 2 RPC)
- Agent Periodic Lab O2 #1021 — balanceOf 1 (ERC-1155)
- DIGG Copper Ore id 2 — balanceOf 1 (ERC-1155)

KOREKSI KONTRAK CRACK: CRACK #792 ternyata BUKAN di kontrak Vault-Crack #752 (0x1a7a8BbB49e3e8Cf951996789Fd69d4C7524A2B4). Receipt mint tx 0xf3c1478fc8f66b3dc669a18858fb8e321c65e843f121f3607686854e8de2e41a menunjukkan `to` = 0xaea1433dbd9e7ede0914d996c2dad692e6e01e09, dan ownerOf(792) di kontrak itu = wallet agent (2 RPC). Token #792 di kontrak 0x1a7a... justru milik 0x9884e8b7e2c436ebc53bf4e3dc01e5de1b5282c8 (bukan kita). Kemungkinan redeploy/kontrak berbeda untuk mint 06 Nov — perlu rekonsiliasi bila inventaris mencatat keduanya di kontrak yang sama.

## 2. Sistem offer per venue (cek ABI Sourcify + bytecode)

| Venue / kontrak market | Ada sistem offer? | Hasil cek live |
|---|---|---|
| AlienID market 0x8336317f0f05e840209c4f8f3d05f9fe8c045bc9 (alamat baru ditemukan via getApproved #3333/#3684) | TIDAK — Sourcify exact_match, 11 fungsi: list/buy/cancel/listings saja | — (tidak mungkin ada offer) |
| SAFU market 0x85d03dc8e84fd6ed316beaec09538e8488fd0f59 (alamat baru via getApproved #3073) | YA — makeOffer, tokenOffer, getTokenOffers, acceptOffer, cancelOffer, + collection offers (analisis selector bytecode + OpenChain) | getTokenOffers(3073) = KOSONG (2 array kosong, terverifikasi di ninicoin + binance.org); getCollectionOffers(0,10) = KOSONG (2 RPC). **0 offer.** Market hidup: listedCount 66 |
| Brutes market 0x2199ea11ac7d11f5ef50c8d8e30c256b51bdbed4 (via getApproved #3967) | TIDAK teridentifikasi — hanya list/buy/cancel/listings (+Ownable). 6 konstanta PUSH4 tidak dikenal di OpenChain maupun 4byte.directory | — |
| Hirelings (market nempel di kontrak NFT) | TIDAK — list/buy/listing/unlist saja, tanpa offer (Sourcify exact_match, 86 fungsi) | — |
| Agent Cards (market nempel di kontrak NFT) | TIDAK — list/buy/cancel saja, tanpa offer (exact_match, 83 fungsi) | — |
| TRACE market 0x30cAc2eA33fA5B06EDC44fF01f9B8c768D8DFEB3 | TIDAK teridentifikasi — list/buy/cancel/listings + fee/proceeds saja. 10 konstanta PUSH4 tidak dikenal (sebagian jelas fragmen string ASCII, bukan selector) | — |
| AgentsEstates market 0x1EeA3629C7505Dcf8c8d247558F6E244D19C60dE (EIP-712 orderbook) | YA tapi OFF-CHAIN — acceptOffer, offerDigest, OFFER_TYPEHASH; offer berupa signed order di backend proyek, tidak bisa dibaca on-chain. isApprovedForAll(agent, market) = true | TIDAK BISA DIVERIFIKASI: halaman agentsestates.app/nft/4611 mengembalikan 403 dari sini |
| LabMarket (O2) 0xD69e644DD0DbC22cE20448E1F8646D95e097ccDd | TIDAK — Sourcify match, 24 fungsi: list/buy/cancel/updatePrice/getListing saja | — |
| BobbieMarketV4 0xfA239D919Db60E1b497E9E8CA26CA79689a180AF | YA, on-chain — placeOffer, offers, acceptOffer, cancelOffer, nextOfferId | nextOfferId = 1; offer#0 kosong/nonaktif. **0 offer aktif untuk #4023 (belum pernah ada offer)** |
| DIGG market 0xA66BC88D14543c11044F9876471738FAc5BD637e | YA, on-chain bids — placeBid721/1155, bids, nextBidId | nextBidId = 2; bid#1 (tier 1, 0,39 BNB, bidder 0xe5b4a396ee65993c91b8d7278b45bce868605b45) NONAKTIF, remaining 0. **0 bid aktif untuk DIGG Copper tier 2** |
| ACATMarket 0x3424De685702E8d63BaAC20BB67d1a205db89427 | TIDAK — list/buy/cancel saja | ACAT #1817 juga tidak ter-listing (hold user) |
| Lumen market 0xcA67924b905e89f98651E2d9FF69bBA2fbb9cF73 | ABI tidak terverifikasi di Sourcify | #2321 tidak ter-listing; market dulu tanpa listing live — tidak dienumerasi |

## 3. Aggregator / venue luar

- Element API — TERBLOKIR. Path benar GET /openapi/v1/orders/list mengembalikan 400 {"status":400,"error":"Bad Request","message":"Missing Header: X-api-key"}. Semua request butuh header x-api-key; tidak ada jalur anonim. (Path salah /openapi/v1/order/list dan /asset/list mengembalikan 404.)
- OpenSea API v2 — TERBLOKIR. /api/v2/offers/collection/... mengembalikan {"errors":["Missing an API Key, which is required for this request."]}
- tofuNFT / PancakeSwap NFT API — tidak ada respons dari sini (curl kosong). Tidak dicek per-item; PCS NFT market juga hanya melayani koleksi PCS sendiri, bukan koleksi free-mint ini.
- INKOI, NULLRAID, CRACK, Vault-Crack: tidak ada own market terverifikasi → satu-satunya jalur offer adalah Element/OpenSea (keduanya terblokir di atas).

## 4. Daftar offer LIVE yang ditemukan

Tidak ada. 0 offer aktif di semua venue yang bisa diverifikasi on-chain (SAFU #3073, BOBBIE #4023, DIGG tier 2).

## 5. Rekomendasi

- Tidak ada offer untuk diterima — tidak ada aksi.
- Satu-satunya blind spot yang penting: **AgentsEstates #4611** (listing tertinggi, 0,0035 BNB) — marketnya mendukung offer off-chain (EIP-712) yang tidak terlihat dari chain. Bila user mau memastikan, cek manual di browser pada halaman aset agentsestates.app / element.market (user connect wallet, lihat tab Offers), atau sediakan Element x-api-key (minta di element.market / api@element.market) supaya cek Element bisa otomatis.
- SAFU #3073 punya sistem offer on-chain yang hidup — bila nanti ada yang menawar, bisa dicek kapan saja via getTokenOffers(3073) tanpa key.
- Harga listing pembanding (terakhir terverifikasi 2026-11-06): AgentsEstates 0,0035; AlienID 0,001; SAFU 0,0001425; Brutes 0,000076; Hirelings 0,000133; Agent Cards 0,00085; TRACE 0,000495; O2 0,000171. Total kotor bila semua terjual ±0,0076 BNB.

## 6. Catatan tooling

- fast_rpc.race() gagal di sesi ini (semua endpoint gagal — kemungkinan health file basi); semua baca on-chain dilakukan via curl mentah ke bsc-dataseed1.ninicoin.io dan bsc-dataseed.binance.org, berhasil.
- Alamat market baru yang ditemukan dari getApproved (belum ada di markets.json): AlienID 0x8336317f0f05e840209c4f8f3d05f9fe8c045bc9, SAFU 0x85d03dc8e84fd6ed316beaec09538e8488fd0f59, Brutes 0x2199ea11ac7d11f5ef50c8d8e30c256b51bdbed4. Sebaiknya dicatat ke markets.json oleh parent bila dianggap berguna.
- NFT wallet utama (0xcf3c...) tidak dicek live satu per satu — tidak ada yang ter-listing di own market, jadi jalur offer-nya hanya Element/OpenSea (terblokir).
