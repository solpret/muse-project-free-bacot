#!/usr/bin/env python3
"""Merge for free-mint-search run 2026-11-13 08:01 WIB.
Applies fresh reads (verify block 133263835, triage block 133264690),
discovery (Sourcify feed + Boltbook), pre-flight (Ankr 401 fast-fail),
bridge (116 contracts, 0 new), and the 0701 checkpoint's pending merge
(JNTM/OBFG/AgentMuse track_c; PX24-group watchlist; LuckyCatch already gone).
Writes onchain-snapshot.json (backup already taken). No preview/mint.
"""
import json, datetime
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
NOW = "2026-11-13 ~08:38 WIB"
s = json.load(open(BASE + "onchain-snapshot.json"))
C = s.setdefault("contracts", {})
T = s.setdefault("track_c", {})
EX = s.setdefault("excluded", {})

def mv_excluded(section, key, status, note):
    src = C if section == "contracts" else T
    if key in src:
        v = src.pop(key)
        v["status"] = status
        v["excludedNote0801"] = note
        EX[key] = v
        return True
    return False

# --- 1. Agentx: candidate legs PASS, website gate FAILED -> report once ---
ax = C["Agentx"]
ax.update({
    "totalMinted": 628, "freeMinted": 628,
    "freePct": 56.5,
    "freePctNote": "628/1111 FREE_CAP (verified on-chain run 0801, block 133263835)",
    "status": "candidate-gate-blocked-2026-11-13",
    "lastReadBlock": 133263835, "lastReadWib": NOW,
    "velocityLegPasses": True,
    "velocityNote": "Run 0801: 526 (hot-leg 0744) -> 628 (+102 in ~35 mnt = 2.91/mnt) vs prev interval 522 (0701) -> 526 (+4 in ~45 mnt = 0.089/mnt) = ~32.7x >= 1.5x DAN +102 >= 20 token -> velocity LOLOS. (Juga vs snapshot stored rate 0.195/mnt: 0.76/mnt = 3.9x.)",
    "previousRatePerMin": 0.089, "currentRatePerMin": 2.91,
    "previousTotalSupply": 526, "mintedInInterval": 102,
    "intervalMinutes": 35.0, "velocityRatio": 32.7,
    "gate": "website_failed",
    "gateNote": "GATE GAGAL run 0801 (fresh re-check): (A) contract-address search 0 project hits (hanya AgentX InferenceX/YouTube/Codenotary/arXiv/IETF yang tidak terkait); (D) re-fetch agentx.fun 31104 byte / agentx.pages.dev 9919 byte / agentx.vercel.app 7923 byte - semua HIDUP tapi TIDAK SATU PUN mencetak kontrak 0x64a5... (same-name pages, bukan bukti); (B)(C)(E)(G)(H)(I)(J)(K)(M) sudah dicoba run 0101, tanpa situs; (L) BscScan token page via live browser BELUM dicoba (2 delegasi sebelumnya tutup tanpa hasil; recheck track). X unverified (opsional, tidak meng-gate). Dilaporkan sekali run 0801 sebagai kandidat gate-blocked; TIDAK di-preview/TIDAK di-mint.",
    "runNote0801": "Run 0801 (blok 133263835): free 628/1111 = 56.5% (>=50%), umur TERVERIFIKASI 9,6 jam (mintOpensAt 23:11:05 WIB 12 Nov), velocity LOLOS, diskusi Boltbook terverifikasi, slot user TERBUKA - SEMUA kaki kandidat LOLOS kecuali website gate (GAGAL). Dilaporkan sekali sebagai kandidat gate-blocked; TIDAK di-preview/TIDAK di-mint.",
})

