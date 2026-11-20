#!/usr/bin/env python3
"""Merge run 2026-11-18 01:31 (free-mint-search) into the main snapshot.
Updates scalar readings + last_run fields only; does NOT delete history keys.
Interval: 0101 blok 134164123 -> 0131 blok 134168552 = 4429 blok * 0.45 dtk = ~33.2 mnt.
Retry chunk (XCOPY..HANAMI) blok 134168725. No tier changes except AgentEcho
EARLY lead added + ADRAW added watchlist-only."""
import json
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
snap = json.load(open(BASE + "onchain-snapshot.json"))
BLK = 134168552
WIB = "2026-11-18 ~01:31 WIB"
INTERVAL = 33.2

def upd(name, fields, note):
    e = snap["contracts"].get(name)
    if e is None:
        print("MISSING in snapshot:", name); return False
    e.update(fields)
    e["lastReadBlock"] = BLK
    e["lastReadWib"] = WIB
    e["runNote0131_1118"] = note
    return True

def vel(name, new_supply):
    """velocity from snapshot stored prev supply/rate; returns dict of fields."""
    e = snap["contracts"].get(name, {})
    prev = e.get("totalSupply")
    prev_rate = e.get("currentRatePerMin")
    if prev is None or new_supply is None:
        return {"previousTotalSupply": new_supply, "mintedInInterval": None,
                "intervalMinutes": INTERVAL, "velocityLegPasses": False}
    minted = new_supply - prev
    rate = minted / INTERVAL if INTERVAL else 0.0
    ratio = (rate / prev_rate) if prev_rate else None
    passes = bool(prev_rate) and rate >= 1.5 * prev_rate and minted >= 20
    return {"previousTotalSupply": new_supply, "mintedInInterval": minted,
            "intervalMinutes": INTERVAL, "currentRatePerMin": round(rate, 4),
            "previousRatePerMin": prev_rate, "velocityRatio": (round(ratio, 2) if ratio is not None else None),
            "velocityLegPasses": passes}

upd("HIVE Agents", {"totalSupply": 1263, "balanceOf_user": 1},
    "Run 0131 (blok 134168552): totalSupply 1263 FLAT, balanceOf(user)=1, minted-by-user. DIAM.")
upd("Bubblebruin", dict({"totalSupply": 2620, "freeClaimed": 2614, "balanceOf_user": 1,
                    "freePctVerified": 33.6}, **vel("Bubblebruin", 2620)),
    "Run 0131 (blok 134168552): totalSupply 2620 FLAT vs 0101 (2620), freeClaimed 2614/7777=33,6% (<70%). velocity 0. minted-by-user, bukan kandidat. DIAM.")
upd("CAT402", {"freeCatsClaimed": 100, "freeCatsRemaining": 0},
    "Run 0131 (blok 134168552): freeCatsClaimed 100/100, freeCatsRemaining 0 -> tetap SOLD OUT. totalSupply/mintOpen revert run ini (nilai lama dipertahankan). DIAM.")
upd("JADE", {"totalSupply": 191, "freeClaimed": 188, "cost_user_1": 500000000000000, "mintedBy_user": 0, "balanceOf_user": 0},
    "Run 0131 (blok 134168552): totalSupply 191 FLAT, freeClaimed 188; cost(user,1)=0,0005 BNB -> slot user TIDAK gratis (jalur berbayar). Bukan kandidat/lead. DIAM.")
upd("AgentBubble", dict({"freeMinted": 1872, "totalSupply": 2017, "totalMinted": 2017,
                    "balanceOf_user": 0}, **vel("AgentBubble", 2017)),
    "Run 0131 (blok 134168552): freeMinted 1871->1872, totalSupply 2016->2017 (+1, 0,03/mnt vs prev 0,07 = 0,43x, <20) -> velocity GAGAL. free% TETAP UNVERIFIED (FREE_SUPPLY null; 1872/2222=84,2% hanya inferensi total-supply) + umur UNVERIFIED -> BUKAN strong lead. DIAM.")
upd("DRAGON", {"freeMinted": 1000, "totalMinted": 1005, "balanceOf_user": 1},
    "Run 0131 (blok 134168552): freeMinted 1000, totalMinted 1005, balanceOf(user)=1 (minted-by-user). freeRemaining 0 (sudah diketahui). DIAM.")
