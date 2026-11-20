#!/usr/bin/env python3
"""Merge run 2026-11-17 23:31 (free-mint-search) into the main snapshot.
Updates scalar readings + last_run fields only; does NOT delete history keys.
Interval: 2301 blok 134148514 -> 2331 blok 134152336 = 3822 blok * 0.45 dtk = ~28.7 mnt.
Hot-leg 2334 re-read after this run (AgentBubble 1866/2011, AGCLUB 523, CPASS 1772,
MORFO 1087, AgentNOVA 721, Zephyra 982) - no tier change; values below are this run's."""
import json
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
snap = json.load(open(BASE + "onchain-snapshot.json"))
BLK = 134152336
WIB = "2026-11-17 ~23:31 WIB"

def upd(name, fields, note):
    e = snap["contracts"].get(name)
    if e is None:
        print("MISSING in snapshot:", name); return False
    e.update(fields)
    e["lastReadBlock"] = BLK
    e["lastReadWib"] = WIB
    e["runNote2331_1117"] = note
    return True

upd("HIVE Agents", {"totalSupply": 1263, "balanceOf_user": 1},
    "Run 2331 (blok 134152336): totalSupply 1263 FLAT, balanceOf(user)=1, minted-by-user. DIAM.")
upd("Bubblebruin", {"totalSupply": 2620, "freeClaimed": 2614, "balanceOf_user": 1,
                    "previousTotalSupply": 2620, "mintedInInterval": 0,
                    "currentRatePerMin": 0.0, "velocityLegPasses": False,
                    "freePctVerified": 33.6},
    "Run 2331 (blok 134152336): totalSupply 2620 FLAT vs 2301 (2620), freeClaimed 2614/7777=33,6% (<70%). velocity 0. minted-by-user, bukan kandidat. DIAM.")
upd("CAT402", {"freeCatsClaimed": 100, "freeCatsRemaining": 0},
    "Run 2331 (blok 134152336): freeCatsClaimed 100/100, freeCatsRemaining 0 -> tetap SOLD OUT (sudah dilaporkan hot-leg 19:44 + run 2231). totalSupply/mintOpen revert run ini (nilai lama dipertahankan). DIAM.")
upd("JADE", {"totalSupply": 191, "freeClaimed": 188, "cost_user_1": 500000000000000},
    "Run 2331 (blok 134152336): totalSupply 191 FLAT, freeClaimed 188; cost(user,1)=0,0005 BNB -> slot user TIDAK gratis (jalur berbayar). Bukan kandidat/lead. DIAM.")
upd("Agent Bubble", {"freeMinted": 1865, "totalSupply": 2010, "totalMinted": 2010,
                     "previousTotalSupply": 1996, "mintedInInterval": 14,
                     "intervalMinutes": 28.7, "currentRatePerMin": 0.49,
                     "previousRatePerMin": 0.0, "velocityRatio": None,
                     "velocityLegPasses": False},
    "Run 2331 (blok 134152336): freeMinted 1851->1865, totalSupply 1996->2010 (+14, 0,49/mnt vs prev 0,0 = tidak terhitung, <20) -> velocity GAGAL. free% TETAP UNVERIFIED (FREE_SUPPLY null) + umur UNVERIFIED -> BUKAN strong lead. DIAM. (hot-leg 2334: 1866/2011, tanpa perubahan tier.)")
upd("DRAGON", {"freeMinted": 1000, "totalMinted": 1005, "balanceOf_user": 1},
    "Run 2331 (blok 134152336): freeMinted 1000, totalMinted 1005, balanceOf(user)=1 (minted-by-user). freeRemaining 0 (sudah diketahui). DIAM.")
upd("Matrix Agents", {"freeMinted": 588, "freeRemaining": 412, "totalSupply": 585,
                      "previousTotalSupply": 585, "mintedInInterval": 0,
                      "velocityLegPasses": False, "freePctVerified": 58.8},
    "Run 2331 (blok 134152336): freeMinted 588 FLAT, totalSupply 585 FLAT; free 588/1000=58,8% (<70%). velocity GAGAL. DIAM.")
