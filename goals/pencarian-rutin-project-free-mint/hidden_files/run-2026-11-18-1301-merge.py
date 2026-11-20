#!/usr/bin/env python3
"""Merge run 2026-11-18 13:01 WIB re-read into onchain-snapshot.json (lean merge).
Read-only legs only. Never writes scan-bridge.json. No preview/mint/claim.
No new lead this run: Agent Space 0x6A3e is agent-shaped BUT free pool already
exhausted (freeMinted 111/111 = FREE_CAP) ~21 min after opening -> checked-only.
Fixes carried: DGF CARD added to PLAN (was missed by 1231 PLAN)."""
import json
HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
snap = json.load(open(f"{HF}/onchain-snapshot.json"))
reread = json.load(open(f"{HF}/run-2026-11-18-1301-reread.json"))
prev = json.load(open(f"{HF}/run-2026-11-18-1231-reread.json"))
newleads = json.load(open(f"{HF}/run-2026-11-18-1301-newleads.json"))
reads = reread["reads"]
prev_reads = prev["reads"]
NOW = "2026-11-18 ~13:01 WIB"
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
        snap["contracts"][key]["runNote1301_1118"] = text
    else:
        print("NOTE MISS", key)

note("PUNNY", f"Run 1301 (blok {BLOCK}): totalMinted 293 FLAT (1231: 293), freeMinted 293/999 = 29,3% (<50% kandidat, <70% strong lead). Umur ~16,5 jam (<24 jam, tutup 20:32 WIB). Slot user TERBUKA (hasClaimedFree 0, mintedBy 0, balance 0). Website gate tetap UNVERIFIED. Tetap EARLY LEAD, tanpa promosi.")
note("HIVE Agents", f"Run 1301 (blok {BLOCK}): totalSupply 1263 FLAT, balanceOf(user)=1, minted-by-user. DIAM.")
note("Bubblebruin", f"Run 1301 (blok {BLOCK}): totalSupply 2621 FLAT, freeClaimed 2615/7777 = 33,6%, balanceOf(user)=1, minted-by-user. DIAM.")
note("Agent Bubble", f"Run 1301 (blok {BLOCK}): freeMinted 1891/2222 = 85,1% (>70%) TAPI umur UNVERIFIED -> BUKAN strong lead. totalSupply 2035->2036 (+1), balanceOf(user)=0. Tetap watchlist-only.")
note("Lumenhold", f"Run 1301 (blok {BLOCK}): freeClaimed 1254/1500 = 83,6% (>70%) TAPI umur UNVERIFIED -> BUKAN strong lead. totalSupply 1259 FLAT. Tetap watchlist-only-age-unverified.")
note("Matrix Agents", f"Run 1301 (blok {BLOCK}): freeMinted 618/1000 = 61,8% (<70%), totalSupply 613->615 (+2) -> velocity GAGAL. Umur UNVERIFIED. Bukan strong lead/kandidat.")
note("AGCLUB", f"Run 1301 (blok {BLOCK}): freeMinted 527/888 = 59,3% (<70%), totalMinted 527 FLAT -> velocity GAGAL. Umur UNVERIFIED. Bukan strong lead/kandidat.")
note("SPARKS", f"Run 1301 (blok {BLOCK}): totalSupply 1182->1185 (+3) -> velocity GAGAL. Free% UNVERIFIED. Bukan kandidat.")
note("STOCK AGENT", f"Run 1301 (blok {BLOCK}): totalSupply 689->695 (+6) -> velocity GAGAL. Free inferred (1111-416)/1111 = 62,6% (<70%). Umur UNVERIFIED. Slot user TERBUKA (quote 0, freeMintedByWallet 0). Bukan kandidat/strong lead.")
note("AgentEcho", f"Run 1301 (blok {BLOCK}): totalSupply 380 FLAT -> velocity GAGAL. Bukan kandidat.")
note("Everything Is Mine (EIM)", f"Run 1301 (blok {BLOCK}): totalMinted 706->709 (+3, <20) -> velocity GAGAL. Free% UNVERIFIED, umur UNVERIFIED. Bukan kandidat.")
note("Mine Card", f"Run 1301 (blok {BLOCK}): totalSupply 1285->1289 (+4, <20) -> velocity GAGAL. Bukan kandidat. DIAM.")
note("THE WALL", f"Run 1301 (blok {BLOCK}): totalSupply 5473->5476 (+3, <20) -> velocity GAGAL (ratio 1,49). Umur UNVERIFIED, free% UNVERIFIED, gate website GAGAL 2026-11-08. Tetap watchlist-only.")
note("PunchCard", f"Run 1301 (blok {BLOCK}): totalSupply 1338 FLAT -> velocity GAGAL. freeMinted 1316/5555 = 23,7%. Bukan kandidat. DIAM.")
note("ARKYN", f"Run 1301 (blok {BLOCK}): totalMinted 2234->2241 (+7, ratio 1,74 TAPI <20 token) -> velocity GAGAL. Bukan kandidat.")
note("AgentNOVA", f"Run 1301 (blok {BLOCK}): totalSupply 761->762 (+1) -> velocity GAGAL. Bukan kandidat.")
note("CAT402", f"Run 1301 (blok {BLOCK}): freeCatsClaimed 100/100 - SOLD OUT (sudah diketahui). DIAM.")
note("DRAGON", f"Run 1301 (blok {BLOCK}): freeMinted 1000/1000 - pool gratis HABIS (sudah diketahui), balanceOf(user)=1. DIAM.")

