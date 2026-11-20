#!/usr/bin/env python3
"""Merge run 2026-11-18 20:31 WIB re-read into onchain-snapshot.json (lean merge).
Reread via Quicknode tunnel: 285 calls, 0 chunk errors. Block 134321122,
interval ~15,5 mnt vs 2001.
Outcome: 0 kandidat baru, 0 strong lead baru/promosi, 0 early lead BARU,
0 track-B dibuka, 0 track-C lead BARU. SATU PERUBAHAN STATUS: PUNNY
mintClosed 0->1 (jendela 24 jam tutup 2026-11-18 20:32:03 WIB) -> AGE-EXCLUDED,
dilaporkan sekali + dihapus dari snapshot. AONE track-C: freeMinted 9959/10000
(tersisa 41), kuota user 0. Boltbook EN+ZH OK (10 alamat, semua sudah dikenal).
Sourcify feed OK (20 alamat; 15 shape-checked, semua S1/S2 false; 5 TimeoutError
- belum terperiksa, BUKAN lolos). Scan leg FAST-FAIL pre-flight timeout.
Read-only except snapshot. None/err values NEVER overwrite."""
import json
HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
snap = json.load(open(f"{HF}/onchain-snapshot.json"))
reread = json.load(open(f"{HF}/run-2026-11-18-2031-reread.json"))
prev = json.load(open(f"{HF}/run-2026-11-18-2001-reread.json"))
reads = reread["reads"]; prev_reads = prev["reads"]
NOW = "2026-11-18 ~20:31 WIB"
BLOCK = reread["block"]; PREV_BLOCK = prev["block"]
INTERVAL_MIN = (BLOCK - PREV_BLOCK) * 0.45 / 60.0
print(f"block {BLOCK} prev {PREV_BLOCK} interval {INTERVAL_MIN:.1f} min")
addr2key = {}
for _k, _v in snap.get("contracts", {}).items():
    if isinstance(_v, dict) and isinstance(_v.get("address"), str):
        addr2key[_v["address"].lower()] = _k
updated, missed, vel_pass = [], [], []
for name, d in reads.items():
    addr = d.get("address", "")
    key = addr2key.get(addr.lower()) if isinstance(addr, str) else None
    if key is None:
        missed.append(name); continue
    e = snap["contracts"][key]
    v = d.get("views", {})
    for f, val in v.items():
        if isinstance(val, int):
            e[f] = val
    pv = prev_reads.get(name, {}).get("views", {})
    fresh = v.get("totalSupply"); pval = pv.get("totalSupply"); view = "totalSupply"
    if not isinstance(fresh, int):
        fresh = v.get("totalMinted"); pval = pv.get("totalMinted"); view = "totalMinted"
    if isinstance(fresh, int) and isinstance(pval, int):
        minted = fresh - pval
        rate = minted / INTERVAL_MIN if INTERVAL_MIN > 0 else 0.0
        prev_rate = e.get("currentRatePerMin")
        ratio = (rate / prev_rate) if isinstance(prev_rate, (int, float)) and prev_rate else None
        vel = bool(ratio is not None and ratio >= 1.5 and minted >= 20)
        if vel:
            vel_pass.append((name, minted, round(rate, 4), round(ratio, 2)))
        e["previousTotalSupply"] = pval; e["mintedInInterval"] = minted
        e["intervalMinutes"] = round(INTERVAL_MIN, 1)
        e["currentRatePerMin"] = round(rate, 4); e["previousRatePerMin"] = prev_rate
        e["velocityRatio"] = round(ratio, 2) if ratio is not None else None
        e["velocityLegPasses"] = vel; e["supplyView"] = view
    e["lastReadWib"] = NOW; e["lastReadBlock"] = BLOCK
    updated.append((name, key))
print(f"updated {len(updated)} entries; missed (not in snapshot): {missed}")
print("velocity PASS:", vel_pass)

def note(key, text):
    if key in snap.get("contracts", {}):
        snap["contracts"][key]["runNote2031_1118"] = text
    else:
        print("NOTE MISS", key)

