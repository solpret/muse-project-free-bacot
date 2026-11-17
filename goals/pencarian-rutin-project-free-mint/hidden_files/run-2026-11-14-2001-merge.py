#!/usr/bin/env python3
"""Merge run 2001 (2026-11-14) into onchain-snapshot.json.
Reads run-2026-11-14-1901/1931/2001-reread.json + run-2026-11-14-2001-feedshape.json
+ run-2026-11-14-2001-sourcify.json (web legs by subagent). Intervals from block deltas x 0.45s.
Read-only except the snapshot write. No preview/mint.
CORRECTIONS vs 1931 boilerplate: (1) DragonAgents 0xad0d is AGE-EXCLUDED (launch <=12 Nov 06:00 WIB)
despite free 85.1% - never reported as lead, so silent removal from active watchlist.
(2) The 'deadline terdekat CRTSAINTS/0x2e50/MOONDRILL/NAPPER' lines in runNote1901/1931 were STALE
boilerplate from 12 Nov - those five were age-excluded + deleted 12 Nov 21:01-22:22; NOT repeated here.
(3) AgentPals gate verdict is FINAL (user 14 Nov ~20:21 WIB, tap 'Ya, putuskan (B)'): metadata worker
does NOT count as website evidence - applies to PARUS gate FAILED status too.
"""
import json, shutil

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
shutil.copy(BASE + "onchain-snapshot.json", BASE + "onchain-snapshot.json.bak-20261114-2001")
snap = json.load(open(BASE + "onchain-snapshot.json"))
r1901 = json.load(open(BASE + "run-2026-11-14-1901-reread.json"))
r1931 = json.load(open(BASE + "run-2026-11-14-1931-reread.json"))
r2001 = json.load(open(BASE + "run-2026-11-14-2001-reread.json"))
INT_PREV = (r1931["block"] - r1901["block"]) * 0.45 / 60.0
INT_CUR = (r2001["block"] - r1931["block"]) * 0.45 / 60.0
BLOCK = r2001["block"]
WIB = "2026-11-14 ~20:01 WIB"

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
 "HashcatDepot": ("totalMinted", None),
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
    v1901, v1931, v2001 = getv(r1901, name, skey), getv(r1931, name, skey), getv(r2001, name, skey)
    note_parts = []
    if v1931 is not None and v2001 is not None:
        minted = v2001 - v1931
        rate = minted / INT_CUR
        prev_rate = None
        if v1901 is not None:
            prev_rate = (v1931 - v1901) / INT_PREV
        ratio = (rate / prev_rate) if prev_rate else None
        passes = bool(minted >= 20 and ratio is not None and ratio >= 1.5)
        if passes:
            vel_pass.append((name, minted, round(rate, 3), round(ratio, 2)))
        elif minted >= 20 and ratio is not None and ratio >= 1.0:
            vel_fail_close.append((name, minted, round(rate, 3), round(ratio, 2)))
        entry["previousTotalSupply"] = v1931
        entry[skey] = v2001
        entry["previousRatePerMin"] = round(prev_rate, 4) if prev_rate is not None else None
        entry["currentRatePerMin"] = round(rate, 4)
        entry["velocityRatio"] = round(ratio, 2) if ratio is not None else None
        entry["velocityLegPasses"] = passes
        entry["mintedInInterval"] = minted
        entry["intervalMinutes"] = round(INT_CUR, 1)
        note_parts.append(
            f"{v1931}->{v2001} (+{minted}, {rate:.3f}/mnt vs prev {round(prev_rate,3) if prev_rate is not None else 'None'} = "
            f"{round(ratio,2) if ratio is not None else 'None'}x) -> velocity {'LOLOS' if passes else 'GAGAL'}")
    elif v2001 is not None:
        entry[skey] = v2001
        note_parts.append(f"{skey} {v2001} (baseline 1931 None, velocity tidak dihitung)")
    else:
        note_parts.append(f"{skey} gagal baca run ini (nilai lama dipertahankan)")
    if fkey:
        fv = getv(r2001, name, fkey)
        if fv is not None:
            entry[fkey] = fv
            cap = entry.get("FREE_SUPPLY") or entry.get("FREE_MAX") or entry.get("FREE_CAP") or entry.get("FREE_POOL")
            if cap:
                pct = round(100.0 * fv / cap, 1)
                entry["freePctVerified"] = pct
                note_parts.append(f"free {fv}/{cap}={pct}%")
    entry["lastReadBlock"] = BLOCK
    entry["lastReadWib"] = WIB
    entry["runNote2001_1114"] = "Run 2001 (blok %d, interval %.1f mnt vs run 1931): %s" % (BLOCK, INT_CUR, "; ".join(note_parts))

