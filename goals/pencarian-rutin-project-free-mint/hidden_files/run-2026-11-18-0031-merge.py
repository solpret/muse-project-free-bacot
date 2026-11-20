#!/usr/bin/env python3
"""Merge run 2026-11-18 00:31 (free-mint-search) into the main snapshot.
Updates scalar readings + last_run fields only; does NOT delete history keys.
Interval: 0001 blok 134156373 -> 0031 blok 134160308 = 3935 blok * 0.45 dtk = ~29.5 mnt.
Adds two first-read entries: STOCK AGENT (early lead, reported once this run)
and THYRK (watchlist-only-age-unverified)."""
import json
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
snap = json.load(open(BASE + "onchain-snapshot.json"))
BLK = 134160308
WIB = "2026-11-18 ~00:31 WIB"

def upd(name, fields, note):
    e = snap["contracts"].get(name)
    if e is None:
        print("MISSING in snapshot:", name); return False
    e.update(fields)
    e["lastReadBlock"] = BLK
    e["lastReadWib"] = WIB
    e["runNote0031_1118"] = note
    return True

upd("HIVE Agents", {"totalSupply": 1263, "balanceOf_user": 1},
    "Run 0031 (blok 134160308): totalSupply 1263 FLAT, balanceOf(user)=1, minted-by-user. DIAM.")
upd("Bubblebruin", {"totalSupply": 2620, "freeClaimed": 2614, "balanceOf_user": 1,
                    "previousTotalSupply": 2620, "mintedInInterval": 0,
                    "currentRatePerMin": 0.0, "velocityLegPasses": False,
                    "freePctVerified": 33.6},
    "Run 0031 (blok 134160308): totalSupply 2620 FLAT vs 0001 (2620), freeClaimed 2614/7777=33,6% (<70%). velocity 0. minted-by-user, bukan kandidat. DIAM.")
upd("CAT402", {"freeCatsClaimed": 100, "freeCatsRemaining": 0},
    "Run 0031 (blok 134160308): freeCatsClaimed 100/100, freeCatsRemaining 0 -> tetap SOLD OUT (sudah dilaporkan hot-leg 19:44 + run 2231). totalSupply/mintOpen revert run ini (nilai lama dipertahankan). DIAM.")
upd("JADE", {"totalSupply": 191, "freeClaimed": 188, "cost_user_1": 500000000000000},
    "Run 0031 (blok 134160308): totalSupply 191 FLAT, freeClaimed 188; cost(user,1)=0,0005 BNB -> slot user TIDAK gratis (jalur berbayar). Bukan kandidat/lead. DIAM.")
upd("Agent Bubble", {"freeMinted": 1869, "totalSupply": 2014, "totalMinted": 2014,
                     "previousTotalSupply": 2012, "mintedInInterval": 2,
                     "intervalMinutes": 29.5, "currentRatePerMin": 0.07,
                     "previousRatePerMin": 0.07, "velocityRatio": 0.97,
                     "velocityLegPasses": False},
    "Run 0031 (blok 134160308): freeMinted 1867->1869, totalSupply 2012->2014 (+2, 0,07/mnt vs prev 0,07 = 0,97x, <20) -> velocity GAGAL. free% TETAP UNVERIFIED (FREE_SUPPLY null) + umur UNVERIFIED -> BUKAN strong lead. DIAM.")
upd("DRAGON", {"freeMinted": 1000, "totalMinted": 1005, "balanceOf_user": 1},
    "Run 0031 (blok 134160308): freeMinted 1000, totalMinted 1005, balanceOf(user)=1 (minted-by-user). freeRemaining 0 (sudah diketahui). DIAM.")
upd("Matrix Agents", {"freeMinted": 588, "freeRemaining": 412, "totalSupply": 585,
                      "previousTotalSupply": 585, "mintedInInterval": 0,
                      "velocityLegPasses": False, "freePctVerified": 58.8},
    "Run 0031 (blok 134160308): freeMinted 588 FLAT, totalSupply 585 FLAT; free 588/1000=58,8% (<70%). velocity GAGAL. DIAM.")
upd("AGCLUB", {"totalMinted": 523, "freeMinted": 523, "FREE_CAP": 888,
               "velocityLegPasses": False, "freePctVerified": 58.9},
    "Run 0031 (blok 134160308): freeMinted 523 FLAT; free 523/888=58,9% (<70%). DIAM.")
