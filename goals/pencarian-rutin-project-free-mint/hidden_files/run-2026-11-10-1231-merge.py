#!/usr/bin/env python3
"""Merge run 1231 reread+vel into snapshot. Read-only wrt chain; writes snapshot + backup.
Main event: DRIFTWIRE strong-lead direct mint (token #745, tx verified).
Adds Moss Transmission + Neon Circuit watchlist-only; RIGBYPASS excluded sold-out.
Does NOT re-report anything (reporting is the parent run's final message)."""
import json, shutil
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TS = "2026-11-10-1231"
BLOCK = 132721079
NOW = "2026-11-10 12:31 WIB"
snap = json.load(open(f"{BASE}/onchain-snapshot.json"))
rr = json.load(open(f"{BASE}/run-{TS}-reread.json"))
vel = json.load(open(f"{BASE}/run-{TS}-vel.json"))
shutil.copy(f"{BASE}/onchain-snapshot.json", f"{BASE}/onchain-snapshot.json.bak-1231-premerge")

updated = 0
for name, entry in snap.get("contracts", {}).items():
    if not isinstance(entry, dict):
        continue
    f = rr.get("reread", {}).get(name)
    if not f:
        continue
    row = vel.get("rows", {}).get(name, {})
    for k in ("totalSupply", "totalMinted", "freeClaimed", "freeMinted", "FREE_SUPPLY",
              "MAX_SUPPLY", "mintOpen", "balanceOf_user", "freeClaimed_user"):
        if f.get(k) is not None:
            entry[k] = f[k]
    entry["lastReadBlock"] = BLOCK
    entry["lastReadWib"] = NOW
    if row.get("minted") is not None:
        entry["previousTotalSupply"] = row.get("prev")
        entry["mintedInInterval"] = row.get("minted")
        entry["intervalMinutes"] = 60.0
        entry["currentRatePerMin"] = row.get("rate")
        entry["velocityRatio"] = row.get("ratio")
        entry["velocityLegPasses"] = row.get("passes")
    updated += 1

def note(name, text):
    e = snap["contracts"].get(name)
    if isinstance(e, dict):
        e["runNote1231_1110"] = text

note("SEVENFOLD", "Run 1231 (blok 132721079): totalSupply 1528->1579 (+51, rate 0,85/mnt vs prev 0,95 = 0,89x) velocity GAGAL; freeMinted 1578/3000 = 52,6% (LEWAT 50% tapi velocity gagal -> BUKAN kandidat). CATATAN: klaim Boltbook hi5.ai 'freeMinted 418' TIDAK cocok dengan 2x bacaan langsung run 1201 (1527) + run 1231 (1578) — angka 418 ditolak, freeMinted ~1578 dipakai. Audit MORROW RISK tetap blokir; status strong-lead-reported-2026-11-10-audit-blocked dipertahankan, TIDAK dilaporkan ulang.")
note("Sakura", "Run 1231: totalSupply 1326->1345 (+19, 0,317/mnt, 2,11x) velocity GAGAL (butuh >=20 token, hanya 19); freeMinted 1335/6000 = 22,25% (<25% strong-lead). Tetap early-lead watchlist-only; umur terverifikasi <=48 jam (first mint 01:47 WIB 10 Nov, deadline 2026-11-12 01:47 WIB); website unverified.")
note("THYRK", "Run 1231: totalSupply 2829->3143 (+314, rate 5,23/mnt vs prev 1,75 = 2,99x) velocity LOLOS; freeMinted 3084; bal_user=1 (sudah mint user 08:22 WIB). Velocity lolos tapi slot user terpakai -> TIDAK ada aksi, bukan kandidat.")
note("Sidecoo", "Run 1231: totalSupply 21206->21244 (+38) velocity LOLOS lagi — tapi free% UNVERIFIED (free views null, MAX_SUPPLY tak terbatas) + umur/website/X UNVERIFIED -> TIDAK ada promosi, tetap watchlist-only.")
note("FCAT Agents", "Run 1231: totalSupply 421->435 (+14, 1,99x) velocity GAGAL (<20 token); freeClaimed 432/888 = 48,6%; umur UNVERIFIED, website null -> watchlist-only.")
note("JINCHAN Agents", "Run 1231: totalSupply 242->245 (+3) velocity GAGAL; freeClaimed 242/888 = 27,2%; umur UNVERIFIED -> watchlist-only.")
note("Roguefall", "Run 1231: totalSupply 1136->1144 (+8) velocity GAGAL; freeMinted 1138; umur+website UNVERIFIED -> watchlist-only.")
note("Rose Genesis", "Run 1231: totalSupply 1049->1050 (Boltbook bangwi.ai: 1.050/3.333, 61 slot free phase-1 tersisa); free% UNVERIFIED (free views null); umur UNVERIFIED -> tetap watchlist-only-mature-newly-noticed, bukan strong lead/kandidat.")
note("Aura Agents", "Run 1231: totalSupply 5069->5134 (+65) velocity GAGAL; free views None; umur+website UNVERIFIED -> watchlist-only, tanpa promosi.")
note("Ore Raiders", "Run 1231: totalSupply 2.286/10.000, freeMinted 2.276/6.000 = 37,9% (Boltbook belski.ai day-3); umur UNVERIFIED (day-3, belum ada stated launch) -> tetap watchlist-only (status checked-2026-11-05 dipertahankan).")
note("Lion's Share", "Run 1231: totalSupply 784/1.450, pace +1/jam (Boltbook janglex.ai recheck #61) -> watchlist-only, tanpa perubahan.")

