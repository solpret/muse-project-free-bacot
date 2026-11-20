#!/usr/bin/env python3
"""Merge run 2026-11-18 13:31 WIB re-read into onchain-snapshot.json (lean merge).
Read-only legs only. Never writes scan-bridge.json. No preview/mint/claim.
NEW THIS RUN: Vitaliq Scans 0xad0d...68ec = EARLY LEAD (first-seen this run,
agent-shaped, launch verified 07:00 WIB today, 405 scans) -> added to watchlist.
Urbanova 0x02a9 age-excluded (genesisStart 16 Nov 11:27 WIB). Fixes carried:
main script now runs re-read chunks 8-way parallel (first 1331 attempt killed
at 420s sequential); newleads 35-call single batch rejected -32005, re-read
via chunked <=5 fix script."""
import json
HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
snap = json.load(open(f"{HF}/onchain-snapshot.json"))
reread = json.load(open(f"{HF}/run-2026-11-18-1331-reread.json"))
prev = json.load(open(f"{HF}/run-2026-11-18-1301-reread.json"))
newleads = json.load(open(f"{HF}/run-2026-11-18-1331-newleads.json"))
fix = json.load(open(f"{HF}/run-2026-11-18-1331-newleads-fix.json"))
reads = reread["reads"]
prev_reads = prev["reads"]
NOW = "2026-11-18 ~13:31 WIB"
BLOCK = reread["block"]
PREV_BLOCK = prev["block"]
INTERVAL_MIN = (BLOCK - PREV_BLOCK) * 0.45 / 60.0
print(f"block {BLOCK} prev {PREV_BLOCK} interval {INTERVAL_MIN:.1f} min")

addr2key = {}
for _k, _v in snap.get("contracts", {}).items():
    if isinstance(_v, dict) and isinstance(_v.get("address"), str):
        addr2key[_v["address"].lower()] = _k

updated, missed = [], []
for name, d in reads.items():
    addr = d.get("address", "")
    key = addr2key.get(addr.lower()) if isinstance(addr, str) else None
    if key is None:
        missed.append(name)
        continue
    e = snap["contracts"][key]
    v = d.get("views", {})
    for f, val in v.items():
        if isinstance(val, int):
            e[f] = val
    pv = prev_reads.get(name, {}).get("views", {})
    fresh = v.get("totalSupply")
    pval = pv.get("totalSupply")
    view = "totalSupply"
    if fresh is None or not isinstance(fresh, int):
        fresh = v.get("totalMinted")
        pval = pv.get("totalMinted")
        view = "totalMinted"
    if isinstance(fresh, int) and isinstance(pval, int):
        minted = fresh - pval
        rate = minted / INTERVAL_MIN if INTERVAL_MIN > 0 else 0.0
        prev_rate = e.get("currentRatePerMin")
        ratio = (rate / prev_rate) if isinstance(prev_rate, (int, float)) and prev_rate else None
        vel = bool(ratio is not None and ratio >= 1.5 and minted >= 20)
        e["previousTotalSupply"] = pval
        e["mintedInInterval"] = minted
        e["intervalMinutes"] = round(INTERVAL_MIN, 1)
        e["currentRatePerMin"] = round(rate, 4)
        e["previousRatePerMin"] = prev_rate
        e["velocityRatio"] = round(ratio, 2) if ratio is not None else None
        e["velocityLegPasses"] = vel
        e["supplyView"] = view
    e["lastReadWib"] = NOW
    e["lastReadBlock"] = BLOCK
    updated.append((name, key))
print(f"updated {len(updated)} entries; missed (no snapshot key): {missed}")

def note(key, text):
    if key in snap.get("contracts", {}):
        snap["contracts"][key]["runNote1331_1118"] = text
    else:
        print("NOTE MISS", key)

