#!/usr/bin/env python3
"""Merge run 2026-11-17 22:31 (free-mint-search) into the main snapshot.
Updates scalar readings + last_run fields only; does NOT delete history keys,
EXCEPT Bold Leonidas (sold out, verified) which is removed from contracts
per the early-lead sellout rule, with removal evidence kept top-level.
Koreksi baseline: snapshot PunchCard/Bubblebruin tertinggal dari 2131 -
nilai 2201 yang benar dipakai sebagai baseline interval ini."""
import json
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
snap = json.load(open(BASE + "onchain-snapshot.json"))
BLK = 134145823
WIB = "2026-11-17 ~22:31 WIB"
# Interval A: last read 22:01 blok 134140699 -> 5124 blok * 0.45 dtk = 38.4 mnt
# Interval B: last read 21:31 blok 134136283 -> 9540 blok * 0.45 dtk = 71.6 mnt

def upd(name, fields, note):
    e = snap["contracts"].get(name)
    if e is None:
        print("MISSING in snapshot:", name); return False
    e.update(fields)
    e["lastReadBlock"] = BLK
    e["lastReadWib"] = WIB
    e["runNote2231_1117"] = note
    return True

upd("HIVE Agents", {"totalSupply": 1263, "balanceOf_user": 1},
    "Run 2231 (blok 134145823): totalSupply 1263 FLAT, balanceOf(user)=1, minted-by-user. DIAM.")
upd("Bubblebruin", {"totalSupply": 2620, "freeClaimed": 2614, "balanceOf_user": 1,
                    "previousTotalSupply": 2620, "mintedInInterval": 0,
                    "currentRatePerMin": 0.0, "velocityLegPasses": False,
                    "freePctVerified": 33.6},
    "Run 2231 (blok 134145823): totalSupply 2620 FLAT vs reread 2201 (2620); snapshot 2530 tertinggal dari 2131, DIKOREKSI. freeClaimed 2614/7777=33,6% (<70%). velocity 0. minted-by-user, bukan kandidat. DIAM.")
upd("CAT402", {"freeCatsClaimed": 100, "freeCatsRemaining": 0, "totalCatsMinted": 100,
               "status": "sold-out-2026-11-17"},
    "Run 2231 (blok 134145823): freeCatsClaimed 100/100, freeCatsRemaining 0 -> tetap SOLD OUT (sudah dilaporkan hot-leg 19:44). totalSupply/mintOpen revert run ini (nilai lama dipertahankan). DIAM.")
upd("JADE", {"totalSupply": 191, "freeClaimed": 188},
    "Run 2231 (blok 134145823): totalSupply 191 FLAT, freeClaimed 188. DIAM.")
upd("AgentBubble", {"freeMinted": 1851, "totalSupply": 1996, "totalMinted": 1996,
                    "previousTotalSupply": 1995, "mintedInInterval": 1,
                    "velocityLegPasses": False},
    "Run 2231 (blok 134145823): freeMinted 1850->1851, totalSupply 1995->1996 (+1). free% vs MAX inferensi 83,3% (bukan counter gratis terverifikasi); umur UNVERIFIED -> bukan strong lead. DIAM.")
upd("DRAGON", {"freeMinted": 1000, "totalMinted": 1005, "balanceOf_user": 1},
    "Run 2231 (blok 134145823): freeMinted 1000, totalMinted 1005, balanceOf(user)=1 (minted-by-user). freeRemaining 0 (sudah diketahui). DIAM.")
upd("Matrix Agents", {"freeMinted": 587, "freeRemaining": 413, "totalSupply": 583,
                      "previousTotalSupply": 583, "mintedInInterval": 0,
                      "velocityLegPasses": False, "freePctVerified": 58.7},
    "Run 2231 (blok 134145823): freeMinted 586->587, free 587/1000=58,7% (<70%). velocity GAGAL. DIAM.")
