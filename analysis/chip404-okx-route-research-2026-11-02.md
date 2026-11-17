# Riset Rute Eksekusi Pembelian 2 NFT Chip404 di OKX

**Tanggal riset:** 2026-11-02, pemeriksaan ulang terakhir ~20:07 WIB
**Sifat:** READ-ONLY. Tidak ada signing, approval, pembelian, transfer, atau koneksi wallet yang dilakukan dalam riset ini.
**Status persetujuan user:** pembelian #2560 + #107 di OKX SUDAH disetujui user (19:45 WIB). Yang tertahan hanya rute eksekusinya.

---

## VONIS DI ATAS: belum ada rute yang bisa dieksekusi dari VM ini

**Satu-satunya data yang hilang adalah signature penjual (bytes tanda tangan) untuk kedua order.** Semua komponen lain — parameter order lengkap, kontrak protokol, conduit, approval penjual, harga, masa berlaku — sudah ditemukan dan terverifikasi on-chain maupun dari API publik OKX.

API publik OKX (halaman item, `detail-info`, `multi-listings`, `batch/multi-listings`) **sengaja mengosongkan field signature** (`"signature": ""`). Tanpa signature itu, `fulfillOrder` di kontrak Seaport OKX PASTI revert (terbukti lewat simulasi `eth_call`, lihat §5). Signature hanya diserahkan OKX lewat jalur buy yang butuh sesi login — dan kedua jalur buy yang ditemukan gagal dari VM tanpa sesi:

- `POST /priapi/v1/nft/me/instructions/buy-now` → menolak dengan `"This collection isn't available for trade"` untuk semua variasi body yang dicoba.
- `POST /priapi/v1/nft/trading/buy` → HTTP 500 `"unknown inner error"` untuk semua variasi body yang dicoba (konsisten dengan endpoint yang butuh sesi login, atau payload yang belum tepat — tidak bisa dibedakan dari VM).

**Jadi laporan ini adalah hasil negatif yang jujur untuk eksekusi anonim, PLUS peta jalan eksekusi yang lengkap seandainya signature didapat (§8) dan dua fallback yang nyata (§9). Tidak ada rute karangan di sini.**

---

## 1. Target: kedua order MASIH LIVE saat pemeriksaan terakhir (~20:07 WIB)

Dikonfirmasi lewat DUA sumber independen yang sama-sama mengembalikan ordernya: halaman item OKX (SSR) dan API publik `GET /priapi/v1/nft/order/multi-listings` (code 0).

| | #2560 | #107 |
|---|---|---|
| Koleksi | Chip404 `0xAB6b18C626daaDd1ff7Cc45F402141153a5a9759` (BSC 56, ERC-721) | sama |
| Grade (dari riset parent) | Cyan (tier 1) | Cyan (tier 1) |
| Penjual (offerer = owner on-chain) | `0x000003d7424c35a79704c3bba5b9825d8533228e` | `0x1c4a529aa5d3c5e77191cbfd6cca082b3a5dc7a7` |
| Harga listing | **0,0006 BNB** | **0,00078 BNB** |
| Total | 0,00138 BNB + gas (lihat koreksi BNB vs WBNB di §4) | |
| OKX order id | 8831833188 | 8831829092 |
| OKX nftId | 62139217408436057 | 62117381438187353 |
| OKX orderHash | `0xecdc97c52adb46a1a379814327c71dcd396a9f480a95e861a43b753d13d67bbf` | `0x3368f8f4eb8ca2a581641f81fc73ae454038e8c93b42f6b306b7e0d2353f6a49` |
| Sumber order | OKX (source 4, sourceName "OKX") | sama |
| Masa berlaku order | 2026-11-02 19:33:06 WIB s/d **2026-11-09 19:32:54 WIB** | 2026-11-02 19:16:27 WIB s/d **2026-11-09 19:15:55 WIB** |
| Halaman OKX | https://web3.okx.com/id/nft/asset/bsc/0xab6b18c626daadd1ff7cc45f402141153a5a9759/2560 | https://web3.okx.com/id/nft/asset/bsc/0xab6b18c626daadd1ff7cc45f402141153a5a9759/107 |

**Peringatan:** listing bisa dibatalkan penjual kapan saja dan harga bisa berubah. Parent WAJIB membaca ulang order lewat `multi-listings` tepat sebelum eksekusi apa pun; angka di laporan ini adalah potret ~20:07 WIB, bukan kunci harga.

