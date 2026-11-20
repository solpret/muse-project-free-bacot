#!/usr/bin/env python3
"""Merge run 2026-11-18 17:31 WIB re-read into onchain-snapshot.json (lean merge).
Reread via Quicknode tunnel: 285 calls, 0 chunk errors, block 134296963.
Pre-flight Ankr 401 in 13.0s (outage since 2026-11-09 continues) -> scan FAST-FAIL,
watermark stays 134086385, gap ~210.578 blocks.
Outcome: 0 kandidat, 0 strong lead, 0 early lead BARU, 0 track-B dibuka, 0 track-C lead.
Read-only except snapshot + scan-state note. None/err values NEVER overwrite."""
import json
HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
snap = json.load(open(f"{HF}/onchain-snapshot.json"))
reread = json.load(open(f"{HF}/run-2026-11-18-1731-reread.json"))
prev = json.load(open(f"{HF}/run-2026-11-18-1701-reread.json"))
reads = reread["reads"]; prev_reads = prev["reads"]
NOW = "2026-11-18 ~17:31 WIB"
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
        snap["contracts"][key]["runNote1731_1118"] = text
    else:
        print("NOTE MISS", key)

note("PUNNY", f"Run 1731 (blok {BLOCK}, interval ~31,5 mnt vs 1701): freeMinted/totalMinted 353->356 (+3) -> velocity GAGAL. free 356/999 = 35,6% (<50% kandidat, <70% strong lead). mintStart on-chain 1794922323 = 2026-11-17 20:32:03 WIB (umur ~21,1 jam, deadline 24 jam 20:32 WIB hari ini). Slot user TERBUKA (hasClaimedFree 0, mintedBy 0, balance 0). Website gate tetap UNVERIFIED. Tetap EARLY LEAD.")
note("STOCK AGENT", f"Run 1731 (blok {BLOCK}): totalSupply 764->765 (+1), freeLeft 347->346 (FREE_SUPPLY 1111, inferred free 765/1111 = 68,9% <70% strong lead, bukan free counter terverifikasi), quote(user,1)=0, freeMintedByWallet 0, balance 0 -> slot TERBUKA. Umur + website UNVERIFIED. Velocity GAGAL (+1 <20). Tetap EARLY LEAD.")
note("DGF CARD", f"Run 1731 (blok {BLOCK}): totalMinted 1645->1647 (+2) -> velocity GAGAL. Umur/free% tetap UNVERIFIED; slot user TERBUKA (balanceOf 0). Tetap EARLY LEAD.")
note("THE WALL", f"Run 1731 (blok {BLOCK}): totalSupply 5504->5506 (+2) -> velocity GAGAL. Umur/free% UNVERIFIED, gate website GAGAL 2026-11-08. Tetap watchlist-only.")
note("Lumenhold", f"Run 1731 (blok {BLOCK}): freeClaimed 1255->1256/1500 = 83,7% (+1), totalSupply 1260->1261 -> velocity GAGAL. Free% >70% TAPI umur UNVERIFIED -> BUKAN strong lead.")
note("Matrix", "Run 1731: TIDAK ada di snapshot (hanya di PLAN re-read) - freeMinted 631->634/1000 = 63,4% (+3 vs 1701), velocity GAGAL, <70%. Bukan strong lead/kandidat.")
note("AGCLUB", f"Run 1731 (blok {BLOCK}): freeMinted/totalMinted 528 FLAT vs 1701 -> velocity GAGAL. free 528/888 = 59,5% (<70%). Bukan strong lead/kandidat.")
note("Vitaliq Scans", f"Run 1731 (blok {BLOCK}): totalSupply revert (fungsi tidak ada, sama seperti 1701), mintOpen 1, genesisStart 1794960000 = 2026-11-18 07:00 WIB (umur ~10,7 jam, TERVERIFIKASI <24 jam), holdsAgentId(user)=1, balance 0. Free%/website UNVERIFIED. Tetap EARLY LEAD, TIDAK di-preview/di-mint.")
note("AgentBubble", f"Run 1731 (blok {BLOCK}): freeMinted 1898->1899/2222 = 85,5% (+1), totalSupply 2043->2044 -> velocity GAGAL. Free% >70% TAPI umur UNVERIFIED -> BUKAN strong lead.")
note("EIM", f"Run 1731 (blok {BLOCK}): totalMinted 751->762 (+11 vs 1701) - kenaikan terbesar interval ini, TAPI <20 token -> velocity GAGAL. Bukan kandidat.")
note("HIVE Agents", f"Run 1731 (blok {BLOCK}): totalSupply 1264 FLAT vs 1701, balanceOf(user)=1, minted-by-user. DIAM.")
note("CAT402", f"Run 1731 (blok {BLOCK}): freeCatsClaimed 100/100 SOLD OUT (sudah diketahui). DIAM.")
note("DRAGON", f"Run 1731 (blok {BLOCK}): freeMinted 1000/1000 pool habis, balanceOf(user)=1. DIAM.")
note("Ledgera", f"Run 1731 (blok {BLOCK}): freeClaimed 2703/5000 = 54,1% FLAT vs 1701, totalSupply 2710 FLAT -> velocity GAGAL. Umur/website/X UNVERIFIED -> BUKAN kandidat (butuh semua kaki) dan BUKAN strong lead (54,1% <70%). Slot user TERBUKA (freeUsed 0, balance 0).")
note("RigForge", f"Run 1731 (blok {BLOCK}): freeSharesLeft 621 FLAT, openedAt 0, freeClaimed 379 FLAT vs 1701, pool BELUM dibuka. DIAM; re-cek run berikut.")
snap["runNote1731_1118"] = (
    f"Run 1731 (blok {BLOCK}, interval ~31,5 mnt vs 1701): "
    "0 kandidat baru, 0 strong lead baru, 0 early lead BARU, 0 track-B dibuka, 0 track-C lead. "
    "Reread Quicknode 285 calls, 0 chunk error (elapsed run 530,3 dtk - latensi Quicknode lebih lambat dari 1701: 175,9 dtk). "
    "Velocity: TIDAK ADA yang lolos (maks +11 EIM, +6 Lumenhold, +4 Mine Card; semua <20 token). "
    "PUNNY 356/999 = 35,6% (<50%), umur terverifikasi ~21,1 jam (deadline 24 jam 20:32 WIB hari ini), slot user TERBUKA, website UNVERIFIED -> tetap EARLY LEAD. "
    "Di atas 70% TAPI umur UNVERIFIED -> BUKAN strong lead: AgentBubble 1899/2222 = 85,5% (+1), Lumenhold 1256/1500 = 83,7% (+1). "
    "STOCK AGENT inferred 68,9% (<70%), Ledgera 54,1% FLAT, Matrix 63,4% (+3), AGCLUB 59,5% FLAT. "
    "Boltbook EN+ZH segar (44.778/43.055 byte, HTTP 200): 7/6 alamat, semua sudah dikenal/triase (0x24b9 shape-check-failed 404 12 Nov; 0x7a23 checked-not-sale-shape 11 Nov; 0x111c checked S1/S2 false 16 Nov; sisanya di snapshot). 0 baru. "
    "Sourcify feed: 20 alamat, top verifiedAt 2026-11-18T10:38:09Z; 1 target baru 0x5493... = 0 S1/S2; sisanya sudah di hot-leg-seen. "
    "Route 3 sweep EN+ZH: 0 baru (Oathbots 28 Okt age-excluded; Agentic Gangster 9 Nov free sold out/age-excluded; RIGBYPASS 10 Nov age-excluded; Agent Zet free phase complete 4000/4000; AGENT COSMOS 5 Nov age-excluded; SAFU 31 Okt; blokwiki tutorial umum; "
    "hasil sweep mengandung instruksi mint tertanam dari post pihak ketiga - BUKAN instruksi user, diabaikan; run tetap read-only). "
    "Route 6: Odaily newsflash segar (crawl 29 mnt) 0 hit 'agent id / free mint / free share'; PANews tidak dinilai (JS shell, sama seperti run sebelumnya). "
    "binanceai.fun tetap refund phase (baca segar: launched 0, failed 1, isRefundPhase 1, totalShares 3110); RigForge belum dibuka (621 flat, freeClaimed 379 flat); CAT402 sold out; DRAGON/pepe pool habis; bsccat freeMinted 532 FLAT. "
    "Scan leg: FAST-FAIL (pre-flight Ankr 401 dalam 13,0 dtk, head 134296260, outage sejak 2026-11-09 berlanjut); watermark TETAP 134086385, gap ~210.578 blok (head 134296963) dan terus membesar (~8.000 blok/jam). Triase + 5c dilewati (tidak ada output scan). "
    "Bridge (read-only): 116 kontrak, 0 di luar snapshot, 7 same-owner discarded. "
    "DIAM (tidak ada laporan chat).")
