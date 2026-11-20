#!/usr/bin/env python3
"""Merge run 2026-11-17 23:01 (free-mint-search) into the main snapshot.
Updates scalar readings + last_run fields only; does NOT delete history keys.
Bold Leonidas already removed in 2231 merge (sold out) - NOT re-added.
Interval: 2231 blok 134145823 -> 2301 blok 134148514 = 2691 blok * 0.45 dtk = ~20.2 mnt."""
import json
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
snap = json.load(open(BASE + "onchain-snapshot.json"))
BLK = 134148514
WIB = "2026-11-17 ~23:01 WIB"

def upd(name, fields, note):
    e = snap["contracts"].get(name)
    if e is None:
        print("MISSING in snapshot:", name); return False
    e.update(fields)
    e["lastReadBlock"] = BLK
    e["lastReadWib"] = WIB
    e["runNote2301_1117"] = note
    return True

upd("HIVE Agents", {"totalSupply": 1263, "balanceOf_user": 1},
    "Run 2301 (blok 134148514): totalSupply 1263 FLAT, balanceOf(user)=1, minted-by-user. DIAM.")
upd("Bubblebruin", {"totalSupply": 2620, "freeClaimed": 2614, "balanceOf_user": 1,
                    "previousTotalSupply": 2620, "mintedInInterval": 0,
                    "currentRatePerMin": 0.0, "velocityLegPasses": False,
                    "freePctVerified": 33.6},
    "Run 2301 (blok 134148514): totalSupply 2620 FLAT vs 2231 (2620), freeClaimed 2614/7777=33,6% (<70%). velocity 0. minted-by-user, bukan kandidat. DIAM.")
upd("CAT402", {"freeCatsClaimed": 100, "freeCatsRemaining": 0},
    "Run 2301 (blok 134148514): freeCatsClaimed 100/100, freeCatsRemaining 0 -> tetap SOLD OUT (sudah dilaporkan hot-leg 19:44 + run 2231). totalSupply/mintOpen revert run ini (nilai lama dipertahankan). DIAM.")
upd("JADE", {"totalSupply": 191, "freeClaimed": 188, "cost_user_1": 500000000000000},
    "Run 2301 (blok 134148514): totalSupply 191 FLAT, freeClaimed 188; cost(user,1)=0,0005 BNB (500000000000000 wei) -> slot user TIDAK gratis (jalur berbayar). Bukan kandidat/lead. DIAM.")
upd("AgentBubble", {"freeMinted": 1851, "totalSupply": 1996, "totalMinted": 1996,
                    "previousTotalSupply": 1996, "mintedInInterval": 0,
                    "velocityLegPasses": False},
    "Run 2301 (blok 134148514): freeMinted 1851 FLAT, totalSupply 1996 FLAT. velocity GAGAL. DIAM.")
upd("DRAGON", {"freeMinted": 1000, "totalMinted": 1005, "balanceOf_user": 1},
    "Run 2301 (blok 134148514): freeMinted 1000, totalMinted 1005, balanceOf(user)=1 (minted-by-user). freeRemaining 0 (sudah diketahui). DIAM.")
upd("Matrix Agents", {"freeMinted": 588, "freeRemaining": 412, "totalSupply": 585,
                      "previousTotalSupply": 583, "mintedInInterval": 2,
                      "velocityLegPasses": False, "freePctVerified": 58.8},
    "Run 2301 (blok 134148514): freeMinted 587->588, totalSupply 583->585 (+2 <20); free 588/1000=58,8% (<70%). velocity GAGAL. DIAM.")
upd("AGCLUB", {"totalMinted": 522, "freeMinted": 522, "FREE_CAP": 888,
               "velocityLegPasses": False, "freePctVerified": 58.8},
    "Run 2301 (blok 134148514): freeMinted 522 FLAT; free 522/888=58,8% (<70%). DIAM.")
upd("BNBG", {"totalMinted": 69},
    "Run 2301 (blok 134148514): totalMinted 69 FLAT. DIAM.")
upd("SPARKS", {"totalSupply": 1153},
    "Run 2301 (blok 134148514): totalSupply 1152->1153 (+1). DIAM.")
upd("Ledgera", {"freeClaimed": 2702, "totalSupply": 2709, "freeUsed_user": 0,
                "balanceOf_user": 0, "previousTotalSupply": 2706,
                "mintedInInterval": 3, "velocityLegPasses": False,
                "freePctVerified": 54.0},
    "Run 2301 (blok 134148514): freeClaimed 2699->2702, totalSupply 2706->2709 (+3 <20); free 2702/5000=54,0% (<70%). velocity GAGAL. Umur UNVERIFIED. DIAM.")