---

## 2. Protokol order: OKX Seaport fork (BUKAN Seaport kanonik, BUKAN Element, BUKAN OpenSea)

Bukti, bukan tebakan:

- **Kontrak protokol:** `0x0000000000000068f116a894984e2db1123eb395` (field `protocolAddress` di order OKX, sama untuk kedua token).
- **Terverifikasi di Sourcify** (BSC 56) — ABI lengkap diambil dari `https://sourcify.dev/server/v2/contract/56/0x0000000000000068f116a894984e2db1123eb395?fields=abi`. Constructor-nya menerima `conduitController`; `information()` mengembalikan **versi "1.6"**, domainSeparator `0x81c117ec5faefe0c9a3702715a3f7a0adc8ec4255bfc447755cbabe0877aa3eb` (cocok dengan hitungan EIP-712 `EIP712Domain("Seaport","1.6",56,protocol)`), dan conduitController `0x00000000f9490004c11cef243f5400493c00ad63` (controller milik OKX, BUKAN controller Seaport kanonik).
- **Bukan Seaport kanonik** `0x00000000000000ADc04C56Bf30aC9d3c0AaA15cA`: alamat protokolnya berbeda, dan — yang paling penting — **varian ini TIDAK punya field `counter` di struct OrderParameters** (11 field, bukan 12) dan **`fulfillOrder`-nya hanya 2 argumen, tanpa argumen `recipient`**.
- **Bukan Element:** field `elementOrderParam` = null di kedua order; sumber order = OKX (source 4). ElementEx `0xb3e3DfCb2d9f3DdE16d78B9e6EB3538Eb32B5ae1` tidak terlibat di order ini.
- **Bukan OpenSea/Seaport kanonik:** field `seaportOrderParam` = null; yang terisi hanya `okxSeaportOrderParam`.

Fungsi eksekusi (dari ABI Sourcify, diverifikasi programatik):

```
fulfillOrder(
  ( OrderParameters parameters, bytes signature ),  // Order
  bytes32 fulfillerConduitKey
) payable
```

dengan `OrderParameters` = `(offerer, zone, offer[], consideration[], orderType, startTime, endTime, zoneHash, salt, conduitKey, totalOriginalConsiderationItems)` — **tanpa `counter`**.

**Selector `fulfillOrder` = `0xb3a34c4c`** (dihitung dari signature kanonik ABI, BUKAN dari Seaport kanonik yang 3-argumen). Karena tidak ada argumen `recipient`, **NFT otomatis terkirim ke caller (msg.sender = wallet pembeli)**. `fulfillerConduitKey` diisi `0x0...0` (pembeli membayar BNB native, tidak memakai conduit).

---

## 3. Parameter lengkap kedua order (dari API publik OKX, cocok dengan SSR halaman item)

### #2560 — harga 0,0006 BNB

- offerer: `0x000003d7424c35a79704c3bba5b9825d8533228e`
- zone: `0xdf2d4bffec010debd302674c9fb9cda99bb5e852`, zoneHash: `0x0...0`
- orderType: **2 (FULL_RESTRICTED)** — artinya zone HARUS menyetujui order saat fulfill (lihat §10, belum teruji)
- offer: 1 × ERC-721 (itemType 2) Chip404 tokenId 2560
- consideration (token = `0x0...0` = **BNB native**, BUKAN WBNB):
  - 594000000000000 wei = **0,000594 BNB → penjual**
  - 6000000000000 wei = **0,000006 BNB (1%) → fee `0x2a6f4608647feef2b0aeb540008a8038325aaabf`**
  - Total persis 0,0006 BNB
- salt: `75709917772491462883404595467616030100461711290482812024345901971726251996682`
- conduitKey: `0x0000007b02230091a7ed01230072f7006a004d60a8d4e71d599b8104250f0000`
- totalOriginalConsiderationItems: 2
- **signature: `""` (KOSONG di semua sumber publik)**

### #107 — harga 0,00078 BNB

