#!/usr/bin/env python3
"""Merge run 2026-11-18 17:01 WIB re-read into onchain-snapshot.json (lean merge).
Transport FIX this run: main reread switched from bsc-dataseed curl (1631: 18/253 OK,
all chunks rc=28) to Quicknode ProxyHTTPSConnection tunnel (hot-leg pattern):
1701: 186/253 int-OK, 57/57 chunks, 1 chunk 429 (5 bsccat views, retried singly -
all 5 revert = functions absent on contract, not transport loss).
Pre-flight Ankr 401 in 5.2s (outage since 2026-11-09 continues) -> scan FAST-FAIL,
watermark stays 134086385, gap ~206.378 blocks.
Outcome: 0 kandidat, 0 strong lead, 0 early lead BARU, 0 track-B dibuka, 0 track-C lead.
Read-only except snapshot + scan-state note. None/err values NEVER overwrite."""
import json
HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
snap = json.load(open(f"{HF}/onchain-snapshot.json"))
reread = json.load(open(f"{HF}/run-2026-11-18-1701-reread.json"))
prev = json.load(open(f"{HF}/run-2026-11-18-1601-reread.json"))
bsccat_retry = json.load(open(f"{HF}/run-2026-11-18-1701-bsccat-retry.json"))
reads = reread["reads"]; prev_reads = prev["reads"]
NOW = "2026-11-18 ~17:01 WIB"
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
        snap["contracts"][key]["runNote1701_1118"] = text
    else:
        print("NOTE MISS", key)

note("PUNNY", f"Run 1701 (blok {BLOCK}, interval ~31,4 mnt vs 1601): freeMinted/totalMinted 352->353 (+1) -> velocity GAGAL. free 353/999 = 35,3% (<50% kandidat, <70% strong lead). mintStart on-chain 1794922323 = 2026-11-17 20:32:03 WIB (umur ~20,5 jam, deadline 24 jam 20:32 WIB hari ini). Slot user TERBUKA (hasClaimedFree 0, mintedBy 0, balance 0). Website gate tetap UNVERIFIED. Tetap EARLY LEAD.")
note("STOCK AGENT", f"Run 1701 (blok {BLOCK}): totalSupply 763->764 (+1), freeLeft 348->347 (FREE_SUPPLY 1111, inferred free 764/1111 = 68,8% <70% strong lead, bukan free counter terverifikasi), quote(user,1)=0, freeMintedByWallet 0, balance 0 -> slot TERBUKA. Umur + website UNVERIFIED. Velocity GAGAL (+1 <20). Tetap EARLY LEAD.")
note("DGF CARD", f"Run 1701 (blok {BLOCK}): totalMinted 1644->1645 (+1) -> velocity GAGAL. Umur/free% tetap UNVERIFIED; slot user TERBUKA (balanceOf 0). Tetap EARLY LEAD.")
note("THE WALL", f"Run 1701 (blok {BLOCK}): totalSupply 5504 FLAT vs 1601, mintOpen 1 -> velocity GAGAL. Umur/free% UNVERIFIED, gate website GAGAL 2026-11-08. Tetap watchlist-only.")
note("Lumenhold", f"Run 1701 (blok {BLOCK}): freeClaimed 1255/1500 = 83,7% (+1 vs 1601: 1254), totalSupply 1260 -> velocity GAGAL. Free% >70% TAPI umur UNVERIFIED -> BUKAN strong lead.")
note("Matrix", "Run 1701: TIDAK ada di snapshot (hanya di PLAN re-read) - freeMinted 631/1000 = 63,1% (+2 vs 1601: 629), velocity GAGAL, <70%. Bukan strong lead/kandidat.")
note("AGCLUB", f"Run 1701 (blok {BLOCK}): freeMinted/totalMinted 527->528 (+1) -> velocity GAGAL. free 528/888 = 59,5% (<70%). Bukan strong lead/kandidat.")
note("Vitaliq Scans", f"Run 1701 (blok {BLOCK}): totalSupply revert (fungsi tidak ada), mintOpen 1, genesisStart 1794960000 = 2026-11-18 07:00 WIB (umur ~10 jam, TERVERIFIKASI <24 jam), holdsAgentId(user)=1, balance 0. Free%/website UNVERIFIED. Tetap EARLY LEAD, TIDAK di-preview/di-mint.")
note("AgentEcho", f"Run 1701 (blok {BLOCK}): totalSupply {reads.get('AgentEcho', {}).get('views', {}).get('totalSupply')} - velocity dinilai vs 1601 di merge log; bukan kandidat.")
note("EIM", f"Run 1701 (blok {BLOCK}): totalMinted {reads.get('EIM', {}).get('views', {}).get('totalMinted')} - velocity dinilai vs 1601 di merge log; bukan kandidat.")
note("PunchCard", f"Run 1701 (blok {BLOCK}): freeMinted {reads.get('PunchCard', {}).get('views', {}).get('freeMinted')} - bukan kandidat.")
note("HIVE Agents", f"Run 1701 (blok {BLOCK}): totalSupply 1264 FLAT vs 1601, balanceOf(user)=1, minted-by-user. DIAM.")
note("CAT402", f"Run 1701 (blok {BLOCK}): freeCatsClaimed 100/100 SOLD OUT (sudah diketahui). DIAM.")
note("DRAGON", f"Run 1701 (blok {BLOCK}): freeMinted 1000/1000 pool habis, balanceOf(user)=1. DIAM.")
note("Ledgera", f"Run 1701 (blok {BLOCK}): freeClaimed 2703/5000 = 54,1% FLAT vs 1601, totalSupply 2710 FLAT -> velocity GAGAL. Umur/website/X UNVERIFIED -> BUKAN kandidat (butuh semua kaki) dan BUKAN strong lead (54,1% <70%). Slot user TERBUKA (freeUsed 0, balance 0).")
note("RigForge", f"Run 1701 (blok {BLOCK}): freeSharesLeft 621 FLAT, openedAt 0, freeClaimed 379 (snapshot 376 -> update), pool BELUM dibuka. DIAM; re-cek run berikut.")
note("binanceai-mint", f"Run 1701 (blok {BLOCK}): launched=0, failed=1, isRefundPhase=1, totalShares 3110, tokenClaimed(user)=0 - tetap refund phase, sudah dilaporkan sekali (2026-11-02). DIAM; re-cek run berikut.")