note("PUNNY", f"Run 2031 (blok {BLOCK}, interval ~15,5 mnt vs 2001): freeMinted/totalMinted 377->379 (+2, <20) -> velocity GAGAL. free 379/999 = 37,9% (<50% kandidat, <70% strong lead). mintClosed 0->1: jendela 24 jam TUTUP 2026-11-18 20:32:03 WIB (mintStart 1794922323 + MINT_DURATION 86400); dikonfirmasi bacaan segar independen blok 134322338 (mintClosed=1, freeMinted 379, freeRemaining 620). Slot user HILANG karena mint tutup (hasClaimedFree 0, mintedBy 0, balance 0 - user tidak pernah klaim). Website gate tetap UNVERIFIED. PERUBAHAN STATUS: AGE-EXCLUDED / mint closed -> dilaporkan sekali + dihapus dari snapshot run ini.")
note("STOCK AGENT", f"Run 2031 (blok {BLOCK}): totalSupply 791->794 (+3), freeLeft 317 (FREE_SUPPLY 1111, inferred free 794/1111 = 71,5% - MELEWATI 70% secara INFERENSI SAJA, freeMinted/freeClaimed revert = bukan counter terverifikasi, jadi BUKAN strong lead; umur + website tetap UNVERIFIED). quote(user,1)=0, freeMintedByWallet 0, balance 0 -> slot TERBUKA. Velocity GAGAL (+3 <20). Tetap EARLY LEAD.")
note("Lumenhold", f"Run 2031 (blok {BLOCK}): freeClaimed 1257->1258/1500 = 83,9%, totalSupply 1262->1263 (+1) -> velocity GAGAL. Free% >70% TAPI umur UNVERIFIED -> BUKAN strong lead.")
note("Ledgera", f"Run 2031 (blok {BLOCK}): freeClaimed 2706->2707/5000 = 54,1%, totalSupply 2713->2714 (+1) -> velocity GAGAL. Umur/website/X UNVERIFIED -> BUKAN kandidat dan BUKAN strong lead (54,1% <70%).")
note("Vitaliq Scans", f"Run 2031 (blok {BLOCK}): totalSupply revert (fungsi tidak ada, sama seperti 2001), mintOpen 1, genesisStart 1794960000 = 2026-11-18 07:00 WIB (umur ~13,5 jam, TERVERIFIKASI <24 jam), holdsAgentId(user)=1, balance 0. Free%/website UNVERIFIED. Tetap EARLY LEAD, TIDAK di-preview/di-mint.")
note("HIVE Agents", f"Run 2031 (blok {BLOCK}): totalSupply 1264 FLAT vs 2001, balanceOf(user)=1, minted-by-user. DIAM.")
note("CAT402", f"Run 2031 (blok {BLOCK}): freeCatsClaimed 100/100 SOLD OUT (sudah diketahui). DIAM.")
note("Bubblebruin", f"Run 2031 (blok {BLOCK}): totalSupply 2627 FLAT, freeClaimed 2621/7777 = 33,7% -> velocity GAGAL. Minted-by-user, bukan kandidat. DIAM.")
note("DGF CARD", f"Run 2031 (blok {BLOCK}): totalMinted 1665 terbaca lagi (2001 gagal baca, nilai lama 1657 dipertahankan; +8 vs 1657 tapi velocity tidak dihitung karena 2001 None). freeMinted/mintOpen revert. Tetap EARLY LEAD.")
note("THE WALL", f"Run 2031 (blok {BLOCK}): totalSupply 5514->5515 (+1) -> velocity GAGAL; free views revert. Bukan kandidat.")
note("Mine Card", f"Run 2031 (blok {BLOCK}): totalSupply/totalMinted 1363->1366 (+3) -> velocity GAGAL (<20). Bukan kandidat.")
note("AgentNOVA", f"Run 2031 (blok {BLOCK}): totalSupply 790->793 (+3) -> velocity GAGAL (<20). Bukan kandidat.")
note("EIM", f"Run 2031 (blok {BLOCK}): totalMinted 777->780 (+3) -> velocity GAGAL (<20). Bukan kandidat.")
note("PunchCard", f"Run 2031 (blok {BLOCK}): totalSupply/totalMinted 1355->1356 (+1) -> velocity GAGAL. Umur/website UNVERIFIED. Bukan kandidat.")
note("ALIEN", f"Run 2031 (blok {BLOCK}): totalSupply 503->504 (+1) -> velocity GAGAL (<20). Bukan kandidat.")
note("ARKYN", f"Run 2031 (blok {BLOCK}): totalMinted 2292->2294 (+2) -> velocity GAGAL (<20). Bukan kandidat.")
note("MORFO", f"Run 2031 (blok {BLOCK}): totalMinted 1130->1132 (+2) -> velocity GAGAL (<20). Bukan kandidat.")
note("SPARKS", f"Run 2031 (blok {BLOCK}): totalSupply 1211->1212 (+1) -> velocity GAGAL (<20). Bukan kandidat.")
note("AgentEcho", f"Run 2031 (blok {BLOCK}): totalSupply 409->413 (+4, maks run ini) -> velocity GAGAL (<20). Bukan kandidat.")
note("Stromboat", f"Run 2031 (blok {BLOCK}): totalMinted 330->331 (+1) -> velocity GAGAL. Bukan kandidat.")
note("Kageveil Genesis", f"Run 2031 (blok {BLOCK}): totalSupply 48->49 (+1) -> velocity GAGAL. Bukan kandidat.")

