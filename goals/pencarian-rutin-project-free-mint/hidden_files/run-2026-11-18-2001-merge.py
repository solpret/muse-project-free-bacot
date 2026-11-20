#!/usr/bin/env python3
"""Merge run 2026-11-18 20:01 WIB re-read into onchain-snapshot.json (lean merge).
Reread via Quicknode tunnel: 285 calls, 9 chunk errors (calls 200-244,
TimeoutError; Velko/Crown/Longge/DGF/bsccat views failed - old values kept).
Block 134319057, interval ~36,0 mnt vs 1931.
Outcome: 0 kandidat baru, 0 strong lead baru/promosi, 0 early lead BARU,
0 track-B dibuka, 0 track-C lead BARU. PUNNY 37,7% (deadline 24 jam 20:32 WIB
hari ini); STOCK AGENT inferred 71,2% (bukan counter terverifikasi) - tetap
EARLY LEAD. AONE track-C: freeMinted 7442 -> 9567 (tersisa 433), kuota user 0.
Boltbook EN+ZH + Sourcify feed GAGAL TimeoutError (egress degradasi) -
tidak ada bacaan segar, BUKAN 0 temuan. Scan leg FAST-FAIL pre-flight timeout.
Read-only except snapshot. None/err values NEVER overwrite."""
import json
HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
snap = json.load(open(f"{HF}/onchain-snapshot.json"))
reread = json.load(open(f"{HF}/run-2026-11-18-2001-reread.json"))
prev = json.load(open(f"{HF}/run-2026-11-18-1931-reread.json"))
reads = reread["reads"]; prev_reads = prev["reads"]
NOW = "2026-11-18 ~20:01 WIB"
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
        snap["contracts"][key]["runNote2001_1118"] = text
    else:
        print("NOTE MISS", key)

