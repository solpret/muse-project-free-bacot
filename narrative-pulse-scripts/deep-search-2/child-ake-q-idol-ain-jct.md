# Deep-search-2 — first-30 early buyer, 5 koin terbentuk (BSC, read-only)

**Tanggal scan:** 2026-11-02 (WIB, blok tip saat scan awal 131231329). **Penulis:** subagent scan riset wallet (child). **Tidak ada** file state/feed/cron/goal yang diubah; file ini adalah satu-satunya file baru.

**Metode (sama untuk 4 koin yang berhasil):** pair V2 diverifikasi on-chain lewat factory PCS V2 `0xca143ce32fe78f1f7019d7d551a6402fc5350c73` `getPair(token, WBNB)` — selector dibangun programatik dengan `eth_utils.keccak`, tidak pernah hand-type. Blok pembuatan pair diverifikasi silang lewat event `PairCreated` factory (Ankr) — alamat pair di data event cocok persis dengan hasil `getPair`. First-30 = 30 penerima berbeda pertama kronologis dari log `Transfer` token dengan pengirim = pair, diurutkan (blok, logIndex) — Ankr mengembalikan log tidak terurut, jadi pengurutan dilakukan di sisi klien. Chunk 10.000 blok; bila satu chunk mengembalikan tepat 1.000 log, chunk dipecah (tidak ada chunk yang kena cap dalam scan ini — volume per 10.000 blok jauh di bawah 1.000 untuk semua koin). Waktu beli pertama = timestamp header blok (`eth_getBlockByNumber` via fast_rpc) — dicocokkan dengan timestamp log Ankr untuk ke-120 pembeli pertama: **0 mismatch**. Desimal dibaca on-chain: 18 untuk keempat token. Saldo sekarang = `balanceOf` on-chain. `% dipegang = saldo / beli awal 6 jam`; `% jual ≤1 jam = transfer wallet→pair dalam 1 jam sejak beli pertama / beli awal 6 jam`. Aturan debu: saldo ≤0,5% beli awal 6 jam = SOLD.

**Batasan yang wajib dibaca koordinator:** (1) "Beli" di sini = transfer pair→wallet saja — transfer itu juga bisa berasal dari remove-liquidity, tidak dibedakan oleh log Transfer saja. (2) "Proxy profit" (beli awal + pegang/jual) BUKAN PnL terverifikasi; tidak ada klaim PnL dan tidak ada klaim "terbukti insider" di file ini. (3) Co-buy = linkage LEMAH; linkage KUAT hanya shared funding/transfer langsung — funding TIDAK dinilai di sini. (4) Coret "exchange", "klaster insider MSX", dan "pemegang round-amount tim/vesting" TIDAK bisa diverifikasi dari data Transfer saja karena daftar alamat MSX/exchange tidak dilampirkan dalam tugas dan tidak ada data vesting/supply per wallet di sini — tidak ada wallet yang dicoret semata-mata atas dasar itu; wallet dengan beli awal 6 jam yang bulat (kelipatan 10.000, angka bulat) DITANDAI "round-amount — perlu cek koordinator", bukan dicoret otomatis. (5) Set terpantau = 50 kunci `wallets` di `~/workspace/narrative-pulse/tier-ab-watch-state.json` (field `tier_a_private`/`tier_b_private` di file itu hanya angka hitung 13/1, bukan daftar alamat, jadi pembedaan tier A vs B tidak bisa dilakukan dari file itu).

## Ringkasan hasil

| Koin | Pair V2 (WBNB) terverifikasi | Status pasar-pertama | First-30 V2 | Kontrak/bot di first-30 | Daftar bersih |
|---|---|---|---|---|---|
| AKE | 0x31e492e0b47ebda736b8655f6e9cb564bc9d4435 | BUKAN pasar pertama (lihat § koin) | 30 | 22 | 2 |
| Q | 0x8b01ff647ad15fbf9ffb43a0f84cb8bcfbab9acd | BUKAN pasar pertama (lihat § koin) | 30 | 26 | 2 |
| IDOL | 0x46377435d96be3e68799e98fd94381a061d174e5 | BUKAN pasar pertama (lihat § koin) | 30 | 28 | 0 |
| AIN | 0xd18ed1a49b3488550d0be01c5a010b26363c52a0 | BUKAN pasar pertama (lihat § koin) | 30 | 24 | 4 |
| JCT | TIDAK ADA (getPair = 0x0000000000000000000000000000000000000000 untuk WBNB, USDT, USD1, USDC, BUSD) | GAGAL TOTAL — tidak bisa dinilai pasar-pertama V2 | — | — | 0 (gagal) |

**Catatan ringkasan penting:** keempat pair V2 yang terverifikasi BUKAN pasar pertama tokennya — semuanya dibuat SETELAH pool V3 pertama di GeckoTerminal (AKE +~2,8 hari, Q +~2 hari, IDOL +~86 hari, AIN +~1,1 hari). Jadi "first-30 V2" di sini adalah pembeli awal pair V2, BUKAN pembeli pertama token secara keseluruhan. Pembeli pertama sesungguhnya ada di pool V3 (dan pool-pool lain yang lebih awal) dan TIDAK dicakup tugas ini. Selain itu first-30 V2 keempat koin didominasi kontrak/bot executor (AKE 22/30, Q 26/30, IDOL 28/30, AIN 24/30) — wajar untuk pair V2 yang lahir belakangan dan lebih sepi daripada pasar pertamanya (arbitrase V3↔V2 oleh bot). Daftar bersih per koin menjadi kecil — itu hasil, bukan kegagalan scan.

## AKE

- **CA (persis dari tugas):** `0x2c3a8ee94ddd97244a93bc48298f97d2c412f7db` — mcap GeckoTerminal 2026-11-02 17:35 WIB: ~$141 juta.
- **Pair V2 terverifikasi:** `0x31e492e0b47ebda736b8655f6e9cb564bc9d4435` — `getPair(token, WBNB 0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c)` on-chain + `PairCreated` factory di blok 58558942 (2025-08-23T02:50:39Z (blok 58558942)). Pair USDT V2 lain: AKE: `0x168770fc147cbe3b94e958bb9404dde5406dde08` (PairCreated blok 60664955, 2025-09-10T09:41:23Z).
- **Status pasar-pertama: BUKAN pasar pertama.** Pool GeckoTerminal paling awal yang terdaftar: 2025-08-20T07:40:09Z PancakeSwap V3 AKE/WBNB 0.01% (pool 0x4d3bf29ba30f8bfe4624e7678709afa195689c5d). Pair V2 ini dibuat setelahnya. (Endpoint GeckoTerminal `tokens/<CA>/pools` berhasil dibaca; daftar lengkap 20 pool pertama dicatat di log kerja, hanya pool paling awal + pair V2 yang dikutip di sini agar file tetap terbaca.)
- **Jendela scan V2:** blok 58558942 s.d. 63558941 (chunk 10.000 blok, Ankr `ankr_getLogs`, pageSize 1000, tidak ada cap-hit, tidak ada gagal baca). Log pair→wallet dalam jendela: 130.
- **Rentang beli pertama first-30:** 2025-08-23 02:54:44 UTC / 2025-08-23 09:54:44 WIB s.d. 2025-09-27 00:20:46 UTC / 2025-09-27 07:20:46 WIB.

### Tabel 30 pembeli pertama (pair V2, kronologis)