- offerer: `0x1c4a529aa5d3c5e77191cbfd6cca082b3a5dc7a7`
- zone, zoneHash, orderType, conduitKey, totalOriginalConsiderationItems: sama seperti #2560
- offer: 1 × ERC-721 (itemType 2) Chip404 tokenId 107
- consideration (BNB native):
  - 772200000000000 wei = **0,0007722 BNB → penjual**
  - 7800000000000 wei = **0,0000078 BNB (1%) → fee `0x2a6f4608647feef2b0aeb540008a8038325aaabf`**
  - Total persis 0,00078 BNB
- salt: `90852125959116138091732715246248682012106816140322697312886475265077119714729`
- **signature: `""` (KOSONG di semua sumber publik)**

---

## 4. Yang SUDAH terverifikasi on-chain (bukan dari tampilan web saja)

1. **Approval conduit penjual = AKTIF untuk kedua penjual.** Conduit untuk key di atas (via `ConduitController.getConduit`) adalah `0x1e0049783f008a0085193e00003d00cd54003c71` (exists = true). `isApprovedForAll(penjual, conduit)` = true untuk kedua penjual. Sebaliknya `isApprovedForAll(penjual, protocol)` = false untuk keduanya — jadi transfer NFT penjual HANYA bisa lewat conduit, dan itu sudah siap. (Ini juga membuktikan resolusi conduit saya benar: penjual memberi approval ke conduit itu persis saat listing di OKX.)
2. **Counter penjual = 0** untuk keduanya (konsisten dengan order; varian ini tidak memakai counter di struct, tapi `getCounter` tetap ada dan bernilai 0).
3. **Penjual #2560 adalah akun EIP-7702**: `eth_getCode` = `0xef0100490aac77c960b0569c8e446ac7e12490bd44ca1d` (delegasi ke `0x0490aac77c960b0569c8e446ac7e12490bd44ca1d`). Konsekuensinya: signature-nya akan diverifikasi lewat EIP-1271 (`isValidSignature` di akun itu), bukan ECDSA biasa. Ini transparan bagi pembeli — signature yang sama tinggal diteruskan ke `fulfillOrder` — tapi menjelaskan error simulasi yang berbeda (§5). Penjual #107 adalah EOA biasa (code `0x`).
4. **KOREKSI PENTING soal mata uang: pembeli membayar BNB NATIVE, bukan WBNB.** Halaman OKX menampilkan label "WBNB", tapi consideration di order memakai token `0x0...0` (native). Jadi: **tidak perlu wrap BNB→WBNB dan tidak perlu approve apa pun dari sisi pembeli** — cukup kirim `value` = harga + gas. (Fee 1% sudah termasuk di dalam harga, dibayar dari consideration, bukan biaya tambahan di atas harga.)
5. **Masa berlaku order** masih jauh (±9 November 2026, §1), dan order belum terisi (simulasi dan status on-chain konsisten dengan order yang masih terbuka; pembatalan sewaktu-waktu tetap mungkin — verifikasi ulang wajib).

---

## 5. Simulasi `eth_call`: bukti bahwa signature adalah satu-satunya yang hilang

Saya membangun calldata `fulfillOrder` persis dari parameter §3 (encoding `eth_abi`, selector `0xb3a34c4c` dari ABI) dan mensimulasikannya dari wallet user dengan `value` = harga, via `eth_call` (read-only, tidak mengubah state):

- **#2560 → revert `0x4f7fb80d` = `BadContractSignature()`** (cabang EIP-1271 untuk penjual akun 7702).
- **#107 → revert `0x8baa579f` = `InvalidSignature()`** (cabang ECDSA untuk penjual EOA).

Kedua error ini adalah error VALIDASI SIGNATURE dari kontrak Seaport — artinya encoding dan selector saya sudah benar (kontrak berhasil mem-parsing order dan mencapai tahap cek signature, bahkan membedakan cabang EOA vs kontrak sesuai jenis penjual). Dengan signature kosong, order ini tidak akan pernah lolos. Dengan signature penjual yang valid, simulasi yang sama adalah tes pertama yang harus diulang parent sebelum preview baw.

**Catatan kejujuran tentang satu percobaan awal yang salah:** percobaan simulasi pertama saya memakai struct 12-field (dengan `counter`, meniru Seaport kanonik) dan revert dengan data kosong `0x` — itu murni kesalahan encoding saya, BUKAN bukti apa pun. Setelah struct diperbaiki ke 11-field varian OKX, revert-nya menjadi dua error signature spesifik di atas. Percobaan pertama itu saya abaikan sepenuhnya.