upd("RaceAgents", {"totalSupply": 631, "freeMinted": 631},
    "Run 2301 (blok 134148514): totalSupply 631 FLAT, freeMinted 631. DIAM.")
upd("CPASS", {"totalMinted": 1770, "balanceOf_user": 0},
    "Run 2301 (blok 134148514): totalMinted 1770 FLAT. DIAM.")
upd("REOPIR", {"freeClaimed": 581, "totalSupply": 581},
    "Run 2301 (blok 134148514): freeClaimed 581 FLAT, totalSupply 581. DIAM.")
upd("RAVE", {"totalMinted": 366, "freeMinted": 366},
    "Run 2301 (blok 134148514): totalMinted 366 FLAT. DIAM.")
upd("MORFO", {"totalMinted": 1084},
    "Run 2301 (blok 134148514): totalMinted 1083->1084 (+1). DIAM.")
upd("PIXELFROGS", {"totalSupply": 456, "freeMinted": 454, "freeLeft": 2546,
                   "mintOpen": 0, "freeClaimed_user": 0, "freePctVerified": 15.1},
    "Run 2301 (blok 134148514): totalSupply 456 FLAT, freeMinted 454, freeLeft 2546, mintOpen=0 (tutup); free 454/(454+2546)=15,1% (<70%). DIAM.")
upd("Flare-bd6f", {"totalSupply": 4900},
    "Run 2301 (blok 134148514): totalSupply 4900 FLAT. DIAM.")
upd("PunchCard", {"totalSupply": 1292, "totalMinted": 1292, "freeMinted": 1274,
                  "paidMinted": 18, "previousTotalSupply": 1287,
                  "mintedInInterval": 5, "intervalMinutes": 20.2,
                  "currentRatePerMin": 0.25, "previousRatePerMin": 0.76,
                  "velocityRatio": 0.33, "velocityLegPasses": False,
                  "freePctVerified": 22.9, "mintPriceFor_user_1": 0,
                  "mintedCount_user": 0, "balanceOf_user": 0},
    "Run 2301 (blok 134148514): totalSupply 1287->1292 (+5, 0,25/mnt vs prev 0,76 = 0,33x, <20) -> velocity GAGAL (2231 LOLOS, kini gagal). freeMinted 1269->1274; free 1274/5555=22,9% (<50% kandidat, <70% strong lead); umur UNVERIFIED -> BUKAN kandidat/strong lead. Slot user terbuka (mintPriceFor 0, mintedCount 0). DIAM.")
upd("XCOPY", {"totalSupply": 447, "totalMinted": 447, "previousTotalSupply": 445,
              "mintedInInterval": 2, "velocityLegPasses": False},
    "Run 2301 (blok 134148514): totalSupply 445->447 (+2) -> velocity GAGAL. DIAM.")
upd("ARKYN", {"totalMinted": 1974, "previousTotalSupply": 1969,
              "mintedInInterval": 5, "velocityLegPasses": False},
    "Run 2301 (blok 134148514): totalMinted 1969->1974 (+5 <20) -> velocity GAGAL; totalSupply revert run ini. free% UNVERIFIED. DIAM.")
upd("Mine Card", {"totalSupply": 1073, "totalMinted": 1073,
                  "previousTotalSupply": 1063, "mintedInInterval": 10,
                  "intervalMinutes": 20.2, "currentRatePerMin": 0.50,
                  "previousRatePerMin": 0.95, "velocityRatio": 0.52,
                  "velocityLegPasses": False},
    "Run 2301 (blok 134148514): totalSupply 1063->1073 (+10, 0,50/mnt vs prev 0,95 = 0,52x, <20) -> velocity GAGAL (2231 LOLOS, kini gagal). free% + umur UNVERIFIED -> BUKAN kandidat/strong lead. DIAM.")
upd("ALIEN", {"totalSupply": 455, "previousTotalSupply": 454,
              "mintedInInterval": 1, "velocityLegPasses": False},
    "Run 2301 (blok 134148514): totalSupply 454->455 (+1) -> velocity GAGAL. DIAM.")
upd("Kitebots", {"totalSupply": 1454, "freeMinted": 1454, "previousTotalSupply": 1454,
                 "mintedInInterval": 0, "velocityLegPasses": False},
    "Run 2301 (blok 134148514): totalSupply 1454 FLAT, freeMinted 1454 -> velocity GAGAL. Umur UNVERIFIED. DIAM.")
