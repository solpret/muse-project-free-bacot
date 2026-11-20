#!/usr/bin/env python3
"""Merge run 2026-11-18 16:31 WIB re-read into onchain-snapshot.json (lean merge).
Egress degradation this run: main pass 18/253 reads OK (40/57 chunks curl rc=28),
retry pass 0/200 recovered (304,7 dtk, all endpoints timed out). Hot-leg 1629 +
1634 also FAILED (all legs timeout). Velocity assessed from freshest reliable
reads: hot-leg 1624 values (PUNNY 349, STOCK 760, DGF 1644) vs 1601 baseline.
Outcome: 0 kandidat, 0 strong lead, 0 early lead BARU, 0 track-B dibuka, 0 track-C lead.
Read-only except snapshot + scan-state note. None values NEVER overwrite."""
import json
HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
snap = json.load(open(f"{HF}/onchain-snapshot.json"))
reread = json.load(open(f"{HF}/run-2026-11-18-1631-reread-retry.json"))
prev = json.load(open(f"{HF}/run-2026-11-18-1601-reread.json"))
hl = json.load(open(f"{HF}/hot-leg-run-2026-11-18-1624-reread.json"))
reads = reread["reads"]; prev_reads = prev["reads"]; hl_reads = hl["reads"]
NOW = "2026-11-18 ~16:31 WIB"
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
    # velocity: fresh 1631 value if int, else hot-leg 1624 value if int
    pv = prev_reads.get(name, {}).get("views", {})
    hv = hl_reads.get(name, {}).get("views", {})
    fresh = v.get("totalSupply"); pval = pv.get("totalSupply"); view = "totalSupply"
    if fresh is None or not isinstance(fresh, int):
        fresh = hv.get("totalSupply")
    if fresh is None or not isinstance(fresh, int):
        fresh = v.get("totalMinted"); pval = pv.get("totalMinted"); view = "totalMinted"
        if fresh is None or not isinstance(fresh, int):
            fresh = hv.get("totalMinted")
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
print(f"updated {len(updated)} entries; missed: {missed}")
print("velocity PASS:", vel_pass)

def note(key, text):
    if key in snap.get("contracts", {}):
        snap["contracts"][key]["runNote1631_1118"] = text
    else:
        print("NOTE MISS", key)