upd("Matrix", dict({"freeMinted": 588, "freeRemaining": 412, "totalSupply": 585,
               "freePctVerified": 58.8}, **vel("Matrix", 585)),
    "Run 0131 (blok 134168552): freeMinted 588 FLAT, totalSupply 585 FLAT; free 588/1000=58,8% (<70%). velocity GAGAL. DIAM.")
upd("AGCLUB", dict({"totalMinted": 524, "freeMinted": 524, "FREE_CAP": 888,
               "freePctVerified": 59.0}, **vel("AGCLUB", 524)),
    "Run 0131 (blok 134168552): totalMinted/freeMinted 523->524 (+1, <20); free 524/888=59,0% (<70%). velocity GAGAL. DIAM.")
upd("BNBG", {"totalMinted": 69},
    "Run 0131 (blok 134168552): totalMinted 69. DIAM.")
upd("SPARKS", {"totalSupply": 1156},
    "Run 0131 (blok 134168552): totalSupply 1156 FLAT. DIAM.")
upd("Ledgera", dict({"freeClaimed": 2702, "totalSupply": 2709, "freeUsed_user": 0,
                "balanceOf_user": 0, "freePctVerified": 54.0}, **vel("Ledgera", 2709)),
    "Run 0131 (blok 134168552): freeClaimed 2702 FLAT, totalSupply 2709 FLAT; free 2702/5000=54,0% (<70%). velocity GAGAL. Umur UNVERIFIED. DIAM.")
upd("BoldLeonidas", {"totalSupply": 1111, "mintOpen": 1, "balanceOf_user": 0},
    "Run 0131 (blok 134168552): totalSupply 1111, mintOpen 1, balanceOf(user)=0. DIAM.")
upd("RaceAgents", dict({"totalSupply": 633, "freeMinted": 633}, **vel("RaceAgents", 633)),
    "Run 0131 (blok 134168552): totalSupply/freeMinted 632->633 (+1, <20) -> velocity GAGAL. DIAM.")
upd("CPASS", {"totalMinted": 1773, "balanceOf_user": 0},
    "Run 0131 (blok 134168552): totalMinted 1773 FLAT. DIAM.")
upd("REOPIR", {"freeClaimed": 581, "totalSupply": 581},
    "Run 0131 (blok 134168552): freeClaimed 581 FLAT, totalSupply 581. DIAM.")
upd("RAVE", {"totalMinted": 366, "freeMinted": 366},
    "Run 0131 (blok 134168552): totalMinted 366 FLAT. DIAM.")
upd("MORFO", {"totalMinted": 1091},
    "Run 0131 (blok 134168552): totalMinted 1091 FLAT. DIAM.")
upd("PIXEL FROGS", {"totalSupply": 456, "freeMinted": 454, "freeLeft": 2546,
                   "mintOpen": 0, "freeClaimed_user": 0, "freePctVerified": 15.1},
    "Run 0131 (blok 134168552): totalSupply 456 FLAT, freeMinted 454, freeLeft 2546, mintOpen=0 (tutup); free 454/(454+2546)=15,1% (<70%). DIAM.")
upd("Flare-bd6f", {"totalSupply": 4900},
    "Run 0131 (blok 134168552): totalSupply 4900 FLAT. DIAM.")
upd("PunchCard", dict({"totalSupply": 1306, "totalMinted": 1306, "freeMinted": 1284,
                  "paidMinted": 22, "freePctVerified": 23.1, "mintPriceFor_user_1": 0,
                  "mintedCount_user": 0, "balanceOf_user": 0}, **vel("PunchCard", 1306)),
    "Run 0131 (blok 134168552): totalSupply 1304->1306 (+2, 0,06/mnt vs prev 0,03 = 2,0x TAPI <20) -> velocity GAGAL. freeMinted 1284; free 1284/5555=23,1% (<50% kandidat, <70% strong lead); umur UNVERIFIED -> BUKAN kandidat/strong lead. Slot user terbuka (mintPriceFor 0, mintedCount 0). DIAM.")
