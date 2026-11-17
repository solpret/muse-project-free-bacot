#!/usr/bin/env python3
"""Merge run 1731 (2026-11-14) into onchain-snapshot.json.
Reads run-2026-11-14-1631-reread.json + run-2026-11-14-1701-reread.json + run-2026-11-14-1731-reread.json.
Intervals from block deltas x 0.45s. Read-only except the snapshot write. No preview/mint."""
import json

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
snap = json.load(open(BASE + "onchain-snapshot.json"))
r1631 = json.load(open(BASE + "run-2026-11-14-1631-reread.json"))
r1701 = json.load(open(BASE + "run-2026-11-14-1701-reread.json"))
r1731 = json.load(open(BASE + "run-2026-11-14-1731-reread.json"))
INT_PREV = (r1701["block"] - r1631["block"]) * 0.45 / 60.0
INT_CUR = (r1731["block"] - r1701["block"]) * 0.45 / 60.0
BLOCK = r1731["block"]
WIB = "2026-11-14 ~17:31 WIB"

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
    v1631, v1701, v1731 = getv(r1631, name, skey), getv(r1701, name, skey), getv(r1731, name, skey)
    note_parts = []
    if v1701 is not None and v1731 is not None:
        minted = v1731 - v1701
        rate = minted / INT_CUR
        prev_rate = None
        if v1631 is not None:
            prev_rate = (v1701 - v1631) / INT_PREV
        ratio = (rate / prev_rate) if prev_rate else None
        passes = bool(minted >= 20 and ratio is not None and ratio >= 1.5)
        if passes:
            vel_pass.append((name, minted, round(rate, 3), round(ratio, 2)))
        elif minted >= 20 and ratio is not None and ratio >= 1.0:
            vel_fail_close.append((name, minted, round(rate, 3), round(ratio, 2)))
        entry["previousTotalSupply"] = v1701
        entry[skey] = v1731
        entry["previousRatePerMin"] = round(prev_rate, 4) if prev_rate is not None else None
        entry["currentRatePerMin"] = round(rate, 4)
        entry["velocityRatio"] = round(ratio, 2) if ratio is not None else None
        entry["velocityLegPasses"] = passes
        entry["mintedInInterval"] = minted
        entry["intervalMinutes"] = round(INT_CUR, 1)
        note_parts.append(
            f"{v1701}->{v1731} (+{minted}, {rate:.3f}/mnt vs prev {round(prev_rate,3) if prev_rate is not None else 'None'} = "
            f"{round(ratio,2) if ratio is not None else 'None'}x) -> velocity {'LOLOS' if passes else 'GAGAL'}")
    elif v1731 is not None:
        entry[skey] = v1731
        note_parts.append(f"{skey} {v1731} (baseline 1701 None, velocity tidak dihitung)")
    else:
        note_parts.append(f"{skey} gagal baca run ini (nilai lama dipertahankan)")
    if fkey:
        fv = getv(r1731, name, fkey)
        if fv is not None:
            entry[fkey] = fv
            cap = entry.get("FREE_SUPPLY") or entry.get("FREE_MAX") or entry.get("FREE_CAP") or entry.get("FREE_POOL")
            if cap:
                pct = round(100.0 * fv / cap, 1)
                entry["freePctVerified"] = pct
                note_parts.append(f"free {fv}/{cap}={pct}%")
    entry["lastReadBlock"] = BLOCK
    entry["lastReadWib"] = WIB
    entry["runNote1731_1114"] = "Run 1731 (blok %d, interval %.1f mnt vs run 1701): %s" % (BLOCK, INT_CUR, "; ".join(note_parts))

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
bai = r1731["reads"]["BinanceAI-mint"]["views"]
pc = snap["pending_claims"]["binanceai.fun"]
pc.update({"launched": bai["launched"], "failed": bai["failed"], "isRefundPhase": bai["isRefundPhase"],
           "totalShares": bai["totalShares"], "tokenClaimed_user": bai["tokenClaimed_user"],
           "lastReadWib": WIB, "lastReadBlock": BLOCK})
pc["runNote1731"] = ("Run 1731: launched=0, failed=1, isRefundPhase=1, totalShares=3110, tokenClaimed(user)=0 "
                     "(blok %d) - tetap pending/refund, sudah dilaporkan sekali (fase refund), DIAM" % BLOCK)

