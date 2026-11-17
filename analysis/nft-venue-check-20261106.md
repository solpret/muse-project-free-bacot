# Cek Venue NFT — 2026-11-06 ~08:45 WIB (read-only)

Perintah user 2026-11-06 ~08:34 WIB: cek venue yang belum terverifikasi untuk 7 grup NFT.
Kurs: BNB **$693,86** (CoinGecko, 2026-11-06 ~08:40 WIB; DexScreener ~$694,98).
Prioritas: (1) market proyek sendiri, contract-matched, listing live terverifikasi; (2) Element sebagai fallback (API butuh x-api-key, listing manual — bukan opsi eksekusi).

## ⚠️ KOREKSI KEPEMILIKAN — penting

Bacaan live hari ini (dua sumber independen: `ownerOf` eth_call langsung + enumerasi Ankr `ankr_getNFTsByOwner` kedua wallet) membuktikan **Coracle #897/#898, Botmolt #2628, SOLVD #869/#2137, dan drop.ai #2193 semuanya ada di wallet KEDUA (tujuan) `0xcf3c6fc1bf670a8d3f03436395286f86dbee7418`, BUKAN wallet utama**. Catatan "ownerOf live 2026-11-02 membuktikan di wallet utama" sudah tidak berlaku — entah dipindah sesudah 2026-11-02 atau catatan itu keliru. Listing untuk kelima token itu (bila diputuskan) harus dari wallet kedua, bukan wallet utama.

Yang terverifikasi di wallet UTAMA `0xeb237F6f9FB4e826739F0954e9768914F28b2c2E`: Agentic Bull #322 ✓, DigDown #5361 ✓, Mars Nexus #1448 ✓.

## Ringkasan verdict

| # | NFT | Venue live? | Nilai kasar bila laku di floor |
|---|-----|-------------|-------------------------------|
| 1 | Agentic Bull #322 | ❌ Tidak ada market sendiri; situs hanya menautkan Element + OKX NFT | — (tanpa floor terverifikasi) |
| 2 | DigDown #5361 | ❌ Tidak ada market (situs + skill.md hanya mint/reveal) | — |
| 3 | Mars Nexus #1448 | ❌ Tidak terverifikasi hari ini (situs 403); dulu: butuh approval review, buku beli Miner kosong | — |
| 4 | Coracle #897 + #898 | ✅ Market sendiri LIVE, terverifikasi on-chain | ~0,0002 BNB (~$0,14) per token di klaster harga terbanyak; floor penuh terakhir 0,000035 BNB (~$0,024, 2026-10-29) |
| 5 | Botmolt #2628 | ❌ Tidak ada market/situs resmi ditemukan | — |
| 6 | drop.ai #2193 | ❌ Tidak ada venue; ini voucher rewards AIDROP Vault | — |
| 7 | SOLVD #869 + #2137 | ✅ Market sendiri LIVE, penjualan nyata | floor **0,102 USDT (~$0,10)** per token |

Hanya **Coracle dan SOLVD** yang punya venue live yang bisa dipakai. Keduanya dipegang wallet kedua.

---

## 1. Agentic Bull #322 — ❌ tidak ada market sendiri

- Kontrak `0xcd4472Af68801DE87E970A333C71da5d12E825A3`, owner = wallet utama ✓ (live `ownerOf`).
- Tier **Legendary** (1 dari 75 Legendary dari 3.000; trait: Background Gold Rush, Fur White, Horns Golden, Eyes Glowing, Accessory Crown) — dari `tokenURI` on-chain.
- Situs resmi terverifikasi: `https://agentic-bull.pages.dev` — `contractURI()` on-chain mengarah ke situs ini (`external_link`), dan `/llms.txt` situs mencetak persis kontrak `0xcd4472Af68801DE87E970A333C71da5d12E825A3` ✓. Royalty 5% (ERC-2981).
- **Tidak ada market sendiri**: situs hanya halaman mint + FAQ; satu-satunya tautan dagang adalah "Element / OKX NFT" di tabel situs. Tidak ada kontrak market di ABI (40 fungsi Sourcify: hanya mint/pricing/`royaltyInfo`, tanpa `list`/`buy`/`market`).
- Fallback: Element / OKX NFT — disebut situs proyek sendiri, tapi listing live-nya TIDAK terverifikasi (API Element butuh x-api-key; tidak ada jalur anonim). Listing di sana butuh user connect wallet manual.
- Harga acuan mint: bull ke-3 = 0,00035 BNB — BUKAN floor, jangan dipakai sebagai harga jual.