| # | Alamat lengkap | Blok beli pertama | Waktu beli pertama (UTC / WIB) | Beli awal 6 jam | Saldo sekarang | % dipegang | % jual ≤1 jam | EOA/kontrak | Tanda |
|---|---|---|---|---|---|---|---|---|---|
| 1 | `0xbc203d7f83677c7ed3f7acec959963e7f4ecc5c2` | 58559269 | 2025-08-23 02:54:44 UTC / 2025-08-23 09:54:44 WIB | 3,318.71 | 0 | 0.00% | 0.00% | KONTRAK | SOLD (debu ≤0,5%) |
| 2 | `0x173e6f719b1deb322f349f87f993c67ecfd21835` | 58559299 | 2025-08-23 02:55:07 UTC / 2025-08-23 09:55:07 WIB | 0.00000000 | 0.00000000 | 100.00% | 0.00% | KONTRAK | — |
| 3 | `0x426603bac5e0ea73fd13aecad7a80c9f963f6eac` | 58559308 | 2025-08-23 02:55:13 UTC / 2025-08-23 09:55:13 WIB | 0.00000000 | 0.08326559 | 5582482774.06% | 0.00% | KONTRAK | — |
| 4 | `0xb21a7d6b07ad608202c5c057031a034bf4166b38` | 58559312 | 2025-08-23 02:55:16 UTC / 2025-08-23 09:55:16 WIB | 0.00000001 | 154.1305 | 1646065349377.42% | 0.00% | KONTRAK | — |
| 5 | `0x29a4b61a493ca34ab367594594a730fddd131bfa` | 58559432 | 2025-08-23 02:56:46 UTC / 2025-08-23 09:56:46 WIB | 0.00000000 | 0.00000000 | 100.00% | 0.00% | EOA | — |
| 6 | `0xb12a6ea8512b305ae2a37e9b0d771e5ef15fcf0c` | 58559774 | 2025-08-23 03:01:03 UTC / 2025-08-23 10:01:03 WIB | 0.00000000 | 0 | 0.00% | 100.00% | KONTRAK | SOLD (debu ≤0,5%) |
| 7 | `0xea5d36d207dd70a981d0315349697d3c1045c159` | 58739050 | 2025-08-24 16:22:15 UTC / 2025-08-24 23:22:15 WIB | 0.00000000 | 0 | 0.00% | 100.00% | KONTRAK | SOLD (debu ≤0,5%) |
| 8 | `0xd65b25d3988a9616e3af05f81d5c114a40b4d1aa` | 58739050 | 2025-08-24 16:22:15 UTC / 2025-08-24 23:22:15 WIB | 0.00000000 | 0 | 0.00% | 0.00% | KONTRAK | SOLD (debu ≤0,5%) |
| 9 | `0x0000000d94514cbcf9455c0be85541e5d45cf1f5` | 58945105 | 2025-08-26 11:18:05 UTC / 2025-08-26 18:18:05 WIB | 445.4576 | 0 | 0.00% | 0.00% | KONTRAK | SOLD (debu ≤0,5%) |
| 10 | `0x60aecaf099040486763e7a87374bebc104f55617` | 59735141 | 2025-09-02 07:57:10 UTC / 2025-09-02 14:57:10 WIB | 0.01405855 | 0 | 0.00% | 0.00% | KONTRAK | SOLD (debu ≤0,5%) |
| 11 | `0x3df9a5a906e4d85aa167270211243d81b8aa52e9` | 60114855 | 2025-09-05 15:04:10 UTC / 2025-09-05 22:04:10 WIB | 0.00426645 | 0 | 0.00% | 0.00% | EOA | SOLD (debu ≤0,5%) |
| 12 | `0x8ecb1a8d8fe0c0b4d1ce823210d8d61a615ec9f9` | 60310312 | 2025-09-07 07:47:34 UTC / 2025-09-07 14:47:34 WIB | 0.01067510 | 2,700.85 | 25300478.90% | 0.00% | EOA | — |
| 13 | `0xa46e968c85fe656084ff699d4d3d50eb3f9f81c4` | 60459522 | 2025-09-08 14:53:04 UTC / 2025-09-08 21:53:04 WIB | 0.00028416 | 0.00028416 | 100.00% | 0.00% | KONTRAK | — |
| 14 | `0xea56b9b9716e9f28b969c1308da46fc3331438b0` | 60459523 | 2025-09-08 14:53:04 UTC / 2025-09-08 21:53:04 WIB | 2,114.54 | 0 | 0.00% | 0.00% | KONTRAK | SOLD (debu ≤0,5%) |
| 15 | `0xcb9c2b96bcd7e6aa41f7ef14b8ac3a51bef36bed` | 60880272 | 2025-09-12 06:34:38 UTC / 2025-09-12 13:34:38 WIB | 0.00054719 | 0 | 0.00% | 0.00% | KONTRAK | SOLD (debu ≤0,5%) |
| 16 | `0xfe9e6df6dab641a9fead05d9e6d24c9c18bb1eba` | 60880535 | 2025-09-12 06:37:55 UTC / 2025-09-12 13:37:55 WIB | 0.00000270 | 0 | 0.00% | 100.00% | KONTRAK | SOLD (debu ≤0,5%) |
| 17 | `0x1fa6a05af340ff81e63129f6f3552763ffa6002a` | 61053616 | 2025-09-13 18:41:36 UTC / 2025-09-14 01:41:36 WIB | 0.00000009 | 0 | 0.00% | 100.00% | KONTRAK | SOLD (debu ≤0,5%) |
| 18 | `0x4d3bf29ba30f8bfe4624e7678709afa195689c5d` | 61150730 | 2025-09-14 14:55:39 UTC / 2025-09-14 21:55:39 WIB | 806.2356 | 133,427,845.16 | 16549485.98% | 0.43% | KONTRAK | — |
| 19 | `0x89a1d49a4e08ecdfb0228509db58bc5726628b0b` | 61243903 | 2025-09-15 10:20:39 UTC / 2025-09-15 17:20:39 WIB | 0.00000159 | 0 | 0.00% | 100.00% | EOA | SOLD (debu ≤0,5%) |
| 20 | `0x7c1c3a69b47ee0d915892247e721d764aeec7c51` | 61244664 | 2025-09-15 10:30:10 UTC / 2025-09-15 17:30:10 WIB | 0.00007219 | 0 | 0.00% | 100.00% | KONTRAK | SOLD (debu ≤0,5%) |
| 21 | `0x653b40ab9dd1d1b42845f67f2be617b2445b7ea5` | 61263791 | 2025-09-15 14:29:18 UTC / 2025-09-15 21:29:18 WIB | 0.04858861 | 0 | 0.00% | 234.54% | KONTRAK | SOLD (debu ≤0,5%) |
| 22 | `0xf87e9ea0408f8cd001d93dd83bee5d3dea99b72d` | 61614843 | 2025-09-18 15:39:34 UTC / 2025-09-18 22:39:34 WIB | 12,213.05 | 0 | 0.00% | 14.49% | EOA | SOLD (debu ≤0,5%) |
| 23 | `0x71ad73eebc14dd8e2ddb8229269ea7a71b704257` | 61702547 | 2025-09-19 09:56:00 UTC / 2025-09-19 16:56:00 WIB | 3.8504 | 0 | 0.00% | 0.00% | EOA | SOLD (debu ≤0,5%) |
| 24 | `0x3f947d2047fab980956030695f86a470106ba4fa` | 61702871 | 2025-09-19 10:00:03 UTC / 2025-09-19 17:00:03 WIB | 0.00154793 | 0 | 0.00% | 100.00% | KONTRAK | SOLD (debu ≤0,5%) |
| 25 | `0x4675748248a1182819e5ea6819e41be0b2ad3a7d` | 61752420 | 2025-09-19 20:19:28 UTC / 2025-09-20 03:19:28 WIB | 0.12243938 | 0 | 0.00% | 898.52% | KONTRAK | SOLD (debu ≤0,5%) |
| 26 | `0x253761c375fa6d108bfb6c6298bec899299fb565` | 62076194 | 2025-09-22 15:47:15 UTC / 2025-09-22 22:47:15 WIB | 0.04581904 | 0 | 0.00% | 0.00% | EOA | SOLD (debu ≤0,5%) |
| 27 | `0x15ea855289f01855ef23bed8937f937351a3a4f8` | 62129382 | 2025-09-23 02:52:08 UTC / 2025-09-23 09:52:08 WIB | 3.5341 | 0 | 0.00% | 0.00% | EOA | SOLD (debu ≤0,5%) |
| 28 | `0x3a5a32afb23c9e8241bcc7c2940f5f60acde5b44` | 62196237 | 2025-09-23 16:47:58 UTC / 2025-09-23 23:47:58 WIB | 0.00234712 | 0 | 0.00% | 100.00% | KONTRAK | SOLD (debu ≤0,5%) |
| 29 | `0xc2ddc44038953659f58803a9f8851954ef8bf799` | 62197241 | 2025-09-23 17:00:33 UTC / 2025-09-24 00:00:33 WIB | 2.4823 | 0.00000001 | 0.00% | 0.00% | KONTRAK | SOLD (debu ≤0,5%) |
| 30 | `0x63adbccbd5265f03e581ebad4e3eeb3a09233af1` | 62578014 | 2025-09-27 00:20:46 UTC / 2025-09-27 07:20:46 WIB | 2.9674 | 0.00000000 | 0.00% | 0.00% | KONTRAK | SOLD (debu ≤0,5%) |

### Daftar coret

- `0xbc203d7f83677c7ed3f7acec959963e7f4ecc5c2` — kontrak/bot executor (beli awal 6 jam 3,318.71, saldo 0, 0.00% dipegang).
- `0x173e6f719b1deb322f349f87f993c67ecfd21835` — kontrak/bot executor (beli awal 6 jam 0.00000000, saldo 0.00000000, 100.00% dipegang).
- `0x426603bac5e0ea73fd13aecad7a80c9f963f6eac` — kontrak/bot executor (beli awal 6 jam 0.00000000, saldo 0.08326559, 5582482774.06% dipegang).
- `0xb21a7d6b07ad608202c5c057031a034bf4166b38` — kontrak/bot executor (beli awal 6 jam 0.00000001, saldo 154.1305, 1646065349377.42% dipegang).
- `0xb12a6ea8512b305ae2a37e9b0d771e5ef15fcf0c` — kontrak/bot executor (beli awal 6 jam 0.00000000, saldo 0, 0.00% dipegang).
- `0xea5d36d207dd70a981d0315349697d3c1045c159` — kontrak/bot executor (beli awal 6 jam 0.00000000, saldo 0, 0.00% dipegang).
- `0xd65b25d3988a9616e3af05f81d5c114a40b4d1aa` — kontrak/bot executor (beli awal 6 jam 0.00000000, saldo 0, 0.00% dipegang).
- `0x0000000d94514cbcf9455c0be85541e5d45cf1f5` — kontrak/bot executor (beli awal 6 jam 445.4576, saldo 0, 0.00% dipegang).
- `0x60aecaf099040486763e7a87374bebc104f55617` — kontrak/bot executor (beli awal 6 jam 0.01405855, saldo 0, 0.00% dipegang).
- `0xa46e968c85fe656084ff699d4d3d50eb3f9f81c4` — kontrak/bot executor (beli awal 6 jam 0.00028416, saldo 0.00028416, 100.00% dipegang).
- `0xea56b9b9716e9f28b969c1308da46fc3331438b0` — kontrak/bot executor (beli awal 6 jam 2,114.54, saldo 0, 0.00% dipegang).
- `0xcb9c2b96bcd7e6aa41f7ef14b8ac3a51bef36bed` — kontrak/bot executor (beli awal 6 jam 0.00054719, saldo 0, 0.00% dipegang).
- `0xfe9e6df6dab641a9fead05d9e6d24c9c18bb1eba` — kontrak/bot executor (beli awal 6 jam 0.00000270, saldo 0, 0.00% dipegang).
- `0x1fa6a05af340ff81e63129f6f3552763ffa6002a` — kontrak/bot executor (beli awal 6 jam 0.00000009, saldo 0, 0.00% dipegang).
- `0x4d3bf29ba30f8bfe4624e7678709afa195689c5d` — kontrak/bot executor (beli awal 6 jam 806.2356, saldo 133,427,845.16, 16549485.98% dipegang).
- `0x7c1c3a69b47ee0d915892247e721d764aeec7c51` — kontrak/bot executor (beli awal 6 jam 0.00007219, saldo 0, 0.00% dipegang).
- `0x653b40ab9dd1d1b42845f67f2be617b2445b7ea5` — kontrak/bot executor (beli awal 6 jam 0.04858861, saldo 0, 0.00% dipegang).
- `0x3f947d2047fab980956030695f86a470106ba4fa` — kontrak/bot executor (beli awal 6 jam 0.00154793, saldo 0, 0.00% dipegang).
- `0x4675748248a1182819e5ea6819e41be0b2ad3a7d` — kontrak/bot executor (beli awal 6 jam 0.12243938, saldo 0, 0.00% dipegang).
- `0x3a5a32afb23c9e8241bcc7c2940f5f60acde5b44` — kontrak/bot executor (beli awal 6 jam 0.00234712, saldo 0, 0.00% dipegang).
- `0xc2ddc44038953659f58803a9f8851954ef8bf799` — kontrak/bot executor (beli awal 6 jam 2.4823, saldo 0.00000001, 0.00% dipegang).
- `0x63adbccbd5265f03e581ebad4e3eeb3a09233af1` — kontrak/bot executor (beli awal 6 jam 2.9674, saldo 0.00000000, 0.00% dipegang).