# --- DragonAgents 0xad0d: AGE-EXCLUDED correction (free 85.1% but launch <=12 Nov 06:00 WIB) ---
da = snap["contracts"]["DragonAgents"]
da["status"] = "age-excluded-2026-11-14"
da["runNote2001_1114"] = (
 "Run 2001 (blok %d): totalSupply 756->760, freeClaimed 752->756/888 = 85,1%%. KOREKSI STATUS: AGE-EXCLUDED - "
 "bukan strong lead meski free%% >70%%. Bukti umur: first-seen hot-leg 2026-11-12 05:59:51 WIB dengan freeClaimed 22/888 "
 "di blok 133053821 (sudah minting ~06:00 WIB 12 Nov); Sourcify verifiedAt 2026-11-11T22:52:03Z (12 Nov 05:52 WIB); "
 "umur saat run >=62 jam (>24 jam). Hot-leg sudah menandai age-excluded-2026-11-14; entri snapshot utama baru dikoreksi run ini. "
 "Tidak pernah dilaporkan sebagai lead (watchlist-only) -> penghapusan dari pantauan aktif DIAM sesuai aturan (tanpa laporan chat). "
 "Keluarkan dari ITEMS reread run berikut." % BLOCK)

# --- GUARD / PenjagaArusNFT (PARUS) early lead: 4 -> 83 ---
g = r2001["reads"]["GUARD"]["views"]
parus = snap["contracts"]["PenjagaArusNFT"]
free_claimed = g["freeBlock"] - g["freeRemaining"] if g["freeBlock"] is not None and g["freeRemaining"] is not None else None
parus.update({"totalMinted": g["totalMinted"], "freeRemaining": g["freeRemaining"],
              "freeBlock": g["freeBlock"], "maxSupply": g["maxSupply"],
              "mintOpenTimestamp": g["mintOpenTimestamp"], "mintPaused": g["mintPaused"],
              "lastReadBlock": BLOCK, "lastReadWib": WIB})
if free_claimed is not None:
    parus["freePctVerified"] = round(100.0 * free_claimed / g["freeBlock"], 1)
parus["runNote2001_1114"] = (
 "Run 2001 (blok %d): totalMinted 4->%s, free %s/2000 = %s%% (hot-leg 20:14: 63; +20 sejak 20:14, +79 sejak 19:31), "
 "mintPaused 0, slot user TERBUKA (freeUsed=0, mintedBy=0, balanceOf=0). Umur <24 jam (mintOpen 19:22:56 WIB 14 Nov, ~1 jam 10 mnt). "
 "Gate tetap FAILED: satu-satunya situs = metadata host parus.fcfs.workers.dev; putusan FINAL user 14 Nov ~20:21 WIB (tap 'Ya, putuskan (B)' "
 "review 3-hari AgentPals): metadata worker TIDAK dihitung sebagai bukti website. Tetap EARLY lead, TIDAK PERNAH di-preview/di-mint. "
 "Promosi hanya bila free%% menembus 70%% + gate website lolos." % (BLOCK, g["totalMinted"], free_claimed, parus.get("freePctVerified")))

# BinanceAI-mint (track B pending)
bai = r2001["reads"]["BinanceAI-mint"]["views"]
pc = snap["pending_claims"]["binanceai.fun"]
pc.update({"launched": bai["launched"], "failed": bai["failed"], "isRefundPhase": bai["isRefundPhase"],
           "totalShares": bai["totalShares"], "tokenClaimed_user": bai["tokenClaimed_user"],
           "lastReadWib": WIB, "lastReadBlock": BLOCK})