# track_c updates
tc_updated = 0
for k, v in snap.get("track_c", {}).items():
    if not isinstance(v, dict):
        continue
    f = rr.get("track_c", {}).get(k)
    if not f:
        continue
    for key in ("totalSupply", "freeMinted", "freeSharesRemaining", "balanceOf_user", "freeClaimed_user"):
        if f.get(key) is not None:
            v[key] = f[key]
    v["lastReadBlock"] = BLOCK
    v["lastReadWib"] = NOW
    tc_updated += 1

nusa = snap["track_c"].get("NUSA")
if isinstance(nusa, dict):
    nusa["runNote1231"] = ("Run 1231: freeMinted TETAP 365/560 (0 klaim ~60 mnt, Boltbook masbboyy.ai cocok); "
        "freeClaimed(user)=0; gate website TETAP FAILED. Umur: first mint 2026-11-08 17:05 WIB -> deadline 48 jam 2026-11-10 17:05 WIB "
        "(kurang ~4,5 jam dari run ini). TIDAK preview/mint, TIDAK dilaporkan ulang; bila gate tetap gagal sampai deadline -> age-exclude + lapor sekali.")
bome = snap["track_c"].get("BOME-50CD")
if isinstance(bome, dict):
    bome["runNote1231"] = ("Run 1231: totalSupply tidak berubah; mintOpen=0 (sale BELUM dibuka; Boltbook run 1201: buka 14:00 WIB hari ini — "
        "sudah lewat dari run ini tapi mintOpen tetap 0). Tetap watchlist-only-not-open; TIDAK preview/mint.")

# binanceai (track-B pending, refund/failed) — fresh read this run
snap["runNote1231_binanceai"] = ("Run 1231: binanceai TETAP fase refund/failed (launched=0, failed=1, isRefundPhase=1, totalShares 3110, "
    "tokenClaimed_user=0). SUDAH dilaporkan run 1701 2026-11-07 - TIDAK dilaporkan ulang.")

# bridge diff (complementary leg)
try:
    bridge = json.load(open(f"{BASE}/scan-bridge.json"))
    bcontracts = bridge.get("contracts", {}) if isinstance(bridge, dict) else {}
    snap_addrs = {str(v.get("address", "")).lower() for v in snap.get("contracts", {}).values() if isinstance(v, dict)}
    new_bridge = [a for a in bcontracts if a.lower() not in snap_addrs]
    discarded_bridge = [a for a, v in bcontracts.items() if isinstance(v, dict) and v.get("same_owner_discarded")]
    snap["runNote1231_bridge"] = (f"Run 1231 bridge: {len(bcontracts)} kontrak, {len(new_bridge)} belum di snapshot "
        f"({new_bridge[:5]}), {len(discarded_bridge)} same_owner_discarded; 0 promosi (tidak ada yang memenuhi tier). "
        "RIGBYPASS/Moss/Neon/Driftwire bukan dari bridge (dari Boltbook run ini).")
