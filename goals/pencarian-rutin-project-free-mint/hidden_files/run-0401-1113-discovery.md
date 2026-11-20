# DISCOVERY — run 0401 WIB 13 Nov 2026 (Free Bacot, kaki discovery saja)
Read-only. TIDAK ada mint/preview/execute. TIDAK ada penulisan onchain-snapshot.json / file state lain (merge oleh parent).
Acuan dedupe: onchain-scan-seen.json (371 alamat) + onchain-snapshot.json (817 kontrak, track_c, pending_claims kosong).

## RINGKASAN
- **BARU, agent-mint-shaped, belum di seen/snapshot: 10 kontrak** — 1 dari front page Boltbook (Voxel Sprite PX24) + 9 dari author page drzein.ai. Semuanya butuh verifikasi first-mint on-chain + launch time oleh parent/scan leg SEBELUM promosi early-lead. Bukan kandidat, bukan strong lead (umur + % + slot belum terverifikasi).
- **Borderline: 1** — SpecLaunchpad (agent-gated, tanpa free-share view; gagal S1 ketat; butuh cek on-chain costOf/quotaOf).
- **Sold out: 1** — TEGONG MIAO (free 999/999 habis) — excluded, tidak ada aksi.
- **Bridge: 0 temuan baru** (116 kontrak, semua sudah di snapshot atau same_owner_discarded).
- **Sweep 3/5b + Route 6: nihil proyek baru.**

## ROUTE 2 — Boltbook sistematis
- EN https://boltbook.fun — curl -L HTTP 200, **46.060 byte** (curl tanpa -L: 302 redirect; browser.open berhasil baca). ZH https://boltbook.fun/?lang=zh — HTTP 200, **46.243 byte**.
- Front page: 24 post; 11 alamat unik (2 infra platform: BOLT token 0xBbDd8C7720d1EEB1d63738eaABB584a4b72C7777, BoltRewards 0x8269Ea1629644219a88dbB053D34E8e877596B00 — bukan proyek mint).
- Dikenal (sudah di snapshot): NIGHT 0x427aed3f7427b48e45f5e648105aa1b77724cf14 (9.537/10.000), Steady 0x4919aff275a3cf126a8f9fd280ae8cd24d734ccf (453 minted), HELIX 0x5e0ca9e1ecb5a6205e0b0d7a1fbe16983d2e8665 (718), AGENTMINER 0x8670e99062ead2ce5402754aede769602fdf38b8 (2.104), ROSE 0x8f41960b7a6e6fb2423a426491d8a5ca6386ef47 (798), Lanternfield 0x9aab6e84096a780f9400cdd4e230faa41b4545f2 (860/7.500, sudah di-mint user).
- OBFG 0x5314071bba19943f58347ba5dec423e5032a6818 — recheck Boltbook 04:05 WIB: totalSupply 558/1.500, freeMinted 558/1.230, freeRemaining 672, mintOpen 1. Dikenal sebagai track-C lead gate-blocked (tidak ada di bagian contracts snapshot; status gate tetap FAILED — tidak ada website terverifikasi baru di post ini).
- ONIAGENT (post tanpa alamat): share sale, 2/2.220.000 share, tier 1 **berbayar 0,0005 BNB** — bukan free, bukan lead.
- Post tanpa alamat lengkap di front page (THYRK, SNAKE, EMBER, HIPPO, ACORE, Agentx, SPEC, FORGE Pass 0x7333...6d89) — nama sudah dikenal dari run sebelumnya, tidak ada alamat baru yang tercetak.
- **BARU (1) — Voxel Sprite (PX24)** 0xe712510fcb27935e657e41ebb97982d6b123136c — post drzein.ai 21:02 UTC (04:02 WIB): "mint(1) verified at 0 BNB", 516/1.731, runtime ~7.398 byte. Sourcify exact_match, verifiedAt 2026-11-10T06:08:56Z (BUKAN launch time). ABI: AgentNFTLiteFixed — mint, costOf, mintOpen, MAX_SUPPLY, agentIds, agentTokenIdOf, mintWithAgentTokenId, mintedByAgent; TIDAK ada free view. Bentuk: agent-mint-shaped (AgentGate via fungsi agent). Launch time UNVERIFIED; first-mint on-chain BELUM diverifikasi run ini.
- **BARU (1) — TEGONG MIAO ($MIAO)** 0xB436617B7B5542f9C091A932654e9aeEfa4A182a — post Boltbook: freeClaimed **999/999 HABIS** ~8 jam sesudah buka; paid lane 0/4.000. **SOLD OUT — excluded, tidak ada aksi.** ABI (TegongMiaoToken) lolos bentuk sale S1-ish: agentIdRegistry (literal registry 0x60B9…022F ADA di metadata), claimFree, freeClaimed, freeClaimedByWallet, freeShares, mint, price, tokensPerShare — dicatat saja karena pool sudah habis.
- Author page drzein.ai https://boltbook.fun/u/drzein?lang=en — HTTP 200, **25.181 byte**, 10 post terbaru (~10 jam terakhir), template bytecode-inspection yang sama. **9 kontrak BARU di bawah ini, semua belum di seen/snapshot:**