pc["runNote2001"] = ("Run 2001: launched=0, failed=1, isRefundPhase=1, totalShares=%s, tokenClaimed(user)=0 "
                     "(blok %d) - tetap pending/refund, sudah dilaporkan sekali (fase refund), DIAM" % (bai["totalShares"], BLOCK))

# ORBIT track_c
orb = r2001["reads"]["ORBIT"]["views"]
tc = snap["track_c"]["ORBIT"]
tc.update({"freeClaimed": orb["freeClaimed"], "totalSupply": orb["totalSupply"],
           "lastReadWib": WIB, "lastReadBlock": BLOCK})
tc["runNote2001_1114"] = ("Run 2001 (blok %d): freeClaimed %s/888 = %.1f%% (1931: 276, tidak berubah), claimOpen 1, "
                          "hasFreeClaimed(user)=0 - umur UNVERIFIED, website NOT CHECKED -> watchlist-only, "
                          "BUKAN lead/kandidat." % (BLOCK, orb["freeClaimed"], 100.0 * orb["freeClaimed"] / 888))

# RigForge track_c (pool not open)
rg = r2001["reads"]["RigForge"]["views"]
rgt = snap["track_c"]["RigForge"]
rgt.update({"freeSharesLeft": rg["freeSharesLeft"], "openedAt": rg["openedAt"],
            "freeClaimed": rg["freeClaimed"], "freeBooked_user": rg["freeBooked_user"],
            "lastReadWib": WIB, "lastReadBlock": BLOCK})
rgt["runNote2001_1114"] = ("Run 2001 (blok %d): freeSharesLeft %s/1000 (1931: 659, tidak berubah), openedAt 0 "
                           "(pool BELUM buka), freeClaimed %s, freeBooked(wallet)=10000 RIG utuh. TIDAK ada aksi."
                           % (BLOCK, rg["freeSharesLeft"], rg["freeClaimed"]))

# PIXEL FROGS
pf = r2001["reads"]["PIXEL FROGS"]["views"]
pfe = snap["contracts"]["PIXEL FROGS"]
pfe.update({"totalSupply": pf["totalSupply"], "freeMinted": pf["freeMinted"],
            "freeLeft": pf["freeLeft"], "mintOpen": pf["mintOpen"],
            "freeClaimed_user": pf["freeClaimed_user"], "balanceOf_user": pf["balanceOf_user"],
            "lastReadBlock": BLOCK, "lastReadWib": WIB})
pfe["free_pct"] = round(100.0 * pf["freeMinted"] / pf["FREE_CAP"], 1) if pf["freeMinted"] is not None else None
pfe["runNote2001_1114"] = ("Run 2001 (blok %d): totalSupply 275->%s, freeMinted %s/3000 = %s%%, freeLeft %s, "
                           "mintOpen 1 - BUKAN promosi (sudah dilaporkan sekali sebagai lead 15:35 + gate FAILED no-website), "
                           "BUKAN strong lead (%s%% jauh di bawah 70%%), BUKAN kandidat. Deadline umur 24 jam 2026-11-15 15:29:57 WIB."
                           % (BLOCK, pf["totalSupply"], pf["freeMinted"], pfe["free_pct"], pf["freeLeft"], pfe["free_pct"]))

# HAPPE AGENTS - EARLY lead, free pool already exhausted; update fresh values only
hap = r2001["reads"]["AbsurdAgentNFT"]["views"]
happe = snap["contracts"]["HAPPE AGENTS"]
happe.update({"totalMinted": hap["totalMinted"], "mintOpen": hap["mintOpen"],
              "mintStartTime": hap["mintStartTime"], "isEligible_user": hap["isEligible_user"],
              "lastReadBlock": BLOCK, "lastReadWib": WIB})