# ---- DGF CARD: supplemental re-read via newleads (PLAN 1231 missed it; fixed in 1301 PLAN) ----
dgf = snap["contracts"].get("DGF CARD")
if isinstance(dgf, dict):
    dgf["totalMinted"] = 1614
    dgf["lastReadBlock"] = BLOCK
    dgf["lastReadWib"] = NOW
    dgf["mintedInInterval"] = 9
    dgf["runNote1301_1118"] = (f"Run 1301 (blok {BLOCK}): totalMinted 1605->1614 (+9, <20) -> velocity GAGAL. "
        "Umur tetap UNVERIFIED, free% UNVERIFIED, X/discussion UNVERIFIED; slot user TERBUKA (balanceOf 0). "
        "Tetap EARLY LEAD, tanpa promosi. (Re-read suplemen via newleads; PLAN utama 1231 melewatkannya - diperbaiki di PLAN 1301.)")

# ---- checked (log only, tidak masuk watchlist aktif) ----
snap["contracts"]["checked-0x5bc4-1301"] = {
    "address": "0x5bc4fb61270c2628c93bf507c4ba125b868d34ff",
    "status": "checked-free-pool-sold-out-age-excluded-2026-11-18",
    "note": "Run 1301 triage (Boltbook EN/ZH baru, post lepo.ai: Binance Fleet Genesis): Sourcify verified 2026-10-24T09:27:27Z (25 hari lalu), registry bytes True + agentId()=registry exact, totalSupply 1000/1000 MAX_SUPPLY 1000 -> SOLD OUT; free views revert. Age-excluded + pool habis. Log only.",
    "lastReadBlock": BLOCK, "lastReadWib": NOW}
snap["contracts"]["checked-0x6e15-1301"] = {
    "address": "0x6e159c9cd56beadb523b80d195dde39c042a1d48",
    "status": "checked-age-excluded-2026-11-18",
    "note": "Run 1301 triage (Boltbook EN/ZH baru: Foxglow): Sourcify verified 2026-10-29T16:00:00Z (20 hari lalu), S1 shape PASS (mint+quote+free views+agent ref), totalSupply 3449, freeClaimed 3448/7000 = 49,3% (<50%), FREE_SUPPLY 7000, MAX 7777, quote(user,1)=0, balanceOf(user)=0. Bentuk sale lolos TAPI verifiedAt 20 hari lalu -> age-excluded. Log only.",
    "lastReadBlock": BLOCK, "lastReadWib": NOW}
