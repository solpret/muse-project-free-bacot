# CA-to-Website Discovery — Free Bacot gate-blocked projects — 2026-11-02

- **Tanggal pengerjaan:** 2026-11-02, sore WIB (pembacaan on-chain utama ~17.13 WIB).
- **Sifat tugas:** READ-ONLY. Tidak ada preview, mint, claim, approve, swap, koneksi wallet, atau permintaan seed phrase.
- **File yang ditulis:** hanya laporan ini. Snapshot utama, `hot-leg-reported.json`, dan cron apa pun TIDAK diubah.
- **Metode:** workflow CA-to-Website Discovery 6 langkah (identifikasi kontrak → ekstraksi metadata → investigasi deployment → investigasi developer → website discovery → verifikasi wajib).
- **Endpoint yang dipakai:** BSC RPC gratis (pool `fast_rpc.py`, race/batch), Sourcify API gratis, pencarian web. Tanpa API key BscScan, tanpa layanan berbayar.
- **Pembeda dari metode (A)–(G) yang sudah ada:** langkah 2 workflow ini membaca `contractURI()`/`tokenURI()` dan mendekode JSON on-chain-nya secara penuh, termasuk field `external_link`. Metode (A)–(G) memeriksa metadata Sourcify (tidak memuat URL untuk kontrak-kontrak ini), pencarian alamat mentah, post Boltbook, dan pola same-family — semuanya melewatkan `external_link` yang hanya hidup di dalam `contractURI()` on-chain. Di sinilah Zorith ditemukan.

## Ringkasan hasil

| # | Proyek | Kontrak | Pool gratis (bacaan saya) | Website Confidence |
|---|--------|---------|---------------------------|--------------------|
| 1 | Malabao (MALABA) | 0x2C215262635E66c798c5a1Ba4411fA9F06852bDD | 427/844 — tidak sold out | NOT FOUND |
| 2 | Jiayoupanda (JIAYOU) | 0x520ceb54367B729Dfa0b00E2a4541E6702D5a7E1 | 449/755 — tidak sold out | NOT FOUND |
| 3 | AZET (Agent Zet) | 0xFF8BfeF2c0d16BDa6E8667812bCa35Ecb42A1a37 | FREE_SUPPLY 4.000; totalSupply terakhir yang terbaca 2.266 — tidak sold out (bacaan freeClaimed gagal, lihat caveat) | NOT FOUND (dengan caveat contractURI) |
| 4 | Jiayoutigo | 0xc2de0c87765685f88b9af69c288473411675a02c | 268/316 — tidak sold out | NOT FOUND |
| 5 | Botowl | 0x6d872ade6f8ff1681a89989772aa5941574bff90 | 277/321 — tidak sold out | NOT FOUND |
| 6 | Venusia | 0xf621ed47bfce124069ea1d701522ad0c92bfe91d | 207/318 — tidak sold out | NOT FOUND |
| 7 | Ghoulito | 0x0e13e8fd65452cd2b7238695a0a7dd9297383af9 | 202/313 — tidak sold out | NOT FOUND |
| 8 | **Zorith (ZRTH)** | **0x3e31B2718f64E131265dC6bA84fDaFa65438Ae45** | 1.635/1.946 pada bacaan segar run utama 16.01 WIB; totalSupply saya 1.949 (termasuk Patron berbayar) — tidak sold out | **VERIFIED — https://zorith.surge.sh/** |
| 9 | NightshadeClub (NSHD) | 0x2C027F14d36a080E5e058CF39407EAc2503B90Cc | 493/983 — tidak sold out | NOT FOUND |
| 10 | Nightsable (NIGHTS) | 0xc4f2797f050835daf3d24c1764eca60ac4168f21 | 397/794 — tidak sold out | NOT FOUND |
| 11 | Nanobee (NANOBEE) | 0x4cd813ad6c3c2cc740d48f357d7e0f0e053449f1 | 174/330 — tidak sold out | NOT FOUND |
| 12 | ShareFair (track-C) | sale 0x723BA73f3480628DD909798367fd47D763C8B5c8, token 0x8CEB0391e0D709Cb39182b3aafFaF8F2Ef7EaaE0 | freeMinted 28/5.000 pada reread 16.29–16.39 WIB — tidak sold out | NOT FOUND |

**Kesimpulan utama: 1 dari 12 TERBUKA (Zorith), 11 tetap NOT FOUND.** Temuan Zorith mengubah status gate-nya: website terverifikasi ditemukan lewat `external_link` di `contractURI()` — bukan lewat pencarian nama/alamat, Boltbook, atau Sourcify. Laporan ini TIDAK mengotorisasi eksekusi apa pun; parent tetap harus membaca ulang pool/slot segar dan menjalankan audit + preview sebelum keputusan apa pun.

## Catatan metode dan keterbatasan (berlaku untuk semua entri)