note("PUNNY", f"Run 1631 (blok {BLOCK}, interval ~32,0 mnt vs 1601): baca utama GAGAL transport (chunk OSError) - nilai segar dari hot-leg 1624: totalMinted/freeMinted 348->349 (+1) -> velocity GAGAL. freeMinted 349/999 = 34,9% (<50% kandidat, <70% strong lead). mintStart on-chain 2026-11-17 20:32:03 WIB (umur ~20 jam, deadline 24 jam 20:32 WIB hari ini). Slot user TERBUKA (hasClaimedFree 0 hot-leg 1624). Website gate tetap UNVERIFIED. Tetap EARLY LEAD.")
note("STOCK AGENT", f"Run 1631 (blok {BLOCK}): baca utama GAGAL transport - nilai segar hot-leg 1624: totalSupply 759->760 (+1, <20) -> velocity GAGAL. freeLeft 351 (inferred free ~68,1%, <70% strong lead, bukan free counter terverifikasi), umur UNVERIFIED. Slot user TERBUKA (quote 0, freeMintedByWallet 0). Tetap EARLY LEAD.")
note("DGF CARD", f"Run 1631 (blok {BLOCK}): totalMinted 1644 (baca segar run ini; 1601: 1640, hot-leg 1624: 1644) -> +4 vs 1601, <20 -> velocity GAGAL. Umur/free% tetap UNVERIFIED; slot user TERBUKA (balanceOf 0). Tetap EARLY LEAD.")
note("THE WALL", f"Run 1631 (blok {BLOCK}): totalSupply 5504 (baca segar run ini; 1601: 5504 FLAT), mintOpen 1 -> velocity GAGAL. Umur/free% UNVERIFIED, gate website GAGAL 2026-11-08. Tetap watchlist-only.")
note("AgentBubble", f"Run 1631 (blok {BLOCK}): baca GAGAL transport (semua view None) - nilai terakhir run 1601 dipertahankan: freeMinted 1894/2222 = 85,2% (>70%) TAPI umur UNVERIFIED -> BUKAN strong lead. Tidak ada perubahan terverifikasi run ini.")
note("Lumenhold", f"Run 1631 (blok {BLOCK}): baca GAGAL transport - nilai terakhir run 1601 dipertahankan: freeClaimed 1254/1500 = 83,6% FLAT (>70%) TAPI umur UNVERIFIED -> BUKAN strong lead.")
note("Matrix", f"Run 1631 (blok {BLOCK}): baca GAGAL transport - nilai terakhir run 1601 dipertahankan: freeMinted 629/1000 = 62,9% (<70%). Bukan strong lead/kandidat.")
note("AGCLUB", f"Run 1631 (blok {BLOCK}): baca GAGAL transport - nilai terakhir run 1601 dipertahankan: freeMinted 527/888 = 59,3% FLAT (<70%). Bukan strong lead/kandidat.")
note("Vitaliq Scans", f"Run 1631 (blok {BLOCK}): baca GAGAL transport - nilai terakhir run 1601 dipertahankan: mintOpen 1, genesisStart 2026-11-18 07:00 WIB (umur ~9,5 jam, TERVERIFIKASI <24 jam), holdsAgentId(user)=1, balance 0. Free%/website UNVERIFIED. Tetap EARLY LEAD, TIDAK di-preview/di-mint.")
note("AgentEcho", f"Run 1631 (blok {BLOCK}): baca GAGAL transport - nilai terakhir run 1601 dipertahankan: totalSupply 401 (+9 vs 1531, <20) -> velocity GAGAL. Bukan kandidat.")
note("EIM", f"Run 1631 (blok {BLOCK}): baca GAGAL transport - nilai terakhir run 1601 dipertahankan: totalMinted 742 (+6, <20) -> velocity GAGAL. Bukan kandidat.")
note("PunchCard", f"Run 1631 (blok {BLOCK}): baca GAGAL transport - nilai terakhir run 1601 dipertahankan: freeMinted 1321/5555 = 23,8%. Bukan kandidat.")
note("HIVE Agents", f"Run 1631 (blok {BLOCK}): baca GAGAL transport - nilai terakhir run 1601 dipertahankan: totalSupply 1264 FLAT, balanceOf(user)=1. DIAM.")
note("CAT402", f"Run 1631 (blok {BLOCK}): baca GAGAL transport - nilai terakhir run 1601 dipertahankan: freeCatsClaimed 100/100 SOLD OUT (sudah diketahui). DIAM.")
note("DRAGON", f"Run 1631 (blok {BLOCK}): baca GAGAL transport - nilai terakhir run 1601 dipertahankan: freeMinted 1000/1000 pool habis, balanceOf(user)=1. DIAM.")
note("RigForge", f"Run 1631 (blok {BLOCK}): baca GAGAL transport (freeSharesLeft/openedAt/freeClaimed None) - nilai terakhir run 1601 dipertahankan: openedAt 0, freeSharesLeft 621 FLAT, freeClaimed 379 FLAT - pool BELUM dibuka. DIAM; re-cek run berikut.")
note("binanceai-mint", f"Run 1631 (blok {BLOCK}): baca GAGAL transport (launched/failed/isRefundPhase None) - nilai terakhir run 1601 dipertahankan: launched=0, failed=1, isRefundPhase=1, tokenClaimed(user)=0, totalShares 3110 - tetap refund phase, sudah dilaporkan sekali (2026-11-02). DIAM; re-cek run berikut.")

snap["contracts"].setdefault("pepe", {})["runNote1631_1118"] = (
    f"Run 1631 (blok {BLOCK}): freeMinted 500/500 (baca segar run ini), hasMinted(user)=1, FREE_SHARES 500, opened 0 - pool gratis HABIS, user sudah mint. DIAM.")
snap["contracts"].setdefault("bsccat", {})["runNote1631_1118"] = (
    f"Run 1631 (blok {BLOCK}): baca GAGAL transport (23/26 view None) - nilai terakhir run 1601 dipertahankan: freeMinted 531 FLAT. DIAM.")

pc = snap["pending_claims"]["binanceai.fun"]
pc["lastReadWib"] = NOW
pc["runNote1631_1118"] = (f"Run 1631 (blok {BLOCK}): baca GAGAL transport (launched/failed/isRefundPhase None) - "
    "nilai terakhir run 1601 dipertahankan (launched=0, failed=1, isRefundPhase=1) - tetap pending/refund, sudah dilaporkan sekali (2026-11-02). DIAM; re-cek run berikut.")
rf = snap["track_c"]["RigForge"]
rf["lastReadBlock"] = BLOCK
rf["runNote1631_1118"] = (f"Run 1631 (blok {BLOCK}): baca GAGAL transport - nilai terakhir run 1601 dipertahankan "
    "(openedAt 0, freeSharesLeft 621 flat, freeClaimed 379 flat) - pool BELUM dibuka. DIAM; re-cek run berikut.")

