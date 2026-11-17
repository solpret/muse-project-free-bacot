# Metode 3 — Top holder koin terbentuk via BscScan (2026-11-03)

Tujuan: irisan top-50 holder di ≥3 dari 14 koin metode 1 + status holding alamat bernama (WATCH f16b, bot 9999, kuartet klaster, hub, provisioner).
Cara: baca halaman Holders BscScan per token, read-only, tanpa login/wallet/sign.

## Hasil: SEBAGIAN — 3 dari 15 token terbaca, 12 UNREAD

Tiga percobaan berturut-turut gagal menyelesaikan metode ini (run 1: hanya AKE; kontinuitas 1: mati ~2 menit; kontinuitas 2: 15:34–16:40 WIB, 3 token selesai lalu tugas gagal total). Penyebab: Cloudflare "Verify you are human" berputar (klik → verifikasi → reset ke tantangan baru) atau menolak eksplisit "Incorrect device time" (jam perangkat environment salah); jatah pindah environment tugas ini habis. UNREAD = tidak terbaca, BUKAN kosong/tidak ada.

### Token yang terbaca penuh

AKE (0x2c3a8ee94ddd97244a93bc48298f97d2c412f7db) — 41.896 holder, top-10:
1. 0x27333Bd8c321a263B0565e69eea3b736b9d1f42c — 13,3734%
2. 0xD229b65d50E412cC3C394233E7a53A1DAc4dA457 — 6,0477%
3. 0xca9A3c9542761E8d1C0A3D7691bAAd0447637401 — 4,2327%
4. 0xB8210c25df20921538eA35729Badc3e0A63520f1 — 4,1148%
5. 0x57114155891605D9c5a2907e2B702cF60AB07c0e — 3,4703%
6. 0x3E2BD24eA2aabf4311C3cA61bF5Ce290fF52a448 — 3,4116%
7. 0x73D8bD54F7Cf5FAb43fE4Ef40A62D390644946Db (Binance: Alpha 2.0 Router Proxy, Exchange) — 3,2002%
8. 0x55a3319b1cFE8B82Cacb0b5cF96C7445Bf12066a — 2,7987%
9. 0xA9578b2b9dDCD0465cDc05140b3821032B5A722B — 2,4491%
10. 0xaf6bC591Cd10E62c74497Bd5F9904329EcB59da1 — 2,1042%

IDOL / MEET48 Token (0x3b4de3c7855c03bb9f50ea252cd2c9fa1125ab07) — 315.086 holder, top-10 (baris 11–25 juga diperiksa, tidak ada alamat bernama):
1. 0x93e5fd8C2B99EE937022cbf6c9564CB2cc795755 — 27,9042%
2. 0xb6e78Db8187D316851b803a0F2f43d480bF4a656 — 13,8750%
3. 0x32a7EE7F5edEC39d467016E004C216cE1C034F9f — 11,8750%
4. Gate 5 (Exchange) — 4,5804%
5. 0x118f58F20898B0EfA0C07B388C0CdaEc3f796344 — 4,2958%
6. 0xaDFffc33cdC9970349CBcEa3D73Ec343d6ed116D — 3,9341%
7. 0x93dEb693b170d56BdDe1B0a5222B14c0F885d976 — 3,2169%
8. 0x0363F1DA9739615f928605406dcF25004DCc1b04 — 3,1667%
9. 0x178c8E92d801b94d5183752452cc1A4682B744DE — 3,1250%
10. Binance: Alpha 2.0 Router Proxy (Exchange) — 2,6510%

AIN / Infinity Ground AI (0x9558a9254890b2a8b057a789f413631b9084f4a3) — 19.167 holder, top-10 (baris 11–25 juga diperiksa, tidak ada alamat bernama):
1. Binance: Alpha 2.0 Router Proxy (Exchange) — 25,9368%
2. 0xAe006EE8e46Da3325f02a61dEaeB911C769fe086 — 20,0000%
3. 0x840a406FA125f7Acc738B00350bBe67C8D812295 — 7,1638%
4. 0x89F97c4606069ac01502E7697C58eDb758C09C65 — 6,9724%
5. 0x66bFF73a29EEDd432163cc627dc36f70F89E3A37 — 4,8735%
6. Gate 5 (Exchange) — 4,3175%
7. 0x8047a4b87D07A4fC844Bf27f3955c90989673963 — 3,9760%
8. 0x5e3Ef72492abeFe115234d0Ef61eF8468368bdb2 — 3,9748%
9. Gate 1 (Exchange) — 3,6327%
10. 0x87740BD0fab8F369B20BD520Bc369E21307f1e9e — 3,4595%

### Irisan (target ≥3 token)

TIDAK ADA alamat non-kontrak/non-exchange yang muncul di 3 token atau lebih (dari 3 token yang terbaca).
Overlap 2-token yang terdeteksi (IDOL ↔ AIN, bukan promosi — hanya 2 koin):
- 0x93dEb693b170d56BdDe1B0a5222B14c0F885d976 — IDOL #7 (3,2169%), AIN #11 (2,8458%)
- 0xaDFffc33cdC9970349CBcEa3D73Ec343d6ed116D — IDOL #6 (3,9341%), AIN #12 (1,9917%)
- 0x594FcF750721300618679303b78AD4Ca8F0bd055 — IDOL #12 (1,9792%), AIN #16 (0,7500%)
- 0x4cAd1efBFd5F0848E0c3c14FAb23F92b2FA81F17 — IDOL #20 (0,9215%), AIN #22 (0,2277%)
Binance Alpha 2.0 Router Proxy muncul di AKE #7, IDOL #10, AIN #1 — diabaikan sebagai exchange.

### Status alamat bernama (diperiksa di AKE top-10, IDOL top-25, AIN top-25)

TIDAK DITEMUKAN di ketiganya: WATCH 0xf16b4b87e6f214b60abc8e52e207c5009e14d019; bot 0x9999b0cdd35d7f3b281ba02efc0d228486940515; kuartet klaster 0x874d92be9a7966805e5de651c726f2c22dfde7d2, 0xad066bf19d4cdf7916552139f5fbda4e7e645d02, 0xe12c2e198fa28153511a7322beb75086826df9a7, 0xb735a41cf69b03d6fef807815e52880cb75cf6c2; hub 0x4982085c9e2f89f2ecb8131eca71afad896e89cb; provisioner 0x9b79cc64cd3e5ec86d951acb27ddbd9ed660cd07.
Status untuk 12 token UNREAD tidak dapat ditentukan (termasuk pertanyaan apakah hub/provisioner top holder di Q/UAI).

### Token UNREAD (12)

Q, UAI, ARIA, JAGENT, EVAA, ESPORTS, LYN, BASED, JCT, SAFU-B13B, COLLECT, AEON.

## Kesimpulan metode 3

TIDAK MENYIMPULKAN — metode ini tidak selesai: tidak ada irisan ≥3 token yang bisa diklaim, tidak ada promosi dari metode 3, dan tidak ada wallet yang ditambahkan ke feed/tier-ab dari metode ini. Data 3 token yang terbaca dicatat di atas untuk shortlist akhir gelombang. Alternatif yang dipertimbangkan untuk melengkapi: metode 4–6 (sudah diperintahkan user, berurutan), data holder via Ankr, atau menunda sisa BscScan ke percobaan browser baru di lain waktu.