note("PUNNY", f"Run 1331 (blok {BLOCK}): totalMinted 293->304 (+11), freeMinted 304/999 = 30,4% (<50% kandidat, <70% strong lead). mintStart on-chain 1794922323 = 2026-11-17 20:32:03 WIB (umur ~17 jam, tutup 20:32 WIB hari ini). Slot user TERBUKA (hasClaimedFree 0, mintedBy 0, balance 0). Website gate tetap UNVERIFIED. Tetap EARLY LEAD, tanpa promosi.")
note("HIVE Agents", f"Run 1331 (blok {BLOCK}): totalSupply 1263 FLAT, balanceOf(user)=1, minted-by-user. DIAM.")
note("Bubblebruin", f"Run 1331 (blok {BLOCK}): totalSupply 2621->2622 (+1), freeClaimed 2615->2616/7777 = 33,6%, balanceOf(user)=1, minted-by-user. DIAM.")
note("Agent Bubble", f"Run 1331 (blok {BLOCK}): freeMinted 1891/2222 = 85,1% FLAT (>70%) TAPI umur UNVERIFIED -> BUKAN strong lead. totalSupply 2036 FLAT, balanceOf(user)=0. Tetap watchlist-only.")
note("Lumenhold", f"Run 1331 (blok {BLOCK}): freeClaimed 1254/1500 = 83,6% FLAT (>70%) TAPI umur UNVERIFIED -> BUKAN strong lead. totalSupply 1259 FLAT. Tetap watchlist-only-age-unverified.")
note("Matrix Agents", f"Run 1331 (blok {BLOCK}): freeMinted 618/1000 = 61,8% FLAT (<70%), totalSupply 615 FLAT -> velocity GAGAL. Umur UNVERIFIED. Bukan strong lead/kandidat.")
note("AGCLUB", f"Run 1331 (blok {BLOCK}): freeMinted 527/888 = 59,3% FLAT (<70%), totalMinted 527 FLAT -> velocity GAGAL. Umur UNVERIFIED. Bukan strong lead/kandidat.")
note("SPARKS", f"Run 1331 (blok {BLOCK}): totalSupply 1185->1188 (+3) -> velocity GAGAL. Free% UNVERIFIED. Bukan kandidat.")
note("STOCK AGENT", f"Run 1331 (blok {BLOCK}): totalSupply 695->700 (+5) -> velocity GAGAL. Free inferred (1111-411)/1111 = 63,0% (<70%). Umur UNVERIFIED. Slot user TERBUKA (quote 0, freeMintedByWallet 0). Bukan kandidat/strong lead.")
note("AgentEcho", f"Run 1331 (blok {BLOCK}): totalSupply 380->382 (+2) -> velocity GAGAL. Bukan kandidat.")
note("Everything Is Mine (EIM)", f"Run 1331 (blok {BLOCK}): totalMinted 709->717 (+8, ratio 2,11x TAPI <20 token) -> velocity GAGAL. Free% UNVERIFIED, umur UNVERIFIED. Bukan kandidat.")
note("Mine Card", f"Run 1331 (blok {BLOCK}): totalSupply 1289->1300 (+11, ratio 2,18x TAPI <20 token) -> velocity GAGAL. Bukan kandidat. DIAM.")
note("THE WALL", f"Run 1331 (blok {BLOCK}): totalSupply 5476->5477 (+1) -> velocity GAGAL. Umur UNVERIFIED, free% UNVERIFIED, gate website GAGAL 2026-11-08. Tetap watchlist-only.")
note("PunchCard", f"Run 1331 (blok {BLOCK}): totalSupply 1338 FLAT -> velocity GAGAL. freeMinted 1316/5555 = 23,7%. Bukan kandidat. DIAM.")
note("ARKYN", f"Run 1331 (blok {BLOCK}): totalMinted 2241->2254 (+13, ratio 1,47x TAPI <20 token) -> velocity GAGAL. Bukan kandidat.")
note("AgentNOVA", f"Run 1331 (blok {BLOCK}): totalSupply 762->763 (+1) -> velocity GAGAL. Bukan kandidat.")
note("DGF CARD", f"Run 1331 (blok {BLOCK}): totalMinted 1614->1621 (+7, <20) -> velocity GAGAL. Umur tetap UNVERIFIED, free% UNVERIFIED, X/discussion UNVERIFIED; slot user TERBUKA (balanceOf 0). Tetap EARLY LEAD, tanpa promosi.")
note("CAT402", f"Run 1331 (blok {BLOCK}): freeCatsClaimed 100/100 - SOLD OUT (sudah diketahui). DIAM.")
note("DRAGON", f"Run 1331 (blok {BLOCK}): freeMinted 1000/1000 - pool gratis HABIS (sudah diketahui), balanceOf(user)=1. DIAM.")
note("Thetavox", f"Run 1331 (blok {BLOCK}, baca suplemen di luar PLAN): freeClaimed 1423->1602/1632 = 98,2% (>70%), totalSupply 1609, mintOpen 1, balanceOf(user)=0. TAPI umur UNVERIFIED + gate website FAILED (2026-11-10) -> BUKAN strong lead. Tanpa perubahan status; post Boltbook sarpawi98.ai '30 free left' konsisten (1632-1602=30).")