upd("Everything Is Mine (EIM)", {"totalMinted": 402, "mintOpen": 1,
                                 "velocityLegPasses": False},
    "Run 2301 (blok 134148514): totalMinted 400->402 (+2 <20) -> velocity GAGAL. free% + umur UNVERIFIED -> tetap early lead, BUKAN strong lead/kandidat. TIDAK preview/mint. DIAM.")
upd("Lumenhold", {"totalSupply": 1239, "freeClaimed": 1234,
                  "previousTotalSupply": 1238, "mintedInInterval": 1,
                  "velocityLegPasses": False, "freePctVerified": 82.3},
    "Run 2301 (blok 134148514): totalSupply 1238->1239, freeClaimed 1233->1234; free 1234/1500=82,3% TERVERIFIKASI (>70%) TAPI umur UNVERIFIED + velocity GAGAL -> BUKAN strong lead/kandidat. TIDAK dilaporkan. DIAM.")
upd("PXIO Miners", {"totalSupply": 15737, "previousTotalSupply": 15590,
                    "mintedInInterval": 147, "velocityLegPasses": False},
    "Run 2301 (blok 134148514): totalSupply 15590->15737 (+147/20,2 mnt, hot-leg focus, BUKAN di snapshot-tier; free view tetap None semua, first-seen 16 Nov 19:19 WIB (>24 jam), checked-not-sale-shape, minted-by-user). Dicatat saja, bukan tier. DIAM.")
upd("FrieAgent-B751", {"totalSupply": 9901},
    "Run 2301 (blok 134148514): totalSupply 9901 FLAT. DIAM.")
upd("FrieAgent-c64d", {"totalSupply": 4901},
    "Run 2301 (blok 134148514): totalSupply 4901 FLAT. DIAM.")
upd("Abyssora", {},
    "Run 2301 (blok 134148514): totalSupply GAGAL baca (revert) - degradasi view, BUKAN nol; nilai lama (63) dipertahankan. DIAM.")
upd("HANAMI", {"totalSupply": 132, "freeMinted": 130, "previousTotalSupply": 132,
               "mintedInInterval": 0, "velocityLegPasses": False},
    "Run 2301 (blok 134148514): totalSupply 132 FLAT, freeMinted 130 -> velocity GAGAL. DIAM.")
upd("Zephyra", {"totalMinted": 980},
    "Run 2301 (blok 134148514): totalMinted 978->980 (+2). DIAM.")
upd("AgentNOVA", {"totalSupply": 720},
    "Run 2301 (blok 134148514): totalSupply 720 FLAT. DIAM.")
upd("ONI", {"totalMinted": 6, "totalSupply": 6},
    "Run 2301 (blok 134148514): totalMinted 6 FLAT. DIAM.")
upd("HAPPE", {"totalMinted": 241, "freeMinted": 222},
    "Run 2301 (blok 134148514): totalMinted 241 FLAT, freeMinted 222. DIAM.")
upd("Kryntar", {"totalMinted": 1368},
    "Run 2301 (blok 134148514): totalMinted 1368 FLAT. DIAM.")
upd("Pengu", {"totalMinted": 138, "freeMinted": 138},
    "Run 2301 (blok 134148514): totalMinted 138 FLAT, freeMinted 138. DIAM.")

# ---- Track C: RigForge + bsccat + pepe ----
rf = snap.get("track_c", {}).get("RigForge")
if rf is not None:
    rf.update({"freeSharesLeft": 627, "openedAt": 0, "freeClaimed": 373,
               "freeBooked_user": 10000000000000000000000,
               "lastReadWib": WIB, "lastReadBlock": BLK})
    rf["runNote2301_1117"] = ("Run 2301 (blok 134148514): freeSharesLeft 627 FLAT, openedAt 0 "
        "(pool BELUM buka), freeClaimed 373, freeBooked(user)=10000 RIG. Tetap lead-minted-by-user, belum dibuka. DIAM.")
    print("RigForge: still not open, freeSharesLeft 627 flat")
bs = snap.get("track_c", {}).get("bsccat")
if bs is not None:
    bs.update({"freeMinted": 519, "lastReadWib": WIB, "lastReadBlock": BLK})
    bs["runNote2301_1117"] = "Run 2301 (blok 134148514): freeMinted 519 FLAT. Tetap watchlist-only-age-unverified. DIAM."
    print("bsccat: freeMinted 519 flat")
pp = snap.get("track_c", {}).get("PEPE")
if pp is not None:
    pp.update({"lastReadWib": WIB, "lastReadBlock": BLK})
    pp["runNote2301_1117"] = ("Run 2301 (blok 134148514): freeMinted 500 (pool habis), soldShares 501, "
        "opened 0, hasMinted(user)=1. Tetap minted-by-user. DIAM.")
    print("PEPE: unchanged")