---

## 6. Endpoint frontend OKX yang BENAR (ditemukan dari bundle JS, bukan tebakan)

Sumber: chunk `okfe/defi-mode/4199/index.a3cb7c9d.js` (modul konstanta API, base `n = "/priapi/v1/nft"`), dikonfirmasi lewat pemakaian di chunk `7344` (modul API market). Semua endpoint di bawah ini BENAR-BENAR ADA (merespons JSON terstruktur, bukan 404):

| Endpoint | Metode | Hasil dari VM (anonim) |
|---|---|---|
| `GET /priapi/v1/nft/detail-info?chain=56&contractAddress=…&tokenId=…` | GET | code 0, data item lengkap, **tanpa sellOrders dan tanpa signature** |
| `GET /priapi/v1/nft/order/multi-listings?chain=56&contractAddress=…&tokenId=…&ownerAddress=…&nftId=…&supportSeaport=true` | GET | code 0, order lengkap, **`signature: ""`** (param `ownerAddress` dan `nftId` (OKX id) WAJIB; tanpa keduanya error 400 memandu param) |
| `POST /priapi/v1/nft/batch/multi-listings` `{chain, nftIds, ownerAddress}` | POST | code 0, data market/currency, **tanpa signature** |
| `POST /priapi/v1/nft/order/query/order/data` `{orderIdList: […]}` | POST | `"Unsupported the orders."` untuk kedua order id ini (param `orderIdList` benar, tapi order Seaport OKX ini ditolak jalur ini) |
| `POST /priapi/v1/nft/me/instructions/buy-now` | POST | `"This collection isn't available for trade"` untuk SEMUA variasi body (orderId, id, sellOrderId, + buyerAddress + chain) |
| `POST /priapi/v1/nft/trading/buy` (konstanta `TRADE_BUY_BY_ORDERS`) | POST | HTTP 500 `"unknown inner error"` untuk SEMUA variasi body (orderIds, orderIdList, orders+address, + chain/buyer) |
| `POST /priapi/v1/nft/orderbook` | POST | `"sellOrdersCount is null"` (butuh param lanjutan; bukan jalur signature — tidak dikejar lebih jauh) |

**Pola yang konsisten:** semua endpoint baca publik OKX mengembalikan parameter order LENGKAP tapi signature KOSONG. Signature hanya ada di jalur buy yang butuh sesi. Endpoint login OKX sendiri ada (`/priapi/v1/nft/user/login`, `/priapi/v1/nft/user/sign` di chunk 3488) — login itu memakai signature wallet user, yang berada di luar wewenang riset read-only ini (keputusan parent, §9).

Yang SUDAH dicoba parent sebelumnya dan TIDAK saya ulangi persis: `priapi/v1/nft/asset/detail`, `order/list`, `api/v5/marketplace/…` (semua 404/kosong — memang bukan path frontend yang benar; path yang benar ada di tabel di atas).

---

## 7. Venue alternatif untuk KEDUA token yang sama

| Venue | Hasil |
|---|---|
| **Pasar proyek sendiri** (`0xA98b…`, `buy(uint256)`) | TIDAK ADA listing untuk #2560 maupun #107 (pindai penuh 526 listing oleh parent). Bukan rute di harga ini. |
| **Element** | TIDAK SAYA PERIKSA ULANG — pembacaan Element sedang berjalan terpisah oleh parent; hasil tugas itu yang berlaku. Catatan: order ini adalah order OKX-native (protokol Seaport fork OKX, bukan ElementEx), jadi Element hanya relevan bila penjual JUGA listing di sana — belum terbukti. |
| **tofuNFT** | **MATI sebagai venue.** `tofunft.com` me-redirect ke `https://tofu-bye.vercel.app/` yang mengembalikan HTTP 402 (deployment ditangguhkan). Tidak ada halaman koleksi Chip404 yang bisa dibuka di path mana pun yang dicoba. |
| **OpenSea** | **Bukan venue beli untuk BSC.** OpenSea menghentikan pembuatan listing/penawaran baru untuk NFT BSC sejak 18 Agustus 2023 (hanya lihat/transfer). Sumber: pengumuman OpenSea yang diliput The Block / U.Today. |
| **Blur** | **Tidak mendukung BSC** (hanya Ethereum/Blast/Base). Bukan venue. |
| **Kesimpulan venue** | OKX adalah satu-satunya venue yang terverifikasi memegang listing persis kedua token ini di harga yang disetujui. Tidak ada venue alternatif ≤ harga yang disetujui yang ditemukan. |