upd("AGCLUB", {"totalMinted": 522, "freeMinted": 522, "FREE_CAP": 888,
               "velocityLegPasses": False, "freePctVerified": 58.8},
    "Run 2231 (blok 134145823): freeMinted 522 FLAT; free 522/888=58,8% (<70%). DIAM.")
upd("BNBG", {"totalMinted": 69},
    "Run 2231 (blok 134145823): totalMinted 69. DIAM.")
upd("SPARKS", {"totalSupply": 1152},
    "Run 2231 (blok 134145823): totalSupply 1152 (+1 vs 1151 hot-leg 2229). DIAM.")
upd("Ledgera", {"freeClaimed": 2699, "totalSupply": 2706, "freeUsed_user": 0,
                "balanceOf_user": 0, "previousTotalSupply": 2703,
                "mintedInInterval": 3, "velocityLegPasses": False,
                "freePctVerified": 54.0},
    "Run 2231 (blok 134145823): freeClaimed 2696->2699, totalSupply 2703->2706 (+3); free 2699/5000=54,0% (<70%). velocity GAGAL. Umur UNVERIFIED. DIAM.")
upd("RaceAgents", {"totalSupply": 631, "freeMinted": 631},
    "Run 2231 (blok 134145823): totalSupply 631 FLAT, freeMinted 631. DIAM.")
upd("CPASS", {"totalMinted": 1770, "balanceOf_user": 0},
    "Run 2231 (blok 134145823): totalMinted 1770. DIAM.")
upd("REOPIR", {"freeClaimed": 581, "totalSupply": 581},
    "Run 2231 (blok 134145823): freeClaimed 581 FLAT, totalSupply 581. DIAM.")
upd("RAVE", {"totalMinted": 366, "freeMinted": 366},
    "Run 2231 (blok 134145823): totalMinted 366 FLAT. DIAM.")
upd("MORFO", {"totalMinted": 1083},
    "Run 2231 (blok 134145823): totalMinted 1083 (+1 vs 1082 hot-leg 2234). DIAM.")
upd("PIXELFROGS", {"totalSupply": 456, "freeMinted": 454, "freeLeft": 2546,
                   "mintOpen": 0, "freeClaimed_user": 0, "freePctVerified": 15.1},
    "Run 2231 (blok 134145823): totalSupply 456, freeMinted 454, freeLeft 2546, mintOpen=0 (tutup); free 454/(454+2546)=15,1% (<70%). DIAM.")
upd("Flare-bd6f", {"totalSupply": 4900},
    "Run 2231 (blok 134145823): totalSupply 4900 FLAT. DIAM.")
upd("PunchCard", {"totalSupply": 1287, "totalMinted": 1287, "freeMinted": 1269,
                  "paidMinted": 18, "previousTotalSupply": 1258,
                  "mintedInInterval": 29, "intervalMinutes": 38.4,
                  "currentRatePerMin": 0.76, "previousRatePerMin": 0.27,
                  "velocityRatio": 2.8, "velocityLegPasses": True,
                  "freePctVerified": 22.8, "mintPriceFor_user_1": 0,
                  "mintedCount_user": 0, "balanceOf_user": 0},
    "Run 2231 (blok 134145823): totalSupply 1258->1287 (+29, 0,76/mnt vs prev 0,27 = 2,8x, >=20) -> velocity LOLOS. freeMinted 1240->1269; free 1269/5555=22,8% (<50% kandidat, <70% strong lead); umur UNVERIFIED -> BUKAN kandidat/strong lead. Slot user terbuka (mintPriceFor 0, mintedCount 0). DIAM, dicatat saja.")
upd("XCOPY", {"totalSupply": 445, "totalMinted": 445, "previousTotalSupply": 443,
              "mintedInInterval": 2, "velocityLegPasses": False},
    "Run 2231 (blok 134145823): totalSupply 443->445 (+2) -> velocity GAGAL. DIAM.")
upd("ARKYN", {"totalMinted": 1969, "previousTotalSupply": 1963,
              "mintedInInterval": 6, "velocityLegPasses": False},
    "Run 2231 (blok 134145823): totalMinted 1963->1969 (+6 <20) -> velocity GAGAL; totalSupply revert run ini. free% UNVERIFIED. DIAM.")