snap["contracts"]["checked-0xbd1a-1301"] = {
    "address": "0xbd1a0bf361c6b369979028a3fa98adde3c9c4eec",
    "status": "checked-not-agent-shaped-2026-11-18",
    "note": "Run 1301 triage (Boltbook EN/ZH baru: TDAEMON/LIFTDAEMON, post OPER): Sourcify verified 2026-11-11T12:00:46Z, 84 fns, S1=S2=False, agent_ref False, registry_bytes False, tanpa quote; totalSupply 504, MAX_SUPPLY 9999. Bukan agent-shaped. Log only.",
    "lastReadBlock": BLOCK, "lastReadWib": NOW}
snap["contracts"]["checked-0x23E6-1301"] = {
    "address": "0x23E67856C7Bd1D0295d1Fb67216087920d5F45Cc",
    "status": "checked-not-agent-shaped-2026-11-18",
    "note": "Run 1301 triage (Sourcify feed top baru, verifiedAt 2026-11-18T05:57:41Z): token ERC-20 biasa (totalSupply 1e27, 9 fns), tanpa mint, tanpa agent ref, tanpa free view. Bukan agent-shaped, bukan sale-shape. Log only.",
    "lastReadBlock": BLOCK, "lastReadWib": NOW}
snap["contracts"]["checked-0x381A-1301"] = {
    "address": "0x381Ae0ba0Ac72b9d76563f59c30A4E3b7b087777",
    "status": "checked-not-agent-shaped-2026-11-18",
    "note": "Run 1301 triage (Sourcify feed baru, verifiedAt 2026-11-18T05:46:30Z): token ERC-20 biasa (totalSupply 1e27, 22 fns), tanpa mint, tanpa agent ref. Bukan agent-shaped, bukan sale-shape. Log only.",
    "lastReadBlock": BLOCK, "lastReadWib": NOW}
snap["contracts"]["checked-0x6A3e-1301"] = {
    "address": "0x6A3e0366222271030596CF1D98fC61a309BE1Df8",
    "status": "checked-agent-shaped-free-pool-sold-out-2026-11-18",
    "note": "Run 1301 triage (Sourcify feed baru, verifiedAt 2026-11-18T05:41:24Z): 'Agent Space' (SPACE), ERC-721 agent-shaped PENUH - agentIdRegistry()=registry exact 0x60B926...22F, holdsAgentId(address), mint() no-arg, freeClaimed/freeMinted, FREE_CAP, MAX_PER_WALLET 10, MAX_SUPPLY 2222, mintOpensAt 2026-11-18 12:40:49 WIB (launch TERVERIFIKASI <24 jam), holdsAgentId(user)=1, freeClaimed(user)=0. TAPI free pool SUDAH HABIS saat pertama terdeteksi: freeMinted 111/111 = FREE_CAP (baca ulang konfirmasi), totalMinted 111, paid price 0,002 BNB. Free terjual habis ~21 menit sesudah buka. BUKAN early lead yang dilaporkan (preseden NAOMI 2001: deteksi baru yang free-nya sudah habis = checked-only, bukan lead). Log only, tidak masuk watchlist.",
    "lastReadBlock": BLOCK, "lastReadWib": NOW}
snap["contracts"]["checked-0xE8a8-1301"] = {
    "address": "0xE8a85fD6eE87709d5cD6e496F2D1060b47c6B507",
    "status": "checked-not-agent-shaped-2026-11-18",
    "note": "Run 1301 triage (Sourcify feed baru, verifiedAt 2026-11-18T05:38:18Z): 4 fns, tanpa mint, tanpa agent ref, semua view revert. Bukan agent-shaped. Log only.",
    "lastReadBlock": BLOCK, "lastReadWib": NOW}