upd("RigForge", {"freeSharesLeft": 625, "openedAt": 0, "freeClaimed": 375,
                "freeBooked_user": 10000000000000000000000},
    "Run 0131 (blok 134168552): openedAt 0 (belum buka), freeSharesLeft 625, freeClaimed 375 (tetap). freeBooked(user) terbaca 1e22 (satuan mentah, tanpa interpretasi). DIAM.")
upd("binanceai-mint", {"launched": 0, "failed": 1, "isRefundPhase": 1, "totalShares": 3110},
    "Run 0131 (blok 134168552): launched 0, failed 1, isRefundPhase 1 (tetap pending/refund, sudah dilaporkan sekali 2 Nov). tokenClaimed(user) gagal baca run ini (nilai lama 0 dipertahankan). DIAM.")
upd("XCOPY", {"totalSupply": 452, "totalMinted": 452},
    "Run 0131 (retry blok 134168725): totalSupply/totalMinted 452 FLAT (baca utama None - degradasi RPC, dipulihkan via retry). DIAM.")
upd("ARKYN", {"totalMinted": 1976},
    "Run 0131 (retry blok 134168725): totalMinted 1976 (baca utama None - degradasi RPC, dipulihkan via retry; totalSupply revert, nilai lama dipertahankan). DIAM.")
upd("Mine Card", {"totalSupply": 1097, "totalMinted": 1097},
    "Run 0131 (retry blok 134168725): totalSupply 1096->1097 (+1, <20) -> velocity GAGAL (baca utama None - degradasi RPC, dipulihkan via retry). DIAM.")
upd("ALIEN", {"totalSupply": 474},
    "Run 0131 (retry blok 134168725): totalSupply 474 (baca utama None - degradasi RPC, dipulihkan via retry). DIAM.")
upd("Kitebots", {"totalSupply": 1458, "freeMinted": 1458},
    "Run 0131 (retry blok 134168725): totalSupply/freeMinted 1458 (baca utama None - degradasi RPC, dipulihkan via retry). DIAM.")
upd("EIM", {"totalMinted": 419, "mintOpen": 1},
    "Run 0131 (retry blok 134168725): totalMinted 418->419 (+1, <20) -> velocity GAGAL (baca utama None - degradasi RPC, dipulihkan via retry). DIAM.")
# Lumenhold: cap from snapshot (FREE cap 1500 per earlier 82.8%)
lum = snap["contracts"].get("Lumenhold", {})
cap = lum.get("FREE_SUPPLY") or lum.get("freeSupply") or lum.get("MAX_SUPPLY") or 1500
pct = round(1245 / cap * 100, 1) if cap else None
upd("Lumenhold", dict({"totalSupply": 1250, "freeClaimed": 1245, "freePctVerified": pct}, **vel("Lumenhold", 1250)),
    f"Run 0131 (retry blok 134168725): totalSupply 1250, freeClaimed 1245; free {pct}% (cap {cap}) TAPI umur UNVERIFIED + velocity tidak lolos -> BUKAN strong lead. (baca utama None - degradasi RPC, dipulihkan via retry). DIAM.")
upd("PXIO Miners", {"totalSupply": 16666},
    "Run 0131 (retry blok 134168725): totalSupply 16666 (baca utama None - degradasi RPC, dipulihkan via retry). DIAM.")
upd("FrieAgent-B751", {"totalSupply": 9901},
    "Run 0131 (retry blok 134168725): totalSupply 9901 (baca utama None - degradasi RPC, dipulihkan via retry). DIAM.")
upd("FrieAgent-c64d", {"totalSupply": 4901},
    "Run 0131 (retry blok 134168725): totalSupply 4901 (baca utama None - degradasi RPC, dipulihkan via retry). DIAM.")
upd("Abyssora", {},
    "Run 0131 (retry blok 134168725): totalSupply revert di baca utama DAN retry (nilai lama dipertahankan, BUKAN nol). DIAM.")
upd("HANAMI", {"totalSupply": 132, "freeMinted": 130},
    "Run 0131 (retry blok 134168725): totalSupply 132, freeMinted 130 (baca utama None - degradasi RPC, dipulihkan via retry). DIAM.")
upd("Zephyra", {"totalMinted": 993},
    "Run 0131 (blok 134168552): totalMinted 993. DIAM.")