# ---- Vitaliq Scans: EARLY LEAD baru run ini ----
snap["contracts"]["Vitaliq Scans"] = {
    "address": "0xad0d78689d047bb9a32f5bf93438373a73da68ec",
    "name": "Vitaliq Scans",
    "symbol": "SCAN",
    "kind": "ERC721",
    "status": "early-lead-2026-11-18",
    "genesisStart": 1794960000,
    "genesisStartWib": "2026-11-18 07:00:00 WIB",
    "readingStart_1": 1794960000,
    "readingEnd_1": 1795046400,
    "readingEndWib": "2026-11-19 07:00:00 WIB",
    "currentReading": 1,
    "totalScans": 405,
    "scansInReading_1": 405,
    "mintOpen": 1,
    "isSealed_1": 0,
    "MAX_PER_READING": 10,
    "holdsAgentId_user": 1,
    "balanceOf_user": 0,
    "freePctVerified": None,
    "freePctNote": "UNVERIFIED: tidak ada free counter di kontrak (tanpa FREE_SUPPLY/FREE_CAP/freeMinted/freeClaimed); priceFor(user,1) revert; mintFree butuh puzzle answer (post klaim 55).",
    "velocityVerified": False,
    "xVerified": False,
    "websiteVerified": False,
    "firstSeenBlock": BLOCK,
    "firstSeenWib": "2026-11-18 ~13:47 WIB",
    "source": "Boltbook front page EN+ZH run 1331 (post gregrichy.ai /p/HuNwq6DI5T8j, 'Two new free Agent ID mints overnight') + verifikasi on-chain run ini",
    "baselineNote": "EARLY LEAD dilaporkan sekali run 1331. Agent-shaped PENUH: Sourcify verified 2026-11-17T19:02:52Z, ABI mintFree + holdsAgentId, registry bytes persis 0x60B926...22F, genesisStart on-chain 2026-11-18 07:00 WIB (umur ~7 jam <24 jam TERVERIFIKASI). Diskusi: post Boltbook gregrichy.ai (third-party). Website: UNVERIFIED - author tidak menemukan situs/sosial; pencarian alamat kontrak + nama proyek 0 hasil situs proyek; tokenURI(1) tanpa URL; ABI tanpa fungsi situs. X proyek: TIDAK DITEMUKAN. Free% UNVERIFIED, slot user UNVERIFIED, velocity belum terhitung (baseline pertama). TIDAK PERNAH di-preview/di-mint sebagai early lead; promosi ke strong lead hanya bila 3 kaki terpenuhi; ke kandidat hanya bila SEMUA kriteria + safety lolos.",
    "lastReadBlock": BLOCK,
    "lastReadWib": NOW,
    "runNote1331_1118": "Run 1331: EARLY LEAD BARU. Launch 07:00 WIB hari ini, Reading 1 live (405 scans, tutup 19 Nov 07:00 WIB), mintOpen 1, holdsAgentId(user)=1, balance 0. Free% UNVERIFIED, website UNVERIFIED, X proyek tidak ditemukan. Dilaporkan sekali sebagai EARLY LEAD; masuk watchlist.",
}

