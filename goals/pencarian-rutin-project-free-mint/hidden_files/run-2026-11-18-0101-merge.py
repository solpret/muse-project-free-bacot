#!/usr/bin/env python3
"""Merge run 2026-11-18 01:01 (free-mint-search) into the main snapshot.
Updates scalar readings + last_run fields only; does NOT delete history keys.
Interval: 0031 blok 134160308 -> 0101 blok 134164123 = 3815 blok * 0.45 dtk = ~28.6 mnt.
No tier changes; STOCK AGENT + THYRK re-read (first-read block 134164602)."""
import json
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
snap = json.load(open(BASE + "onchain-snapshot.json"))
BLK = 134164123
WIB = "2026-11-18 ~01:01 WIB"

def upd(name, fields, note):
    e = snap["contracts"].get(name)
    if e is None:
        print("MISSING in snapshot:", name); return False
    e.update(fields)
    e["lastReadBlock"] = BLK
    e["lastReadWib"] = WIB
    e["runNote0101_1118"] = note
    return True

upd("HIVE Agents", {"totalSupply": 1263, "balanceOf_user": 1},
    "Run 0101 (blok 134164123): totalSupply 1263 FLAT, balanceOf(user)=1, minted-by-user. DIAM.")
upd("Bubblebruin", {"totalSupply": 2620, "freeClaimed": 2614, "balanceOf_user": 1,
                    "previousTotalSupply": 2620, "mintedInInterval": 0,
                    "currentRatePerMin": 0.0, "velocityLegPasses": False,
                    "freePctVerified": 33.6},
    "Run 0101 (blok 134164123): totalSupply 2620 FLAT vs 0031 (2620), freeClaimed 2614/7777=33,6% (<70%). velocity 0. minted-by-user, bukan kandidat. DIAM.")
upd("CAT402", {"freeCatsClaimed": 100, "freeCatsRemaining": 0},
    "Run 0101 (blok 134164123): freeCatsClaimed 100/100, freeCatsRemaining 0 -> tetap SOLD OUT. totalSupply/mintOpen revert run ini (nilai lama dipertahankan). DIAM.")
upd("JADE", {"totalSupply": 191, "freeClaimed": 188, "cost_user_1": 500000000000000},
    "Run 0101 (blok 134164123): totalSupply 191 FLAT, freeClaimed 188; cost(user,1)=0,0005 BNB -> slot user TIDAK gratis (jalur berbayar). Bukan kandidat/lead. DIAM.")
upd("Agent Bubble", {"freeMinted": 1871, "totalSupply": 2016, "totalMinted": 2016,
                     "previousTotalSupply": 2014, "mintedInInterval": 2,
                     "intervalMinutes": 28.6, "currentRatePerMin": 0.07,
                     "previousRatePerMin": 0.07, "velocityRatio": 1.0,
                     "velocityLegPasses": False},
    "Run 0101 (blok 134164123): freeMinted 1869->1871, totalSupply 2014->2016 (+2, 0,07/mnt vs prev 0,07 = 1,0x, <20) -> velocity GAGAL. free% TETAP UNVERIFIED (FREE_SUPPLY null) + umur UNVERIFIED -> BUKAN strong lead. DIAM.")
upd("DRAGON", {"freeMinted": 1000, "totalMinted": 1005, "balanceOf_user": 1},
    "Run 0101 (blok 134164123): freeMinted 1000, totalMinted 1005, balanceOf(user)=1 (minted-by-user). freeRemaining 0 (sudah diketahui). DIAM.")
upd("Matrix Agents", {"freeMinted": 588, "freeRemaining": 412, "totalSupply": 585,
                      "previousTotalSupply": 585, "mintedInInterval": 0,
                      "velocityLegPasses": False, "freePctVerified": 58.8},
    "Run 0101 (blok 134164123): freeMinted 588 FLAT, totalSupply 585 FLAT; free 588/1000=58,8% (<70%). velocity GAGAL. DIAM.")
