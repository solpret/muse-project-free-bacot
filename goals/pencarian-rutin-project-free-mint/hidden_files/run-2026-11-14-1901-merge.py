#!/usr/bin/env python3
"""Merge run 1901 (2026-11-14) into onchain-snapshot.json.
Reads run-2026-11-14-1801-reread.json + run-2026-11-14-1831-reread.json + run-2026-11-14-1901-reread.json.
Intervals from block deltas x 0.45s. Read-only except the snapshot write. No preview/mint."""
import json

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
snap = json.load(open(BASE + "onchain-snapshot.json"))
r1731 = json.load(open(BASE + "run-2026-11-14-1801-reread.json"))
r1801 = json.load(open(BASE + "run-2026-11-14-1831-reread.json"))
r1901 = json.load(open(BASE + "run-2026-11-14-1901-reread.json"))
INT_PREV = (r1801["block"] - r1731["block"]) * 0.45 / 60.0
INT_CUR = (r1901["block"] - r1801["block"]) * 0.45 / 60.0
BLOCK = r1901["block"]
WIB = "2026-11-14 ~19:01 WIB"

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
    v1731, v1801, v1901 = getv(r1731, name, skey), getv(r1801, name, skey), getv(r1901, name, skey)
    note_parts = []
    if v1801 is not None and v1901 is not None:
        minted = v1901 - v1801
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
        entry[skey] = v1901
        entry["previousRatePerMin"] = round(prev_rate, 4) if prev_rate is not None else None
        entry["currentRatePerMin"] = round(rate, 4)
        entry["velocityRatio"] = round(ratio, 2) if ratio is not None else None
        entry["velocityLegPasses"] = passes
        entry["mintedInInterval"] = minted
        entry["intervalMinutes"] = round(INT_CUR, 1)
        note_parts.append(
            f"{v1801}->{v1901} (+{minted}, {rate:.3f}/mnt vs prev {round(prev_rate,3) if prev_rate is not None else 'None'} = "
            f"{round(ratio,2) if ratio is not None else 'None'}x) -> velocity {'LOLOS' if passes else 'GAGAL'}")
    elif v1901 is not None:
        entry[skey] = v1901
        note_parts.append(f"{skey} {v1901} (baseline 1801 None, velocity tidak dihitung)")
    else:
        note_parts.append(f"{skey} gagal baca run ini (nilai lama dipertahankan)")
    if fkey:
        fv = getv(r1901, name, fkey)
        if fv is not None:
            entry[fkey] = fv
            cap = entry.get("FREE_SUPPLY") or entry.get("FREE_MAX") or entry.get("FREE_CAP") or entry.get("FREE_POOL")
            if cap:
                pct = round(100.0 * fv / cap, 1)
                entry["freePctVerified"] = pct
                note_parts.append(f"free {fv}/{cap}={pct}%")
    entry["lastReadBlock"] = BLOCK
    entry["lastReadWib"] = WIB
    entry["runNote1901_1114"] = "Run 1901 (blok %d, interval %.1f mnt vs run 1831): %s" % (BLOCK, INT_CUR, "; ".join(note_parts))

# BinanceAI-mint (track B pending)
bai = r1901["reads"]["BinanceAI-mint"]["views"]
pc = snap["pending_claims"]["binanceai.fun"]
pc.update({"launched": bai["launched"], "failed": bai["failed"], "isRefundPhase": bai["isRefundPhase"],
           "totalShares": bai["totalShares"], "tokenClaimed_user": bai["tokenClaimed_user"],
           "lastReadWib": WIB, "lastReadBlock": BLOCK})
pc["runNote1901"] = ("Run 1901: launched=0, failed=1, isRefundPhase=1, totalShares=3110, tokenClaimed(user)=0 "
                     "(blok %d) - tetap pending/refund, sudah dilaporkan sekali (fase refund), DIAM" % BLOCK)

# ORBIT track_c
orb = r1901["reads"]["ORBIT"]["views"]
tc = snap["track_c"]["ORBIT"]
tc.update({"freeClaimed": orb["freeClaimed"], "totalSupply": orb["totalSupply"],
           "lastReadWib": WIB, "lastReadBlock": BLOCK})