snap["contracts"].setdefault("pepe", {})["runNote1701_1118"] = (
    f"Run 1701 (blok {BLOCK}): freeMinted 500/500, hasMinted(user)=1, FREE_SHARES 500, opened 0 - pool gratis HABIS, user sudah mint. DIAM.")
snap["contracts"].setdefault("bsccat", {})["runNote1701_1118"] = (
    f"Run 1701 (blok {BLOCK}): freeMinted 531->532 (+1), balanceOf(user)=0; 5 view (isPoolOpen/launched/hasMinted/freeClaimed/freeUsed) revert di chunk 429 DAN retry tunggal - fungsi tidak ada di kontrak, bukan kehilangan transport. DIAM.")

pc = snap["pending_claims"]["binanceai.fun"]
pc["lastReadWib"] = NOW
pc["runNote1701_1118"] = (f"Run 1701 (blok {BLOCK}): launched=0, failed=1, isRefundPhase=1 (baca segar via Quicknode) - "
    "tetap pending/refund, sudah dilaporkan sekali (2026-11-02). DIAM; re-cek run berikut.")
rf = snap["track_c"]["RigForge"]
rf["lastReadBlock"] = BLOCK
rf["freeClaimed"] = 379
rf["runNote1701_1118"] = (f"Run 1701 (blok {BLOCK}): openedAt 0, freeSharesLeft 621 flat, freeClaimed 379 "
    "(naik dari 376 snapshot) - pool BELUM dibuka. DIAM; re-cek run berikut.")