### Daftar bersih (hold bermakna + EOA + bukan daftar coret)

Definisi di sini: saldo >0,5% beli awal 6 jam (bukan SOLD), `eth_getCode` kosong (EOA), dan tidak masuk daftar coret di atas. Wallet yang sudah terpantau tetap bisa masuk daftar bersih bila memenuhi syarat, tapi ditandai — koordinator yang memutuskan apakah itu "baru".

- `0x29a4b61a493ca34ab367594594a730fddd131bfa` — beli pertama blok 58559432 (2025-08-23 02:56:46 UTC / 2025-08-23 09:56:46 WIB), beli awal 6 jam 0.00000000, saldo sekarang 0.00000000, 100.00% dipegang, jual ≤1 jam 0.00%.
- `0x8ecb1a8d8fe0c0b4d1ce823210d8d61a615ec9f9` — beli pertama blok 60310312 (2025-09-07 07:47:34 UTC / 2025-09-07 14:47:34 WIB), beli awal 6 jam 0.01067510, saldo sekarang 2,700.85, 25300478.90% dipegang, jual ≤1 jam 0.00%.

### Gagal baca

- Ankr `ankr_getLogs` pair→wallet: nihil. Ankr `ankr_getLogs` wallet→pair (per pembeli): nihil. `balanceOf`/`eth_getCode`/header blok: nihil. Timestamp header vs timestamp log Ankr untuk 30 beli pertama: 0 mismatch.

## Q

- **CA (persis dari tugas):** `0xc07e1300dc138601fa6b0b59f8d0fa477e690589` — mcap GeckoTerminal 2026-11-02 17:35 WIB: ~$127,3 juta.
- **Pair V2 terverifikasi:** `0x8b01ff647ad15fbf9ffb43a0f84cb8bcfbab9acd` — `getPair(token, WBNB 0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c)` on-chain + `PairCreated` factory di blok 59755007 (2025-09-02T12:05:30Z (blok 59755007)). Pair USDT V2 lain: tidak ada (getPair USDT/USD1/USDC/BUSD = 0).
- **Status pasar-pertama: BUKAN pasar pertama.** Pool GeckoTerminal paling awal yang terdaftar: 2025-08-31T08:07:27Z PancakeSwap V3 Q/USDT 0.01% (pool 0x8bafe0bdd3eb9ae0539f5b32e771c1a72a189b7f). Pair V2 ini dibuat setelahnya. (Endpoint GeckoTerminal `tokens/<CA>/pools` berhasil dibaca; daftar lengkap 20 pool pertama dicatat di log kerja, hanya pool paling awal + pair V2 yang dikutip di sini agar file tetap terbaca.)
- **Jendela scan V2:** blok 59755007 s.d. 60755006 (chunk 10.000 blok, Ankr `ankr_getLogs`, pageSize 1000, tidak ada cap-hit, tidak ada gagal baca). Log pair→wallet dalam jendela: 2042.
- **Rentang beli pertama first-30:** 2025-09-02 12:28:53 UTC / 2025-09-02 19:28:53 WIB s.d. 2025-09-03 13:28:11 UTC / 2025-09-03 20:28:11 WIB.

### Tabel 30 pembeli pertama (pair V2, kronologis)

| # | Alamat lengkap | Blok beli pertama | Waktu beli pertama (UTC / WIB) | Beli awal 6 jam | Saldo sekarang | % dipegang | % jual ≤1 jam | EOA/kontrak | Tanda |
|---|---|---|---|---|---|---|---|---|---|
| 1 | `0x946d85048ab0faf75fb29d43645cc2ff14701870` | 59756878 | 2025-09-02 12:28:53 UTC / 2025-09-02 19:28:53 WIB | 197.2323 | 0 | 0.00% | 0.00% | KONTRAK | SOLD (debu ≤0,5%) |
| 2 | `0x426603bac5e0ea73fd13aecad7a80c9f963f6eac` | 59756878 | 2025-09-02 12:28:53 UTC / 2025-09-02 19:28:53 WIB | 1.1251 | 1.8343 | 163.04% | 0.00% | KONTRAK | — |
| 3 | `0xb21a7d6b07ad608202c5c057031a034bf4166b38` | 59756886 | 2025-09-02 12:28:59 UTC / 2025-09-02 19:28:59 WIB | 2.1986 | 2.7296 | 124.15% | 0.00% | KONTRAK | — |
| 4 | `0x60bc631c58db2bea6a9343c7821a8b2fb49b1f21` | 59757227 | 2025-09-02 12:33:15 UTC / 2025-09-02 19:33:15 WIB | 0.17117923 | 0 | 0.00% | 100.00% | KONTRAK | SOLD (debu ≤0,5%) |
| 5 | `0x3cfa4c77c35c78bb0b4d719a5afecf949817bcbc` | 59757358 | 2025-09-02 12:34:53 UTC / 2025-09-02 19:34:53 WIB | 70.0745 | 0 | 0.00% | 0.00% | KONTRAK | SOLD (debu ≤0,5%) |
| 6 | `0xa2750e6039f6d92a07a7686be4468c4dc8fdfc11` | 59760125 | 2025-09-02 13:09:29 UTC / 2025-09-02 20:09:29 WIB | 0.00941947 | 0.00000001 | 0.00% | 0.00% | KONTRAK | SOLD (debu ≤0,5%) |
| 7 | `0xbc203d7f83677c7ed3f7acec959963e7f4ecc5c2` | 59761190 | 2025-09-02 13:22:48 UTC / 2025-09-02 20:22:48 WIB | 7.7910 | 0 | 0.00% | 0.00% | KONTRAK | SOLD (debu ≤0,5%) |
| 8 | `0x173e6f719b1deb322f349f87f993c67ecfd21835` | 59761268 | 2025-09-02 13:23:46 UTC / 2025-09-02 20:23:46 WIB | 0.16402417 | 0.16402417 | 100.00% | 0.00% | KONTRAK | — |
| 9 | `0x2b40f892a5b8aefdf9868317330ca0f956f70d2b` | 59761300 | 2025-09-02 13:24:10 UTC / 2025-09-02 20:24:10 WIB | 56.6244 | 86.9690 | 153.59% | 0.00% | EOA | — |
| 10 | `0x29a4b61a493ca34ab367594594a730fddd131bfa` | 59761309 | 2025-09-02 13:24:17 UTC / 2025-09-02 20:24:17 WIB | 0.15984350 | 0.15984350 | 100.00% | 0.00% | EOA | — |
| 11 | `0x8bafe0bdd3eb9ae0539f5b32e771c1a72a189b7f` | 59761572 | 2025-09-02 13:27:34 UTC / 2025-09-02 20:27:34 WIB | 71.6033 | 14,175,383.75 | 19797117.03% | 9.01% | KONTRAK | — |
| 12 | `0x60e4b2ddce57438d69e226550bc78ef737ce8fa4` | 59768929 | 2025-09-02 14:59:33 UTC / 2025-09-02 21:59:33 WIB | 16.5178 | 0 | 0.00% | 0.00% | KONTRAK | SOLD (debu ≤0,5%) |
| 13 | `0x04b4f0de2e0efd3ee884c35c6e91e15d9328a78f` | 59771000 | 2025-09-02 15:25:26 UTC / 2025-09-02 22:25:26 WIB | 21.9282 | 0 | 0.00% | 0.00% | KONTRAK | SOLD (debu ≤0,5%) |
| 14 | `0xb300000b72deaeb607a12d5f54773d1c19c7028d` | 59779625 | 2025-09-02 17:13:16 UTC / 2025-09-03 00:13:16 WIB | 27.7460 | 0 | 0.00% | 0.00% | KONTRAK | SOLD (debu ≤0,5%) |
| 15 | `0xca292dd4e9abdd1e5e21a2d7320baf5346a17d43` | 59782297 | 2025-09-02 17:46:40 UTC / 2025-09-03 00:46:40 WIB | 146.4674 | 0 | 0.00% | 0.00% | EOA | SOLD (debu ≤0,5%) |
| 16 | `0xb5cb05550357a4ac6c095d96a19bce513ba5ac04` | 59790065 | 2025-09-02 19:23:47 UTC / 2025-09-03 02:23:47 WIB | 5.1969 | 0 | 0.00% | 0.00% | KONTRAK | SOLD (debu ≤0,5%) |
| 17 | `0x76a8daee4b6e00823ee57a264c2b01ef27941ee8` | 59817623 | 2025-09-03 01:08:16 UTC / 2025-09-03 08:08:16 WIB | 330.6635 | 0 | 0.00% | 0.00% | KONTRAK | SOLD (debu ≤0,5%) |
| 18 | `0x2ea94a042461940fb59cc7260bb85342891fb5eb` | 59818982 | 2025-09-03 01:25:16 UTC / 2025-09-03 08:25:16 WIB | 285.2845 | 0.36386763 | 0.13% | 0.00% | KONTRAK | SOLD (debu ≤0,5%) |
| 19 | `0x653b40ab9dd1d1b42845f67f2be617b2445b7ea5` | 59831434 | 2025-09-03 04:00:58 UTC / 2025-09-03 11:00:58 WIB | 56.3117 | 0 | 0.00% | 5.94% | KONTRAK | SOLD (debu ≤0,5%) |
| 20 | `0xa01cd5b68265b972b73a713f6d824d1a6d3612b0` | 59832219 | 2025-09-03 04:10:47 UTC / 2025-09-03 11:10:47 WIB | 0.04367570 | 0.00000000 | 0.00% | 0.00% | KONTRAK | SOLD (debu ≤0,5%) |
| 21 | `0x4b1b2ea60cc20a171cb7eed8fe0de988f79651d2` | 59833777 | 2025-09-03 04:30:15 UTC / 2025-09-03 11:30:15 WIB | 68.5584 | 0 | 0.00% | 0.00% | KONTRAK | SOLD (debu ≤0,5%) |
| 22 | `0x9999b0cdd35d7f3b281ba02efc0d228486940515` | 59833980 | 2025-09-03 04:32:48 UTC / 2025-09-03 11:32:48 WIB | 184.5404 | 0.00092365 | 0.00% | 0.00% | KONTRAK | SOLD (debu ≤0,5%) |
| 23 | `0x4e10013061ad49af015cd320bd6b2739607244e8` | 59837648 | 2025-09-03 05:18:39 UTC / 2025-09-03 12:18:39 WIB | 10.4165 | 0 | 0.00% | 0.00% | EOA | SOLD (debu ≤0,5%) |
| 24 | `0x33f3184168de4a75a3f64a1dc86b73e4eb4c7a43` | 59846673 | 2025-09-03 07:11:27 UTC / 2025-09-03 14:11:27 WIB | 562.6119 | 0.00000000 | 0.00% | 0.00% | KONTRAK | SOLD (debu ≤0,5%) |
| 25 | `0xaf7076ff9f05f2653e73aea69cf68e6ffc4ec800` | 59848828 | 2025-09-03 07:38:24 UTC / 2025-09-03 14:38:24 WIB | 97.0284 | 32.0387 | 33.02% | 0.00% | KONTRAK | — |
| 26 | `0xea305f9cfbfec9be5a4de0300273466840a76e23` | 59857854 | 2025-09-03 09:31:14 UTC / 2025-09-03 16:31:14 WIB | 74.6354 | 0 | 0.00% | 0.00% | KONTRAK | SOLD (debu ≤0,5%) |
| 27 | `0xa4d8ca843293b45cb2f61d54509186ca81a34408` | 59858343 | 2025-09-03 09:37:20 UTC / 2025-09-03 16:37:20 WIB | 57.5821 | 0 | 0.00% | 0.00% | KONTRAK | SOLD (debu ≤0,5%) |
| 28 | `0x1231deb6f5749ef6ce6943a275a1d3e7486f4eae` | 59864715 | 2025-09-03 10:57:00 UTC / 2025-09-03 17:57:00 WIB | 5.3250 | 0 | 0.00% | 0.00% | KONTRAK | SOLD (debu ≤0,5%) |
| 29 | `0xa49839864c752ca76281335453a700fe31c0463b` | 59871338 | 2025-09-03 12:19:47 UTC / 2025-09-03 19:19:47 WIB | 197.6889 | 0.00000000 | 0.00% | 102.80% | KONTRAK | SOLD (debu ≤0,5%) |
| 30 | `0x472a167b714563f7ec80d25aa0e193f7e447061f` | 59876810 | 2025-09-03 13:28:11 UTC / 2025-09-03 20:28:11 WIB | 62.4314 | 373.0511 | 597.54% | 0.00% | KONTRAK | — |

