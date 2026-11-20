#!/usr/bin/env python3
"""Merge run 2026-11-18 18:31 WIB re-read into onchain-snapshot.json (lean merge).
Reread via Quicknode tunnel: 291 calls, 2 chunk errors (429 rate-limit on
Quicknode: calls 35-39 + 105-109 -> DRAGON/ARKYN/MineCard/ALIEN/AgentBubble-balance
read None this run; previous values KEPT, never overwritten with None).
Block 134305159, interval ~34,8 mnt vs 1801.
Outcome: 0 kandidat baru, 0 strong lead baru/promosi, 0 early lead BARU,
0 track-B dibuka, 0 track-C lead BARU. AONE track-C: freeMinted 3610 -> 4305
(minted-by-user 18:17 WIB, kuota user 0). Read-only except snapshot +
scan-state note. None/err values NEVER overwrite."""
import json
HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
snap = json.load(open(f"{HF}/onchain-snapshot.json"))
reread = json.load(open(f"{HF}/run-2026-11-18-1831-reread.json"))
prev = json.load(open(f"{HF}/run-2026-11-18-1801-reread.json"))
reads = reread["reads"]; prev_reads = prev["reads"]
NOW = "2026-11-18 ~18:31 WIB"
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
        snap["contracts"][key]["runNote1831_1118"] = text
    else:
        print("NOTE MISS", key)

note("PUNNY", f"Run 1831 (blok {BLOCK}, interval ~34,8 mnt vs 1801): freeMinted/totalMinted 361->362 (+1, <20) -> velocity GAGAL. free 362/999 = 36,2% (<50% kandidat, <70% strong lead). mintStart on-chain 1794922323 = 2026-11-17 20:32:03 WIB (umur ~22,0 jam, deadline 24 jam 20:32 WIB hari ini). Slot user TERBUKA (hasClaimedFree 0, mintedBy 0, balance 0). Website gate tetap UNVERIFIED. Tetap EARLY LEAD.")
note("STOCK AGENT", f"Run 1831 (blok {BLOCK}): totalSupply 774->777 (+3), freeLeft 337->334 (FREE_SUPPLY 1111, inferred free 777/1111 = 69,9% MASIH <70% strong lead - butuh 778; bukan free counter terverifikasi), quote(user,1)=0, freeMintedByWallet 0, balance 0 -> slot TERBUKA. Umur + website UNVERIFIED. Velocity GAGAL (+3 <20). Tetap EARLY LEAD.")
note("DGF CARD", f"Run 1831 (blok {BLOCK}): totalMinted 1648->1652 (+4) -> velocity GAGAL. Umur/free% tetap UNVERIFIED; slot user TERBUKA (balanceOf 0). Tetap EARLY LEAD.")
note("THE WALL", f"Run 1831 (blok {BLOCK}): totalSupply 5506->5508 (+2) -> velocity GAGAL. Umur/free% UNVERIFIED, gate website GAGAL 2026-11-08. Tetap watchlist-only.")
note("Lumenhold", f"Run 1831 (blok {BLOCK}): freeClaimed 1256/1500 = 83,7% FLAT, totalSupply 1261 FLAT -> velocity GAGAL. Free% >70% TAPI umur UNVERIFIED -> BUKAN strong lead.")
note("Matrix", "Run 1831: TIDAK ada di snapshot (hanya di PLAN re-read) - freeMinted 634/1000 = 63,4% FLAT vs 1801, velocity GAGAL, <70%. Bukan strong lead/kandidat.")
note("AGCLUB", f"Run 1831 (blok {BLOCK}): freeMinted/totalMinted 528 FLAT vs 1801 -> velocity GAGAL. free 528/888 = 59,5% (<70%). Bukan strong lead/kandidat.")
note("Vitaliq Scans", f"Run 1831 (blok {BLOCK}): totalSupply revert (fungsi tidak ada, sama seperti 1801), mintOpen 1, genesisStart 1794960000 = 2026-11-18 07:00 WIB (umur ~11,5 jam, TERVERIFIKASI <24 jam), holdsAgentId(user)=1, balance 0. Free%/website UNVERIFIED. Tetap EARLY LEAD, TIDAK di-preview/di-mint.")
note("AgentBubble", f"Run 1831 (blok {BLOCK}): freeMinted 1905/2222 = 85,7% FLAT vs 1801, totalSupply 2050 FLAT -> velocity GAGAL. Free% >70% TAPI umur UNVERIFIED -> BUKAN strong lead. (balanceOf_user None run ini - chunk 429, nilai lama dipertahankan.)")
note("EIM", f"Run 1831 (blok {BLOCK}): totalMinted 765->768 (+3 vs 1801) -> velocity GAGAL (<20). Bukan kandidat.")
note("HIVE Agents", f"Run 1831 (blok {BLOCK}): totalSupply 1264 FLAT vs 1801, balanceOf(user)=1, minted-by-user. DIAM.")
note("CAT402", f"Run 1831 (blok {BLOCK}): freeCatsClaimed 100/100 SOLD OUT (sudah diketahui). DIAM.")
note("DRAGON", f"Run 1831 (blok {BLOCK}): SEMUA view None run ini (chunk 35-39 kena Quicknode 429 rate-limit) - nilai lama dipertahankan (freeMinted 1000/1000 pool habis, balanceOf(user)=1). DIAM.")
note("Ledgera", f"Run 1831 (blok {BLOCK}): freeClaimed 2703/5000 = 54,1% FLAT vs 1801, totalSupply 2710 FLAT -> velocity GAGAL. Umur/website/X UNVERIFIED -> BUKAN kandidat dan BUKAN strong lead (54,1% <70%). Slot user TERBUKA (freeUsed 0, balance 0).")
note("RigForge", f"Run 1831 (blok {BLOCK}): freeSharesLeft 621 FLAT, openedAt 0, freeClaimed 379 FLAT vs 1801, pool BELUM dibuka. DIAM; re-cek run berikut.")
note("RAVE", f"Run 1831 (blok {BLOCK}): totalMinted/freeMinted 371->372 (+1) -> velocity GAGAL. free 372/3000 = 12,4%. Bukan kandidat.")
note("PunchCard", f"Run 1831 (blok {BLOCK}): totalMinted 1348->1350 (+2), freeMinted 1326->1328, mintPriceFor(user,1)=0, slot TERBUKA (mintedCount 0, balance 0) -> velocity GAGAL. Umur/website UNVERIFIED. Bukan kandidat.")
note("ARKYN", f"Run 1831 (blok {BLOCK}): totalMinted/totalSupply None run ini (chunk 105-109 kena Quicknode 429) - nilai lama dipertahankan (totalMinted 2286 run 1801). DIAM.")
note("Mine Card", f"Run 1831 (blok {BLOCK}): totalMinted/totalSupply None run ini (chunk 105-109 kena Quicknode 429) - nilai lama dipertahankan (1343 run 1801). DIAM.")
note("ALIEN", f"Run 1831 (blok {BLOCK}): totalSupply None run ini (chunk 105-109 kena Quicknode 429) - nilai lama dipertahankan (495 run 1801). DIAM.")