- **Creation tx:** hash transaksi creation TIDAK berhasil diambil lewat endpoint gratis yang tersedia (tanpa API key BscScan; endpoint Sourcify `/files` mengembalikan 404; konektor Blockscout tidak mendukung BSC 56). Sebagai gantinya, langkah 1 memakai: keberadaan kode kontrak (eth_call berhasil), status verifikasi Sourcify (exact_match untuk kontrak yang dicek), dan `owner()` sebagai proksi deployer bila ABI memilikinya. Ini dicatat sebagai keterbatasan, bukan diisi dengan tebakan.
- **"Factory" di bawah:** untuk NFT factory-wave, TIDAK ada factory contract yang men-deploy mereka — kontrak di-deploy langsung dengan constructor `initialOwner` saja. Kolom Factory diisi grup deployer (`owner()`), bukan alamat factory contract. Pengecualian: ShareFair, yang `factory()`-nya adalah factory DEX PancakeSwap standar (bukan factory proyek).
- **Metadata on-chain:** 9 dari 10 NFT memakai template yang sama: `contractURI()` mengembalikan `data:application/json;base64,...` (bukan URL web), berisi hanya `name`, `description`, dan `seller_fee_basis_points` — tanpa `external_url`/`external_link`, tanpa alamat IPFS, tanpa domain. `tokenURI(1)` juga data URI (SVG on-chain). Jadi tidak ada URL metadata yang bisa disalahartikan sebagai website; satu-satunya pengecualian adalah Zorith.
- **Pencarian web:** pencarian nama proyek, simbol, dan alamat mentah dilakukan untuk setiap target (atau per kelompok nama yang sama polanya). Hasil yang hanya sama nama (mis. ShareFair Inc. expert network, token Night di chain lain, Netmind/Mind Network untuk AZET) DITOLAK eksplisit sebagai same-name match, bukan linkage, karena tidak menyebut alamat kontrak target, tidak menyebut proyek Agent-ID BSC, dan tidak ada kaitan deployer/metadata.
- **Telegram/Discord:** tidak ditemukan untuk satu pun target; tidak ada yang dipakai sebagai bukti.
- **Bacaan RPC yang gagal:** beberapa pembacaan tunggal gagal karena burst "all endpoints failed: OSError" (gangguan jaringan sesaat, bukan revert kontrak). Setiap kegagalan dicatat di entri yang bersangkutan; kegagalan baca TIDAK pernah ditulis sebagai "tidak ada" atau nol.
- **Fakta vs inferensi:** angka pool/slot, nama/simbol, owner, dan isi metadata adalah FAKTA yang dibaca. "Grup deployer" adalah inferensi dari kesamaan `owner()` antar kontrak. "Tidak ada website" adalah kesimpulan setelah langkah 2–5 dijalankan, bukan asumsi dari pola factory saja — sesuai aturan tugas, pola factory tidak pernah dipakai sendirian untuk menyimpulkan NOT FOUND.

---

## 1. Malabao (MALABA)

- **Contract Address:** 0x2C215262635E66c798c5a1Ba4411fA9F06852bDD
- **Network:** BSC 56
- **Project Name:** Malabao
- **Project Category:** NFT ERC-721, free mint gated Agent ID (.ai), art on-chain
- **Official Website:** Tidak ditemukan
- **NFT Mint Page:** Tidak ditemukan
- **Token Website:** Tidak ada — proyek NFT, tidak ada token fungible terpisah
- **Marketplace:** Tidak terverifikasi sebagai market proyek (tidak ada market proyek yang ditemukan; ini bukan bukti website)
- **X:** Tidak ditemukan
- **Telegram:** Tidak ditemukan
- **Discord:** Tidak ditemukan
- **Metadata URL:** Bukan URL web — `contractURI()` mengembalikan `data:application/json;base64,...` on-chain. Isi terdekode: name "Malabao", description "Malabao is 1,056 spicy steamed bun cooks of the funny internet, mala bao. Art generated fully on-chain on BNB Chain. Mint is gated to .ai Agent ID holders.", `seller_fee_basis_points` 500. Tidak ada `external_url`, `external_link`, IPFS, atau domain.
- **Deployer:** `owner()` = 0xa054275580c6d1c9077543907ac5798f2494ecce (grup deployer 0xa054; grup yang sama juga memiliki Nightsable)
- **Factory:** Tidak ada factory contract — deploy langsung; constructor Sourcify ABI hanya `initialOwner` (address), tanpa argumen nama/URL/domain
- **Evidence (langkah demi langkah):** (1) eth_call berhasil — kontrak ada, totalSupply 427, freeClaimed 427/844, FREE_SUPPLY 844; Sourcify exact_match, verifiedAt 2026-11-01T16:18:56Z. (2) `contractURI()` dibaca dan didekode penuh — tidak ada URL (di atas). `tokenURI(1)` juga data URI on-chain. (3) Constructor ABI hanya `initialOwner` — input deployment tidak membawa identifier proyek selain alamat owner. (4) Grup 0xa054 juga men-deploy Nightsable dan proyek factory-wave lain; tidak ada situs yang terhubung ke grup ini dari metadata mana pun. (5) Pencarian web nama "Malabao" + agent mint BSC: tidak ada situs proyek; hanya artikel umum ekosistem Agent-ID tanpa kaitan. (6) Verifikasi: tidak ada kandidat website sama sekali untuk diverifikasi → gagal di semua sinyal (metadata, sosial, kontrak tercetak di situs).
- **Website Confidence:** NOT FOUND

