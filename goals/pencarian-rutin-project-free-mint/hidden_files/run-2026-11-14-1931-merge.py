#!/usr/bin/env python3
"""Merge run 1931 (2026-11-14) into onchain-snapshot.json.
Fresh merge (replaces the 1901-derived merge whose note strings carried 1901 baselines).
Reads run-2026-11-14-1831/1901/1931-reread.json + run-2026-11-14-1931-feedshape.json
+ run-2026-11-14-1931-sourcify.json. Intervals from block deltas x 0.45s.
Read-only except the snapshot write. No preview/mint."""
import json

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
snap = json.load(open(BASE + "onchain-snapshot.json"))
r1831 = json.load(open(BASE + "run-2026-11-14-1831-reread.json"))
r1901 = json.load(open(BASE + "run-2026-11-14-1901-reread.json"))
r1931 = json.load(open(BASE + "run-2026-11-14-1931-reread.json"))
INT_PREV = (r1901["block"] - r1831["block"]) * 0.45 / 60.0
INT_CUR = (r1931["block"] - r1901["block"]) * 0.45 / 60.0
BLOCK = r1931["block"]
WIB = "2026-11-14 ~19:31 WIB"

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
    v1831, v1901, v1931 = getv(r1831, name, skey), getv(r1901, name, skey), getv(r1931, name, skey)
    note_parts = []
    if v1901 is not None and v1931 is not None:
        minted = v1931 - v1901
        rate = minted / INT_CUR
        prev_rate = None
        if v1831 is not None:
            prev_rate = (v1901 - v1831) / INT_PREV
        ratio = (rate / prev_rate) if prev_rate else None
        passes = bool(minted >= 20 and ratio is not None and ratio >= 1.5)
        if passes:
            vel_pass.append((name, minted, round(rate, 3), round(ratio, 2)))
        elif minted >= 20 and ratio is not None and ratio >= 1.0:
            vel_fail_close.append((name, minted, round(rate, 3), round(ratio, 2)))
        entry["previousTotalSupply"] = v1901
        entry[skey] = v1931
        entry["previousRatePerMin"] = round(prev_rate, 4) if prev_rate is not None else None
        entry["currentRatePerMin"] = round(rate, 4)
        entry["velocityRatio"] = round(ratio, 2) if ratio is not None else None
        entry["velocityLegPasses"] = passes
        entry["mintedInInterval"] = minted
        entry["intervalMinutes"] = round(INT_CUR, 1)
        note_parts.append(
            f"{v1901}->{v1931} (+{minted}, {rate:.3f}/mnt vs prev {round(prev_rate,3) if prev_rate is not None else 'None'} = "
            f"{round(ratio,2) if ratio is not None else 'None'}x) -> velocity {'LOLOS' if passes else 'GAGAL'}")
    elif v1931 is not None:
        entry[skey] = v1931
        note_parts.append(f"{skey} {v1931} (baseline 1901 None, velocity tidak dihitung)")
    else:
        note_parts.append(f"{skey} gagal baca run ini (nilai lama dipertahankan)")
    if fkey:
        fv = getv(r1931, name, fkey)
        if fv is not None:
            entry[fkey] = fv
            cap = entry.get("FREE_SUPPLY") or entry.get("FREE_MAX") or entry.get("FREE_CAP") or entry.get("FREE_POOL")
            if cap:
                pct = round(100.0 * fv / cap, 1)
                entry["freePctVerified"] = pct
                note_parts.append(f"free {fv}/{cap}={pct}%")
    entry["lastReadBlock"] = BLOCK
    entry["lastReadWib"] = WIB
    entry["runNote1931_1114"] = "Run 1931 (blok %d, interval %.1f mnt vs run 1901): %s" % (BLOCK, INT_CUR, "; ".join(note_parts))

# BinanceAI-mint (track B pending)
bai = r1931["reads"]["BinanceAI-mint"]["views"]
pc = snap["pending_claims"]["binanceai.fun"]
pc.update({"launched": bai["launched"], "failed": bai["failed"], "isRefundPhase": bai["isRefundPhase"],
           "totalShares": bai["totalShares"], "tokenClaimed_user": bai["tokenClaimed_user"],
           "lastReadWib": WIB, "lastReadBlock": BLOCK})
pc["runNote1931"] = ("Run 1931: launched=0, failed=1, isRefundPhase=1, totalShares=%s, tokenClaimed(user)=0 "
                     "(blok %d) - tetap pending/refund, sudah dilaporkan sekali (fase refund), DIAM" % (bai["totalShares"], BLOCK))