# --- 2. Zero (0x89B3): NEW EARLY LEAD, reported once run 0801 ---
C["Zero"] = {
    "address": "0x89B340435e4fD27e00442f7F1b3a3b3244b4E647",
    "name": "Zero", "symbol": "ZERO", "kind": "ERC721",
    "status": "early-lead-reported-2026-11-13",
    "totalMinted": 117, "freeMinted": 117, "FREE_CAP": 500, "MAX_SUPPLY": 10000,
    "mintOpen": 1, "mintOpensAt": 1794531303, "mintOpensAtWib": "2026-11-13 07:55:03 WIB",
    "price": 5000000000000000, "MAX_PER_WALLET": 2,
    "agentIdRegistry": "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F",
    "freeClaimed_user": 0, "mintsBy_user": 0, "balanceOf_user": 0, "holdsAgentId_user": 1,
    "userSlotNote": "Slot TERBUKA: freeClaimed(user)=0, mintsBy(user)=0, balanceOf(user)=0, holdsAgentId(user)=1.",
    "firstSeenBlock": 133263835, "firstSeenWib": "2026-11-13 ~08:25 WIB",
    "sourcifyVerifiedAt": "2026-11-13T00:55:26Z",
    "ageVerified": True,
    "ageNote": "mintOpensAt on-chain 1794531303 = 07:55:03 WIB 13 Nov; umur ~30 mnt saat bacaan pertama (blok 133263835).",
    "freePct": 23.4, "freePctNote": "117/500 FREE_CAP (verified on-chain run 0801)",
    "velocityLegPasses": False,
    "velocityNote": "First read run 0801 (baseline): 117 minted. Velocity cannot pass yet (no previous rate).",
    "previousRatePerMin": 0.0, "currentRatePerMin": None,
    "discussion": None, "xVerified": False,
    "discussionNote": "Diskusi publik BELUM ditemukan run ini (tidak ada post Boltbook/web yang mengutip Zero 0x89B3).",
    "website": None, "gate": "website_unverified",
    "gateNote": "Website BELUM DITEMUKAN run 0801: (A) contract-address search 0 project hits (hanya Zero/ZERO token Solana + ZeroWayNFT yang tidak terkait); (I) tokenURI(1) = bare '1', tanpa URL; (H) tidak ada fungsi contractURI. Metode B-G/J/K/M belum dicoba (early lead - gate dicek penuh bila promosi).",
    "agentShapeNote": "Sourcify ABI 36 fns: mint(), price(), freeClaimed/freeMinted, agentIdRegistry(), holdsAgentId(), mintsBy(); agentIdRegistry() on-chain = registry resmi 0x60B926...22F.",
    "baselineNote": "EARLY lead dilaporkan sekali run 0801 (temuan feed Sourcify recently-verified 00:55:26Z; pertama terlihat job ini run ini). BUKAN kandidat (23,4% <50%), BUKAN strong lead (<70%), website UNVERIFIED -> TIDAK di-preview/TIDAK di-mint (early lead tidak pernah auto-mint/preview).",
    "lastReadBlock": 133264690, "lastReadWib": NOW,
}