upd("SPARKS", {"totalSupply": 1156},
    "Run 0031 (blok 134160308): totalSupply 1155->1156 (+1). DIAM.")
upd("Ledgera", {"freeClaimed": 2702, "totalSupply": 2709, "freeUsed_user": 0,
                "balanceOf_user": 0, "previousTotalSupply": 2709,
                "mintedInInterval": 0, "velocityLegPasses": False,
                "freePctVerified": 54.0},
    "Run 0031 (blok 134160308): freeClaimed 2702 FLAT, totalSupply 2709 FLAT; free 2702/5000=54,0% (<70%). velocity GAGAL. Umur UNVERIFIED. DIAM.")
upd("RaceAgents", {"totalSupply": 632, "freeMinted": 632},
    "Run 0031 (blok 134160308): totalSupply 631->632 (+1), freeMinted 631->632. velocity GAGAL. DIAM.")
upd("CPASS", {"totalMinted": 1773, "balanceOf_user": 0},
    "Run 0031 (blok 134160308): totalMinted 1773 FLAT. DIAM.")
upd("REOPIR", {"freeClaimed": 581, "totalSupply": 581},
    "Run 0031 (blok 134160308): freeClaimed 581 FLAT, totalSupply 581. DIAM.")
upd("RAVE", {"totalMinted": 366, "freeMinted": 366},
    "Run 0031 (blok 134160308): totalMinted 366 FLAT. DIAM.")
upd("MORFO", {"totalMinted": 1089},
    "Run 0031 (blok 134160308): totalMinted 1087->1089 (+2). DIAM.")
upd("PIXEL FROGS", {"totalSupply": 456, "freeMinted": 454, "freeLeft": 2546,
                   "mintOpen": 0, "freeClaimed_user": 0, "freePctVerified": 15.1},
    "Run 0031 (blok 134160308): totalSupply 456 FLAT, freeMinted 454, freeLeft 2546, mintOpen=0 (tutup); free 454/(454+2546)=15,1% (<70%). DIAM.")
upd("Flare Agent-bd6f", {"totalSupply": 4900},
    "Run 0031 (blok 134160308): totalSupply 4900 FLAT. DIAM.")
upd("PunchCard", {"totalSupply": 1303, "totalMinted": 1303, "freeMinted": 1281,
                  "paidMinted": 22, "previousTotalSupply": 1303,
                  "mintedInInterval": 0, "intervalMinutes": 29.5,
                  "currentRatePerMin": 0.0, "previousRatePerMin": 0.30,
                  "velocityRatio": 0.0, "velocityLegPasses": False,
                  "freePctVerified": 23.1, "mintPriceFor_user_1": 0,
                  "mintedCount_user": 0, "balanceOf_user": 0},
    "Run 0031 (blok 134160308): totalSupply 1303 FLAT (+0, 0,00/mnt vs prev 0,30 = 0,0x) -> velocity GAGAL. freeMinted 1281; free 1281/5555=23,1% (<50% kandidat, <70% strong lead); umur UNVERIFIED -> BUKAN kandidat/strong lead. Slot user terbuka (mintPriceFor 0, mintedCount 0). DIAM.")
upd("XCOPY", {"totalSupply": 452, "totalMinted": 452, "previousTotalSupply": 451,
              "mintedInInterval": 1, "velocityLegPasses": False},
    "Run 0031 (blok 134160308): totalSupply 451->452 (+1) -> velocity GAGAL. DIAM.")
upd("ARKYN", {"totalMinted": 1976, "previousTotalSupply": 1976,
              "mintedInInterval": 0, "velocityLegPasses": False},
    "Run 0031 (blok 134160308): totalMinted 1976 FLAT -> velocity GAGAL; totalSupply revert run ini. free% UNVERIFIED. DIAM.")
upd("Mine Card", {"totalSupply": 1093, "totalMinted": 1093,
                  "previousTotalSupply": 1087, "mintedInInterval": 6,
                  "intervalMinutes": 29.5, "currentRatePerMin": 0.20,
                  "previousRatePerMin": 0.23, "velocityRatio": 0.88,
                  "velocityLegPasses": False},
    "Run 0031 (blok 134160308): totalSupply 1087->1093 (+6, 0,20/mnt vs prev 0,23 = 0,88x, <20) -> velocity GAGAL. free% + umur UNVERIFIED -> BUKAN kandidat/strong lead. DIAM.")