happe["paidMinted"] = (hap["totalMinted"] - 222) if hap["totalMinted"] is not None else happe.get("paidMinted")
happe["runNote2001_1114"] = ("Run 2001 (blok %d): totalMinted %s (1931: 239, FLAT), free pool tetap HABIS 222/222, "
                             "paid %s, mintOpen 1, launch 17:00 WIB. Status early-lead-reported-sold-out; "
                             "BUKAN kandidat/strong lead; TIDAK PERNAH di-preview/di-mint; jangan laporkan ulang."
                             % (BLOCK, hap["totalMinted"], happe["paidMinted"]))

# LumenFindings + NOISE: already age-excluded; refresh values only
lum = snap["contracts"]["LumenFindings"]
lum.update({"totalSpecimens": getv(r2001, "LumenFindings", "totalSpecimens"),
            "currentExperiment": getv(r2001, "LumenFindings", "currentExperiment"),
            "genesisStart": getv(r2001, "LumenFindings", "genesisStart"),
            "genesisOpen": getv(r2001, "LumenFindings", "genesisOpen"),
            "lastReadBlock": BLOCK, "lastReadWib": WIB})
lum["runNote2001_1114"] = ("Run 2001 (blok %d): totalSpecimens 3156->%s (+%s, velocity %s). "
                           "Tetap AGE-EXCLUDED (genesisStart 13 Nov 08:43 WIB, umur ~35 jam > 24 jam). DIAM."
                           % (BLOCK, getv(r2001, "LumenFindings", "totalSpecimens"),
                              (getv(r2001, "LumenFindings", "totalSpecimens") or 0) - 3156,
                              "LOLOS" if (getv(r2001, "LumenFindings", "totalSpecimens") or 0) - 3156 >= 20 else "GAGAL"))
nz = snap["contracts"].setdefault("NOISE", {})
nz.update({"totalMinted": getv(r2001, "NOISE", "totalMinted"),
           "remainingSupply": getv(r2001, "NOISE", "remainingSupply"),
           "mintOpen": getv(r2001, "NOISE", "mintOpen"),
           "lastReadBlock": BLOCK, "lastReadWib": WIB})
nz["runNote2001_1114"] = ("Run 2001 (blok %d): totalMinted 1208->%s (+%s, velocity GAGAL). "
                          "Tetap AGE-EXCLUDED (259 termint 05:32 13 Nov). DIAM."
                          % (BLOCK, getv(r2001, "NOISE", "totalMinted"),
                             (getv(r2001, "NOISE", "totalMinted") or 0) - 1208))

# --- Feed Sourcify: shape-check results (filled from subagent files) ---
feed = json.load(open(BASE + "run-2026-11-14-2001-feedshape.json"))
sour = json.load(open(BASE + "run-2026-11-14-2001-sourcify.json"))["results"]
feed_vat = {r["address"].lower(): r["verifiedAt"] for r in sour}
n_new = 0
for o in feed:
    addr = o["address"]
    key = "Feed-" + addr[2:6]
    if key in snap["contracts"] and snap["contracts"][key].get("status", "").startswith("checked-not-sale-shape-2026-11-14"):
        continue  # already recorded this run (should not happen; guard anyway)
    n_new += 1
    if addr.lower() == "0xb8b7ef8d49981f8987dfc271dca50e24ce87abeb":
        note = ("Feed Sourcify run 2001 (verifiedAt %s): shape-check S1=%s S2=%s (mint+quote+freeUsed+agent_ref) - "
                "kontrak ini NFT PenjagaArusNFT, BUKAN sale fungible -> sudah ditangani sebagai EARLY LEAD track A run 1931, "
                "bukan lead track C; TIDAK dilaporkan ulang." % (feed_vat.get(addr.lower(), "?"), o.get("S1"), o.get("S2")))
    else:
        note = ("Feed Sourcify run 2001 (verifiedAt %s): shape-check S1=%s S2=%s, has_mint=%s, has_quote=%s, "
                "free_views=%s, agent_ref=%s, n_fns=%s. BUKAN sale-shape, BUKAN agent-shaped. "
                "Tidak dilaporkan, tidak masuk watchlist aktif."
                % (feed_vat.get(addr.lower(), "?"), o.get("S1"), o.get("S2"), o.get("has_mint"), o.get("has_quote"),
                   o.get("free_views"), o.get("agent_ref"), o.get("n_fns")))
    snap["contracts"][key] = {
     "address": addr, "status": "checked-not-sale-shape-2026-11-14",
     "lastReadWib": WIB, "lastReadBlock": BLOCK,
     "baselineNote": note,
     "runNote2001_1114": "Run 2001: feed %s S1=%s S2=%s -> %s." % (addr[:10], o.get("S1"), o.get("S2"),
                        "early lead PenjagaArusNFT (NFT, bukan sale; sudah dilaporkan 1931)" if addr.lower() == "0xb8b7ef8d49981f8987dfc271dca50e24ce87abeb" else "bukan sale-shape"),
    }

