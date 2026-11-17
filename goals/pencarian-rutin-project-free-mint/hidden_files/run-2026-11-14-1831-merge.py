#!/usr/bin/env python3
"""Merge run 1831 (2026-11-14) into onchain-snapshot.json.
Reads run-2026-11-14-1731-reread.json + run-2026-11-14-1801-reread.json + run-2026-11-14-1831-reread.json.
Intervals from block deltas x 0.45s. Read-only except the snapshot write. No preview/mint."""
import json

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
snap = json.load(open(BASE + "onchain-snapshot.json"))
r1731 = json.load(open(BASE + "run-2026-11-14-1731-reread.json"))
r1801 = json.load(open(BASE + "run-2026-11-14-1801-reread.json"))
r1831 = json.load(open(BASE + "run-2026-11-14-1831-reread.json"))
INT_PREV = (r1801["block"] - r1731["block"]) * 0.45 / 60.0
INT_CUR = (r1831["block"] - r1801["block"]) * 0.45 / 60.0
BLOCK = r1831["block"]
WIB = "2026-11-14 ~18:31 WIB"

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
    v1731, v1801, v1831 = getv(r1731, name, skey), getv(r1801, name, skey), getv(r1831, name, skey)
    note_parts = []
    if v1801 is not None and v1831 is not None:
        minted = v1831 - v1801
        rate = minted / INT_CUR
        prev_rate = None
        if v1731 is not None:
            prev_rate = (v1801 - v1731) / INT_PREV
        ratio = (rate / prev_rate) if prev_rate else None
        passes = bool(minted >= 20 and ratio is not None and ratio >= 1.5)
        if passes:
            vel_pass.append((name, minted, round(rate, 3), round(ratio, 2)))
        elif minted >= 20 and ratio is not None and ratio >= 1.0:
            vel_fail_close.append((name, minted, round(rate, 3), round(ratio, 2)))
        entry["previousTotalSupply"] = v1801
        entry[skey] = v1831
        entry["previousRatePerMin"] = round(prev_rate, 4) if prev_rate is not None else None
        entry["currentRatePerMin"] = round(rate, 4)
        entry["velocityRatio"] = round(ratio, 2) if ratio is not None else None
        entry["velocityLegPasses"] = passes
        entry["mintedInInterval"] = minted
        entry["intervalMinutes"] = round(INT_CUR, 1)
        note_parts.append(
            f"{v1801}->{v1831} (+{minted}, {rate:.3f}/mnt vs prev {round(prev_rate,3) if prev_rate is not None else 'None'} = "
            f"{round(ratio,2) if ratio is not None else 'None'}x) -> velocity {'LOLOS' if passes else 'GAGAL'}")
    elif v1831 is not None:
        entry[skey] = v1831
        note_parts.append(f"{skey} {v1831} (baseline 1801 None, velocity tidak dihitung)")
    else:
        note_parts.append(f"{skey} gagal baca run ini (nilai lama dipertahankan)")
    if fkey:
        fv = getv(r1831, name, fkey)
        if fv is not None:
            entry[fkey] = fv
            cap = entry.get("FREE_SUPPLY") or entry.get("FREE_MAX") or entry.get("FREE_CAP") or entry.get("FREE_POOL")
            if cap:
                pct = round(100.0 * fv / cap, 1)
                entry["freePctVerified"] = pct
                note_parts.append(f"free {fv}/{cap}={pct}%")
    entry["lastReadBlock"] = BLOCK
    entry["lastReadWib"] = WIB
    entry["runNote1831_1114"] = "Run 1831 (blok %d, interval %.1f mnt vs run 1801): %s" % (BLOCK, INT_CUR, "; ".join(note_parts))

# BinanceAI-mint (track B pending)
bai = r1831["reads"]["BinanceAI-mint"]["views"]
pc = snap["pending_claims"]["binanceai.fun"]
pc.update({"launched": bai["launched"], "failed": bai["failed"], "isRefundPhase": bai["isRefundPhase"],
           "totalShares": bai["totalShares"], "tokenClaimed_user": bai["tokenClaimed_user"],
           "lastReadWib": WIB, "lastReadBlock": BLOCK})