upd("ALIEN", {"totalSupply": 473, "previousTotalSupply": 472,
              "mintedInInterval": 1, "velocityLegPasses": False},
    "Run 0031 (blok 134160308): totalSupply 472->473 (+1, <20) -> velocity GAGAL. free% + umur UNVERIFIED. DIAM.")
upd("Kitebots", {"totalSupply": 1456, "freeMinted": 1456, "previousTotalSupply": 1456,
                 "mintedInInterval": 0, "velocityLegPasses": False},
    "Run 0031 (blok 134160308): totalSupply 1456 FLAT, freeMinted 1456 -> velocity GAGAL. Umur UNVERIFIED. DIAM.")
upd("Everything Is Mine (EIM)", {"totalMinted": 415, "mintOpen": 1,
                                 "velocityLegPasses": False},
    "Run 0031 (blok 134160308): totalMinted 407->415 (+8, 0,27/mnt vs prev 0,07 = ~4,1x TAPI <20) -> velocity GAGAL. free% + umur UNVERIFIED -> tetap early lead, BUKAN strong lead/kandidat. TIDAK preview/mint. DIAM.")
upd("Lumenhold", {"totalSupply": 1247, "freeClaimed": 1242,
                  "previousTotalSupply": 1245, "mintedInInterval": 2,
                  "velocityLegPasses": False, "freePctVerified": 82.8},
    "Run 0031 (blok 134160308): totalSupply 1245->1247, freeClaimed 1240->1242; free 1242/1500=82,8% TERVERIFIKASI (>70%) TAPI umur UNVERIFIED + velocity GAGAL -> BUKAN strong lead/kandidat. TIDAK dilaporkan. DIAM.")
upd("PXIO Miners", {"totalSupply": 16666, "previousTotalSupply": 16532,
                    "mintedInInterval": 134, "velocityLegPasses": False},
    "Run 0031 (blok 134160308): totalSupply 16532->16666 (+134/29,5 mnt, hot-leg focus, BUKAN di snapshot-tier; free view tetap None semua, first-seen 16 Nov 19:19 WIB (>24 jam), checked-not-sale-shape, minted-by-user). Dicatat saja, bukan tier. DIAM.")
upd("FrieAgent-B751", {"totalSupply": 9901},
    "Run 0031 (blok 134160308): totalSupply 9901 FLAT. DIAM.")
upd("FrieAgent-c64d", {"totalSupply": 4901},
    "Run 0031 (blok 134160308): totalSupply 4901 FLAT. DIAM.")
upd("Abyssora", {},
    "Run 0031 (blok 134160308): totalSupply GAGAL baca (revert) - degradasi view, BUKAN nol; nilai lama dipertahankan. DIAM.")
upd("HANAMI", {"totalSupply": 132, "freeMinted": 130, "previousTotalSupply": 132,
               "mintedInInterval": 0, "velocityLegPasses": False},
    "Run 0031 (blok 134160308): totalSupply 132 FLAT, freeMinted 130 -> velocity GAGAL. DIAM.")
upd("Zephyra", {"totalMinted": 991},
    "Run 0031 (blok 134160308): totalMinted 987->991 (+4). DIAM.")
upd("AgentNOVA", {"totalSupply": 723},
    "Run 0031 (blok 134160308): totalSupply 721->723 (+2). DIAM.")
upd("ONI", {"totalMinted": 6, "totalSupply": 6},
    "Run 0031 (blok 134160308): totalMinted 6 FLAT. DIAM.")
upd("HAPPE AGENTS", {"totalMinted": 241, "freeMinted": 222},
    "Run 0031 (blok 134160308): totalMinted 241 FLAT, freeMinted 222. DIAM.")
upd("Pengu", {"totalMinted": 138, "freeMinted": 138},
    "Run 0031 (blok 134160308): totalMinted 138 FLAT, freeMinted 138. DIAM.")
# BoldLeonidas / BNBG / Kryntar: reread-only items (no snapshot entry expected) -
# BoldLeonidas totalSupply 1111 FLAT, mintOpen 1, balanceOf(user) 0; BNBG totalMinted 69 FLAT;
# Kryntar totalMinted 1370 FLAT. Recorded in runNote0031 only.