# --- 3. JNTM -> track_c lead, reported once (blocked: gate L pending + quote NULL) ---
T["JNTM"] = {
    "sale": "0x13204B86c56e709a7E2D1e95ABBA3638a93FB84b",
    "token": "0xb03836B0eFF7a563881CBB8E0a424c6a3Fa0924C",
    "name": "JNTM / 鸡你太美", "kind": "S1 factory sale",
    "status": "lead-gate-pending-quote-unverified-2026-11-13",
    "saleShape": "S1 VERIFIED: mint + quote(address,uint256) + free views (freeClaimed/freeLeft) + registry()=0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F.",
    "tokenNote": "token() mengembalikan uint256 1006035981668221707099398194407624553432315105868 = hex 0xb03836b0eff7a563881cbb8e0a424c6a3fa0924c (bukan alamat langsung); alamat token 0xb03836B0eFF7a563881CBB8E0a424c6a3Fa0924C dikoroborasi feed hot-leg 0619 (verified 2026-11-12T23:20:39Z).",
    "freeClaimed": 306, "freeLeft": 694, "FREE_LOTS_CAP": 1000, "TOTAL_LOTS": 12500,
    "totalMinted": 311, "paidMinted": 5,
    "mintStart": 1794525192, "mintStartWib": "2026-11-13 06:13:12 WIB",
    "ageVerified": True,
    "ageNote": "mintStart on-chain 1794525192 = 06:13:12 WIB 13 Nov; umur ~2,6 jam saat bacaan run 0801.",
    "quote_user_1": None,
    "quoteNote": "quote(address,uint256) dengan (user,1) NULL run ini (juga NULL sejak run 0724) - gratis via quote BELUM terverifikasi; safety (c) TIDAK terpenuhi -> TIDAK di-preview/TIDAK di-mint.",
    "freeClaimedByAgent_user": 0, "mintedLots_user": 0,
    "userSlotNote": "Slot TERBUKA: freeClaimedByAgent(user)=0, mintedLots(user)=0.",
    "gate": "website_pending_L",
    "gateNote": "Gate PENDING metode (L): BscScan token page (token 0xb038... + sale 0x1320...) via live browser didelegasikan 2x (0701 task 7dcbc507 + 0744 re-delegasi) - keduanya TUTUP tanpa hasil yang bisa diambil; metode A,B,C,D,E,G,J,K,M sudah dicoba run 0701, gagal; H/I N/A. Gate BELUM LOLOS -> TIDAK di-preview/TIDAK di-mint.",
    "baselineNote": "TRACK-C LEAD dilaporkan sekali run 0801 (lead report + blocking reason: gate pending L + quote unverified). BUKAN strong lead (30,6% <70%), BUKAN kandidat track-A. Dilaporkan via hasil mint outcome: blocked -> lead report.",
    "lastReadBlock": 133263835, "lastReadWib": NOW,
}

# --- 4. OBFG -> track_c lead (gate-blocked, already reported) ---
T["OBFG"] = {
    "sale": "0x5314071bba19943f58347ba5dec423e5032a6818",
    "name": "Obsidian Forge", "kind": "S1 factory sale",
    "status": "lead-gate-blocked-2026-11-12",
    "totalSupply": 618, "totalMinted": 618, "freeMinted": 618, "FREE_SUPPLY": 1230,
    "saleStart": 1794488476, "saleStartWib": "2026-11-12 20:01:16 WIB",
    "saleOpen": 1, "freeAvailable_user": 1, "balanceOf_user": 0,
    "freePct": 50.2,
    "freePctNote": "618/1230 FREE_SUPPLY (verified on-chain run 0801, block 133263835) - melewati 50% run ini (600 di 0701, 602 di 0744); untuk track-C % hanya info, bukan gate.",
    "ageNote": "Sale dibuka 20:01:16 WIB 12 Nov (saleStart on-chain); umur ~12,6 jam <24 jam.",
    "userSlotNote": "Slot TERBUKA: freeAvailable(user)=1, balanceOf(user)=0.",
    "gate": "website_failed",
    "gateNote": "Gate GAGAL: tidak ada website terverifikasi ditemukan metode A-K/M/N (dilaporkan sekali 12 Nov ~20:xx WIB sebagai track-C lead gate-blocked). TIDAK di-preview/TIDAK di-mint.",
    "baselineNote": "TRACK-C LEAD gate-blocked, SUDAH dilaporkan 12 Nov. Run 0801: 618/1230 = 50,2% (naik dari 600), slot terbuka, umur <24 jam - TANPA perubahan reportable, DIAM.",
    "lastReadBlock": 133263835, "lastReadWib": NOW,
}

# --- 5b. NOTV -> track_c watchlist-only-not-open (opens 18:00 WIB today) ---
T["NOTV"] = {
    "sale": "0x0415d265FdaE1CE6D0E778f78Daf6D0722f6Ab01",
    "name": "NOTV", "kind": "S1 factory sale",
    "status": "watchlist-only-not-open-2026-11-13",
    "totalSupply": 0, "totalMinted": 0, "FREE_SHARES": 2000,
    "freeStart": 1794567600, "freeStartWib": "2026-11-13 18:00:00 WIB",
    "baselineNote": "Watchlist-only-not-open run 0801 (temuan main run 0701; verifikasi ulang run ini 0/2000). BELUM dibuka (freeStart 18:00 WIB 13 Nov). TIDAK dilaporkan sebagai lead.",
    "lastReadBlock": 133263835, "lastReadWib": NOW,
}