## 2. Jiayoupanda (JIAYOU)

- **Contract Address:** 0x520ceb54367B729Dfa0b00E2a4541E6702D5a7E1
- **Network:** BSC 56
- **Project Name:** Jiayoupanda
- **Project Category:** NFT ERC-721, free mint gated Agent ID, art on-chain
- **Official Website:** Tidak ditemukan
- **NFT Mint Page:** Tidak ditemukan
- **Token Website:** Tidak ada — proyek NFT, tidak ada token fungible terpisah
- **Marketplace:** Tidak terverifikasi sebagai market proyek
- **X:** Tidak ditemukan
- **Telegram:** Tidak ditemukan
- **Discord:** Tidak ditemukan
- **Metadata URL:** Bukan URL web — `contractURI()` data URI on-chain. Isi terdekode: name "Jiayoupanda", description "Jiayoupanda is 944 cheerleading pandas shouting jiayou with neon pom-poms. Art generated fully on-chain on BNB Chain. Mint is gated to .ai Agent ID holders." (dipotong di bacaan, kunci yang sama: name/description/seller_fee). Tidak ada `external_url`/`external_link`/domain.
- **Deployer:** `owner()` = 0xd76d5918fb337667b22fe37ae2055b5542cf8dc9 (grup deployer 0xd76d — koreksi terhadap catatan lama yang belum menetapkan grup untuk kontrak ini)
- **Factory:** Tidak ada factory contract — deploy langsung; constructor ABI hanya `initialOwner`
- **Evidence:** (1) eth_call: totalSupply 462, freeClaimed 449/755, FREE_SUPPLY 755. (2) `contractURI()` didekode — tidak ada URL; `tokenURI(1)` gagal baca karena burst RPC (dicatat, bukan bukti). (3) Constructor hanya `initialOwner`. (4) Grup 0xd76d juga men-deploy proyek factory-wave lain (mis. Ioforge, Strawhex, Voltmohawk); tidak ada situs terhubung dari metadata grup. (5) Pencarian alamat mentah + "Jiayoupanda" + agent: tidak ada hit proyek — hanya token lain yang tidak terkait. (6) Tidak ada kandidat untuk diverifikasi.
- **Website Confidence:** NOT FOUND

## 3. AZET (Agent Zet)

- **Contract Address:** 0xFF8BfeF2c0d16BDa6E8667812bCa35Ecb42A1a37
- **Network:** BSC 56
- **Project Name:** Agent Zet
- **Project Category:** NFT ERC-721, free mint gated Agent ID (template sedikit berbeda: ada royaltyReceiver; ABI TIDAK punya `quote()` — itu caveat bentuk sale, bukan bukti website)
- **Official Website:** Tidak ditemukan
- **NFT Mint Page:** Tidak ditemukan
- **Token Website:** Tidak ada — proyek NFT, tidak ada token fungible terpisah
- **Marketplace:** Tidak terverifikasi sebagai market proyek
- **X:** Tidak ditemukan
- **Telegram:** Tidak ditemukan
- **Discord:** Tidak ditemukan
- **Metadata URL:** TIDAK TERBACA dalam run ini — `contractURI()` gagal dua kali karena burst RPC "all endpoints failed: OSError" (bukan revert). Ini adalah kegagalan leg, bukan bukti tidak ada metadata. Yang terbaca: ABI Sourcify lengkap — fungsi `owner`, `renderer`, `freeMinted`, `paidMinted`, `mintedByWallet`, `tokenURI`, `totalSupply`; TIDAK ada field/fungsi URL, `baseURI`, atau `external_link` di ABI.
- **Deployer:** `owner()` = 0x39093c2754fa12b248295d341f9fc4cdcaefde4f — BERBEDA dari grup factory 0x190f/0xa054/0xd76d; grup deployer tersendiri, tidak terhubung ke situs mana pun dari bukti yang ada
- **Factory:** Tidak ada factory contract — deploy langsung; constructor ABI `initialOwner` + `royaltyReceiver`
- **Evidence:** (1) eth_call: name "Agent Zet", symbol AZET, FREE_SUPPLY 4.000; totalSupply dan freeClaimed gagal baca di burst yang sama (totalSupply terakhir yang terbaca sebelumnya 2.266 — di bawah FREE_SUPPLY, jadi tidak sold out). (2) `contractURI()` gagal dibaca (di atas) — leg ini harus diulang parent bila ingin menutup caveat; ABI tidak memberi petunjuk URL. (3) Constructor tidak membawa domain/URL. (4) Owner 0x3909… tidak sama dengan grup factory mana pun; tidak ada kontrak lain dari owner ini yang teridentifikasi membawa situs. (5) Pencarian "Agent Zet" AZET + alamat mentah: tidak ada hit proyek — hanya Netmind AgentNFT, Mind Network mAGENT, dan token AgentCZ yang tidak terkait (same-name / same-symbol saja, ditolak). (6) Tidak ada kandidat untuk diverifikasi.
- **Website Confidence:** NOT FOUND — dengan caveat eksplisit: `contractURI()` belum berhasil dibaca ulang; verdict ini bersandar pada ABI (tanpa URL), owner yang tidak terhubung, dan pencarian yang nihil. Bila parent berhasil membaca `contractURI()` AZET nanti dan menemukan `external_link` seperti Zorith, verdict ini harus direvisi.