# RigForge track_c (pool not open)
rg = r1901["reads"]["RigForge"]["views"]
rgt = snap["track_c"]["RigForge"]
rgt.update({"freeSharesLeft": rg["freeSharesLeft"], "openedAt": rg["openedAt"],
            "freeClaimed": rg["freeClaimed"], "freeBooked_user": rg["freeBooked_user"],
            "lastReadWib": WIB, "lastReadBlock": BLOCK})
rgt["runNote1901_1114"] = ("Run 1901 (blok %d): freeSharesLeft %s/1000 (1831: 659, tidak berubah), openedAt 0 "
                            "(pool BELUM buka), freeClaimed %s, freeBooked(wallet)=10000 RIG utuh. TIDAK ada aksi."
                            % (BLOCK, rg["freeSharesLeft"], rg["freeClaimed"]))

# PIXEL FROGS
pf = r1901["reads"]["PIXEL FROGS"]["views"]
pfe = snap["contracts"]["PIXEL FROGS"]
pfe.update({"totalSupply": pf["totalSupply"], "freeMinted": pf["freeMinted"],
            "freeLeft": pf["freeLeft"], "mintOpen": pf["mintOpen"],
            "freeClaimed_user": pf["freeClaimed_user"], "balanceOf_user": pf["balanceOf_user"],
            "lastReadBlock": BLOCK, "lastReadWib": WIB})
pfe["free_pct"] = round(100.0 * pf["freeMinted"] / pf["FREE_CAP"], 1) if pf["freeMinted"] is not None else None
pfe["runNote1901_1114"] = ("Run 1901 (blok %d): totalSupply 252->%s, freeMinted %s/3000 = %s%%, freeLeft %s, "
                            "mintOpen 1 - BUKAN promosi (sudah dilaporkan sekali sebagai lead 15:35 + gate FAILED no-website), "
                            "BUKAN strong lead (%s%% jauh di bawah 70%%), BUKAN kandidat. Deadline umur 24 jam 2026-11-15 15:29:57 WIB."
                            % (BLOCK, pf["totalSupply"], pf["freeMinted"], pfe["free_pct"], pf["freeLeft"], pfe["free_pct"]))

# HAPPE AGENTS - EARLY lead, free pool already exhausted; update fresh values only
hap = r1901["reads"]["AbsurdAgentNFT"]["views"]
happe = snap["contracts"]["HAPPE AGENTS"]
happe.update({"totalMinted": hap["totalMinted"], "mintOpen": hap["mintOpen"],
              "mintStartTime": hap["mintStartTime"], "isEligible_user": hap["isEligible_user"],
              "lastReadBlock": BLOCK, "lastReadWib": WIB})
happe["paidMinted"] = (hap["totalMinted"] - 222) if hap["totalMinted"] is not None else happe.get("paidMinted")
happe["runNote1901_1114"] = ("Run 1901 (blok %d): totalMinted %s (1831: 239), free pool tetap HABIS 222/222, "
                             "paid %s, mintOpen 1, launch 17:00 WIB. Status early-lead-reported-sold-out; "
                             "BUKAN kandidat/strong lead; TIDAK PERNAH di-preview/di-mint; jangan laporkan ulang."
                             % (BLOCK, hap["totalMinted"], happe["paidMinted"]))

# LumenFindings + NOISE: already age-excluded run 1801; refresh values only
lum = snap["contracts"]["LumenFindings"]
lum.update({"totalSpecimens": getv(r1901, "LumenFindings", "totalSpecimens"),
            "currentExperiment": getv(r1901, "LumenFindings", "currentExperiment"),
            "genesisStart": getv(r1901, "LumenFindings", "genesisStart"),
            "genesisOpen": getv(r1901, "LumenFindings", "genesisOpen"),
            "lastReadBlock": BLOCK, "lastReadWib": WIB})
