#!/usr/bin/env python3
"""Merge run 1531 (2026-11-14) into onchain-snapshot.json.
Reads run-2026-11-14-1431-reread.json + run-2026-11-14-1501-reread.json + run-2026-11-14-1531-reread.json.
CORRECTION: snapshot rate fields lagged (run 1501 merge did not update them; stored rates are
from run 1431, e.g. NOISE/B77D currentRatePerMin 0.3598 = interval 1401->1431). True previous
rates are recomputed here from 1431->1501 reread JSONs (4129 blocks x 0.45s = 30.97 min).
Current interval 1501->1531: 4725 blocks x 0.45s = 35.44 min.
Read-only except the snapshot write. No preview/mint."""
import json

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
snap = json.load(open(BASE + "onchain-snapshot.json"))
r1431 = json.load(open(BASE + "run-2026-11-14-1431-reread.json"))
r1501 = json.load(open(BASE + "run-2026-11-14-1501-reread.json"))
r1531 = json.load(open(BASE + "run-2026-11-14-1531-reread.json"))
INT_PREV = (r1501["block"] - r1431["block"]) * 0.45 / 60.0   # 30.97
INT_CUR = (r1531["block"] - r1501["block"]) * 0.45 / 60.0   # 35.44
BLOCK = r1531["block"]
WIB = "2026-11-14 ~15:42 WIB"

MAP = {
 "WoozCode": ("totalSnippets", None),
 "MORFO": ("totalMinted", None),
 "NOISE": ("totalMinted", None),
 "DragonAgents": ("totalSupply", "freeClaimed"),
 "AngelEye-77D9": ("totalMinted", "freeMinted"),
 "AngelEye-07bD": ("totalMinted", "freeMinted"),
 "NovaRemnants": ("totalRemnants", None),
 "RaceAgents": ("totalSupply", "freeMinted"),
 "AbsurdAgentNFT": ("totalMinted", None),
 "B77D": ("totalMinted", None),
 "Zero": ("totalSupply", "freeClaimed"),
 "HIVE": ("totalSupply", None),
 "AgentZENITH": ("totalSupply", None),
 "AgentNOVA": ("totalSupply", None),
 "SPARKS": ("totalMinted", None),
 "AgentBubble": ("totalSupply", "freeMinted"),
 "WANGCAI": ("totalSupply", "freeClaimed"),
 "YUANBAO": ("totalSupply", "freeClaimed"),
 "NOTV": ("totalSupply", None),
 "PX24": ("totalSupply", "freeClaimed"),
 "Zephyra": ("totalMinted", None),
 "LumenFindings": ("totalSpecimens", None),
 "Pengu": ("totalMinted", "freeMinted"),
 "CPASS": ("totalMinted", None),
 "SPEC": ("totalSpecimens", None),
 "TrashBandits": ("totalMinted", None),
 "SKRR": ("totalSupply", "freeClaimed"),
 "REOPIR": ("totalSupply", "freeClaimed"),
 "FrieAgent-B751": ("totalSupply", None),
 "FrieAgent-c64d": ("totalSupply", None),
 "Ledgera": ("totalSupply", "freeClaimed"),
 "MAMI": ("totalSupply", "freeClaimed"),
 "INKI": ("totalSupply", "freeClaimed"),
 "HashcatDepot": ("totalSupply", None),
 "OTV": ("totalSupply", None),
}
KEYMAP = {"HIVE": "HIVE Agents"}

def getv(rd, name, key):
    try:
        return rd["reads"][name]["views"].get(key)
    except Exception:
        return None