# --- Run notes (web-leg strings patched from subagent result) ---
WEB_BOLTBOOK = 'Boltbook EN+ZH run 2001 (fetch ~20:22 WIB, EN 45.027 byte, ZH 45.354 byte; root boltbook.fun 302 ke /?lang=en). Alamat unik 10; 0 baru vs hot-leg-seen (8 juga di snapshot). 0 alamat kontrak baru dari Boltbook run ini; 0 early lead baru dari Boltbook.'
WEB_SWEEP = 'Sweep EN+ZH run 2001: 0 baru yang lolos. EN: Oathbots, ONLYAI Crystals, Agentic Gangster, STAMP PASS, RIGBYPASS, AGENT COSMOS, BLOB Miner, AGENT ID cards, Cosmic Sentinel, Periodic Lab (semua di snapshot/dikenal); ZH: UFO, NEBULA, VISION, JOLT (tutup), NOVRA + ORBITA (track_c; ORBITA sold out), PESI (terverifikasi 10 Nov), AgentVOLT (dikenal). Komplemen 6a Square tercakup sweep (tanpa proyek baru). 6b Odaily (287.141 byte, HTTP 200) + PANews (120.028 byte, HTTP 200): 0 penyebutan Agent ID/free-mint di teks terbaca (text-fetch only, halaman mungkin JS-rendered). 6c DappBay: dilewati (tidak ada proyek baru yang butuh gate-check).'
WEB_FEED = 'Feed Sourcify run 2001 (limit 20, top verifiedAt 2026-11-14T13:20:36Z 0x1469E99A, tertua 12:49:46Z): 3 benar-benar baru vs hot-leg-seen - 0x1469E99A game/boss contract (6 fns, tanpa mint/quote/free/agent), 0xa9bdAE1F ABI kosong (0 fns, unverifiable), 0x24E8C96C ERC-20 biasa dengan mint (16 fns, tanpa quote/free/agent) - ketiganya S1=False S2=False, BUKAN sale-shape, BUKAN agent-shaped. PARUS tidak ada di top 20 feed run ini (sudah dilaporkan 1931). 0 early lead baru dari feed.'

snap["runNote2001_1114"] = (
 "Run 2001: reread 42/42 OK blok %d (106,5 dtk, interval 52,6 mnt vs run 1931). "
 "Velocity LOLOS 0: terbesar CPASS +64 (prev 0 -> ratio None, free%% UNVERIFIED), NovaRemnants +60 (0,29x, melambat), "
 "WoozCode +45 (0,25x, melambat), LumenFindings +34 (0,18x, age-excluded moot), B77D +20 (1,20x, close-fail). "
 "Ledgera +19 (1,26x) velocity GAGAL; free 2621/5000=52,4%% (>50%% kaki kandidat) TAPI umur/website/X UNVERIFIED "
 "-> BUKAN kandidat dan BUKAN strong lead (52,4%% < 70%%); slot user terbuka, mintOpen 1. Tanpa promosi, tanpa eksekusi. "
 "AgentBubble freeMinted 1442/2222=64,9%% (<70%%), velocity GAGAL (+8). RaceAgents free 570/1000=57,0%%, FLAT (+2). "
 "DragonAgents free 756/888=85,1%% TAPI AGE-EXCLUDED (launch <=12 Nov 06:00 WIB, umur >=62 jam) -> BUKAN strong lead; "
 "status snapshot dikoreksi run ini, dihapus dari pantauan aktif (DIAM, tidak pernah dilaporkan sebagai lead). "
 "Zero/PX24/HashcatDepot masih gagal baca (nilai lama dipertahankan). "
 "PIXEL FROGS 275->303, free 301/3000=10,0%% - bukan promosi (gate FAILED, sudah dilaporkan 15:35). "
 "HAPPE totalMinted 239 FLAT, free pool tetap HABIS 222/222. "
 "WANGCAI/YUANBAO tetap sold out free 188/188. NOTV totalMinted masih 0. "
 "EARLY LEAD PARUS: totalMinted 4->83, free 83/2000=4,2%%, slot terbuka, gate tetap FAILED (metadata host; putusan FINAL user 20:21 WIB "
 "metadata worker bukan bukti website) - tetap EARLY, TIDAK di-preview/di-mint. "
 "0 kandidat baru, 0 strong lead baru/promosi, 0 early lead baru, 0 track-B dibuka/diblokir, 0 track-C lead/kandidat baru, 0 eksekusi/preview." % BLOCK)
