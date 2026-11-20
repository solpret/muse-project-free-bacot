# Discovery run Free Bacot 2026-11-10 10:01 WIB (tag 1001) — ringkasan leg discovery (READ-ONLY)

Tidak ada preview/mint/claim/swap/sign. Snapshot/seen/bridge tidak ditulis oleh leg ini
(kecuali merge-clean yang menambahkan discovery terverifikasi).

## 0. Catatan jaringan run ini
- VM exec: google.com curl 000 (10:32 WIB); bsc-dataseed1 OK 200 (blok 132704365, 10:32 WIB).
  Jaringan flapping: grove-check 10:02 WIB gagal total (bahkan google.com), hot-leg 1024 leg4
  masih sempat baca sebagian (blok 132704774, 157 read_failed).
- Pre-flight Ankr: FAIL 14,1 dtk HTTP 401 Unauthorized (head 132705988) — outage Ankr berlanjut
  sejak 2026-11-09 ~13:33 WIB. Scan leg FAST-FAIL; watermark tetap 132512564; gap ~193.400 blok.

## 1. Boltbook route 2 — browser.open (crawl cache ~16 jam, 2026-11-09 11:03 UTC EN / 10:50 UTC ZH)
- EN: front page 179 baris; ZH: 178 baris. Hot-leg 1024 (live, 10:24 WIB) membaca EN 47870B +
  ZH 47226B — lebih segar; temuan baru hot-leg 1024: 2 alamat (lihat §5).
- Temuan EN yang BELUM di snapshot saat dibaca:
  - **Iron Bloom (ME01) 0xb8c7658f6fc4d0d91da2dd6faeaf0328ff57ccaf** — post ~18:05 WIB 9 Nov:
    345/786, mintOpen true, mint(1) value 0 lolos, Sourcify exact_match. DIVERIFIKASI run ini
    (lihat §1a) -> watchlist-only.
  - HELM 0xe0df49c281b8584f03ed21beac0e5002ec4a0599 — ZH post ~22:07 WIB 9 Nov: 542/555.
    Baca ulang run ini: totalSupply 555/555 = SOLD OUT -> excluded, tidak masuk watchlist.
  - EMBER 0xaaef5bb8a7363b5997f17149d554640dc35f306d — 434/5.555, first mint free, TANPA gate
    Agent ID (requireAgentId off) + 7,8% -> bukan narasi agent-gated, log saja.
  - Orin Agent — 4.790/5.000 free (95,8%), Sourcify UNVERIFIED, alamat kontrak terpotong di crawl
    -> tidak bisa diverifikasi, log saja.
  - MWORKS 0xCc844748C64b9b8e45aC4504553C9757c7CDB7E0 — 507/5.555, burst; SUDAH di snapshot
    (Marbleworks, minted-by-user-2026-11-09); baca ulang: freeMinted 1111/1111 (pool gratis habis,
    tak berubah — pola artefak; user sudah pegang 1; tidak dilaporkan).
  - Sudah di snapshot: Agentite (early-lead-reported), FourAgent, AGENT CORE (promotion-discarded),
    Orivia (watchlist-only), Pokechain (sold-out-free-2026-11-09), Kappaxis, BMT Agents (sold out).
- Temuan ZH yang BELUM di snapshot: Hivebyte 0xae9d85e78a609f185b4682d87da12d13b03cf8d8 —
  ternyata SUDAH di snapshot sebagai '0xaE9d85E7' (watchlist-only-mature-newly-noticed-2026-11-09);
  baca ulang: totalSupply 292, freeClaimed 288/2000 = 14,4%, tanpa perubahan.

## 1a. Iron Bloom — verifikasi penuh run 1001 (run-2026-11-10-1001-newdisc.json)
- On-chain (blok 132706216): totalSupply 715/786 (91,0%), MAX_SUPPLY 786, mintOpen=1,
  balanceOf(user)=0, costOf(user,1)=0, price()=0,0002 BNB, mintedBy(user)=0, mintsLeft(user)=10,
  MAX_PER_WALLET=10, agentIds()=0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F (registry resmi).
  freeClaimed/freeMinted: tidak ada view (None). contractURI(): None. START_TIME: None.
- Sourcify exact_match, verifiedAt 2026-11-09T06:49:20Z. ABI: mint/mintWithAgentTokenId/costOf/
  price/mintsLeft/mintedBy/MAX_SUPPLY/MAX_PER_WALLET; devdoc: "first mint for every wallet is free".
- Website GATE TERVERIFIKASI (metode I/H/G): tokenURI(1) =
  https://agent-mecha-002-iron-bloom.pages.dev/meta/1.json (external_url = site root);
  /llms.txt mencetak 'Contract: 0xB8C7658f6Fc4D0d91dA2Dd6FAEAF0328FF57CCaf' + 'first mint is free';
  /agent.json mencetak contract + supply 786 + price 0.0002 BNB + freeRule first-mint.
  Metode A (pencarian alamat kontrak): 0 hit relevan. Metode C (metadata Sourcify): tanpa URL.
  Site root adalah SPA (tanpa kontrak di teks hasil fetch) — bukti bertumpu pada /llms.txt +
  /agent.json (preseden SEVENFOLD).