# --- 5. AgentMuse -> track_c minted-by-user ---
T["AgentMuse"] = {
    "sale": "0x779fa133848d23052B7345F63B3b2E5309cd13ed",
    "name": "AgentMuse", "kind": "S1 factory sale",
    "status": "minted-by-user-2026-11-13",
    "freeClaimed": 176, "FREE_SHARES": 888,
    "bookedTotal": 17600000000000000000000000, "FREE_OSK": 100000000000000000000000,
    "bookedOf_user": 100000000000000000000000,
    "mintTx": "0x7d03a60177fe28c90aa8d9548ebd80504ee677f6637fc7454f4fd971707b7925",
    "note": "Mint eksekusi main job run 0601 (FREE_OSK booking terverifikasi); run 0801: freeClaimed 176/888, bookedOf(user)=FREE_OSK utuh. DIAM.",
    "lastReadBlock": 133263835, "lastReadWib": NOW,
}

# --- 6. PX24-group -> contracts watchlist-only-age-unverified (merge 0701 tertunda) ---
for nm, addr, ts, mx in [
    ("PX24", "0xe712510fcb27935e657e41ebb97982d6b123136c", 519, 1731),
    ("SKRR", "0x9081f02876c173d0c69f042959cfd0d61c668b17", 504, 1682),
    ("ME30", "0xa545c8726bcf4acf840dac521b369911fe2abc8d", 267, 1950),
    ("CY24", "0x731d879ee2cd4bbf32efef9178d51d5c1441d052", 451, 1703)]:
    names = {"PX24": ("Voxel Sprite", "PX24"), "SKRR": ("Skua Repeater", "SKRR"),
             "ME30": ("Forge Machine", "ME30"), "CY24": ("Chrome Runner", "CY24")}
    C[nm] = {
        "address": addr, "name": names[nm][0], "symbol": names[nm][1], "kind": "ERC721",
        "status": "watchlist-only-age-unverified-2026-11-13",
        "totalSupply": ts, "MAX_SUPPLY": mx, "mintOpen": 1,
        "balanceOf_user": 0, "costOf_user_1": 0,
        "ageVerified": False,
        "ageNote": "Umur TETAP UNVERIFIED run 0801: post Boltbook ~03:30-04:02 WIB saja; binary-search eth_call historis GAGAL (missing trie node, run 0701); eth_getLogs limit exceeded; Ankr 401 (outage sejak 9 Nov) memblokir koroborasi first-mint. costOf(user,1)=0 terbaca run ini tapi umur unverified memblokir semua promosi.",
        "baselineNote": "Watchlist-only first read main run 0701 (temuan Boltbook front page). TIDAK dilaporkan sebagai lead (bukan temuan baru run ini; umur unverified).",
        "lastReadBlock": 133263835, "lastReadWib": NOW,
    }