# ORBIT track_c
orb = r1931["reads"]["ORBIT"]["views"]
tc = snap["track_c"]["ORBIT"]
tc.update({"freeClaimed": orb["freeClaimed"], "totalSupply": orb["totalSupply"],
           "lastReadWib": WIB, "lastReadBlock": BLOCK})
tc["runNote1931_1114"] = ("Run 1931 (blok %d): freeClaimed %s/888 = %.1f%% (1901: 272), claimOpen 1, "
                          "hasFreeClaimed(user)=0 - umur UNVERIFIED, website NOT CHECKED -> watchlist-only, "
                          "BUKAN lead/kandidat." % (BLOCK, orb["freeClaimed"], 100.0 * orb["freeClaimed"] / 888))

# RigForge track_c (pool not open)
rg = r1931["reads"]["RigForge"]["views"]
rgt = snap["track_c"]["RigForge"]
rgt.update({"freeSharesLeft": rg["freeSharesLeft"], "openedAt": rg["openedAt"],
            "freeClaimed": rg["freeClaimed"], "freeBooked_user": rg["freeBooked_user"],
            "lastReadWib": WIB, "lastReadBlock": BLOCK})
rgt["runNote1931_1114"] = ("Run 1931 (blok %d): freeSharesLeft %s/1000 (1901: 659, tidak berubah), openedAt 0 "
                           "(pool BELUM buka), freeClaimed %s, freeBooked(wallet)=10000 RIG utuh. TIDAK ada aksi."
                           % (BLOCK, rg["freeSharesLeft"], rg["freeClaimed"]))

# PIXEL FROGS
pf = r1931["reads"]["PIXEL FROGS"]["views"]
pfe = snap["contracts"]["PIXEL FROGS"]
pfe.update({"totalSupply": pf["totalSupply"], "freeMinted": pf["freeMinted"],
            "freeLeft": pf["freeLeft"], "mintOpen": pf["mintOpen"],
            "freeClaimed_user": pf["freeClaimed_user"], "balanceOf_user": pf["balanceOf_user"],
            "lastReadBlock": BLOCK, "lastReadWib": WIB})
pfe["free_pct"] = round(100.0 * pf["freeMinted"] / pf["FREE_CAP"], 1) if pf["freeMinted"] is not None else None
pfe["runNote1931_1114"] = ("Run 1931 (blok %d): totalSupply 262->%s, freeMinted %s/3000 = %s%%, freeLeft %s, "
                           "mintOpen 1 - BUKAN promosi (sudah dilaporkan sekali sebagai lead 15:35 + gate FAILED no-website), "
                           "BUKAN strong lead (%s%% jauh di bawah 70%%), BUKAN kandidat. Deadline umur 24 jam 2026-11-15 15:29:57 WIB."
                           % (BLOCK, pf["totalSupply"], pf["freeMinted"], pfe["free_pct"], pf["freeLeft"], pfe["free_pct"]))

# HAPPE AGENTS - EARLY lead, free pool already exhausted; update fresh values only
hap = r1931["reads"]["AbsurdAgentNFT"]["views"]
happe = snap["contracts"]["HAPPE AGENTS"]
happe.update({"totalMinted": hap["totalMinted"], "mintOpen": hap["mintOpen"],
              "mintStartTime": hap["mintStartTime"], "isEligible_user": hap["isEligible_user"],
              "lastReadBlock": BLOCK, "lastReadWib": WIB})
happe["paidMinted"] = (hap["totalMinted"] - 222) if hap["totalMinted"] is not None else happe.get("paidMinted")
happe["runNote1931_1114"] = ("Run 1931 (blok %d): totalMinted %s (1901: 239), free pool tetap HABIS 222/222, "
                             "paid %s, mintOpen 1, launch 17:00 WIB. Status early-lead-reported-sold-out; "
                             "BUKAN kandidat/strong lead; TIDAK PERNAH di-preview/di-mint; jangan laporkan ulang."
                             % (BLOCK, hap["totalMinted"], happe["paidMinted"]))

# LumenFindings + NOISE: already age-excluded; refresh values only
lum = snap["contracts"]["LumenFindings"]
lum.update({"totalSpecimens": getv(r1931, "LumenFindings", "totalSpecimens"),
            "currentExperiment": getv(r1931, "LumenFindings", "currentExperiment"),
            "genesisStart": getv(r1931, "LumenFindings", "genesisStart"),
            "genesisOpen": getv(r1931, "LumenFindings", "genesisOpen"),
            "lastReadBlock": BLOCK, "lastReadWib": WIB})
