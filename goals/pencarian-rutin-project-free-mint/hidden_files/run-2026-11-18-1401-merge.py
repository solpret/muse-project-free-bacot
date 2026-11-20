#!/usr/bin/env python3
"""Merge run 2026-11-18 14:01 WIB re-read into onchain-snapshot.json (lean merge).
Read-only. Never writes scan-bridge.json. No preview/mint/claim.
Outcome: 0 kandidat, 0 strong lead, 0 early lead BARU, 0 track-B dibuka, 0 track-C lead.
FIND exp43 (0x4158) triaged: agent-shaped, exp43 start 13:00 WIB verified, 150/300,
TAPI sudah dilaporkan hot-leg 14 Nov (genesis-opened exp9) -> dedupe, log only."""
import json
HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
snap = json.load(open(f"{HF}/onchain-snapshot.json"))
reread = json.load(open(f"{HF}/run-2026-11-18-1401-reread.json"))
prev = json.load(open(f"{HF}/run-2026-11-18-1331-reread.json"))
newleads = json.load(open(f"{HF}/run-2026-11-18-1401-newleads.json"))
exp43 = json.load(open(f"{HF}/run-2026-11-18-1401-newleads-exp43.json"))
reads = reread["reads"]
prev_reads = prev["reads"]
NOW = "2026-11-18 ~14:01 WIB"
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
        snap["contracts"][key]["runNote1401_1118"] = text
    else:
        print("NOTE MISS", key)