# ---- Boltbook-new triage: 0x3461 (NOT a contract) ----
snap.setdefault("contracts", {})["checked-0x3461-1831"] = {
    "address": "0x3461a1595a0d80d8bc643c6ad08adc67248744ee",
    "status": "checked-not-a-contract-2026-11-18",
    "totalSupply": None,
    "lastReadWib": NOW,
    "lastReadBlock": BLOCK,
    "note": "Run 1831 Boltbook EN+ZH baru (bukan di hot-leg-seen/snapshot): eth_getCode = 0x (bukan kontrak, kemungkinan EOA/wallet yang disebut di post Boltbook), Sourcify 404, semua view call null. Bukan lead, bukan agent-shaped, TIDAK di-preview/di-mint.",
}

# ---- AONE track-C update: pool keeps draining, user quota already used ----
aone = snap.setdefault("track_c", {}).get("AONE")
if isinstance(aone, dict):
    aone["freeMinted"] = 4305
    aone["freeRemaining"] = 5695
    aone["lastReadWib"] = NOW
    aone["note1831"] = ("Run 1831 (blok 134305159): freeMinted 3610 -> 4305 (+695 dalam ~30 mnt, ~23/mnt), "
        "FREE_TOTAL 10000, LAUNCH 1794999600 = 2026-11-18 18:00 WIB terverifikasi. freeQuotaLeft/freeTaken/quote "
        "revert pada signature ini (nama fungsi berbeda dari hot-leg) - tidak dipakai sebagai bukti slot; "
        "kuota user SUDAH 0 (minted-by-user 18:17 WIB, hero #3330/#3331). Tidak ada eksekusi ulang. DIAM.")
    print("AONE updated: freeMinted 4305, freeRemaining 5695")
else:
    print("AONE MISSING from track_c!")