lum["runNote1901_1114"] = ("Run 1901 (blok %d): totalSpecimens 2981->%s (+%s, velocity GAGAL). "
                            "Tetap AGE-EXCLUDED (genesisStart 13 Nov 08:43 WIB, umur ~34 jam > 24 jam). DIAM."
                            % (BLOCK, getv(r1901, "LumenFindings", "totalSpecimens"),
                               (getv(r1901, "LumenFindings", "totalSpecimens") or 0) - 2981))
nz = snap["contracts"].setdefault("NOISE", {})
nz.update({"totalMinted": getv(r1901, "NOISE", "totalMinted"),
           "remainingSupply": getv(r1901, "NOISE", "remainingSupply"),
           "mintOpen": getv(r1901, "NOISE", "mintOpen"),
           "lastReadBlock": BLOCK, "lastReadWib": WIB})
nz["runNote1901_1114"] = ("Run 1901 (blok %d): totalMinted 1175->%s (+%s, velocity GAGAL). "
                           "Tetap AGE-EXCLUDED (259 termint 05:32 13 Nov). DIAM."
                           % (BLOCK, getv(r1901, "NOISE", "totalMinted"),
                              (getv(r1901, "NOISE", "totalMinted") or 0) - 1175))

# Feed Sourcify: 9 new vs run 1831, all S1/S2 False -> checked-not-sale-shape entries
feed = json.load(open(BASE + "run-2026-11-14-1901-feedshape.json"))
feed_vat = {"0xAFE2aa712bb4187f00EdCD333C50f6D92772AA1c": "2026-11-14T11:50:16Z",
            "0xbbD1F94a435598309E1e8261c5ECEd5932E6a2ae": "2026-11-14T11:49:19Z",
            "0xA4C66c5e87059CB560758bB7cE87f1737cC79Cce": "2026-11-14T11:45:32Z",
            "0xF423486D0B021E457c0132b3144728DEa105f028": "2026-11-14T11:42:21Z",
            "0x651a15460F62dF9d9B77ea0324fc948F6b94b5fA": "2026-11-14T11:42:17Z",
            "0x0126652bFCfEcfE7E9638a413d41D528bcc56420": "2026-11-14T11:39:11Z",
            "0xfDFe4113D8dFC4a580b48767d63A9D780CAd3638": "2026-11-14T11:34:47Z",
            "0x0E7487C42b636C2dc691f9B37359888908ecDc97": "2026-11-14T11:34:18Z",
            "0x67144992ce6d0948ff183968D0fCD11773A4E153": "2026-11-14T11:33:18Z"}
for o in feed:
    addr = o["address"]
    key = "Feed-" + addr[2:6]
    snap["contracts"][key] = {
     "address": addr, "status": "checked-not-sale-shape-2026-11-14",
     "lastReadWib": WIB, "lastReadBlock": BLOCK,
     "baselineNote": ("Feed Sourcify run 1901 (verifiedAt %s): shape-check S1=%s S2=%s, has_mint=%s, has_quote=%s, "
                      "free_views=%s, agent_ref=%s, n_fns=%s. BUKAN sale-shape, BUKAN agent-shaped. "
                      "Tidak dilaporkan, tidak masuk watchlist aktif."
                      % (feed_vat.get(addr, "?"), o.get("S1"), o.get("S2"), o.get("has_mint"), o.get("has_quote"),
                         o.get("free_views"), o.get("agent_ref"), o.get("n_fns"))),
     "runNote1901_1114": "Run 1901: feed %s S1/S2 False -> bukan sale-shape." % addr[:10],
    }