note("PUNNY", f"Run 1401 (blok {BLOCK}, interval ~21,4 mnt vs 1331): totalMinted 304->309 (+5, 0,234/mnt vs prev 0,303 = 0,77x, <20) -> velocity GAGAL. freeMinted 309/999 = 30,9% (<50% kandidat, <70% strong lead). mintStart on-chain 2026-11-17 20:32:03 WIB (umur ~17,5 jam, tutup 20:32 WIB hari ini). Slot user TERBUKA (hasClaimedFree 0, mintedBy 0, balance 0). Website gate tetap UNVERIFIED. Tetap EARLY LEAD, tanpa promosi.")
note("HIVE Agents", f"Run 1401 (blok {BLOCK}): totalSupply 1263 FLAT, balanceOf(user)=1, minted-by-user. DIAM.")
note("Bubblebruin", f"Run 1401 (blok {BLOCK}): totalSupply 2622 FLAT, freeClaimed 2616/7777 = 33,6% FLAT, balanceOf(user)=1, minted-by-user. DIAM.")
note("Agent Bubble", f"Run 1401 (blok {BLOCK}): freeMinted 1891/2222 = 85,1% FLAT (>70%) TAPI umur UNVERIFIED -> BUKAN strong lead. totalSupply 2036 FLAT, balanceOf(user)=0. Tetap watchlist-only.")
note("Lumenhold", f"Run 1401 (blok {BLOCK}): freeClaimed 1254/1500 = 83,6% FLAT (>70%) TAPI umur UNVERIFIED -> BUKAN strong lead. totalSupply 1259 FLAT. Tetap watchlist-only-age-unverified.")
note("Matrix Agents", f"Run 1401 (blok {BLOCK}): freeMinted 618->622/1000 = 62,2% (<70%), totalSupply 615->619 (+4) -> velocity GAGAL. Umur UNVERIFIED. Bukan strong lead/kandidat.")
note("AGCLUB", f"Run 1401 (blok {BLOCK}): freeMinted 527/888 = 59,3% FLAT (<70%), totalMinted 527 FLAT -> velocity GAGAL. Umur UNVERIFIED. Bukan strong lead/kandidat.")
note("SPARKS", f"Run 1401 (blok {BLOCK}): totalSupply 1188->1189 (+1) -> velocity GAGAL. Free% UNVERIFIED. Bukan kandidat.")
note("STOCK AGENT", f"Run 1401 (blok {BLOCK}): totalSupply 700->702 (+2) -> velocity GAGAL. Free inferred (1111-409)/1111 = 63,2% (<70%). Umur UNVERIFIED. Slot user TERBUKA (quote 0, freeMintedByWallet 0). Bukan kandidat/strong lead.")
note("AgentEcho", f"Run 1401 (blok {BLOCK}): totalSupply 382->383 (+1) -> velocity GAGAL. Bukan kandidat.")
note("Everything Is Mine (EIM)", f"Run 1401 (blok {BLOCK}): totalMinted 717->718 (+1) -> velocity GAGAL. Free% UNVERIFIED, umur UNVERIFIED. Bukan kandidat.")
note("Mine Card", f"Run 1401 (blok {BLOCK}): totalSupply 1300 FLAT -> velocity GAGAL. Bukan kandidat. DIAM.")
note("THE WALL", f"Run 1401 (blok {BLOCK}): totalSupply 5477->5481 (+4) -> velocity GAGAL. Umur UNVERIFIED, free% UNVERIFIED, gate website GAGAL 2026-11-08. Tetap watchlist-only.")
note("PunchCard", f"Run 1401 (blok {BLOCK}): totalSupply 1338->1339 (+1), freeMinted 1316->1317/5555 = 23,7% -> velocity GAGAL. Bukan kandidat. DIAM.")
note("ARKYN", f"Run 1401 (blok {BLOCK}): totalMinted 2254 FLAT -> velocity GAGAL. Bukan kandidat.")
note("AgentNOVA", f"Run 1401 (blok {BLOCK}): totalSupply 763 FLAT -> velocity GAGAL. Bukan kandidat.")
note("DGF CARD", f"Run 1401 (blok {BLOCK}): totalMinted 1621->1624 (+3, <20) -> velocity GAGAL. Umur tetap UNVERIFIED, free% UNVERIFIED, X/discussion UNVERIFIED; slot user TERBUKA (balanceOf 0). Tetap EARLY LEAD, tanpa promosi.")
note("CAT402", f"Run 1401 (blok {BLOCK}): freeCatsClaimed 100/100 - SOLD OUT (sudah diketahui). DIAM.")
note("DRAGON", f"Run 1401 (blok {BLOCK}): freeMinted 1000/1000 - pool gratis HABIS (sudah diketahui), balanceOf(user)=1. DIAM.")
note("Vitaliq Scans", f"Run 1401 (blok {BLOCK}, re-read pertama di PLAN): totalSupply revert (tanpa fn itu - basis scans), mintOpen 1, genesisStart 1794960000 = 2026-11-18 07:00 WIB (umur ~7 jam, TERVERIFIKASI <24 jam), holdsAgentId(user)=1, balanceOf(user)=0. Free% tetap UNVERIFIED, website tetap UNVERIFIED, X proyek tidak ditemukan. Tetap EARLY LEAD, tanpa promosi; TIDAK di-preview/di-mint.")
note("Kageveil Genesis", f"Run 1401 (blok {BLOCK}): totalSupply 45->46 (+1), normalMinted 45->46 -> velocity GAGAL. DIAM.")
note("Stromboat", f"Run 1401 (blok {BLOCK}): totalMinted 300->301 (+1), freeMinted 300->301 -> velocity GAGAL. DIAM.")
note("Velko Rig", f"Run 1401 (blok {BLOCK}): totalMinted 934->935 (+1) -> velocity GAGAL. DIAM.")