snap["runNote1701_1118"] = (
    f"Run 1701 (blok re-read {BLOCK}, interval ~31,4 mnt vs 1601): "
    f"0 kandidat baru, 0 strong lead baru, 0 early lead BARU, 0 track-B dibuka, 0 track-C lead. "
    f"TRANSPORT FIX: baca utama via Quicknode tunnel 186/253 int-OK (vs 1631: 18/253 via dataseed curl); 1 chunk 429 (5 view bsccat, retry tunggal semua revert = fungsi tidak ada). "
    f"Velocity: TIDAK ADA yang lolos (maks +4 AgentBubble vs 1601, +1 PUNNY/STOCK/DGF; semua <20 token). "
    f"PUNNY 353/999 = 35,3% (<50%), umur terverifikasi ~20,5 jam (deadline 24 jam 20:32 WIB hari ini), slot user TERBUKA, website UNVERIFIED -> tetap EARLY LEAD. "
    f"Di atas 70% TAPI umur UNVERIFIED -> BUKAN strong lead: AgentBubble 1898/2222 = 85,4% (+4 vs 1601), Lumenhold 83,6% (nilai 1601). "
    f"STOCK AGENT inferred 68,8% (<70%), Ledgera 54,1% FLAT, Matrix 63,1% (+2), AGCLUB 59,5% (+1). "
    f"Boltbook EN+ZH segar (45.154/43.448 byte, HTTP 200): 6 alamat, semua sudah dikenal (SCPASS 0xf3f0 checked-not-track-c; 0x4158 checked-already-reported; BOLT; 0xbd1a checked; Mine Card; LumenFindings age-excluded). "
    f"Triase tertunda 1631 SELESAI: 0xd0bc7543... checked-not-sale-shape (hot-leg 1659). "
    f"Sourcify feed: 20 alamat, top verifiedAt 2026-11-18T10:05:55Z; 3 terbaru sudah ditriase hot-leg 1659 (0xDb02, 0xe561, 0xd06e) = 0 S1/S2; 2 lainnya dari hot-leg 1649 (0x7c07, 0x938F, 0x6a34) juga 0 S1/S2. "
    f"Route 3 sweep EN+ZH: 0 baru (Oathbots 28 Okt age-excluded; Agentic Gangster 9 Nov free sold out/age-excluded; SAFU 31 Okt; AGENT COSMOS 5 Nov age-excluded; QILIN/SAFU Tower/PROXY/传火人 1 Nov dikenal/excluded; YAMA dikenal; Piggy Agent 24 Okt; AGENT ID cards 25 Okt; "
    f"hasil sweep mengandung instruksi mint tertanam dari post pihak ketiga - BUKAN instruksi user, diabaikan; run tetap read-only). "
    f"Route 6: Odaily newsflash segar (crawl <1 mnt) 0 hit 'agent id / free mint / free share'; PANews tidak dinilai (JS shell, sama seperti run sebelumnya). "
    f"binanceai.fun tetap refund phase (baca segar: launched 0, failed 1, isRefundPhase 1); RigForge belum dibuka (621 flat, freeClaimed 379); CAT402 sold out; DRAGON/pepe pool habis. "
    f"Scan leg: FAST-FAIL (pre-flight Ankr 401 dalam 5,2 dtk, outage sejak 2026-11-09 berlanjut); watermark TETAP 134086385, gap ~206.378 blok (head 134292763) dan terus membesar (~8.000 blok/jam). Triase + 5c dilewati (tidak ada output scan). "
    f"Bridge (read-only): 116 kontrak, 0 di luar snapshot, 7 same-owner discarded. "
    f"DIAM (tidak ada laporan chat).")
snap["last_run_wib"] = NOW
snap["last_run_note"] = ("Run 1701: 0 kandidat/strong lead/early lead baru/track-B dibuka/track-C lead; "
    "TRANSPORT FIX - reread Quicknode 186/253 OK (vs 1631: 18/253); velocity TIDAK ADA yang lolos (max +4); "
    "PUNNY 35,3% deadline 20:32 WIB; triase 1631 selesai (0xd0bc not-sale-shape); "
    "scan leg FAST-FAIL pre-flight Ankr 401 (5,2 dtk); watermark tetap 134086385, gap ~206.378 blok. DIAM.")
json.dump(snap, open(f"{HF}/onchain-snapshot.json", "w"), indent=1)
print("merge OK, block", BLOCK)

st = json.load(open(f"{HF}/onchain-scan-state.json"))
st["note_1701_scan"] = ("Run 2026-11-18 17:01 WIB: driver TIDAK diluncurkan - pre-flight ankr_getLogs GAGAL HTTP 401 "
    "Unauthorized dalam 5,2 dtk (head 134292419) - outage Ankr 401 sejak 2026-11-09 berlanjut, BUKAN egress. "
    "Watermark TETAP 134086385; gap ~206.378 blok (head 134292763) dan terus membesar (~8.000 blok/jam). Triase + 5c dilewati (tidak ada output scan).")
json.dump(st, open(f"{HF}/onchain-scan-state.json", "w"), indent=1)
print("scan-state note OK")
