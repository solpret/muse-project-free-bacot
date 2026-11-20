#!/usr/bin/env python3
"""Merge run 2026-11-18 00:01 (free-mint-search) into the main snapshot.
Updates scalar readings + last_run fields only; does NOT delete history keys.
Interval: 2331 blok 134152336 -> 0001 blok 134156373 = 4037 blok * 0.45 dtk = ~30.3 mnt.
Hot-leg 2359 re-read blok 134156063 just before this run (AgentBubble 1866/2011,
AGCLUB 523, CPASS 1772, MORFO 1087, AgentNOVA 721, Zephyra 982) - no tier change; values below are this run's."""
import json
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
snap = json.load(open(BASE + "onchain-snapshot.json"))
BLK = 134156373
WIB = "2026-11-18 ~00:01 WIB"

def upd(name, fields, note):
    e = snap["contracts"].get(name)
    if e is None:
        print("MISSING in snapshot:", name); return False
    e.update(fields)
    e["lastReadBlock"] = BLK
    e["lastReadWib"] = WIB
    e["runNote0001_1118"] = note
    return True

upd("HIVE Agents", {"totalSupply": 1263, "balanceOf_user": 1},
    "Run 0001 (blok 134156373): totalSupply 1263 FLAT, balanceOf(user)=1, minted-by-user. DIAM.")
upd("Bubblebruin", {"totalSupply": 2620, "freeClaimed": 2614, "balanceOf_user": 1,
                    "previousTotalSupply": 2620, "mintedInInterval": 0,
                    "currentRatePerMin": 0.0, "velocityLegPasses": False,
                    "freePctVerified": 33.6},
    "Run 0001 (blok 134156373): totalSupply 2620 FLAT vs 2301 (2620), freeClaimed 2614/7777=33,6% (<70%). velocity 0. minted-by-user, bukan kandidat. DIAM.")
upd("CAT402", {"freeCatsClaimed": 100, "freeCatsRemaining": 0},
    "Run 0001 (blok 134156373): freeCatsClaimed 100/100, freeCatsRemaining 0 -> tetap SOLD OUT (sudah dilaporkan hot-leg 19:44 + run 2231). totalSupply/mintOpen revert run ini (nilai lama dipertahankan). DIAM.")
upd("JADE", {"totalSupply": 191, "freeClaimed": 188, "cost_user_1": 500000000000000},
    "Run 0001 (blok 134156373): totalSupply 191 FLAT, freeClaimed 188; cost(user,1)=0,0005 BNB -> slot user TIDAK gratis (jalur berbayar). Bukan kandidat/lead. DIAM.")
upd("Agent Bubble", {"freeMinted": 1867, "totalSupply": 2012, "totalMinted": 2012,
                     "previousTotalSupply": 2010, "mintedInInterval": 2,
                     "intervalMinutes": 30.3, "currentRatePerMin": 0.07,
                     "previousRatePerMin": 0.49, "velocityRatio": 0.13,
                     "velocityLegPasses": False},
    "Run 0001 (blok 134156373): freeMinted 1865->1867, totalSupply 2010->2012 (+2, 0,07/mnt vs prev 0,49 = 0,13x, <20) -> velocity GAGAL. free% TETAP UNVERIFIED (FREE_SUPPLY null) + umur UNVERIFIED -> BUKAN strong lead. DIAM.")
upd("DRAGON", {"freeMinted": 1000, "totalMinted": 1005, "balanceOf_user": 1},
    "Run 0001 (blok 134156373): freeMinted 1000, totalMinted 1005, balanceOf(user)=1 (minted-by-user). freeRemaining 0 (sudah diketahui). DIAM.")
upd("Matrix Agents", {"freeMinted": 588, "freeRemaining": 412, "totalSupply": 585,
                      "previousTotalSupply": 585, "mintedInInterval": 0,
                      "velocityLegPasses": False, "freePctVerified": 58.8},
    "Run 0001 (blok 134156373): freeMinted 588 FLAT, totalSupply 585 FLAT; free 588/1000=58,8% (<70%). velocity GAGAL. DIAM.")