note("PUNNY", f"Run 2001 (blok {BLOCK}, interval ~36,0 mnt vs 1931): freeMinted/totalMinted 370->377 (+7, <20) -> velocity GAGAL. free 377/999 = 37,7% (<50% kandidat, <70% strong lead). mintStart on-chain 1794922323 = 2026-11-17 20:32:03 WIB (umur ~23,5 jam, deadline 24 jam 20:32 WIB hari ini - run 21:01 nanti sudah lewat umur bila belum sold out). Slot user TERBUKA (hasClaimedFree 0, mintedBy 0, balance 0). Website gate tetap UNVERIFIED. Tetap EARLY LEAD.")
note("STOCK AGENT", f"Run 2001 (blok {BLOCK}): totalSupply 787->791 (+4), freeLeft 320 (FREE_SUPPLY 1111, inferred free 791/1111 = 71,2% - MELEWATI 70% secara INFERENSI SAJA, freeMinted/freeClaimed revert = bukan counter terverifikasi, jadi BUKAN strong lead; umur + website tetap UNVERIFIED). quote(user,1)=0, freeMintedByWallet 0, balance 0 -> slot TERBUKA. Velocity GAGAL (+4 <20). Tetap EARLY LEAD.")
note("Lumenhold", f"Run 2001 (blok {BLOCK}): freeClaimed 1256->1257/1500 = 83,8%, totalSupply 1261->1262 (+1) -> velocity GAGAL. Free% >70% TAPI umur UNVERIFIED -> BUKAN strong lead.")
note("Ledgera", f"Run 2001 (blok {BLOCK}): freeClaimed 2703->2706/5000 = 54,1%, totalSupply 2710->2713 (+3) -> velocity GAGAL. Umur/website/X UNVERIFIED -> BUKAN kandidat dan BUKAN strong lead (54,1% <70%).")
note("Vitaliq Scans", f"Run 2001 (blok {BLOCK}): totalSupply revert (fungsi tidak ada, sama seperti 1931), mintOpen 1, genesisStart 1794960000 = 2026-11-18 07:00 WIB (umur ~13 jam, TERVERIFIKASI <24 jam), holdsAgentId(user)=1, balance 0. Free%/website UNVERIFIED. Tetap EARLY LEAD, TIDAK di-preview/di-mint.")
note("HIVE Agents", f"Run 2001 (blok {BLOCK}): totalSupply 1264 FLAT vs 1931, balanceOf(user)=1, minted-by-user. DIAM.")
note("CAT402", f"Run 2001 (blok {BLOCK}): freeCatsClaimed 100/100 SOLD OUT (sudah diketahui; totalSupply/mintOpen gagal baca run ini - transport, nilai lama dipertahankan). DIAM.")
note("Bubblebruin", f"Run 2001 (blok {BLOCK}): totalSupply 2626->2627 (+1), freeClaimed 2620->2621/7777 = 33,7% -> velocity GAGAL. Minted-by-user, bukan kandidat. DIAM.")
note("DGF CARD", f"Run 2001 (blok {BLOCK}): SEMUA view gagal baca (chunk error TimeoutError, calls 200-244) - degradasi transport, BUKAN nol; nilai lama (totalMinted 1657) dipertahankan, velocity TIDAK dihitung. Tetap EARLY LEAD.")
note("Velko Rig", f"Run 2001 (blok {BLOCK}): SEMUA view gagal baca (chunk error TimeoutError) - degradasi transport, BUKAN nol; nilai lama dipertahankan, velocity TIDAK dihitung.")
note("Crown", f"Run 2001 (blok {BLOCK}): SEMUA view gagal baca (chunk error TimeoutError) - degradasi transport, BUKAN nol; nilai lama dipertahankan, velocity TIDAK dihitung.")
note("Longge", f"Run 2001 (blok {BLOCK}): SEMUA view gagal baca (chunk error TimeoutError) - degradasi transport, BUKAN nol; nilai lama dipertahankan, velocity TIDAK dihitung.")
note("THE WALL", f"Run 2001 (blok {BLOCK}): totalSupply 5513->5514 (+1) -> velocity GAGAL; free views gagal baca run ini (transport). Bukan kandidat.")
note("Mine Card", f"Run 2001 (blok {BLOCK}): totalSupply 1361->1363 (+2) -> velocity GAGAL (<20). Bukan kandidat.")
note("AgentNOVA", f"Run 2001 (blok {BLOCK}): totalSupply 787->790 (+3) -> velocity GAGAL (<20). Bukan kandidat.")
note("EIM", f"Run 2001 (blok {BLOCK}): totalMinted 774->777 (+3) -> velocity GAGAL (<20). Bukan kandidat.")
note("PunchCard", f"Run 2001 (blok {BLOCK}): totalMinted 1352->1355 (+3) -> velocity GAGAL. Umur/website UNVERIFIED. Bukan kandidat.")
note("ALIEN", f"Run 2001 (blok {BLOCK}): totalSupply 499->503 (+4) -> velocity GAGAL (<20). Bukan kandidat.")
note("ARKYN", f"Run 2001 (blok {BLOCK}): totalSupply 2289->2292 (+3) -> velocity GAGAL (<20). Bukan kandidat.")
note("Matrix", f"Run 2001 (blok {BLOCK}): totalSupply 630->632 (+2) -> velocity GAGAL. Bukan kandidat.")
note("SPARKS", f"Run 2001 (blok {BLOCK}): totalSupply 1207->1211 (+4) -> velocity GAGAL. Bukan kandidat.")

# ---- AONE track-C update ----
aone = snap.setdefault("track_c", {}).get("AONE")
if isinstance(aone, dict):
    aone["freeMinted"] = 9567
    aone["freeRemaining"] = 433
    aone["lastReadWib"] = NOW
    aone["note2001"] = ("Run 2001 (blok 134319057): freeMinted 7442 -> 9567 (+2125 dalam ~36,0 mnt, ~59/mnt - pool menguras sangat cepat), "
        "FREE_TOTAL 10000, tersisa 433. LAUNCH 1794999600 = 2026-11-18 18:00 WIB. "
        "Kuota user SUDAH 0 (minted-by-user 18:17 WIB, hero #3330/#3331). freeQuotaLeft/freeTaken/quote revert run ini (pool hampir habis / user sudah klaim). Tidak ada eksekusi ulang. DIAM.")
    print("AONE updated: freeMinted 9567, freeRemaining 433")
else:
    print("AONE MISSING from track_c!")

# ---- Track-B pending: binanceai.fun (re-read via leg4) ----
bc = snap.setdefault("pending_claims", {}).get("binanceai.fun")
if isinstance(bc, dict):
    bc["lastReadWib"] = NOW
    bc["runNote2001"] = ("Run 2001: launched=0, failed=1, isRefundPhase=1, totalShares 3110, tokenClaimed(user)=0 (blok 134319057) - tetap pending/refund, "
        "sudah dilaporkan sekali (fase refund 2026-11-02). DIAM.")
    print("binanceai note updated")