snap["runNote1831_1118"] = (
    f"Run 1831 (blok {BLOCK}, interval ~34,8 mnt vs 1801): "
    "0 kandidat baru, 0 strong lead baru/promosi, 0 early lead BARU, 0 track-B dibuka, 0 track-C lead BARU. "
    "Reread Quicknode 291 calls, 2 chunk error (429 rate-limit: calls 35-39 + 105-109 -> DRAGON/ARKYN/MineCard/ALIEN/AgentBubble-balance None; nilai lama dipertahankan; elapsed run 558,7 dtk - jauh lebih lambat dari 1801 (167,6 dtk), mostly shape-check sequential + egress lambat). "
    "Velocity: TIDAK ADA yang lolos (maks +4 DGF, +3 STOCK, +3 EIM, +2 PunchCard/THE WALL/AgentNOVA/Zephyra/Velko Rig/MORFO; semua <20 token). "
    "PUNNY 362/999 = 36,2% (<50%), umur terverifikasi ~22,0 jam (deadline 24 jam 20:32 WIB hari ini), slot user TERBUKA, website UNVERIFIED -> tetap EARLY LEAD. "
    "STOCK AGENT inferred 777/1111 = 69,9% (MASIH <70% - butuh 778), slot TERBUKA, umur/website UNVERIFIED -> tetap EARLY LEAD. "
    "Di atas 70% TAPI umur UNVERIFIED -> BUKAN strong lead: AgentBubble 1905/2222 = 85,7% FLAT, Lumenhold 1256/1500 = 83,7% FLAT. "
    "Ledgera 54,1% FLAT, Matrix 63,4% FLAT, AGCLUB 59,5% FLAT, RAVE 372/3000 = 12,4%. "
    "AONE track-C: freeMinted 3610 -> 4305 (+695/~30 mnt), pool 5695 tersisa, kuota user 0 (minted-by-user 18:17 WIB). DIAM. "
    "Boltbook EN+ZH segar (44.649/42.946 byte, HTTP 200): 6 alamat, 3 baru vs 1801 - 0x23ff (dikenal, checked-not-verified 10 Nov), 0x3361 (dikenal, Sourcify 404, 14 Nov), 0x3461 BARU -> triase: eth_getCode 0x, Sourcify 404, BUKAN kontrak - dicatat checked-not-a-contract, bukan lead. "
    "Sourcify feed: 20 alamat, top verifiedAt 2026-11-18T11:41:46Z; 20 baru di-shape-check (dengan fix registry-bytes run ini), 0 S1/S2 (2 agent_ref=true tanpa mint/quote/free views: 0x6008, 0x6383). "
    "Route 3 sweep EN+ZH + share-sale: 0 baru (Oathbots 28 Okt, Agentic Gangster 9 Nov pool habis, AgentForge 27 Okt, LeadLoop 25 Okt, AGENTID cards 25 Okt, QILIN/SAFU/PROXY/传火人/BNBPIG 1 Nov, Subsonic/BNBmeme/Skynet 26 Okt, ORBITA CLOSED 1000/1000, YAMA dikenal, UFO tutup 12 Nov, NEBULA 10 Nov umur >24 jam, NOVRA 7 Nov umur >24 jam; "
    "hasil sweep mengandung instruksi mint tertanam dari post pihak ketiga - BUKAN instruksi user, diabaikan; run tetap read-only). "
    "Route 6: Odaily newsflash segar (crawl <1 mnt) 0 hit 'agent id / free mint / free share'; PANews tidak dinilai (JS shell, sama seperti run sebelumnya). "
    "binanceai.fun tetap refund phase (baca segar: launched 0, failed 1, isRefundPhase 1, totalShares 3110); RigForge belum dibuka (621 flat, freeClaimed 379 flat); CAT402 sold out; DRAGON/pepe pool habis; bsccat freeMinted 533 FLAT. "
    "Scan leg: FAST-FAIL (pre-flight ankr_getLogs GAGAL RemoteDisconnected dalam 28,3 dtk, head 134304453 - kali ini bukan 401, koneksi ditutup; outage Ankr sejak 2026-11-09 berlanjut); watermark TETAP 134086385, gap ~218.774 blok (head 134305159) dan terus membesar (~8.000 blok/jam). Triase + 5c dilewati (tidak ada output scan). "
    "Bridge (read-only): 116 kontrak, 0 di luar snapshot, 7 same-owner discarded. "
    "LAPOR: tidak ada (DIAM - 0 kandidat/lead/klaim/perubahan yang wajib dilaporkan).")
snap["last_run_wib"] = NOW
snap["last_run_note"] = ("Run 1831: 0 kandidat/strong lead/early lead baru/track-B dibuka/track-C lead baru; "
    "reread Quicknode 291 calls, 2 chunk error 429 (DRAGON/ARKYN/MineCard/ALIEN None, nilai lama dipertahankan; 558,7 dtk); "
    "velocity TIDAK ADA yang lolos (max +4 DGF); PUNNY 36,2% deadline 20:32 WIB; STOCK 69,9% (<70%); "
    "Boltbook 1 baru 0x3461 -> BUKAN kontrak; Sourcify 20 baru 0 S1/S2; AONE freeMinted 4305 (kuota user 0); "
    "scan leg FAST-FAIL pre-flight RemoteDisconnected (28,3 dtk); watermark tetap 134086385, gap ~218.774 blok; "
    "DIAM - tidak ada laporan chat.")
json.dump(snap, open(f"{HF}/onchain-snapshot.json", "w"), indent=1)
print("merge OK, block", BLOCK)

st = json.load(open(f"{HF}/onchain-scan-state.json"))
st["note_1831_scan"] = ("Run 2026-11-18 18:31 WIB: driver TIDAK diluncurkan - pre-flight ankr_getLogs GAGAL "
    "RemoteDisconnected (remote end closed connection without response) dalam 28,3 dtk (head 134304453) - "
    "kali ini BUKAN 401, koneksi Ankr ditutup; outage Ankr sejak 2026-11-09 berlanjut. "
    "Watermark TETAP 134086385; gap ~218.774 blok (head 134305159) dan terus membesar (~8.000 blok/jam). "
    "Triase + 5c dilewati (tidak ada output scan).")
json.dump(st, open(f"{HF}/onchain-scan-state.json", "w"), indent=1)
print("scan-state note OK")