lum["runNote1931_1114"] = ("Run 1931 (blok %d): totalSpecimens 3043->%s (+%s, velocity %s). "
                           "Tetap AGE-EXCLUDED (genesisStart 13 Nov 08:43 WIB, umur ~34 jam > 24 jam). DIAM."
                           % (BLOCK, getv(r1931, "LumenFindings", "totalSpecimens"),
                              (getv(r1931, "LumenFindings", "totalSpecimens") or 0) - 3043,
                              "LOLOS" if (getv(r1931, "LumenFindings", "totalSpecimens") or 0) - 3043 >= 20 else "GAGAL"))
nz = snap["contracts"].setdefault("NOISE", {})
nz.update({"totalMinted": getv(r1931, "NOISE", "totalMinted"),
           "remainingSupply": getv(r1931, "NOISE", "remainingSupply"),
           "mintOpen": getv(r1931, "NOISE", "mintOpen"),
           "lastReadBlock": BLOCK, "lastReadWib": WIB})
nz["runNote1931_1114"] = ("Run 1931 (blok %d): totalMinted 1199->%s (+%s, velocity GAGAL). "
                          "Tetap AGE-EXCLUDED (259 termint 05:32 13 Nov). DIAM."
                          % (BLOCK, getv(r1931, "NOISE", "totalMinted"),
                             (getv(r1931, "NOISE", "totalMinted") or 0) - 1199))

# --- NEW: PenjagaArusNFT early lead (route 5a Sourcify feed, S1 shape but NFT not sale) ---
snap["contracts"]["PenjagaArusNFT"] = {
 "address": "0xB8b7eF8D49981F8987Dfc271DCa50E24ce87AbEb",
 "name": "Guardian of the Currents", "symbol": "PARUS", "kind": "ERC721",
 "status": "early-lead-reported-2026-11-14",
 "firstSeenWib": "2026-11-14 ~19:31 WIB",
 "discovery": "Route 5a Sourcify feed run 1931 (verifiedAt 2026-11-14T12:25:28Z, baru vs run 1901); shape-check S1=True (mint+quote+freeUsed+agent_ref) tapi kontrak ini NFT (ERC721, tiers), BUKAN sale fungible -> ditangani sebagai early lead track A, BUKAN lead track C.",
 "agentShape": "TERVERIFIKASI: Sourcify exact_match; registry()=0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F (registry resmi Binance Agent ID); mintFree(address) + freeRemaining/freeBlock/freeUsed; price()=0.002 BNB (paid lane); tokenContract()=0x1d02c90d14e68a7bc7a19f29466bd76b5ee2332a.",
 "totalMinted": 4, "maxSupply": 10000, "freeBlock": 2000, "freeRemaining": 1996,
 "freePctVerified": 0.2, "mintPaused": 0,
 "mintOpenTimestamp": 1794658976, "mintOpenWib": "2026-11-14 19:22:56 WIB",
 "age": "VERIFIED <24 jam via mintOpenTimestamp on-chain 19:22:56 WIB 14 Nov (~25 mnt saat run); first-mint block timestamp UNVERIFIED (dataseed eth_getLogs limit/throttle; BscScan V2 free tier tidak mencakup BSC chain 56 - terkonfirmasi parent 19:35 WIB).",
 "firstMints": "4 mint oleh 4 wallet berbeda (ownerOf 1-4: 0x5ce09cba..., 0x9cb87807..., 0xf79d08df..., 0x3b8656ab...), bukan deployer (mintedBy(owner)=0); freeRemaining 1996/2000.",
 "website": None,
 "gate": "FAILED (website UNVERIFIED): satu-satunya situs yang ditemukan = metadata host parus.fcfs.workers.dev (tokenURI external_url + baseURI); root-nya halaman proyek (8.795 byte, judul 'Guardian of the Currents - PARUS') TAPI TIDAK mencetak alamat kontrak persis; /skill.md /launch.json /api/stats /api/verify /llms.txt /mint /market semua 404; tanpa tautan X/Telegram/Discord. Per aturan interim AgentPals (user 2026-11-11 ~19:36 WIB) metadata-worker host saja TIDAK cukup sebagai bukti website. Metode dicoba: (A) contract-address search - nihil; (B) Boltbook - nihil; (C) Sourcify source grep - endpoint /files 404; (G) project-name search - nihil; (I) tokenURI/external_url - metadata host saja; (J) ABI grep - tanpa fungsi website; (K) GitHub search - nihil; (E) owner group: 0xe9a232aefaa230a38bc9fec961eea19134903308 = owner yang sama dengan ONI/KIJIN/MECHA (early leads 7-11 Nov, tanpa website).",
 "xVerified": False,
 "userSlot": "TERBUKA: freeUsed(user)=false, mintedBy(user)=0, balanceOf(user)=0.",
 "tier": "Common (tokenURI #1: Tier Common, PARUS claim per season 10000).",
 "lastReadBlock": BLOCK, "lastReadWib": WIB,
 "runNote1931_1114": ("Run 1931: EARLY LEAD baru, dilaporkan sekali. Free 4/2000=0,2%% (jauh di bawah kandidat 50%% dan strong lead 70%%), "
                     "velocity belum ada baseline, umur <24 jam terverifikasi, slot user terbuka, website UNVERIFIED (gate FAILED), X unverified. "
                     "TIDAK PERNAH di-preview/di-mint (early lead). Promosi hanya bila free%% menembus 70%% + gate website lolos."),
}