# ---- checked (log only, tidak masuk watchlist aktif) ----
snap["contracts"]["checked-0x02a9-1331"] = {
    "address": "0x02A9830b695229d0BcAa39d236778C257b87D85b",
    "status": "checked-age-excluded-2026-11-18",
    "note": "Run 1331 triage (Boltbook EN/ZH baru, post gregrichy.ai: Urbanova Plots PLOT): Sourcify verified 2026-11-16T04:31:22Z, 51 fns, mintFree + holdsAgentId + registry bytes persis, genesisOpen 1, currentDistrict 3, totalPlots 926 (515+248+163), district 3: 18 Nov 07:00 -> 19 Nov 07:00 WIB, holdsAgentId(user)=1. TAPI genesisStart on-chain 1794803233 = 2026-11-16 11:27:13 WIB -> umur ~50 jam >= 24 jam -> AGE-EXCLUDED. District 3 adalah jendela lanjutan dari launch yang sama (bukan kontrak/fase baru), jadi tidak me-reset umur. priceFor(user,1) revert (slot gratis tidak terverifikasi via view itu). Log only.",
    "lastReadBlock": BLOCK, "lastReadWib": NOW}
snap["contracts"]["checked-0x83d3-1331"] = {
    "address": "0x83d30e4bb1793d85ac315ed8792d6c1ef1572715",
    "status": "checked-not-agent-shaped-2026-11-18",
    "note": "Run 1331 triage (Boltbook EN/ZH baru, post dieuxuan50.ai: Zora Agent 9.901/10.001 free 99,0% recheck 13:27): Sourcify UNVERIFIED (ABI kosong; post sendiri menyatakan UNVERIFIED), registry bytes True, codelen 6.800 byte. On-chain (chunked <=5): totalSupply=totalMinted=9901, MAX_SUPPLY 10000, price 0,001 BNB, balanceOf(user)=0, mintedBy(user)=0; SEMUA free view revert/tidak ada -> free% UNVERIFIED. Template sama dengan Orin 0xf92e (codelen identik). Bukan agent-shaped terverifikasi (tanpa ABI). Log only.",
    "lastReadBlock": BLOCK, "lastReadWib": NOW}
snap["contracts"]["checked-0xa255-1331"] = {
    "address": "0xa2556377118dD333F9f09600DE0bBCf54Cbc69A0",
    "status": "checked-claim-not-open-2026-11-18",
    "note": "Run 1331 triage (Boltbook EN/ZH baru, post sunpump.ai: PTAH IAO claim review, claimAirdrop): Sourcify ABI kosong (n_fns 0), registry bytes False. On-chain (chunked <=5): claimed(user)=0, isOpen=0, startTime 1793421840 = 2026-10-31 11:44 WIB. Klaim TIDAK TERBUKA + umur 18 hari -> bukan kandidat/track-B. Log only.",
    "lastReadBlock": BLOCK, "lastReadWib": NOW}
snap["contracts"]["checked-0xf92e-1331"] = {
    "address": "0xf92e693f43428d5cd1a85acb2cd8e242a717e964",
    "status": "checked-not-agent-shaped-2026-11-18",
    "note": "Run 1331 triage (Boltbook EN/ZH baru, post cskh.ai: Orin Agent ORINAGENT 9.901/10.000, 99 free left, blok 134.263.892): Sourcify ABI kosong (n_fns 0), registry bytes True, codelen 6.800 byte (identik Zora 0x83d3 - template sama). On-chain (chunked <=5): totalSupply=totalMinted=9901, MAX_SUPPLY 10000, price 0,001 BNB, balanceOf(user)=0, mintedBy(user)=0; SEMUA free view revert/tidak ada -> free% UNVERIFIED. Bukan agent-shaped terverifikasi (tanpa ABI). Log only.",
    "lastReadBlock": BLOCK, "lastReadWib": NOW}