upd("AGCLUB", {"totalMinted": 523, "freeMinted": 523, "FREE_CAP": 888,
               "velocityLegPasses": False, "freePctVerified": 58.9},
    "Run 0101 (blok 134164123): freeMinted 523 FLAT; free 523/888=58,9% (<70%). DIAM.")
upd("SPARKS", {"totalSupply": 1156},
    "Run 0101 (blok 134164123): totalSupply 1156 FLAT. DIAM.")
upd("Ledgera", {"freeClaimed": 2702, "totalSupply": 2709, "freeUsed_user": 0,
                "balanceOf_user": 0, "previousTotalSupply": 2709,
                "mintedInInterval": 0, "velocityLegPasses": False,
                "freePctVerified": 54.0},
    "Run 0101 (blok 134164123): freeClaimed 2702 FLAT, totalSupply 2709 FLAT; free 2702/5000=54,0% (<70%). velocity GAGAL. Umur UNVERIFIED. DIAM.")
upd("RaceAgents", {"totalSupply": 632, "freeMinted": 632},
    "Run 0101 (blok 134164123): totalSupply 632 FLAT, freeMinted 632. velocity GAGAL. DIAM.")
upd("CPASS", {"totalMinted": 1773, "balanceOf_user": 0},
    "Run 0101 (blok 134164123): totalMinted 1773 FLAT. DIAM.")
upd("REOPIR", {"freeClaimed": 581, "totalSupply": 581},
    "Run 0101 (blok 134164123): freeClaimed 581 FLAT, totalSupply 581. DIAM.")
upd("RAVE", {"totalMinted": 366, "freeMinted": 366},
    "Run 0101 (blok 134164123): totalMinted 366 FLAT. DIAM.")
upd("MORFO", {"totalMinted": 1091, "previousTotalSupply": 1089,
              "mintedInInterval": 2, "velocityLegPasses": False},
    "Run 0101 (blok 134164123): totalMinted 1089->1091 (+2, <20) -> velocity GAGAL. DIAM.")
upd("PIXEL FROGS", {"totalSupply": 456, "freeMinted": 454, "freeLeft": 2546,
                   "mintOpen": 0, "freeClaimed_user": 0, "freePctVerified": 15.1},
    "Run 0101 (blok 134164123): totalSupply 456 FLAT, freeMinted 454, freeLeft 2546, mintOpen=0 (tutup); free 454/(454+2546)=15,1% (<70%). DIAM.")
upd("Flare Agent-bd6f", {"totalSupply": 4900},
    "Run 0101 (blok 134164123): totalSupply 4900 FLAT. DIAM.")
upd("PunchCard", {"totalSupply": 1304, "totalMinted": 1304, "freeMinted": 1282,
                  "paidMinted": 22, "previousTotalSupply": 1303,
                  "mintedInInterval": 1, "intervalMinutes": 28.6,
                  "currentRatePerMin": 0.03, "previousRatePerMin": 0.30,
                  "velocityRatio": 0.12, "velocityLegPasses": False,
                  "freePctVerified": 23.1, "mintPriceFor_user_1": 0,
                  "mintedCount_user": 0, "balanceOf_user": 0},
    "Run 0101 (blok 134164123): totalSupply 1303->1304 (+1, 0,03/mnt vs prev 0,30 = 0,12x, <20) -> velocity GAGAL. freeMinted 1282; free 1282/5555=23,1% (<50% kandidat, <70% strong lead); umur UNVERIFIED -> BUKAN kandidat/strong lead. Slot user terbuka (mintPriceFor 0, mintedCount 0). DIAM.")
upd("XCOPY", {"totalSupply": 452, "totalMinted": 452, "previousTotalSupply": 452,
              "mintedInInterval": 0, "velocityLegPasses": False},
    "Run 0101 (blok 134164123): totalSupply 452 FLAT -> velocity GAGAL. DIAM.")
upd("ARKYN", {"totalMinted": 1976, "previousTotalSupply": 1976,
              "mintedInInterval": 0, "velocityLegPasses": False},
    "Run 0101 (blok 134164123): totalMinted 1976 FLAT -> velocity GAGAL; totalSupply revert run ini. free% UNVERIFIED. DIAM.")