upd("AGCLUB", {"totalMinted": 523, "freeMinted": 523, "FREE_CAP": 888,
               "velocityLegPasses": False, "freePctVerified": 58.9},
    "Run 0001 (blok 134156373): freeMinted 522->523; free 523/888=58,9% (<70%). DIAM.")
# BNBG: no snapshot entry (reread-only item) - totalMinted 69 FLAT, recorded in runNote0001 only.
upd("SPARKS", {"totalSupply": 1155},
    "Run 0001 (blok 134156373): totalSupply 1153->1155 (+2). DIAM.")
upd("Ledgera", {"freeClaimed": 2702, "totalSupply": 2709, "freeUsed_user": 0,
                "balanceOf_user": 0, "previousTotalSupply": 2709,
                "mintedInInterval": 0, "velocityLegPasses": False,
                "freePctVerified": 54.0},
    "Run 0001 (blok 134156373): freeClaimed 2702 FLAT, totalSupply 2709 FLAT; free 2702/5000=54,0% (<70%). velocity GAGAL. Umur UNVERIFIED. DIAM.")
upd("RaceAgents", {"totalSupply": 631, "freeMinted": 631},
    "Run 0001 (blok 134156373): totalSupply 631 FLAT, freeMinted 631. DIAM.")
upd("CPASS", {"totalMinted": 1773, "balanceOf_user": 0},
    "Run 0001 (blok 134156373): totalMinted 1771->1773 (+2). DIAM.")
upd("REOPIR", {"freeClaimed": 581, "totalSupply": 581},
    "Run 0001 (blok 134156373): freeClaimed 581 FLAT, totalSupply 581. DIAM.")
upd("RAVE", {"totalMinted": 366, "freeMinted": 366},
    "Run 0001 (blok 134156373): totalMinted 366 FLAT. DIAM.")
upd("MORFO", {"totalMinted": 1087},
    "Run 0001 (blok 134156373): totalMinted 1084->1087 (+3). DIAM.")
upd("PIXEL FROGS", {"totalSupply": 456, "freeMinted": 454, "freeLeft": 2546,
                   "mintOpen": 0, "freeClaimed_user": 0, "freePctVerified": 15.1},
    "Run 0001 (blok 134156373): totalSupply 456 FLAT, freeMinted 454, freeLeft 2546, mintOpen=0 (tutup); free 454/(454+2546)=15,1% (<70%). DIAM.")
upd("Flare Agent-bd6f", {"totalSupply": 4900},
    "Run 0001 (blok 134156373): totalSupply 4900 FLAT. DIAM.")
upd("PunchCard", {"totalSupply": 1303, "totalMinted": 1303, "freeMinted": 1281,
                  "paidMinted": 22, "previousTotalSupply": 1294,
                  "mintedInInterval": 9, "intervalMinutes": 30.3,
                  "currentRatePerMin": 0.30, "previousRatePerMin": 0.07,
                  "velocityRatio": 4.29, "velocityLegPasses": False,
                  "freePctVerified": 23.1, "mintPriceFor_user_1": 0,
                  "mintedCount_user": 0, "balanceOf_user": 0},
    "Run 0001 (blok 134156373): totalSupply 1294->1303 (+9, 0,30/mnt vs prev 0,07 = 4,29x TAPI <20 token) -> velocity GAGAL. freeMinted 1276->1281; free 1281/5555=23,1% (<50% kandidat, <70% strong lead); umur UNVERIFIED -> BUKAN kandidat/strong lead. Slot user terbuka (mintPriceFor 0, mintedCount 0). DIAM.")
upd("XCOPY", {"totalSupply": 451, "totalMinted": 451, "previousTotalSupply": 450,
              "mintedInInterval": 1, "velocityLegPasses": False},
    "Run 0001 (blok 134156373): totalSupply 450->451 (+1) -> velocity GAGAL. DIAM.")
