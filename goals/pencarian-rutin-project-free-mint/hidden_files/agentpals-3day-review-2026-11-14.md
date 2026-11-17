# Review 3-Hari AgentPals — Putusan Gate Metode (I)
**Run:** Sabtu 2026-11-14 ~19:37–20:10 WIB (cron runonce `agentpals-3day-gate-review`)
**Status:** READ-ONLY — tanpa preview/mint/approve/sign/tx, tanpa login.
**Vonis: (B) TIDAK ADA PERKEMBANGAN → tetap butuh situs proyek. Metadata worker TIDAK dihitung sebagai bukti website untuk AgentPals.**
Vonis ini rekomendasi putusan akhir untuk diputuskan user; TIDAK mengubah aturan gate di cron lain.

## Konteks
- AgentPals (APAL) 0xD265a929D0E50bD5ee4675e4E97F38D8380802E2 — free mint #268, wallet agent 0xeb237F6f9FB4e826739F0954e9768914F28b2c2E, tx 0x6ed2eade4928e135d03a1f3a256fa7a92ac52490320c077bbc2c1356ab9a36f5, blok 132967594, 11 Nov 2026 19:23:16 WIB. Mint ini melanggar mandatory website gate (tanpa situs terverifikasi sebelum eksekusi).
- Sengketa: hot-leg menilai tokenURI host agentpalsmeta.agenticmeta.workers.dev (root mencetak kontrak persis + maxSupply 1111) memenuhi metode (I); parent menilai host metadata bukan situs proyek.
- Keputusan user 11 Nov ~19:36 WIB: pantau 3 hari (s.d. 14 Nov) apakah proyek jalan + ada value; bila aktif + ada value → metadata dihitung sebagai bukti website; bila tidak ada perkembangan → tetap butuh situs proyek. Sementara: tetap butuh situs proyek.

## 1. On-chain segar (14 Nov ~19:37 WIB, blok 133547961, bsc-dataseed.binance.org)
- freeMinted = 300 / FREE_SUPPLY 300 → **free pool HABIS** (sold out sejak malam 11 Nov, tidak berubah).
- totalMinted = 302 / MAX_SUPPLY 1111 → hanya **+2 mint berbayar dalam 3 hari** sejak sold out. Praktis mati.
- freePhaseStart = 1794353637 = 11 Nov 06:33:57 WIB (tidak berubah).
- hasFreeMinted(user) = 1, balanceOf(user) = 1, ownerOf(268) = wallet agent. #268 tetap dipegang user.
- name "AgentPals", symbol APAL, owner 0x9e07f754116315298d8aaf3e24181de2907b4623 (tidak berubah).
- baseURI/tokenURI(268) = https://agentpalsmeta.agenticmeta.workers.dev/ (masih live, HTTP 200 — isi tidak berubah sejak 11 Nov).
- palsToken() = 0x01b0150501dec67a26bbf079129dd2fef81eb2dd (ditemukan via getter kontrak).

## 2. Aktivitas proyek 11–14 Nov: TIDAK ADA
- Pencarian web "AgentPals APAL NFT Agentic BSC" + "AgentPals / agentpalsmeta X twitter" (14 Nov): **0 hasil** untuk proyek NFT ini — tanpa situs resmi, tanpa akun X, tanpa pengumuman, tanpa fase mint baru.
- Satu-satunya "AgentPals" di web adalah agentpals.io — game PC Righteous Games ("Agentic RPG", Steam wishlist) — **tanpa kaitan kontrak**, sudah diputuskan 11 Nov bukan situs proyek ini.
- Pencarian "Agentic AGTC token BSC AgentPals companion": hanya mengembalikan AGC (Agentic Coin, token lain) — tidak ada proyek AGTC/AgentPals.
- Metadata worker masih live tapi isinya **identik** dengan 11 Nov (root: kontrak + maxSupply 1111; 268.json: Common/Ember/Cub, Power 11 / Defense 29 / Speed 23 / Luck 8). Itu kontinuitas infrastruktur, bukan perkembangan proyek.
- Transfer sekunder: **TIDAK TERVERIFIKASI** — eth_getLogs publik RPC -32005 di semua chunk (12 chunk, 3 endpoint); BscScan API chain-56 diblokir tier gratis (terkonfirmasi 19:35 WIB 14 Nov); halaman token BscScan diblokir Cloudflare di browser (20:06–20:10 WIB, Ray ID a5a640e9fd78db33, halaman tidak pernah tampil); Blockscout BSC 404. Jumlah holder + transfer tidak diketahui. Kaki ini tidak mengubah vonis: totalMinted +2 sudah membatasi aktivitas minting ke nyaris nol.