pc["runNote1831"] = ("Run 1831: launched=0, failed=1, isRefundPhase=1, totalShares=3110, tokenClaimed(user)=0 "
                     "(blok %d) - tetap pending/refund, sudah dilaporkan sekali (fase refund), DIAM" % BLOCK)

# ORBIT track_c
orb = r1831["reads"]["ORBIT"]["views"]
tc = snap["track_c"]["ORBIT"]
tc.update({"freeClaimed": orb["freeClaimed"], "totalSupply": orb["totalSupply"],
           "lastReadWib": WIB, "lastReadBlock": BLOCK})

# RigForge track_c (pool not open)
rg = r1831["reads"]["RigForge"]["views"]
rgt = snap["track_c"]["RigForge"]
rgt.update({"freeSharesLeft": rg["freeSharesLeft"], "openedAt": rg["openedAt"],
            "freeClaimed": rg["freeClaimed"], "freeBooked_user": rg["freeBooked_user"],
            "lastReadWib": WIB, "lastReadBlock": BLOCK})
rgt["runNote1831_1114"] = ("Run 1831 (blok %d): freeSharesLeft %s/1000 (1801: 659, tidak berubah), openedAt 0 "
                            "(pool BELUM buka), freeClaimed %s, freeBooked(wallet)=10000 RIG utuh. TIDAK ada aksi."
                            % (BLOCK, rg["freeSharesLeft"], rg["freeClaimed"]))

# PIXEL FROGS
pf = r1831["reads"]["PIXEL FROGS"]["views"]
pfe = snap["contracts"]["PIXEL FROGS"]
pfe.update({"totalSupply": pf["totalSupply"], "freeMinted": pf["freeMinted"],
            "freeLeft": pf["freeLeft"], "mintOpen": pf["mintOpen"],
            "freeClaimed_user": pf["freeClaimed_user"], "balanceOf_user": pf["balanceOf_user"],
            "lastReadBlock": BLOCK, "lastReadWib": WIB})
pfe["free_pct"] = round(100.0 * pf["freeMinted"] / pf["FREE_CAP"], 1) if pf["freeMinted"] is not None else None
pfe["runNote1831_1114"] = ("Run 1831 (blok %d): totalSupply 202->%s, freeMinted %s/3000 = %s%%, freeLeft %s, "
                            "mintOpen 1 - BUKAN promosi (sudah dilaporkan sekali sebagai lead 15:35 + gate FAILED no-website), "
                            "BUKAN strong lead (%s%% jauh di bawah 70%%), BUKAN kandidat. Deadline umur 24 jam 2026-11-15 15:29:57 WIB."
                            % (BLOCK, pf["totalSupply"], pf["freeMinted"], pfe["free_pct"], pf["freeLeft"], pfe["free_pct"]))

# HAPPE AGENTS - EARLY lead, free pool already exhausted; update fresh values only
hap = r1831["reads"]["AbsurdAgentNFT"]["views"]
happe = snap["contracts"]["HAPPE AGENTS"]
happe.update({"totalMinted": hap["totalMinted"], "mintOpen": hap["mintOpen"],
              "mintStartTime": hap["mintStartTime"], "isEligible_user": hap["isEligible_user"],
              "lastReadBlock": BLOCK, "lastReadWib": WIB})
happe["paidMinted"] = (hap["totalMinted"] - 222) if hap["totalMinted"] is not None else happe.get("paidMinted")
happe["runNote1831_1114"] = ("Run 1831 (blok %d): totalMinted %s (1801: 239), free pool tetap HABIS 222/222, "
                             "paid %s, mintOpen 1, launch 17:00 WIB. Status early-lead-reported-sold-out; "
                             "BUKAN kandidat/strong lead; TIDAK PERNAH di-preview/di-mint; jangan laporkan ulang."
                             % (BLOCK, hap["totalMinted"], happe["paidMinted"]))