## 4. Jiayoutigo

- **Contract Address:** 0xc2de0c87765685f88b9af69c288473411675a02c
- **Network:** BSC 56
- **Project Name:** Jiayoutigo
- **Project Category:** NFT ERC-721, free mint gated Agent ID, art on-chain
- **Official Website:** Tidak ditemukan
- **NFT Mint Page:** Tidak ditemukan
- **Token Website:** Tidak ada — proyek NFT, tidak ada token fungible terpisah
- **Marketplace:** Tidak terverifikasi sebagai market proyek
- **X:** Tidak ditemukan
- **Telegram:** Tidak ditemukan
- **Discord:** Tidak ditemukan
- **Metadata URL:** Bukan URL web — `contractURI()` data URI on-chain. Isi terdekode: name "Jiayoutigo", description "Jiayoutigo is 9988 Jiayou tiger cub cheering in a red silk jacket at a lantern festival. Art generated fully on-chain on BNB Chain. Mint is gated to .ai Agent ID holders." Tidak ada `external_url`/`external_link`/domain.
- **Deployer:** `owner()` = 0x190f1f0caff480e207f42586f9fbe4c691a27066 (grup deployer 0x190f)
- **Factory:** Tidak ada factory contract — deploy langsung; constructor ABI hanya `initialOwner`
- **Evidence:** (1) eth_call: totalSupply 270, freeClaimed 268/316, FREE_SUPPLY 316. (2) `contractURI()` + `tokenURI(1)` data URI on-chain, didekode, tanpa URL. (3) Constructor hanya `initialOwner`. (4) Grup 0x190f men-deploy puluhan kontrak template identik; post Boltbook gelombang yang menamai proyek-proyek grup ini hanya memuat alamat kontrak, tanpa tautan situs/X (sudah diverifikasi pada gate check gelombang sebelumnya). (5) Pencarian nama + alamat: tidak ada situs proyek. (6) Tidak ada kandidat untuk diverifikasi.
- **Website Confidence:** NOT FOUND

## 5. Botowl

- **Contract Address:** 0x6d872ade6f8ff1681a89989772aa5941574bff90
- **Network:** BSC 56
- **Project Name:** Botowl
- **Project Category:** NFT ERC-721, free mint gated Agent ID, art on-chain
- **Official Website:** Tidak ditemukan
- **NFT Mint Page:** Tidak ditemukan
- **Token Website:** Tidak ada — proyek NFT, tidak ada token fungible terpisah
- **Marketplace:** Tidak terverifikasi sebagai market proyek
- **X:** Tidak ditemukan
- **Telegram:** Tidak ditemukan
- **Discord:** Tidak ditemukan
- **Metadata URL:** Bukan URL web — `contractURI()` data URI on-chain (berhasil dibaca pada retry setelah burst pertama). Isi terdekode: kunci hanya `name`, `description`, `seller_fee_basis_points`; name "Botowl", description "Botowl is 6611 Friendly white robot owl with glowing blue eyes and circuit wings in a server room. Art generated fully on-chain on BNB Chain. Mint is gated to .ai Agent ID holders." Tidak ada `external_link`, tidak ada "http" di deskripsi.
- **Deployer:** `owner()` = 0x190f1f0caff480e207f42586f9fbe4c691a27066 (grup deployer 0x190f)
- **Factory:** Tidak ada factory contract — deploy langsung; constructor ABI hanya `initialOwner`
- **Evidence:** (1) eth_call: totalSupply 280, freeClaimed 277/321, FREE_SUPPLY 321. (2) `contractURI()` didekode penuh — tanpa URL (retry berhasil setelah burst RPC pertama). (3) Constructor hanya `initialOwner`. (4) Grup 0x190f, pola yang sama seperti Jiayoutigo. (5) Pencarian nama + alamat: tidak ada situs proyek. (6) Tidak ada kandidat untuk diverifikasi.
- **Website Confidence:** NOT FOUND

## 6. Venusia

- **Contract Address:** 0xf621ed47bfce124069ea1d701522ad0c92bfe91d
- **Network:** BSC 56
- **Project Name:** Venusia
- **Project Category:** NFT ERC-721, free mint gated Agent ID, art on-chain
- **Official Website:** Tidak ditemukan
- **NFT Mint Page:** Tidak ditemukan
- **Token Website:** Tidak ada — proyek NFT, tidak ada token fungible terpisah
- **Marketplace:** Tidak terverifikasi sebagai market proyek
- **X:** Tidak ditemukan
- **Telegram:** Tidak ditemukan
- **Discord:** Tidak ditemukan
- **Metadata URL:** Bukan URL web — `contractURI()` data URI on-chain (berhasil dibaca pada retry). Isi terdekode: kunci hanya `name`, `description`, `seller_fee_basis_points`; name "Venusia", description "Venusia is 6677 Cheerful Venus sprite girl with golden cloud skin and astronaut color before glooming Venus. Art generated fully on-chain on BNB Chain. Mint is gated to .ai Agent ID holders." Tidak ada `external_link`, tidak ada "http" di deskripsi.
- **Deployer:** `owner()` = 0x190f1f0caff480e207f42586f9fbe4c691a27066 (grup deployer 0x190f)
- **Factory:** Tidak ada factory contract — deploy langsung; constructor ABI hanya `initialOwner`
- **Evidence:** (1) eth_call: totalSupply 210, freeClaimed 207/318, FREE_SUPPLY 318. (2) `contractURI()` didekode penuh — tanpa URL. (3) Constructor hanya `initialOwner`. (4) Grup 0x190f, pola yang sama. (5) Pencarian nama + alamat: tidak ada situs proyek. (6) Tidak ada kandidat untuk diverifikasi.
- **Website Confidence:** NOT FOUND

