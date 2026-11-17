#!/usr/bin/env python3
"""Merge run 1831 reread + triage + focused checks into onchain-snapshot.json.
Preserves old values when fresh reads are None (read artifact, not zero).
Writes run-2026-11-09-1831-merge.json (summary).
INTERVAL 27.57 min from block timestamps 132573635 (18:06:29 WIB) -> 132577311 (18:34:03 WIB).
NOTE: run-2026-11-09-1831-analyze.py used interval=50.0 (copied bug from 1801 analyze);
velocity was recomputed with 27.57 for the run notes below."""
import json, copy
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
snap = json.load(open(f"{BASE}/onchain-snapshot.json"))
rr = json.load(open(f"{BASE}/run-2026-11-09-1831-reread.json"))
tri = json.load(open(f"{BASE}/run-2026-11-09-1831-triage-new.json"))
follow = json.load(open(f"{BASE}/run-2026-11-09-1831-triage-followup.json"))
focus = json.load(open(f"{BASE}/run-2026-11-09-1831-trackc-focus.json"))
INTERVAL = 27.57
BLOCK = rr.get("block")
contracts = snap.setdefault("contracts", {})
track_c = snap.setdefault("track_c", {})
n_upd = 0
for name, v in contracts.items():
    r = rr.get("reread", {}).get(name)
    if not isinstance(r, dict):
        continue
    prev_ts = v.get("totalSupply")
    new_ts = r.get("totalSupply")
    minted = None
    if isinstance(prev_ts, int) and isinstance(new_ts, int):
        minted = new_ts - prev_ts
        prev_rate = v.get("currentRatePerMin")
        rate = minted / INTERVAL
        ratio = (rate / prev_rate) if (isinstance(prev_rate, (int, float)) and prev_rate > 0) else None
        v["previousTotalSupply"] = prev_ts
        v["mintedInInterval"] = minted
        v["intervalMinutes"] = INTERVAL
        v["currentRatePerMin"] = round(rate, 4)
        v["previousRatePerMin"] = prev_rate
        v["velocityRatio"] = (round(ratio, 2) if ratio is not None else None)
        v["velocityLegPasses"] = bool(ratio is not None and ratio >= 1.5 and minted >= 20)
    for k in ("totalSupply", "totalMinted", "freeClaimed", "freeMinted", "FREE_SUPPLY",
              "MAX_SUPPLY", "mintOpen", "balanceOf_user", "freeClaimed_user"):
        if r.get(k) is not None:
            v[k] = r[k]
    fs = v.get("FREE_SUPPLY")
    fc = v.get("freeClaimed")
    if isinstance(fs, int) and fs and isinstance(fc, int):
        v["freePctVerified"] = round(100.0 * fc / fs, 2)
    v["lastReadBlock"] = BLOCK
    v["lastReadWib"] = "2026-11-09 18:3x WIB"
    v["runNote1831_1109"] = (
        f"Run 1831 (blok {BLOCK}, interval {INTERVAL} mnt vs run 1801): "
        f"{prev_ts}->{new_ts} (+{minted if minted is not None else 'n/a'}), "
        f"velocity {'LOLOS' if v.get('velocityLegPasses') else 'GAGAL'}; "
        f"free={v.get('freeClaimed')}/{v.get('FREE_SUPPLY')}; bal_user={v.get('balanceOf_user')}; "
        f"status {v.get('status')}."
    )
    n_upd += 1
# track_c reread merge (lean views only)
n_tc = 0
for name, v in track_c.items():
    if not isinstance(v, dict):
        continue
    r = rr.get("track_c", {}).get(name)
    if not isinstance(r, dict):
        continue
    for k in ("totalSupply", "freeMinted", "freeSharesRemaining", "balanceOf_user", "freeClaimed_user"):
        if r.get(k) is not None:
            v[k] = r[k]
    v["lastReadBlock"] = BLOCK
    v["lastReadWib"] = "2026-11-09 18:3x WIB"
    v["runNote1831_1109"] = f"Run 1831 (blok {BLOCK}): totalSupply={r.get('totalSupply')} freeMinted={r.get('freeMinted')} freeSharesRemaining={r.get('freeSharesRemaining')} bal_user={r.get('balanceOf_user')}."
    n_tc += 1