vel_pass, vel_fail_close = [], []
for name, (skey, fkey) in MAP.items():
    sname = KEYMAP.get(name, name)
    entry = snap["contracts"].setdefault(sname, {})
    v1431, v1501, v1531 = getv(r1431, name, skey), getv(r1501, name, skey), getv(r1531, name, skey)
    note_parts = []
    if v1501 is not None and v1531 is not None:
        minted = v1531 - v1501
        rate = minted / INT_CUR
        prev_rate = None
        if v1431 is not None:
            prev_rate = (v1501 - v1431) / INT_PREV
        ratio = (rate / prev_rate) if prev_rate else None
        passes = bool(minted >= 20 and ratio is not None and ratio >= 1.5)
        if passes:
            vel_pass.append((name, minted, round(rate, 3), round(ratio, 2)))
        elif minted >= 20 and ratio is not None and ratio >= 1.0:
            vel_fail_close.append((name, minted, round(rate, 3), round(ratio, 2)))
        entry["previousTotalSupply"] = v1501
        entry[skey] = v1531
        entry["previousRatePerMin"] = round(prev_rate, 4) if prev_rate is not None else None
        entry["currentRatePerMin"] = round(rate, 4)
        entry["velocityRatio"] = round(ratio, 2) if ratio is not None else None
        entry["velocityLegPasses"] = passes
        entry["mintedInInterval"] = minted
        entry["intervalMinutes"] = round(INT_CUR, 1)
        note_parts.append(
            f"{v1501}->{v1531} (+{minted}, {rate:.3f}/mnt vs prev {round(prev_rate,3) if prev_rate is not None else 'None'} = "
            f"{round(ratio,2) if ratio is not None else 'None'}x) -> velocity {'LOLOS' if passes else 'GAGAL'}")
    elif v1531 is not None:
        entry[skey] = v1531
        note_parts.append(f"{skey} {v1531} (baseline 1501 None, velocity tidak dihitung)")
    else:
        note_parts.append(f"{skey} gagal baca run ini (nilai lama dipertahankan)")
    if fkey:
        fv = getv(r1531, name, fkey)
        if fv is not None:
            entry[fkey] = fv
            cap = entry.get("FREE_SUPPLY") or entry.get("FREE_MAX") or entry.get("FREE_CAP") or entry.get("FREE_POOL")
            if cap:
                pct = round(100.0 * fv / cap, 1)
                entry["freePctVerified"] = pct
                note_parts.append(f"free {fv}/{cap}={pct}%")
    entry["lastReadBlock"] = BLOCK
    entry["lastReadWib"] = WIB
    entry["runNote1531_1114"] = "Run 1531 (blok %d, interval %.1f mnt vs run 1501): %s" % (BLOCK, INT_CUR, "; ".join(note_parts))

# BinanceAI-mint (track B pending)
bai = r1531["reads"]["BinanceAI-mint"]["views"]
pc = snap["pending_claims"]["binanceai.fun"]
pc.update({"launched": bai["launched"], "failed": bai["failed"], "isRefundPhase": bai["isRefundPhase"],
           "totalShares": bai["totalShares"], "tokenClaimed_user": bai["tokenClaimed_user"],
           "lastReadWib": WIB, "lastReadBlock": BLOCK})

# ORBIT track_c
orb = r1531["reads"]["ORBIT"]["views"]
tc = snap["track_c"]["ORBIT"]
tc.update({"freeClaimed": orb["freeClaimed"], "totalSupply": orb["totalSupply"],
           "lastReadWib": WIB, "lastReadBlock": BLOCK})

# HashcatDepot: add watchlist-only entry (checked run 1431, missing from snapshot)
snap["contracts"]["HashcatDepot"] = {
 "address": "0x5aff123300685b6e08aa4396227baf44aabbd4ed",
 "name": "HashcatDepot", "symbol": "HADE", "kind": "ERC721",
 "status": "watchlist-only-checked-not-lead-2026-11-14",
 "totalSupply": getv(r1531, "HashcatDepot", "totalSupply"),
 "MAX_SUPPLY": 1125, "mintOpen": 1,
 "mintedBy_user": 0, "balanceOf_user": 0,
 "lastReadBlock": BLOCK, "lastReadWib": WIB,
 "baselineNote": "Temuan Boltbook run 1431 (3 post, 146-152/1.125): Sourcify exact_match 34 fns (mint/mintWithAgentTokenId/costOf/mintedBy/mintsLeft) TAPI tanpa free view + registry bytes TIDAK ada -> free% UNVERIFIED; first-mint TIDAK terverifikasi (getLogs gagal semua endpoint kecuali jendela 133491000-133491999 = 0 log); tokenURI(1)=https://hashcatdepot.668823.xyz/meta/1.json. BUKAN early lead (bukan agent-shaped + first mint unverified). Ditambahkan ke snapshot run 1531 (sebelumnya hanya di run log 1431).",
 "runNote1531_1114": "Run 1531 (blok %d): totalSupply 182->221 (+39, %.3f/mnt vs prev 0,775 = 1,42x <1,5x) -> velocity GAGAL tipis; free%% UNVERIFIED; bukan kandidat/strong lead." % (BLOCK, 39 / INT_CUR),
 "currentRatePerMin": round(39 / INT_CUR, 4),
 "previousRatePerMin": round((182 - 158) / INT_PREV, 4),
 "velocityLegPasses": False, "velocityRatio": 1.42,
 "mintedInInterval": 39, "intervalMinutes": round(INT_CUR, 1),
}