snap["runNote2001_1114_scan"] = (
 "Scan leg FAST-FAIL run 2001: pre-flight ankr_getLogs HTTP 401 Unauthorized dalam 3,0 dtk "
 "(head 133551435 via dataseed). Scan TIDAK dijalankan; watermark tetap 132512564; track-C 5c dilewati (tanpa output scan). "
 "Outage Ankr 401 sejak 2026-11-09 berlanjut. CATATAN: user tap 14 Nov ~20:20 WIB 'Ya, coba RPC publik lain untuk scan' - "
 "tapi itu untuk cron tracked-wallet-mint-scan-hourly; scan leg job ini tetap Ankr-only per body ('ONLY the existing free Ankr endpoint'). "
 "Bila RPC pengganti terbukti jalan di job tracked-wallet, adopsi ke job ini butuh keputusan/persetujuan terpisah - JANGAN alihkan sendiri.")
snap["runNote2001_1114_feedshape"] = WEB_FEED
snap["runNote2001_1114_boltbook"] = WEB_BOLTBOOK
snap["runNote2001_1114_sweep"] = WEB_SWEEP
snap["runNote2001_1114_binanceai"] = (
 "Run 2001: binanceai.fun TIDAK BERUBAH - launched()=0, failed()=1, isRefundPhase()=1, totalShares=3110, "
 "tokenClaimed(user)=0 (blok %d). Status pending/refund; sudah dilaporkan sekali (fase refund), DIAM." % BLOCK)
snap["runNote2001_1114_bridge"] = (
 "Run 2001: bridge file dibaca read-only (mtime 2026-11-08 18:21 UTC, tidak berubah). 116 kontrak, 0 benar-benar belum ada di snapshot, "
 "7 same_owner_discarded. Job ini tidak menulis bridge; temuan pelengkap scan tidak ada yang naik tier.")
snap["runNote2001_1114_pixelfrogs"] = (
 "PIXEL FROGS (PXFRG) 0x454054e55FA2D7Ba37df7F3ceA269696f19037dF - run 2001: totalSupply 275->303, freeMinted 301/3000 = 10,0%%, "
 "freeLeft 2699, mintOpen 1, slot user terbuka (freeClaimed(user)=0). Launch TERVERIFIKASI 2026-11-14 15:29:57 WIB, umur ~4,5 jam, "
 "deadline 24 jam 2026-11-15 15:29:57 WIB. Website tetap UNVERIFIED (gate FAILED, sudah dilaporkan sekali 15:35). "
 "BUKAN strong lead (10,0%% < 70%%), BUKAN kandidat. Tetap watchlist-only; promosi hanya bila free%% menembus 70%% + gate lolos.")