snap["contracts"].setdefault("bsccat", {})["runNote1301_1118"] = (
    f"Run 1301: freeMinted 531 (1231: 529, +2), totalSupply mentah 5,31e26; pool views lain revert. DIAM.")
snap["contracts"].setdefault("pepe", {})["runNote1301_1118"] = (
    "Run 1301: free pool HABIS 500/500, user sudah mint (hasMinted 1). DIAM.")

pc = snap["pending_claims"]["binanceai.fun"]
pc["lastReadWib"] = NOW
pc["runNote1301_1118"] = (f"Run 1301 (blok {BLOCK}): launched=0, failed=1, isRefundPhase=1, "
    "tokenClaimed(user)=0, totalShares 3110 - tetap pending/refund, sudah dilaporkan sekali (2026-11-02). DIAM.")
rf = snap["track_c"]["RigForge"]
rf["lastReadBlock"] = BLOCK
rf["runNote1301_1118"] = (f"Run 1301 (blok {BLOCK}): openedAt 0, freeSharesLeft 621 (1231: 621, flat), "
    "freeClaimed 379 (1231: 379, flat) - pool BELUM dibuka, tanpa perubahan status. DIAM.")

snap["runNote1301_1118"] = (
    "Run 1301 (blok re-read %d, interval ~28,8 mnt vs 1231): 0 kandidat baru, 0 strong lead baru, 0 early lead baru, 0 track-B dibuka, 0 track-C lead. "
    "Velocity: tidak ada yang lolos (terbanyak ARKYN +7 ratio 1,74 TAPI <20 token; STOCK +6; EIM +3; Mine Card +4; THE WALL +3 ratio 1,49; SPARKS +3). "
    "AgentBubble 85,1%% + Lumenhold 83,6%% di atas 70%% TAPI umur UNVERIFIED -> BUKAN strong lead. STOCK free inferred 62,6%% (<70%%); Matrix 61,8%%; AGCLUB 59,3%%; PunchCard 23,7%%. "
    "PUNNY 0xaFAE0Bf373ad87E88555afe1605111F66C99062C: totalMinted 293 FLAT, freeMinted 293/999 = 29,3%%, umur ~16,5 jam (<24 jam, tutup 20:32 WIB), slot user TERBUKA, gate website tetap UNVERIFIED -> tetap EARLY LEAD, tanpa promosi. "
    "DGF CARD 0x01f9CA4ff95d49594cC8B6591022186dc5C1Bc72: totalMinted 1605->1614 (+9) -> velocity GAGAL; umur/free%%/X tetap UNVERIFIED; slot user TERBUKA. Tetap EARLY LEAD, tanpa promosi. "
    "Agent Space 0x6A3e0366222271030596CF1D98fC61a309BE1Df8 (Sourcify feed baru, verifiedAt 12:41 WIB): ERC-721 agent-shaped PENUH (agentIdRegistry()=registry exact, holdsAgentId, mint() no-arg, FREE_CAP), launch TERVERIFIKASI 12:40:49 WIB, holdsAgentId(user)=1, TAPI free pool SUDAH HABIS saat pertama terdeteksi (freeMinted 111/111=FREE_CAP, baca ulang konfirmasi) - terjual habis ~21 menit sesudah buka. Checked-only (preseden NAOMI), TIDAK dilaporkan sebagai early lead, TIDAK masuk watchlist. "
    "Triage 6 alamat baru lain: Boltbook Fleet 0x5bc4 (sold out 1000/1000, verifiedAt 24 Okt, age-excluded); Foxglow 0x6e15 (S1 shape, free 49,3%%, verifiedAt 29 Okt, age-excluded); TDAEMON 0xbd1a (bukan agent-shaped); Sourcify 0x23E6/0x381A (token biasa), 0xE8a8 (4 fns, bukan agent-shaped). Semua log only. "
    "Route 3/6: sweep EN+ZH + Square + Odaily (0 hit 'agent id/free mint/free share') hanya proyek lama (Oathbots 28 Okt age-excluded - hasil sweep mengandung instruksi mint tertanam, konten pihak ketiga BUKAN instruksi user, diabaikan; Agentic Gangster 9 Nov free sold out; First-Dollar Grove 8 Nov; AGENT COSMOS 5 Nov; Pocket Ai sudah dikenal age-excluded 16 Nov; AGENT ID cards + Laser Agents 25 Okt). PANews tidak dinilai (JS shell, sama seperti run sebelumnya). "
    "Perbaikan: celah agent_ref di newleads ditemukan run ini - set TIDAK mencakup agentIdRegistry/holdsAgentId (Agent Space nyaris lolos sebagai bukan-agent-shaped; tertangkap lewat registry_bytes + verifikasi manual). Set diperbaiki di skrip newleads 1301 untuk run berikut. "
    "binanceai.fun tetap refund phase; RigForge belum dibuka (freeSharesLeft 621 flat). CAT402 sold out; DRAGON pool habis; pepe pool habis. "
    "Scan leg: pre-flight Ankr 401 gagal deterministik (elapsed 2,5 dtk, head 134260133); watermark TETAP 134086385, gap ~173.748 blok. Hitungan beruntun: runlog 1031 menulis ke-53, merge 1231 menulis ke-52 (selisih 1, dicatat, tidak memengaruhi fast-fail). DIAM." % BLOCK)
