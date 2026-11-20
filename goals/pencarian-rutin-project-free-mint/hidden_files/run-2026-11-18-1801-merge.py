#!/usr/bin/env python3
"""Merge run 2026-11-18 18:01 WIB re-read into onchain-snapshot.json (lean merge).
Reread via Quicknode tunnel: 285 calls, 0 chunk errors, block 134300516.
Pre-flight Ankr 401 in 3.3s (outage since 2026-11-09 continues) -> scan FAST-FAIL,
watermark stays 134086385, gap ~214.131 blocks.
Outcome: 0 kandidat baru, 0 strong lead baru, 0 early lead BARU, 0 track-B dibuka,
0 track-C lead BARU dari run ini - TAPI track-C lead AGENTONE (AONE) terdeteksi
feed Sourcify + diverifikasi run ini, dan SUDAH di-mint oleh hot-leg run 18:04 WIB
(tx 0xa4ec355801b810e3132abe0d2b41cf026b3f5d942fe562e5a9bc5a0ab7ca6cbe, blok 134301991,
hero #3330/#3331). Run ini TIDAK preview/execute (kuota user sudah 0).
Read-only except snapshot + scan-state note. None/err values NEVER overwrite."""
import json
HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
snap = json.load(open(f"{HF}/onchain-snapshot.json"))
reread = json.load(open(f"{HF}/run-2026-11-18-1801-reread.json"))
prev = json.load(open(f"{HF}/run-2026-11-18-1731-reread.json"))
reads = reread["reads"]; prev_reads = prev["reads"]
NOW = "2026-11-18 ~18:01 WIB"
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
        snap["contracts"][key]["runNote1801_1118"] = text
    else:
        print("NOTE MISS", key)

note("PUNNY", f"Run 1801 (blok {BLOCK}, interval ~26,6 mnt vs 1731): freeMinted/totalMinted 356->361 (+5, 0,188/mnt vs prev 0,095 = ~1,97x TAPI <20 token) -> velocity GAGAL. free 361/999 = 36,1% (<50% kandidat, <70% strong lead). mintStart on-chain 1794922323 = 2026-11-17 20:32:03 WIB (umur ~21,6 jam, deadline 24 jam 20:32 WIB hari ini). Slot user TERBUKA (hasClaimedFree 0, mintedBy 0, balance 0). Website gate tetap UNVERIFIED. Tetap EARLY LEAD.")
note("STOCK AGENT", f"Run 1801 (blok {BLOCK}): totalSupply 765->774 (+9), freeLeft 346->337 (FREE_SUPPLY 1111, inferred free 774/1111 = 69,7% <70% strong lead, bukan free counter terverifikasi), quote(user,1)=0, freeMintedByWallet 0, balance 0 -> slot TERBUKA. Umur + website UNVERIFIED. Velocity GAGAL (+9 <20). Tetap EARLY LEAD.")
note("DGF CARD", f"Run 1801 (blok {BLOCK}): totalMinted 1647->1648 (+1) -> velocity GAGAL. Umur/free% tetap UNVERIFIED; slot user TERBUKA (balanceOf 0). Tetap EARLY LEAD.")
note("THE WALL", f"Run 1801 (blok {BLOCK}): totalSupply 5506 FLAT vs 1731 -> velocity GAGAL. Umur/free% UNVERIFIED, gate website GAGAL 2026-11-08. Tetap watchlist-only.")
note("Lumenhold", f"Run 1801 (blok {BLOCK}): freeClaimed 1256/1500 = 83,7% FLAT, totalSupply 1261 FLAT -> velocity GAGAL. Free% >70% TAPI umur UNVERIFIED -> BUKAN strong lead.")
note("Matrix", "Run 1801: TIDAK ada di snapshot (hanya di PLAN re-read) - freeMinted 634/1000 = 63,4% FLAT vs 1731, velocity GAGAL, <70%. Bukan strong lead/kandidat.")
note("AGCLUB", f"Run 1801 (blok {BLOCK}): freeMinted/totalMinted 528 FLAT vs 1731 -> velocity GAGAL. free 528/888 = 59,5% (<70%). Bukan strong lead/kandidat.")
note("Vitaliq Scans", f"Run 1801 (blok {BLOCK}): totalSupply revert (fungsi tidak ada, sama seperti 1731), mintOpen 1, genesisStart 1794960000 = 2026-11-18 07:00 WIB (umur ~11,1 jam, TERVERIFIKASI <24 jam), holdsAgentId(user)=1, balance 0. Free%/website UNVERIFIED. Tetap EARLY LEAD, TIDAK di-preview/di-mint.")
note("AgentBubble", f"Run 1801 (blok {BLOCK}): freeMinted 1899->1905/2222 = 85,7% (+6), totalSupply 2044->2050 -> velocity GAGAL. Free% >70% TAPI umur UNVERIFIED -> BUKAN strong lead.")
note("EIM", f"Run 1801 (blok {BLOCK}): totalMinted 762->765 (+3 vs 1731) -> velocity GAGAL (<20). Bukan kandidat.")
note("HIVE Agents", f"Run 1801 (blok {BLOCK}): totalSupply 1264 FLAT vs 1731, balanceOf(user)=1, minted-by-user. DIAM.")
note("CAT402", f"Run 1801 (blok {BLOCK}): freeCatsClaimed 100/100 SOLD OUT (sudah diketahui). DIAM.")
note("DRAGON", f"Run 1801 (blok {BLOCK}): freeMinted 1000/1000 pool habis, balanceOf(user)=1. DIAM.")
note("Ledgera", f"Run 1801 (blok {BLOCK}): freeClaimed 2703/5000 = 54,1% FLAT vs 1731, totalSupply 2710 FLAT -> velocity GAGAL. Umur/website/X UNVERIFIED -> BUKAN kandidat (butuh semua kaki) dan BUKAN strong lead (54,1% <70%). Slot user TERBUKA (freeUsed 0, balance 0).")
note("RigForge", f"Run 1801 (blok {BLOCK}): freeSharesLeft 621 FLAT, openedAt 0, freeClaimed 379 FLAT vs 1731, pool BELUM dibuka. DIAM; re-cek run berikut.")