upd("AGCLUB", {"totalMinted": 523, "freeMinted": 523, "FREE_CAP": 888,
               "velocityLegPasses": False, "freePctVerified": 58.9},
    "Run 2331 (blok 134152336): freeMinted 522->523; free 523/888=58,9% (<70%). DIAM.")
# BNBG: no snapshot entry (reread-only item) - totalMinted 69 FLAT, recorded in runNote2331 only.
upd("SPARKS", {"totalSupply": 1153},
    "Run 2331 (blok 134152336): totalSupply 1153 FLAT. DIAM.")
upd("Ledgera", {"freeClaimed": 2702, "totalSupply": 2709, "freeUsed_user": 0,
                "balanceOf_user": 0, "previousTotalSupply": 2709,
                "mintedInInterval": 0, "velocityLegPasses": False,
                "freePctVerified": 54.0},
    "Run 2331 (blok 134152336): freeClaimed 2702 FLAT, totalSupply 2709 FLAT; free 2702/5000=54,0% (<70%). velocity GAGAL. Umur UNVERIFIED. DIAM.")
upd("RaceAgents", {"totalSupply": 631, "freeMinted": 631},
    "Run 2331 (blok 134152336): totalSupply 631 FLAT, freeMinted 631. DIAM.")
upd("CPASS", {"totalMinted": 1771, "balanceOf_user": 0},
    "Run 2331 (blok 134152336): totalMinted 1770->1771 (+1). DIAM.")
upd("REOPIR", {"freeClaimed": 581, "totalSupply": 581},
    "Run 2331 (blok 134152336): freeClaimed 581 FLAT, totalSupply 581. DIAM.")
upd("RAVE", {"totalMinted": 366, "freeMinted": 366},
    "Run 2331 (blok 134152336): totalMinted 366 FLAT. DIAM.")
upd("MORFO", {"totalMinted": 1087},
    "Run 2331 (blok 134152336): totalMinted 1084->1087 (+3). DIAM.")
upd("PIXEL FROGS", {"totalSupply": 456, "freeMinted": 454, "freeLeft": 2546,
                   "mintOpen": 0, "freeClaimed_user": 0, "freePctVerified": 15.1},
    "Run 2331 (blok 134152336): totalSupply 456 FLAT, freeMinted 454, freeLeft 2546, mintOpen=0 (tutup); free 454/(454+2546)=15,1% (<70%). DIAM.")
upd("Flare Agent-bd6f", {"totalSupply": 4900},
    "Run 2331 (blok 134152336): totalSupply 4900 FLAT. DIAM.")
upd("PunchCard", {"totalSupply": 1294, "totalMinted": 1294, "freeMinted": 1276,
                  "paidMinted": 18, "previousTotalSupply": 1292,
                  "mintedInInterval": 2, "intervalMinutes": 28.7,
                  "currentRatePerMin": 0.07, "previousRatePerMin": 0.25,
                  "velocityRatio": 0.28, "velocityLegPasses": False,
                  "freePctVerified": 23.0, "mintPriceFor_user_1": 0,
                  "mintedCount_user": 0, "balanceOf_user": 0},
    "Run 2331 (blok 134152336): totalSupply 1292->1294 (+2, 0,07/mnt vs prev 0,25 = 0,28x, <20) -> velocity GAGAL. freeMinted 1274->1276; free 1276/5555=23,0% (<50% kandidat, <70% strong lead); umur UNVERIFIED -> BUKAN kandidat/strong lead. Slot user terbuka (mintPriceFor 0, mintedCount 0). DIAM.")
upd("XCOPY", {"totalSupply": 450, "totalMinted": 450, "previousTotalSupply": 447,
              "mintedInInterval": 3, "velocityLegPasses": False},
    "Run 2331 (blok 134152336): totalSupply 447->450 (+3) -> velocity GAGAL. DIAM.")
