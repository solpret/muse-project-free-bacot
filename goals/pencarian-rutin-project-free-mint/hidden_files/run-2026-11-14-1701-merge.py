#!/usr/bin/env python3
"""Merge run 1701 (2026-11-14) into onchain-snapshot.json.
Reads run-2026-11-14-1601-reread.json + run-2026-11-14-1631-reread.json + run-2026-11-14-1701-reread.json.
Intervals from block deltas x 0.45s. Read-only except the snapshot write. No preview/mint."""
import json

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
snap = json.load(open(BASE + "onchain-snapshot.json"))
r1601 = json.load(open(BASE + "run-2026-11-14-1601-reread.json"))
r1631 = json.load(open(BASE + "run-2026-11-14-1631-reread.json"))
r1701 = json.load(open(BASE + "run-2026-11-14-1701-reread.json"))
INT_PREV = (r1631["block"] - r1601["block"]) * 0.45 / 60.0
INT_CUR = (r1701["block"] - r1631["block"]) * 0.45 / 60.0
BLOCK = r1701["block"]
WIB = "2026-11-14 ~17:01 WIB"

MAP = {
 "WoozCode": ("totalSnippets", None),
 "MORFO": ("totalMinted", None),
 "NOISE": ("totalMinted", None),
 "DragonAgents": ("totalSupply", "freeClaimed"),
 "AngelEye-77D9": ("totalMinted", "freeMinted"),
 "AngelEye-07bD": ("totalMinted", "freeMinted"),
 "NovaRemnants": ("totalRemnants", None),
 "RaceAgents": ("totalSupply", "freeMinted"),
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
 "RAVE": ("totalMinted", "freeMinted"),
 "HANAMI": ("totalSupply", "freeMinted"),
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
    v1601, v1631, v1701 = getv(r1601, name, skey), getv(r1631, name, skey), getv(r1701, name, skey)
    note_parts = []
    if v1631 is not None and v1701 is not None:
        minted = v1701 - v1631
        rate = minted / INT_CUR
        prev_rate = None
        if v1601 is not None:
            prev_rate = (v1631 - v1601) / INT_PREV
        ratio = (rate / prev_rate) if prev_rate else None
        passes = bool(minted >= 20 and ratio is not None and ratio >= 1.5)
        if passes:
            vel_pass.append((name, minted, round(rate, 3), round(ratio, 2)))
        elif minted >= 20 and ratio is not None and ratio >= 1.0:
            vel_fail_close.append((name, minted, round(rate, 3), round(ratio, 2)))
        entry["previousTotalSupply"] = v1631
        entry[skey] = v1701
        entry["previousRatePerMin"] = round(prev_rate, 4) if prev_rate is not None else None
        entry["currentRatePerMin"] = round(rate, 4)
        entry["velocityRatio"] = round(ratio, 2) if ratio is not None else None
        entry["velocityLegPasses"] = passes
        entry["mintedInInterval"] = minted
        entry["intervalMinutes"] = round(INT_CUR, 1)
        note_parts.append(
            f"{v1631}->{v1701} (+{minted}, {rate:.3f}/mnt vs prev {round(prev_rate,3) if prev_rate is not None else 'None'} = "
            f"{round(ratio,2) if ratio is not None else 'None'}x) -> velocity {'LOLOS' if passes else 'GAGAL'}")
    elif v1701 is not None:
        entry[skey] = v1701
        note_parts.append(f"{skey} {v1701} (baseline 1631 None, velocity tidak dihitung)")
    else:
        note_parts.append(f"{skey} gagal baca run ini (nilai lama dipertahankan)")
    if fkey:
        fv = getv(r1701, name, fkey)
        if fv is not None:
            entry[fkey] = fv
            cap = entry.get("FREE_SUPPLY") or entry.get("FREE_MAX") or entry.get("FREE_CAP") or entry.get("FREE_POOL")
            if cap:
                pct = round(100.0 * fv / cap, 1)
                entry["freePctVerified"] = pct
                note_parts.append(f"free {fv}/{cap}={pct}%")
    entry["lastReadBlock"] = BLOCK
    entry["lastReadWib"] = WIB
    entry["runNote1701_1114"] = "Run 1701 (blok %d, interval %.1f mnt vs run 1631): %s" % (BLOCK, INT_CUR, "; ".join(note_parts))

# HANAMI: re-read since run 1631 but never added to snapshot -> add as watchlist-only
if "HANAMI" not in snap["contracts"] or snap["contracts"]["HANAMI"].get("address") is None:
    snap["contracts"]["HANAMI"] = {
     "address": "0x8A742EcE2a8C1dCc5dE792A062dbEe9C00A74640",
     "name": "HANAMI", "kind": "ERC721",
     "status": "watchlist-only-added-2026-11-14",
     "totalSupply": getv(r1701, "HANAMI", "totalSupply"),
     "freeMinted": getv(r1701, "HANAMI", "freeMinted"),
     "MAX_SUPPLY": getv(r1701, "HANAMI", "MAX_SUPPLY"),
     "balanceOf_user": getv(r1701, "HANAMI", "balanceOf_user"),
     "lastReadBlock": BLOCK, "lastReadWib": WIB,
     "launchNote": "Umur UNVERIFIED: belum ada waktu launch terverifikasi; pertama dibaca run 1631 (totalSupply 132).",
     "baselineNote": "Ditambahkan ke snapshot run 1701 (sudah di reread-set sejak run 1631 tapi belum pernah masuk snapshot). totalSupply 132, freeMinted 130, MAX_SUPPLY 3333; free% UNVERIFIED (tidak ada free-cap view yang dibaca); balanceOf(user)=0. BUKAN kandidat/strong lead/early lead (bukan agent-shaped terverifikasi + umur unverified).",
     "runNote1701_1114": "Run 1701 (blok %d): totalSupply 132 (1631: 132, +0), freeMinted 130; velocity GAGAL." % BLOCK,
    }

# BinanceAI-mint (track B pending)
bai = r1701["reads"]["BinanceAI-mint"]["views"]
pc = snap["pending_claims"]["binanceai.fun"]
pc.update({"launched": bai["launched"], "failed": bai["failed"], "isRefundPhase": bai["isRefundPhase"],
           "totalShares": bai["totalShares"], "tokenClaimed_user": bai["tokenClaimed_user"],
           "lastReadWib": WIB, "lastReadBlock": BLOCK})
pc["runNote1701"] = ("Run 1701: launched=0, failed=1, isRefundPhase=1, totalShares=3110, tokenClaimed(user)=0 "
                     "(blok %d) - tetap pending/refund, sudah dilaporkan sekali (fase refund), DIAM" % BLOCK)

# ORBIT track_c
orb = r1701["reads"]["ORBIT"]["views"]
tc = snap["track_c"]["ORBIT"]
tc.update({"freeClaimed": orb["freeClaimed"], "totalSupply": orb["totalSupply"],
           "lastReadWib": WIB, "lastReadBlock": BLOCK})

# RigForge track_c (lead minted by user 11 Nov; pool not open)
rg = r1701["reads"]["RigForge"]["views"]
rgt = snap["track_c"]["RigForge"]
rgt.update({"freeSharesLeft": rg["freeSharesLeft"], "openedAt": rg["openedAt"],
            "freeClaimed": rg["freeClaimed"], "freeBooked_user": rg["freeBooked_user"],
            "lastReadWib": WIB, "lastReadBlock": BLOCK})
rgt["runNote1701_1114"] = ("Run 1701 (blok %d): freeSharesLeft 659/1000 (1631: 659, tidak berubah), openedAt 0 "
                            "(pool BELUM buka), freeClaimed 341, freeBooked(wallet)=10000 RIG utuh. TIDAK ada aksi." % BLOCK)

# PIXEL FROGS: first mints now verified (126), free 4.2%
pf = r1701["reads"]["PIXEL FROGS"]["views"]
pfe = snap["contracts"]["PIXEL FROGS"]
pfe.update({"totalSupply": pf["totalSupply"], "freeMinted": pf["freeMinted"],
            "freeLeft": pf["freeLeft"], "mintOpen": pf["mintOpen"],
            "freeClaimed_user": pf["freeClaimed_user"], "balanceOf_user": pf["balanceOf_user"],
            "lastReadBlock": BLOCK, "lastReadWib": WIB})
pfe["free_pct"] = round(100.0 * pf["freeMinted"] / pf["FREE_CAP"], 1) if pf["freeMinted"] is not None else None
pfe["runNote1701_1114"] = ("Run 1701 (blok %d): totalSupply 0->126, freeMinted 126/3000 = 4,2%%, freeLeft 2874, "
                            "mintOpen 1 - FIRST MINT TERVERIFIKASI run ini (1631 masih 0). BUKAN early lead baru "
                            "(sudah dilaporkan sekali sebagai lead 15:35 + gate FAILED no-website), BUKAN strong lead "
                            "(4,2%% jauh di bawah 70%%), BUKAN kandidat. Deadline umur 24 jam 2026-11-15 15:29:57 WIB." % BLOCK)

# HAPPE AGENTS (ex-AbsurdAgentNFT) - EARLY lead, free pool already exhausted
snap["contracts"]["HAPPE AGENTS"] = {
 "address": "0x72c14121681F1133545947B0735563835CC07B67",
 "name": "HAPPE AGENTS", "symbol": "HAPPE", "kind": "ERC721",
 "status": "early-lead-reported-sold-out-2026-11-14",
 "totalMinted": 233, "freeMinted": 222, "paidMinted": 11,
 "FREE_SUPPLY": 222, "MAX_SUPPLY": 2222, "MAX_PER_WALLET": 22,
 "price": 1500000000000000, "mintOpen": 1, "mintStartTime": 1794650400,
 "nextTokenId": 234, "rewardToken": "0x4cacbe52089aa3e8312d95c89bef45d50f0047d8",
 "isEligible_user": 1, "freeClaimed_user": 0, "mintedPerWallet_user": 0, "balanceOf_user": 0,
 "firstSeenBlock": 133524416,
 "lastReadBlock": 133525500, "lastReadWib": "2026-11-14 ~17:09 WIB",
 "website": None, "gate": "website_unverified", "xVerified": False,
 "free_pct": 100.0,
 "launchNote": "Launch TERVERIFIKASI: mintStartTime() on-chain 1794650400 = 2026-11-14 17:00:00 WIB; first mints: totalMinted 0 (run 1631) -> 222 (hot-leg 16:59) -> 233 (fresh read 17:09, blok 133525500). Umur ~9 menit saat verifikasi.",
 "baselineNote": "EARLY lead dilaporkan sekali run 1701 (SUDAH sold out saat dilaporkan): agent-shaped TERVERIFIKASI (Sourcify verified 58 fns; AGENT_ID()=registry Binance persis 0x60B926...; claimFree() no-arg + FREE_SUPPLY/freeClaimed/freeMinted). Free pool HABIS 222/222 = 100% (paid 11, total 233/2222, harga paid 0,0015 BNB). Slot user: isEligible=1, freeClaimed(user)=0, TAPI pool habis -> TIDAK ADA free slot. Website UNVERIFIED (name-search + contract-address search tanpa hasil; tanpa contractURI; ABI tanpa site function; tokenURI(1)=https://happe-metadata.pages.dev/metadata/1 - metadata host saja, fetch kosong, root 404 - BUKAN website evidence per aturan interim AgentPals). X/discussion UNVERIFIED. Distinct minters tidak diketahui (Ankr getLogs 401). BUKAN kandidat/strong lead (pool habis). TIDAK PERNAH di-preview/di-mint. Jangan laporkan ulang.",
 "runNote1701_1114": "Run 1701: EARLY lead (sold out) - totalMinted 233, free 222/222 HABIS, paid 11, mintOpen 1, launch 17:00 WIB. Dilaporkan sekali run ini sebagai early lead + sold out.",
}

snap["runNote1701_1114"] = (
 "Run 1701: reread 41/41 OK blok 133524969 (295,3 dtk, interval ~31,0 mnt vs run 1631; egress lambat, semua chunk lolos setelah retry endpoint). "
 "Velocity LOLOS 4 item TAPI BUKAN kandidat: WoozCode +61 (1,97/mnt, 5,50x), NOISE +137 (4,42/mnt, 3,48x), Ledgera +22 (0,71/mnt, 3,64x), "
 "MAMI +26 (0,84/mnt, 1,98x) - WoozCode/NOISE/MAMI free%% UNVERIFIED (tanpa free view), Ledgera free 2479/5000=49,6%% (<50%%); umur keempatnya UNVERIFIED. Close-fail: %s. "
 "EARLY LEAD BARU 1: HAPPE AGENTS 0x72c14121681F1133545947B0735563835CC07B67 - launch terverifikasi 17:00 WIB, agent-shaped terverifikasi "
 "(AGENT_ID()=registry persis), first mints 0->233 - TAPI free pool SUDAH HABIS 222/222 (paid 11, harga paid 0,0015 BNB), website/X unverified. "
 "Dilaporkan sekali sebagai early lead + sold out; jangan laporkan ulang. "
 "PIXEL FROGS first mint TERVERIFIKASI (0->126, free 126/3000=4,2%%) - bukan promosi (sudah dilaporkan 15:35, gate FAILED, jauh di bawah 70%%). "
 "AgentBubble free 1416/2222=63,7%% (>=50%%) TAPI velocity GAGAL + umur UNVERIFIED -> bukan kandidat. "
 "RaceAgents/NovaRemnants/Zero/YUANBAO/NOTV/PX24 gagal baca run ini (nilai lama dipertahankan). "
 "DragonAgents free 736/888=82,9%% tapi age-excluded-2026-11-14 -> moot. WANGCAI tetap sold out 188/188. "
 "HIVE 1263 FLAT, minted-by-user. RAVE +16 (<20) velocity GAGAL, early-lead-reported, bukan promosi. HANAMI ditambahkan ke snapshot run ini (watchlist-only). "
 "0 kandidat baru, 0 strong lead baru, 0 track-B, 0 track-C lead/kandidat baru, 0 eksekusi/preview." % (vel_fail_close,))
snap["runNote1701_1114_scan"] = (
 "Scan leg FAST-FAIL run 1701: pre-flight ankr_getLogs HTTP 401 Unauthorized dalam 9,5 dtk "
 "(head 133524359, blok 133524309-133524359). Scan TIDAK dijalankan; watermark tetap 132512564; "
 "track-C 5c dilewati (tanpa output scan). Outage Ankr 401 sejak 2026-11-09 berlanjut; perlu reconnect kredensial Ankr (di luar scope job ini).")
snap["runNote1701_1114_feedshape"] = (
 "Feed Sourcify run 1701 (limit 20, top verifiedAt 2026-11-14T09:56:57Z 0x905cc94f): 7 baru vs hot-leg-seen, "
 "semuanya sudah di-shape-check hot-leg 16:59 (S1/S2 False semua, 0 hit): 0x905cc94f (9 fns, tanpa mint/quote/free/agent), "
 "0x6f4b3b51 (57 fns), 0xb59B88dd (mint+freeClaimed TAPI tanpa quote/agent), 0x71D4c374, 0x47925979, 0x051E3C6E, 0x1441f697. "
 "0 early lead baru dari feed.")
snap["runNote1701_1114_boltbook"] = (
 "Boltbook EN+ZH run 1701 (fetch ~17:03 WIB, EN 45.990 byte PULIH, ZH 46.202 byte; EN 10 alamat, ZH 10 alamat, identik). "
 "0 alamat baru vs hot-leg-seen/snapshot: 5 sudah di reread-set (LumenFindings, CPASS, SPEC, DragonAgents, B77D), "
 "0xbf30f872 sudah dicek hot-leg 16:54 (bukan sale-shape), 0x595b5849/0x8269Ea16/0xBbDd8C77/0xb8164afe (Meow Cards) sudah di hot-leg-seen/snapshot. "
 "0 early lead baru dari Boltbook run ini.")
snap["runNote1701_1114_sweep"] = (
 "Sweep EN+ZH run 1701: 0 baru. EN: Oathbots (28 Okt, age-excluded), Agentic Gangster (9 Nov, dikenal), Meow Cards (10 Nov, di snapshot), "
 "STAMP PASS 0x202dcfbC (9 Nov, sudah di snapshot) + RIGBYPASS 0xe657465f (10 Nov, sudah di snapshot) - keduanya >24 jam, bukan temuan baru. "
 "ZH: KOMA (track_c, age-excluded), First-Dollar Grove (Agent Grove, di snapshot), Agentic Gangster, AGENT ID cards 0x486d0947 (25 Okt), "
 "Subsonic Tribe/BNBmeme/BN Agent File/PIXEL PETS/Skynet (26 Okt, age-excluded). "
 "Komplemen 6a Square tercakup sweep (post Square Oathbots + AGENT ID cards, tanpa proyek baru). 6b Odaily/PANews + 6c DappBay: tidak ada gate-check yang dibutuhkan run ini, dilewati (retry run berikut bila ada proyek yang butuh gate-check).")
snap["runNote1701_1114_binanceai"] = (
 "Run 1701: binanceai.fun TIDAK BERUBAH - launched()=0, failed()=1, isRefundPhase()=1, totalShares=3110, "
 "tokenClaimed(user)=0 (blok 133524969). Status pending/refund; sudah dilaporkan sekali (fase refund), DIAM.")
snap["runNote1701_1114_bridge"] = (
 "Run 1701: bridge file dibaca read-only (mtime 2026-11-08 18:21 UTC, tidak berubah). 116 kontrak, 0 tidak ada di snapshot, "
 "7 same_owner_discarded (sama seperti hot-leg 16:59). Job ini tidak menulis bridge; temuan pelengkap scan tidak ada yang naik tier.")
snap["runNote1701_1114_pixelfrogs"] = (
 "PIXEL FROGS (PXFRG) 0x454054e55FA2D7Ba37df7F3ceA269696f19037dF - first mint TERVERIFIKASI run 1701: "
 "totalSupply 0->126 dalam ~30 menit sejak run 1631 (free 126/3000 = 4,2%%, freeLeft 2874, mintOpen 1). "
 "Launch TERVERIFIKASI 2026-11-14 15:29:57 WIB (mintStart on-chain); umur ~1,6 jam, deadline 24 jam 2026-11-15 15:29:57 WIB. "
 "Slot user: freeClaimed(user) dibaca run ini (lihat views). Website tetap UNVERIFIED (gate FAILED, sudah dilaporkan sekali 15:35). "
 "BUKAN early lead baru (sudah dilaporkan sebagai lead), BUKAN strong lead (4,2%% < 70%%), BUKAN kandidat. Tetap watchlist-only; promosi hanya bila free%% menembus 70%% + gate lolos.")
snap["runNote1701_1114_happe"] = (
 "HAPPE AGENTS (HAPPE) 0x72c14121681F1133545947B0735563835CC07B67 - EARLY lead BARU run 1701, dilaporkan sekali (sudah sold out): "
 "kontrak ini ada di reread-set sejak ~10:01 WIB sebagai pre-launch (totalMinted 0, mintOpen 0, mintStart 17:00 WIB); "
 "launch TERVERIFIKASI mintStartTime 1794650400 = 2026-11-14 17:00:00 WIB; first mints terverifikasi on-chain run ini: "
 "totalMinted 0 (1631) -> 222 (hot-leg 16:59, blok 133524416) -> 233 (fresh read 17:09, blok 133525500). "
 "Agent-shaped TERVERIFIKASI: Sourcify verified 58 fns, AGENT_ID() = registry Binance persis 0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F "
 "(desimal 552192074493313695968015109214105588393044541999 cocok), claimFree() no-arg + FREE_SUPPLY 222 + freeClaimed/freeMinted. "
 "Free pool HABIS: freeMinted 222/222 = 100%%, paidMinted 11, totalMinted 233/2222, MAX_PER_WALLET 22, price paid 0,0015 BNB. "
 "Slot user: isEligible(user)=1, freeClaimed(user)=0, mintedPerWallet(user)=0, balanceOf(user)=0 - TAPI pool habis, TIDAK ADA free slot. "
 "Website UNVERIFIED: name-search 'AbsurdAgentNFT'/'HAPPE AGENTS' tanpa hasil; contract-address search tanpa hasil; tanpa contractURI; "
 "ABI tanpa site function; tokenURI(1)=https://happe-metadata.pages.dev/metadata/1 (metadata host saja, fetch kosong, root 404) - BUKAN website evidence. "
 "X/discussion UNVERIFIED. Distinct minters tidak diketahui (Ankr getLogs 401). Status: early-lead-reported-sold-out-2026-11-14; "
 "BUKAN kandidat/strong lead; TIDAK PERNAH di-preview/di-mint; jangan laporkan ulang.")
snap["last_run_wib"] = WIB
snap["last_run_note"] = snap["runNote1701_1114"]
snap["timestamp_wib"] = WIB

json.dump(snap, open(BASE + "onchain-snapshot.json", "w"), indent=1)
print("merged. velocity LOLOS:", vel_pass)
print("velocity close-fail:", vel_fail_close)
print("interval prev/cur min:", round(INT_PREV, 2), round(INT_CUR, 2))