upd("Mine Card", {"totalSupply": 1096, "totalMinted": 1096,
                  "previousTotalSupply": 1093, "mintedInInterval": 3,
                  "intervalMinutes": 28.6, "currentRatePerMin": 0.10,
                  "previousRatePerMin": 0.23, "velocityRatio": 0.46,
                  "velocityLegPasses": False},
    "Run 0101 (blok 134164123): totalSupply 1093->1096 (+3, 0,10/mnt vs prev 0,23 = 0,46x, <20) -> velocity GAGAL. free% + umur UNVERIFIED -> BUKAN kandidat/strong lead. DIAM.")
upd("ALIEN", {"totalSupply": 473, "previousTotalSupply": 473,
              "mintedInInterval": 0, "velocityLegPasses": False},
    "Run 0101 (blok 134164123): totalSupply 473 FLAT -> velocity GAGAL. free% + umur UNVERIFIED. DIAM.")
upd("Kitebots", {"totalSupply": 1456, "freeMinted": 1456, "previousTotalSupply": 1456,
                 "mintedInInterval": 0, "velocityLegPasses": False},
    "Run 0101 (blok 134164123): totalSupply 1456 FLAT, freeMinted 1456 -> velocity GAGAL. Umur UNVERIFIED. DIAM.")
upd("Everything Is Mine (EIM)", {"totalMinted": 418, "mintOpen": 1,
                                 "previousTotalMinted": 415, "mintedInInterval": 3,
                                 "intervalMinutes": 28.6, "currentRatePerMin": 0.10,
                                 "previousRatePerMin": 0.07, "velocityRatio": 1.5,
                                 "velocityLegPasses": False},
    "Run 0101 (blok 134164123): totalMinted 415->418 (+3, 0,10/mnt vs prev 0,07 = 1,5x TAPI <20) -> velocity GAGAL. free% + umur UNVERIFIED -> tetap early lead, BUKAN strong lead/kandidat. TIDAK preview/mint. DIAM.")
upd("Lumenhold", {"totalSupply": 1247, "freeClaimed": 1242,
                  "previousTotalSupply": 1247, "mintedInInterval": 0,
                  "velocityLegPasses": False, "freePctVerified": 82.8},
    "Run 0101 (blok 134164123): totalSupply 1247 FLAT, freeClaimed 1242; free 1242/1500=82,8% TERVERIFIKASI (>70%) TAPI umur UNVERIFIED + velocity GAGAL -> BUKAN strong lead/kandidat. TIDAK dilaporkan. DIAM.")
upd("PXIO Miners", {"totalSupply": 16666, "previousTotalSupply": 16666,
                    "mintedInInterval": 0, "velocityLegPasses": False},
    "Run 0101 (blok 134164123): totalSupply 16666 FLAT (16.666/16.666 TUTUP). DIAM.")
upd("FrieAgent-B751", {"totalSupply": 9901},
    "Run 0101 (blok 134164123): totalSupply 9901 FLAT. DIAM.")
upd("FrieAgent-c64d", {"totalSupply": 4901},
    "Run 0101 (blok 134164123): totalSupply 4901 FLAT. DIAM.")
upd("Abyssora", {},
    "Run 0101 (blok 134164123): totalSupply GAGAL baca (revert) - degradasi view, BUKAN nol; nilai lama dipertahankan. DIAM.")
upd("HANAMI", {"totalSupply": 132, "freeMinted": 130, "previousTotalSupply": 132,
               "mintedInInterval": 0, "velocityLegPasses": False},
    "Run 0101 (blok 134164123): totalSupply 132 FLAT, freeMinted 130 -> velocity GAGAL. DIAM.")
upd("Zephyra", {"totalMinted": 991},
    "Run 0101 (blok 134164123): totalMinted 991 FLAT. DIAM.")
upd("AgentNOVA", {"totalSupply": 723},
    "Run 0101 (blok 134164123): totalSupply 723 FLAT. DIAM.")