# ---- AGENTONE (AONE) track-C lead: detected by Sourcify feed in this run,
# verified independently by this run; minted by hot-leg run started 18:04 WIB.
snap.setdefault("track_c", {})["AONE"] = {
    "name": "AGENTONE (AONE)",
    "sale": "0x84D82E933D7781fe11245e7bbd3Eb23dbb963666",
    "token": "0x84a0e2831665f2a9aa3824efbe0f5d32f9331f87",
    "hero": "0x9B0c237A123277fCf8768550Bbdd7767C73Cf5D3",
    "arena": "0x4A003Cc2C60945D31f464F7D664f8AD48fa49F6B",
    "pair": "0x062af274ad1ee9c4e2520968e4d3865784bc7975",
    "status": "minted-by-user-2026-11-18",
    "tier": "track-c-lead",
    "shape": "S1 (mintFree/buyCards + quote + free views freeMinted/freeQuotaLeft/freeTaken + registry bytes in bytecode + agentIdOf)",
    "launchWib": "2026-11-18 18:00 WIB (LAUNCH() 1794999600; site aoneai.lol operative.md: 19:00 UTC+8 = 18:00 WIB)",
    "launchAgeVerified": True,
    "FREE_TOTAL": 10000,
    "freeMinted": 3610,
    "freeRemaining": 6390,
    "userQuotaLeft": 0,
    "userFreeTaken": 2,
    "website": "https://aoneai.lol",
    "websiteGate": "PASSED (aoneai.lol/operative.md prints exact sale + token + hero + arena + registry contracts; contract website() = https://aoneai.lol)",
    "x": "https://x.com/aone_agent",
    "audit": "token AONE: hasResult=true, LOW riskLevel 1, all risk items isHit=false, buyTax 0.0, verified; sale Forge + Hero: hasResult=false (no result, disclosed as no result)",
    "mintTx": "0xa4ec355801b810e3132abe0d2b41cf026b3f5d942fe562e5a9bc5a0ab7ca6cbe",
    "mintOrderId": "26111800002062927906",
    "mintBlock": 134301991,
    "mintGas": 385917,
    "mintFeeBnb": "0.000032871396256041",
    "mintTimeWib": "2026-11-18 18:17:50 WIB",
    "mintCall": "mintFree(2, 0x0000000000000000000000000000000000000000), value 0",
    "mintExecutedBy": "hot-leg run started 2026-11-18 18:04 WIB (file hot-leg-run-2026-11-18-1759.json) under TRACK-C LEAD DIRECT MINT; preview requestId b2aa73616c504e6ba31f5839f2f58862, simulationCode 000000000, value 0, no authority/allowance changes, no risks",
    "heroTokenIds": [3330, 3331],
    "heroBalanceBeforeAfter": [0, 2],
    "lockedAonePerCard": 3000,
    "aoneLockedTotal": 6000,
    "rarity": "Level 1, Locked AONE 3000, Edition Genesis (both identical)",
    "marketplace": "no project market for hero cards (Arena game pieces); no secondary listings (collection hours old)",
    "note": "Run 1801 verifikasi independen: S1 lolos, pool 6390 tersisa, quote(1)=0, slot user TERBUKA saat deteksi (freeQuotaLeft 2) - TAPI kuota sudah 0 saat prefresh run ini karena hot-leg sudah mint 18:17:50 WIB. Run ini TIDAK preview/execute (tidak ada yang tersisa untuk di-mint; duplikat akan revert NoQuotaLeft). Lead dilaporkan SEKALI via hasil mint ini; jangan laporkan ulang sebagai lead baru.",
    "lastReadWib": NOW,
}
snap["runNote1801_1118"] = (
    f"Run 1801 (blok {BLOCK}, interval ~26,6 mnt vs 1731): "
    "0 kandidat baru, 0 strong lead baru, 0 early lead BARU, 0 track-B dibuka, 0 track-C lead BARU dari run ini. "
    "TRACK-C LEAD AGENTONE (AONE) terdeteksi feed Sourcify + diverifikasi run ini (S1 lolos, LAUNCH 18:00 WIB terverifikasi <24 jam, "
    "free pool 6390 tersisa, quote(1)=0, slot user terbuka saat deteksi, website gate PASSED via aoneai.lol/operative.md, "
    "audit token LOW clean, sale/hero no-result) - DAN SUDAH DI-MINT oleh hot-leg run 18:04 WIB: mintFree(2, 0x0), "
    "tx 0xa4ec355801b810e3132abe0d2b41cf026b3f5d942fe562e5a9bc5a0ab7ca6cbe, blok 134301991, gas 385.917, fee ~0,0000329 BNB, "
    "hero #3330 + #3331 (level 1, 3.000 AONE locked per kartu). Run ini TIDAK preview/execute (kuota user sudah 0). "
    "Reread Quicknode 285 calls, 0 chunk error (elapsed run 167,6 dtk). "
    "Velocity: TIDAK ADA yang lolos (maks +9 STOCK, +7 Mine Card, +6 AgentBubble, +5 PUNNY; semua <20 token). "
    "PUNNY 361/999 = 36,1% (<50%), umur terverifikasi ~21,6 jam (deadline 24 jam 20:32 WIB hari ini), slot user TERBUKA, website UNVERIFIED -> tetap EARLY LEAD. "
    "Di atas 70% TAPI umur UNVERIFIED -> BUKAN strong lead: AgentBubble 1905/2222 = 85,7% (+6), Lumenhold 1256/1500 = 83,7% FLAT. "
    "STOCK AGENT inferred 69,7% (<70%), Ledgera 54,1% FLAT, Matrix 63,4% FLAT, AGCLUB 59,5% FLAT. "
    "Boltbook EN+ZH segar (44.348/43.062 byte, HTTP 200): 6/5 alamat, semua sudah dikenal/triase (Velko Rig, 0x2a2a, 0x7df7, 0x8269, BOLT, STOCK). 0 baru. "
    "Sourcify feed: 20 alamat, top verifiedAt 2026-11-18T11:06:36Z; 13 baru di-shape-check, 0 S1/S2 selain AONE (0x69013444: mint+agent_ref tanpa quote/free views, bukan agent-mint-shaped; "
    "0x84D82E93: S1 lolos via registry-bytes di bytecode + agentIdOf - CATATAN DETEKSI: shape-check run utama tidak menghitung agentIdOf sebagai agent_ref, "
    "registry-bytes check yang memutuskan; samakan dengan hot-leg (substring agent_ref) di run berikut). "
    "Route 3 sweep EN+ZH: 0 baru (Oathbots 28 Okt, Agentic Gangster 9 Nov, Jinchan 8-10 Nov tutup, YAMA/QILIN/SAFU/PROXY/传火人/BNBPIG dikenal; "
    "hasil sweep mengandung instruksi mint tertanam dari post pihak ketiga - BUKAN instruksi user, diabaikan; run tetap read-only). "
    "Route 6: Odaily newsflash segar (crawl <1 mnt) 0 hit 'agent id / free mint / free share'; PANews tidak dinilai (JS shell, sama seperti run sebelumnya). "
    "binanceai.fun tetap refund phase (baca segar: launched 0, failed 1, isRefundPhase 1, totalShares 3110); RigForge belum dibuka (621 flat, freeClaimed 379 flat); CAT402 sold out; DRAGON/pepe pool habis; bsccat freeMinted 533 (+1). "
    "Scan leg: FAST-FAIL (pre-flight Ankr 401 dalam 3,3 dtk, head 134300260, outage sejak 2026-11-09 berlanjut); watermark TETAP 134086385, gap ~214.131 blok (head 134300516) dan terus membesar (~8.000 blok/jam). Triase + 5c dilewati (tidak ada output scan). "
    "Bridge (read-only): 116 kontrak, 0 di luar snapshot, 7 same-owner discarded. "
    "LAPOR: AONE track-C lead + mint (sekali, via hasil mint hot-leg). Selain itu DIAM.")