# LumenFindings + NOISE: already age-excluded run 1801; refresh values only
lum = snap["contracts"]["LumenFindings"]
lum.update({"totalSpecimens": getv(r1831, "LumenFindings", "totalSpecimens"),
            "currentExperiment": getv(r1831, "LumenFindings", "currentExperiment"),
            "genesisStart": getv(r1831, "LumenFindings", "genesisStart"),
            "genesisOpen": getv(r1831, "LumenFindings", "genesisOpen"),
            "lastReadBlock": BLOCK, "lastReadWib": WIB})
lum["runNote1831_1114"] = ("Run 1831 (blok %d): totalSpecimens 2969->%s (+%s, velocity GAGAL). "
                            "Tetap AGE-EXCLUDED (genesisStart 13 Nov 08:43 WIB, umur ~34 jam > 24 jam). DIAM."
                            % (BLOCK, getv(r1831, "LumenFindings", "totalSpecimens"),
                               (getv(r1831, "LumenFindings", "totalSpecimens") or 0) - 2969))
nz = snap["contracts"].setdefault("NOISE", {})
nz.update({"totalMinted": getv(r1831, "NOISE", "totalMinted"),
           "remainingSupply": getv(r1831, "NOISE", "remainingSupply"),
           "mintOpen": getv(r1831, "NOISE", "mintOpen"),
           "lastReadBlock": BLOCK, "lastReadWib": WIB})
nz["runNote1831_1114"] = ("Run 1831 (blok %d): totalMinted 1163->%s (+%s, velocity GAGAL). "
                           "Tetap AGE-EXCLUDED (259 termint 05:32 13 Nov). DIAM."
                           % (BLOCK, getv(r1831, "NOISE", "totalMinted"),
                              (getv(r1831, "NOISE", "totalMinted") or 0) - 1163))

# Feed Sourcify: 7 new vs run 1801, all S1/S2 False -> checked-not-sale-shape entries
feed = json.load(open(BASE + "run-2026-11-14-1831-feedshape.json"))
feed_vat = {"0xbDcaBF218A54ae484a9F8C6edb202C8939b6EDA5": "2026-11-14T11:32:19Z",
            "0x153De4d87E22B29bC78c4365f4340a9E6bE720d8": "2026-11-14T11:31:13Z",
            "0x15927990f7167478aadc4E11CAf8762d21AAA8F1": "2026-11-14T11:30:43Z",
            "0x024899bD1C82b89Da3C52E108beB19A2CC27B378": "2026-11-14T11:27:14Z",
            "0x7ED704a0E28523bdc06198d41d831086E5c42a6F": "2026-11-14T11:18:37Z",
            "0x8A25a5929A18c132EAf47a2b497c86aD00eA5b9e": "2026-11-14T11:18:35Z",
            "0x0bfeB5c0cBd65A707E1c2b271cF206B9729f0E5d": "2026-11-14T11:11:59Z"}
for o in feed:
    addr = o["address"]
    key = "Feed-" + addr[2:6]
    snap["contracts"][key] = {
     "address": addr, "status": "checked-not-sale-shape-2026-11-14",
     "lastReadWib": WIB, "lastReadBlock": BLOCK,
     "baselineNote": ("Feed Sourcify run 1831 (verifiedAt %s): shape-check S1=%s S2=%s, has_mint=%s, has_quote=%s, "
                      "free_views=%s, agent_ref=%s, n_fns=%s. BUKAN sale-shape, BUKAN agent-shaped. "
                      "Tidak dilaporkan, tidak masuk watchlist aktif."
                      % (feed_vat.get(addr, "?"), o.get("S1"), o.get("S2"), o.get("has_mint"), o.get("has_quote"),
                         o.get("free_views"), o.get("agent_ref"), o.get("n_fns"))),
     "runNote1831_1114": "Run 1831: feed %s S1/S2 False -> bukan sale-shape." % addr[:10],
    }