upd("ARKYN", {"totalMinted": 1975, "previousTotalSupply": 1974,
              "mintedInInterval": 1, "velocityLegPasses": False},
    "Run 2331 (blok 134152336): totalMinted 1974->1975 (+1) -> velocity GAGAL; totalSupply revert run ini. free% UNVERIFIED. DIAM.")
upd("Mine Card", {"totalSupply": 1080, "totalMinted": 1080,
                  "previousTotalSupply": 1073, "mintedInInterval": 7,
                  "intervalMinutes": 28.7, "currentRatePerMin": 0.24,
                  "previousRatePerMin": 0.50, "velocityRatio": 0.49,
                  "velocityLegPasses": False},
    "Run 2331 (blok 134152336): totalSupply 1073->1080 (+7, 0,24/mnt vs prev 0,50 = 0,49x, <20) -> velocity GAGAL. free% + umur UNVERIFIED -> BUKAN kandidat/strong lead. DIAM.")
upd("ALIEN", {"totalSupply": 471, "previousTotalSupply": 455,
              "mintedInInterval": 16, "velocityLegPasses": False},
    "Run 2331 (blok 134152336): totalSupply 455->471 (+16, 0,56/mnt - laju naik tapi <20 token) -> velocity GAGAL. free% + umur UNVERIFIED. DIAM.")
upd("Kitebots", {"totalSupply": 1455, "freeMinted": 1455, "previousTotalSupply": 1454,
                 "mintedInInterval": 1, "velocityLegPasses": False},
    "Run 2331 (blok 134152336): totalSupply 1454->1455 (+1), freeMinted 1454->1455 -> velocity GAGAL. Umur UNVERIFIED. DIAM.")
upd("Everything Is Mine (EIM)", {"totalMinted": 405, "mintOpen": 1,
                                 "velocityLegPasses": False},
    "Run 2331 (blok 134152336): totalMinted 402->405 (+3 <20) -> velocity GAGAL. free% + umur UNVERIFIED -> tetap early lead, BUKAN strong lead/kandidat. TIDAK preview/mint. DIAM.")
upd("Lumenhold", {"totalSupply": 1241, "freeClaimed": 1236,
                  "previousTotalSupply": 1239, "mintedInInterval": 2,
                  "velocityLegPasses": False, "freePctVerified": 82.4},
    "Run 2331 (blok 134152336): totalSupply 1239->1241, freeClaimed 1234->1236; free 1236/1500=82,4% TERVERIFIKASI (>70%) TAPI umur UNVERIFIED + velocity GAGAL -> BUKAN strong lead/kandidat. TIDAK dilaporkan. DIAM.")
upd("PXIO Miners", {"totalSupply": 15952, "previousTotalSupply": 15737,
                    "mintedInInterval": 215, "velocityLegPasses": False},
    "Run 2331 (blok 134152336): totalSupply 15737->15952 (+215/28,7 mnt, hot-leg focus, BUKAN di snapshot-tier; free view tetap None semua, first-seen 16 Nov 19:19 WIB (>24 jam), checked-not-sale-shape, minted-by-user). Dicatat saja, bukan tier. DIAM.")
upd("FrieAgent-B751", {"totalSupply": 9901},
    "Run 2331 (blok 134152336): totalSupply 9901 FLAT. DIAM.")
upd("FrieAgent-c64d", {"totalSupply": 4901},
    "Run 2331 (blok 134152336): totalSupply 4901 FLAT. DIAM.")
upd("Abyssora", {},
    "Run 2331 (blok 134152336): totalSupply GAGAL baca (revert) - degradasi view, BUKAN nol; nilai lama (63) dipertahankan. DIAM.")
upd("HANAMI", {"totalSupply": 132, "freeMinted": 130, "previousTotalSupply": 132,
               "mintedInInterval": 0, "velocityLegPasses": False},
    "Run 2331 (blok 134152336): totalSupply 132 FLAT, freeMinted 130 -> velocity GAGAL. DIAM.")
upd("Zephyra", {"totalMinted": 982},
    "Run 2331 (blok 134152336): totalMinted 980->982 (+2). DIAM.")