upd("Mine Card", {"totalSupply": 1063, "totalMinted": 1063,
                  "previousTotalSupply": 995, "mintedInInterval": 68,
                  "intervalMinutes": 71.6, "currentRatePerMin": 0.95,
                  "previousRatePerMin": 0.40, "velocityRatio": 2.4,
                  "velocityLegPasses": True},
    "Run 2231 (blok 134145823): totalSupply 995->1063 (+68 dalam ~71,6 mnt, 0,95/mnt vs prev 0,40 = 2,4x, >=20) -> velocity LOLOS. free% + umur UNVERIFIED -> BUKAN kandidat/strong lead. DIAM, dicatat saja.")
upd("ALIEN", {"totalSupply": 454, "previousTotalSupply": 454,
              "mintedInInterval": 0, "velocityLegPasses": False},
    "Run 2231 (blok 134145823): totalSupply 454 FLAT -> velocity GAGAL. DIAM.")
upd("Kitebots", {"totalSupply": 1454, "freeMinted": 1454, "previousTotalSupply": 1453,
                 "mintedInInterval": 1, "velocityLegPasses": False},
    "Run 2231 (blok 134145823): totalSupply 1453->1454 (+1), freeMinted 1454 -> velocity GAGAL. Umur UNVERIFIED. DIAM.")
upd("Everything Is Mine (EIM)", {"totalMinted": 400, "mintOpen": 1,
                                 "velocityLegPasses": False},
    "Run 2231 (blok 134145823): totalMinted 394->400 (+6 <20) -> velocity GAGAL (bacaan ke-2, baseline). free% + umur UNVERIFIED -> tetap early lead, BUKAN strong lead/kandidat. TIDAK preview/mint. DIAM.")
upd("Lumenhold", {"totalSupply": 1238, "freeClaimed": 1233,
                  "previousTotalSupply": 1237, "mintedInInterval": 1,
                  "velocityLegPasses": False, "freePctVerified": 82.2},
    "Run 2231 (blok 134145823): totalSupply 1237->1238, freeClaimed 1232->1233; free 1233/1500=82,2% TERVERIFIKASI (>70%) TAPI umur UNVERIFIED + velocity GAGAL -> BUKAN strong lead/kandidat. TIDAK dilaporkan. DIAM.")
upd("PXIO Miners", {"totalSupply": 15590, "previousTotalSupply": 14872,
                    "mintedInInterval": 718, "velocityLegPasses": False},
    "Run 2231 (blok 134145823): totalSupply 14872->15590 (+718/71,6 mnt, hot-leg focus, BUKAN di snapshot-tier; free view tetap None semua, first-seen 16 Nov 19:19 WIB (>24 jam), checked-not-sale-shape, minted-by-user). Dicatat saja, bukan tier. DIAM.")
upd("FrieAgent-B751", {"totalSupply": 9901},
    "Run 2231 (blok 134145823): totalSupply 9901 FLAT. DIAM.")
upd("FrieAgent-c64d", {"totalSupply": 4901},
    "Run 2231 (blok 134145823): totalSupply 4901 FLAT. DIAM.")
upd("Abyssora", {},
    "Run 2231 (blok 134145823): totalSupply GAGAL baca (revert) - degradasi view, BUKAN nol; nilai lama (63) dipertahankan. DIAM.")
upd("HANAMI", {"totalSupply": 132, "freeMinted": 130, "previousTotalSupply": 132,
               "mintedInInterval": 0, "velocityLegPasses": False},
    "Run 2231 (blok 134145823): totalSupply 132 FLAT, freeMinted 130 -> velocity GAGAL. DIAM.")
upd("Zephyra", {"totalMinted": 978},
    "Run 2231 (blok 134145823): totalMinted 978 FLAT. DIAM.")
upd("AgentNOVA", {"totalSupply": 720},
    "Run 2231 (blok 134145823): totalSupply 720. DIAM.")