# ---- NEW first-read entries ----
snap["contracts"]["STOCK AGENT"] = {
    "address": "0xba7068233da805bdebcc167be361c219002e6b7f",
    "status": "early-lead-reported-2026-11-18-0031",
    "name": "STOCK AGENT",
    "symbol": "STOCK",
    "kind": "ERC721",
    "totalSupply": 509,
    "freeLeft": 602,
    "FREE_SUPPLY": 1111,
    "MAX_SUPPLY": 2222,
    "mintOpen": 1,
    "mintPrice": 500000000000000,
    "quote_user_1": 0,
    "freeMintedByWallet_user": 0,
    "balanceOf_user": 0,
    "freePctVerified": 45.8,
    "firstSeenBlock": 134160826,
    "firstSeenWib": "2026-11-18 ~00:31 WIB",
    "xVerified": False,
    "velocityVerified": False,
    "websiteGate": "unverified",
    "launchNote": "Umur peluncuran UNVERIFIED: Sourcify verifiedAt 2026-11-17T14:51:29Z (21:51 WIB 17 Nov) menunjukkan kontrak baru, TAPI verifiedAt BUKAN launch time; waktu peluncuran proyek belum ditemukan (pencarian nama + alamat kontrak tidak menemukan situs/proyek); koroborasi first-mint terblokir Ankr 401. Diskusi publik: post Boltbook cskh.ai ~00:25 WIB 18 Nov ('STOCK AGENT (STOCK, BSC) block 134,159,386 recheck: 504/2,222 minted').",
    "baselineNote": "EARLY lead dilaporkan sekali run 0031 2026-11-18 (S1 TRUE: mint+quote+freeLeft/freeMintedByWallet+agent ref hasAgentId; first-seen oleh job ini run ini; mint terverifikasi on-chain 509). TIDAK PERNAH auto-mint/preview. Naik jadi strong lead hanya bila 3 kaki lead kuat terpenuhi; jadi kandidat hanya bila SEMUA kriteria + safety lolos. free 509/1111=45,8% (<50% kandidat, <70% strong lead). Slot user TERBUKA (quote 0, freeMintedByWallet 0). Website gate BELUM terverifikasi (contractURI revert; pencarian nama+kontrak tidak menemukan situs) -> TIDAK ADA preview/eksekusi sampai gate lolos.",
    "previousTotalSupply": 509,
    "mintedInInterval": 0,
    "intervalMinutes": 0,
    "currentRatePerMin": 0.0,
    "previousRatePerMin": None,
    "velocityLegPasses": False,
    "supplyView": "totalSupply",
    "lastReadBlock": 134160826,
    "lastReadWib": WIB,
    "runNote0031_1118": "Run 0031 (blok 134160826 first-read): EARLY LEAD dilaporkan sekali. totalSupply 509, freeLeft 602/1111=45,8% free, mintOpen 1, quote(user,1)=0, slot user terbuka. Umur UNVERIFIED, velocity belum ada baseline, X unverified, website gate unverified. TIDAK preview/mint."
}
snap["contracts"]["THYRK"] = {
    "address": "0x4d90ffc3075fb8897edff6d7c6269c906664a20e",
    "status": "watchlist-only-age-unverified-2026-11-18",
    "name": "THYRK",
    "kind": "ERC721",
    "totalSupply": 4414,
    "freeMinted": 4313,
    "MAX_SUPPLY": 7777,
    "mintActive": 1,
    "freeUsed_user": 1,
    "balanceOf_user": 1,
    "freePctNote": "freeMinted 4313; penyebut kuota gratis UNVERIFIED (post Boltbook klaim 7.896, MAX_SUPPLY 7.777) -> ~55% (4313/7777=55,4% atau 4313/7896=54,6%), di atas 50% TAPI di bawah 70%.",
    "firstSeenBlock": 134160826,
    "firstSeenWib": "2026-11-18 ~00:31 WIB",
    "xVerified": False,
    "velocityVerified": False,
    "websiteGate": "unverified",
    "ageNote": "Umur peluncuran UNVERIFIED: Sourcify verifiedAt 2026-11-09T22:19:52Z (kontrak sudah ada sejak 9 Nov, mengindikasikan umur >24 jam) TAPI verifiedAt BUKAN launch time; koroborasi first-mint terblokir Ankr 401; waktu peluncuran proyek belum ditemukan. Pace Boltbook +12 dalam 1137 mnt (~0,01/mnt) -> velocity MATI.",
    "baselineNote": "First-read run 0031 2026-11-18 via Boltbook front page (post nice969.ai ~00:28 WIB: 'THYRK: 4.414/7.896 free (55,9%)'). S1 TRUE (mint+quote+freeMinted/freeUsed+agentIdRegistry/holdsAgentId). BUKAN early lead (proyek lama, mint sudah berjalan berhari-hari, bukan first-seen minting) dan BUKAN strong lead/kandidat (velocity mati, umur unverified, slot user SUDAH TERPAKAI freeUsed=1/balanceOf=1). Watchlist-only; TIDAK dilaporkan sebagai lead.",
    "previousTotalSupply": 4414,
    "mintedInInterval": 0,
    "intervalMinutes": 0,
    "currentRatePerMin": 0.0,
    "previousRatePerMin": None,
    "velocityLegPasses": False,
    "supplyView": "totalSupply",
    "lastReadBlock": 134160826,
    "lastReadWib": WIB,
    "runNote0031_1118": "Run 0031 (blok 134160826 first-read): watchlist-only-age-unverified. totalSupply 4414, freeMinted 4313, MAX 7777, mintActive 1, slot user SUDAH TERPAKAI (freeUsed=1, balanceOf=1). Velocity mati (+12/1137 mnt per Boltbook). BUKAN lead/kandidat. DIAM."
}