snap["contracts"]["checked-0x7dF7-1331"] = {
    "address": "0x7dF7fD03bD5b7a024B1341849AaD14758f12a4A8",
    "status": "checked-agent-shaped-low-free-pct-2026-11-18",
    "note": "Run 1331 triage (Sourcify feed baru, verifiedAt 2026-11-18T06:16:31Z / 13:16 WIB): proyek egg/hatch (ABI: claimFree, freeInfo, hatch, openEgg, eggOf, speciesCounts; tanpa mint fn, tanpa quote fn) - agent-shaped (registry bytes persis + freeClaimed + FREE_CAP), TAPI freeClaimed 138/3000 = 4,6% (freeRemaining 2849, totalMinted 137, PRICE 0,0025 BNB, paused 0, freeUsedByWallet(user)=0). Umur UNVERIFIED (verifiedAt BUKAN launch time), timing first-mint UNVERIFIED -> BUKAN early lead (first mints dalam run ini tidak terverifikasi). Log only, tidak masuk watchlist.",
    "lastReadBlock": BLOCK, "lastReadWib": NOW}
snap["contracts"]["checked-0xc116-1331"] = {
    "address": "0xc116b90c1Fb4e19cde4Fb93e7546841D4a54A6cB",
    "status": "checked-not-agent-shaped-2026-11-18",
    "note": "Run 1331 triage (Sourcify feed baru, verifiedAt 2026-11-18T06:25:51Z): kontrak lotere/sale (73 fns: lots, prizes, draws, idRegistry, saleStart/saleEnd, LOT_PRICE, mint) - totalSupply 0 (belum ada mint), has_mint True, registry bytes True, TAPI tanpa free view + tanpa agent fn -> bukan agent-shaped, bukan sale-shape S1/S2. Belum launch. Log only.",
    "lastReadBlock": BLOCK, "lastReadWib": NOW}

snap["contracts"].setdefault("bsccat", {})["runNote1331_1118"] = (
    f"Run 1331: freeMinted 531 FLAT (1301: 531), totalSupply mentah 5,31e26; balanceOf(user)=0. DIAM.")
snap["contracts"].setdefault("pepe", {})["runNote1331_1118"] = (
    "Run 1331: free pool HABIS 500/500, user sudah mint (hasMinted 1). DIAM.")

pc = snap["pending_claims"]["binanceai.fun"]
pc["lastReadWib"] = NOW
pc["runNote1331_1118"] = (f"Run 1331 (blok {BLOCK}): launched=0, failed=1, isRefundPhase=1, "
    "tokenClaimed(user)=0, totalShares 3110 - tetap pending/refund, sudah dilaporkan sekali (2026-11-02). DIAM.")
rf = snap["track_c"]["RigForge"]
rf["lastReadBlock"] = BLOCK
rf["runNote1331_1118"] = (f"Run 1331 (blok {BLOCK}): openedAt 0, freeSharesLeft 621 (1301: 621, flat), "
    "freeClaimed 379 (1301: 379, flat) - pool BELUM dibuka, tanpa perubahan status. DIAM.")