upd("AgentNOVA", {"totalSupply": 726},
    "Run 0131 (blok 134168552): totalSupply 726. DIAM.")
upd("ONI", {"totalMinted": 6, "totalSupply": 6},
    "Run 0131 (blok 134168552): totalMinted/totalSupply 6. DIAM.")
upd("HAPPE AGENTS", {"totalMinted": 241, "freeMinted": 222},
    "Run 0131 (blok 134168552): totalMinted 241, freeMinted 222. DIAM.")
upd("Kryntar", {"totalMinted": 1370},
    "Run 0131 (blok 134168552): totalMinted 1370 FLAT. DIAM.")
upd("Pengu", {"totalMinted": 138, "freeMinted": 138},
    "Run 0131 (blok 134168552): totalMinted/freeMinted 138. DIAM.")
upd("STOCK AGENT", dict({"totalSupply": 529, "freeLeft": 582, "FREE_SUPPLY": 1111,
                    "MAX_SUPPLY": 2222, "mintOpen": 1, "quote_user_1": 0,
                    "freeMintedByWallet_user": 0, "balanceOf_user": 0,
                    "freePctVerified": 47.6}, **vel("STOCK AGENT", 529)),
    "Run 0131 (blok 134168552): totalSupply 518->529 (+11, 0,33/mnt vs prev 0,32 = 1,03x TAPI <20) -> velocity GAGAL. freeLeft 593->582; free 529/1111=47,6% (<50% kandidat, <70% strong lead). quote(user,1)=0, freeMintedByWallet(user)=0, balanceOf(user)=0 (slot TERBUKA). Umur TETAP UNVERIFIED + website gate TETAP UNVERIFIED -> tetap EARLY lead, BUKAN strong lead/kandidat. TIDAK preview/mint.")
upd("THYRK", {"totalSupply": 4414, "freeMinted": 4313, "MAX_SUPPLY": 7777,
             "freeUsed_user": 1, "balanceOf_user": 1},
    "Run 0131 (blok 134168552): totalSupply 4414 FLAT, freeMinted 4313 FLAT; freeUsed(user)=1, balanceOf(user)=1 (slot user SUDAH TERPAKAI). Umur TETAP UNVERIFIED. Tetap watchlist-only-age-unverified, BUKAN lead.")