upd("ARKYN", {"totalMinted": 1976, "previousTotalSupply": 1975,
              "mintedInInterval": 1, "velocityLegPasses": False},
    "Run 0001 (blok 134156373): totalMinted 1975->1976 (+1) -> velocity GAGAL; totalSupply revert run ini. free% UNVERIFIED. DIAM.")
upd("Mine Card", {"totalSupply": 1087, "totalMinted": 1087,
                  "previousTotalSupply": 1080, "mintedInInterval": 7,
                  "intervalMinutes": 30.3, "currentRatePerMin": 0.23,
                  "previousRatePerMin": 0.24, "velocityRatio": 0.96,
                  "velocityLegPasses": False},
    "Run 0001 (blok 134156373): totalSupply 1080->1087 (+7, 0,23/mnt vs prev 0,24 = 0,96x, <20) -> velocity GAGAL. free% + umur UNVERIFIED -> BUKAN kandidat/strong lead. DIAM.")
upd("ALIEN", {"totalSupply": 472, "previousTotalSupply": 471,
              "mintedInInterval": 1, "velocityLegPasses": False},
    "Run 0001 (blok 134156373): totalSupply 471->472 (+1, <20) -> velocity GAGAL. free% + umur UNVERIFIED. DIAM.")
upd("Kitebots", {"totalSupply": 1456, "freeMinted": 1456, "previousTotalSupply": 1455,
                 "mintedInInterval": 1, "velocityLegPasses": False},
    "Run 0001 (blok 134156373): totalSupply 1455->1456 (+1), freeMinted 1455->1456 -> velocity GAGAL. Umur UNVERIFIED. DIAM.")
upd("Everything Is Mine (EIM)", {"totalMinted": 407, "mintOpen": 1,
                                 "velocityLegPasses": False},
    "Run 0001 (blok 134156373): totalMinted 405->407 (+2 <20) -> velocity GAGAL. free% + umur UNVERIFIED -> tetap early lead, BUKAN strong lead/kandidat. TIDAK preview/mint. DIAM.")
upd("Lumenhold", {"totalSupply": 1245, "freeClaimed": 1240,
                  "previousTotalSupply": 1241, "mintedInInterval": 4,
                  "velocityLegPasses": False, "freePctVerified": 82.7},
    "Run 0001 (blok 134156373): totalSupply 1241->1245, freeClaimed 1236->1240; free 1240/1500=82,7% TERVERIFIKASI (>70%) TAPI umur UNVERIFIED + velocity GAGAL -> BUKAN strong lead/kandidat. TIDAK dilaporkan. DIAM.")
upd("PXIO Miners", {"totalSupply": 16532, "previousTotalSupply": 15952,
                    "mintedInInterval": 580, "velocityLegPasses": False},
    "Run 0001 (blok 134156373): totalSupply 15952->16532 (+580/30,3 mnt, hot-leg focus, BUKAN di snapshot-tier; free view tetap None semua, first-seen 16 Nov 19:19 WIB (>24 jam), checked-not-sale-shape, minted-by-user). Dicatat saja, bukan tier. DIAM.")
upd("FrieAgent-B751", {"totalSupply": 9901},
    "Run 0001 (blok 134156373): totalSupply 9901 FLAT. DIAM.")
upd("FrieAgent-c64d", {"totalSupply": 4901},
    "Run 0001 (blok 134156373): totalSupply 4901 FLAT. DIAM.")
upd("Abyssora", {},
    "Run 0001 (blok 134156373): totalSupply GAGAL baca (revert) - degradasi view, BUKAN nol; nilai lama (63) dipertahankan. DIAM.")
upd("HANAMI", {"totalSupply": 132, "freeMinted": 130, "previousTotalSupply": 132,
               "mintedInInterval": 0, "velocityLegPasses": False},
    "Run 0001 (blok 134156373): totalSupply 132 FLAT, freeMinted 130 -> velocity GAGAL. DIAM.")
upd("Zephyra", {"totalMinted": 987},
    "Run 0001 (blok 134156373): totalMinted 982->987 (+5). DIAM.")
upd("AgentNOVA", {"totalSupply": 721},
    "Run 0001 (blok 134156373): totalSupply 720->721 (+1). DIAM.")