# --- 7. JAGENT + Lumen Findings -> upcoming watchlist ---
C["JAGENT"] = {
    "address": "0x70FdD1a7f382893708d00fC2eF9C38cAe7DEC92B",
    "name": "JAGENT", "symbol": "JAGENT", "kind": "ERC721",
    "status": "watchlist-only-upcoming-2026-11-13",
    "minted": 0, "freeSold": 0, "paidSold": 0, "FREE_SUPPLY": 500, "PAID_CAP": 15000,
    "START": 1794672034, "startWib": "2026-11-14 22:13:54 WIB",
    "FREE_END": 1794758434, "FREE_FEE": 100000000000000, "PRICE": 3000000000000000,
    "phase": 0, "freeOpen": 0, "paidOpen": 0,
    "REGISTRY": "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F",
    "freeQuotaOf_user": 1, "quotaOf_user": 10, "balanceOf_user": 0,
    "notFreeNote": "FREE_FEE()=0.0001 BNB TETAP - jalur 'free' berbayar, BUKAN gas-only (sama seperti OUTY); gagal kriteria (1) Free Bacot bahkan saat dibuka. TIDAK PERNAH jadi kandidat/lead.",
    "baselineNote": "Upcoming-watchlist run 0801 (temuan feed Sourcify recently-verified 01:25:54Z). BELUM dibuka (START 14 Nov 22:13:54 WIB), minted 0. TIDAK dilaporkan sebagai lead.",
    "lastReadBlock": 133264690, "lastReadWib": NOW,
}
C["LumenFindings"] = {
    "address": "0x4158B701EaA30E8FaDBaA526F70780A38318c1C4",
    "name": "Lumen Findings", "symbol": "FIND", "kind": "ERC721",
    "status": "watchlist-only-upcoming-2026-11-13",
    "totalSpecimens": 0, "currentExperiment": 0, "genesisStart": 0, "genesisOpen": 0,
    "priceFor_user": 0, "holdsAgentId_user": 1, "balanceOf_user": 0,
    "specimensOf_user": None,
    "baselineNote": "Upcoming-watchlist run 0801 (temuan feed Sourcify recently-verified 01:05:32Z; template sama dengan AgentLabs: genesis/experiment + mintFree/mintPaid + holdsAgentId). BELUM dibuka (genesisStart 0, genesisOpen 0, totalSpecimens 0). TIDAK dilaporkan sebagai lead; promosi ke early lead bila first mint terverifikasi + genesis dibuka.",
    "lastReadBlock": 133264690, "lastReadWib": NOW,
}

# --- 8. Fresh reads for existing entries ---
sol = C["SolNFT"]
sol.update({"totalMinted": 327, "freeMinted": 327, "freePctVerified": 98.2,
            "lastReadBlock": 133263835, "lastReadWib": NOW,
            "runNote0801": "Run 0801 (blok 133263835): freeMinted 327/333 = 98,2% (6 slot tersisa), mintOpen 1, slot user TERBUKA. Gate-blocked SUDAH dilaporkan 23:30 12 Nov - TANPA perubahan reportable, DIAM."})
hive = C["HIVE Agents"]
hive.update({"totalSupply": 1263, "lastReadBlock": 133263835, "lastReadWib": NOW,
             "runNote0801": "Run 0801 (blok 133263835): totalSupply 1263 flat vs run 0331 (1263), minted interval 0, velocity GAGAL; balanceOf(user)=1; minted-by-user, bukan kandidat."})
mecha = C["MECHA"]
mecha.update({"totalMinted": 1899, "freeClaimed": 1898, "freePctVerified": 42.7,
              "lastReadBlock": 133263835, "lastReadWib": NOW,
              "runNote0801": "Run 0801 (blok 133263835): totalMinted 1899, freeClaimed 1898/4444 = 42,7% (<50%/<70%); gate website TIDAK DITEMUKAN (tetap). DIAM."})
pg = C["Pickgrid"]
pg.update({"freeMinted": 216, "totalMinted": 218 if pg.get("totalMinted") else 218,
           "lastReadBlock": 133263835, "lastReadWib": NOW,
           "runNote0801": "Run 0801 (blok 133263835): free 216/300 = 72% TAPI umur UNVERIFIED - TIDAK BISA promosi ke strong lead, watchlist-only, DIAM."})
outy = C["OUTY"]
outy.update({"minted": 11, "freeSold": 11, "lastReadBlock": 133263835, "lastReadWib": NOW,
             "runNote0801": "Run 0801 (blok 133263835): freeSold 8->11/1500 (+3). FREE_FEE 0.0001 BNB TETAP - BUKAN gas-only; bukan kandidat/lead, tidak di-preview/di-mint, DIAM."})