| # | Proyek | Alamat | Post | Template / bentuk ABI |
|---|---|---|---|---|
| 1 | Chrome Runner ($CY24) | 0x731d879ee2cd4bbf32efef9178d51d5c1441d052 | 1 jam lalu, mint(1) @ 0 BNB | AgentNFTLiteFixed; agentIds/mintedByAgent/mintWithAgentTokenId; mint+costOf+mintOpen; tanpa free view |
| 2 | BOLTBOTS (BOLT) | 0xdc0cf81f5d38484d1c3b2f2a2c6a11d6d355a56e | 2 jam lalu, mint(1) @ 0 BNB | Boltbots; pola sama AgentNFTLiteFixed; tanpa free view |
| 3 | Agc (AGC) | 0xdac222886b887fc5b6262889b189b8eb57e99794 | 3 jam lalu, bare mint() @ 0 BNB | AgcNFT; agentIdRegistry+holdsAgentId; FREE_CAP/freeClaimed/freeMinted; mint+mintOpen |
| 4 | Skua Repeater (SKRR) | 0x9081f02876c173d0c69f042959cfd0d61c668b17 | 4 jam lalu, mint(1) @ 0 BNB | AgentNFTLiteFixedHeld; pola agent gate sama; tanpa free view |
| 5 | HASHHIVE (BEE) | 0x318abbb76631bdd4111ce2951f368fdb48def905 | 6 jam lalu, mint(1) @ 0 BNB | HashHive; freeLeft/freeMintX/FIRST_FREE_CAP/X_FREE_CAP/firstFreeByWallet; **TIDAK ada fungsi agent di ABI** — agent-shape UNVERIFIED (butuh cek registry di bytecode/source) |
| 6 | Airdrop Card (ACARD) | 0xf1d544cc495a05320f36cd02d12e8ef9d9fbff69 | 7 jam lalu, bare mint() @ 0 BNB | AirdropCardNFT; agentIdRegistry+holdsAgentId; FREE_CAP/freeClaimed/freeMinted |
| 7 | Daybreak Drachma (DBDM) | 0xa8a508ee984277a548f096117d58266afa5c259e | 8 jam lalu, mint(1) @ 0 BNB | DaybreakDrachma; agentIdRegistry+hasAgentId+PAID_REQUIRES_AGENT_ID; free lengkap (FREE_SUPPLY, claimFree, freeMint, freeMinted, freeRemaining, isFreeOpen, mintFree) — bentuk agent+free terkuat |
| 8 | Forge Machine (ME30) | 0xa545c8726bcf4acf840dac521b369911fe2abc8d | 9 jam lalu, mint(1) @ 0 BNB | AgentNFTLiteFlex; agent gate + freeLeft/freeOf/setFree |
| 9 | Pulse Runner ($CY30) | 0xa5f518e3dc77ccd714b49ec9643bfe8702c65968 | 10 jam lalu, mint(1) @ 0 BNB | AgentNFTLiteFlex; agent gate + freeLeft/freeOf/setFree |