snap["runNote2001_1114_happe"] = (
 "HAPPE AGENTS (HAPPE) 0x72c14121681F1133545947B0735563835CC07B67 - run 2001: totalMinted 239 FLAT (1931: 239), free pool tetap HABIS 222/222, "
 "paid 17, mintOpen 1, isEligible(user)=1. Status early-lead-reported-sold-out-2026-11-14 (dilaporkan sekali run 1701); "
 "BUKAN kandidat/strong lead; TIDAK PERNAH di-preview/di-mint; jangan laporkan ulang.")
snap["runNote2001_1114_ledgera"] = (
 "Ledgera 0x8d292d7d423bc48b5f1954f2c0440cfbe9dabd7d - run 2001: VELOCITY GAGAL run ini (+19, 0,361/mnt, 1,26x vs prev 0,286). "
 "freeClaimed 2621/5000=52,4%% (>50%% kaki kandidat), slot user terbuka (mintedBy 0, balanceOf 0), mintOpen 1. "
 "TAPI umur UNVERIFIED + website UNVERIFIED + X unverified -> BUKAN kandidat dan BUKAN strong lead (52,4%% < 70%%). "
 "Tanpa promosi, tanpa preview/mint. Pantau run berikut bila umur/website terverifikasi.")
snap["runNote2001_1114_parus"] = (
 "PenjagaArusNFT (PARUS) 0xB8b7eF8D49981F8987Dfc271DCa50E24ce87AbEb - run 2001: totalMinted 4->83, free 83/2000=4,2%%, "
 "mintPaused 0, slot user TERBUKA. Umur <24 jam (mintOpen 19:22:56 WIB 14 Nov). Gate tetap FAILED (metadata host parus.fcfs.workers.dev; "
 "putusan FINAL user 14 Nov ~20:21 WIB: metadata worker TIDAK dihitung sebagai bukti website). Tetap EARLY lead (dilaporkan sekali run 1931); "
 "TIDAK PERNAH di-preview/di-mint; promosi hanya bila free%% menembus 70%% + gate website lolos.")
snap["runNote2001_1114_dragonagents"] = (
 "DragonAgents 0xad0D8ac3D61fC8ab397B7136C69fcBf1281a4998 - run 2001: totalSupply 756->760, freeClaimed 756/888=85,1%%, slot user terbuka. "
 "KOREKSI: AGE-EXCLUDED (launch <= 12 Nov ~06:00 WIB; freeClaimed sudah 22/888 di blok 133053821; Sourcify verifiedAt 2026-11-11T22:52:03Z; "
 "umur >=62 jam). Hot-leg sudah menandai age-excluded-2026-11-14; snapshot utama baru dikoreksi run ini. "
 "BUKAN strong lead (kaki umur gagal) meski free%% >70%%. Tidak pernah dilaporkan sebagai lead -> DIAM, dihapus dari pantauan aktif; "
 "keluarkan dari ITEMS reread run berikut. Jangan triase ulang sebagai early/strong lead.")
snap["runNote2001_1114_age_exclusions"] = (
 "Run 2001 AGE-EXCLUSION: 1 koreksi - DragonAgents 0xad0d (lihat runNote2001_1114_dragonagents). TIDAK ADA age-exclusion baru lain. "
 "KOREKSI BOILERPLATE: baris 'deadline terdekat CRTSAINTS ~20:50 / 0x2e50 ~21:00 / MOONDRILL ~21:10 / NAPPER ~22:00' di runNote1901/1931 "
 "adalah SALAH (stale copy-paste dari 12 Nov) - kelima proyek itu SUDAH age-excluded + dihapus dari contracts pada 12 Nov 21:01-22:22 WIB "
 "(runNote2101_1112/2131_1112/2201_1112); TIDAK diulang di run ini dan TIDAK boleh dibawa ke run berikut.")
snap["last_run"] = "run-2001"
snap["last_run_wib"] = WIB
snap["last_run_note"] = snap["runNote2001_1114"]
snap["timestamp_wib"] = WIB

json.dump(snap, open(BASE + "onchain-snapshot.json", "w"), indent=1)
print("merged. velocity LOLOS:", vel_pass)
print("velocity close-fail:", vel_fail_close)
print("feed new recorded:", n_new)
print("interval prev/cur min:", round(INT_PREV, 2), round(INT_CUR, 2))