### Daftar coret

- `0x946d85048ab0faf75fb29d43645cc2ff14701870` — kontrak/bot executor (beli awal 6 jam 197.2323, saldo 0, 0.00% dipegang).
- `0x426603bac5e0ea73fd13aecad7a80c9f963f6eac` — kontrak/bot executor (beli awal 6 jam 1.1251, saldo 1.8343, 163.04% dipegang).
- `0xb21a7d6b07ad608202c5c057031a034bf4166b38` — kontrak/bot executor (beli awal 6 jam 2.1986, saldo 2.7296, 124.15% dipegang).
- `0x60bc631c58db2bea6a9343c7821a8b2fb49b1f21` — kontrak/bot executor (beli awal 6 jam 0.17117923, saldo 0, 0.00% dipegang).
- `0x3cfa4c77c35c78bb0b4d719a5afecf949817bcbc` — kontrak/bot executor (beli awal 6 jam 70.0745, saldo 0, 0.00% dipegang).
- `0xa2750e6039f6d92a07a7686be4468c4dc8fdfc11` — kontrak/bot executor (beli awal 6 jam 0.00941947, saldo 0.00000001, 0.00% dipegang).
- `0xbc203d7f83677c7ed3f7acec959963e7f4ecc5c2` — kontrak/bot executor (beli awal 6 jam 7.7910, saldo 0, 0.00% dipegang).
- `0x173e6f719b1deb322f349f87f993c67ecfd21835` — kontrak/bot executor (beli awal 6 jam 0.16402417, saldo 0.16402417, 100.00% dipegang).
- `0x8bafe0bdd3eb9ae0539f5b32e771c1a72a189b7f` — kontrak/bot executor (beli awal 6 jam 71.6033, saldo 14,175,383.75, 19797117.03% dipegang).
- `0x60e4b2ddce57438d69e226550bc78ef737ce8fa4` — kontrak/bot executor (beli awal 6 jam 16.5178, saldo 0, 0.00% dipegang).
- `0x04b4f0de2e0efd3ee884c35c6e91e15d9328a78f` — kontrak/bot executor (beli awal 6 jam 21.9282, saldo 0, 0.00% dipegang).
- `0xb300000b72deaeb607a12d5f54773d1c19c7028d` — kontrak/bot executor (beli awal 6 jam 27.7460, saldo 0, 0.00% dipegang).
- `0xb5cb05550357a4ac6c095d96a19bce513ba5ac04` — kontrak/bot executor (beli awal 6 jam 5.1969, saldo 0, 0.00% dipegang).
- `0x76a8daee4b6e00823ee57a264c2b01ef27941ee8` — kontrak/bot executor (beli awal 6 jam 330.6635, saldo 0, 0.00% dipegang).
- `0x2ea94a042461940fb59cc7260bb85342891fb5eb` — kontrak/bot executor (beli awal 6 jam 285.2845, saldo 0.36386763, 0.13% dipegang).
- `0x653b40ab9dd1d1b42845f67f2be617b2445b7ea5` — kontrak/bot executor (beli awal 6 jam 56.3117, saldo 0, 0.00% dipegang).
- `0xa01cd5b68265b972b73a713f6d824d1a6d3612b0` — kontrak/bot executor (beli awal 6 jam 0.04367570, saldo 0.00000000, 0.00% dipegang).
- `0x4b1b2ea60cc20a171cb7eed8fe0de988f79651d2` — kontrak/bot executor (beli awal 6 jam 68.5584, saldo 0, 0.00% dipegang).
- `0x9999b0cdd35d7f3b281ba02efc0d228486940515` — kontrak/bot executor (beli awal 6 jam 184.5404, saldo 0.00092365, 0.00% dipegang).
- `0x33f3184168de4a75a3f64a1dc86b73e4eb4c7a43` — kontrak/bot executor (beli awal 6 jam 562.6119, saldo 0.00000000, 0.00% dipegang).
- `0xaf7076ff9f05f2653e73aea69cf68e6ffc4ec800` — kontrak/bot executor (beli awal 6 jam 97.0284, saldo 32.0387, 33.02% dipegang).
- `0xea305f9cfbfec9be5a4de0300273466840a76e23` — kontrak/bot executor (beli awal 6 jam 74.6354, saldo 0, 0.00% dipegang).
- `0xa4d8ca843293b45cb2f61d54509186ca81a34408` — kontrak/bot executor (beli awal 6 jam 57.5821, saldo 0, 0.00% dipegang).
- `0x1231deb6f5749ef6ce6943a275a1d3e7486f4eae` — kontrak/bot executor (beli awal 6 jam 5.3250, saldo 0, 0.00% dipegang).
- `0xa49839864c752ca76281335453a700fe31c0463b` — kontrak/bot executor (beli awal 6 jam 197.6889, saldo 0.00000000, 0.00% dipegang).
- `0x472a167b714563f7ec80d25aa0e193f7e447061f` — kontrak/bot executor (beli awal 6 jam 62.4314, saldo 373.0511, 597.54% dipegang).

### Daftar bersih (hold bermakna + EOA + bukan daftar coret)

Definisi di sini: saldo >0,5% beli awal 6 jam (bukan SOLD), `eth_getCode` kosong (EOA), dan tidak masuk daftar coret di atas. Wallet yang sudah terpantau tetap bisa masuk daftar bersih bila memenuhi syarat, tapi ditandai — koordinator yang memutuskan apakah itu "baru".

- `0x2b40f892a5b8aefdf9868317330ca0f956f70d2b` — beli pertama blok 59761300 (2025-09-02 13:24:10 UTC / 2025-09-02 20:24:10 WIB), beli awal 6 jam 56.6244, saldo sekarang 86.9690, 153.59% dipegang, jual ≤1 jam 0.00%.
- `0x29a4b61a493ca34ab367594594a730fddd131bfa` — beli pertama blok 59761309 (2025-09-02 13:24:17 UTC / 2025-09-02 20:24:17 WIB), beli awal 6 jam 0.15984350, saldo sekarang 0.15984350, 100.00% dipegang, jual ≤1 jam 0.00%.

### Gagal baca

- Ankr `ankr_getLogs` pair→wallet: nihil. Ankr `ankr_getLogs` wallet→pair (per pembeli): nihil. `balanceOf`/`eth_getCode`/header blok: nihil. Timestamp header vs timestamp log Ankr untuk 30 beli pertama: 0 mismatch.

## IDOL

