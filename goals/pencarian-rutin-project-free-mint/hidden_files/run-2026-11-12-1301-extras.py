#!/usr/bin/env python3
"""Run 1301 extras (after merge): add AIRDROP + Oliver Agents to snapshot,
remove age-excluded Meow Cards, finalize last_run_note + final.json decision.
No preview/mint. Snapshot already backed up by merge (.bak-1301)."""
import json

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
snap_path = BASE + "onchain-snapshot.json"
snap = json.load(open(snap_path))

# --- 1. AIRDROP (0x417d): strong lead, gate-blocked, ALREADY reported by hot-leg 13:21 ---
snap["contracts"]["Airdrop"] = {
    "address": "0x417d04C0a323fC89cDBbEf4D361161fCfA45baF9",
    "name": "Airdrop", "symbol": "AIRDROP", "kind": "ERC721",
    "status": "strong-lead-gate-blocked-2026-11-12",
    "FREE_CAP": 77, "freeMinted": 69, "totalMinted": 69, "MAX_SUPPLY": 7777,
    "MAX_PER_WALLET": 5, "mintOpen": 1,
    "mintOpensAt": 1794463075,
    "price": 1400000000000000,
    "freeClaimed_user": 0, "balanceOf_user": 0, "holdsAgentId_user": 1,
    "mintsBy_user": 0,
    "agentIdRegistry": "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F",
    "owner": "0x133ca80daa98c254b067a693f69b5b3d3f4202db",
    "firstSeenWib": "2026-11-12 13:01 WIB",
    "launchNote": "Umur TERVERIFIKASI <24 jam: mintOpensAt on-chain 1794463075 = 2026-11-12 12:57:55 WIB; first mints 4 terverifikasi run ini blok 133109353 (~13:05 WIB). Sourcify exact_match, verifiedAt 2026-11-12T05:58:11Z.",
    "baselineNote": "EARLY shape terdeteksi run ini (feed Sourcify baru, S1+early_shape): agent-shaped (agentIdRegistry = registry persis, freeMinted/freeClaimed, FREE_CAP 77, mint payable, rewardPool). Free 4/77 = 5,2% saat baca pertama run ini (~13:05 WIB, blok 133109353). X discussion UNVERIFIED run ini (0 hits pencarian alamat; nama generik 'Airdrop'). Website UNVERIFIED (metode A/N: pencarian alamat 0 hasil; H: tanpa contractURI; I: tokenURI(1)='1' tanpa URL; G: nama generik tanpa linkage; Sourcify tanpa URL). Slot user TERBUKA (freeClaimed(user)=0, holdsAgentId(user)=1, balanceOf(user)=0).",
    "runNote1301": "Run 1301: baca pertama 4/77 (blok 133109353); hot-leg 1304/1309 mempromosikan ke STRONG LEAD (60/77 = 77,9% blok ~133111200) dan MELAPORKAN SEKALI sebagai strong-lead-gate-blocked 13:21:29 WIB (hot-leg-reported.json) - main job TIDAK melaporkan ulang (dedupe lintas job). Baca ulang run ini 69/77 = 89,6% (blok 133111612, ~13:23 WIB), slot user TETAP terbuka; sellout segera - hot-leg own the sellout watch. TIDAK di-preview/di-mint (gate website gagal = scope block).",
    "lastReadBlock": 133111612,
    "lastReadWib": "2026-11-12 13:23 WIB",
    "velocityVerified": False,
    "xVerified": False,
    "websiteVerified": False,
}