snap["runNote1901_1114"] = (
 "Run 1901: reread 41/41 OK blok 133540454 (94,0 dtk, interval ~29,9 mnt vs run 1831). "
 "Velocity LOLOS 1 item: NovaRemnants +54 (1,806/mnt, 2,36x) - free%% UNVERIFIED -> BUKAN kandidat dan BUKAN strong lead. "
 "Ledgera +26 (0,870/mnt, 0,74x) velocity GAGAL run ini; free 2593/5000=51,9%% (>50%% kaki kandidat) TAPI umur/website/X UNVERIFIED "
 "-> BUKAN kandidat dan BUKAN strong lead (51,9%% < 70%%); slot user terbuka, mintOpen 1. Tanpa promosi, tanpa eksekusi. "
 "Close-fail: Ledgera +26 (0,74x) velocity GAGAL. AgentBubble +3 velocity GAGAL; "
 "free 1432/2222=64,4%% (<70%%). WoozCode +24 (0,88x) velocity GAGAL; free%% UNVERIFIED. "
 "NOISE +24 (1,83x) dan LumenFindings +62 (4,73x) velocity LOLOS tapi keduanya AGE-EXCLUDED (moot). "
 "RaceAgents +1, freeMinted 568/1000=56,8%% - velocity GAGAL, umur/website/X unverified -> BUKAN kandidat/strong lead. "
 "HIVE 1263 FLAT, minted-by-user. Zero/PX24 masih gagal baca (nilai lama dipertahankan). "
 "PIXEL FROGS 252->262, free 260/3000=8,7%% - bukan promosi (gate FAILED, sudah dilaporkan 15:35). "
 "HAPPE totalMinted 239 FLAT, free pool tetap HABIS 222/222. "
 "LumenFindings +62 (age-excluded, moot). NOISE +24 (age-excluded, moot). DragonAgents FLAT (age-excluded, moot). "
 "WANGCAI/YUANBAO tetap sold out free 188/188. NOTV totalMinted masih 0. "
 "0 kandidat baru, 0 strong lead baru, 0 early lead baru, 0 track-B, 0 track-C lead/kandidat baru, 0 eksekusi/preview.")
snap["runNote1901_1114_scan"] = (
 "Scan leg FAST-FAIL run 1901: pre-flight ankr_getLogs HTTP 401 Unauthorized dalam 2,8 dtk "
 "(head 133540306 via dataseed). Scan TIDAK dijalankan; watermark tetap 132512564; track-C 5c dilewati (tanpa output scan). "
 "Outage Ankr 401 sejak 2026-11-09 berlanjut; perlu reconnect kredensial Ankr (di luar scope job ini).")
snap["runNote1901_1114_feedshape"] = (
 "Feed Sourcify run 1901 (limit 20, top verifiedAt 2026-11-14T11:50:16Z 0xAFE2aa71): 9 benar-benar baru vs run 1831 "
 "(0xAFE2aa71, 0xbbD1F94a, 0xA4C66c5e, 0xF423486D, 0x651a1546, 0x0126652b, 0xfDFe4113, 0x0E7487C4, 0x67144992) - semuanya dicek run ini: "
 "S1=False S2=False semua (tidak satu pun punya kombinasi mint+quote+free view+agent_ref) -> BUKAN sale-shape, BUKAN agent-shaped. "
 "0 early lead baru dari feed.")
snap["runNote1901_1114_boltbook"] = (
 "Boltbook EN+ZH run 1901 (fetch ~19:01 WIB, EN 44.786 byte, ZH 44.988 byte, 25 article EN). "
 "Alamat unik 8, 0 alamat baru vs snapshot+hot-leg-seen: 7 sudah di snapshot (NovaRemnants, PIXEL FROGS, Feed-5a5e, 0x8269Ea16, BUGHOUND, BOLT, CAVE) "
 "dan 1 (Flare Agent 0x628a90f0, post dieuxuan50.ai 18:55 WIB) sudah dilihat hot-leg 1859 - triase run ini: kontrak KEDUA bernama Flare Agent "
 "(snapshot punya 0xe2deb4...), totalSupply 9900/10000, Sourcify UNVERIFIED, free views revert (free%% UNVERIFIED), umur UNVERIFIED, "
 "balanceOf(user)=0, code_len 13598 (template Nova yang sama). BUKAN early lead (sudah mature 9900 termint), BUKAN strong lead/kandidat; "
 "dicatat watchlist-only-2026-11-14 di snapshot, tidak dilaporkan. 0 early lead baru dari Boltbook run ini.")