snap["runNote1831_1114"] = (
 "Run 1831: reread 41/41 OK blok 133536468 (86,1 dtk, interval ~27,4 mnt vs run 1801). "
 "Velocity LOLOS 1 item: Ledgera +32 (1,170/mnt, 1,96x) - free 2567/5000=51,3%% (>50%% kandidat) TAPI umur/website/X UNVERIFIED "
 "-> BUKAN kandidat (butuh semua kaki) dan BUKAN strong lead (51,3%% < 70%%); slot user terbuka, mintOpen 1. Tanpa promosi, tanpa eksekusi. "
 "Close-fail: [('NovaRemnants', 21, 0.768, 1.22)] - free%% UNVERIFIED. AgentBubble +8 (8,8x tapi <20 token) velocity GAGAL; "
 "free 1429/2222=64,3%% (<70%%). WoozCode +25 (0,57x) velocity GAGAL; free%% UNVERIFIED. "
 "RaceAgents +1, freeMinted 567/1000=56,7%% - velocity GAGAL, umur/website/X unverified -> BUKAN kandidat/strong lead. "
 "HIVE 1263 FLAT, minted-by-user. Zero/PX24 masih gagal baca (nilai lama dipertahankan). "
 "PIXEL FROGS 202->252, free 250/3000=8,3%% - bukan promosi (gate FAILED, sudah dilaporkan 15:35). "
 "HAPPE totalMinted 239 FLAT, free pool tetap HABIS 222/222. "
 "LumenFindings +12 (age-excluded, moot). NOISE +12 (age-excluded, moot). DragonAgents +2 (age-excluded, moot). "
 "WANGCAI/YUANBAO tetap sold out free 188/188. NOTV totalMinted masih 0. "
 "0 kandidat baru, 0 strong lead baru, 0 early lead baru, 0 track-B, 0 track-C lead/kandidat baru, 0 eksekusi/preview.")
snap["runNote1831_1114_scan"] = (
 "Scan leg FAST-FAIL run 1831: pre-flight ankr_getLogs HTTP 401 Unauthorized dalam 2,5 dtk "
 "(head 133536299 via dataseed). Scan TIDAK dijalankan; watermark tetap 132512564; track-C 5c dilewati (tanpa output scan). "
 "Outage Ankr 401 sejak 2026-11-09 berlanjut; perlu reconnect kredensial Ankr (di luar scope job ini).")
snap["runNote1831_1114_feedshape"] = (
 "Feed Sourcify run 1831 (limit 20, top verifiedAt 2026-11-14T11:32:19Z 0xbDcaBF21): 7 benar-benar baru vs run 1801 "
 "(0xbDcaBF21, 0x153De4d8, 0x15927990, 0x024899bD, 0x7ED704a0, 0x8A25a592, 0x0bfeB5c0) - semuanya dicek run ini: "
 "S1=False S2=False semua (0xbDcaBF21 + 0x024899bD: mint+quote tanpa free view/agent; 0x7ED704a0: mint+agent_ref tanpa quote/free view; "
 "sisanya token biasa tanpa mint/quote/free/agent) -> BUKAN sale-shape, BUKAN agent-shaped. "
 "0 early lead baru dari feed.")
snap["runNote1831_1114_boltbook"] = (
 "Boltbook EN+ZH run 1831 (fetch ~18:3x WIB, EN 47.699 byte, ZH 48.365 byte, 50 article EN). "
 "Alamat unik 11, 0 alamat baru vs snapshot+hot-leg-seen (semua sudah dikenal: PIXEL FROGS, LumenFindings, TrashBandits, DragonAgents, "
 "gang.fun token 0xBbDd8C77, ONI 0x852f80b9, 0x3bbABBDB, 0xf4bacf30, Long Agents 0xad0d8ac3, 0x5A5Eff4e, ZH-only 0x8670e990). "
 "0 early lead baru dari Boltbook run ini.")