upd("ONI", {"totalMinted": 6, "totalSupply": 6},
    "Run 2231 (blok 134145823): totalMinted 6. DIAM.")
upd("HAPPE", {"totalMinted": 241, "freeMinted": 222},
    "Run 2231 (blok 134145823): totalMinted 241, freeMinted 222. DIAM.")
upd("Kryntar", {"totalMinted": 1368},
    "Run 2231 (blok 134145823): totalMinted 1368. DIAM.")
upd("Pengu", {"totalMinted": 138, "freeMinted": 138},
    "Run 2231 (blok 134145823): totalMinted 138, freeMinted 138. DIAM.")

# ---- Track C: RigForge + bsccat + pepe ----
rf = snap.get("track_c", {}).get("RigForge")
if rf is not None:
    rf.update({"freeSharesLeft": 627, "openedAt": 0, "freeClaimed": 373,
               "freeBooked_user": 10000000000000000000000,
               "lastReadWib": WIB, "lastReadBlock": BLK})
    rf["runNote2231_1117"] = ("Run 2231 (blok 134145823): freeSharesLeft 627 FLAT, openedAt 0 "
        "(pool BELUM buka), freeClaimed 373, freeBooked(user)=10000 RIG. Tetap lead-minted-by-user, belum dibuka. DIAM.")
    print("RigForge: still not open, freeSharesLeft 627 flat")
bs = snap.get("track_c", {}).get("bsccat")
if bs is not None:
    bs.update({"freeMinted": 519, "lastReadWib": WIB, "lastReadBlock": BLK})
    bs["runNote2231_1117"] = "Run 2231 (blok 134145823): freeMinted 518->519 (+1). Tetap watchlist-only-age-unverified. DIAM."
    print("bsccat: freeMinted 519")
pp = snap.get("track_c", {}).get("PEPE")
if pp is not None:
    pp.update({"lastReadWib": WIB, "lastReadBlock": BLK})
    pp["runNote2231_1117"] = ("Run 2231 (blok 134145823): freeMinted 500 (pool habis), soldShares 501, "
        "opened 0, hasMinted(user)=1. Tetap minted-by-user. DIAM.")
    print("PEPE: unchanged")

# ---- Track B pending: binanceai.fun ----
pc = snap.get("pending_claims", {}).get("binanceai.fun")
if pc is not None:
    pc.update({"launched": 0, "failed": 1, "isRefundPhase": 1,
               "tokenClaimed_user": 0, "lastReadWib": WIB})
    pc["runNote2231_1117"] = ("Run 2231 (blok 134145823): launched=0, failed=1, isRefundPhase=1, "
        "tokenClaimed(user)=0, totalShares 3110 - tetap pending/refund, sudah dilaporkan sekali (fase refund), DIAM.")
    print("binanceai pending: still launched=0, failed=1, refund=1 (no change)")

# ---- Bold Leonidas SELLOUT: remove from contracts, keep evidence top-level ----
bold = snap["contracts"].pop("Bold Leonidas", None)
snap["removed2231_boldleonidas_sellout"] = {
    "address": "0x84bcb8c16566e81ce902530c9da1e3de291f9941",
    "status": "sold-out-2026-11-17",
    "evidence": ("totalSupply 1111/1111 MAX_SUPPLY, totalMinted 1111, remaining() 0 "
        "(baca run 2231 blok 134145823 + konfirmasi independen blok 134146264); "
        "hot-leg 2239/2244: 1111 flat. Jalur: 898 (2131) -> 900 (2201) -> 926 (hot-leg 2224) "
        "-> 998 (2229) -> 1075 (2234) -> 1111 (2239). Early lead dilaporkan sekali run 0601 2026-11-16; "
        "sellout dilaporkan sekali run 2231."),
    "removedWib": WIB,
    "reported_once": "run 2231",
}
print("Bold Leonidas REMOVED from snapshot (sold out, reported once)")