except Exception as e:
    snap["runNote1231_bridge"] = f"Run 1231 bridge: baca gagal ({e}); lanjut normal, bridge tidak menggagalkan run."

# new entries
snap["contracts"]["DRIFTWIRE"] = {
    "address": "0x485be9daa4620fcee4e2baed7cc85ea57acb44b0",
    "status": "minted-by-user-2026-11-10",
    "name": "DRIFTWIRE", "symbol": "DRIFT", "kind": "ERC721",
    "totalSupply": 745, "MAX_SUPPLY": 5555, "mintOpen": 1,
    "AGENT_FREE_CAP": 2000, "X_FREE_CAP": 200, "agentFreeUsed": 745,
    "freeLeft": [1255, 200], "freePctVerified": 36.9,
    "PRICE": 1500000000000000, "paidMinted": 0,
    "balanceOf_user": 1, "freeUsedByWallet_user": 1,
    "mintTx": "0xba820f5101ec5a21e7b0d8b41d9df2f52e9b0590b4a5981ba7083ce68f721100",
    "mintBlock": 132723038, "mintGas": 247824, "mintTokenId": 745,
    "mintOrderId": "26111000002030897090",
    "mintTimeWib": "2026-11-10 12:48:21 WIB",
    "mintStartWib": "2026-11-10 09:37:15 WIB", "mintEndWib": "2026-11-17 09:37:15 WIB",
    "owner": None, "payee": "0xe0fecb4a720d8f39531b3bc3f0ebb865e10be191",
    "ownerInDiscards": False, "payeeInDiscards": False,
    "token": "0x07683f749e1e6dda9059456109c2d161ce3c0f41",
    "market": "0x5FEF88E9E7eb0899f3F70EF16d50A08E0fd8bd09",
    "website": "https://driftwire.pages.dev",
    "lastReadBlock": 132723038, "lastReadWib": "2026-11-10 12:48 WIB",
    "source": "Boltbook front page EN+ZH run 1231 (post rizeiki.ai 'Driftwire #141', 12:2x WIB) + verifikasi on-chain run ini",
    "launchNote": "UMUR TERVERIFIKASI <=48 jam: mintStart() on-chain = 2026-11-10 09:37:15 WIB (umur ~3 jam saat mint); deadline 48 jam 2026-11-12 09:37 WIB. Sourcify verifiedAt 2026-11-10T02:38:12Z (bukan launch time, hanya verifikasi).",
    "websiteNote": "GATE website LOLOS (methods H/I/G): contractURI + tokenURI -> driftwire.pages.dev; /llms.txt situs mencetak kontrak NFT persis 0x485be9daA4620FcEE4e2bAEd7cc85Ea57Acb44b0 + market 0x5FEF88E9E7eb0899f3F70EF16d50A08E0fd8bd09; config.js situs mencetak nft+market+registry persis + supply/harga/cap cocok dengan on-chain. X: opsional, tidak dicari sebagai gate.",
    "auditNote": "Audit Binance run 1231: NFT hasResult=false (TIDAK ADA HASIL, bukan pass; code 000000, isSupported true, riskAlert null, 0 hit); token WIRE riskLevel 3 MID, 0 hit RISK (2 CAUTION: Contract Code Not Verified, Newly Created Token), riskAlert null, buy/sell tax 0.0.",
    "previewNote": "Preview bersih 000000000 (requestId 00c349fa3bb44cf0a95f6ba4a711f1cc): mint(1) value 0, balance +1 ERC-721 tokenId 745, tanpa allowance/authority changes, tanpa risk hits; requireConfirmation false.",
    "baselineNote": "STRONG LEAD -> DIRECT MINT run 1231 (otorisasi user 2026-11-02): umur terverifikasi <=48 jam + free 737/2000 = 36,9% TERVERIFIKASI (agentFreeUsed/AGENT_FREE_CAP) + slot user terbuka (freeUsedByWallet=0, balanceOf=0) + website TERVERIFIKASI + audit diungkap + preview bersih. Velocity TIDAK dibutuhkan untuk strong lead (baseline pertama).",
    "mintNote1231": "MINT SUKSES run 1231: NFT #745 ke agent wallet, gratis (gas saja), tx 0xba820f5101ec5a21e7b0d8b41d9df2f52e9b0590b4a5981ba7083ce68f721100, blok 132723038, receipt status 1, gas 247824. Verifikasi pasca: ownerOf(745)=agent wallet, balanceOf=1, freeUsedByWallet=1, agentFreeUsed 737->745 (8 mint lain di menit yang sama), totalSupply 745, claimable(user)=10.000 WIRE.",
    "wireClaimNote": "KLAIM WIRE: claimable(user)=10.000 WIRE pasca-mint (claimRewards()), TAPI TIDAK di-auto-claim: token WIRE BELUM ADA pair (kutipan Boltbook: no liquidity) -> LP hook TIDAK jelas -> BUKAN kandidat track-B. Pantau pair; klaim hanya bila pair terverifikasi + guard lolos.",
    "rarityNote": "Rarity #745: Tier 'Neon Ronin' (nama tier asli proyek, bukan Common-Legendary), Courier 'Last Shogun', Rank 3. Tercatat di nft-rarity-inventory.md run 1231.",
    "marketNote": "Market proyek sendiri: Night Market 0x5FEF88E9E7eb0899f3F70EF16d50A08E0fd8bd09 (Sourcify exact_match, fee 3% / FEE_BPS 300) ADA tapi listedCount=0, volume=0 -> TIDAK ADA listing live -> BUKAN venue live -> #745 TIDAK di-auto-list (aturan post-mint auto-list: tanpa floor live, tidak listing).",
    "velocityVerified": False, "xVerified": False,
}
snap["contracts"]["Moss Transmission"] = {
    "address": "0xec51eed38cee346c2a6b22dd1310f0e278df5994",
    "status": "watchlist-only-age-free-website-unverified-2026-11-10",
    "name": "Moss Transmission", "symbol": "BO03", "kind": "ERC721",
    "totalSupply": 207, "MAX_SUPPLY": 883, "mintOpen": 1,
    "freeClaimed": None, "freeMinted": None, "FREE_SUPPLY": None,
    "balanceOf_user": 0, "price": 50000000000000,
    "owner": "0x3fbe2b54baf80d33e2ef6e46cb972959536eca17", "ownerInDiscards": False,
    "lastReadBlock": 132721477, "lastReadWib": "2026-11-10 12:3x WIB",
    "source": "Boltbook front page EN+ZH run 1231 (post raca.ai ZH + drzein.ai, 12:25 WIB) + verifikasi on-chain run ini",
    "launchNote": ("UMUR UNVERIFIED: Sourcify verifiedAt 2026-11-10T02:08:28Z (09:08 WIB) BUKAN launch time; "
        "tidak ada stated launch time proyek; first-mint on-chain TERBLOKIR (Ankr 401 + dataseed eth_getLogs -32005). "
        "Pertama terlihat Boltbook ~12:25 WIB 10 Nov (totalSupply 195 saat itu)."),
    "websiteNote": ("GATE website BELUM DINILAI PENUH: contractURI() tidak ada di ABI; tokenURI(1) -> mosstransmission.pages.dev/meta/1.json "
        "tapi fetch meta GAGAL (curl tanpa respons); pencarian web 'Moss Transmission' belum dilakukan run ini (bukan lead). "
        "Bila umur terverifikasi + free% terverifikasi, gate wajib dinilai penuh sebelum promosi apa pun."),
    "baselineNote": ("BARU run 1231: agent-shaped terverifikasi (Sourcify exact_match; mintWithAgentTokenId + agentIds + mintedByAgent); "
        "totalSupply 207/883 = 23,4% total (BUKAN free% — free views revert, free% UNVERIFIED, tidak boleh diganti % total supply); "
        "price 0,00005 BNB (jalur berbayar) + klaim Boltbook 'mint(1) verified at 0 BNB' (first free); slot user: balanceOf=0, mintedBy(user)=0. "
        "BUKAN early lead (first mint bukan di run ini), BUKAN strong lead (umur+free% unverified). Watchlist-only; promosi hanya bila umur terverifikasi "
        "<=48 jam + free% terverifikasi >=25% + website terverifikasi. TIDAK pernah preview/mint."),
    "ownerGroupNote": "Owner 0x3fbe...ca17 SAMA dengan Neon Circuit (CY02, baru run ini) — grup deployer 2 proyek sejauh ini, bukan discards.",
    "velocityVerified": False, "xVerified": False,
}
snap["contracts"]["Neon Circuit"] = {
    "address": "0xfe0f456fb78efbde4427b81b025b6838321156ab",
    "status": "watchlist-only-age-free-unverified-2026-11-10",
    "name": "Neon Circuit", "symbol": "CY02", "kind": "ERC721",
    "totalSupply": 367, "MAX_SUPPLY": 819, "mintOpen": 1,
    "freeClaimed": None, "freeMinted": None, "FREE_SUPPLY": None,
    "balanceOf_user": 0, "price": 69000000000000,
    "owner": "0x3fbe2b54baf80d33e2ef6e46cb972959536eca17", "ownerInDiscards": False,
    "lastReadBlock": 132721477, "lastReadWib": "2026-11-10 12:4x WIB",
    "source": "Boltbook front page ZH run 1231 (post mamun21k.ai 'Neon Circuit (CY02): recheck 360/819', ~12:24 WIB) + verifikasi on-chain run ini",
    "launchNote": ("UMUR UNVERIFIED: Sourcify verifiedAt 2026-11-10T02:06:47Z (09:06 WIB) BUKAN launch time; "
        "tidak ada stated launch time proyek; first-mint on-chain TERBLOKIR (Ankr 401). "
        "Pertama terlihat Boltbook ~10:00 WIB 10 Nov (totalSupply 318 saat itu, lokie)."),
    "websiteNote": "GATE website BELUM DINILAI (bukan lead; umur+free% unverified). tokenURI() ada di ABI — cek external_url bila promosi mendekat.",
    "baselineNote": ("BARU run 1231: agent-shaped terverifikasi (Sourcify exact_match; template sama dengan Moss: mintWithAgentTokenId + agentIds + mintedByAgent); "
        "totalSupply 367/819 = 44,8% total (BUKAN free% — freeMinted/paidMinted revert, free% UNVERIFIED, cocok dengan caveat mamun21k.ai); "
        "price 0,000069 BNB; pace ~0,6/mnt steady (Boltbook); slot user: balanceOf=0. "
        "BUKAN early lead (first mint bukan di run ini), BUKAN strong lead. Watchlist-only. TIDAK pernah preview/mint."),
    "ownerGroupNote": "Owner 0x3fbe...ca17 SAMA dengan Moss Transmission (BO03, baru run ini) — grup deployer 2 proyek sejauh ini, bukan discards.",
    "velocityVerified": False, "xVerified": False,
}

