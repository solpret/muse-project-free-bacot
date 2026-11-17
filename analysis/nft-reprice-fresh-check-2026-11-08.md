# Cek Segar Floor NFT untuk Repricing — 2026-11-08 (Read-Only)

Tanggal cek: 2026-11-08 pagi WIB. Wallet agent: 0xeb237F6f9FB4e826739F0954e9768914F28b2c2E.
BNB: $695,32 (CoinGecko, saat cek). TIDAK ada transaksi, preview, sign, atau connect wallet dalam cek ini.

## Hasil per item (target = floor SEGAR)

| # | NFT | Harga kita sekarang | Floor SEGAR | Target reprice | Floor seller | Floor hold-verified? | Listing kita masih aktif? | Kepemilikan kita terverifikasi? |
|---|---|---|---|---|---|---|---|---|
| 1 | SAFU Bots #3073 | 0,0001425 BNB (142.500.000.000.000 wei) | **0,0000961 BNB (96.100.000.000.000 wei)** — token #2784 | **0,0000961 BNB** | 0x56bd77c00322e12a5df5cd0ae2237b90fc7436b2 | ✅ YA (ownerOf #2784 = penjual, blok 132291429) | ✅ YA — listings(3073) seller = agent, rank #12/66 | ✅ YA (ownerOf #3073 = agent) |
| 2 | Brutes #3967 | 0,000076 BNB (76.000.000.000.000 wei) | **0,000069 BNB (69.000.000.000.000 wei)** — token #1382/#1383/#1384/#2606/#2607 | **0,000069 BNB** | #1382: 0x5b9eb47a4bde9bda3eea5a7ad65650f51b75e649; #1383: 0x0fe1585d40627d691e55f349c8c49188eedf087c; #2606: 0x6957cf4c53a831088c09838acba03ee62d0974fa | ✅ YA (ownerOf #1382/#1383/#2606 = penjual, blok 132291429) | ✅ YA — listings(3967) seller = agent, rank #56/239 | ✅ YA (ownerOf #3967 = agent) |
| 3 | Hirelings #3927 | 0,000133 BNB (133.000.000.000.000 wei) | **0,00001 BNB (10.000.000.000.000 wei)** — 23 token di floor, a.l. #329/#330/#573 | **0,00001 BNB** | #329/#330: 0x816b881fe2c6d8190dd2f32ef34a2b6a7d0cdb21 (holder dari scan() — dibaca langsung dari _ownerOf) | ✅ YA (holder = _ownerOf saat scan) | ✅ YA — listing(3927) = 0,000133, rank #210/516 | ✅ YA (ownerOf #3927 = agent) |
| 4 | Hirelings #4342 | 0,000133 BNB (133.000.000.000.000 wei) | **0,00001 BNB** (floor sama) | **0,00001 BNB** | sama dengan #3927 | ✅ YA | ✅ YA — listing(4342) = 0,000133, rank #210/516 | ✅ YA (ownerOf #4342 = agent) |
| 5 | Agent Cards #1720 | 0,00085 BNB (850.000.000.000.000 wei) | **0,00001 BNB (10.000.000.000.000 wei)** — 6 token di floor: #568/#1651/#1934/#3667/#3670/#7831 | **0,00001 BNB** | #568: 0x507b806e18c79fbbe81137e8fffd41267d7c2ed4; #1651: 0x1e3fce24bf0214ecf1bdb28f7517eb58947e0d68 | ✅ YA (ownerOf #568/#1651 mengembalikan holder, blok 132291429) | ✅ YA — priceOf(1720) = 0,00085, rank #250/1.831 | ✅ YA (ownerOf #1720 = agent) |
| 6 | O2 #1021 (ERC-1155, LabMarket listingId 291) | 0,000171 BNB/unit (171.000.000.000.000 wei) | **0,00016 BNB/unit (160.000.000.000.000 wei)** — listingId 437/479/481/485 | **0,00016 BNB/unit** | 437: 0xc117bce178c8307ba2c2e9e54c9b00dcf30b237c; 479: 0xd3395d5ab0340a408249c301b9e81ae6d00d3e77; 481: 0xd724b21830f6a941ce20ecff26ebe81ef0258363; 485: 0xc8d65df5dd9ff0059d3cd917fbeceb2e234d6875 | ✅ YA (balanceOf id 1021 = 1 untuk keempat penjual, blok 132291429) | ✅ YA — getListing(291): seller = agent, id 1021, amount 1, available 1 | ✅ YA (balanceOf agent id 1021 = 1) |