# PIXEL FROGS (PXFRG) 0x4540... - just launched 15:29:57 WIB, 0 mints
snap["contracts"]["PIXEL FROGS"] = {
 "address": "0x454054e55FA2D7Ba37df7F3ceA269696f19037dF",
 "name": "PIXEL FROGS", "symbol": "PXFRG", "kind": "ERC721",
 "status": "watchlist-only-just-launched-2026-11-14",
 "totalSupply": 0, "totalPaid": 0, "freeMinted": 0, "freeLeft": 3000,
 "FREE_CAP": 3000, "MAX_SUPPLY": 8000, "PRICE": 600000000000000,
 "mintOpen": 1, "mintStart": 1794644997, "mintEnd": 1794904197,
 "agentId": "0x60b9262456de011f7d15a54cdd8c48baaa8b022f",
 "poolBalance": 0, "claimDeadline": 1795508997,
 "freeClaimed_user": False, "claimable_user": 0, "paidLeftFor_user": 30,
 "quote_1": 600000000000000,
 "firstSeenBlock": 133512559,
 "lastReadBlock": 133513090, "lastReadWib": "2026-11-14 ~15:38 WIB",
 "website": None, "gate": "website_unverified",
 "free_pct": 0.0,
 "launchNote": "Launch TERVERIFIKASI: mintStart() on-chain 1794644997 = 2026-11-14 15:29:57 WIB; mintEnd 2026-11-17 15:29:57 WIB. Umur ~9 menit saat verifikasi run 1531. Deadline 24 jam 2026-11-15 15:29:57 WIB.",
 "baselineNote": "BARU dari poll feed Sourcify limit 20 run 1531 (verifiedAt 08:30:23Z, S1-shape-hit hot-leg 15:29: S1=true mint+quote+freeClaimed/freeLeft+registry). Sourcify exact_match 61 fns; agentId()=registry Binance persis -> agent-shaped TERVERIFIKASI. On-chain run ini (blok 133513090): totalSupply 0 = freeMinted 0 (BELUM ADA mint pertama), freeLeft 3000/3000 = 0% (jauh di bawah 50%/70%), mintOpen 1, freeClaimed(user)=false (slot TERBUKA), PRICE 0,0006 BNB (paid lane). BUKAN early lead (first mint belum terverifikasi - totalSupply 0), BUKAN kandidat/strong lead (0%), BUKAN track-C lead (kontrak NFT ERC-721 ownerOf/tokenURI, bukan fungible share sale - S1 di sini false positive heuristik). TIDAK PERNAH di-preview/di-mint. Website UNVERIFIED (pencarian nama 'PIXEL FROGS'/'PXFRG' tanpa hasil; tokenURI(1) revert karena belum ada token; tanpa contractURI). Watchlist-only untuk tracking velocity + first mint.",
 "source": "Sourcify feed run 1531 + hot-leg 15:29 S1 hit",
}

snap["runNote1531_1114"] = (
 "Run 1531: reread 37/37 OK blok 133513500 (163,1 dtk, interval ~35,4 mnt vs run 1501). "
 "KOREKSI rate: field rate snapshot lag 1 run (run 1501 tidak update rate); rate prev dihitung ulang dari reread JSON 1431->1501 (4129 blok, 31,0 mnt). "
 "Velocity LOLOS 4 item TAPI free%% UNVERIFIED semua -> BUKAN kandidat/strong lead: NOISE +114 (3,22/mnt, 2,69x vs prev 1,195); "
 "NovaRemnants +156 (4,40/mnt, 4,26x vs prev 1,033); WoozCode +37 (1,04/mnt, 5,39x vs prev 0,194; umur TERVERIFIKASI genesisStart 02:07 WIB, website woozcode.fun TERVERIFIKASI, tapi free%% UNVERIFIED); "
 "AgentZENITH +26 (0,73/mnt, 5,68x vs prev 0,129). "
 "B77D +30 TAPI ratio 0,62x (prev 1,356) -> velocity GAGAL (bukan 2,36x dari field lama yang basi). HashcatDepot +39 ratio 1,42x -> GAGAL tipis. "
 "AgentBubble free 1414/2222=63,6% (>=50%) TAPI velocity GAGAL (+7, 0,20/mnt) + umur UNVERIFIED -> bukan kandidat. "
 "RaceAgents free 559/1000=55,9% TAPI velocity GAGAL (+19 <20). Ledgera free 2450/5000=49,0% (<50%), velocity GAGAL (+12). "
 "DragonAgents free 733/888=82,6% tapi age-excluded-2026-11-14 -> moot. WANGCAI+YUANBAO tetap sold out 188/188 (sudah dilaporkan). "
 "HIVE 1263 FLAT, minted-by-user. ORBIT track_c free 252/888=28,4%, umur UNVERIFIED -> watchlist-only. "
 "0 kandidat baru, 0 strong lead baru, 0 early lead baru, 0 track-B, 0 track-C lead/kandidat baru, 0 eksekusi/preview. DIAM (aturan diam).")