## 2. DigDown #5361 — ❌ tidak ada market

- Kontrak `0xF464550f1d744793893C0ce09b89269Ed726d796`, owner = wallet utama ✓.
- Situs resmi terverifikasi: `https://digdown.xyz` — `siteURL()` on-chain mengembalikan URL ini; halaman mencetak persis kontrak DigDown V2 `0xF464550f1d744793893C0ce09b89269Ed726d796` ✓. X: `https://x.com/digdownhash` (dari `xURL()` on-chain). Royalty 5%.
- **Tidak ada market**: homepage hanya mint / reveal / daftar miner / aktivitas; `skill.md` (`https://digdown.xyz/skill.md`) seluruhnya tentang mint + reveal, tanpa satu pun bagian market/list/jual. ABI (61 fungsi Sourcify) tanpa fungsi market.
- Catatan brief "Element disebut di situs" tidak terkonfirmasi di teks halaman maupun skill.md yang terbaca hari ini.
- Fallback: Element saja (listing live tidak terverifikasi, butuh connect manual).
- Harga acuan mint: miner 2–5 = 0,0003 BNB, 6–10 = 0,0006 BNB — BUKAN floor.

## 3. Mars Nexus #1448 — ❌ tidak terverifikasi hari ini

- Kontrak `0xC4059D2F9F6F86695896e68F3E73E1e6cC3791c8`, owner = wallet utama ✓. Tier MINER, Power Units 100 (dari `tokenURI` on-chain).
- Situs `https://marsnexus.fun` **HTTP 403 (access denied)** saat dicek 2026-11-06 ~08:40 WIB — status hari ini TIDAK terverifikasi (sama seperti catatan 2026-11-04: orderbook 403).
- Status terakhir tercatat (2026-11-04): Order Trading Market resmi dibuka, TAPI listing butuh approval review (status review tidak terbaca — bukan bukti lolos/tolak), dan buku beli tier Miner KOSONG (top buy 3,1 USDT sebelumnya sudah tidak ada). Jadi penjualan #1448 tetap terblokir saat itu.
- Tidak ada eksekusi yang diusulkan untuk item ini (rute Mars Nexus sudah dihentikan user) — ini hanya info venue.
- Catatan lain: alokasi 2.793 MARS tercatat untuk #1448 tapi belum bisa diklaim (distributor belum ter-deploy, per 2026-11-04).

## 4. Coracle #897 + #898 — ✅ market sendiri LIVE

- Kontrak `0x2FCefA216dA37751E102399aCbe1dCC86Dc96eCf`. **Owner live = wallet KEDUA `0xcf3c…7418`** (bukan wallet utama — lihat koreksi di atas). Ankr dest-wallet mengonfirmasi #897 + #898.
- Market: **CoracleMarket `0x598f5AF7Ccb5520F51848C7189402C25Ee2222b7`** — terverifikasi Sourcify exact match; `market.nft()` on-chain mengembalikan persis kontrak Coracle ✓ (contract-matched). Fungsi: `list(tokenId, price)`, `buy(tokenId)` payable, `cancel`, `isLive`, `listings`, `page`.
- Situs: `https://coracle-agents.pages.dev` — menyatakan market live, fee platform 0%, royalty 5% (penjual terima 95%), NFT non-custodial (tetap di wallet sampai terjual); `tokenURI(897)` on-chain mengarah ke `https://coracle-agents.pages.dev/meta/897.json` ✓.
- Status token user: **#897 dan #898 keduanya `isLive=false`, tidak ter-listing** (seller 0x0, harga 0).
- Floor — verifikasi hari ini SEBAGIAN (RPC flaky): dari 3.003 dari 10.000 ID yang berhasil dibaca via `page()`, **137 listing live**; harga termurah yang terbaca 0,000001 BNB (dust), lalu 0,00001 / 0,00001108 / 0,0000147 BNB; harga terbanyak: **0,001 BNB (14 listing), 0,0002 BNB (10), 0,005 BNB (8)**. 7 dari 10 chunk `page()` gagal dibaca (RPC putus). **Retry selesai ~09:00 WIB dengan chunk lebih kecil (500 ID): hanya page(0,500) yang terbaca (501 entri, 8 live, termurah 0,000014 BNB); 13 dari 14 chunk sisanya TETAP tidak terbaca.** Jadi floor cakupan penuh hari ini tidak didapat; angka di bawah memakai sampel + floor penuh 2026-10-29.
- Floor acuan terakhir cakupan penuh: **0,000035 BNB** (2026-10-29, dust dikecualikan; 573 listing live saat itu).
- Perkiraan realistis: bila #897/#898 di-list di klaster 0,0002 BNB → kotor ~$0,14 per token, bersih 95% = 0,00019 BNB (~$0,13). Di floor 0,000035 BNB → ~$0,024 per token.
- Kelayakan listing: bisa — market live, non-custodial; butuh `setApprovalForAll(CoracleMarket)` sekali dari wallet kedua (pemegang token). Harga pilihan penjual; tidak ada harga floor yang dipaksakan kontrak.