# RIGBYPASS -> excluded (sold out, verified on-chain this run)
ex = snap.setdefault("excluded", {})
ex["RIGBYPASS"] = {
    "address": "0xe657465f0eb4b55877246026bfae4ec75ef2e160",
    "reason": "sold-out-2026-11-10",
    "note": ("Run 1231: freeMinted 1111/1111 (free lane HABIS, dikonfirmasi Boltbook ferrr.ai + jaykojay.ai ~12:16-12:35 WIB + baca on-chain run ini); "
        "totalMinted 1112 (1 paid); MAX_SUPPLY 8888; Sourcify UNVERIFIED; bal_user=0. Tidak pernah dilaporkan sebagai lead (sold out sebelum sempat dipromosikan). "
        "Postingan ghostagent.ai '?/8.888, 8.888 left' adalah bacaan MAX_SUPPLY yang salah kaprah — free cap 1.111 yang benar."),
    "excludedWib": "2026-11-10 12:31 WIB",
}

# run-level notes
snap["runNote1231_1110"] = ("Run 1231 (2026-11-10 12:31 WIB, blok 132721079, interval 60 mnt vs run 1201): re-read 645 kontrak + 75 track_c (629,8 dtk). "
    "Velocity LOLOS: ['Sidecoo', 'THYRK'] — tanpa promosi (Sidecoo free% unverified; THYRK slot user terpakai). "
    "MINT: DRIFTWIRE #745 (strong-lead direct mint, tx 0xba820f5101ec5a21e7b0d8b41d9df2f52e9b0590b4a5981ba7083ce68f721100, blok 132723038, gas 247824). "
    "BARU watchlist-only: Moss Transmission + Neon Circuit (umur+free% unverified). RIGBYPASS excluded sold-out. "
    "Feed Sourcify 20/20 dicek, 0 S1/0 S2. Boltbook EN 45.958 B / ZH 46.154 B. Ankr 401 fast-fail (preflight 5,1 dtk, head 132721035); watermark tetap 132512564; gap ~208.471 blok. "
    "Scan leg GAGAL CEPAT; 5c: tanpa output scan baru -> 0 dicek run ini. Sweep web: 0 proyek baru (hasil lama Okt). Square/Odaily/PANews 0 baru (via sweep). "
    "Kandidat baru 0; strong lead baru 1 (DRIFTWIRE, sudah di-mint); early lead baru 0; track-C lead/kandidat baru 0; sellout baru 1 (RIGBYPASS, sudah excluded).")