# --- 2. Oliver Agents: watchlist-only (age unverified), website + X verified ---
snap["contracts"]["Oliver Agents"] = {
    "address": "0xad86e4d52e55709d1bda08f922853d4b109e0810",
    "name": "Oliver Agents", "symbol": "OLIVER", "kind": "ERC721",
    "status": "watchlist-only-age-unverified-2026-11-12",
    "FREE_MAX": 1000, "freeMinted": 649, "freeRemaining": 351,
    "totalSupply": 649, "mintedCount": 649, "paidMinted": 0,
    "MAX_SUPPLY": 5000, "PAID_MAX": 4000, "PAID_PRICE": 1000000000000000,
    "mintPrice": 1000000000000000, "mintOpen": 1,
    "balanceOf_user": 0,
    "agentIdRegistry": "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F",
    "owner": "0xbc8f04b7fd68bbe4c2c298a63d20da0962879ced",
    "firstSeenWib": "2026-11-12 13:01 WIB",
    "website": "https://oliveragents.pages.dev/",
    "websiteVerified": True,
    "websiteNote": "Gate website LOLOS run ini: https://oliveragents.pages.dev/ HTTP 200 (43.618 byte) mencetak kontrak persis 0xAD86e4D52E55709D1bda08f922853D4b109e0810 x3 (termasuk link BscScan); tokenURI(1) = https://oliveragents.pages.dev/meta/5.json (metode I). Judul 'OLIVER AGENTS - Merge. Battle. Mine.'; deskripsi: 5.000 battle agents, 1.000 free claims, sisanya 0,001 BNB.",
    "xVerified": True,
    "xNote": "Diskusi publik terverifikasi: post Boltbook vibibiy.ai 2026-11-12T06:03:11Z 'Oliver Agents (OLIVER): 630/1,000 free claimed - mintFree() passes from our Agent wallet, 370 left'.",
    "launchNote": "Umur UNVERIFIED: tidak ada stated launch time ditemukan; first-mint block tidak bisa ditarik (Ankr getLogs HTTP 401, outage sejak 9 Nov); Sourcify verifiedAt 2026-11-12T03:52:35Z = 10:52:35 WIB BUKAN launch time.",
    "baselineNote": "Ditemukan run ini via Boltbook front page EN+ZH (route 2). Agent-shaped: Sourcify exact_match; AGENT_ID_REGISTRY = registry persis; mintFree() + FREE_MAX/freeRemaining/freeClaimedByAgent; PAID_MAX 4000 @ 0,001 BNB. Free 649/1000 = 64,9% (blok 133110xxx, ~13:2x WIB) - di bawah ambang strong lead >70%; di atas 50% kandidat TAPI velocity belum ada baseline (baca pertama run ini) DAN umur unverified -> BUKAN kandidat, BUKAN strong lead. Slot user: balanceOf(user)=0 (freeClaimedByAgent belum dibaca - butuh agent token id). TIDAK di-preview/di-mint.",
    "velocityVerified": False,
    "velocityNote": "Run 1301: baca pertama totalSupply/freeMinted 649 - baseline disimpan, rasio belum terhitung -> velocity TIDAK lulus run ini.",
    "runNote1301": "Run 1301: freeMinted 649/1000 = 64,9% (freeRemaining 351), mintOpen 1, paidMinted 0; website + X terverifikasi; umur UNVERIFIED -> watchlist-only, tanpa laporan chat, tanpa eksekusi.",
    "lastReadBlock": 133110998,
    "lastReadWib": "2026-11-12 13:20 WIB",
    "previousTotalSupply": 649,
    "mintedInInterval": 0,
    "intervalMinutes": 30.0,
    "currentRatePerMin": 0.0,
    "previousRatePerMin": 0.0,
    "velocityLegPasses": False,
}