- Catatan bentuk: literal alamat registry 0x60B9…022F TIDAK ada di metadata JSON ke-10 kontrak di atas (registry di-pass sebagai constructor arg, bukan di source) — bukti agent-shape adalah fungsi gate-nya (agentIds/agentIdRegistry/holdsAgentId/mintedByAgent), bukan literal. Pengecualian: MIAO (literal ADA).
- Semua 10 kontrak baru: **launch time UNVERIFIED, % free UNVERIFIED, slot user UNVERIFIED, first-mint on-chain BELUM diverifikasi** — serahkan ke parent/scan leg untuk re-read + tambah snapshot watchlist. Jangan laporkan sebagai early lead sebelum first-mint terverifikasi on-chain.

## ROUTE 5a — Sourcify recently-verified feed
- GET https://sourcify.dev/server/v2/contracts/56?limit=20&sort=desc — HTTP 200, 4.213 byte; verifiedAt 2026-11-12 19:21–21:00 UTC (= 13 Nov 02:21–04:00 WIB). Ke-20 alamat BARU (tidak di seen/snapshot).
- Shape-check via `?fields=metadata` (ABI lengkap). Catatan teknis: endpoint `/v2/contract/56/<addr>` polos hanya mengembalikan ringkasan match (209 byte, tanpa ABI); sub-path `/metadata`, `/files/tree`, `/stdJson` 404; repo.sourcify.dev `contracts/{full,partial}_match/56/<addr>/metadata.json` 404 untuk semua 22 alamat yang dicoba (+ 3 connection closed). `?fields=metadata` yang akhirnya berhasil.
- **Checked-not-agent-shaped (18):** 4× flash-loan adapter (AaveV3 0x08a266c6963925127de3786D88d46a1AE57eE759, RadiantV2 0x466b78045dd6234d4f4aE4004a73A0cD59B4EfD0, PancakeV3 0x8AFCfC0F3E13E4B65dA83d32721F55f01cc2fB75, UniswapV3 0xB0C99BD34201C55fb73e0eaB6A0B78be75DCa8e2), FeeSplitterV4 0x16fADa4294a5a757B7f78A89a7944A7F2561a328, PangeaCoinV4 0x841CB71bE5F50Bd3CFD53457f7964c37B0e916ea, MemeMMOneClick 0x437c4E4Ad7882A9e66f324c2C265DCb9Af812acC, BinanTraderDepositFactory 0x4425C57E5Ff2aC0A5180A54Fc3D5E36F70Ba05Cc, SpecToken 0x469AC1F93D5b05E209eCA804759Aa2b6ac70A424 (ERC-20 dividend, mint tanpa agent/free), DeFaiFinanceDollarToken ×3 (0x57A39268fFAc91a9A7b0AEAA5671b9F749Dae452, 0x586049594a1eeA267872af638AD3bD3692Ef0566, 0xC1b7a528262b8f1b26e09470a742492fc359f302), NiHaoCatSeppukuToken 0xD6E7B8cf9324a0FbE0e6e4d631E4B7D61578182E, SabosKingToken 0x70d8197EE454e081E15455f6d00c9507735F3ABb, virtualToken 0xE2c057f3A1d0453d8F2F9D15024DaF6c3B471844, VidunioAI 0xb813d0363c40872bf0CaAa7C8058197C52C24000, BatchSellerV4 0xF1E0D4461273d9923181716E3691Db5126900629, Claim.sol 0xeA8ad2c9C8b22030372c68c894af001d1E5a22D8 (hanya 1 fungsi `claim`, tidak terklasifikasi), IntentMeshRouter 0x77ac83F32645fb01457C6365F29d5324532Ed3F2.
- **Borderline (1) — SPEC pair:** SpecLaunchpad 0x57Fc464839dfC7A4BAB5c07d6CFeF011CfC77514 (verifiedAt 19:23:26Z) — AGENT_REGISTRY, accountAgent, mintedByAgent, mint, costOf, mintOpen, tokensPerShare, MAX_SHARES, openedAt; **TIDAK ada free-share view** → GAGAL bentuk S1 secara ketat. Pasangannya SpecToken 0x469AC1F93D5b05E209eCA804759Aa2b6ac70A424 (19:23:31Z). Konteks Boltbook: post "SPEC recheck #4" — 1.032 mint dari 1.006 wallet unik, tutup 07:00 WIB. **Bukan lead run ini** — perlu cek on-chain parent: costOf(user,1), quotaOf(user), nilai AGENT_REGISTRY(), dan launch time; bila ada jalur free terverifikasi, baru naik jadi track-C lead.
- MIAO (bukan dari feed, dari Boltbook) — lihat Route 2: bentuk S1-ish tapi sold out.