al = C["AgentLabs"]
al.update({"totalSpecimens": 1494, "currentExperiment": 2,
           "lastReadBlock": 133264690, "lastReadWib": NOW,
           "runNote0801": "Run 0801 (blok 133264690): experiment 1 SELESAI 07:00 WIB, experiment 2 BERJALAN (currentExperiment 2, totalSpecimens 1494 vs 1487). specimensOf(user)/participants/isSealed/experimentEnd NULL run ini (view gagal, bukan nol) - slot user di experiment 2 UNVERIFIED. Early lead, TIDAK di-preview/TIDAK di-mint. DIAM (rollover experiment bukan promosi/perubahan tier)."})
notv = C.get("NOTV")
if isinstance(notv, dict):
    notv.update({"totalSupply": 0, "totalMinted": 0, "lastReadBlock": 133263835,
                 "lastReadWib": NOW,
                 "runNote0801": "Run 0801: masih 0/2000, freeStart 18:00 WIB 13 Nov - BELUM buka, DIAM."})

# --- 9. Age-exclusions: AgentGrid REPORTED once; BHTB silent (already reported 11 Nov) ---
mv_excluded("track_c", "AgentGrid", "age-excluded-2026-11-13",
            "Run 0801: deadline on-chain 1794433670 = 2026-11-12 04:47:50 WIB LEWAT; start derivasi ~2026-11-09 04:47 WIB -> umur ~100 jam (>=24 jam); freeUsed 21/500 (479 tersisa), belum sold out; gate tidak pernah lolos. Pernah dilaporkan sebagai early lead 9 Nov; age-exclusion dilaporkan sekali run ini. Dihapus dari track_c.")
mv_excluded("track_c", "BHTB", "age-excluded-2026-11-11",
            "Run 0801 (silent removal, bookkeeping catch-up): age-exclusion SUDAH dilaporkan sekali 11 Nov (umur 53,6 jam dari startTime 2026-11-08 18:44 WIB); baca segar run ini freeUsed 279/555, startTime 1794138281 = 2026-11-08 18:44:41 WIB mengonfirmasi. TIDAK dilaporkan ulang. Dihapus dari track_c.")
# LuckyCatch already absent from contracts (removed by parent ~05:05 WIB handling); record only.
s["runNote0801_luckycatch"] = "Run 0801 (blok 133263835): LuckyCatch totalSupply 21, agentFreeCount 20, paidSold 1, balanceOf(user)=0. Age-excluded SUDAH dilaporkan parent ~05:05 WIB dan kontrak SUDAH tidak ada di snapshot - TIDAK dilaporkan ulang, tidak ada yang dihapus run ini."

# --- 10. Checked-not-sale-shape feed items (compact, dedupe) ---
checked = {
 "0xAd4743EAD580A984d23Bb41161BA58fB3F540726": (5, "2026-11-13T01:27:18Z"),
 "0xF268D325F097333d1e620BA4033B39da8bBA0B82": (15, "2026-11-13T01:27:02Z"),
 "0x043d60d568456DE954D405cf69ABf65C624c4139": (8, "2026-11-13T01:25:52Z"),
 "0x190c669849322B489ba719da8408C9b3F1bB2D54": (12, "2026-11-13T01:18:53Z"),
 "0x9a631A11e547C87e61497Df68d686bE95D1A8D83": (12, "2026-11-13T01:16:23Z"),
 "0xD86679AcC5C79038ED192f52217B9Acb16b4313e": (34, "2026-11-13T01:15:46Z"),
 "0xEe71a51e4EB815e52B036Ada9C041D479fB336eA": (34, "2026-11-13T01:15:33Z"),
 "0x813d705A97a8600cE28651E119EF57338181b6Ea": (34, "2026-11-13T01:14:12Z"),
 "0xd91A76878bCd95f6f55A3A70f2Af3C3c1691a152": (34, "2026-11-13T01:13:55Z"),
 "0x817BE53cF090aE55d492aBc64Eca5E2eCF5043Ef": (12, "2026-11-13T01:06:23Z"),
 "0xfBaf998334e3ad792E4b107f284D25E4c3A443C0": (22, "2026-11-13T01:05:35Z"),
 "0xc5655b7653412533e733C034A6CF024776808c50": (10, "2026-11-13T01:05:22Z"),
 "0x605556634bed8068b5B2FDA7C28c98404A11DE73": (40, "2026-11-13T00:53:37Z"),
 "0xFb3A7Ff9Bb1ec2E62136b49E5836ff11eFF74805": (56, "2026-11-13T00:52:20Z"),
}
n_added = 0
for addr, (nfns, va) in checked.items():
    key = "Feed-0x" + addr[2:6]
    if key not in C and addr.lower() not in [str(v.get("address", "")).lower() for v in C.values() if isinstance(v, dict)]:
        C[key] = {"address": addr, "status": "checked-not-sale-shape-2026-11-13",
                  "n_fns": nfns, "sourcifyVerifiedAt": va,
                  "note": "Feed Sourcify recently-verified run 0801: S1/S2 false (tanpa mint+quote+free+agent lengkap). Bukan lead track-C; bukan early lead track-A.",
                  "lastReadWib": NOW}
        n_added += 1