# ORBIT track_c
orb = r1731["reads"]["ORBIT"]["views"]
tc = snap["track_c"]["ORBIT"]
tc.update({"freeClaimed": orb["freeClaimed"], "totalSupply": orb["totalSupply"],
           "lastReadWib": WIB, "lastReadBlock": BLOCK})

# RigForge track_c (lead minted by user 11 Nov; pool not open)
rg = r1731["reads"]["RigForge"]["views"]
rgt = snap["track_c"]["RigForge"]
rgt.update({"freeSharesLeft": rg["freeSharesLeft"], "openedAt": rg["openedAt"],
            "freeClaimed": rg["freeClaimed"], "freeBooked_user": rg["freeBooked_user"],
            "lastReadWib": WIB, "lastReadBlock": BLOCK})
rgt["runNote1731_1114"] = ("Run 1731 (blok %d): freeSharesLeft 659/1000 (1701: 659, tidak berubah), openedAt 0 "
                            "(pool BELUM buka), freeClaimed 341, freeBooked(wallet)=10000 RIG utuh. TIDAK ada aksi." % BLOCK)

# PIXEL FROGS: first mints now verified (126), free 4.2%
pf = r1731["reads"]["PIXEL FROGS"]["views"]
pfe = snap["contracts"]["PIXEL FROGS"]
pfe.update({"totalSupply": pf["totalSupply"], "freeMinted": pf["freeMinted"],
            "freeLeft": pf["freeLeft"], "mintOpen": pf["mintOpen"],
            "freeClaimed_user": pf["freeClaimed_user"], "balanceOf_user": pf["balanceOf_user"],
            "lastReadBlock": BLOCK, "lastReadWib": WIB})
pfe["free_pct"] = round(100.0 * pf["freeMinted"] / pf["FREE_CAP"], 1) if pf["freeMinted"] is not None else None
pfe["runNote1731_1114"] = ("Run 1731 (blok %d): totalSupply 126->162, freeMinted 160/3000 = 5,3%%, freeLeft 2840, "
                            "mintOpen 1 - BUKAN promosi (sudah dilaporkan sekali sebagai lead 15:35 + gate FAILED no-website), "
                            "BUKAN strong lead (5,3%% jauh di bawah 70%%), BUKAN kandidat. Deadline umur 24 jam 2026-11-15 15:29:57 WIB." % BLOCK)

# HAPPE AGENTS (ex-AbsurdAgentNFT) - EARLY lead, free pool already exhausted; update fresh values only
hap = r1731["reads"]["AbsurdAgentNFT"]["views"]
happe = snap["contracts"]["HAPPE AGENTS"]
happe.update({"totalMinted": hap["totalMinted"], "mintOpen": hap["mintOpen"],
              "mintStartTime": hap["mintStartTime"], "isEligible_user": hap["isEligible_user"],
              "lastReadBlock": BLOCK, "lastReadWib": WIB})
happe["paidMinted"] = (hap["totalMinted"] - 222) if hap["totalMinted"] is not None else happe.get("paidMinted")
happe["runNote1731_1114"] = ("Run 1731 (blok %d): totalMinted %s (1701: 233), free pool tetap HABIS 222/222, "
                             "paid %s, mintOpen 1, launch 17:00 WIB. Status early-lead-reported-sold-out; "
                             "BUKAN kandidat/strong lead; TIDAK PERNAH di-preview/di-mint; jangan laporkan ulang."
                             % (BLOCK, hap["totalMinted"], happe["paidMinted"]))

# Saturnagent - sellout verified by own read this run (totalSupply 2000, freeClaimed 1996, blok 133528924)
sat = snap["contracts"]["Saturnagent"]
sat.update({"totalSupply": 2000, "freeClaimed": 1996, "mintOpen": 1,
            "status": "sold-out-2026-11-14", "lastReadBlock": 133528924, "lastReadWib": WIB})
sat["runNote1731_1114"] = ("Run 1731: SOLD OUT terverifikasi bacaan sendiri (blok 133528924): totalSupply 2000/2000, "
                           "freeClaimed 1996/2000 = 99,8%%, mintOpen 1 - cocok dengan post Boltbook 17:3x WIB. "
                           "Status checked-not-lead -> sold-out; TIDAK PERNAH dilaporkan sebagai lead, jadi TIDAK ada "
                           "laporan chat (sellout item non-lead). Jangan laporkan ulang.")