snap["runNote1331_1118"] = (
    "Run 1331 (blok re-read %d, interval ~36,3 mnt vs 1301): 1 EARLY LEAD BARU (Vitaliq Scans 0xad0d78689d047bb9a32f5bf93438373a73da68ec); 0 kandidat baru, 0 strong lead baru, 0 track-B dibuka, 0 track-C lead. "
    "Velocity: tidak ada yang lolos (terbanyak ARKYN +13 ratio 1,47x TAPI <20 token; Mine Card +11 ratio 2,18x TAPI <20; EIM +8 ratio 2,11x TAPI <20; STOCK +5; SPARKS +3; MORFO +3; THE WALL +1). "
    "AgentBubble 85,1%% + Lumenhold 83,6%% di atas 70%% TAPI umur UNVERIFIED -> BUKAN strong lead. Thetavox freeClaimed 1602/1632 = 98,2%% (baca suplemen) TAPI umur UNVERIFIED + gate website FAILED -> BUKAN strong lead. STOCK free inferred 63,0%% (<70%%); Matrix 61,8%%; AGCLUB 59,3%%; PunchCard 23,7%%. "
    "PUNNY 0xaFAE0Bf373ad87E88555afe1605111F66C99062C: totalMinted 293->304 (+11), freeMinted 304/999 = 30,4%%, mintStart on-chain 2026-11-17 20:32:03 WIB (umur ~17 jam, tutup 20:32 WIB hari ini), slot user TERBUKA, gate website tetap UNVERIFIED -> tetap EARLY LEAD, tanpa promosi. "
    "DGF CARD 0x01f9CA4ff95d49594cC8B6591022186dc5C1Bc72: totalMinted 1614->1621 (+7) -> velocity GAGAL; umur/free%%/X tetap UNVERIFIED; slot user TERBUKA. Tetap EARLY LEAD, tanpa promosi. "
    "Vitaliq Scans 0xad0d78689d047bb9a32f5bf93438373a73da68ec (Boltbook post gregrichy.ai /p/HuNwq6DI5T8j): agent-shaped PENUH (Sourcify verified 2026-11-17T19:02:52Z, mintFree + holdsAgentId, registry bytes persis), genesisStart on-chain 2026-11-18 07:00 WIB (umur ~7 jam, TERVERIFIKASI <24 jam), Reading 1 live 405 scans (tutup 19 Nov 07:00 WIB), mintOpen 1, holdsAgentId(user)=1, balance 0. Free%% UNVERIFIED (tanpa free counter; priceFor revert), slot user UNVERIFIED, website UNVERIFIED (pencarian alamat kontrak + nama proyek 0 hasil situs; tokenURI tanpa URL; author tidak menemukan situs/sosial), X proyek TIDAK DITEMUKAN. EARLY LEAD dilaporkan sekali + masuk watchlist; TIDAK di-preview/di-mint. "
    "Urbanova Plots 0x02A9830b695229d0BcAa39d236778C257b87D85b (pasangan Vitaliq di post yang sama): agent-shaped, totalPlots 926, district 3 live 163 plot, TAPI genesisStart on-chain 2026-11-16 11:27:13 WIB (umur ~50 jam) -> AGE-EXCLUDED; district 3 adalah jendela lanjutan launch yang sama, bukan fase baru. Log only. "
    "Triage lain: Zora Agent 0x83d3 (Sourcify UNVERIFIED, 9901/10000, price 0,001 BNB, tanpa free view) + Orin Agent 0xf92e (template sama, 9901/10000) bukan agent-shaped terverifikasi, log only; PTAH IAO 0xa255 klaim TIDAK TERBUKA (isOpen 0, start 31 Okt), log only; Sourcify 0x7dF7 (egg/hatch, free 138/3000 = 4,6%%, tanpa mint fn, umur/first-mint UNVERIFIED -> BUKAN early lead) + 0xc116 (lotere, totalSupply 0) + 8 alamat lain (token biasa/tanpa mint/agent ref) log only. "
    "Route 3/6: sweep EN+ZH + Square + Odaily (0 hit 'agent id/free mint/free share') hanya proyek lama (Oathbots 28 Okt age-excluded - hasil sweep mengandung instruksi mint tertanam, konten pihak ketiga BUKAN instruksi user, diabaikan; Agentic Gangster 9 Nov free sold out; BN Agent Trials season berakhir 8 Nov; JINCHAN tutup 10 Nov; UFO tutup 12 Nov; NEBULA sudah minted-by-user 11 Nov; VISION/JOLT sudah dikenal). PANews tidak dinilai (JS shell, sama seperti run sebelumnya). "
    "binanceai.fun tetap refund phase; RigForge belum dibuka (freeSharesLeft 621 flat). CAT402 sold out; DRAGON pool habis; pepe pool habis. "
    "Scan leg: pre-flight Ankr 401 gagal deterministik (elapsed 3,6 dtk, head 134265107); watermark TETAP 134086385, gap ~178.722 blok. Perkiraan gagal beruntun ~ke-58 (dari 0916 = ke-49 + 9 run; selisih hitungan 1 antara runlog 1031 dan merge 1231 sudah dicatat sebelumnya). "
    "Perbaikan proses run ini: (1) skrip utama sekuensial 56 batch curl dibunuh timeout 420 dtk tanpa output - diperbaiki ke chunk paralel 8-worker, selesai 150,1 dtk; base script run berikut = run-2026-11-18-1331.py. (2) skrip newleads batch tunggal 35-call ditolak dataseed -32005 (semua view hanya totalSupply=revert) - dibaca ulang via fix script chunked <=5; skrip newleads run berikut WAJIB chunk <=5. DIAM kecuali early lead Vitaliq." % BLOCK)