# ---- PUNNY removal: age-excluded / mint closed (early-lead change, reported once) ----
punny = snap.get("contracts", {}).pop("PUNNY", None)
if punny is not None:
    snap["removed2031_punny"] = {
        "address": punny.get("address"),
        "name": "PUNNY",
        "reason": "age-excluded / mint closed",
        "evidence": ("mintClosed 0->1 run 2031 (blok 134321122), dikonfirmasi bacaan segar "
                     "independen blok 134322338 (mintClosed=1, freeMinted 379, freeRemaining 620, "
                     "mintStart 1794922323 = 2026-11-17 20:32:03 WIB, MINT_DURATION 86400 -> "
                     "jendela tutup 2026-11-18 20:32:03 WIB). freeMinted akhir 379/999 = 37,9% "
                     "(<50% kandidat, <70% strong lead). Slot user hilang karena mint tutup "
                     "(hasClaimedFree 0, mintedBy 0, balance 0 - user tidak pernah klaim). "
                     "Website gate UNVERIFIED (tokenURI host punny-nft.surge.sh root 404, tanpa "
                     "external_url). Early lead dilaporkan sekali run 1131 WIB 2026-11-18; "
                     "perubahan status ini dilaporkan sekali run 2031."),
        "removedWib": NOW,
        "reported": "once, run 2031",
    }
    print("PUNNY removed from snapshot (age-excluded / mint closed)")
else:
    print("PUNNY NOT in snapshot?!")

# ---- AONE track-C update ----
aone = snap.setdefault("track_c", {}).get("AONE")
if isinstance(aone, dict):
    aone["freeMinted"] = 9959
    aone["freeRemaining"] = 41
    aone["lastReadWib"] = NOW
    aone["note2031"] = ("Run 2031 (blok 134321122): freeMinted 9567 -> 9959 (+392 dalam ~15,5 mnt, ~25/mnt), "
        "FREE_TOTAL 10000, tersisa 41. LAUNCH 1794999600 = 2026-11-18 18:00 WIB. "
        "Kuota user SUDAH 0 (minted-by-user 18:17 WIB, hero #3330/#3331). freeQuotaLeft/freeTaken/quote revert run ini. "
        "Tidak ada eksekusi ulang. Belum sold out (41 tersisa) - DIAM sampai sold out.")
    print("AONE updated: freeMinted 9959, freeRemaining 41")
else:
    print("AONE MISSING from track_c!")

# ---- Track-B pending: binanceai.fun (re-read via leg4) ----
bc = snap.setdefault("pending_claims", {}).get("binanceai.fun")
if isinstance(bc, dict):
    bc["lastReadWib"] = NOW
    bc["runNote2031"] = ("Run 2031: launched=0, failed=1, isRefundPhase=1, totalShares 3110, tokenClaimed(user)=0 (blok 134321122) - tetap pending/refund, "
        "sudah dilaporkan sekali (fase refund 2026-11-02). DIAM.")
    print("binanceai note updated")

snap["last_run_wib"] = NOW
snap["last_run"] = ("free-mint-search 2026-11-18 20:31 WIB - 0 kandidat, 0 strong lead, 0 early lead baru, 0 track-B dibuka, "
    "0 track-C lead; 1 PERUBAHAN STATUS: PUNNY mintClosed 0->1 (jendela 24 jam tutup 20:32:03 WIB) -> AGE-EXCLUDED, "
    "dilaporkan sekali + dihapus dari snapshot; AONE freeMinted 9959/10000 (tersisa 41), kuota user 0; "
    "STOCK AGENT inferred 71,5% (bukan counter terverifikasi) - tetap EARLY LEAD; Lumenhold 83,9% tapi umur UNVERIFIED.")