# --- 11. Run notes + timestamps ---
s["timestamp_wib"] = NOW
s["last_run_wib"] = NOW
s["last_run_note"] = ("Run 0801: LAPOR 4x - (1) Agentx KANDIDAT GATE-BLOCKED (628/1111=56,5%, velocity LOLOS ~32,7x, umur 9,6 jam, diskusi Boltbook; website GAGAL); "
    "(2) Zero EARLY LEAD baru (117/500=23,4%, umur ~30 mnt, registry resmi); "
    "(3) JNTM TRACK-C LEAD blocked (306/1000=30,6%, gate pending L + quote NULL); "
    "(4) AgentGrid AGE-EXCLUDED (deadline lewat, umur ~100 jam). "
    "DIAM: Sol 327/333=98,2% gate-blocked; OBFG 618/1230=50,2% gate-blocked; AgentLabs exp 2 (slot unverified); OUTY 11/1500 fee; MECHA 42,7%; Pickgrid 72% umur-unverified; PX24-group umur-unverified; HIVE flat; NOTV belum buka; binanceai launched 0. "
    "BHTB silent-removal (age-excl sudah dilaporkan 11 Nov). Scan fast-fail Ankr 401 (watermark TETAP 132512564). Boltbook EN 44809/ZH 43134 byte, 2 alamat baru = tx hash (bukan kontrak). Bridge 116 kontrak, 0 baru. Feed baru dicek 14x (" + str(n_added) + " added). JAGENT + Lumen Findings upcoming-watchlist.")
s["runNote0801"] = s["last_run_note"]
s["runNote0801_scan"] = ("Run 0801 SCAN FAST-FAIL: pre-flight ankr_getLogs 1 chunk 50 blok GAGAL HTTP 401 Unauthorized (~9 dtk) - kelanjutan outage sejak 2026-11-09 (~4 hari; kuota freemium Ankr 0% s.d. 1 Des 2026). "
    "Driver penuh TIDAK dijalankan. Watermark TETAP 132512564; gap ke head ~751.000 blok dan membesar. 5c dilewati (tanpa output scan). 0 first-seen, 0 lead dari scan leg.")
s["runNote0801_bridge"] = "Run 0801 BRIDGE (read-only): 116 kontrak, 0 not-in-snapshot, 7 same-owner-discarded - tidak ada temuan pelengkap scan, tidak ada promosi."
s["runNote0801_binanceai"] = "Run 0801 (blok 133263835): binanceai.fun MINT launched()=0, tokenClaimed(user)=0, claimable NULL; TOKEN balanceOf(user)=0. Tetap belum buka/pending-refund (sudah dilaporkan sekali) - tanpa aksi, DIAM."
json.dump(s, open(BASE + "onchain-snapshot.json", "w"), indent=1)
print("MERGE OK; contracts:", len(C), "track_c:", len(T), "excluded:", len(EX), "checked added:", n_added)