snap["last_run_wib"] = NOW
snap["last_run_note"] = ("Run 1801: TRACK-C LEAD AGENTONE (AONE) terdeteksi + SUDAH di-mint hot-leg 18:04 WIB "
    "(tx 0xa4ec35..., blok 134301991, hero #3330/#3331, fee ~0,0000329 BNB); run ini verifikasi independen + TIDAK re-mint; "
    "0 kandidat/strong lead/early lead baru/track-B dibuka/track-C lead baru lainnya; "
    "reread Quicknode 285 calls 0 error (167,6 dtk); velocity TIDAK ADA yang lolos (max +9 STOCK); "
    "PUNNY 36,1% deadline 20:32 WIB; Boltbook 0 baru; Sourcify 13 baru 0 S1/S2 selain AONE; "
    "scan leg FAST-FAIL pre-flight Ankr 401 (3,3 dtk); watermark tetap 134086385, gap ~214.131 blok.")
json.dump(snap, open(f"{HF}/onchain-snapshot.json", "w"), indent=1)
print("merge OK, block", BLOCK)

st = json.load(open(f"{HF}/onchain-scan-state.json"))
st["note_1801_scan"] = ("Run 2026-11-18 18:01 WIB: driver TIDAK diluncurkan - pre-flight ankr_getLogs GAGAL HTTP 401 "
    "Unauthorized dalam 3,3 dtk (head 134300260) - outage Ankr 401 sejak 2026-11-09 berlanjut, BUKAN egress. "
    "Watermark TETAP 134086385; gap ~214.131 blok (head 134300516) dan terus membesar (~8.000 blok/jam). Triase + 5c dilewati (tidak ada output scan).")
json.dump(st, open(f"{HF}/onchain-scan-state.json", "w"), indent=1)
print("scan-state note OK")