# --- 3. Meow Cards: AGE-EXCLUDED -> remove from active watchlist ---
meow = snap["contracts"].pop("Meow Cards", None)
meow_evidence = (
    "Run 1301 AGE-EXCLUSION (dilaporkan sekali): Meow Cards (MEOWC) 0xb8164afefc53910d7a74cece15a60a9e0c86089e - "
    "first mint terverifikasi 2026-11-09 02:14:09 WIB (blok 132446691); umur kini ~83 jam (>=24 jam) dan belum sold out "
    "(totalSupply 607/10.000, blok 133109986 run ini; burst +566 dari 41 terakhir dibaca 2026-11-11 01:01 WIB - fase mint yang sama, "
    "tanpa bukti phase/batch baru). Dihapus dari watchlist aktif (entry snapshot dihapus). Free% TETAP UNVERIFIED (tanpa free-pool counter). "
    "Website: meow-cards.pages.dev ada (Colony post 10 Nov + tokenURI metadata host) tapi fetch root tidak mencetak kontrak persis - moot karena umur gugur. "
    "X/diskusi terverifikasi hari ini (3 post Boltbook 13:03-13:04 WIB + Colony 10 Nov). Slot user terbuka (firstFreeUsed=0, balanceOf=0) - TETAP tidak bisa promosi/mint via jalur ini karena umur gugur. "
    "Status sebelumnya: early-lead-2026-11-09 (dilaporkan sekali 9 Nov oleh job backfill)."
)
if isinstance(snap.get("age_exclusions"), list):
    snap["age_exclusions"].append(meow_evidence)
elif isinstance(snap.get("age_exclusions"), dict):
    snap["age_exclusions"]["runNote1301_meow"] = meow_evidence
else:
    snap["age_exclusions_note1301_meow"] = meow_evidence
snap["runNote1301_age_exclusions"] = meow_evidence

# --- 4. Finalize run note + decision ---
snap["last_run_note"] = (
    "Run 1301: pre-flight FAIL (Ankr HTTP 401, outage sejak 9 Nov) - scan fast-fail, watermark tidak dimajukan; 5c dilewati. "
    "Legs: feed 20 (verified 05:52:54-06:01:13Z), 5 baru vs hot-leg-seen, Boltbook EN 45.210 byte/9 alamat + ZH 43.702 byte/10 alamat, 1 baru Boltbook (0xa161 = tx hash Meow, bukan kontrak - Sourcify match null). "
    "Shape: 1 S1+early (Airdrop 0x417d - dipromosikan hot-leg ke strong-lead-gate-blocked, dilaporkan hot-leg 13:21, main job TIDAK lapor ulang). "
    "Verify2 blok 133110279; reread blok 133110653 (63 kontrak + 21 track_c, delta maks +5, tanpa promosi); tc-age blok 133110998 (CLEPSYDRA + MoonAgent + WNO tetap age-excluded). "
    "Sweep EN+ZH: 0 baru (NAOMI/AgenticGangster sold out, WUMPO excluded, Agent Zet free phase complete, AGENT COSMOS sudah di snapshot). "
    "MEOWC AGE-EXCLUDED (dihapus dari snapshot, dilaporkan sekali). Oliver Agents ditambah watchlist-only (64,9%, website+X terverifikasi, umur unverified). "
    "Stampooor pages.dev 200 tapi kontrak sale tidak tercetak - gate tetap gagal (moot: age-excluded + minted-by-user). "
    "Keputusan: LAPOR SEKALI age-exclusion Meow Cards; selebihnya SILENT. Detail di run-2026-11-12-1301-runlog.md."
)
final = json.load(open(BASE + "run-2026-11-12-1301-final.json"))
final["decision"] = "REPORT-ONCE-MEOW-AGE-EXCLUSION"
final["extras"] = {
    "airdrop_added": "strong-lead-gate-blocked (reported by hot-leg 13:21, no re-report)",
    "oliver_added": "watchlist-only-age-unverified",
    "meow_removed": "age-excluded (~83h), reported once",
}
json.dump(final, open(BASE + "run-2026-11-12-1301-final.json", "w"), indent=1)
json.dump(snap, open(snap_path, "w"), indent=1)
print(json.dumps({"meow_removed": bool(meow), "contracts_now": len(snap["contracts"]),
                  "decision": final["decision"]}, indent=1))