## 3. Value: TIDAK ADA
### NFT APAL — market/floor
- Own market: tidak ada (tidak ada situs proyek).
- Element: pencarian "element.market AgentPals APAL NFT collection" (14 Nov) — **0 hasil**; tidak ada koleksi APAL ditemukan. (API Element butuh x-api-key — tidak ada jalur anonim; pencarian web adalah bukti yang tersedia.)
- Market BSC lain: tidak ada yang ditemukan. Floor: **tidak ada floor terverifikasi (>0)**.
- #268: Common/Ember/Cub — tier tercatat di nft-rarity-inventory.md 11 Nov; tidak berubah.

### PALS token + HolderRewards
- PALS 0x01b0150501dec67a26bbf079129dd2fef81eb2dd: name "Pals", symbol PALS, decimals 18, totalSupply 50.000.000, balanceOf(user) = 0 (klaim belum dilakukan).
- GoPlus (14 Nov): is_honeypot 0, open source 1, creator 0x6ad9cc8cda76d38380023dc69f132a3d24881de7, **holder_count 24, is_in_dex 0, dex null**.
- DexScreener API token PALS: **0 pair**.
- On-chain (factory PCS V2 0xca143ce32fe78f1f7019d7d551a6402fc5350c73): getPair(PALS, WBNB) = 0x0, getPair(PALS, USDT) = 0x0. **Tidak ada pair, tidak ada likuiditas, tidak ada harga.**
- HolderRewards contract: **TIDAK DITEMUKAN** — 12+ nama getter dicoba di kontrak APAL (holderRewards, rewardsContract, holderRewardsContract, rewards, REWARDS, holderRewardsAddress, rewardsAddress, claimContract, distributor, rewardContract, PALSRewards, claimableRewards, rewardsPerGrade, claimAmount, gradeReward) semuanya revert; source Sourcify tidak bisa diambil (v2 exact_match tapi repo/files 404); BscScan API chain-56 diblokir tier gratis. Akibatnya **claimable(user) TIDAK TERVERIFIKASI** — dan kalaupun bisa diklaim, PALS tanpa pair/likuiditas berarti nilai klaim = 0 saat ini.
- Metadata #268 menyebut "one-time PALS claim sized by grade, claimed through the AgentPals HolderRewards contract" — janji itu belum bisa dieksekusi/dinilai karena kontraknya tidak ditemukan dan tokennya tidak punya pasar.

## 4. Vonis per kaki (keputusan user 11 Nov 19:36 WIB)
| Kaki | Syarat (A) | Bukti 14 Nov | Lolos? |
|---|---|---|---|
| AKTIF | situs/sosial/mint/claim berjalan | Free pool habis 11 Nov; totalMinted +2/3 hari; tanpa situs, tanpa X, tanpa pengumuman, tanpa fase baru | TIDAK |
| ADA VALUE | floor > 0 atau pair PALS berlikuiditas | Tanpa market/floor; PALS 0 pair, 0 likuiditas, 0 harga; HolderRewards tak ditemukan, claimable unverified | TIDAK |

**Vonis: (B).** Kedua kaki gagal. Tidak ada perkembangan proyek dalam 3 hari pantauan (11–14 Nov 2026). Maka sesuai keputusan user: **tetap butuh situs proyek; metadata worker (agentpalsmeta.agenticmeta.workers.dev) TIDAK dihitung sebagai bukti website untuk AgentPals.** Strong lead yang buktinya hanya metadata-worker tetap ditandai tidak lolos gate, seperti status sementara yang berlaku sejak 11 Nov.

## Yang tidak berubah / tindak lanjut
- #268 tetap milik wallet agent (Common Ember Cub). Tidak ada aksi jual/listing yang bisa dilakukan — tidak ada market.
- Klaim PALS: jangan diklaim sebelum HolderRewards ditemukan + pair/likuiditas terverifikasi; saat ini nilainya 0 dan kontrak klaimnya tidak ditemukan.
- Aturan gate di cron lain TIDAK diubah oleh review ini.
- Celah bukti yang dicatat (bukan temuan baru): transfer sekunder + jumlah holder APAL tidak terverifikasi karena BscScan diblokir Cloudflare + API BSC tier gratis + getLogs RPC limit. Bila user ingin angka itu, jalurnya: buka halaman token BscScan sendiri di perangkat user, atau BscScan API plan berbayar (jangan bayar tanpa perintah user).

## Artefak run
- Skrip baca: /tmp/apal_review_read.py → /tmp/apal-review-onchain.json; /tmp/pals_read.py → /tmp/pals-onchain.json + /tmp/pals-dexscreener.json; /tmp/apal_logs.py → /tmp/apal-logs-summary.json; /tmp/apal-268.json (metadata), /tmp/apal-root.html (worker root).
- Sumber: RPC publik BSC (bsc-dataseed.binance.org, blok 133547961), DexScreener API, GoPlus token_security, pencarian web 14 Nov, browser read-only BscScan (blokir Cloudflare 20:06–20:10 WIB).