snap["runNote2031_1118"] = (
    f"Run 2031 (blok {BLOCK}, interval ~15,5 mnt vs 2001): "
    "0 kandidat baru, 0 strong lead baru/promosi, 0 early lead BARU, 0 track-B dibuka, 0 track-C lead BARU. "
    "1 PERUBAHAN STATUS: PUNNY mintClosed 0->1 (jendela mint 24 jam tutup 2026-11-18 20:32:03 WIB; mintStart 1794922323 + MINT_DURATION 86400), "
    "dikonfirmasi bacaan segar independen blok 134322338 (mintClosed=1, freeMinted 379/999 = 37,9%, freeRemaining 620); slot user hilang karena mint tutup "
    "(hasClaimedFree 0, mintedBy 0, balance 0 - user tidak pernah klaim); website gate UNVERIFIED -> AGE-EXCLUDED, dilaporkan sekali + dihapus dari snapshot. "
    "Scan leg FAST-FAIL: Ankr pre-flight GAGAL setup OSError timeout (egress-wide, BUKAN 401); watermark TIDAK maju (tetap 134086385, gap ~234.737 blok vs head 134321122). "
    "Reread Quicknode 285 calls, 0 chunk error; elapsed run 904,5 dtk. "
    "Velocity: 0 LOLOS - maks +4 AgentEcho, +3 Mine Card/EIM/STOCK AGENT/AgentNOVA, +2 ARKYN/MORFO/PUNNY, +1 THE WALL/Ledgera/PunchCard/Lumenhold/SPARKS/ALIEN/Stromboat/Kageveil - semua <20 token. "
    "STOCK AGENT inferred 794/1111 = 71,5% (INFERENSI totalSupply, freeMinted/freeClaimed revert; umur + website UNVERIFIED) -> tetap EARLY LEAD, BUKAN strong lead. "
    "Di atas 70% TAPI umur UNVERIFIED -> BUKAN strong lead: Lumenhold 1258/1500 = 83,9%. "
    "Ledgera 54,1%, Bubblebruin 33,7% FLAT, CAT402 sold out 100/100, HIVE 1264 FLAT (minted-by-user). "
    "Vitaliq Scans: genesisStart 07:00 WIB (umur ~13,5 jam TERVERIFIKASI <24 jam), free%/website UNVERIFIED -> tetap EARLY LEAD. "
    "DGF CARD totalMinted 1665 terbaca lagi (2001 gagal). "
    "AONE track-C: freeMinted 9567 -> 9959 (+392/~15,5 mnt, ~25/mnt), tersisa 41, LAUNCH 18:00 WIB; kuota user 0 (minted-by-user 18:17 WIB). DIAM (belum sold out). "
    "Boltbook EN+ZH OK (45.170 / 43.472 byte, 10 alamat penuh, semua sudah dikenal - 6 di snapshot, 10 di hot-leg-seen; Mine Card sudah di PLAN). "
    "Sourcify feed OK (20 alamat; 15 shape-checked, semua S1/S2 false; 5 TimeoutError - belum terperiksa, BUKAN lolos). "
    "Sweep EN+ZH + share-sale (browser.search): 0 proyek segar baru - hanya proyek lama yang dikenal (Oathbots age-excluded, Agentic Gangster 9 Nov, "
    "RIGBYPASS 10 Nov, AGENT COSMOS 5 Nov, MOLT 6 Nov; UFO tutup 12 Nov, NEBULA minted-by-user, VISION age-excluded, NOVRA age-excluded + pool 0, "
    "YAMA age-excluded, WNO minted-by-user). "
    "Bridge read-only: 116 kontrak, 0 baru, 7 same-owner-discarded - tidak berubah, tanpa promosi/perubahan. "
    "BinanceAI pending: launched=0, failed=1, isRefundPhase=1, tokenClaimed(user)=0 - tetap pending/refund, DIAM. "
    "LAPORAN SEKALI: PUNNY age-excluded / mint closed (lihat removed2031_punny)."
)
json.dump(snap, open(f"{HF}/onchain-snapshot.json", "w"), indent=1)
print("snapshot saved")