snap["runNote1231_1110_scan"] = ("Run 1231 scan: PRE-FLIGHT GAGAL (Ankr 401 Unauthorized, 5,1 dtk, head 132721035) — outage Ankr sejak 2026-11-09 ~13:33 WIB BERLANJUT. "
    "Scan leg FAST-FAIL per amandemen 2026-11-06; watermark TETAP 132512564; gap ke head ~208.471 blok (backfill OFF atas perintah user).")
snap["runNote1231_1110_discovery"] = ("Run 1231 discovery (routes 2/3/5a/6): Boltbook EN+ZH front page — DRIFTWIRE (strong lead -> mint), Moss Transmission + Neon Circuit (watchlist-only), "
    "RIGBYPASS (sold out -> excluded), THYRK/NUSA/SEVENFOLD/Ore Raiders/Lion's Share/Rose Genesis (sudah di snapshot, tanpa promosi). "
    "ACORE vs GOLD (post zanbryan.ai): alamat kontrak TERPOTONG di postingan (0xf4bacf30... / 0x1de1a2bc...) -> tidak bisa diverifikasi run ini, log saja; "
    "komentar beautyhaven.ai: deployer 0x1103 family sudah di-flag sebelumnya (AGENT CORE/Blox owner-withdraw risk) — dicatat sebagai peringatan, bukan vonis. "
    "BITCAT sale+token muncul di front page tapi SUDAH di-mint user 12:30 WIB (user-named) -> bukan temuan baru. "
    "Sourcify feed 20 -> 0 S1/0 S2. Sweep web: 0 baru (BLOB Miner/AgentForge/Pixel Fox/Hundred/PocketDragons/AgentGoldMiner/Cilok Cats — semua lama/ter-exclude). "
    "twitterapi.io tidak pernah dipanggil.")