- **CA (persis dari tugas):** `0x3b4de3c7855c03bb9f50ea252cd2c9fa1125ab07` — mcap GeckoTerminal 2026-11-02 17:35 WIB: ~$57,9 juta.
- **Pair V2 terverifikasi:** `0x46377435d96be3e68799e98fd94381a061d174e5` — `getPair(token, WBNB 0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c)` on-chain + `PairCreated` factory di blok 60007761 (2025-09-04T16:45:15Z (blok 60007761)). Pair USDT V2 lain: tidak ada (getPair USDT/USD1/USDC/BUSD = 0).
- **Status pasar-pertama: BUKAN pasar pertama.** Pool GeckoTerminal paling awal yang terdaftar: 2025-06-10T13:33:11Z PancakeSwap V3 IDOL/WBNB 0.01% (pool 0xfff4857a955b2b460c27fd431aa5a85fabca5559). Pair V2 ini dibuat setelahnya. (Endpoint GeckoTerminal `tokens/<CA>/pools` berhasil dibaca; daftar lengkap 20 pool pertama dicatat di log kerja, hanya pool paling awal + pair V2 yang dikutip di sini agar file tetap terbaca.)
- **Jendela scan V2:** blok 60007761 s.d. 61007760 (chunk 10.000 blok, Ankr `ankr_getLogs`, pageSize 1000, tidak ada cap-hit, tidak ada gagal baca). Log pair→wallet dalam jendela: 1812.
- **Rentang beli pertama first-30:** 2025-09-04 16:45:29 UTC / 2025-09-04 23:45:29 WIB s.d. 2025-09-06 00:44:48 UTC / 2025-09-06 07:44:48 WIB.

### Tabel 30 pembeli pertama (pair V2, kronologis)

| # | Alamat lengkap | Blok beli pertama | Waktu beli pertama (UTC / WIB) | Beli awal 6 jam | Saldo sekarang | % dipegang | % jual ≤1 jam | EOA/kontrak | Tanda |
|---|---|---|---|---|---|---|---|---|---|
| 1 | `0x2ea94a042461940fb59cc7260bb85342891fb5eb` | 60007779 | 2025-09-04 16:45:29 UTC / 2025-09-04 23:45:29 WIB | 1,317.26 | 0.00000000 | 0.00% | 0.00% | KONTRAK | SOLD (debu ≤0,5%) |
| 2 | `0x144d395b5562c742259932d2ee6e1d8d092a21b8` | 60007803 | 2025-09-04 16:45:47 UTC / 2025-09-04 23:45:47 WIB | 710.3883 | 11,023.36 | 1551.74% | 62.99% | KONTRAK | — |
| 3 | `0x6b080b294bfb2d908595e12068c8d054f58f9a76` | 60007901 | 2025-09-04 16:47:01 UTC / 2025-09-04 23:47:01 WIB | 502.7291 | 0.00000000 | 0.00% | 0.00% | KONTRAK | SOLD (debu ≤0,5%) |
| 4 | `0x6b3affc894b0d2d566e5ff03ad79188f1b65bfff` | 60007913 | 2025-09-04 16:47:10 UTC / 2025-09-04 23:47:10 WIB | 582.6777 | 0.00000000 | 0.00% | 0.00% | KONTRAK | SOLD (debu ≤0,5%) |
| 5 | `0xfff4857a955b2b460c27fd431aa5a85fabca5559` | 60007922 | 2025-09-04 16:47:17 UTC / 2025-09-04 23:47:17 WIB | 1,092.20 | 25,802,157.31 | 2362412.96% | 140.47% | KONTRAK | — |
| 6 | `0x9999b0cdd35d7f3b281ba02efc0d228486940515` | 60007981 | 2025-09-04 16:48:01 UTC / 2025-09-04 23:48:01 WIB | 1,249.74 | 0 | 0.00% | 0.00% | KONTRAK | SOLD (debu ≤0,5%) |
| 7 | `0x6483d86d075b1a657664444363ad94144a01deea` | 60007988 | 2025-09-04 16:48:07 UTC / 2025-09-04 23:48:07 WIB | 118.5370 | 0.00000000 | 0.00% | 0.00% | KONTRAK | SOLD (debu ≤0,5%) |
| 8 | `0xb5cb05550357a4ac6c095d96a19bce513ba5ac04` | 60008351 | 2025-09-04 16:52:39 UTC / 2025-09-04 23:52:39 WIB | 414.1176 | 0.00000000 | 0.00% | 0.00% | KONTRAK | SOLD (debu ≤0,5%) |
| 9 | `0xbd99f73a3b4cd763ec40f66fa5a7a6014cf669da` | 60008860 | 2025-09-04 16:59:01 UTC / 2025-09-04 23:59:01 WIB | 397.4579 | 0 | 0.00% | 0.00% | KONTRAK | SOLD (debu ≤0,5%) |
| 10 | `0x7ac30f228b3bd2295c7b1d6b3ce2006e255245ec` | 60010100 | 2025-09-04 17:14:31 UTC / 2025-09-05 00:14:31 WIB | 30.4468 | 0 | 0.00% | 0.00% | KONTRAK | SOLD (debu ≤0,5%) |
| 11 | `0xb56013770dd5b2fc90f397f1c27396c783f277e5` | 60010162 | 2025-09-04 17:15:17 UTC / 2025-09-05 00:15:17 WIB | 419.8728 | 0 | 0.00% | 38.43% | KONTRAK | SOLD (debu ≤0,5%) |
| 12 | `0x04b4f0de2e0efd3ee884c35c6e91e15d9328a78f` | 60012337 | 2025-09-04 17:42:28 UTC / 2025-09-05 00:42:28 WIB | 85.2995 | 0 | 0.00% | 173.31% | KONTRAK | SOLD (debu ≤0,5%) |
| 13 | `0x10ed43c718714eb63d5aa57b78b54704e256024e` | 60015246 | 2025-09-04 18:18:52 UTC / 2025-09-05 01:18:52 WIB | 42,981.96 | 0 | 0.00% | 0.00% | KONTRAK | SOLD (debu ≤0,5%) |
| 14 | `0xba53da030f3504db8cf0309bb89791950d0ce5e6` | 60015656 | 2025-09-04 18:23:59 UTC / 2025-09-05 01:23:59 WIB | 253.7879 | 39.8750 | 15.71% | 0.00% | KONTRAK | — |
| 15 | `0x5dda609d62fce85d50a406a447cd28590c8042fe` | 60017061 | 2025-09-04 18:41:34 UTC / 2025-09-05 01:41:34 WIB | 210.0275 | 0 | 0.00% | 0.00% | KONTRAK | SOLD (debu ≤0,5%) |
| 16 | `0xf3389601114d8a904d3e4e2cf91426b347699f04` | 60017125 | 2025-09-04 18:42:22 UTC / 2025-09-05 01:42:22 WIB | 0 | 0 | 0.00% | n/a (beli=0) | EOA | SOLD (debu ≤0,5%) |
| 17 | `0x899ec4a0c4ee1db985ceeef9bb313c091ea3deb9` | 60017371 | 2025-09-04 18:45:26 UTC / 2025-09-05 01:45:26 WIB | 154.1480 | 0 | 0.00% | 0.00% | KONTRAK | SOLD (debu ≤0,5%) |
| 18 | `0xc590175e458b83680867afd273527ff58f74c02b` | 60017375 | 2025-09-04 18:45:29 UTC / 2025-09-05 01:45:29 WIB | 49.0748 | 0 | 0.00% | 0.00% | KONTRAK | SOLD (debu ≤0,5%) |
| 19 | `0x38fd39dce70c83a05f6d4de08e6ec56f732f4b09` | 60021650 | 2025-09-04 19:38:56 UTC / 2025-09-05 02:38:56 WIB | 332.5723 | 0 | 0.00% | 16.21% | KONTRAK | SOLD (debu ≤0,5%) |
| 20 | `0x653b40ab9dd1d1b42845f67f2be617b2445b7ea5` | 60022733 | 2025-09-04 19:52:28 UTC / 2025-09-05 02:52:28 WIB | 14.4610 | 0 | 0.00% | 264.03% | KONTRAK | SOLD (debu ≤0,5%) |
| 21 | `0x33f3184168de4a75a3f64a1dc86b73e4eb4c7a43` | 60038472 | 2025-09-04 23:09:13 UTC / 2025-09-05 06:09:13 WIB | 1,302.72 | 0.00000000 | 0.00% | 0.00% | KONTRAK | SOLD (debu ≤0,5%) |
| 22 | `0x4b1b2ea60cc20a171cb7eed8fe0de988f79651d2` | 60055770 | 2025-09-05 02:45:29 UTC / 2025-09-05 09:45:29 WIB | 423.9995 | 0.00000000 | 0.00% | 31.08% | KONTRAK | SOLD (debu ≤0,5%) |
| 23 | `0xe3f2aea7f9615dc110cd9bad48248ffdc7178f8a` | 60058725 | 2025-09-05 03:22:25 UTC / 2025-09-05 10:22:25 WIB | 179.2010 | 0 | 0.00% | 0.00% | KONTRAK | SOLD (debu ≤0,5%) |
| 24 | `0xa14c1e5efbc410c166d5643aca50d2f42824a18d` | 60063861 | 2025-09-05 04:26:39 UTC / 2025-09-05 11:26:39 WIB | 416.7306 | 0.34178432 | 0.08% | 0.00% | KONTRAK | SOLD (debu ≤0,5%) |
| 25 | `0x927f64c33f48de56577fb08c87b58c66a038f53e` | 60077452 | 2025-09-05 07:16:35 UTC / 2025-09-05 14:16:35 WIB | 197.7716 | 0 | 0.00% | 0.00% | KONTRAK | SOLD (debu ≤0,5%) |
| 26 | `0x7a8698dab718de34943d6e419f97e7c92ce9ad24` | 60110234 | 2025-09-05 14:06:23 UTC / 2025-09-05 21:06:23 WIB | 390.7661 | 0 | 0.00% | 0.00% | KONTRAK | SOLD (debu ≤0,5%) |
| 27 | `0x76c3ab3aead88bb361199d9c6f9baed6fbaeeb99` | 60121497 | 2025-09-05 16:27:11 UTC / 2025-09-05 23:27:11 WIB | 124.4009 | 0 | 0.00% | 0.00% | EOA | SOLD (debu ≤0,5%) |
| 28 | `0x6ce839f0bfced47dbaacf3aba10728334a9752a2` | 60142686 | 2025-09-05 20:52:03 UTC / 2025-09-06 03:52:03 WIB | 279.1305 | 0 | 0.00% | 0.00% | KONTRAK | SOLD (debu ≤0,5%) |
| 29 | `0xea305f9cfbfec9be5a4de0300273466840a76e23` | 60150695 | 2025-09-05 22:32:10 UTC / 2025-09-06 05:32:10 WIB | 324.2239 | 0.00000000 | 0.00% | 0.00% | KONTRAK | SOLD (debu ≤0,5%) |
| 30 | `0x26cf31dab94c5163f775d85838aafc5a4b23c80f` | 60161306 | 2025-09-06 00:44:48 UTC / 2025-09-06 07:44:48 WIB | 974.5389 | 0.29835529 | 0.03% | 0.00% | KONTRAK | SOLD (debu ≤0,5%) |