# ---- Track C: RigForge + bsccat + pepe ----
rf = snap.get("track_c", {}).get("RigForge")
if rf is not None:
    rf.update({"freeSharesLeft": 625, "openedAt": 0, "freeClaimed": 375,
               "freeBooked_user": 10000000000000000000000,
               "lastReadWib": WIB, "lastReadBlock": BLK})
    rf["runNote0031_1118"] = ("Run 0031 (blok 134160308): freeSharesLeft 626->625, openedAt 0 "
        "(pool BELUM buka), freeClaimed 374->375, freeBooked(user)=10000 RIG. Tetap lead-minted-by-user, belum dibuka. DIAM.")
    print("RigForge: still not open, freeSharesLeft 625")
bs = snap.get("track_c", {}).get("bsccat")
if bs is not None:
    bs.update({"freeMinted": 519, "lastReadWib": WIB, "lastReadBlock": BLK})
    bs["runNote0031_1118"] = "Run 0031 (blok 134160308): freeMinted 519 FLAT. Tetap watchlist-only-age-unverified. DIAM."
    print("bsccat: freeMinted 519 flat")
pp = snap.get("track_c", {}).get("PEPE")
if pp is not None:
    pp.update({"lastReadWib": WIB, "lastReadBlock": BLK})
    pp["runNote0031_1118"] = ("Run 0031 (blok 134160308): freeMinted 500 (pool habis), soldShares 501, "
        "opened 0, hasMinted(user)=1. Tetap minted-by-user. DIAM.")
    print("PEPE: unchanged")

# ---- Track B pending: binanceai.fun ----
pc = snap.get("pending_claims", {}).get("binanceai.fun")
if pc is not None:
    pc.update({"launched": 0, "failed": 1, "isRefundPhase": 1,
               "tokenClaimed_user": 0, "lastReadWib": WIB})
    pc["runNote0031_1118"] = ("Run 0031 (blok 134160308): launched=0, failed=1, isRefundPhase=1, "
        "tokenClaimed(user)=0, totalShares 3110 - tetap pending/refund, sudah dilaporkan sekali (fase refund), DIAM.")
    print("binanceai pending: still launched=0, failed=1, refund=1 (no change)")