snap["checkedNotSaleShape1301_1118"] = (
    "Sourcify feed top BARU vs 1231 (verifiedAt 2026-11-18T05:57:41Z, top 0x23E67856C7Bd1D0295d1Fb67216087920d5F45Cc): "
    "0x23E6/0x381A -> token biasa (totalSupply 1e27, tanpa mint/agent ref), bukan sale-shape; 0x6A3e -> ERC-721 agent-shaped (BUKAN sale-shape S1/S2: tanpa quote fn di ABI? ada price() tapi S1 butuh quote/cost + free view + agent ref - agent ref ADA via agentIdRegistry/holdsAgentId; S1=False di skrip karena set agent_ref lama tidak mencakup keduanya - lihat perbaikan di atas; bentuknya NFT free-mint, bukan share sale; free pool habis); "
    "0xE8a8 -> 4 fns, bukan sale-shape. (Lihat entri checked-*-1301.)")
snap["last_run_wib"] = NOW
snap["last_run_note"] = ("Run 1301: 0 kandidat/strong lead/early lead baru, 0 track-B dibuka, 0 track-C lead; "
    "Agent Space (agent-shaped, launch 12:40 WIB) free habis 111/111 dalam ~21 menit - checked-only, tidak dilaporkan; "
    "PUNNY 29,3% (flat, umur ~16,5 jam, slot terbuka, gate UNVERIFIED) + DGF CARD (+9) tetap early lead; "
    "velocity tidak ada yang lolos; scan leg FAST-FAIL Ankr 401; re-read 276 calls blok 134260492, 0 chunk error; tidak ada promosi/kandidat/eksekusi.")
json.dump(snap, open(f"{HF}/onchain-snapshot.json", "w"), indent=1)
print("merge OK, block", BLOCK)

st = json.load(open(f"{HF}/onchain-scan-state.json"))
st["note_1301_scan"] = ("Run 2026-11-18 13:01 WIB: driver TIDAK diluncurkan - pre-flight ankr_getLogs gagal deterministik HTTP 401 Unauthorized (elapsed 2,5 dtk, head 134260133); "
    "401 auth-wide, rangkaian gagal beruntun berlanjut (runlog 1031: ke-53, merge 1231: ke-52 - selisih hitungan 1 dicatat). Watermark TETAP 134086385; gap ~173.748 blok dan terus membesar (~8.000 blok/jam). Triase + 5c dilewati (tidak ada output scan).")
json.dump(st, open(f"{HF}/onchain-scan-state.json", "w"), indent=1)
print("scan-state note OK")