### Daftar coret

- `0x2ea94a042461940fb59cc7260bb85342891fb5eb` — kontrak/bot executor (beli awal 6 jam 1,317.26, saldo 0.00000000, 0.00% dipegang).
- `0x144d395b5562c742259932d2ee6e1d8d092a21b8` — kontrak/bot executor (beli awal 6 jam 710.3883, saldo 11,023.36, 1551.74% dipegang).
- `0x6b080b294bfb2d908595e12068c8d054f58f9a76` — kontrak/bot executor (beli awal 6 jam 502.7291, saldo 0.00000000, 0.00% dipegang).
- `0x6b3affc894b0d2d566e5ff03ad79188f1b65bfff` — kontrak/bot executor (beli awal 6 jam 582.6777, saldo 0.00000000, 0.00% dipegang).
- `0xfff4857a955b2b460c27fd431aa5a85fabca5559` — kontrak/bot executor (beli awal 6 jam 1,092.20, saldo 25,802,157.31, 2362412.96% dipegang).
- `0x9999b0cdd35d7f3b281ba02efc0d228486940515` — kontrak/bot executor (beli awal 6 jam 1,249.74, saldo 0, 0.00% dipegang).
- `0x6483d86d075b1a657664444363ad94144a01deea` — kontrak/bot executor (beli awal 6 jam 118.5370, saldo 0.00000000, 0.00% dipegang).
- `0xb5cb05550357a4ac6c095d96a19bce513ba5ac04` — kontrak/bot executor (beli awal 6 jam 414.1176, saldo 0.00000000, 0.00% dipegang).
- `0xbd99f73a3b4cd763ec40f66fa5a7a6014cf669da` — kontrak/bot executor (beli awal 6 jam 397.4579, saldo 0, 0.00% dipegang).
- `0x7ac30f228b3bd2295c7b1d6b3ce2006e255245ec` — kontrak/bot executor (beli awal 6 jam 30.4468, saldo 0, 0.00% dipegang).
- `0xb56013770dd5b2fc90f397f1c27396c783f277e5` — kontrak/bot executor (beli awal 6 jam 419.8728, saldo 0, 0.00% dipegang).
- `0x04b4f0de2e0efd3ee884c35c6e91e15d9328a78f` — kontrak/bot executor (beli awal 6 jam 85.2995, saldo 0, 0.00% dipegang).
- `0x10ed43c718714eb63d5aa57b78b54704e256024e` — kontrak/bot executor (beli awal 6 jam 42,981.96, saldo 0, 0.00% dipegang).
- `0xba53da030f3504db8cf0309bb89791950d0ce5e6` — kontrak/bot executor (beli awal 6 jam 253.7879, saldo 39.8750, 15.71% dipegang).
- `0x5dda609d62fce85d50a406a447cd28590c8042fe` — kontrak/bot executor (beli awal 6 jam 210.0275, saldo 0, 0.00% dipegang).
- `0x899ec4a0c4ee1db985ceeef9bb313c091ea3deb9` — kontrak/bot executor (beli awal 6 jam 154.1480, saldo 0, 0.00% dipegang).
- `0xc590175e458b83680867afd273527ff58f74c02b` — kontrak/bot executor (beli awal 6 jam 49.0748, saldo 0, 0.00% dipegang).
- `0x38fd39dce70c83a05f6d4de08e6ec56f732f4b09` — kontrak/bot executor (beli awal 6 jam 332.5723, saldo 0, 0.00% dipegang).
- `0x653b40ab9dd1d1b42845f67f2be617b2445b7ea5` — kontrak/bot executor (beli awal 6 jam 14.4610, saldo 0, 0.00% dipegang).
- `0x33f3184168de4a75a3f64a1dc86b73e4eb4c7a43` — kontrak/bot executor (beli awal 6 jam 1,302.72, saldo 0.00000000, 0.00% dipegang).
- `0x4b1b2ea60cc20a171cb7eed8fe0de988f79651d2` — kontrak/bot executor (beli awal 6 jam 423.9995, saldo 0.00000000, 0.00% dipegang).
- `0xe3f2aea7f9615dc110cd9bad48248ffdc7178f8a` — kontrak/bot executor (beli awal 6 jam 179.2010, saldo 0, 0.00% dipegang).
- `0xa14c1e5efbc410c166d5643aca50d2f42824a18d` — kontrak/bot executor (beli awal 6 jam 416.7306, saldo 0.34178432, 0.08% dipegang).
- `0x927f64c33f48de56577fb08c87b58c66a038f53e` — kontrak/bot executor (beli awal 6 jam 197.7716, saldo 0, 0.00% dipegang).
- `0x7a8698dab718de34943d6e419f97e7c92ce9ad24` — kontrak/bot executor (beli awal 6 jam 390.7661, saldo 0, 0.00% dipegang).
- `0x6ce839f0bfced47dbaacf3aba10728334a9752a2` — kontrak/bot executor (beli awal 6 jam 279.1305, saldo 0, 0.00% dipegang).
- `0xea305f9cfbfec9be5a4de0300273466840a76e23` — kontrak/bot executor (beli awal 6 jam 324.2239, saldo 0.00000000, 0.00% dipegang).
- `0x26cf31dab94c5163f775d85838aafc5a4b23c80f` — kontrak/bot executor (beli awal 6 jam 974.5389, saldo 0.29835529, 0.03% dipegang).

### Daftar bersih (hold bermakna + EOA + bukan daftar coret)

Definisi di sini: saldo >0,5% beli awal 6 jam (bukan SOLD), `eth_getCode` kosong (EOA), dan tidak masuk daftar coret di atas. Wallet yang sudah terpantau tetap bisa masuk daftar bersih bila memenuhi syarat, tapi ditandai — koordinator yang memutuskan apakah itu "baru".

- (tidak ada — semua first-30 adalah kontrak, SOLD, atau masuk daftar coret)

### Gagal baca

- Ankr `ankr_getLogs` pair→wallet: nihil. Ankr `ankr_getLogs` wallet→pair (per pembeli): nihil. `balanceOf`/`eth_getCode`/header blok: nihil. Timestamp header vs timestamp log Ankr untuk 30 beli pertama: 0 mismatch.

## AIN

- **CA (persis dari tugas):** `0x9558a9254890b2a8b057a789f413631b9084f4a3` — mcap GeckoTerminal 2026-11-02 17:35 WIB: ~$50,3 juta.
- **Pair V2 terverifikasi:** `0xd18ed1a49b3488550d0be01c5a010b26363c52a0` — `getPair(token, WBNB 0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c)` on-chain + `PairCreated` factory di blok 52977374 (2025-07-05T15:54:00Z (blok 52977374)). Pair USDT V2 lain: AIN: `0xa70e798ca59ca9496c81be2a8eb393d9aa949d8f` (PairCreated blok 52977851, 2025-07-05T15:59:58Z).
- **Status pasar-pertama: BUKAN pasar pertama.** Pool GeckoTerminal paling awal yang terdaftar: 2025-07-04T12:46:04Z PancakeSwap V3 AIN/USDT 0.01% (pool 0xf4262c4dbf524f53851a5176bdc7d6c1e0fa82d8c). Pair V2 ini dibuat setelahnya. (Endpoint GeckoTerminal `tokens/<CA>/pools` berhasil dibaca; daftar lengkap 20 pool pertama dicatat di log kerja, hanya pool paling awal + pair V2 yang dikutip di sini agar file tetap terbaca.)
- **Jendela scan V2:** blok 52977374 s.d. 56977373 (chunk 10.000 blok, Ankr `ankr_getLogs`, pageSize 1000, tidak ada cap-hit, tidak ada gagal baca). Log pair→wallet dalam jendela: 517.
- **Rentang beli pertama first-30:** 2025-07-05 15:55:17 UTC / 2025-07-05 22:55:17 WIB s.d. 2025-08-02 06:55:07 UTC / 2025-08-02 13:55:07 WIB.

### Tabel 30 pembeli pertama (pair V2, kronologis)