snap["last_run"] = "2026-11-18 ~00:31 WIB"
snap["last_run_wib"] = "2026-11-18 ~00:31 WIB"
snap["timestamp_wib"] = "2026-11-18 ~00:31 WIB"
snap["runNote0031"] = (
    "Run 0031 (jadwal 00:31 WIB 2026-11-18): 1 EARLY LEAD BARU (STOCK AGENT, dilaporkan sekali), "
    "0 kandidat baru, 0 strong lead baru, 0 track-B dibuka, 0 track-C lead/kandidat baru. "
    "THYRK first-read -> watchlist-only-age-unverified (bukan lead). "
    "Reread 40/40 OK (blok 134160308, 93,4 dtk, 141 calls, 0 chunk error; interval ~29,5 mnt vs 0001): "
    "HIVE 1263 flat; Bubblebruin 2620 FLAT, free 2614/7777=33,6%; "
    "Agent Bubble 2012->2014 (+2, 0,07/mnt, 0,97x) velocity GAGAL; free% UNVERIFIED (FREE_SUPPLY null) + umur UNVERIFIED -> bukan strong lead; "
    "PunchCard 1303 FLAT (+0) velocity GAGAL, free 1281/5555=23,1%; "
    "Mine Card 1087->1093 (+6, 0,20/mnt vs prev 0,23 = 0,88x, <20) velocity GAGAL; ALIEN 472->473 (+1) velocity GAGAL; "
    "Matrix free 588/1000=58,8%; AGCLUB free 523/888=58,9%; Ledgera free 2702/5000=54,0%; "
    "Lumenhold free 1242/1500=82,8% TERVERIFIKASI tapi umur unverified + velocity GAGAL -> bukan strong lead; "
    "JADE cost(user,1)=0,0005 BNB -> slot user TIDAK gratis; "
    "EIM 407->415 (+8, ~4,1x TAPI <20) velocity GAGAL; XCOPY 451->452; RaceAgents 631->632; MORFO 1087->1089; "
    "SPARKS 1155->1156; Zephyra 987->991; AgentNOVA 721->723; Kitebots 1456 FLAT; CPASS 1773 FLAT; "
    "PXIO-Miners 16532->16666 (+134, hot-leg focus, bukan tier); BNBG totalMinted 69 FLAT; CAT402 100/100 tetap SOLD OUT; "
    "DRAGON freeRemaining 0; RigForge openedAt 0, freeSharesLeft 625, freeClaimed 375; bsccat freeMinted 519 flat; "
    "PEPE pool habis, opened 0. BinanceAI pending tetap launched=0/failed=1/refund=1. "
    "Pre-flight Ankr 401 fast-fail (ke-33 berturut-turut main job, 7,7 dtk, head 134160184), "
    "watermark TETAP 134086385 (milik backfill cron); scan + 5c dilewati. "
    "Feed Sourcify 20 kontrak (top verifiedAt 17:33:54Z); 2 baru vs hot-leg 0029 dicek run ini "
    "(0xd966 token biasa 40 fn tanpa mint/quote/freeview/agent; 0x8157 token PikaLaunch 103 fn, quoteAsset tapi tanpa mint/freeview/agent), 0 hit S1/S2; "
    "0x2F95 + 0x8a44 sudah di-shape-check hot-leg 0024/0029, 0 hit. "
    "Boltbook EN 44.543 B (13 alamat) / ZH 42.793 B (13 alamat); 2 temuan baru first-read run ini: "
    "STOCK AGENT 0xba70 (EARLY lead, lihat entri) + THYRK 0x4d90 (watchlist-only); sisanya sudah dikenal: "
    "Fable 0x182b (track_c checked-not-sale-shape 16 Nov), HOG 0x336a (post audit memecoin, bukan lead free-mint), "
    "FIND 0x4158 (age-excluded 14 Nov), PXIO Miners 0x58e8 (watchlist, TUTUP 16.666/16.666), "
    "Agentx 0x64a5 (age-excluded 13 Nov), Lion's Share 0x6ac0 (age-excluded 8 Nov), "
    "Forge Machine 0xa545 (watchlist-only-age-unverified, 358/2280=15,7%), "
    "Chipmunks 0xb262 (excluded-free-exhausted 9 Nov), Navigara 0x551f (same-owner-discarded, tidak pernah dipromosikan). "
    "1% Club (post Sensus 02:21 WIT: window buka 02:00 WIT, free lane 1/10 masih kosong) TANPA alamat kontrak di post -> tidak bisa diverifikasi on-chain, bukan lead. "
    "Bridge 116 kontrak, 0 outside snapshot, 7 same_owner_discarded. "
    "Sweep EN+ZH: semua sudah dikenal (Oathbots 28 Okt, Agentic Gangster 9 Nov free 111/111 habis, STAMP PASS sold-out-free-pool 10 Nov, "
    "Burn Agent excluded-free-sold-out 9 Nov, AGENT COSMOS 5 Nov, First-Dollar Grove 8 Nov, Bitcoin Frogs free 2000/2000 habis, "
    "AGENT ID cards sold-out 12 Nov, Laser Agents di daftar excluded, AGENT MAO paused, MOLT AGENT excluded-free-pool 9 Nov) - 0 kandidat baru. "
    "Route 6: Odaily newsflash 200 (0 pengumuman free-mint Agent ID baru), PANews 200 (0 pengumuman free-mint Agent ID baru). "
    "LAPORAN CHAT: 1 early lead (STOCK AGENT)."
)
json.dump(snap, open(BASE + "onchain-snapshot.json", "w"), indent=1)
print("SNAPSHOT UPDATED, last_run 00:31 WIB")