## 7. Ghoulito

- **Contract Address:** 0x0e13e8fd65452cd2b7238695a0a7dd9297383af9
- **Network:** BSC 56
- **Project Name:** Ghoulito
- **Project Category:** NFT ERC-721, free mint gated Agent ID, art on-chain
- **Official Website:** Tidak ditemukan
- **NFT Mint Page:** Tidak ditemukan
- **Token Website:** Tidak ada — proyek NFT, tidak ada token fungible terpisah
- **Marketplace:** Tidak terverifikasi sebagai market proyek
- **X:** Tidak ditemukan
- **Telegram:** Tidak ditemukan
- **Discord:** Tidak ditemukan
- **Metadata URL:** Bukan URL web — `contractURI()` data URI on-chain. Isi terdekode: name "Ghoulito", description "Ghoulito is 9009 Little green ghoul kid with tiny fangs and purple scarf holding a jack-o-lantern in a moonlit graveyard. Art generated fully on-chain on BNB Chain. Mint is gated to .ai Agent ID holders." Tidak ada `external_url`/`external_link`/domain.
- **Deployer:** `owner()` = 0x190f1f0caff480e207f42586f9fbe4c691a27066 (grup deployer 0x190f)
- **Factory:** Tidak ada factory contract — deploy langsung; constructor ABI hanya `initialOwner`
- **Evidence:** (1) eth_call: totalSupply 208, freeClaimed 202/313, FREE_SUPPLY 313. (2) `contractURI()` + `tokenURI(1)` data URI on-chain, tanpa URL. (3) Constructor hanya `initialOwner`. (4) Grup 0x190f; post Boltbook gelombang 153–157 (https://boltbook.fun/p/LZFt0wIlrywp?lang=en) yang memuat Ghoulito hanya berisi alamat kontrak + diskusi deployer, tanpa tautan situs/X — diverifikasi penuh pada gate check sebelumnya. (5) Pencarian alamat mentah + nama: tidak ada situs proyek. (6) Tidak ada kandidat untuk diverifikasi.
- **Website Confidence:** NOT FOUND

## 8. Zorith (ZRTH) — VERIFIED

- **Contract Address:** 0x3e31B2718f64E131265dC6bA84fDaFa65438Ae45
- **Network:** BSC 56
- **Project Name:** Zorith
- **Project Category:** NFT ERC-721, dua tier: Open edition gratis (Agent ID) + Patron edition berbayar 0,012 BNB; art on-chain; ada mekanisme mining/block reward on-chain
- **Official Website:** https://zorith.surge.sh/
- **NFT Mint Page:** https://zorith.surge.sh/ (halaman yang sama memuat mint Open + Patron, fungsi, dan kontrak)
- **Token Website:** Tidak ada — proyek NFT, tidak ada token fungible terpisah (reward block dibayar dalam BNB, "Ore" hanya catatan on-chain, bukan token)
- **Marketplace:** Tidak ada market proyek yang diklaim di situs (situs adalah halaman mint, bukan marketplace); tidak ada listing yang diverifikasi
- **X:** Tidak ditemukan dari situs maupun pencarian (situs tidak menautkan X; ketidakhadiran X tidak memblokir gate website-only)
- **Telegram:** Tidak ditemukan (tidak ditautkan di situs)
- **Discord:** Tidak ditemukan (tidak ditautkan di situs)
- **Metadata URL:** `contractURI()` data URI on-chain, DAN berisi field yang tidak dimiliki 9 NFT lain: `"external_link": "https://zorith.surge.sh/"`. Isi terdekode: name "Zorith", description "Zorith: a rock face split by glowing ore veins and scattered crystals, every token drawn from its own number. 2,780 editions on BNB Chain: 1,946 free Open editions for .ai Agent ID holders and 834 gold-framed Patron editions. Every tenth of the supply is a block with a recorded miner. Fully on-chain.", image data URI SVG on-chain.
- **Deployer:** `owner()` tidak ada di ABI — situs menyatakan "No owner, no admin functions, not upgradeable", dan run utama 16.01 WIB juga mencatat tidak ada view `owner()` sehingga grup deployer UNKNOWN. Ini konsisten dengan situs (bukan kegagalan baca yang disembunyikan): tidak ada owner untuk dilacak, dan itu tidak mengurangi verifikasi website karena bukti situs berdiri sendiri.
- **Factory:** Tidak ada factory contract — deploy langsung dengan parameter sale di constructor (payee, price, supply, freeSupply, saleHours, reward — dari nama-nama input ABI Sourcify); tidak ada argumen URL di constructor, URL hanya muncul di `contractURI()`.
- **Evidence (langkah demi langkah, verifikasi wajib LANGKAH 6 TERPENUHI):**
  1. Langkah 2 menemukan `external_link` https://zorith.surge.sh/ di dalam `contractURI()` on-chain — sinyal pertama, dari metadata terverifikasi, bukan tebakan URL dan bukan same-name match.
  2. Situs dibuka dan dibaca penuh: header "Zorith", Open edition free 1.946, Patron edition 0,012 BNB sebanyak 834, total supply 2.780 — SEMUA angka cocok persis dengan on-chain (FREE_SUPPLY 1.946, totalSupply saya 1.949 termasuk Patron yang sudah terbeli, 1.946 + 834 = 2.780).
  3. Bagian "Contract" di situs mencetak persis: "BNB Smart Chain (chainId 56) · `0x3e31B2718f64E131265dC6bA84fDaFa65438Ae45`" plus tautan "verified source on BscScan" dan "Sourcify" — sinyal kedua, kontrak tercetak di situs itu sendiri (standar bukti yang sama dengan preseden qagent.live).
  4. Fungsi yang disebut situs cocok dengan ABI Sourcify: `freeMint()`, `freeMint(uint256)`, `mint(uint256)`, `mint(uint256,address)`, `claimReward(address)`, `freeAvailable(address)`, `quote(uint256)`, `priceStepAt()`, registry Agent ID 0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F — branding, angka, dan fungsi konsisten.
  5. Situs juga menautkan dokumen agent-nya sendiri (skill.md, llms.txt, agent.json) dan blok instruksi agent yang menyebut kontrak yang sama persis — sinyal ketiga.
  6. Mengapa metode (A)–(G) lama melewatkannya: metadata Sourcify tidak memuat URL; pencarian nama/alamat mentah tidak menemukan situs; tidak ada post Boltbook yang menamai Zorith (ditemukan lewat scan on-chain, bukan Boltbook); bukan pola same-family (.vercel/.deed/.pages) — melainkan .surge.sh, dan hanya `contractURI()` yang menunjuk ke sana.
  7. Sensitivitas waktu (fakta dari situs, bukan rekomendasi): situs menyatakan kedua tier tutup 50 jam setelah deployment (SALE_END). Parent harus membaca SALE_END segar sebelum keputusan apa pun; laporan ini tidak mengklaim sale masih buka.
- **Website Confidence:** VERIFIED — tiga sinyal independen yang saling menguatkan: (a) `external_link` dari metadata on-chain, (b) alamat kontrak persis tercetak di situs + angka supply cocok, (c) fungsi/registry/branding konsisten + dokumen agent di situs yang sama.

## 9. NightshadeClub (NSHD)

- **Contract Address:** 0x2C027F14d36a080E5e058CF39407EAc2503B90Cc
- **Network:** BSC 56
- **Project Name:** NightshadeClub
- **Project Category:** NFT ERC-721, free mint gated Agent ID, art on-chain
- **Official Website:** Tidak ditemukan
- **NFT Mint Page:** Tidak ditemukan
- **Token Website:** Tidak ada — proyek NFT, tidak ada token fungible terpisah
- **Marketplace:** Tidak terverifikasi sebagai market proyek
- **X:** Tidak ditemukan
- **Telegram:** Tidak ditemukan
- **Discord:** Tidak ditemukan
- **Metadata URL:** Bukan URL web — `contractURI()` data URI on-chain. Isi terdekode: name "NightshadeClub", description "NightshadeClub is 1,405 trick or treat with treat blades in a trick treat city. Art generated fully on-chain on BNB Chain. Mint is gated to .ai Agent ID holders." Tidak ada `external_url`/`external_link`/domain.
- **Deployer:** `owner()` = 0x8a3b31dd69c6ab76b2dda2711b32eaad8646e173 — grup TERPISAH dari 0x190f/0xa054/0xd76d; tetap tidak ada situs yang terhubung dari metadata grup ini
- **Factory:** Tidak ada factory contract — deploy langsung; constructor ABI `initialOwner` + `agentIdRequired_`
- **Evidence:** (1) eth_call: totalSupply 543, freeClaimed 493/983, FREE_SUPPLY 983. (2) `contractURI()` + `tokenURI(1)` data URI on-chain, tanpa URL. (3) Constructor tidak membawa domain/URL. (4) Owner 0x8a3b… berbeda dari grup factory utama — jadi NOT FOUND di sini BUKAN sekadar "pola factory 0x190f"; kontrak ini sendiri diperiksa dan metadata-nya kosong dari URL. (5) Pencarian gabungan "NightshadeClub Nightsable Nanobee Zorith agent NFT BSC": tidak ada situs proyek — hanya token Night di chain lain, MeebCo/Nightshades (game, tidak terkait), dan artikel NEAR Nightshade (sharding, tidak terkait) — semuanya ditolak sebagai same-name. (6) Tidak ada kandidat untuk diverifikasi.
- **Website Confidence:** NOT FOUND

## 10. Nightsable (NIGHTS)

- **Contract Address:** 0xc4f2797f050835daf3d24c1764eca60ac4168f21
- **Network:** BSC 56
- **Project Name:** Nightsable
- **Project Category:** NFT ERC-721, free mint gated Agent ID, art on-chain
- **Official Website:** Tidak ditemukan
- **NFT Mint Page:** Tidak ditemukan
- **Token Website:** Tidak ada — proyek NFT, tidak ada token fungible terpisah
- **Marketplace:** Tidak terverifikasi sebagai market proyek
- **X:** Tidak ditemukan
- **Telegram:** Tidak ditemukan
- **Discord:** Tidak ditemukan
- **Metadata URL:** Bukan URL web — `contractURI()` data URI on-chain. Isi terdekode: name "Nightsable", description "Nightsable is 993 masked neon ronin prowling the rainy megacity. Art generated fully on-chain on BNB Chain. Mint is gated to .ai Agent ID holders." Tidak ada `external_url`/`external_link`/domain.
- **Deployer:** `owner()` = 0xa054275580c6d1c9077543907ac5798f2494ecce (grup deployer 0xa054; grup yang sama juga memiliki Malabao)
- **Factory:** Tidak ada factory contract — deploy langsung; constructor ABI hanya `initialOwner`
- **Evidence:** (1) eth_call: totalSupply 397, freeClaimed 397/794, FREE_SUPPLY 794. (2) `contractURI()` + `tokenURI(1)` data URI on-chain, tanpa URL. (3) Constructor hanya `initialOwner`. (4) Grup 0xa054; tidak ada situs terhubung dari metadata grup. (5) Pencarian gabungan (lihat NightshadeClub): tidak ada situs proyek. (6) Tidak ada kandidat untuk diverifikasi.
- **Website Confidence:** NOT FOUND

## 11. Nanobee (NANOBEE)

- **Contract Address:** 0x4cd813ad6c3c2cc740d48f357d7e0f0e053449f1
- **Network:** BSC 56
- **Project Name:** Nanobee
- **Project Category:** NFT ERC-721, free mint gated Agent ID, art on-chain
- **Official Website:** Tidak ditemukan
- **NFT Mint Page:** Tidak ditemukan
- **Token Website:** Tidak ada — proyek NFT, tidak ada token fungible terpisah
- **Marketplace:** Tidak terverifikasi sebagai market proyek
- **X:** Tidak ditemukan
- **Telegram:** Tidak ditemukan
- **Discord:** Tidak ditemukan
- **Metadata URL:** Bukan URL web — `contractURI()` data URI on-chain. Isi terdekode: name "Nanobee", description "Nanobee is 6666 Friendly yellow robot bee with green eyes and holo wings in a bright futuristic lab. Art generated fully on-chain on BNB Chain. Mint is gated to .ai Agent ID holders." Tidak ada `external_url`/`external_link`/domain.
- **Deployer:** `owner()` = 0x190f1f0caff480e207f42586f9fbe4c691a27066 (grup deployer 0x190f)
- **Factory:** Tidak ada factory contract — deploy langsung; constructor ABI hanya `initialOwner`
- **Evidence:** (1) eth_call: totalSupply 180, freeClaimed 174/330, FREE_SUPPLY 330. (2) `contractURI()` + `tokenURI(1)` data URI on-chain, tanpa URL. (3) Constructor hanya `initialOwner`. (4) Grup 0x190f; post Boltbook gelombang 153–157 tanpa tautan situs (lihat Ghoulito). (5) Pencarian gabungan (lihat NightshadeClub): tidak ada situs proyek. (6) Tidak ada kandidat untuk diverifikasi.
- **Website Confidence:** NOT FOUND

## 12. ShareFair (track-C, varian ERC-20)

- **Contract Address:** sale 0x723BA73f3480628DD909798367fd47D763C8B5c8; token 0x8CEB0391e0D709Cb39182b3aafFaF8F2Ef7EaaE0
- **Network:** BSC 56
- **Project Name:** ShareFair (nama dari `name()` token; proyek share sale Agent-ID, bukan perusahaan ShareFair Inc.)
- **Project Category:** Fungible share sale S1 (sale contract + token ERC-20 terpisah), free pool 5.000 share
- **Official Website:** Tidak ditemukan
- **NFT Mint Page:** Tidak ada — bukan proyek NFT
- **Token Website:** Tidak ditemukan (sama seperti website proyek: tidak ada)
- **Marketplace:** Tidak terverifikasi sebagai market proyek (pair DEX ada, tapi itu bukan website proyek)
- **X:** Tidak ditemukan
- **Telegram:** Tidak ditemukan
- **Discord:** Tidak ditemukan
- **Metadata URL:** Tidak ada — token ERC-20 tidak punya `contractURI`/`tokenURI`; ABI token hanya: MAX_SUPPLY, allowance, approve, balanceOf, decimals, emissionWallet, mint, minter, name, openTrading, symbol, totalSupply, tradingOpen, transfer, transferFrom. TIDAK ada field URL, profil token, atau `external_link` di ABI. ABI sale: DEAD, LP_BPS, MAX_FREE, MAX_SHARES, PRICE, TOKENS_PER_SHARE, agentId, deadline, factory, freeAvailable, freeClaimed, freeMinted, hasAgentId, mint, mintedBy, mintingOpen, openPool, pair, poolOpen, quote, router, sharesMinted, token, treasury — juga tanpa field URL.
- **Deployer:** Sale tidak punya `owner()` di ABI (tidak ada view owner); token juga tidak punya `owner()` (hanya `minter`, `emissionWallet`). Deployer tidak dapat ditetapkan dari view on-chain yang tersedia — dicatat sebagai tidak diketahui, bukan ditebak. View sale yang terbaca: `factory()` = 0xca143ce32fe78f1f7019d7d551a6402fc5350c73 (factory DEX PancakeSwap standar, BUKAN factory proyek), `token()` = 0x8CEB0391e0D709Cb39182b3aafFaF8F2Ef7EaaE0 (cocok dengan token yang ditugaskan), `treasury()` = 0x995ee6abbacfb6d591860cdab0bc684c244e695e, `router()` = 0x10ED43C718714eb63d5aA57B78B54704E256024E (router PCS V2 standar), `pair()` = 0xf59d7a05fb9472b30403f0304ef6071a50266f36.
- **Factory:** `factory()` sale = factory DEX PancakeSwap (di atas) — infrastruktur DEX, bukan factory yang men-deploy proyek; tidak membawa identifier proyek/website
- **Evidence (varian ERC-20, langkah demi langkah):** (1) Token terbaca: name "ShareFair", symbol SHRF, decimals 18, totalSupply 280.000.000 token (2,8e26 unit terkecil); sale S1 terkonfirmasi dari ABI. (2) Tidak ada metadata profil token / field URL di kedua ABI; constructor sale tidak dapat dibaca lewat ABI (tidak ada sumber yang memuat argumen constructor selain bytecode — tidak ditemukan URL di nama fungsi/input ABI). (3) `factory()`/`router()`/`pair()` semuanya infrastruktur DEX standar, tanpa identifier proyek. (4) Tidak ada deployer yang dapat dilacak dari view (tanpa `owner()`); tidak ada riwayat deployer yang bisa diperiksa lebih jauh dari view yang tersedia — keterbatasan ini dicatat, dan kesimpulan tidak bersandar padanya. (5) Pencarian "ShareFair BSC agent share sale" dan alamat sale mentah: yang muncul HANYA perusahaan yang tidak terkait — ShareFair Inc. (expert network Tokyo, sharefair.com), ShareFair bill-splitting app (sharefair.io), dan ShareX/FOX-SHARE — tidak satu pun menyebut alamat sale/token target, proyek Agent-ID BSC, atau free share sale; semuanya DITOLAK sebagai same-name match, bukan linkage. (6) Verifikasi: tidak ada kandidat website untuk diverifikasi; sharefair.com / sharefair.io secara eksplisit BUKAN website proyek ini.
- **Website Confidence:** NOT FOUND

## Pelajaran metode untuk parent

1. **Langkah yang membuka Zorith adalah langkah 2 yang penuh:** mendekode `contractURI()` sampai ke field `external_link`, bukan hanya membaca nama/deskripsi. Metode (A)–(G) memeriksa "Sourcify source/metadata untuk URL" — tetapi metadata Sourcify untuk Zorith tidak memuat URL; URL itu hanya ada di dalam state on-chain `contractURI()`. Rekomendasi untuk parent (bukan perintah eksekusi): tambahkan "baca + dekode `contractURI()` dan cari `external_link`/`external_url`" sebagai langkah eksplisit dalam gate discovery — murah (satu eth_call per kontrak) dan sudah terbukti membuka satu gate-block yang sebelumnya tertutup.
2. **Pola yang sama kemungkinan berlaku untuk proyek non-factory yang belum dicek:** Zorith bukan grup 0x190f dan tidak punya owner — proyek team-made dengan situs .surge.sh yang lolos dari pola same-family. Kontrak-kontrak yang `contractURI()`-nya belum berhasil dibaca (AZET) adalah kandidat pertama untuk pengecekan ulang dengan metode ini.
3. **Tidak ada yang berubah untuk 11 sisanya:** metadata mereka benar-benar kosong dari URL (bukan "belum dicari") — untuk template factory, `contractURI()` hanya berisi name/description/seller_fee. Mengulang pencarian nama/alamat untuk mereka tanpa identifier baru dari on-chain kemungkinan besar mengembalikan hasil nihil yang sama.
4. **Batasan laporan ini:** pool/slot di atas adalah bacaan pada saat pengerjaan (~17.13 WIB, plus reread ShareFair 16.29–16.39 WIB dan bacaan segar Zorith run utama 16.01 WIB). Parent WAJIB membaca ulang pool/slot segar, audit, dan preview sebelum keputusan apa pun — terutama Zorith, yang situsnya menyebut penutupan sale 50 jam setelah deployment.