# ---- Track B pending: binanceai.fun ----
pc = snap.get("pending_claims", {}).get("binanceai.fun")
if pc is not None:
    pc.update({"launched": 0, "failed": 1, "isRefundPhase": 1,
               "tokenClaimed_user": 0, "lastReadWib": WIB})
    pc["runNote2301_1117"] = ("Run 2301 (blok 134148514): launched=0, failed=1, isRefundPhase=1, "
        "tokenClaimed(user)=0, totalShares 3110 - tetap pending/refund, sudah dilaporkan sekali (fase refund), DIAM.")
    print("binanceai pending: still launched=0, failed=1, refund=1 (no change)")

snap["last_run"] = "2026-11-17 ~23:01 WIB"
snap["last_run_wib"] = "2026-11-17 ~23:01 WIB"
snap["timestamp_wib"] = "2026-11-17 ~23:01 WIB"
snap["runNote2301"] = (
    "Run 2301 (jadwal 23:01 WIB): 0 kandidat baru, 0 strong lead baru, 0 early lead baru, "
    "0 track-B dibuka, 0 track-C lead/kandidat baru. 0 PERUBAHAN dilaporkan - DIAM. "
    "Reread 40/40 OK (blok 134148514, 47,3 dtk, 141 calls, 0 chunk error; interval ~20,2 mnt vs 2231): "
    "HIVE 1263 flat; Bubblebruin 2620 FLAT, free 2614/7777=33,6%; "
    "PunchCard 1287->1292 (+5, velocity GAGAL 0,33x - 2231 LOLOS, kini gagal), free 1274/5555=22,9%; "
    "Mine Card 1063->1073 (+10, velocity GAGAL 0,52x - 2231 LOLOS, kini gagal); "
    "Matrix free 588/1000=58,8%; AGCLUB free 522/888=58,8%; Ledgera free 2702/5000=54,0%; "
    "Lumenhold free 1234/1500=82,3% TERVERIFIKASI tapi umur unverified + velocity GAGAL -> bukan strong lead; "
    "JADE cost(user,1)=0,0005 BNB -> slot user TIDAK gratis; "
    "EIM totalMinted 400->402; XCOPY 445->447; ARKYN 1969->1974; ALIEN 454->455; Zephyra 978->980; "
    "PXIO-Miners 15590->15737 (+147, hot-leg focus, bukan tier); CAT402 100/100 tetap SOLD OUT; "
    "DRAGON freeRemaining 0; RigForge openedAt 0, freeSharesLeft 627 flat; bsccat freeMinted 519 flat; "
    "PEPE pool habis, opened 0. BinanceAI pending tetap launched=0/failed=1/refund=1. "
    "Pre-flight Ankr 401 fast-fail (ke-30 berturut-turut main job, 3,2 dtk, head 134148433), "
    "watermark TETAP 134086385 (milik backfill cron); scan + 5c dilewati. "
    "Feed Sourcify 20 kontrak (top verifiedAt 16:00:49Z), 6 baru vs 2231 (0x814c, 0xff60, 0xC239, 0x04dd, 0x1754, 0x8ef1) "
    "- semuanya sudah di-shape-check hot-leg 2254/2259, 0 hit S1/S2 (checked-not-sale-shape). "
    "Boltbook EN 45.373 B / ZH 43.592 B, 6/6 alamat; baru vs 2231: 0x4158 (LumenFindings, age-excluded 14 Nov), "
    "0xA0D8 + 0x3ae3 + 0x9a16 (sudah checked-not-sale-shape hot-leg, 11 Nov) + 0x8269 (checked-not-lead 11 Nov) - 0 lead baru. "
    "Bridge 116 kontrak, 0 outside snapshot, 7 same_owner_discarded. "
    "Sweep EN+ZH: semua sudah dikenal (Oathbots, Meow Cards, Agentic Gangster, AGENT COSMOS, Subsonic Tribe, "
    "BAS Medium, daftar 22 proyek 27 Okt); NEXUS CORE 0xa477 (post 25 Okt) tidak di snapshot tapi umur ~23 hari "
    "(age-excluded) + tanpa situs resmi - dicatat saja, tidak dilaporkan. "
    "Odaily newsflash: hanya berita makro (tokenisasi obligasi UK), 0 pengumuman free-mint Agent ID baru. "
    "LAPORAN CHAT: tidak ada (diam)."
)
json.dump(snap, open(BASE + "onchain-snapshot.json", "w"), indent=1)
print("SNAPSHOT UPDATED, last_run 23:01 WIB")