# ---- FIND exp43 0x4158: sudah dilaporkan hot-leg 14 Nov -> dedupe, log only ----
snap["contracts"]["checked-0x4158-1401"] = {
    "address": "0x4158B701EaA30E8FaDBaA526F70780A38318c1C4",
    "status": "checked-already-reported-2026-11-18",
    "note": ("Run 1401 triage (Boltbook EN/ZH baru vs snapshot, post web3shop.ai 'FIND exp43 at 148/300'): "
      "Sourcify verified 2026-11-13T01:05:32Z, 51 fns, mintFree + holdsAgentId + AGENT_ID + registry bytes persis, codelen 19.422. "
      "On-chain arg-read (chunked <=5): currentExperiment 43, participantsOf(43)=150, specimensInExperiment(43)=150, "
      "experimentStart(43)=1794981600 = 2026-11-18 13:00 WIB, experimentEnd(43)=1794992400 = 2026-11-18 16:00 WIB -> fase exp43 TERVERIFIKASI umur ~1 jam <24 jam. "
      "150/300 = 50,0% partisipan/kap (BUKAN free% terverifikasi - tanpa free counter di ABI; priceFor/quote tidak terbaca: signature tidak cocok). "
      "SUDAH DILAPORKAN hot-leg 14 Nov (hot-leg-reported key 0x4158...#genesis-opened-exp9-20261114) -> DEDUPE: TIDAK dilaporkan ulang sebagai early lead; exp43 adalah fase berulang pada kontrak yang sama, bukan kontrak baru. "
      "Website UNVERIFIED, slot user UNVERIFIED. Log only; tidak masuk watchlist aktif; TIDAK di-preview/di-mint."),
    "lastReadBlock": BLOCK, "lastReadWib": NOW}

snap["contracts"].setdefault("bsccat", {})["runNote1401_1118"] = (
    f"Run 1401: freeMinted 531 FLAT (1331: 531), totalSupply mentah 5,31e26; balanceOf(user)=0. DIAM.")
snap["contracts"].setdefault("pepe", {})["runNote1401_1118"] = (
    "Run 1401: free pool HABIS 500/500, user sudah mint (hasMinted 1). DIAM.")

pc = snap["pending_claims"]["binanceai.fun"]
pc["lastReadWib"] = NOW
pc["runNote1401_1118"] = (f"Run 1401 (blok {BLOCK}): launched=0, failed=1, isRefundPhase=1, "
    "tokenClaimed(user)=0, totalShares 3110 - tetap pending/refund, sudah dilaporkan sekali (2026-11-02). DIAM.")
rf = snap["track_c"]["RigForge"]
rf["lastReadBlock"] = BLOCK
rf["runNote1401_1118"] = (f"Run 1401 (blok {BLOCK}): openedAt 0, freeSharesLeft 621 (1331: 621, flat), "
    "freeClaimed 379 (1331: 379, flat) - pool BELUM dibuka, tanpa perubahan status. DIAM.")