upd("AgentNOVA", {"totalSupply": 721},
    "Run 2331 (blok 134152336): totalSupply 720->721 (+1). DIAM.")
upd("ONI", {"totalMinted": 6, "totalSupply": 6},
    "Run 2331 (blok 134152336): totalMinted 6 FLAT. DIAM.")
upd("HAPPE AGENTS", {"totalMinted": 241, "freeMinted": 222},
    "Run 2331 (blok 134152336): totalMinted 241 FLAT, freeMinted 222. DIAM.")
# Kryntar: no snapshot entry (reread-only item) - totalMinted 1368->1369 (+1), recorded in runNote2331 only.
upd("Pengu", {"totalMinted": 138, "freeMinted": 138},
    "Run 2331 (blok 134152336): totalMinted 138 FLAT, freeMinted 138. DIAM.")

# ---- Track C: RigForge + bsccat + pepe ----
rf = snap.get("track_c", {}).get("RigForge")
if rf is not None:
    rf.update({"freeSharesLeft": 626, "openedAt": 0, "freeClaimed": 374,
               "freeBooked_user": 10000000000000000000000,
               "lastReadWib": WIB, "lastReadBlock": BLK})
    rf["runNote2331_1117"] = ("Run 2331 (blok 134152336): freeSharesLeft 627->626, openedAt 0 "
        "(pool BELUM buka), freeClaimed 373->374, freeBooked(user)=10000 RIG. Tetap lead-minted-by-user, belum dibuka. DIAM.")
    print("RigForge: still not open, freeSharesLeft 626")
bs = snap.get("track_c", {}).get("bsccat")
if bs is not None:
    bs.update({"freeMinted": 519, "lastReadWib": WIB, "lastReadBlock": BLK})
    bs["runNote2331_1117"] = "Run 2331 (blok 134152336): freeMinted 519 FLAT. Tetap watchlist-only-age-unverified. DIAM."
    print("bsccat: freeMinted 519 flat")
pp = snap.get("track_c", {}).get("PEPE")
if pp is not None:
    pp.update({"lastReadWib": WIB, "lastReadBlock": BLK})
    pp["runNote2331_1117"] = ("Run 2331 (blok 134152336): freeMinted 500 (pool habis), soldShares 501, "
        "opened 0, hasMinted(user)=1. Tetap minted-by-user. DIAM.")
    print("PEPE: unchanged")

# ---- Track B pending: binanceai.fun ----
pc = snap.get("pending_claims", {}).get("binanceai.fun")
if pc is not None:
    pc.update({"launched": 0, "failed": 1, "isRefundPhase": 1,
               "tokenClaimed_user": 0, "lastReadWib": WIB})
    pc["runNote2331_1117"] = ("Run 2331 (blok 134152336): launched=0, failed=1, isRefundPhase=1, "
        "tokenClaimed(user)=0, totalShares 3110 - tetap pending/refund, sudah dilaporkan sekali (fase refund), DIAM.")
    print("binanceai pending: still launched=0, failed=1, refund=1 (no change)")