# focused track_c notes (values IDENTICAL to run 1801 for all 9 items)
FOCUS_NOTES = {
 "DROID": "Run 1831 (blok 132579057): opened 0 (MASIH BELUM DIBUKA), freeMinted 736/2000 FREE_SHARES, totalMinted 736, paused 0 - IDENTIK run 1801, tetap watchlist-only-not-open.",
 "OSK": "Run 1831 (blok 132579057): opened 0 (MASIH BELUM DIBUKA; saleStart 2026-11-03 23:32:53 WIB, saleEnd 2026-11-06 23:32:53 WIB sudah lewat tanpa dibuka), totalMinted 2278 - IDENTIK run 1801, tetap watchlist-only-not-open.",
 "IMARS": "Run 1831 (blok 132579057): opened 1, freeMinted 300/300 FREE_SHARES (pool gratis habis), totalMinted 624 - IDENTIK run 1801, tetap excluded, BUKAN lead.",
 "NIULAI": "Run 1831 (blok 132579057): launched 0 (MASIH BELUM DIBUKA), freeClaimed 4444/4444 freeShares, phase 4 - IDENTIK run 1801, tetap watchlist-only-not-open.",
 "KillZero-K0-sale": "Run 1831 (blok 132579057): launched 0 (MASIH BELUM DIBUKA), totalFreeClaimed 0, FREE_SHARES 0, totalMintCount 216 - IDENTIK run 1801, tetap watchlist-only-not-open.",
 "0x260bf39a-sale": "Run 1831 (blok 132579057): launched 0, launchTime 0 (MASIH BELUM DIBUKA), FREE_SLOTS 500, freeClaimed 500/500 (pool terisi penuh sebelum dibuka) - IDENTIK run 1801, tetap watchlist-only-not-open; bila kelak dibuka, pool gratis sudah habis.",
 "BoxBigem-3Ee9": "Run 1831 (blok 132579057): freeMinted 7.76e26/1e28 FREE_POOL (7,76%), freeRemaining 9.224e27, mintStart 2026-11-04 20:30 WIB, mintEnd 2026-11-07 20:30 WIB (jendela mint sudah lewat) - IDENTIK run 1801, tetap watchlist-only-age-unverified.",
 "DeY": "Run 1831 (blok 132579057): freeCount 2/1000 FREE_SLOTS (998 tersisa), freeByAddress(user)=0 (slot TERBUKA) - IDENTIK run 1801, tetap track-c-lead-gate-blocked (tidak ada website terverifikasi).",
 "FANBEIMAO-824d": "Run 1831 (blok 132579057): freeCap 2000, freeSold 1124 (876 tersisa), isFreeOpen 0 - IDENTIK run 1801, tetap track-c-lead-gate-blocked (tidak ada website terverifikasi).",
}
for k, note in FOCUS_NOTES.items():
    if k in track_c and isinstance(track_c[k], dict):
        track_c[k]["runNote1831_1109_focus"] = note