### Apakah floor BERGERAK vs semalam (2026-11-07 ~23:02 WIB)?
- **SAFU: 0,0000961 BNB (96.100.000.000.000 wei).** Laporan semalam menulis 0,000096 — selisih 0,0000001 BNB (100.000.000.000 wei). Token floor (#2784) dan penjualnya SAMA dengan semalam. Tidak bisa dipastikan dari laporan semalam apakah ini pergerakan harga atau pembulatan tampilan 6 desimal di laporan itu (data mentah semalam di /tmp sudah hilang). Yang pasti: nilai segar yang terverifikasi langsung (multicall + eth_call langsung, blok 132291544) adalah **0,0000961 — dan itulah target repricing**.
- **Brutes, Hirelings, Agent Cards, O2: floor TIDAK bergerak** — nilai, token floor, dan penjual floor sama persis dengan semalam.
- Perubahan kecil lain: Agent Cards listing aktif 1.826 → **1.831** (rank kita #246 → #250); token floor baru #1651 muncul di harga floor. SAFU/Brutes/Hirelings/LabMarket jumlah listing aktif tidak berubah (66 / 239 / 516 / 396).

### Total (6 listing ini saja)
- Pada harga kita sekarang: 0,0015055 BNB (~$1,05).
- Pada floor segar: **0,0003551 BNB (~$0,25)**. Selisih −0,0011504 BNB bila semua terjual di floor.

## Fungsi cancel / (re-)list per market (discovery only — TIDAK ada preview/execute)

| Market | Cancel | (Re-)list | Approval baru untuk re-list? | Cancel+list 1 tx atau 2 tx? | Fee / batas harga |
|---|---|---|---|---|---|
| SAFU 0x85d03dc8e84fd6ed316beaec09538e8488fd0f59 (UNVERIFIED Sourcify — identifikasi dari dispatcher bytecode + OpenChain) | `cancel(uint256 tokenId)` sel 0x40e58ee5 | `list(uint256 tokenId, uint256 price)` sel 0x50fd7367 | TIDAK (getApproved #3073 = alamat market — approval per-token sudah aktif, bertahan sampai transfer) | **2 tx** (cancel → list). Apakah list() saja menimpa listing lama TANPA cancel — TIDAK terverifikasi dari bytecode (tanpa source); jalur aman = cancel dulu. Tidak ada fungsi gabungan. | Fee: TIDAK terverifikasi (tidak ada getter fee / MIN_PRICE / paused di dispatcher; kemungkinan hardcoded di buy() atau nol — tidak bisa dikonfirmasi dari bytecode). Ada error BadPrice() → list() kemungkinan menolak price 0; target 0,0000961 > 0, aman. Royalty ERC2981 ada (royaltyInfo) — besaran tidak dibaca. |
| Brutes 0x2199ea11ac7d11f5ef50c8d8e30c256b51bdbed4 (UNVERIFIED — dispatcher bytecode) | `cancel(uint256 tokenId)` sel 0x40e58ee5 | `list(uint256 tokenId, uint256 price)` sel 0x50fd7367 | TIDAK (getApproved #3967 = alamat market) | **2 tx** (cancel → list). Sama seperti SAFU: overwrite tanpa cancel TIDAK terverifikasi. | Fee: TIDAK terverifikasi (tidak ada getter fee / MIN_PRICE / paused di dispatcher). Market punya owner() + nft() (NFT = 0x44ab…). |
| Hirelings 0x6b1d77d3dede3fc775ca8c7bde08c2c2eaab9bea — market = kontrak NFT sendiri (Sourcify exact_match, source dibaca) | `unlist(uint256 id)` sel 0xbf5a4dd3 — hanya bila mau batal total; **TIDAK perlu untuk reprice** | `list(uint256 id, uint256 price)` sel 0x50fd7367 — **menimpa langsung** (listing[id] = price), syarat: marketOpen (✅ TRUE, dibaca segar), ownerOf == sender, price 0,00001–1000 ether | TIDAK ADA (market = kontrak NFT; token tidak pernah keluar dari owner sampai buy) | **1 tx** per token: list(id, floor) saja | Fee jual: MARKET_FEE_BPS = **200 (2%)**, dibaca on-chain. Harga min **0,00001 ether** — target 0,00001 PERSIS di minimum, diizinkan (>=). |
| Agent Cards 0x19f125dA1985033f102CA7746Cbd1F6f512CFACd — harga = kontrak NFT sendiri (Sourcify exact_match, source dibaca) | TIDAK ADA fungsi unlist/cancel listing (cancel(uint8) yang ada hanya untuk settings). Batal = `list(id, 0)` (price 0 = tidak ter-listing, buy() menolak price 0) | `list(uint256 id, uint256 price)` sel 0x50fd7367 — **menimpa langsung** (priceOf[id] = price), syarat: ownerOf == sender saja; tanpa cek min-price, tanpa cek pause | TIDAK ADA (market = kontrak NFT) | **1 tx**: list(1720, 0,00001 ether) | Fee jual: marketFeeBps = **250 (2,5%)**, dibaca on-chain, + royalti **5%** (per source: "2.5% ... on top of the 5% royalty"). |
| LabMarket (O2) 0xD69e644DD0DbC22cE20448E1F8646D95e097ccDd (Sourcify match, source dibaca) | `cancel(uint256 listingId)` sel 0x40e58ee5 — hanya bila mau batal total; **TIDAK perlu untuk reprice** | **`updatePrice(uint256 listingId, uint256 pricePerUnit)` sel 0x82367b2d — reprice 1 tx**: syarat seller == msg.sender, listing aktif (amount > 0), price > 0 dan ≤ uint128 max. Alternatif bila cancel dulu: `list(uint256 id, uint256 amount, uint256 pricePerUnit)` sel 0x19aeb490 | TIDAK untuk updatePrice. Untuk list() ulang: butuh isApprovedForAll(seller, market) — ✅ TRUE sudah aktif (dibaca segar) | **1 tx**: updatePrice(291, 0,00016 ether) | Fee jual: feeBps = **200 (2%)**, dibaca on-chain; MAX_FEE_BPS 500 (5%). |

### Rencana eksekusi (untuk parent — BUKAN dieksekusi di sini; tiap langkah tetap butuh preview bersih + konfirmasi per aturan)
1. SAFU #3073: cancel(3073) → list(3073, 96100000000000000 wei). 2 tx.
2. Brutes #3967: cancel(3967) → list(3967, 69000000000000 wei). 2 tx.
3. Hirelings #3927: list(3927, 10000000000000 wei). 1 tx.
4. Hirelings #4342: list(4342, 10000000000000 wei). 1 tx.
5. Agent Cards #1720: list(1720, 10000000000000 wei). 1 tx.
6. O2 listing 291: updatePrice(291, 160000000000000 wei). 1 tx.
Total **8 tx**. Tidak ada approval baru yang dibutuhkan di jalur mana pun (semua sudah aktif / tidak relevan).

## Status sesi baw (read-only)
- `baw wallet status --json` → **CONNECTED** (dicek ~06:40 WIB).
- `baw wallet address` → mengonfirmasi wallet agent 0xeb237F6f9FB4e826739F0954e9768914F28b2c2E di semua chain EVM.
- **Expiry TIDAK ditampilkan CLI** (`baw wallet status` hanya mengembalikan status CONNECTED; `baw auth verify` butuh qrCodeId — itu alur sign-in, bukan cek status). Catatan: dua pembacaan expiry yang tercatat sebelumnya bertentangan (2026-11-09 10:18 WIB vs 2026-11-10 01:23 WIB) — keduanya belum terverifikasi ulang; sesi terbukti hidup saat ini. TIDAK ada re-login / QR yang dimulai.

## Blok & cakupan
- Scan penuh: blok **132290881–132291149** (123 detik). SAFU 4.444/4.444, Brutes 5.555/5.555, Agent Cards 7.888/7.888, Hirelings 10.000/10.000 (via scan() view), LabMarket 396/396 listing aktif — **0 gagal baca, cakupan 100%**.
- Verifikasi listing + kepemilikan kita: blok 132287845. Verifikasi hold penjual floor: blok 132291429. Konfirmasi langsung SAFU #2784: blok 132291544.
- Data mentah: `~/workspace/nft-reprice-scan/` (safu_active.json, brutes_active.json, hirelings_active.json, agentcards_active.json, labmarket_active.json, scan_summary.json, verify_ours.json, verify_floors.json, scan2.py, scan2.log). ABI Sourcify: abi_0x6b1d….json, abi_0x19f1….json, abi_0xD69e….json.

## Catatan metode (penyimpangan dari laporan semalam — WAJIB dibaca parent)
- RPC publik BSC saat ini **menolak eth_call batch JSON-RPC >~10 call** dengan error -32005 "method eth_call in batch triggered rate limit" (terverifikasi langsung di ninicoin, binance.org, defibit). Batch 100-call dan 250-call semuanya gagal; batch 10-call lolos tapi lambat. Dua percobaan scan literal (chunk 250, lalu chunk 100) gagal total karena ini — keduanya dihentikan, tidak ada data setengah jalan yang dipakai.
- Sebagai gantinya, data yang SAMA diambil lewat **satu eth_call per 250 pembacaan ke Multicall3 kanonis 0xcA11bde05977b3631167028862bE2a173976CA11 (Sourcify exact_match) — tryAggregate(false, …)** di RPC publik yang sama. View yang dibaca, tokenId yang dicakup, dan sifat read-only-nya identik dengan metode semalam; hanya pembungkus transportnya yang berbeda. Decoding tervalidasi silang: harga listing kita sendiri (#3073 = 0,0001425 persis, #3967 = 0,000076 persis, #3927/#4342 = 0,000133 persis, #1720 = 0,00085 persis, O2 291 = 0,000171 persis) semuanya cocok dengan nilai yang sudah diketahui — jadi tidak ada kesalahan decode.
- Tambahan kendala sesaat: urllib Python sempat berulang RemoteDisconnected sementara curl ke URL yang sama normal (anomali transport urllib/proxy, bukan RPC-nya); beralih ke `requests` menyelesaikan. Multicall3 di BSC ini mengembalikan tryAggregate sebagai array saja (tanpa blockNumber) — decode disesuaikan dengan ABI Sourcify-nya, tervalidasi.

## Blocker
- **TIDAK ADA blocker untuk repricing.** Semua floor segar terverifikasi + penjual floor masih memegang token; semua listing kita masih aktif pada harga semalam; semua kepemilikan kita terverifikasi; market Hirelings terbuka (marketOpen=true); semua approval yang dibutuhkan sudah aktif; sesi baw CONNECTED.
- Peringatan (bukan blocker): (a) fee jual SAFU/Brutes TIDAK terverifikasi — net proceeds dari kedua itu tidak bisa dihitung pasti sebelum eksekusi; (b) untuk SAFU/Brutes, apakah list() saja menimpa listing lama belum terverifikasi — rencana 2-tx (cancel → list) adalah jalur amannya; (c) floor bisa bergerak lagi antara cek ini dan eksekusi — cek ulang floor segar sebelum eksekusi bila jedanya panjang.