## 5. Botmolt #2628 — ❌ tidak ada market/situs ditemukan

- Kontrak `0x4A15F38c75E529205a45BD2eE57c02AFAB2F6569`. **Owner live = wallet KEDUA `0xcf3c…7418`** (bukan wallet utama). Ankr dest-wallet mengonfirmasi #2628.
- `tokenURI(2628)` on-chain: "Botmolt: 10.000 pixel agents drawn and stored fully on BNB Chain. Minted by Binance .ai Agent ID holders." — tanpa `external_link`; `contractURI()` kosong. ABI (38 fungsi Sourcify) tanpa fungsi market/situs.
- Pencarian web (nama + alamat kontrak): tidak menemukan situs resmi Botmolt — hanya daftar free-mint pihak ketiga (Substack "22 Binance Agent ID Projects", tanpa URL situs untuk Botmolt) dan token bMOLT yang berbeda. Anecdote Boltbook (hanjp.ai): untuk free-mint Agent ID sejenis, "only market is element".
- Verdict: tidak ada market sendiri terverifikasi; fallback hanya Element (listing live tidak terverifikasi, butuh connect manual).

## 6. drop.ai #2193 — ❌ tidak ada venue (voucher rewards)

- Kontrak ditemukan via enumerasi Ankr: **`0x51baA9d0e4F3318Bc2f62bB8eFC3cd65F1548654`**, nama/simbol `drop.ai`. **Owner = wallet KEDUA `0xcf3c…7418`** (Ankr dest-wallet; `ownerOf` live belum diulang untuk kontrak ini, tapi Ankr + pola kepemilikan konsisten — verifikasi `ownerOf` langsung disarankan sebelum aksi apa pun).
- Sifat token: voucher ERC-721 dari **AIDROP Vault `0xd14821c28bF17DFFAb69ff95D2b8A1cFA4479f50`** — didapat lewat `registerForRewards()` (gas only). Fungsinya pendaftaran rewards, bukan koleksi dagang.
- `contractURI()`/`tokenURI(2193)` on-chain kosong (tanpa metadata/situs). Pencarian alamat kontrak hanya menemukan postingan Boltbook tentang AIDROP Vault — tidak ada market/venue apa pun.
- Verdict: tidak ada venue live terverifikasi; fallback Element pun tidak punya bukti listing untuk voucher ini.

## 7. SOLVD #869 + #2137 — ✅ market sendiri LIVE, penjualan nyata

- Kontrak `0x59661d7F8f996f687CD98c116cCaf66eFd254076`. **Owner live = wallet KEDUA `0xcf3c…7418`** — dikonfirmasi tiga sumber: `ownerOf` eth_call, Ankr dest-wallet, DAN API resmi `api.solvd.fun/v3/token/869` + `/2137` (owner `0xcF3C…7418`).
- Situs resmi terverifikasi: `https://solvd.fun` — `skill.md` situs mencetak persis kontrak SOLVD + alamat market (lihat bawah) ✓. Market priced in USDT (BSC-USD 18 desimal).
- Market kontrak (dari `GET https://api.solvd.fun/v3/skill-meta`, cocok dengan `skill.md`):
  - Current: **`0xCEFDFCA3f5709a446b0DabCd8A74491303D6f500`** — pembeli biasa tanpa Agent ID bisa beli.
  - Legacy: `0x456F4c8060D312C12B41182f5D365a444958f321` — pembeli butuh Agent ID.
  - USDT: `0x55d398326f99059fF775485246999027B3197955`.