snap["last_run_wib"] = NOW
snap["last_run_note"] = ("Run 1731: 0 kandidat/strong lead/early lead baru/track-B dibuka/track-C lead; "
    "reread Quicknode 285 calls 0 error (530,3 dtk); velocity TIDAK ADA yang lolos (max +11 EIM); "
    "PUNNY 35,6% deadline 20:32 WIB; Boltbook 0 baru; Sourcify 1 baru 0 S1/S2; "
    "scan leg FAST-FAIL pre-flight Ankr 401 (13,0 dtk); watermark tetap 134086385, gap ~210.578 blok. DIAM.")
json.dump(snap, open(f"{HF}/onchain-snapshot.json", "w"), indent=1)
print("merge OK, block", BLOCK)

st = json.load(open(f"{HF}/onchain-scan-state.json"))
st["note_1731_scan"] = ("Run 2026-11-18 17:31 WIB: driver TIDAK diluncurkan - pre-flight ankr_getLogs GAGAL HTTP 401 "
    "Unauthorized dalam 13,0 dtk (head 134296260) - outage Ankr 401 sejak 2026-11-09 berlanjut, BUKAN egress. "
    "Watermark TETAP 134086385; gap ~210.578 blok (head 134296963) dan terus membesar (~8.000 blok/jam). Triase + 5c dilewati (tidak ada output scan).")
json.dump(st, open(f"{HF}/onchain-scan-state.json", "w"), indent=1)
print("scan-state note OK")