| # | Alamat lengkap | Blok beli pertama | Waktu beli pertama (UTC / WIB) | Beli awal 6 jam | Saldo sekarang | % dipegang | % jual ≤1 jam | EOA/kontrak | Tanda |
|---|---|---|---|---|---|---|---|---|---|
| 1 | `0x144d395b5562c742259932d2ee6e1d8d092a21b8` | 52977477 | 2025-07-05 15:55:17 UTC / 2025-07-05 22:55:17 WIB | 9.6801 | 1,195.73 | 12352.43% | 0.00% | KONTRAK | — |
| 2 | `0xb673e20e8063174e3fe74cfec6dda047a4c5ec08` | 52977489 | 2025-07-05 15:55:26 UTC / 2025-07-05 22:55:26 WIB | 16.1023 | 0.45729723 | 2.84% | 0.00% | KONTRAK | — |
| 3 | `0xfdcfd4abfe00f94d004c64b77172f742e41c38d9` | 52977632 | 2025-07-05 15:57:13 UTC / 2025-07-05 22:57:13 WIB | 2.5531 | 0 | 0.00% | 0.00% | KONTRAK | SOLD (debu ≤0,5%) |
| 4 | `0xd9c4d8260b941351afd28b287055d5f86c963d2f` | 52977664 | 2025-07-05 15:57:37 UTC / 2025-07-05 22:57:37 WIB | 2,601.69 | 0 | 0.00% | 45.43% | EOA | SOLD (debu ≤0,5%) |
| 5 | `0x18e31a59caeae97fa9a30a20df3f72a130147752` | 52977738 | 2025-07-05 15:58:33 UTC / 2025-07-05 22:58:33 WIB | 0.02572564 | 0.02572564 | 100.00% | 0.00% | EOA | — |
| 6 | `0x29a4b61a493ca34ab367594594a730fddd131bfa` | 52977770 | 2025-07-05 15:58:57 UTC / 2025-07-05 22:58:57 WIB | 0.01878428 | 0.01878428 | 100.00% | 0.00% | EOA | — |
| 7 | `0x426603bac5e0ea73fd13aecad7a80c9f963f6eac` | 52977844 | 2025-07-05 15:59:52 UTC / 2025-07-05 22:59:52 WIB | 0.09218618 | 0.82439256 | 894.27% | 0.00% | KONTRAK | — |
| 8 | `0x779a74436eda060911b2c4f209d34ea155f3df09` | 52983221 | 2025-07-05 17:07:05 UTC / 2025-07-06 00:07:05 WIB | 0.05682221 | 0 | 0.00% | 0.00% | KONTRAK | SOLD (debu ≤0,5%) |
| 9 | `0x9be520b4ee9f702dbafe21eede032f2454010498` | 52984867 | 2025-07-05 17:27:40 UTC / 2025-07-06 00:27:40 WIB | 0.00017216 | 0 | 0.00% | 0.00% | KONTRAK | SOLD (debu ≤0,5%) |
| 10 | `0x6b3affc894b0d2d566e5ff03ad79188f1b65bfff` | 52985554 | 2025-07-05 17:36:15 UTC / 2025-07-06 00:36:15 WIB | 24.4125 | 0 | 0.00% | 0.00% | KONTRAK | SOLD (debu ≤0,5%) |
| 11 | `0x9653628b7ac01e375e085b02b9998d86d08f9bd9` | 53016905 | 2025-07-06 00:08:12 UTC / 2025-07-06 07:08:12 WIB | 0.06426983 | 0.00192438 | 2.99% | 0.00% | KONTRAK | — |
| 12 | `0xa70e798ca59ca9496c81be2a8eb393d9aa949d8f` | 53035118 | 2025-07-06 03:55:51 UTC / 2025-07-06 10:55:51 WIB | 0.00281371 | 1.8185 | 64629.46% | 829.23% | KONTRAK | — |
| 13 | `0xf197da97df68f6e72264d340a820e8efd301e1a4` | 53035902 | 2025-07-06 04:05:39 UTC / 2025-07-06 11:05:39 WIB | 0.01032321 | 0 | 0.00% | 0.00% | KONTRAK | SOLD (debu ≤0,5%) |
| 14 | `0xf4262c4dbf524f53851a5176bdc7d6c1e0fa82d8` | 53231494 | 2025-07-07 20:50:42 UTC / 2025-07-08 03:50:42 WIB | 1.0219 | 371,617.47 | 36366921.58% | 14630.89% | KONTRAK | — |
| 15 | `0xb21a7d6b07ad608202c5c057031a034bf4166b38` | 53231499 | 2025-07-07 20:50:45 UTC / 2025-07-08 03:50:45 WIB | 0.08751488 | 2.9019 | 3315.84% | 0.00% | KONTRAK | — |
| 16 | `0x653b40ab9dd1d1b42845f67f2be617b2445b7ea5` | 53536448 | 2025-07-10 12:22:49 UTC / 2025-07-10 19:22:49 WIB | 0.03930839 | 0 | 0.00% | 0.00% | KONTRAK | SOLD (debu ≤0,5%) |
| 17 | `0xda0b66ebf02c7830953f49085db217ad122fcc2a` | 53599742 | 2025-07-11 01:34:01 UTC / 2025-07-11 08:34:01 WIB | 0.03102400 | 11,509.09 | 37097376.25% | 139.64% | KONTRAK | — |
| 18 | `0xb300000b72deaeb607a12d5f54773d1c19c7028d` | 53618617 | 2025-07-11 05:29:58 UTC / 2025-07-11 12:29:58 WIB | 0.09490308 | 0 | 0.00% | 1053.71% | KONTRAK | SOLD (debu ≤0,5%) |
| 19 | `0x9b69b82b91d9d610d53b41fc69146d6f96101be8` | 53688284 | 2025-07-11 20:00:51 UTC / 2025-07-12 03:00:51 WIB | 0.03325125 | 22.1576 | 66637.00% | 0.00% | EOA | — |
| 20 | `0x1e3936b691e27060e55d45deb2cfc891503b087b` | 53764214 | 2025-07-12 11:50:02 UTC / 2025-07-12 18:50:02 WIB | 0.00097180 | 0 | 0.00% | 3472.36% | KONTRAK | SOLD (debu ≤0,5%) |
| 21 | `0x3477efae0d5f9f306d857998e4ada67a2f5f7975` | 53830997 | 2025-07-13 01:44:53 UTC / 2025-07-13 08:44:53 WIB | 0.05387022 | 0.05387022 | 100.00% | 0.00% | EOA | — |
| 22 | `0x38a183074870bc7a89616e5cf4a0565bfda5e133` | 53833252 | 2025-07-13 02:13:04 UTC / 2025-07-13 09:13:04 WIB | 0.00077113 | 0 | 0.00% | 239.37% | KONTRAK | SOLD (debu ≤0,5%) |
| 23 | `0x6e4141d33021b52c91c28608403db4a0ffb50ec6` | 54914696 | 2025-07-22 11:32:32 UTC / 2025-07-22 18:32:32 WIB | 0.23053335 | 0.00000000 | 0.00% | 0.00% | KONTRAK | SOLD (debu ≤0,5%) |
| 24 | `0x0000000000367715a1c746bd336b65e5954c7660` | 54955217 | 2025-07-22 19:59:07 UTC / 2025-07-23 02:59:07 WIB | 0.54269766 | 0 | 0.00% | 0.00% | KONTRAK | SOLD (debu ≤0,5%) |
| 25 | `0xb80ccaa913d36757fe7b6251333113e650a11867` | 54967506 | 2025-07-22 22:32:44 UTC / 2025-07-23 05:32:44 WIB | 0.15810939 | 0 | 0.00% | 0.00% | KONTRAK | SOLD (debu ≤0,5%) |
| 26 | `0xf2551d6b70ed9fa74f5a16cc1787ff1328cf5db6` | 55018423 | 2025-07-23 09:09:16 UTC / 2025-07-23 16:09:16 WIB | 0.32245261 | 52.1547 | 16174.37% | 762.48% | KONTRAK | — |
| 27 | `0xb5cb05550357a4ac6c095d96a19bce513ba5ac04` | 55065067 | 2025-07-23 18:52:23 UTC / 2025-07-24 01:52:23 WIB | 0.22114672 | 0 | 0.00% | 0.00% | KONTRAK | SOLD (debu ≤0,5%) |
| 28 | `0xf4caadd3397ebb286268feaf69c297f98030fde3` | 55207012 | 2025-07-25 00:26:55 UTC / 2025-07-25 07:26:55 WIB | 8.3559 | 0 | 0.00% | 0.00% | EOA | SOLD (debu ≤0,5%) |
| 29 | `0x081df5b08fd64abee82c34c0dee72084d01c3987` | 56078288 | 2025-08-01 13:59:03 UTC / 2025-08-01 20:59:03 WIB | 39.8760 | 0 | 0.00% | 0.23% | KONTRAK | SOLD (debu ≤0,5%) |
| 30 | `0x927f64c33f48de56577fb08c87b58c66a038f53e` | 56159570 | 2025-08-02 06:55:07 UTC / 2025-08-02 13:55:07 WIB | 89.5667 | 0 | 0.00% | 0.00% | KONTRAK | SOLD (debu ≤0,5%) |

### Daftar coret

- `0x144d395b5562c742259932d2ee6e1d8d092a21b8` — kontrak/bot executor (beli awal 6 jam 9.6801, saldo 1,195.73, 12352.43% dipegang).
- `0xb673e20e8063174e3fe74cfec6dda047a4c5ec08` — kontrak/bot executor (beli awal 6 jam 16.1023, saldo 0.45729723, 2.84% dipegang).
- `0xfdcfd4abfe00f94d004c64b77172f742e41c38d9` — kontrak/bot executor (beli awal 6 jam 2.5531, saldo 0, 0.00% dipegang).
- `0x426603bac5e0ea73fd13aecad7a80c9f963f6eac` — kontrak/bot executor (beli awal 6 jam 0.09218618, saldo 0.82439256, 894.27% dipegang).
- `0x779a74436eda060911b2c4f209d34ea155f3df09` — kontrak/bot executor (beli awal 6 jam 0.05682221, saldo 0, 0.00% dipegang).
- `0x9be520b4ee9f702dbafe21eede032f2454010498` — kontrak/bot executor (beli awal 6 jam 0.00017216, saldo 0, 0.00% dipegang).
- `0x6b3affc894b0d2d566e5ff03ad79188f1b65bfff` — kontrak/bot executor (beli awal 6 jam 24.4125, saldo 0, 0.00% dipegang).
- `0x9653628b7ac01e375e085b02b9998d86d08f9bd9` — kontrak/bot executor (beli awal 6 jam 0.06426983, saldo 0.00192438, 2.99% dipegang).
- `0xa70e798ca59ca9496c81be2a8eb393d9aa949d8f` — kontrak/bot executor (beli awal 6 jam 0.00281371, saldo 1.8185, 64629.46% dipegang).
- `0xf197da97df68f6e72264d340a820e8efd301e1a4` — kontrak/bot executor (beli awal 6 jam 0.01032321, saldo 0, 0.00% dipegang).
- `0xf4262c4dbf524f53851a5176bdc7d6c1e0fa82d8` — kontrak/bot executor (beli awal 6 jam 1.0219, saldo 371,617.47, 36366921.58% dipegang).
- `0xb21a7d6b07ad608202c5c057031a034bf4166b38` — kontrak/bot executor (beli awal 6 jam 0.08751488, saldo 2.9019, 3315.84% dipegang).
- `0x653b40ab9dd1d1b42845f67f2be617b2445b7ea5` — kontrak/bot executor (beli awal 6 jam 0.03930839, saldo 0, 0.00% dipegang).
- `0xda0b66ebf02c7830953f49085db217ad122fcc2a` — kontrak/bot executor (beli awal 6 jam 0.03102400, saldo 11,509.09, 37097376.25% dipegang).
- `0xb300000b72deaeb607a12d5f54773d1c19c7028d` — kontrak/bot executor (beli awal 6 jam 0.09490308, saldo 0, 0.00% dipegang).
- `0x1e3936b691e27060e55d45deb2cfc891503b087b` — kontrak/bot executor (beli awal 6 jam 0.00097180, saldo 0, 0.00% dipegang).
- `0x38a183074870bc7a89616e5cf4a0565bfda5e133` — kontrak/bot executor (beli awal 6 jam 0.00077113, saldo 0, 0.00% dipegang).
- `0x6e4141d33021b52c91c28608403db4a0ffb50ec6` — kontrak/bot executor (beli awal 6 jam 0.23053335, saldo 0.00000000, 0.00% dipegang).
- `0x0000000000367715a1c746bd336b65e5954c7660` — kontrak/bot executor (beli awal 6 jam 0.54269766, saldo 0, 0.00% dipegang).
- `0xb80ccaa913d36757fe7b6251333113e650a11867` — kontrak/bot executor (beli awal 6 jam 0.15810939, saldo 0, 0.00% dipegang).
- `0xf2551d6b70ed9fa74f5a16cc1787ff1328cf5db6` — kontrak/bot executor; pool V2 lain (beli awal 6 jam 0.32245261, saldo 52.1547, 16174.37% dipegang).
- `0xb5cb05550357a4ac6c095d96a19bce513ba5ac04` — kontrak/bot executor (beli awal 6 jam 0.22114672, saldo 0, 0.00% dipegang).
- `0x081df5b08fd64abee82c34c0dee72084d01c3987` — kontrak/bot executor (beli awal 6 jam 39.8760, saldo 0, 0.00% dipegang).
- `0x927f64c33f48de56577fb08c87b58c66a038f53e` — kontrak/bot executor (beli awal 6 jam 89.5667, saldo 0, 0.00% dipegang).