snap["runNote1231_1110_5c"] = ("Run 1231 5c: scan leg fast-fail (Ankr 401) -> TIDAK ADA output scan baru -> 0 ERC-20 baru dicek run ini (bukan 0 hasil shape-check; "
    "tidak ada backlog baru). track-c-scan-checked.json tidak berubah.")
snap["runNote1231_1110_age_exclusions"] = ("Run 1231 age-exclusion sweep: TIDAK ADA exclusion baru. Deadline terdekat: NUSA 2026-11-10 17:05 WIB (~4,5 jam lagi, gate tetap FAILED); "
    "SEVENFOLD deadline 2026-11-12 07:33 WIB; Sakura deadline 2026-11-12 01:47 WIB; DRIFTWIRE deadline 2026-11-12 09:37 WIB (sudah minted). "
    "Rose Genesis umur UNVERIFIED -> tidak di-exclude (exclusion butuh umur TERVERIFIKASI >48 jam).")
snap["last_run_wib"] = NOW
snap["last_run_block"] = BLOCK
json.dump(snap, open(f"{BASE}/onchain-snapshot.json", "w"), indent=1)
print(f"MERGE DONE: contracts updated={updated} track_c updated={tc_updated} total contracts={len(snap['contracts'])} track_c={len(snap.get('track_c',{}))} excluded={len(snap.get('excluded',{}))}")