upd("ONI", {"totalMinted": 6, "totalSupply": 6},
    "Run 0001 (blok 134156373): totalMinted 6 FLAT. DIAM.")
upd("HAPPE AGENTS", {"totalMinted": 241, "freeMinted": 222},
    "Run 0001 (blok 134156373): totalMinted 241 FLAT, freeMinted 222. DIAM.")
# Kryntar: no snapshot entry (reread-only item) - totalMinted 1369->1370 (+1), recorded in runNote0001 only.
upd("Pengu", {"totalMinted": 138, "freeMinted": 138},
    "Run 0001 (blok 134156373): totalMinted 138 FLAT, freeMinted 138. DIAM.")

# ---- Track C: RigForge + bsccat + pepe ----
rf = snap.get("track_c", {}).get("RigForge")
if rf is not None:
    rf.update({"freeSharesLeft": 626, "openedAt": 0, "freeClaimed": 374,
               "freeBooked_user": 10000000000000000000000,
               "lastReadWib": WIB, "lastReadBlock": BLK})
    rf["runNote0001_1118"] = ("Run 0001 (blok 134156373): freeSharesLeft 627->626, openedAt 0 "
        "(pool BELUM buka), freeClaimed 373->374, freeBooked(user)=10000 RIG. Tetap lead-minted-by-user, belum dibuka. DIAM.")
    print("RigForge: still not open, freeSharesLeft 626")
bs = snap.get("track_c", {}).get("bsccat")
if bs is not None:
    bs.update({"freeMinted": 519, "lastReadWib": WIB, "lastReadBlock": BLK})
    bs["runNote0001_1118"] = "Run 0001 (blok 134156373): freeMinted 519 FLAT. Tetap watchlist-only-age-unverified. DIAM."
    print("bsccat: freeMinted 519 flat")
pp = snap.get("track_c", {}).get("PEPE")
if pp is not None:
    pp.update({"lastReadWib": WIB, "lastReadBlock": BLK})
    pp["runNote0001_1118"] = ("Run 0001 (blok 134156373): freeMinted 500 (pool habis), soldShares 501, "
        "opened 0, hasMinted(user)=1. Tetap minted-by-user. DIAM.")
    print("PEPE: unchanged")

# ---- Track B pending: binanceai.fun ----
pc = snap.get("pending_claims", {}).get("binanceai.fun")
if pc is not None:
    pc.update({"launched": 0, "failed": 1, "isRefundPhase": 1,
               "tokenClaimed_user": 0, "lastReadWib": WIB})
    pc["runNote0001_1118"] = ("Run 0001 (blok 134156373): launched=0, failed=1, isRefundPhase=1, "
        "tokenClaimed(user)=0, totalShares 3110 - tetap pending/refund, sudah dilaporkan sekali (fase refund), DIAM.")
    print("binanceai pending: still launched=0, failed=1, refund=1 (no change)")