### Daftar bersih (hold bermakna + EOA + bukan daftar coret)

Definisi di sini: saldo >0,5% beli awal 6 jam (bukan SOLD), `eth_getCode` kosong (EOA), dan tidak masuk daftar coret di atas. Wallet yang sudah terpantau tetap bisa masuk daftar bersih bila memenuhi syarat, tapi ditandai — koordinator yang memutuskan apakah itu "baru".

- `0x18e31a59caeae97fa9a30a20df3f72a130147752` — beli pertama blok 52977738 (2025-07-05 15:58:33 UTC / 2025-07-05 22:58:33 WIB), beli awal 6 jam 0.02572564, saldo sekarang 0.02572564, 100.00% dipegang, jual ≤1 jam 0.00%.
- `0x29a4b61a493ca34ab367594594a730fddd131bfa` — beli pertama blok 52977770 (2025-07-05 15:58:57 UTC / 2025-07-05 22:58:57 WIB), beli awal 6 jam 0.01878428, saldo sekarang 0.01878428, 100.00% dipegang, jual ≤1 jam 0.00%.
- `0x9b69b82b91d9d610d53b41fc69146d6f96101be8` — beli pertama blok 53688284 (2025-07-11 20:00:51 UTC / 2025-07-12 03:00:51 WIB), beli awal 6 jam 0.03325125, saldo sekarang 22.1576, 66637.00% dipegang, jual ≤1 jam 0.00%.
- `0x3477efae0d5f9f306d857998e4ada67a2f5f7975` — beli pertama blok 53830997 (2025-07-13 01:44:53 UTC / 2025-07-13 08:44:53 WIB), beli awal 6 jam 0.05387022, saldo sekarang 0.05387022, 100.00% dipegang, jual ≤1 jam 0.00%.

### Gagal baca

- Ankr `ankr_getLogs` pair→wallet: nihil. Ankr `ankr_getLogs` wallet→pair (per pembeli): nihil. `balanceOf`/`eth_getCode`/header blok: nihil. Timestamp header vs timestamp log Ankr untuk 30 beli pertama: 0 mismatch.

## JCT (JANCTION) — GAGAL TOTAL untuk metode V2

- **CA (persis dari tugas):** `0xea37a8de1de2d9d10772eeb569e28bfa5cb17707` — mcap GeckoTerminal 2026-11-02 17:35 WIB: ~$46,6 juta.
- **Verifikasi pair V2 GAGAL:** `getPair(JCT, WBNB)` on-chain = `0x0000000000000000000000000000000000000000`. Diperiksa juga `getPair` dengan USDT `0x55d398326f99059fF775485246999027B3197955`, USD1 `0x8d0D000Ee6f352CB20e9B7c4d1D6fF5846FdC9e9`, USDC `0x8AC76a51cc950d9822D68b83fE1Ad97B32Cd580d`, BUSD `0xe9e7CEA3DedcA5984780Bafc599bD69ADd087D56` — semuanya 0. `PairCreated` factory untuk kelima pasangan itu juga nihil. Tidak ada pair V2 yang bisa dipakai sebagai "pengirim = pair" untuk langkah (c) — scan first-30 V2 TIDAK DAPAT DIJALANKAN dan TIDAK DIKARANG dari pool lain.
- **GeckoTerminal (endpoint `tokens/<CA>/pools`, berhasil dibaca, halaman 1–5 = 100 pool):** TIDAK ADA satu pun pool `pancakeswap_v2` di 100 pool tersebut; semuanya V3/V4/Infinity-CLMM/Uniswap. Pool dengan tanggal 2026-06-03 yang disebut tugas adalah `JCT / USDT 0.007%` PancakeSwap Infinity CLMM (pool id `bsc_0x7bb2f6dab157e444ad8717b0178035c1b1cf24958b37c2a205e61a3582283249`, dibuat 2026-06-03T15:17:17Z) — id-nya lebih panjang dari 20 byte, sesuai peringatan tugas, dan BUKAN pair V2. Lebih jauh lagi, pool-pool 2025-11-09/10 (mis. Infinity CLMM USDT 0.007% 2025-11-09T08:17:52Z dan puluhan pool Uniswap V4 2025-11-10) LEBIH AWAL dari 2026-06-03 — jadi tanggal tugas itu bukan pool paling awal JCT, melainkan (diduga) pool acuan koordinator. Status pasar-pertama V2 untuk JCT: TIDAK DAPAT DINILAI karena pair V2 tidak ada; pasar pertamanya yang sebenarnya ada di luar metode V2 dan di luar tugas ini.
- **Kesimpulan JCT:** laporkan sebagai gagal total (pair tak terverifikasi). Bila koordinator menghendaki first-30 JCT, perlu tugas baru dengan metode pool V3/V4/CLMM yang berbeda — bukan ekstrapolasi dari data V2 ini.

## Gagal baca global

- Tidak ada gagal baca pada 4 koin yang berhasil (Ankr, fast_rpc, GeckoTerminal semua menjawab). Satu-satunya "gagal" adalah JCT di atas — itu kegagalan verifikasi (pair tidak ada), bukan gagal baca, dan dicatat apa adanya.

## Catatan untuk koordinator (bukan penilaian funding)

- Overlap dengan set terpantau (50 wallet) dan label TRIO/PAIR/IBS #2/BORT #8/GANG sudah ditandai per baris di tabel; rekap overlap ada di bawah ini (dihitung dari tabel, bukan dari memori).
- **Skala saldo daftar bersih — baca sebelum memakai daftar bersih:** daftar bersih di file ini mengikuti definisi formal tugas (saldo >0,5% beli awal 6 jam = bukan SOLD, EOA, bukan daftar coret), TANPA ambang dolar — karena tugas tidak memberi ambang $ dan harga/supply per token tidak dihitung di sini. Akibatnya sebagian besar entri bersih bersaldo debu: AKE #5 `0x29a4b61a493ca34ab367594594a730fddd131bfa` saldo ~0,000000 token (beli awal ~0,000000 token, 100% dipegang — praktis debu, bukan posisi bermakna secara dolar); Q #10 wallet yang sama saldo 0,1598 Q; AIN #5 saldo 0,0257 AIN, #6 wallet yang sama saldo 0,0188 AIN, #21 saldo 0,0539 AIN. Entri bersih yang bersaldo paling besar secara token: AKE #12 `0x8ecb1a8d8fe0c0b4d1ce823210d8d61a615ec9f9` saldo 2.700,85 AKE (beli awal 6 jam hanya 0,0107 AKE — saldo sekarang berasal dari akumulasi belakangan lewat jalur lain, bukan dari beli awal V2 itu); Q #9 `0x2b40f892a5b8aefdf9868317330ca0f956f70d2b` saldo 86,97 Q; AIN #19 `0x9b69b82b91d9d610d53b41fc69146d6f96101be8` saldo 22,16 AIN. Koordinator yang memutuskan ambang bermakna dolarnya sendiri.
- Tidak ada penilaian aktif-48-jam dan tidak ada penilaian repeat-buyer lintas koin di file ini, sesuai tugas — itu kerja koordinator.
- Tidak ada klaim linkage KUAT di file ini. Bila dua wallet muncul bersama di beberapa koin, itu co-buy (LEMAH) sampai funding/transfer langsung diperiksa koordinator.

### Rekap overlap (dari tabel di atas)

- **AKE:** sudah-terpantau: 0 — tidak ada; label khusus TRIO/PAIR/IBS/BORT/GANG: 0 — tidak ada; hub sniper/funder: 0.
- **Q:** sudah-terpantau: 0 — tidak ada; label khusus TRIO/PAIR/IBS/BORT/GANG: 0 — tidak ada; hub sniper/funder: 0.
- **IDOL:** sudah-terpantau: 0 — tidak ada; label khusus TRIO/PAIR/IBS/BORT/GANG: 0 — tidak ada; hub sniper/funder: 0.
- **AIN:** sudah-terpantau: 0 — tidak ada; label khusus TRIO/PAIR/IBS/BORT/GANG: 0 — tidak ada; hub sniper/funder: 0.

---
File mentah kerja (bukan untuk user, hanya jejak): `/tmp/first30_raw_*.json`, `/tmp/first30_computed_*.json`, log `/tmp/phaseA2.log`. File bukti ini satu-satunya output permanen di workspace.