# ADRAW: new snapshot entry (hot-leg found it 01:24, main-job first read this run)
snap["contracts"]["ADRAW"] = {
    "address": "0xdc167f998341aa37d734de94db2108f0983bf2a7",
    "status": "watchlist-only-age-unverified-2026-11-18",
    "name": "ADRAW", "kind": "ERC721",
    "totalSupply": None, "freeMinted": 299, "mintOpen": None,
    "balanceOf_user": 0, "hasClaimedFree_user": 0,
    "freePctNote": "299/1000 = 29,9% total-supply (bukan % kuota gratis terverifikasi); <50% kandidat, <70% strong lead.",
    "firstSeenBlock": 134167812, "source": "hot-leg-0124-boltbook-sarpawi98",
    "launchNote": "Launch age UNVERIFIED (periodStart stated only 15:12 WIB 17 Nov - 15:12 WIB 20 Nov; first-mint tx not corroborated).",
    "lastReadBlock": BLK, "lastReadWib": WIB,
    "runNote0131_1118": "Run 0131 (blok 134168552): freeMinted 299 FLAT vs hot-leg 0124 (299); hasClaimedFree(user)=0, balanceOf(user)=0. 29,9% <50% + umur UNVERIFIED -> watchlist-only, BUKAN lead. Ditambahkan ke snapshot run ini (temuan hot-leg 0124).",
}
# AgentEcho: NEW EARLY LEAD (first report this run)
snap["contracts"]["AgentEcho"] = {
    "address": "0xff2dac2389a6a9593209b6008d5ffa9e73aa19c2",
    "status": "early-lead-reported-2026-11-18-0131",
    "name": "AgentEcho", "symbol": "ECHO", "kind": "ERC721",
    "totalSupply": 209, "MAX_SUPPLY": 20000, "mintOpen": 1,
    "balanceOf_user": 0, "mintedBy_user": 0, "MAX_PER_WALLET": 1,
    "freeMinted": None, "freeClaimed": None, "freeLeft": None,
    "freePctNote": "209/20000 = 1,05% total-supply (BUKAN % kuota gratis terverifikasi - kontrak tanpa free view/quote).",
    "agentShape": "VERIFIED: AGENT_ID()=registry persis 0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F; mint() no-arg nonpayable; Sourcify exact_match verifiedAt 2026-11-17T17:39:18Z; MAX_SUPPLY 20000; mintOpen 1.",
    "owner": "0x1f3301bf46b8e85d5e4a1984e05faa8084ae8e5d",
    "ownerDiscarded": False,
    "firstSeenBlock": 134167691,
    "firstSeenNote": "Boltbook post grandtheftauto6.ai ~01:29 WIB: 180/20.000 minted blok 134167691; re-read run ini totalSupply 209 blok 134168875 (+29, minting live). Sourcify feed first-seen hot-leg 00:41 WIB (checked-not-sale-shape).",
    "launchNote": "Launch age UNVERIFIED: first-mint block TIDAK terkoroborasi (eth_getLogs -32005 limit exceeded di bsc-dataseed single/batch, bsc-dataseed1, bsc.publicnode); same-day evidence only: Sourcify verifiedAt 00:39 WIB 18 Nov + Boltbook post 01:29 WIB.",
    "website": None, "websiteNote": "UNVERIFIED: tokenURI(1) base64 JSON tanpa external_url/website; belum ada situs proyek ditemukan (gate methods belum dijalankan - early lead TIDAK PERNAH di-preview/di-mint).",
    "xVerified": True,
    "xNote": "Discussion evidence ADA: Boltbook post grandtheftauto6.ai ~01:29 WIB 18 Nov (kontrak + angka live 180/20.000). BUKAN akun X proyek (X proyek belum ditemukan).",
    "userSlot": "OPEN (mintedBy(user)=0, balanceOf(user)=0, MAX_PER_WALLET 1).",
    "velocityVerified": False,
    "velocityNote": "Baseline pertama run ini (209 @ blok 134168875); belum ada previous rate -> velocity BELUM BISA lolos.",
    "lastReadBlock": 134168875, "lastReadWib": WIB,
    "runNote0131_1118": "Run 0131: EARLY LEAD dilaporkan sekali (temuan Boltbook + verifikasi on-chain run ini). BUKAN kandidat (free% 1,05% total-supply, <50%), BUKAN strong lead (<70%), umur UNVERIFIED, website UNVERIFIED. TIDAK preview/mint.",
}
snap["runNote0131_1118"] = ("Run 0131 (blok 134168552, interval ~33,2 mnt vs 0101): 1 EARLY LEAD BARU AgentEcho "
    "0xff2dac2389a6a9593209b6008d5ffa9e73aa19c2 (AGENT_ID()=registry persis, mint() no-arg nonpayable, totalSupply 209/20000, "
    "mintOpen 1, slot user TERBUKA; umur UNVERIFIED, free% UNVERIFIED, website UNVERIFIED) - dilaporkan sekali, masuk snapshot. "
    "ADRAW ditambahkan watchlist-only (299/1000, umur UNVERIFIED). STOCK AGENT 518->529 (+11, velocity GAGAL), free 47,6% - tetap EARLY. "
    "THYRK flat, slot user terpakai. Scan FAST-FAIL (Ankr 401 ke-35 berturut-turut main job). 0 kandidat, 0 strong lead, 0 track-B dibuka, 0 track-C lead.")
snap["last_run_wib"] = WIB
snap["last_run_note"] = ("Run 0131: 1 early lead baru (AgentEcho), 0 kandidat baru, 0 strong lead baru, 0 track-B dibuka, "
    "0 track-C lead/kandidat baru. Reread OK (blok 134168552, 176 calls, 0 chunk errors; retry chunk blok 134168725). "
    "HIVE 1263 flat; Bubblebruin 2620 flat (33,6%); STOCK AGENT 529 (47,6%); AgentBubble 1872; PunchCard 1306 (23,1%).")
json.dump(snap, open(BASE + "onchain-snapshot.json", "w"), indent=1)
print("merge OK; contracts now:", len(snap["contracts"]))