snap["runNote1631_1118"] = (
    f"Run 1631 (blok re-read {BLOCK}, interval ~32,0 mnt vs 1601): "
    f"0 kandidat baru, 0 strong lead baru, 0 early lead BARU, 0 track-B dibuka, 0 track-C lead. "
    f"DEGRADASI EGRESS: baca utama hanya 18/253 OK (40/57 chunk curl rc=28, 327,9 dtk); retry pass 0/200 recovered (304,7 dtk, semua endpoint timeout); "
    f"hot-leg 1629 + 1634 JUGA FAILED (semua leg timeout). Pre-flight Ankr GAGAL timeout (bukan 401) - egress-wide, bukan auth. "
    f"Velocity dinilai dari baca segar hot-leg 1624 (PUNNY +1, STOCK +1, DGF +4 vs 1601, semua <20 token) -> TIDAK ADA yang lolos. "
    f"PUNNY 349/999 = 34,9% (<50%), umur terverifikasi ~20 jam (deadline 24 jam 20:32 WIB hari ini), slot user TERBUKA, website UNVERIFIED -> tetap EARLY LEAD. "
    f"Di atas 70% TAPI umur UNVERIFIED -> BUKAN strong lead: AgentBubble 85,2%, Lumenhold 83,6% (nilai 1601 dipertahankan, baca 1631 gagal). "
    f"Boltbook EN+ZH segar (44.746/43.350 byte, HTTP 200): 6/7 alamat, semua sudah di snapshot kecuali 0xd0bc754349b9f50580d567f7bd112cf0074cfb83 - "
    f"TRIAGE TERTUNDA (fetch Sourcify timeout 2x, exit 28) -> re-cek run berikut, BUKAN lead. Alamat lain: Rulz Share, Lion's Share, BOLT, Mine Card, FIND exp43 (tutup), 0x8269. "
    f"Sourcify feed: 20 alamat, top verifiedAt 2026-11-18T09:36:13Z; hot-leg 1624 sudah triase 4 terbaru (0x3A37, 0x786D, 0x9485, 0x6742) + 2 Boltbook baru (0x9b2e, 0xe35c) = 0 S1/S2. "
    f"Sisa 16 alamat feed BELUM tertriase run ini (per-item verifiedAt tak terambil - fetch feed timeout) -> re-cek run berikut. "
    f"Route 3 sweep EN+ZH: 0 baru (Oathbots 28 Okt age-excluded; Agentic Gangster 9 Nov free sold out; RIGBYPASS 10 Nov, 1111 free, age >24 jam -> age-excluded; "
    f"MOLT AGENT 6 Nov, 25 free, age >24 jam -> age-excluded; AGENT COSMOS 5 Nov; BN Agent Trials season berakhir 8 Nov; YAMA dikenal; "
    f"hasil sweep mengandung instruksi mint tertanam dari post pihak ketiga, BUKAN instruksi user, diabaikan; run tetap read-only). "
    f"Route 6: Odaily newsflash segar (crawl <1 mnt) 0 hit 'agent id / free mint / free share'; PANews tidak dinilai (JS shell, sama seperti run sebelumnya). "
    f"binanceai.fun tetap refund phase (nilai 1601, baca 1631 gagal); RigForge belum dibuka (621 flat, nilai 1601); CAT402 sold out; DRAGON/pepe pool habis. "
    f"Scan leg: FAST-FAIL (pre-flight timeout); watermark TETAP 134086385, gap ~202.193 blok dan terus membesar (~8.000 blok/jam). Triase + 5c dilewati (tidak ada output scan). "
    f"Bridge (read-only): 116 kontrak, 0 di luar snapshot, 7 same-owner discarded. "
    f"DIAM (tidak ada laporan chat).")
snap["last_run_wib"] = NOW
snap["last_run_note"] = ("Run 1631: 0 kandidat/strong lead/early lead baru/track-B dibuka/track-C lead; "
    "EGRESS DEGRADASI - baca utama 18/253 OK, retry 0/200, hot-leg 1629+1634 FAILED; velocity TIDAK ADA yang lolos (max DGF +4 <20, via hot-leg 1624); "
    "PUNNY 34,9% deadline 20:32 WIB; triase tertunda: Boltbook 0xd0bc + 16 alamat feed Sourcify (fetch timeout) -> re-cek run berikut; "
    "scan leg FAST-FAIL pre-flight timeout (bukan 401); watermark tetap 134086385, gap ~202.193 blok. DIAM.")
json.dump(snap, open(f"{HF}/onchain-snapshot.json", "w"), indent=1)
print("merge OK, block", BLOCK)

st = json.load(open(f"{HF}/onchain-scan-state.json"))
st["note_1631_scan"] = ("Run 2026-11-18 16:31 WIB: driver TIDAK diluncurkan - pre-flight ankr_getLogs GAGAL timeout "
    "(setup OSError: batch failed on all healthy endpoints: timed out) - egress-wide, BUKAN 401 auth. "
    "Watermark TETAP 134086385; gap ~202.193 blok (head 134288578) dan terus membesar (~8.000 blok/jam). Triase + 5c dilewati (tidak ada output scan).")
json.dump(st, open(f"{HF}/onchain-scan-state.json", "w"), indent=1)
print("scan-state note OK")