snap["last_run"] = "2026-11-17 ~22:31 WIB"
snap["last_run_wib"] = "2026-11-17 ~22:31 WIB"
snap["timestamp_wib"] = "2026-11-17 ~22:31 WIB"
snap["runNote2231"] = (
    "Run 2231 (jadwal 22:31 WIB): 0 kandidat baru, 0 strong lead baru, 0 early lead baru, "
    "0 track-B dibuka, 0 track-C lead/kandidat baru. 1 PERUBAHAN: Bold Leonidas SOLD OUT "
    "(totalSupply 1111/1111 MAX_SUPPLY, remaining 0 - terverifikasi 2x: blok 134145823 + 134146264; "
    "hot-leg 2239/2244 konfirmasi 1111 flat) - early lead 16 Nov 06:01, dilaporkan sekali run ini + "
    "dihapus dari snapshot. Reread 40/40 OK (blok 134145823, 26,4 dtk, 141 calls, 0 chunk error): "
    "HIVE 1263 flat; Bubblebruin 2620 FLAT vs 2201 (snapshot 2530 tertinggal, dikoreksi), free 2614/7777=33,6%; "
    "PunchCard 1258->1287 (+29, velocity LOLOS 2,8x) tapi free 22,8% <50% + umur unverified -> bukan kandidat; "
    "Mine Card 995->1063 (+68, velocity LOLOS 2,4x) tapi free%/umur unverified -> bukan kandidat; "
    "Matrix free 587/1000=58,7%; AGCLUB free 522/888=58,8%; Ledgera free 2699/5000=54,0%; "
    "Lumenhold free 1233/1500=82,2% TERVERIFIKASI tapi umur unverified + velocity GAGAL -> bukan strong lead; "
    "EIM totalMinted 394->400 (+6); XCOPY 443->445; ARKYN 1963->1969; ALIEN 454 flat; Kitebots 1453->1454; "
    "PXIO-Miners 14872->15590 (+718, hot-leg focus, bukan tier); CAT402 100/100 tetap SOLD OUT; "
    "DRAGON freeRemaining 0; RigForge openedAt 0, freeSharesLeft 627 flat; bsccat freeMinted 518->519; "
    "PEPE pool habis, opened 0. BinanceAI pending tetap launched=0/failed=1/refund=1. "
    "Pre-flight Ankr 401 fast-fail (ke-29 berturut-turut main job, 1,4 dtk, head 134145792), "
    "watermark TETAP 134086385 (milik backfill cron); 5c dilewati. "
    "Feed Sourcify 20 kontrak (top verifiedAt 15:45:41Z), 5 baru vs hot-leg 2229: 0xa607, 0x92CA, "
    "0xF798, 0x14A3, 0xa85c - semuanya sudah di-shape-check hot-leg 2234/2239/2244, 0 hit S1/S2. "
    "Boltbook EN 44.178 B / ZH 42.481 B, 12/11 alamat; 8 alamat baru vs 2229 semuanya sudah dicek "
    "(6 checked-not-sale-shape, 1 shape-deferred, 1 watchlist-only mint-closed) + Forge Bloom 0x59fe "
    "(age-excluded 15 Nov, post velt.ai hari ini hanya recheck 418/1.746, BUKAN launch baru) + "
    "EWARDEN 0xdb72 (free mint tutup, 921/3.000) + 1 artefak prefix tx-hash. Bridge 116 kontrak, "
    "0 outside snapshot, 7 same_owner_discarded. "
    "Sweep EN+ZH + Odaily: semua sudah dikenal (Oathbots, AGENTID, hackou, LeadLoop, Piggy Agent, "
    "AGENT COSMOS, Agentic Gangster, AGENT MAO, BAS Medium, aiyqx guide); Odaily hanya berita makro, "
    "0 pengumuman free-mint Agent ID baru. "
    "LAPORAN CHAT: hanya sellout Bold Leonidas (1x)."
)
json.dump(snap, open(BASE + "onchain-snapshot.json", "w"), indent=1)
print("SNAPSHOT UPDATED, last_run 22:31 WIB")