snap["runNote1901_1114_sweep"] = (
 "Sweep EN+ZH run 1901: 0 baru yang lolos. EN: Oathbots 0xb777c522 (Square 28 Okt, ~375 minted) -> AGE-EXCLUDED, sudah dicatat di snapshot, DIAM; "
 "Agentic Gangster (di snapshot, free pool exhausted); STAMP PASS / Meow Cards / RIGBYPASS (di snapshot, excluded); AGENT COSMOS (5 Nov, di snapshot); "
 "Agent Nakamigos (sold out 20000/20000). ZH: Agentic Gangster (sama); Cosmic Sentinel (di snapshot); Agent Nakamigos (sold out); "
 "Xuanwu Seed (24 Okt, tua); Periodic Lab (di snapshot via bridge 0xfe5a...). "
 "Komplemen 6a Square tercakup sweep (tanpa proyek baru). 6b Odaily/PANews + 6c DappBay: tidak ada gate-check yang dibutuhkan run ini, dilewati.")
snap["runNote1901_1114_binanceai"] = (
 "Run 1901: binanceai.fun TIDAK BERUBAH - launched()=0, failed()=1, isRefundPhase()=1, totalShares=3110, "
 "tokenClaimed(user)=0 (blok 133540454). Status pending/refund; sudah dilaporkan sekali (fase refund), DIAM.")
snap["runNote1901_1114_bridge"] = (
 "Run 1901: bridge file dibaca read-only (mtime 2026-11-08 18:21 UTC, tidak berubah). 116 kontrak, 0 benar-benar belum ada di snapshot "
 "(cek kehadiran aktual, bukan flag stale in_freebacot_snapshot), 7 same_owner_discarded. "
 "Job ini tidak menulis bridge; temuan pelengkap scan tidak ada yang naik tier.")
snap["runNote1901_1114_pixelfrogs"] = (
 "PIXEL FROGS (PXFRG) 0x454054e55FA2D7Ba37df7F3ceA269696f19037dF - run 1901: totalSupply 252->262, freeMinted 260/3000 = 8,7%%, "
 "freeLeft 2750, mintOpen 1, slot user terbuka (freeClaimed(user)=0). Launch TERVERIFIKASI 2026-11-14 15:29:57 WIB, umur ~3 jam, "
 "deadline 24 jam 2026-11-15 15:29:57 WIB. Website tetap UNVERIFIED (gate FAILED, sudah dilaporkan sekali 15:35). "
 "BUKAN strong lead (8,3%% < 70%%), BUKAN kandidat. Tetap watchlist-only; promosi hanya bila free%% menembus 70%% + gate lolos.")
snap["runNote1901_1114_happe"] = (
 "HAPPE AGENTS (HAPPE) 0x72c14121681F1133545947B0735563835CC07B67 - run 1901: totalMinted 239 FLAT (1831: 239), free pool tetap HABIS 222/222, "
 "paid 17, mintOpen 1, isEligible(user)=1. Status early-lead-reported-sold-out-2026-11-14 (dilaporkan sekali run 1701); "
 "BUKAN kandidat/strong lead; TIDAK PERNAH di-preview/di-mint; jangan laporkan ulang.")
snap["runNote1901_1114_ledgera"] = (
 "Ledgera 0x8d292d7d423bc48b5f1954f2c0440cfbe9dabd7d - run 1901: VELOCITY GAGAL run ini (+26, 0,870/mnt, 0,74x vs prev 1,170). "
 "freeClaimed 2593/5000=51,9%% (>50%% kaki kandidat), slot user terbuka (mintedBy 0, balanceOf 0), mintOpen 1. "
 "TAPI umur UNVERIFIED + website UNVERIFIED + X unverified -> BUKAN kandidat dan BUKAN strong lead (51,9%% < 70%%). "
 "Tanpa promosi, tanpa preview/mint. Velocity kembali GAGAL run ini (0,74x); pantau run berikut bila umur/website terverifikasi.")
snap["last_run_wib"] = WIB
snap["last_run_note"] = snap["runNote1901_1114"]
snap["timestamp_wib"] = WIB

json.dump(snap, open(BASE + "onchain-snapshot.json", "w"), indent=1)
print("merged. velocity LOLOS:", vel_pass)
print("velocity close-fail:", vel_fail_close)
print("interval prev/cur min:", round(INT_PREV, 2), round(INT_CUR, 2))