# --- new entries run 1831 ---
# 1. Shard Id — watchlist-only, age unverified (NOT early lead: first mint not corroborated as launch)
contracts["Shard Id"] = {
 "address": "0x5c46de8d0c5dfdf535558d363f492967cd5e146b",
 "status": "watchlist-only-age-unverified-2026-11-09",
 "name": "Shard Id", "kind": "ERC721",
 "totalSupply": 7849, "totalMinted": 7858, "MAX_SUPPLY": 10000, "mintOpen": 1,
 "PRICE": 2700000000000000, "MAX_PER_WALLET": 3,
 "freeClaimed": None, "FREE_SUPPLY": None, "freePctVerified": None,
 "userBalance": 0, "freeClaimed_user": None,
 "xVerified": False, "velocityVerified": False,
 "website": None,
 "gate": "BELUM DICEK (post Boltbook 429 saat triase; pembacaan browser diminta run 1831, hasil menyusul). tokenURI(1) tanpa external_url; contractURI() None.",
 "launchNote": "Usia peluncuran UNVERIFIED: satu mint terverifikasi blok 132576049 = 2026-11-09 18:24:35 WIB (ts blok via dataseed); nama terlihat ~17:03-17:10 WIB tanpa kontrak; totalSupply 7849 saat triase (~18:52 WIB) mengisyaratkan minting mungkin sudah berjalan sebelum 18:24. Koroborasi first-mint via getLogs TIDAK BISA: Ankr 401 + eth_call historis dataseed gagal di semua blok uji (132400000/132500000/132570000/132575000/132576049). BUKAN early lead (first mint tidak terverifikasi sebagai launch); BUKAN strong lead (free% unverified).",
 "baselineNote": "Ditemukan via Boltbook front page run 1831 (post https://boltbook.fun/p/tOp6Kw9hmdon, drzein.ai ~18:24 WIB). Triase on-chain run 1831 (blok 132579316 + followup 132579538): totalSupply 7849, totalMinted 7858, MAX_SUPPLY 10000, mintOpen 1; registry() = 0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F exact; Sourcify exact_match (HeroArenaShard.sol): mint(uint256) mensyaratkan Agent ID handle + EOA + MAX_PER_WALLET 3; quote() = first mint per wallet GRATIS (cost 0), mint ke-2/3 @ PRICE 0.0027 BNB; quote(user,1) cost 0, mintedBy(user) 0, slot TERBUKA. tokenURI(1) = on-chain JSON (Shard Id #1, Rarity Common, 'Shard Id from HERO ARENA. Combine 3 Shards into a Hero.'), tanpa external_url. Tidak ada di same-owner-discards.json. TIDAK pernah preview/mint. Baseline velocity untuk run berikut.",
 "lastReadBlock": 132579538, "lastReadWib": "2026-11-09 18:5x WIB",
 "runNote1831_1109": "Run 1831: baru masuk snapshot sebagai watchlist-only-age-unverified (lihat baselineNote).",
}
# 2. NEURA — checked, NOT a lead (no pair + not agent-shaped)
contracts["NEURA"] = {
 "address": "0xf027B84D8b1Ae4025fbDa156e843b2773B953DFC",
 "status": "checked-not-lead-2026-11-09",
 "name": "NEURA", "kind": "claim-distributor",
 "token": "0x77da87aeebe07448e896bb5e41da74b451c1e665",
 "owner": "0x2193d6e0468ac747823e7e876f1acd34ffe43a67",
 "claimOpen": 1, "saleOpen": 1,
 "FREE_POOL": 2000000000000000000000000000, "freePoolRemaining": 1997260000000000000000000000,
 "FREE_PER_WALLET": 20000000000000000000000, "freeClaimCount": 137,
 "freeClaimed_user": 0,
 "xVerified": False, "velocityVerified": False,
 "website": None,
 "baselineNote": "Ditemukan via Boltbook run 1831 (post /p/nUjb3zLZB2uQ, e1onmusk.ai ~18:27 WIB: claimFree() 20.000 NEU, tx 0x443d421abee8037b87862b95b34b5f09c57ef7d8179a61ed94db23418bb54ce4 blok 132574109). Triase on-chain run 1831 (blok 132579316/132579538): distributor Sourcify exact_match (claimFree() tanpa argumen, freePoolRemaining, FREE_POOL, FREE_PER_WALLET, saleOpen, buyWithBnb/Usdt, quoteBnb/Usdt); claimOpen 1, saleOpen 1, FREE_POOL 2e27, freePoolRemaining 1.99726e27 (~99.863 wallet tersisa), FREE_PER_WALLET 2e22 (20.000 NEU), freeClaimCount 137, freeClaimed(user) 0 (slot TERBUKA). GUGUR 2 kaki: (i) LP HOOK - TIDAK ADA pair NEU/WBNB maupun NEU/USDT di PCS V2 (getPair via router.factory() terverifikasi 0xca143ce32fe78f1f7019d7d551a6402fc5350c73, keduanya 0x0; percobaan pertama gagal karena alamat factory salah ketik dari memori - dikoreksi dari skrip workspace); (ii) BUKAN agent-shaped - tidak ada agentRegistry/agentGate di ABI maupun bytecode (registry bytes FALSE). BUKAN track B (tanpa pair + tanpa narasi Agent ID) dan BUKAN track C (tanpa registry/AgentGate). TIDAK pernah preview/claim. Log saja.",
 "lastReadBlock": 132579538, "lastReadWib": "2026-11-09 18:5x WIB",
 "runNote1831_1109": "Run 1831: baru masuk snapshot sebagai checked-not-lead (lihat baselineNote).",
}
# 3. JOLT — checked, track-B-shaped but PAID fee (CLAIM_FEE > 0), not open
contracts["JOLT"] = {
 "address": "0x63C9d73f09bb7CCD8E363510676Bd9ecD563f8e4",
 "status": "checked-not-lead-paid-fee-2026-11-09",
 "name": "JOLT", "kind": "claim",
 "token": "0x7a3cd992e6aea95c684d71d1f33511ff1206d9e6",
 "owner": "0x0988d5b7042a65c7ef4e3631700fb0f108d85fc6",
 "pair": "0xcbea2b60178f026650c22dd1988a61e6ba7790a6",
 "launched": 0, "totalClaims": 283, "totalDistributed": 4064000000000000000000000,
 "endsAt": 1794225606, "startTime": 1793966406,
 "MAX_CLAIMS": 6, "MAX_PER_DAY": 2, "CLAIM_FEE": 200000000000000,
 "claimsOf_user": 0, "claimsTodayOf_user": 0, "hasAgentId_user": 1,
 "xVerified": False, "velocityVerified": False,
 "website": None,
 "baselineNote": "Ditemukan via Boltbook run 1831 (post /p/1G7HUS3CJ7_v, muhlis020201.ai ~18:26 WIB; totalClaims 280 ~17:13 WIB). Triase on-chain run 1831 (blok 132579316/132579538): Sourcify exact_match (claim(uint256,uint256,bytes), launched, launch, agentRegistry, hasAgentId, claimsOf, claimsTodayOf, endsAt, startTime, pair, poolReserve); launched 0, totalClaims 283, totalDistributed 4.064.000 JOLT, endsAt 1794225606 = 2026-11-09 19:00 WIB (season berakhir malam ini; launch() permissionless sesudah season per skill doc), startTime 1793966406 = 2026-11-06 19:00 WIB, MAX_CLAIMS 6, MAX_PER_DAY 2, claimsOf(user) 0, claimsTodayOf(user) 0, hasAgentId(user) 1, agentRegistry() = 0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F exact, pair JOLT/WBNB 0xcbea2b60178f026650c22dd1988a61e6ba7790a6 TERVERIFIKASI (token0 JOLT, token1 WBNB, reserves ~2,03 jt JOLT / 0,0397 BNB). GUGUR: CLAIM_FEE = 0,0002 BNB > 0 -> klaim TIDAK gratis (gas only) -> BUKAN track B, TIDAK PERNAH auto-claim; launched 0 -> belum terbuka. Maks 2 klaim/hari = 17.000 JOLT menurut post (ladder). Tidak ada di same-owner-discards.json. TIDAK pernah preview/claim. Log saja.",
 "lastReadBlock": 132579538, "lastReadWib": "2026-11-09 18:5x WIB",
 "runNote1831_1109": "Run 1831: baru masuk snapshot sebagai checked-not-lead-paid-fee (lihat baselineNote).",
}
# 4. MarsNexus — excluded, not gas-only free (VRF fee)
contracts["MarsNexus"] = {
 "address": "0xCBac4faC33aFB361e836E6a0120f5a5aAC9122B3",
 "status": "excluded-not-gas-only-free-2026-11-09",
 "name": "MarsNexus", "kind": "ERC721",
 "website": "https://marsnexus.fun",
 "xVerified": False, "velocityVerified": False,
 "baselineNote": "Ditemukan via Boltbook run 1831 (post /p/fKx92EcKA_-7, bigrich.ai ~18:31 WIB; situs marsnexus.fun). Triase dari post (tanpa triase on-chain penuh - sudah gugur di kaki gratis): total 12.000, totalMinted 10.843/12.000 (90,4%), activated true, paused false, maks 5 per Agent ID. Kartu pertama 0 USDT TAPI minter membayar fee Chainlink VRF dalam BNB (~0,0000562 BNB untuk #10844) -> BUKAN gratis gas-only; kartu ke-2 2,99 USDT, ke-3 s.d. ke-5 4,44 USDT. Jebakan: preview baw hijau (gasPrice=0) tapi tx nyata revert (status 0x0, tx 0x8d685035...) saat feeCap terlalu rendah; re-mint dengan feeCap >=0,3 gwei berhasil. BUKAN lead/kandidat; TIDAK pernah preview/mint. Log saja.",
 "lastReadBlock": 132579538, "lastReadWib": "2026-11-09 18:5x WIB",
 "runNote1831_1109": "Run 1831: baru masuk snapshot sebagai excluded-not-gas-only-free (lihat baselineNote).",
}
# 5. 0x92b379... — checked, agent-referencing token launch, NOT track-C shape
contracts["0x92b379d3807F68aD2bCfd013D831713D8C6dbdFB"] = {
 "address": "0x92b379d3807F68aD2bCfd013D831713D8C6dbdFB",
 "status": "checked-not-lead-2026-11-09",
 "name": "0x92b379d3807F68aD2bCfd013D831713D8C6dbdFB", "kind": "ERC20",
 "xVerified": False, "velocityVerified": False,
 "website": None,
 "baselineNote": "Ditemukan via Sourcify feed run 1831 (verifiedAt 18:31 WIB). Shape-check: lot-based token mint (mint/mintWithInviter/previewMint/quotaOfWallet/tokensPerLot/MAX_LOTS) dengan AGENT_ID_REGISTRY + AGENT_ID_REGISTRY_CODEHASH + isAgentWallet di ABI (hot-leg checker menandai agent=false karena melewatkan casing AGENT_ID_REGISTRY). TAPI: tanpa fungsi quote dan tanpa free views -> BUKAN bentuk sale S1/S2 track C; bukan NFT mint -> BUKAN track A. Flag untuk keputusan parent apakah dilacak; BUKAN lead. TIDAK pernah preview/mint. Log saja.",
 "lastReadBlock": 132579538, "lastReadWib": "2026-11-09 18:5x WIB",
 "runNote1831_1109": "Run 1831: baru masuk snapshot sebagai checked-not-lead (lihat baselineNote).",
}
# --- top-level run notes ---
snap["runNote1831_1109"] = (
 "Run 1831: re-read 606 kontrak + 83 track_c (blok 132577311, interval 27,57 mnt vs run 1801 - block timestamp 132573635 18:06:29 WIB -> 132577311 18:34:03 WIB). "
 "KOREKSI ANALISIS: run-2026-11-09-1831-analyze.py memakai interval=50,0 (bug salinan dari analyze 1801); velocity dihitung ulang dengan 27,57 mnt. "
 "Velocity LOLOS (terkoreksi): 0x4AB41152 (6,51x, +125 - mature, umur unverified, free% unverified, tanpa website), Motor Agent (2,49x, +608 - SUDAH minted-by-user #1282 + listing), "
 "0x57cf26c6... (80,23x - artefak ERC-20 tax/burn, checked-not-lead). TIDAK ADA promosi. Sellout baru: 0 (50 kontrak di ts>=MAX sudah di max sejak sebelum run ini, minted 0). "
 "Free-pool-exhausted baru: 0 (27 kontrak sudah 100% sejak sebelum run ini). Agentite: freeMinted 19/1000 = 1,9% (jauh di bawah 25%), tetap early lead. "
 "Marbleworks totalSupply 581->646 (+65), bal_user 1 (#458 dipegang). Motor Agent totalSupply 1429->2037 (+608), bal_user 1; freeClaimed() None run ini = artefak baca (sebelumnya 1256). "
 "Skunk Hollow all-null run ini kecuali bal_user 1 (artefak baca; #708 dipegang). Onyx Agent totalSupply tetap 4790, gate tetap FAILED. TIME CARDS totalSupply tetap 0 (buka 20:09 WIB). "
 "Scan leg FAST-FAIL (Ankr pre-flight 2x HTTP 401, outage sejak ~13:33 WIB; watermark tetap 132512564; gap ke head ~64.786 blok). "
 "EKSEKUSI: 0. Baru masuk snapshot: Shard Id (watchlist-only-age-unverified), NEURA (checked-not-lead: tanpa pair + bukan agent-shaped), "
 "JOLT (checked-not-lead-paid-fee: CLAIM_FEE 0,0002 BNB), MarsNexus (excluded-not-gas-only-free: fee VRF), 0x92b379d3... (checked-not-lead: token launch agent-referencing, bukan bentuk sale). "
 "Track-B binanceai: TIDAK BERUBAH (launched 0, failed 1, refund 1, totalShares 3110, tokenClaimed(user) 0, blok 132577464). Bridge: tidak berubah (mtime 2026-11-08 18:21); "
 "4 kontrak bridge tidak di snapshot (Ikigai, Panda Emoji Pack, 0x636fdfa9, ETHBack_Dividend_Tracker - semuanya lama Nov 3-8, gate gagal/berbayar, TIDAK ditambahkan); "
 "7 same_owner_discarded di bridge dicatat (tidak pernah dipromosikan). Star Agent (nama saja, tanpa kontrak) + STONK CHAIN (pool gratis habis, tanpa kontrak): log saja."
)
snap["runNote1831_1109_scan"] = (
 "Run 1831 scan: FAST-FAIL. Pre-flight Ankr ankr_getLogs 50 blok (132577301-132577350), 2 attempts: "
 "ATTEMPT 1 FAIL 12,8 dtk HTTP 401 Unauthorized; ATTEMPT 2 FAIL 12,7 dtk HTTP 401 Unauthorized "
 "(kredensial custom.ankr ditolak rpc.ankr.com; outage sejak ~13:33 WIB 2026-11-09). Watermark TIDAK dimajukan (tetap 132512564; "
 "gap ke head ~64.786 blok dan tumbuh - milik backfill, ikut gagal 401). Route 5c: tanpa output scan baru."
)
snap["runNote1831_1109_binanceai"] = (
 "Run 1831 track-B: binanceai.fun TIDAK BERUBAH - launched=0, failed=1, isRefundPhase=1, totalShares=3110, "
 "tokenClaimed(user)=0 (probe dataseed, blok 132577464). Status closed-refund-phase-2026-11-07; sudah dilaporkan sekali; tidak dilaporkan ulang."
)
snap["runNote1831_1109_age_exclusions"] = (
 "Run 1831 age-exclusions baru: 0. Item umur unverified tetap watchlist-only (Shard Id baru masuk dengan alasan itu)."
)
snap["runNote1831_1109_early_leads"] = (
 "Run 1831 early leads: TIDAK ADA early lead baru. Shard Id BUKAN early lead (first mint tidak terverifikasi sebagai launch: nama terlihat ~17:03-17:10 WIB tanpa kontrak, "
 "satu mint 18:24:35 WIB, totalSupply 7849 saat triase; koroborasi getLogs mustahil - Ankr 401 + eth_call historis dataseed gagal). "
 "Sourcify feed 20 terbaru (verifiedAt s.d. 18:36 WIB): 2 kontrak lebih baru dari file hot-leg 18:29 (0x6E31646D wave-NFT tanpa agent/free views; 0x1d9B09Fe validator/governance proxy) - BUKAN agent-shaped; "
 "0x92b379d3 (18:31 WIB) agent-referencing tapi bukan bentuk sale - dicatat checked-not-lead. Boltbook: Shard Id (watchlist-only), NEURA + JOLT (checked, bukan lead), MarsNexus (excluded), Star Agent + STONK CHAIN (tanpa kontrak, log saja)."
)
snap["runNote1831_1109_discovery"] = (
 "Run 1831 discovery (subagent + triase parent): NEURA distributor 0xf027B84D8b1Ae4025fbDa156e843b2773B953DFC (claimFree 20.000 NEU/wallet, pool ~99.863 tersisa, slot user TERBUKA) - GUGUR track B: tanpa pair NEU/WBNB maupun NEU/USDT (getPair via router.factory() terverifikasi, keduanya 0x0) + bukan agent-shaped (tanpa registry/AgentGate); "
 "JOLT 0x63C9d73f09bb7CCD8E363510676Bd9ecD563f8e4 (launched 0, endsAt 19:00 WIB malam ini, pair JOLT/WBNB TERVERIFIKASI 0xcbea2b60178f026650c22dd1988a61e6ba7790a6, reserves ~2,03 jt JOLT / 0,0397 BNB) - GUGUR track B: CLAIM_FEE 0,0002 BNB > 0 (tidak gratis); "
 "Shard Id 0x5c46de8d0c5dfdf535558d363f492967cd5e146b (Agent ID-gated, first-per-wallet GRATIS, PRICE 0,0027 BNB untuk mint ke-2/3, quote(user,1) cost 0, slot TERBUKA) - watchlist-only, umur + free% unverified; "
 "MarsNexus 0xCBac4faC33aFB361e836E6a0120f5a5aAC9122B3 (fee VRF ~0,0000562 BNB, bukan gas-only); Star Agent (nama saja); STONK CHAIN (free pool habis, tanpa kontrak); "
 "0x92b379d3 token launch agent-referencing (bukan bentuk sale). Route 3 sweep: 0 proyek baru (MOLT AGENT stale, sisanya excluded lama). Route 6: Square hanya item lama; Odaily 1 jam terakhir tanpa pengumuman Agent ID/free-mint; DappBay tidak dipakai (tidak ada proyek baru yang butuh cek gate). "
 "Pelajaran: alamat factory/router PCS V2 TIDAK BOLEH ditulis dari memori (keduanya salah 1 karakter, 39 char) - ambil dari skrip workspace / router.factory()."
)
snap["runNote1831_1109_velocity"] = (
 "Run 1831 velocity (interval TERKOREKSI 27,57 mnt dari timestamp blok; analyze.py salah pakai 50,0): LOLOS 3 - 0x4AB41152 (+125, 4,53/mnt, 6,51x - mature, umur unverified, free% unverified, tanpa website: BUKAN promosi), "
 "Motor Agent (+608, 22,05/mnt, 2,49x - SUDAH minted-by-user: BUKAN promosi), 0x57cf26c6... (ERC-20 tax/burn, artefak: BUKAN promosi). "
 "Tidak lolos: Rose Genesis +73 (2,65 vs prev 8,35), Marbleworks +65 (2,36 vs 7,66), Neon District CY01 +21 (0,76 vs 2,09). ERC-20 mint besar (MeowBark +2e24, MiniCoin +1,4e24, VOLT token +1e24) = artefak, prev_rate 0."
)
snap["last_run_wib"] = "2026-11-09 18:5x WIB"
snap["last_run_note"] = ("Run 1831: 606 kontrak + 83 track_c re-read (blok 132577311); 0 eksekusi; 0 promosi; 0 early lead baru; "
 "0 age-exclusion; scan fast-fail Ankr 401 (watermark 132512564); binanceai tetap refund; "
 "5 entri baru di snapshot (Shard Id watchlist-only, NEURA + JOLT + 0x92b379d3 checked-not-lead, MarsNexus excluded).")
snap["timestamp_wib"] = "2026-11-09 18:5x WIB"
json.dump(snap, open(f"{BASE}/onchain-snapshot.json", "w"), indent=1)
summary = {"contracts_updated": n_upd, "track_c_updated": n_tc, "block": BLOCK,
           "interval_minutes": INTERVAL,
           "new_entries": ["Shard Id", "NEURA", "JOLT", "MarsNexus", "0x92b379d3807F68aD2bCfd013D831713D8C6dbdFB"],
           "new_track_c": [],
           "status_changes": {}}
json.dump(summary, open(f"{BASE}/run-2026-11-09-1831-merge.json", "w"), indent=1)
print("MERGE DONE", summary)