- Umur UNVERIFIED: tanpa launch time di /llms.txt//agent.json; first-mint tak diketahui
  (Ankr getLogs 401; public RPC -32005). Post Boltbook 18:05 WIB 9 Nov (345/786) hanya batas atas.
- Free% UNVERIFIED: tanpa free counter; aturan first-mint per-wallet tanpa pool global
  (requiresGlobalFreePool=false); 715/786 mencampur free+paid, bukan pengganti % free.
- BUKAN early lead (first mint tidak terverifikasi on-chain run ini), BUKAN strong lead
  (umur + free% unverified), BUKAN kandidat. Watchlist-only. Tidak ada di same-owner-discards.
  TIDAK preview/mint.

## 1b. Orbit Lantern — discovery via hop jaringan (Agent Mint Network)
- Iron Bloom /llms.txt menautkan next: agent-cosmic-003-orbit-lantern.pages.dev (posisi 3 dari 10).
  /llms.txt-nya mencetak Contract: 0x83B653aab5cAEa240DAcf722f8fa90E479849b5E + 'first mint is free'.
- On-chain: totalSupply 625/794 (78,7%), mintOpen=1, costOf(user,1)=0, price 0,00015 BNB,
  mintedBy(user)=0, balanceOf(user)=0, agentIds()=registry resmi, name Orbit Lantern, symbol CO01.
- Website TERVERIFIKASI (llms.txt mencetak kontrak persis). Umur UNVERIFIED (tanpa postingan
  Boltbook, tanpa launch time, first-mint tak diketahui — Ankr 401). Free% UNVERIFIED
  (tanpa free counter; first-mint per-wallet). Watchlist-only; BUKAN early/strong/kandidat.
  Tidak ada di same-owner-discards. TIDAK preview/mint.
- Berikutnya di jaringan: agent-botanical-004-moss-signal.pages.dev (belum dicek — tugas run berikut).

## 2. Sourcify feed route 5a — 20/20 dicek, 0 S1/S2
- Feed: browser.open (verifiedAt 2026-11-10T03:25:03Z s.d. 03:35:17Z) + curl (200, ~18 dtk).
- Shape-check: run-2026-11-10-1001-feed-shape.py (5 worker, timeout 30 dtk) — 20/20 selesai,
  0 S1, 0 S2, 0 error, 55,8 dtk. File: run-2026-11-10-1001-feed-shape.json.
- Endpoint ABI yang benar: /server/v2/contract/56/{addr}?fields=abi (singular 'contract';
  bentuk jamak 'contracts' 404).

## 3. Route 6b Odaily + PANews — 0 hit
- Odaily newsflash (browser.open, crawl <1 mnt): hanya berita makro/CEX; 0 hit 'free mint'/
  'Agent ID'/'免费铸造'/'免费份额'.
- PANews homepage (browser.open, crawl <1 mnt): 0 hit relevan.

## 4. Route 3 sweep (browser.search, EN + ZH)
- Query 'Binance Agent ID free mint NFT BSC 免费铸造 免费份额': 8 hasil — SEMUA lama
  (22–27 Okt, 1 Nov): daftar '22 projects' (Black Hole, LeadLoop, UMBRA — semua sudah di
  snapshot), Pixel Fox 0x9134ae94... (sudah di snapshot), PocketDragons 0x2cff8302... (sudah di
  snapshot), AGENT MAO (sudah di snapshot/track-c), panduan umum. 0 proyek BARU.

## 5. Hot-leg 1024 (10:24 WIB) — 2 alamat baru, keduanya unverified
- 0x60f7212010600bcbebbfe2a558237004c7f401fd — ABI Sourcify timeout; semua view on-chain None
  run ini. 0xbf87e6fe445e235699103df56ef8d40a88b9e8ba — Sourcify 404 (unverified); semua view None.
  Keduanya watchlist-only (unverified), retry run berikut. Bukan di discards.
- Hot-leg 1024 leg4 (parsial, 157 read_failed): HUNT PASS 1848->1849, Ghostling 4115->4118,
  NUSA 363->364. Report: NONE (silent).

## 6. Bridge (kaki pelengkap scan)
- scan-bridge.json: 116 kontrak, mtime 2026-11-09 01:21 WIB (tidak berubah); 7 tidak di snapshot
  & tidak discarded — semuanya pola mint ERC-20 lama (3–8 Nov), website_no_pointer_found,
  bukan NFT agent-mint; 0 promosi. same_owner_discarded: 7 — tidak pernah dipromosikan.

## 7. Track-B + Grove (special2, blok 132707816; script timeout 280 dtk, hasil parsial)
- binanceai.fun: launched=0, failed=1, isRefundPhase=1, totalShares=3110, tokenClaimed(user)=0,
  saldo TOKEN user=0 — TIDAK BERUBAH (closed-refund-phase-2026-11-07, sudah dilaporkan sekali).
- Grove: freeMinted=2500/2500, FREE_SUPPLY=2500, freeOpen=0, balance user=0 — TIDAK BERUBAH.
- MONOLITH: totalSupply 654/5555. NightBandits: freeUsed 444/444 (pool habis). KingsGame: batch
  gagal total (nilai lama dipertahankan). Track-C specifics (BOME/NUSA/FOUNT/PACTA) tidak tercapai
  sebelum timeout — tercakup reread track_c.