snap["last_run_wib"] = NOW
snap["last_run"] = ("free-mint-search 2026-11-18 20:01 WIB - 0 kandidat, 0 strong lead, 0 early lead baru, 0 track-B dibuka, "
    "0 track-C lead; PUNNY 37,7%, deadline 24 jam 20:32 WIB hari ini; STOCK AGENT inferred 71,2% (bukan counter terverifikasi) - tetap EARLY LEAD; "
    "AONE freeMinted 9567/10000 (tersisa 433), kuota user 0; egress degradasi: Boltbook EN+ZH + Sourcify feed TimeoutError, pre-flight timeout, 9 chunk error re-read.")
snap["runNote2001_1118"] = (
    f"Run 2001 (blok {BLOCK}, interval ~36,0 mnt vs 1931): "
    "0 kandidat baru, 0 strong lead baru/promosi, 0 early lead BARU, 0 track-B dibuka, 0 track-C lead BARU. "
    "Scan leg FAST-FAIL: Ankr pre-flight GAGAL setup OSError timeout (egress-wide, BUKAN 401); watermark TIDAK maju (tetap 134086385, gap ~232.672 blok). "
    "Reread Quicknode 285 calls, 9 chunk error (calls 200-244, TimeoutError; Velko/Crown/Longge/DGF/bsccat views gagal - nilai lama dipertahankan); elapsed run 579,7 dtk. "
    "Velocity: 0 LOLOS - maks +7 PUNNY, +4 STOCK AGENT/ALIEN/SPARKS, +3 Ledgera/EIM/PunchCard/AgentNOVA/ARKYN, +2 Matrix/Mine Card, +1 Bubblebruin/Lumenhold/RaceAgents/RAVE/THE WALL - semua <20 token. "
    "PUNNY 377/999 = 37,7% (<50%), umur terverifikasi ~23,5 jam (deadline 24 jam 20:32 WIB hari ini), slot user TERBUKA, website UNVERIFIED -> tetap EARLY LEAD. "
    "STOCK AGENT inferred 791/1111 = 71,2% (INFERENSI totalSupply, freeMinted/freeClaimed revert; umur + website UNVERIFIED) -> tetap EARLY LEAD, BUKAN strong lead. "
    "Di atas 70% TAPI umur UNVERIFIED -> BUKAN strong lead: Lumenhold 1257/1500 = 83,8%. "
    "Ledgera 54,1%, Bubblebruin 33,7%, CAT402 sold out 100/100, HIVE 1264 FLAT (minted-by-user). "
    "Vitaliq Scans: genesisStart 07:00 WIB (umur ~13 jam TERVERIFIKASI <24 jam), free%/website UNVERIFIED -> tetap EARLY LEAD. "
    "AONE track-C: freeMinted 7442 -> 9567 (+2125/~36 mnt, ~59/mnt), tersisa 433, LAUNCH 18:00 WIB; kuota user 0 (minted-by-user 18:17 WIB). DIAM. "
    "Boltbook EN+ZH GAGAL TimeoutError (tidak ada bacaan segar run ini, BUKAN 0 temuan). "
    "Sourcify feed GAGAL TimeoutError (0 alamat ter-shape-check run ini - belum terperiksa, BUKAN lolos). "
    "Sweep EN+ZH + share-sale (browser.search): 0 proyek segar baru - hanya proyek lama yang dikenal (Oathbots age-excluded, Agentic Gangster 9 Nov, "
    "LeadLoop/NEXUS/hackou Okt, JINCHAN tutup 10 Nov, BN Agent Trials season berakhir 8 Nov, QILIN/SAFU/PROXY/1 Nov, UFO tutup 12 Nov, "
    "NEBULA/VISION sudah di track_c). "
    "Bridge read-only: 116 kontrak, 0 baru, 7 same-owner-discarded - tidak berubah, tanpa promosi/perubahan. "
    "BinanceAI pending: launched=0, failed=1, isRefundPhase=1, tokenClaimed(user)=0 - tetap pending/refund, DIAM. "
    "DIAM (tidak ada laporan ke chat utama)."
)
json.dump(snap, open(f"{HF}/onchain-snapshot.json", "w"), indent=1)
print("snapshot saved")