snap["runNote1531_1114_scan"] = (
 "Scan leg FAST-FAIL run 1531: pre-flight ankr_getLogs HTTP 401 Unauthorized dalam 27,6 dtk "
 "(head 133513669, blok 133513619-133513669). Scan TIDAK dijalankan; watermark tetap 132512564; "
 "track-C 5c dilewati (tanpa output scan). Outage Ankr 401 sejak 2026-11-09 berlanjut; perlu reconnect kredensial Ankr (di luar scope job ini).")
snap["runNote1531_1114_feedshape"] = (
 "Feed Sourcify run 1531 (limit 20, top verifiedAt 08:32:34Z): 1 baru vs hot-leg-seen = 0xC09652CE2354DF62b67034435d78843f926214BD "
 "(17 fns buy/feeWallet/referrer/shares/sold/treasury, TANPA mint/quote/free view/registry -> BUKAN agent-shaped, bukan S1/S2, dicatat checked). "
 "S1-hit hot-leg 15:29 0x454054e55FA2D7Ba37df7F3ceA269696f19037dF (PIXEL FROGS) diverifikasi on-chain run ini (lihat entri PIXEL FROGS): "
 "agent-shaped, baru launch 15:29:57 WIB, 0 mint -> watchlist-only, BUKAN early lead/kandidat/strong lead/track-C.")
snap["runNote1531_1114_boltbook"] = (
 "Boltbook EN+ZH run 1531 (fetch ~15:40 WIB, EN 45.519 byte PULIH setelah 0 byte di hot-leg 15:24/15:29, ZH 45.120 byte; EN 8 alamat, ZH 11 alamat, semua sudah di hot-leg-seen). "
 "Post segar: ICE 0x055998e3 (14 klaim gratis, cap 5.000) + Spelunkers/CAVE 0xF8654BB7 (144/5.000, freeMint sims PASS, site reuniakbarpunk212-arch.github.io/spelunkers) "
 "-> keduanya S1/S2 False + agent_ref False (dicek hot-leg 13:39) -> BUKAN agent-shaped, bukan lead. "
 "Drift Agent 0x7af5a52a (4.901/5.001, 98%) -> sudah checked-not-agent-shaped run 1731 13 Nov, tidak dilaporkan ulang. "
 "0 early lead baru dari Boltbook run ini.")
snap["runNote1531_1114_sweep"] = (
 "Sweep EN+ZH run 1531: 0 baru. EN: Oathbots (28 Okt, age-excluded), Agentic Gangster (9 Nov, dikenal), LeadLoop/Hundred/hackou/Rickshaw/AgentForge (25-27 Okt, age-excluded). "
 "ZH: KOMA (sale 11 Nov 22:00 WIB, age-excluded), UFO/NEBULA (track_c, UFO tutup 12 Nov). "
 "Komplemen 6b: Odaily/PANews 0 pengumuman Agent ID baru (hasil: Square/AirdropBuzz/thecolony/Medium lama). 6a Square tercakup sweep. 6c DappBay: tidak ada proyek yang butuh gate-check run ini.")
snap["runNote1531_1114_binanceai"] = (
 "Run 1531: binanceai.fun TIDAK BERUBAH - launched()=0, failed()=1, isRefundPhase()=1, totalShares=3110, "
 "tokenClaimed(user)=0 (blok 133513500). Status pending/refund; sudah dilaporkan sekali (fase refund), DIAM.")
snap["runNote1531_1114_bridge"] = (
 "Run 1531: bridge file tidak berubah (mtime 2026-11-08 18:21 UTC). 116 kontrak, 0 baru vs run 1501. "
 "Job ini tidak menulis bridge; temuan pelengkap scan tidak ada yang naik tier.")
snap["runNote1531_1114_pixelfrogs"] = (
 "PIXEL FROGS (PXFRG) 0x454054e55FA2D7Ba37df7F3ceA269696f19037dF - BARU run 1531, watchlist-only (BUKAN lead): "
 "agent-shaped TERVERIFIKASI (agentId()=registry persis, Sourcify exact_match 61 fns), launch TERVERIFIKASI mintStart 15:29:57 WIB, "
 "tapi totalSupply 0 (belum ada mint pertama) + free 0/3000 = 0% -> bukan early lead (first mint belum terverifikasi), bukan kandidat/strong lead. "
 "Website UNVERIFIED (name-search tanpa hasil). Slot user terbuka (freeClaimed=false). Dipantau run berikut; promosi hanya bila first mint terverifikasi + kaki terpenuhi.")
snap["last_run_wib"] = WIB
snap["last_run_note"] = snap["runNote1531_1114"]
snap["timestamp_wib"] = WIB

json.dump(snap, open(BASE + "onchain-snapshot.json", "w"), indent=1)
print("merged. velocity LOLOS:", vel_pass)
print("velocity close-fail:", vel_fail_close)
print("interval prev/cur min:", round(INT_PREV, 2), round(INT_CUR, 2))