snap["runNote1731_1114"] = (
 "Run 1731: reread 41/41 OK blok 133528805 (213,0 dtk, interval ~28,8 mnt vs run 1701; egress flapping, semua chunk lolos setelah retry endpoint). "
 "Velocity LOLOS 2 item TAPI BUKAN kandidat: WoozCode +108 (3,75/mnt, 1,90x), Ledgera +38 (1,32/mnt, 1,86x) - "
 "WoozCode free%% UNVERIFIED (tanpa free view), Ledgera free 2517/5000=50,3%% (<70%% strong-lead bar); umur keduanya UNVERIFIED, website/X unverified. Close-fail: %s. "
 "RaceAgents baru terbaca lagi: totalSupply 563, freeMinted 563/1000=56,3%% (>50%%) - velocity belum terhitung (baseline 1701 None), umur/website/X unverified -> BUKAN kandidat/strong lead. "
 "AgentBubble free 1420/2222=63,9%% (<70%%), velocity GAGAL (+4) -> bukan strong lead. "
 "PIXEL FROGS 126->162, free 160/3000=5,3%% - bukan promosi (gate FAILED, sudah dilaporkan 15:35). "
 "HAPPE totalMinted 233->237, free pool tetap HABIS 222/222. Saturnagent SOLD OUT terverifikasi bacaan sendiri (2000/2000, free 1996) - "
 "status checked-not-lead -> sold-out; TIDAK PERNAH dilaporkan sebagai lead, jadi TIDAK ada laporan chat. "
 "DragonAgents free 736/888=82,9%% tapi age-excluded-2026-11-14 -> moot. WANGCAI/YUANBAO tetap sold out 188/188. "
 "HIVE 1263 FLAT, minted-by-user. AgentZENITH/AgentNOVA/SPARKS/OTV/RAVE/HANAMI gagal baca run ini (nilai lama dipertahankan); "
 "Zero/PX24/SKRR masih gagal baca. "
 "0 kandidat baru, 0 strong lead baru, 0 early lead baru, 0 track-B, 0 track-C lead/kandidat baru, 0 eksekusi/preview." % (vel_fail_close,))
snap["runNote1731_1114_scan"] = (
 "Scan leg FAST-FAIL run 1731: pre-flight ankr_getLogs HTTP 401 Unauthorized dalam 5,0 dtk "
 "(probe langsung window 133524919-133524969; head fetch gagal di dataseed/dataseed1/dataseed2/publicnode - Remote end closed / 403, retry 12,4 dtk). "
 "Scan TIDAK dijalankan; watermark tetap 132512564; track-C 5c dilewati (tanpa output scan). "
 "Outage Ankr 401 sejak 2026-11-09 berlanjut; perlu reconnect kredensial Ankr (di luar scope job ini).")
snap["runNote1731_1114_feedshape"] = (
 "Feed Sourcify run 1731 (limit 20, top verifiedAt 2026-11-14T10:31:23Z 0xB13d4497): 7 baru vs run 1701, "
 "6 sudah di-shape-check hot-leg (0x98D6e256, 0x9224B05A, 0xf2c75231, 0x08Ef1e04, 0x6776174F, 0x17a784Bc); "
 "1 dicek run ini: 0xB13d4497 (ERC-20 biasa, fungsi airdrop + sweepAll/sweepToken 'victim' - BUKAN sale-shape S1/S2, BUKAN agent-shaped). "
 "0 early lead baru dari feed.")
snap["runNote1731_1114_boltbook"] = (
 "Boltbook EN+ZH run 1731 (fetch ~17:33 WIB, EN+ZH identik, 27 post). 0 alamat baru vs hot-leg-seen/snapshot: "
 "Storm Agent 0x557ffa02 (4.900/5.000, 98%%, Sourcify UNVERIFIED) sudah di hot-leg-seen; PIXEL FROGS 152/3.000 (di reread-set); "
 "RIMEVAULT 1.279 (minted-by-user), Lion's Share (age-excluded), Ember Agent (age-excluded), ACORE (same-owner discarded), "
 "Saturnagent sold out (verifikasi sendiri run ini), OBSCURA (watchlist-only, di snapshot), CLOUDFLOCK/ALCH/Spelunkers (di hot-leg-seen). "
 "Catacomb Delvers (TOMB) 205/5.000, DeepDig family, Sourcify exact_match - KONTRAK TIDAK TERCETAK di post + pencarian web tanpa hasil, "
 "jadi belum bisa ditambahkan ke snapshot (4,1%%, pace ~6/jam, first mints bukan run ini -> bukan early lead). "
 "0 early lead baru dari Boltbook run ini.")