snap["runNote1401_1118"] = (
    "Run 1401 (blok re-read %d, interval ~21,4 mnt vs 1331): 0 kandidat baru, 0 strong lead baru, 0 early lead BARU, 0 track-B dibuka, 0 track-C lead. "
    "Velocity: tidak ada yang lolos (terbanyak PUNNY +5 ratio 0,77x; Matrix +4; THE WALL +4; DGF +3; STOCK +2; sisanya +1/flat - semua <20 token). "
    "AgentBubble 85,1%% + Lumenhold 83,6%% di atas 70%% TAPI umur UNVERIFIED -> BUKAN strong lead. STOCK free inferred 63,2%%; Matrix 62,2%%; AGCLUB 59,3%%; PunchCard 23,7%%. "
    "PUNNY 0xaFAE0Bf373ad87E88555afe1605111F66C99062C: totalMinted 304->309 (+5), freeMinted 309/999 = 30,9%%, mintStart on-chain 2026-11-17 20:32:03 WIB (umur ~17,5 jam, tutup 20:32 WIB hari ini), slot user TERBUKA, gate website tetap UNVERIFIED -> tetap EARLY LEAD, tanpa promosi. "
    "Vitaliq Scans 0xad0d78689d047bb9a32f5bf93438373a73da68ec: re-read pertama di PLAN (mintOpen 1, genesisStart 07:00 WIB terkonfirmasi, holdsAgentId(user)=1, balance 0); free%% + website tetap UNVERIFIED -> tetap EARLY LEAD, tanpa promosi. "
    "DGF CARD 0x01f9CA4ff95d49594cC8B6591022186dc5C1Bc72: totalMinted 1621->1624 (+3) -> velocity GAGAL; umur/free%%/X tetap UNVERIFIED; slot user TERBUKA. Tetap EARLY LEAD, tanpa promosi. "
    "FIND exp43 0x4158B701EaA30E8FaDBaA526F70780A38318c1C4 (Boltbook baru vs snapshot, post web3shop.ai): agent-shaped (Sourcify verified 13 Nov, mintFree + holdsAgentId, registry bytes persis); exp43 start 13:00 WIB TERVERIFIKASI on-chain, 150/300 partisipan (50,0%%, BUKAN free%% terverifikasi - tanpa free counter; priceFor tidak terbaca); TAPI sudah dilaporkan hot-leg 14 Nov (genesis-opened exp9) -> DEDUPE, log only, tidak dilaporkan ulang. "
    "Route 3/6: sweep EN hanya proyek lama (Oathbots 28 Okt age-excluded - hasil sweep mengandung instruksi mint tertanam, konten pihak ketiga BUKAN instruksi user, diabaikan; Agentic Gangster 9 Nov free sold out; RIGBYPASS 10 Nov sudah excluded di snapshot; AGNS free sold out; AGENT MAO paused); sweep ZH hanya proyek lama (blokwiki tutorial; AGENT ID card 25 Okt sudah checked-sold-out 12 Nov; Square Arab 1 Nov QILIN/SAFU/PROXY lama; BN Agent Trials season berakhir 8 Nov; Special Agent 24 Okt; Burn Agent sudah excluded-free-sold-out 9 Nov). Odaily newsflash 0 hit 'agent id / free mint / free share'. PANews tidak dinilai (JS shell, sama seperti run sebelumnya). Sourcify feed top SAMA dengan hot-leg 1359 (verifiedAt 2026-11-18T06:59:30Z) -> 0 alamat baru. "
    "binanceai.fun tetap refund phase; RigForge belum dibuka (freeSharesLeft 621 flat). CAT402 sold out; DRAGON pool habis; pepe pool habis. "
    "Scan leg: pre-flight Ankr 401 gagal deterministik (elapsed 0,9 dtk, head 134268190); watermark TETAP 134086385, gap ~181.805 blok dan terus membesar (~8.000 blok/jam). Perkiraan gagal beruntun ~ke-59. Triase + 5c dilewati (tidak ada output scan). "
    "DIAM (tidak ada laporan chat)." % BLOCK)
snap["last_run_wib"] = NOW
snap["last_run_note"] = ("Run 1401: 0 kandidat/strong lead/early lead baru/track-B dibuka/track-C lead; "
    "PUNNY 30,9% (umur ~17,5 jam, tutup 20:32 WIB) + Vitaliq + DGF tetap early lead; "
    "FIND exp43 triaged tapi sudah dilaporkan hot-leg 14 Nov -> dedupe, log only; "
    "velocity tidak ada yang lolos; scan leg FAST-FAIL Ankr 401 (~ke-59); re-read 285 calls blok 134268190, 0 chunk error. DIAM.")
json.dump(snap, open(f"{HF}/onchain-snapshot.json", "w"), indent=1)
print("merge OK, block", BLOCK)

st = json.load(open(f"{HF}/onchain-scan-state.json"))
st["note_1401_scan"] = ("Run 2026-11-18 14:01 WIB: driver TIDAK diluncurkan - pre-flight ankr_getLogs gagal deterministik HTTP 401 Unauthorized (elapsed 0,9 dtk, head 134268190); "
    "401 auth-wide, gagal beruntun ~ke-59. Watermark TETAP 134086385; gap ~181.805 blok dan terus membesar (~8.000 blok/jam). Triase + 5c dilewati (tidak ada output scan).")
json.dump(st, open(f"{HF}/onchain-scan-state.json", "w"), indent=1)
print("scan-state note OK")