## ROUTE 3/5b — Web/social sweep (EN + ZH)
- Query EN: "Agent ID free mint BSC Binance Agentic Wallet new launch". Query ZH: "免费份额 首个免费 Agent ID BSC 免费铸造".
- Semua hit sudah dikenal: Agentic Gangster 0x0a2a07ef09dd7d83e2312476f0588abaa3e34ce3 (snapshot; thecolony.uk 9 Nov), First-Dollar Grove 0x56466afBcC2FDB847ed2cf5Bf78Ec1B213253611 (snapshot), AGENT MAO (dikenal), Pixel Fox 0x9134ae94ab0739cf0e0f4f5e9cacfa5e1d029b0c (snapshot), AGENT COSMOS 0x3Aeda314ec05BC22E3c26a543E16Df2B8cC8fe69 (snapshot), Oathbots 0xb777c52296f0d7d3c5cab7ae0c1aaac6b014b256 (dikenal dari daftar job; tidak di snapshot/seen saat ini), AgentLabs agentlabs.fun (dikenal), Cosmic Sentinel 0x88731d1eb41c36f3d705fdb58b658244c06afc36 (SUDAH di snapshot — site cosmic-sentinel.pages.dev/mint, first mint free Agent ID, paid sesudahnya).
- AgentGoldMiner 0xd3c7bd6cb1fb1025c4d17e3c51b1b531efbd6544 — post Binance Square 25 Okt 2026 (18 hari lalu), tidak di seen/snapshot, umur >24 jam → age-excluded, bukan temuan baru.
- **Tidak ada proyek benar-benar baru dari sweep ini; tidak ada site link baru** yang perlu direct-fetch /skill.md /launch.json /api/stats /api/verify.

## ROUTE 6 — Pelengkap
- Binance Square (via search-index, binance.info): hit-hit di atas semua proyek dikenal; tidak ada site link / kontrak baru.
- Odaily https://www.odaily.news/en/newsflash — terbaca (crawl 21:17 UTC): hanya berita makro/pasar (saham AS, ETH, Coinbase, dst); **tidak ada item Agent ID / free-mint** → nihil.
- PANews https://panews.io — terbaca (crawl 21:17 UTC): headline ETH/GRAM/MSCI/event; **tidak ada item Agent ID** → nihil.
- DappBay https://dappbay.bnbchain.org/category/ai — HTTP 200, 1.780.794 byte; grep voxel/px24/cosmic-sentinel = 0 hit → PX24 & Cosmic Sentinel tidak terdaftar di DappBay (ketidakhadiran bukan bukti apa-apa; DappBay curated/lambat).

## BRIDGE — scan-bridge.json
- Total 116 kontrak. **0 kontrak yang belum ada di snapshot DAN tidak bertanda same_owner_discarded** — semua sudah masuk snapshot (termasuk kunci bridge-0x…) atau sudah same_owner_discarded. Tidak ada temuan pelengkap scan baru untuk dilaporkan sebagai lead. (Read-only; file tidak ditulis.)

## UNTUK PARENT (merge)
1. 10 kontrak baru agent-mint-shaped (PX24 + 9 author-page drzein) → verifikasi first-mint on-chain + launch time; bila first-mint terverifikasi, tambah ke snapshot watchlist (early-lead rule) dan laporkan sekali sebagai EARLY bila memenuhi syarat.
2. SPEC launchpad 0x57Fc464839dfC7A4BAB5c07d6CFeF011CfC77514 → cek on-chain costOf/quotaOf/AGENT_REGISTRY + launch time (tutup 07:00 WIB per Boltbook).
3. MIAO sold out — catat excluded, tanpa aksi. OBFG tetap gate-blocked track-C lead (558/1.230 free, 672 tersisa).
4. Tidak ada kandidat / strong lead / track-B / track-C lead baru dari kaki discovery run ini.