snap["runNote1731_1114_sweep"] = (
 "Sweep EN+ZH run 1731: 0 baru. EN: TINY AGENTS 0x83d5e544 (10 Nov, 38 free, age-excluded), FOSTER AGENTS 0x091eAD6e (free pool 111/111 HABIS), "
 "MiniCoin 0x7e624dc2 (free mint() fungible, tanpa Agent-ID gate + tanpa cap, 7 hari lalu - bukan Free Bacot). "
 "ZH: BN Agent Trials (bnagent.si, 26 Okt, age-excluded), Agentic Gangster (9 Nov, di snapshot), blokwiki tutorial Agent ID (bukan proyek mint). "
 "Komplemen 6a Square tercakup sweep (tanpa proyek baru). 6b Odaily/PANews + 6c DappBay: tidak ada gate-check yang dibutuhkan run ini, dilewati (retry run berikut bila ada proyek yang butuh gate-check).")
snap["runNote1731_1114_binanceai"] = (
 "Run 1731: binanceai.fun TIDAK BERUBAH - launched()=0, failed()=1, isRefundPhase()=1, totalShares=3110, "
 "tokenClaimed(user)=0 (blok 133528805). Status pending/refund; sudah dilaporkan sekali (fase refund), DIAM.")
snap["runNote1731_1114_bridge"] = (
 "Run 1731: bridge file dibaca read-only (mtime 2026-11-08 18:21 UTC, tidak berubah). 116 kontrak, 0 benar-benar belum ada di snapshot "
 "(cek kehadiran aktual, bukan flag stale in_freebacot_snapshot), 7 same_owner_discarded. "
 "Job ini tidak menulis bridge; temuan pelengkap scan tidak ada yang naik tier.")
snap["runNote1731_1114_pixelfrogs"] = (
 "PIXEL FROGS (PXFRG) 0x454054e55FA2D7Ba37df7F3ceA269696f19037dF - run 1731: totalSupply 126->162, freeMinted 160/3000 = 5,3%%, "
 "freeLeft 2840, mintOpen 1, slot user terbuka (freeClaimed(user)=0). Launch TERVERIFIKASI 2026-11-14 15:29:57 WIB, umur ~2 jam, "
 "deadline 24 jam 2026-11-15 15:29:57 WIB. Website tetap UNVERIFIED (gate FAILED, sudah dilaporkan sekali 15:35). "
 "BUKAN strong lead (5,3%% < 70%%), BUKAN kandidat. Tetap watchlist-only; promosi hanya bila free%% menembus 70%% + gate lolos.")
snap["runNote1731_1114_happe"] = (
 "HAPPE AGENTS (HAPPE) 0x72c14121681F1133545947B0735563835CC07B67 - run 1731: totalMinted 233->237, free pool tetap HABIS 222/222, "
 "paid 15, mintOpen 1, isEligible(user)=1. Status early-lead-reported-sold-out-2026-11-14 (dilaporkan sekali run 1701); "
 "BUKAN kandidat/strong lead; TIDAK PERNAH di-preview/di-mint; jangan laporkan ulang.")
snap["runNote1731_1114_saturnagent"] = (
 "Saturnagent 0xef870a9b4a529373fb2e174b59ca7a66eb018074 - SOLD OUT run 1731: totalSupply 2000/2000, freeClaimed 1996/2000 = 99,8%%, "
 "mintOpen 1, dibaca sendiri blok 133528924 (cocok post Boltbook). Status checked-not-lead-2026-11-14 -> sold-out-2026-11-14. "
 "TIDAK PERNAH dilaporkan sebagai lead (umur UNVERIFIED) -> TIDAK ada laporan chat untuk sellout ini.")
snap["last_run_wib"] = WIB
snap["last_run_note"] = snap["runNote1731_1114"]
snap["timestamp_wib"] = WIB

json.dump(snap, open(BASE + "onchain-snapshot.json", "w"), indent=1)
print("merged. velocity LOLOS:", vel_pass)
print("velocity close-fail:", vel_fail_close)
print("interval prev/cur min:", round(INT_PREV, 2), round(INT_CUR, 2))