# --- NEW: VISION (VSN) share sale, checked age-excluded via AirdropBuzz 9 Nov ---
snap["track_c"]["VISION"] = {
 "sale": "0x5f76cab7b054e088563d5098e17bd0dc430e61ae",
 "token": "0x5f76cab7b054e088563d5098e17bd0dc430e61ae",
 "status": "checked-age-excluded-2026-11-14",
 "name": "VISION", "symbol": "VSN",
 "lastReadWib": WIB, "lastReadBlock": BLOCK,
 "baselineNote": ("VISION (VSN) single-contract token+sale: first share free (1.000.000 VSN/share), 100.000 shares, 182 free issued saat dicek 9 Nov "
                 "(AirdropBuzz, blok 132621755), site vision-vsn.pages.dev. Alamat sale dari tautan 'VISION token and sale contract' artikel yang sama "
                 "(target bscscan.com/address/0x5f76cab7...; halaman BscScan 403 saat dibuka run ini, tidak diulang). Sale dibuka ~9 Nov -> umur >24 jam "
                 "saat run 1931 -> AGE-EXCLUDED. Tidak dilaporkan, tidak masuk watchlist aktif; jangan triase ulang."),
}

# --- Feed Sourcify: 16 new vs run 1901, shape-check results ---
feed = json.load(open(BASE + "run-2026-11-14-1931-feedshape.json"))
sour = json.load(open(BASE + "run-2026-11-14-1931-sourcify.json"))["results"]
feed_vat = {r["address"].lower(): r["verifiedAt"] for r in sour}
for o in feed:
    addr = o["address"]
    key = "Feed-" + addr[2:6]
    if addr.lower() == "0xb8b7ef8d49981f8987dfc271dca50e24ce87abeb":
        note = ("Feed Sourcify run 1931 (verifiedAt %s): shape-check S1=True S2=False (mint+quote+freeUsed+agent_ref, 54 fns) - "
                "tapi kontrak ini NFT PenjagaArusNFT, BUKAN sale fungible -> ditangani sebagai EARLY LEAD track A (lihat entri PenjagaArusNFT), "
                "bukan lead track C." % feed_vat.get(addr.lower(), "?"))
    else:
        note = ("Feed Sourcify run 1931 (verifiedAt %s): shape-check S1=%s S2=%s, has_mint=%s, has_quote=%s, "
                "free_views=%s, agent_ref=%s, n_fns=%s. BUKAN sale-shape, BUKAN agent-shaped. "
                "Tidak dilaporkan, tidak masuk watchlist aktif."
                % (feed_vat.get(addr.lower(), "?"), o.get("S1"), o.get("S2"), o.get("has_mint"), o.get("has_quote"),
                   o.get("free_views"), o.get("agent_ref"), o.get("n_fns")))
    snap["contracts"][key] = {
     "address": addr, "status": "checked-not-sale-shape-2026-11-14",
     "lastReadWib": WIB, "lastReadBlock": BLOCK,
     "baselineNote": note,
     "runNote1931_1114": "Run 1931: feed %s S1=%s S2=%s -> %s." % (addr[:10], o.get("S1"), o.get("S2"),
                        "early lead PenjagaArusNFT (NFT, bukan sale)" if addr.lower() == "0xb8b7ef8d49981f8987dfc271dca50e24ce87abeb" else "bukan sale-shape"),
    }