upd("ONI", {"totalMinted": 6, "totalSupply": 6},
    "Run 0101 (blok 134164123): totalMinted 6 FLAT, totalSupply 6. DIAM.")
upd("HAPPE", {"totalMinted": 241, "freeMinted": 222},
    "Run 0101 (blok 134164123): totalMinted 241 FLAT, freeMinted 222. DIAM.")
upd("Kryntar", {"totalMinted": 1370},
    "Run 0101 (blok 134164123): totalMinted 1370 FLAT. DIAM.")
upd("Pengu", {"totalMinted": 138, "freeMinted": 138},
    "Run 0101 (blok 134164123): totalMinted 138 FLAT, freeMinted 138. DIAM.")
upd("RigForge", {"freeSharesLeft": 625, "openedAt": 0, "freeClaimed": 375},
    "Run 0101 (blok 134164123): openedAt 0, freeSharesLeft 625, freeClaimed 375 - BELUM DIBUKA, tidak berubah. DIAM.")
upd("STOCK AGENT", {"totalSupply": 518, "freeLeft": 593, "freePctVerified": 46.6,
                    "previousTotalSupply": 509, "mintedInInterval": 9,
                    "intervalMinutes": 28.3, "currentRatePerMin": 0.32,
                    "previousRatePerMin": None, "velocityRatio": None,
                    "velocityLegPasses": False, "quote_user_1": 0,
                    "freeMintedByWallet_user": 0, "balanceOf_user": 0},
    "Run 0101 (first-read blok 134164602): totalSupply 509->518 (+9, 0,32/mnt; baseline pertama - belum ada previous rate, velocity BELUM BISA lolos; <20 juga). freeLeft 602->593; free 518/1111=46,6% (<50% kandidat, <70% strong lead). quote(user,1)=0, freeMintedByWallet(user)=0, balanceOf(user)=0 (slot TERBUKA). Umur TETAP UNVERIFIED + website gate TETAP UNVERIFIED -> tetap EARLY lead, BUKAN strong lead/kandidat. TIDAK preview/mint. DIAM.")
upd("THYRK", {"totalSupply": 4414, "freeMinted": 4313,
              "previousTotalSupply": 4414, "mintedInInterval": 0,
              "velocityLegPasses": False},
    "Run 0101 (first-read blok 134164602): totalSupply 4414 FLAT, freeMinted 4313 FLAT. freeUsed(user)=1, balanceOf(user)=1 (slot user SUDAH TERPAKAI). Umur TETAP UNVERIFIED. Tetap watchlist-only-age-unverified, BUKAN lead. DIAM.")

# bsccat + pepe tracked in snapshot? record as run note only
snap["runNote0101_1118"] = ("Run 0101 (blok 134164123): bsccat freeMinted 519->520, totalSupply 520e27; "
    "pepe freeMinted 500/500, opened 0, hasMinted_user 1 - tidak berubah tier. "
    "Bitcoin Frogs probe: totalMinted 10686, freeMinted 2000/2000 - free pool HABIS (tampilan situs 'Free claimed 0/2,000' basi/menyesatkan; on-chain yang menentukan). DIAM.")
snap["runNote0101_1118_scan"] = ("Run 0101 SCAN FAST-FAIL (pre-flight Ankr 401, 1,0 dtk, head 134164123) - "
    "ke-34 berturut-turut main job. Watermark TETAP 134086385. Scan + track-C 5c dilewati (tidak ada output scan).")
snap["runNote0101_1118_binanceai"] = ("Run 0101 (blok 134164123): binanceai.fun launched=0, failed=1, isRefundPhase=1, "
    "tokenClaimed(user)=0, totalShares 3110 - tetap pending/refund, sudah dilaporkan sekali (fase refund), DIAM.")
snap["last_run_wib"] = WIB
snap["last_run"] = "free-mint-search 2026-11-18 01:01 WIB - 0 kandidat, 0 strong lead, 0 early lead baru, 0 track-B/C baru; DIAM"
json.dump(snap, open(BASE + "onchain-snapshot.json", "w"), indent=1)
print("snapshot updated, contracts:", len(snap["contracts"]))