snap["last_run"] = "2026-11-18 ~00:01 WIB"
snap["last_run_wib"] = "2026-11-18 ~00:01 WIB"
snap["timestamp_wib"] = "2026-11-18 ~00:01 WIB"
snap["runNote0001"] = (
    "Run 0001 (jadwal 00:01 WIB 2026-11-18): 0 kandidat baru, 0 strong lead baru, 0 early lead baru, "
    "0 track-B dibuka, 0 track-C lead/kandidat baru. 0 PERUBAHAN dilaporkan - DIAM. "
    "Reread 40/40 OK (blok 134156373, 25,4 dtk, 141 calls, 0 chunk error; interval ~30,3 mnt vs 2331): "
    "HIVE 1263 flat; Bubblebruin 2620 FLAT, free 2614/7777=33,6%; "
    "Agent Bubble 2010->2012 (+2, 0,07/mnt, 0,13x) velocity GAGAL; free% UNVERIFIED (FREE_SUPPLY null) + umur UNVERIFIED -> bukan strong lead; "
    "PunchCard 1294->1303 (+9, 0,30/mnt vs prev 0,07 = 4,29x TAPI <20) velocity GAGAL, free 1281/5555=23,1%; "
    "Mine Card 1080->1087 (+7, 0,96x) velocity GAGAL; ALIEN 471->472 (+1) velocity GAGAL; "
    "Matrix free 588/1000=58,8%; AGCLUB free 523/888=58,9%; Ledgera free 2702/5000=54,0%; "
    "Lumenhold free 1240/1500=82,7% TERVERIFIKASI tapi umur unverified + velocity GAGAL -> bukan strong lead; "
    "JADE cost(user,1)=0,0005 BNB -> slot user TIDAK gratis; "
    "EIM 405->407; XCOPY 450->451; ARKYN 1975->1976; CPASS 1771->1773; MORFO 1087 FLAT; "
    "Kitebots 1455->1456; Zephyra 982->987; AgentNOVA 721 FLAT; Kryntar 1369->1370; SPARKS 1153->1155; "
    "PXIO-Miners 15952->16532 (+580, hot-leg focus, bukan tier); BNBG totalMinted 69 FLAT; CAT402 100/100 tetap SOLD OUT; "
    "DRAGON freeRemaining 0; RigForge openedAt 0, freeSharesLeft 626 FLAT, freeClaimed 374 FLAT; bsccat freeMinted 519 flat; "
    "PEPE pool habis, opened 0. BinanceAI pending tetap launched=0/failed=1/refund=1. "
    "Pre-flight Ankr 401 fast-fail (ke-32 berturut-turut main job, 1,0 dtk, head 134156330), "
    "watermark TETAP 134086385 (milik backfill cron); scan + 5c dilewati. "
    "Feed Sourcify 20 kontrak (top verifiedAt 17:04:48Z); 2 baru vs hot-leg 2359 sudah di-shape-check run ini "
    "(0x5feF token biasa 12 fn tanpa mint/quote/freeview/registry; 0xe4AD 105 fn quote+agent tapi tanpa mint/freeview), 0 hit S1/S2; "
    "8 lainnya baru vs 2331 sudah di-shape-check hot-leg 2314/2319/2324/2329/2334/2359 (0x10E5, 0x870c, 0x49C4, 0x7625, 0x67f0, 0x901B, 0x5900, 0x80Fc), 0 hit S1/S2. "
    "Boltbook EN 44.789 B (9 alamat) / ZH 42.810 B (9 alamat); alamat baru vs 2331 hanya rotasi front-page: "
    "AGENT COSMOS 0x3ae3 (snapshot, age-excluded), PXIO Miners 0x58e8 (watchlist, checked-not-sale-shape), "
    "registry 0x60b9 (infra, excluded), 0x7619 (dicek hot-leg 2359: 0 fn, bukan sale-shape), "
    "0xc726 (checked-not-sale-shape 23:44 WIB) - 0 lead baru. "
    "Bridge 116 kontrak, 0 outside snapshot, 7 same_owner_discarded. "
    "Sweep EN+ZH: semua sudah dikenal (Meow Cards 10 Nov - early lead 9 Nov, SUDAH age-excluded + dilaporkan sekali 13 Nov; "
    "Agentic Gangster 9 Nov, AGENT COSMOS 5 Nov, Oathbots 28 Okt, First-Dollar Grove 8 Nov, Bitcoin Frogs free 2000/2000 habis, "
    "LeadLoop/Pixel Fox/NEXUS CORE/FACE ID 25 Okt, Xuanwu Seed 25 Okt) "
    "- semuanya umur >24 jam atau pool habis (age-excluded/exhausted), 0 kandidat baru. "
    "Route 6: Odaily newsflash 200 (254.477 B, 0 pengumuman free-mint Agent ID baru), PANews 200 (110.519 B, hanya teks nav umum). "
    "LAPORAN CHAT: tidak ada (diam)."
)
json.dump(snap, open(BASE + "onchain-snapshot.json", "w"), indent=1)
print("SNAPSHOT UPDATED, last_run 00:01 WIB")