---

## 8. Langkah eksekusi SEANDAINYA signature didapat (untuk parent verifikasi ulang)

Ini adalah resep lengkapnya — JANGAN dieksekusi sampai signature benar-benar ada dan preview baw bersih.

**Per item (lakukan satu per satu, #2560 dulu lalu #107; JANGAN digabung — `fulfillOrder` varian ini satu order per transaksi):**

0. **Verifikasi ulang segar** (wajib, karena listing bisa batal): `GET multi-listings` (§6) untuk token itu → pastikan id, harga, owner, dan masa berlaku sama; lalu `ownerOf(tokenId)` di kontrak NFT dan `isApprovedForAll(penjual, conduit)` masih true.
1. **Audit:** Binance audit atas kontrak protokol `0x0000000000000068f116a894984e2db1123eb395` (dan NFT bila belum) — hasil diungkapkan, bukan diasumsikan lolos.
2. **Bangun calldata** `fulfillOrder` ke protokol `0x0000000000000068f116a894984e2db1123eb395`:
   - selector `0xb3a34c4c`, argumen: Order = (parameters §3 + signature penjual yang didapat), `fulfillerConduitKey` = `0x0...0`.
   - Perhatian encoding: struct OrderParameters varian ini **11 field tanpa `counter`**; memakai struct 12-field Seaport kanonik PASTI revert (kesalahan yang sudah saya buktikan di §5).
3. **`value` = harga persis dalam BNB native** (0,0006 untuk #2560; 0,00078 untuk #107) + gas. **Tidak ada wrap WBNB, tidak ada approve ERC-20, tidak ada approve NFT dari pembeli.** NFT terkirim ke wallet pemanggil (tidak ada argumen recipient).
4. **Preview baw** (`contract-call preview`, value = harga) → HARUS bersih: simulation code `000000000`, tidak ada error, tidak ada perubahan authority/allowance yang tidak diharapkan. Bila preview revert (terutama bila zone menolak — lihat §10), STOP, jangan eksekusi.
5. **Execute baw** (`contract-call execute --requestId …`) → verifikasi receipt status 1 + `ownerOf(tokenId)` = wallet user + tidak ada transfer BNB di luar harga + gas.
6. **Pasca-eksekusi (aturan standing):** update daftar NFT + rarity (Chip404 tier: #2560 dan #107 keduanya Cyan = tier 1 — catat dengan kata proyek, tierOf terverifikasi on-chain oleh parent sebelumnya) + marketplace check (pasar proyek sendiri bukan venue; venue pembelian adalah OKX).

**Total biaya bila kedua order tereksekusi:** 0,00138 BNB (harga) + 2× gas fulfill (estimasi gas belum bisa diukur tanpa signature — preview baw yang akan menunjukkannya; jangan mengutip angka gas dari simulasi gagal).

---

## 9. Fallback yang jujur (bila signature tetap tidak didapat)

**A. Manual lewat aplikasi wallet user di OKX — rute yang PASTI bisa jalan hari ini (dengan persetujuan user yang sudah ada).**
User buka sendiri (tanpa perantara) halaman item OKX dan klik Buy dari wallet-nya (OKX Wallet / WalletConnect). Yang user butuhkan: BNB native (bukan WBNB) sebesar harga + gas; TIDAK perlu WBNB, TIDAK perlu approve. Link persis:
- https://web3.okx.com/id/nft/asset/bsc/0xab6b18c626daadd1ff7cc45f402141153a5a9759/2560 (0,0006 BNB)
- https://web3.okx.com/id/nft/asset/bsc/0xab6b18c626daadd1ff7cc45f402141153a5a9759/107 (0,00078 BNB)
Catatan: jalur manual ini tidak bisa diverifikasi/dikendalikan dari VM; harga dan ketersediaan harus dicek user di layar saat klik Buy.

**B. Jalur sesi OKX untuk parent (BELUM TERBUKTI, butuh keputusan parent, bukan bagian riset ini).**
Satu-satunya jalur VM yang secara teori bisa menghasilkan signature adalah: login OKX via `priapi/v1/nft/user/login` + `user/sign` (butuh signature wallet user — satu aksi signing yang HARUS diputuskan parent secara eksplisit, di luar riset read-only ini), lalu ulangi `trading/buy` atau `buy-now` dengan sesi tersebut dan lihat apakah responsnya memuat signature/calldata. Bila responsnya memuat signature → lanjut ke §8. Bila tetap gagal → kembali ke fallback A. **Jangan menjanjikan jalur ini berhasil** — 500 di `trading/buy` dan penolakan `buy-now` bisa saja permanen untuk koleksi ini, bukan sekadar soal sesi.

**C. Yang TIDAK boleh dilakukan tanpa approval baru:**
- Beli di pasar proyek sendiri di harga ≥0,00142/item (harga berbeda dari yang disetujui).
- Menawar/membuat offer baru, mengubah harga, atau memakai venue lain di harga berbeda.
- Membeli token pengganti (mis. Steel termurah lain) — persetujuan user spesifik untuk #2560 + #107.

---

## 10. Yang masih BELUM terverifikasi (jujur dicatat, bukan ditutupi)

1. **Zone approval untuk order RESTRICTED (orderType 2).** Zone `0xdf2d4bffec010debd302674c9fb9cda99bb5e852` harus mengembalikan nilai ajaib saat `fulfillOrder` dipanggil. Karena cek signature gagal lebih dulu, persetujuan zone BELUM PERNAH teruji. Ini hanya bisa dibuktikan lewat preview baw dengan signature asli. Bila preview revert setelah signature didapat, zone adalah tersangka pertama.
2. **Apakah `trading/buy` / `buy-now` akan mengembalikan signature bila dipanggil dengan sesi login.** Belum teruji (butuh login; di luar wewenang riset ini).
3. **Selisih `orderHash` OKX vs hash EIP-712 hitungan saya.** Hash EIP-712 yang saya hitung dari parameter (dengan maupun tanpa `counter`, dengan domainSeparator yang SUDAH terkonfirmasi cocok) TIDAK sama dengan `orderHash` yang ditampilkan OKX. Kemungkinan besar `orderHash` OKX adalah pengenal internal OKX, bukan hash Seaport — dan itu TIDAK menghambat eksekusi, karena `fulfillOrder` menurunkan hash-nya sendiri dari parameter + signature, tidak memakai field `orderHash` OKX. Tetap dicatat sebagai pertanyaan terbuka, bukan blocker.
4. **Estimasi gas fulfill.** Tidak bisa diukur tanpa signature (simulasi selalu revert di cek signature). Preview baw yang akan menentukannya.
5. **Hasil tugas Element parent.** Laporan ini tidak menduplikasi pembacaan Element; bila tugas itu menemukan listing yang sama di Element, itu adalah rute terpisah yang perlu diverifikasi sendiri (orderbook Element ≠ orderbook OKX).

---

## 11. Metode, batas, dan apa yang TIDAK dilakukan

- **Metode:** fetch teks halaman OKX + unduh bundle JS publik (chunk defi-mode 110/1324/3488/3730/3929/4199/5327/7344/810/8122/9082/nftDetail/runtime/vendor-common) → grep konstanta API → probe endpoint `priapi` dengan variasi param yang dipandu pesan error server → ABI Sourcify untuk protokol → `eth_call` read-only (getOrderStatus, getCounter, information, getConduit, isApprovedForAll, eth_getCode, simulasi fulfillOrder) → cek venue alternatif via fetch/search teks.
- **Tidak dilakukan:** tidak ada live browser, tidak ada login OKX, tidak ada signature wallet apa pun, tidak ada preview/execute baw, tidak ada perubahan file state/snapshot/MEMORY/cron. Satu-satunya file yang ditulis adalah laporan ini (file scratch riset dihapus setelah laporan selesai agar hanya laporan ini yang tersisa).
- **Tidak ada data yang dikarang:** setiap alamat kontrak, harga, id order, hash, selector, dan pesan error di atas berasal dari respons tool yang benar-benar diterima (halaman OKX, API priapi, RPC BSC, Sourcify). Klaim yang tidak bisa diverifikasi diberi label eksplisit sebagai belum terverifikasi (§10).