- **Floor live (API, index fresh block 131922606): 0,102 USDT** (token #2749; total 642 listing live). Floor yang sama juga ada di current market (contoh #3617 @ 0,102 USDT, `buyRequiresAgent=false`).
- Volume nyata: **1.375 penjualan, total volume 1.679,61 USDT** (legacy 1.355 sales / 1.675,02 USDT; current 20 sales / 4,59 USDT). Fee market 2,5% (feeBps 250) + royalty 5% (royaltyBps 500) — dipotong dari hasil penjual. Harga list diizinkan 0,01–10.000.000 USDT; listing berlaku 30 hari.
- Cross-check on-chain (kedua market): `solvd()` ✓, `paymentToken()` = USDT ✓, `feeBps()` 250, `paused()` false, `MIN_PRICE()` 0,01 USDT; current `listingCount()` 110 / `totalSales()` 20 / `totalVolume()` 4,59 USDT; legacy `listingCount()` 614 / `totalSales()` 1.355 / `totalVolume()` 1.675,02 USDT. (Jumlah listing on-chain sedikit di atas API — kemungkinan listing kedaluwarsa yang belum dibersihkan; angka API 642 dipakai sebagai listing live.)
- Status token user: **#869 dan #2137 keduanya TIDAK ter-listing** di kedua market (`isListingLive=false`, seller 0x0, harga 0 — on-chain + API `listing:null`). Keduanya `revealed=true`, `transferable=true`, `lastSale=null`. Trait: #869 Tier 2 (Steel/Ink, Signal Volt), #2137 Tier 4 (Peach/Ink, Signal Blue); `Rare: none` keduanya.
- Kelayakan listing: BISA. Syarat: (a) listing dari wallet kedua (pemegang token); (b) `setApprovalForAll(current market, true)` sekali — **peringatan dari skill.md resmi: setiap panggilan `setApprovalForAll` (nilai apa pun, operator mana pun) MEMBUNUHKAN SEMUA listing user di semua market secara permanen** — user saat ini tidak punya listing SOLVD, jadi tidak ada yang hilang; (c) harga pilihan penjual; di floor 0,102 USDT → kotor ~$0,102 per token (~0,000147 BNB), bersih setelah fee 2,5% + royalty 5% ≈ 0,0944 USDT (~$0,094). Listing baru masuk current market.
- Catatan: API `owner` wallet kedua menunjukkan `marketApproved=false` di kedua market dan `isAgent=false` — listing tidak butuh Agent ID (hanya beli di legacy yang butuh).

## Total kasar bila semua yang punya venue live terjual di floor

- SOLVD #869 + #2137 @ 0,102 USDT: **~0,204 USDT (~$0,20)** kotor.
- Coracle #897 + #898 @ klaster 0,0002 BNB: **~0,0004 BNB (~$0,28)** kotor; @ floor penuh terakhir 0,000035 BNB: ~0,00007 BNB (~$0,05).
- Gabungan realistis: **~$0,25–0,48** sebelum fee — kecil, tapi venue-nya nyata dan sudah ada penjualan.

## Yang belum selesai / caveat

- Coracle `page()` retry SELESAI ~09:00 WIB: 13 dari 14 chunk (500 ID) tetap tidak terbaca; hanya page(0,500) yang berhasil (8 live, termurah 0,000014 BNB). Floor cakupan penuh hari ini tidak didapat — angka Coracle di atas memakai sampel 30% + floor penuh 2026-10-29. Verdict Coracle (market live) tidak berubah.
- `ownerOf` live drop.ai #2193 belum dipanggil langsung (hanya Ankr) — verifikasi sebelum aksi apa pun.
- Element tidak bisa dicek live untuk koleksi mana pun (API butuh x-api-key, tanpa jalur anonim) — semua fallback Element di atas berstatus "opsi, listing live tidak terverifikasi".
- Semua token di atas belum ter-listing di venue mana pun (terverifikasi on-chain/API) kecuali dinyatakan lain — tidak ada listing aktif yang terlewat.