snap["runNote1931_1114"] = (
 "Run 1931: reread 41/41 OK blok %d (85,8 dtk, interval 31,5 mnt vs run 1901). "
 "Velocity LOLOS 3: WoozCode +107 (3,399/mnt, 4,23x), NovaRemnants +122 (3,876/mnt, 2,15x), LumenFindings +113 (3,590/mnt, 1,73x, AGE-EXCLUDED moot) - "
 "ketiganya free%% UNVERIFIED -> BUKAN kandidat dan BUKAN strong lead. "
 "Ledgera +9 (0,286/mnt, 0,33x) velocity GAGAL run ini; free 2602/5000=52,0%% (>50%% kaki kandidat) TAPI umur/website/X UNVERIFIED "
 "-> BUKAN kandidat dan BUKAN strong lead (52,0%% < 70%%); slot user terbuka, mintOpen 1. Tanpa promosi, tanpa eksekusi. "
 "AgentBubble free 1434/2222=64,5%% (<70%%), velocity GAGAL (+2). RaceAgents free 568/1000=56,8%%, FLAT. "
 "RAVE +6 (5,7x tapi <20 mint -> GAGAL). Zero/PX24 masih gagal baca (nilai lama dipertahankan). "
 "PIXEL FROGS 262->275, free 273/3000=9,1%% - bukan promosi (gate FAILED, sudah dilaporkan 15:35). "
 "HAPPE totalMinted 239 FLAT, free pool tetap HABIS 222/222. "
 "WANGCAI/YUANBAO tetap sold out free 188/188. NOTV totalMinted masih 0. "
 "EARLY LEAD BARU 1: PenjagaArusNFT (PARUS) 0xB8b7eF8D49981F8987Dfc271DCa50E24ce87AbEb - free 4/2000=0,2%%, umur <24 jam terverifikasi "
 "(mintOpen 19:22:56 WIB), slot user terbuka, website UNVERIFIED (gate FAILED, metadata host saja). Dilaporkan sekali sebagai EARLY. "
 "0 kandidat baru, 0 strong lead baru/promosi, 0 track-B dibuka/diblokir, 0 track-C lead/kandidat baru, 0 eksekusi/preview." % BLOCK)
snap["runNote1931_1114_scan"] = (
 "Scan leg FAST-FAIL run 1931: pre-flight ankr_getLogs HTTP 401 Unauthorized dalam 4,9 dtk "
 "(head 133544429 via dataseed). Scan TIDAK dijalankan; watermark tetap 132512564; track-C 5c dilewati (tanpa output scan). "
 "Outage Ankr 401 sejak 2026-11-09 berlanjut. Jalur pengganti BscScan V2 dites run ini: key VALID (chainid=1 OK) TAPI free tier TIDAK mencakup "
 "BSC chain 56 ('Free API access is not supported for this chain') - terkonfirmasi juga oleh parent ~19:35 WIB; migrasi BscScan buntu tanpa plan berbayar, "
 "JANGAN bayar tanpa perintah user. Perlu reconnect kredensial Ankr / keputusan user (di luar scope job ini).")
snap["runNote1931_1114_feedshape"] = (
 "Feed Sourcify run 1931 (limit 20, top verifiedAt 2026-11-14T12:33:33Z 0xFdb394bc): 16 benar-benar baru vs run 1901 - "
 "15 dicek S1=False S2=False semua (bukan sale-shape, bukan agent-shaped); 1 S1=True = PenjagaArusNFT 0xB8b7eF8D (mint+quote+freeUsed+agent_ref, 54 fns) "
 "tapi kontraknya NFT (ERC721 tiers) -> EARLY LEAD track A, bukan lead track C. "
 "0 early lead lain dari feed.")
snap["runNote1931_1114_boltbook"] = (
 "Boltbook EN+ZH run 1931 (fetch ~19:33 WIB, EN 45.954 byte, ZH 46.155 byte). "
 "Alamat unik 12; 3 'baru' vs snapshot ternyata prefix hash transaksi, BUKAN kontrak: tx klaim BOLT notefound.ai, tx mint MAMI shikifujin.ai, "
 "tx klaim OBSCURA Passkey #81 send.ai (kontrak OBSCURA 0x44a6c3b3 sudah di snapshot sejak 6 Nov, first mint 4 Nov -> age-excluded, DIAM). "
 "0 alamat kontrak baru dari Boltbook run ini; 0 early lead baru dari Boltbook.")