snap["checkedNotSaleShape1331_1118"] = (
    "Sourcify feed top BARU vs 1301 (verifiedAt 2026-11-18T06:34:45Z, top 0x709DA2371cc7a3aA5c6db0AcE50134D46F424A6f): "
    "0x709D/0x83f0/0x4De2 -> token ERC-20 biasa (tanpa mint/agent ref), bukan sale-shape; 0x7355/0x5E4B/0x6335/0x4F00 -> tanpa mint/free view/agent ref, bukan sale-shape; 0xD69E -> 0 fns (proxy/minimal); "
    "0x7dF7 -> egg/hatch agent-shaped (claimFree + freeClaimed 138/3000 = 4,6%, FREE_CAP 3000) TAPI tanpa mint fn + tanpa quote -> S1/S2 False, bukan sale-shape; "
    "0xc116 -> kontrak lotere/sale (lots/prizes/draws, totalSupply 0) tanpa free view/agent fn -> bukan sale-shape. (Lihat entri checked-*-1331.)")
snap["last_run_wib"] = NOW
snap["last_run_note"] = ("Run 1331: 1 EARLY LEAD BARU Vitaliq Scans (launch 07:00 WIB hari ini, 405 scans, umur terverifikasi <24 jam; free% + website UNVERIFIED, tidak di-preview/di-mint); "
    "0 kandidat/strong lead/track-B dibuka/track-C lead; Urbanova age-excluded (launch 16 Nov); "
    "PUNNY 30,4% (umur ~17 jam, tutup 20:32 WIB) + DGF CARD (+7) tetap early lead; "
    "velocity tidak ada yang lolos; scan leg FAST-FAIL Ankr 401; re-read 280 calls blok 134265337, 0 chunk error; "
    "perbaikan: re-read paralel 8-worker (150,1 dtk) + newleads chunked <=5.")
json.dump(snap, open(f"{HF}/onchain-snapshot.json", "w"), indent=1)
print("merge OK, block", BLOCK)

st = json.load(open(f"{HF}/onchain-scan-state.json"))
st["note_1331_scan"] = ("Run 2026-11-18 13:31 WIB: driver TIDAK diluncurkan - pre-flight ankr_getLogs gagal deterministik HTTP 401 Unauthorized (elapsed 3,6 dtk, head 134265107); "
    "401 auth-wide, gagal beruntun ~ke-58 (dari 0916 = ke-49 + 9 run; selisih hitungan 1 antara runlog 1031 dan merge 1231 sudah dicatat). Watermark TETAP 134086385; gap ~178.722 blok dan terus membesar (~8.000 blok/jam). Triase + 5c dilewati (tidak ada output scan).")
json.dump(st, open(f"{HF}/onchain-scan-state.json", "w"), indent=1)
print("scan-state note OK")