snap["last_run"] = "2026-11-17 ~23:31 WIB"
snap["last_run_wib"] = "2026-11-17 ~23:31 WIB"
snap["timestamp_wib"] = "2026-11-17 ~23:31 WIB"
snap["runNote2331"] = (
    "Run 2331 (jadwal 23:31 WIB): 0 kandidat baru, 0 strong lead baru, 0 early lead baru, "
    "0 track-B dibuka, 0 track-C lead/kandidat baru. 0 PERUBAHAN dilaporkan - DIAM. "
    "Reread 40/40 OK (blok 134152336, 46,7 dtk, 141 calls, 0 chunk error; interval ~28,7 mnt vs 2301): "
    "HIVE 1263 flat; Bubblebruin 2620 FLAT, free 2614/7777=33,6%; "
    "Agent Bubble 1996->2010 (+14, 0,49/mnt, <20) velocity GAGAL; free% UNVERIFIED (FREE_SUPPLY null) + umur UNVERIFIED -> bukan strong lead; "
    "PunchCard 1292->1294 (+2, 0,28x) velocity GAGAL, free 1276/5555=23,0%; "
    "Mine Card 1073->1080 (+7, 0,49x) velocity GAGAL; ALIEN 455->471 (+16, <20) velocity GAGAL; "
    "Matrix free 588/1000=58,8%; AGCLUB free 523/888=58,9%; Ledgera free 2702/5000=54,0%; "
    "Lumenhold free 1236/1500=82,4% TERVERIFIKASI tapi umur unverified + velocity GAGAL -> bukan strong lead; "
    "JADE cost(user,1)=0,0005 BNB -> slot user TIDAK gratis; "
    "EIM 402->405; XCOPY 447->450; ARKYN 1974->1975; CPASS 1770->1771; MORFO 1084->1087; "
    "Kitebots 1454->1455; Zephyra 980->982; AgentNOVA 720->721; Kryntar 1368->1369; "
    "PXIO-Miners 15737->15952 (+215, hot-leg focus, bukan tier); BNBG totalMinted 69 FLAT; Kryntar 1368->1369; CAT402 100/100 tetap SOLD OUT; "
    "DRAGON freeRemaining 0; RigForge openedAt 0, freeSharesLeft 627->626, freeClaimed 373->374; bsccat freeMinted 519 flat; "
    "PEPE pool habis, opened 0. BinanceAI pending tetap launched=0/failed=1/refund=1. "
    "Pre-flight Ankr 401 fast-fail (ke-31 berturut-turut main job, 1,3 dtk, head 134152288), "
    "watermark TETAP 134086385 (milik backfill cron); scan + 5c dilewati. "
    "Feed Sourcify 20 kontrak (top verifiedAt 16:31:35Z); baru vs 2301 sudah di-shape-check hot-leg 2314/2319/2324/2329/2334 "
    "(0xe68A, 0x80Fc, 0x1191, 0xFcd0, 0x1922, 0xb979, 0x3D6c, 0xeC93, 0x1e20, 0xCFF0, 0xB447, 0x5Ebb, 0xB750), 0 hit S1/S2; "
    "0xae83 dicek run ini: ERC-20 pajak biasa (62 fn, tanpa mint/quote/freeview/registry) - checked-not-sale-shape. "
    "Boltbook EN 45.028 B (12 alamat) / ZH 43.324 B (14 alamat); alamat baru vs 2301 hanya rotasi front-page: "
    "EIM 0x1fcc (sudah di watchlist), AGENT COSMOS 0x3aed (snapshot, age-excluded), Agentic Gangster 0x0a2a (snapshot, age-excluded), "
    "Lumenhold 0x9701 (watchlist), 0x6ac0/0x851a/0xf4ba/0xf7c1 (sudah di snapshot/hot-seen), "
    "0x7a23 (85 fn: mint+freeview tapi TANPA quote + TANPA registry/AgentGate -> S1/S2 false, checked-not-sale-shape), "
    "0xecbd (ABI kosong di Sourcify, tidak bisa verifikasi agent-shape - log saja) - 0 lead baru. "
    "Bridge 116 kontrak, 0 outside snapshot, 7 same_owner_discarded. "
    "Sweep EN+ZH: semua sudah dikenal (Oathbots 28 Okt, Agentic Gangster 9 Nov, RIGBYPASS 10 Nov, AGENT COSMOS 5 Nov, "
    "MOLT 6 Nov, First-Dollar Grove, Agent Zet free phase complete, Bitcoin Frogs free 2000/2000 habis, Subsonic Tribe 26 Okt) "
    "- semuanya umur >24 jam atau pool habis (age-excluded/exhausted), 0 kandidat baru. "
    "Route 6: Odaily newsflash 200 (0 pengumuman free-mint Agent ID baru), PANews 200 (hanya teks nav umum). "
    "LAPORAN CHAT: tidak ada (diam)."
)
json.dump(snap, open(BASE + "onchain-snapshot.json", "w"), indent=1)
print("SNAPSHOT UPDATED, last_run 23:31 WIB")