snap["runNote1931_1114_sweep"] = (
 "Sweep EN+ZH run 1931: 0 baru yang lolos. EN: Oathbots (Square 28 Okt, age-excluded, di snapshot); Agentic Gangster (di snapshot, free pool exhausted); "
 "STAMP PASS / Meow Cards / RIGBYPASS (di snapshot, excluded); AGENT COSMOS (5 Nov, di snapshot). ZH: UFO (tutup 12 Nov 15:05 UTC + butuh permit X-post, "
 "age-excluded); NEBULA (minted-by-user 11 Nov, di snapshot); VISION (dicek 9 Nov, 182 free issued, sale ~9 Nov -> age-excluded, dicatat track_c VISION); "
 "JOLT (season tutup 9 Nov); HOPKIN (7 Nov, butuh puzzle+X unlock, age-excluded); Periodic Lab (di snapshot via bridge). "
 "Komplemen 6a Square tercakup sweep (tanpa proyek baru). 6b Odaily/PANews + 6c DappBay: tidak ada gate-check yang dibutuhkan run ini, dilewati.")
snap["runNote1931_1114_binanceai"] = (
 "Run 1931: binanceai.fun TIDAK BERUBAH - launched()=0, failed()=1, isRefundPhase()=1, totalShares=3110, "
 "tokenClaimed(user)=0 (blok %d). Status pending/refund; sudah dilaporkan sekali (fase refund), DIAM." % BLOCK)
snap["runNote1931_1114_bridge"] = (
 "Run 1931: bridge file dibaca read-only (mtime 2026-11-08 18:21 UTC, tidak berubah). 116 kontrak, 0 benar-benar belum ada di snapshot, "
 "7 same_owner_discarded. Job ini tidak menulis bridge; temuan pelengkap scan tidak ada yang naik tier.")
snap["runNote1931_1114_pixelfrogs"] = (
 "PIXEL FROGS (PXFRG) 0x454054e55FA2D7Ba37df7F3ceA269696f19037dF - run 1931: totalSupply 262->275, freeMinted 273/3000 = 9,1%%, "
 "freeLeft 2727, mintOpen 1, slot user terbuka (freeClaimed(user)=0). Launch TERVERIFIKASI 2026-11-14 15:29:57 WIB, umur ~4 jam, "
 "deadline 24 jam 2026-11-15 15:29:57 WIB. Website tetap UNVERIFIED (gate FAILED, sudah dilaporkan sekali 15:35). "
 "BUKAN strong lead (9,1%% < 70%%), BUKAN kandidat. Tetap watchlist-only; promosi hanya bila free%% menembus 70%% + gate lolos.")
snap["runNote1931_1114_happe"] = (
 "HAPPE AGENTS (HAPPE) 0x72c14121681F1133545947B0735563835CC07B67 - run 1931: totalMinted 239 FLAT (1901: 239), free pool tetap HABIS 222/222, "
 "paid 17, mintOpen 1, isEligible(user)=1. Status early-lead-reported-sold-out-2026-11-14 (dilaporkan sekali run 1701); "
 "BUKAN kandidat/strong lead; TIDAK PERNAH di-preview/di-mint; jangan laporkan ulang.")
snap["runNote1931_1114_ledgera"] = (
 "Ledgera 0x8d292d7d423bc48b5f1954f2c0440cfbe9dabd7d - run 1931: VELOCITY GAGAL run ini (+9, 0,286/mnt, 0,33x vs prev 0,870). "
 "freeClaimed 2602/5000=52,0%% (>50%% kaki kandidat), slot user terbuka (mintedBy 0, balanceOf 0), mintOpen 1. "
 "TAPI umur UNVERIFIED + website UNVERIFIED + X unverified -> BUKAN kandidat dan BUKAN strong lead (52,0%% < 70%%). "
 "Tanpa promosi, tanpa preview/mint. Pantau run berikut bila umur/website terverifikasi.")
snap["last_run_wib"] = WIB
snap["last_run_note"] = snap["runNote1931_1114"]
snap["timestamp_wib"] = WIB

json.dump(snap, open(BASE + "onchain-snapshot.json", "w"), indent=1)
print("merged. velocity LOLOS:", vel_pass)
print("velocity close-fail:", vel_fail_close)
print("interval prev/cur min:", round(INT_PREV, 2), round(INT_CUR, 2))