snap["runNote1831_1114_sweep"] = (
 "Sweep EN+ZH run 1831: 0 baru yang lolos. EN: Oathbots 0xb777c522 (Square 28 Okt, ~375 minted) -> AGE-EXCLUDED, sudah dicatat di snapshot run 1801, DIAM; "
 "Agentic Gangster (di snapshot, free pool exhausted); STAMP PASS / Meow Cards / RIGBYPASS (di snapshot, excluded); AgentForge (27 Okt, age-excluded). "
 "ZH: Agentic Gangster (sama); UFO/NEBULA (sudah terlacak, UFO tutup 12 Nov 15:05 UTC); VISION (season berakhir 9 Nov); RIGBYPASS + Meow Cards (di snapshot, excluded); "
 "Saturnagent (sold out 2000/2000, sudah dicatat run 1731). "
 "Komplemen 6a Square tercakup sweep (tanpa proyek baru). 6b Odaily/PANews + 6c DappBay: tidak ada gate-check yang dibutuhkan run ini, dilewati.")
snap["runNote1831_1114_binanceai"] = (
 "Run 1831: binanceai.fun TIDAK BERUBAH - launched()=0, failed()=1, isRefundPhase()=1, totalShares=3110, "
 "tokenClaimed(user)=0 (blok 133536468). Status pending/refund; sudah dilaporkan sekali (fase refund), DIAM.")
snap["runNote1831_1114_bridge"] = (
 "Run 1831: bridge file dibaca read-only (mtime 2026-11-08 18:21 UTC, tidak berubah). 116 kontrak, 0 benar-benar belum ada di snapshot "
 "(cek kehadiran aktual, bukan flag stale in_freebacot_snapshot), 7 same_owner_discarded. "
 "Job ini tidak menulis bridge; temuan pelengkap scan tidak ada yang naik tier.")
snap["runNote1831_1114_pixelfrogs"] = (
 "PIXEL FROGS (PXFRG) 0x454054e55FA2D7Ba37df7F3ceA269696f19037dF - run 1831: totalSupply 202->252, freeMinted 250/3000 = 8,3%%, "
 "freeLeft 2750, mintOpen 1, slot user terbuka (freeClaimed(user)=0). Launch TERVERIFIKASI 2026-11-14 15:29:57 WIB, umur ~3 jam, "
 "deadline 24 jam 2026-11-15 15:29:57 WIB. Website tetap UNVERIFIED (gate FAILED, sudah dilaporkan sekali 15:35). "
 "BUKAN strong lead (8,3%% < 70%%), BUKAN kandidat. Tetap watchlist-only; promosi hanya bila free%% menembus 70%% + gate lolos.")
snap["runNote1831_1114_happe"] = (
 "HAPPE AGENTS (HAPPE) 0x72c14121681F1133545947B0735563835CC07B67 - run 1831: totalMinted 239 FLAT (1801: 239), free pool tetap HABIS 222/222, "
 "paid 17, mintOpen 1, isEligible(user)=1. Status early-lead-reported-sold-out-2026-11-14 (dilaporkan sekali run 1701); "
 "BUKAN kandidat/strong lead; TIDAK PERNAH di-preview/di-mint; jangan laporkan ulang.")
snap["runNote1831_1114_ledgera"] = (
 "Ledgera 0x8d292d7d423bc48b5f1954f2c0440cfbe9dabd7d - run 1831: VELOCITY LOLOS (+32, 1,170/mnt, 1,96x vs prev 0,598). "
 "freeClaimed 2567/5000=51,3%% (>50%% kaki kandidat), slot user terbuka (mintedBy 0, balanceOf 0), mintOpen 1. "
 "TAPI umur UNVERIFIED + website UNVERIFIED + X unverified -> BUKAN kandidat dan BUKAN strong lead (51,3%% < 70%%). "
 "Tanpa promosi, tanpa preview/mint. Perubahan kaki saja (velocity kini LOLOS); pantau run berikut bila umur/website terverifikasi.")
snap["last_run_wib"] = WIB
snap["last_run_note"] = snap["runNote1831_1114"]
snap["timestamp_wib"] = WIB

json.dump(snap, open(BASE + "onchain-snapshot.json", "w"), indent=1)
print("merged. velocity LOLOS:", vel_pass)
print("velocity close-fail:", vel_fail_close)
print("interval prev/cur min:", round(INT_PREV, 2), round(INT_CUR, 2))
