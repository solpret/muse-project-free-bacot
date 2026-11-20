#!/usr/bin/env python3
"""Merge run 2026-11-18 12:31 WIB re-read into onchain-snapshot.json (lean merge).
Read-only legs only. Never writes scan-bridge.json. No preview/mint/claim.
Adds DGF CARD 0x01f9CA4f as EARLY LEAD (first-seen this run, sweep route 3).
Applies the 1201 newleads agent_ref fix (AGENT_ID_REGISTRY/hasAgentId/AGENT_ID)."""
import json
HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
snap = json.load(open(f"{HF}/onchain-snapshot.json"))
reread = json.load(open(f"{HF}/run-2026-11-18-1231-reread.json"))
prev = json.load(open(f"{HF}/run-2026-11-18-1201-reread.json"))
reads = reread["reads"]
prev_reads = prev["reads"]
NOW = "2026-11-18 ~12:31 WIB"
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
        snap["contracts"][key]["runNote1231_1118"] = text
    else:
        print("NOTE MISS", key)

# headline notes (values from 1231 re-read vs 1201)
note("PUNNY", f"Run 1231 (blok {BLOCK}): totalMinted 291->293 (+2), freeMinted 293/999 = 29,3% (<50% kandidat, <70% strong lead). Umur ~16 jam (<24 jam, tutup 20:32 WIB). Slot user TERBUKA (hasClaimedFree 0, mintedBy 0, balance 0). Website gate tetap UNVERIFIED. Tetap EARLY LEAD, tanpa promosi.")
note("HIVE Agents", f"Run 1231 (blok {BLOCK}): totalSupply 1263 FLAT, balanceOf(user)=1, minted-by-user. DIAM.")
note("Bubblebruin", f"Run 1231 (blok {BLOCK}): totalSupply 2621 FLAT, freeClaimed 2615/7777 = 33,6%, balanceOf(user)=1, minted-by-user. DIAM.")
note("Agent Bubble", f"Run 1231 (blok {BLOCK}): freeMinted 1890/2222 = 85,1% (>70%) TAPI umur UNVERIFIED -> BUKAN strong lead. totalSupply 2034->2035 (+1), balanceOf(user)=0. Tetap watchlist-only.")
note("Lumenhold", f"Run 1231 (blok {BLOCK}): freeClaimed 1254/1500 = 83,6% (>70%) TAPI umur UNVERIFIED -> BUKAN strong lead. totalSupply 1258->1259 (+1). Tetap watchlist-only-age-unverified.")
note("Matrix Agents", f"Run 1231 (blok {BLOCK}): freeMinted 616/1000 = 61,6% (<70%), totalSupply 613 FLAT -> velocity GAGAL. Umur UNVERIFIED. Bukan strong lead/kandidat.")
note("AGCLUB", f"Run 1231 (blok {BLOCK}): freeMinted 527/888 = 59,3% (<70%), totalMinted 527 FLAT -> velocity GAGAL. Umur UNVERIFIED. Bukan strong lead/kandidat.")
note("SPARKS", f"Run 1231 (blok {BLOCK}): totalSupply 1182 FLAT -> velocity GAGAL. Free% UNVERIFIED. Bukan kandidat.")
note("STOCK AGENT", f"Run 1231 (blok {BLOCK}): totalSupply 689 FLAT -> velocity GAGAL. Free inferred (1111-422)/1111 = 62,0% (<70%). Umur UNVERIFIED. Slot user TERBUKA (quote 0, freeMintedByWallet 0). Bukan kandidat/strong lead.")
note("AgentEcho", f"Run 1231 (blok {BLOCK}): totalSupply 380 FLAT -> velocity GAGAL. Bukan kandidat.")
note("Everything Is Mine (EIM)", f"Run 1231 (blok {BLOCK}): totalMinted 694->706 (+12, <20) -> velocity GAGAL. Free% UNVERIFIED, umur UNVERIFIED. Bukan kandidat.")
note("Mine Card", f"Run 1231 (blok {BLOCK}): totalSupply 1276->1285 (+9, <20) -> velocity GAGAL. Bukan kandidat. DIAM.")
note("THE WALL", f"Run 1231 (blok {BLOCK}): totalSupply 5471->5473 (+2, <20) -> velocity GAGAL. Umur UNVERIFIED, free% UNVERIFIED, gate website GAGAL 2026-11-08. Tetap watchlist-only.")
note("PunchCard", f"Run 1231 (blok {BLOCK}): totalSupply 1338 FLAT -> velocity GAGAL. freeMinted 1316/5555 = 23,7%. Bukan kandidat. DIAM.")
note("ARKYN", f"Run 1231 (blok {BLOCK}): totalSupply 2230->2234 (+4, <20) -> velocity GAGAL. Bukan kandidat.")
note("AgentNOVA", f"Run 1231 (blok {BLOCK}): totalSupply 758->761 (+3, <20) -> velocity GAGAL. Bukan kandidat.")
note("CAT402", f"Run 1231 (blok {BLOCK}): freeCatsClaimed 100/100 - SOLD OUT (sudah diketahui). DIAM.")
note("DRAGON", f"Run 1231 (blok {BLOCK}): freeMinted 1000/1000 - pool gratis HABIS (sudah diketahui), balanceOf(user)=1. DIAM.")

# ---- DGF CARD: agent-shaped, minting live, umur UNVERIFIED -> EARLY LEAD (lapor sekali) ----
snap["contracts"]["DGF CARD"] = {
    "address": "0x01f9CA4ff95d49594cC8B6591022186dc5C1Bc72",
    "name": "DGF CARD",
    "kind": "ERC721",
    "status": "early-lead-reported-2026-11-18-1231",
    "website": "https://dgnft.pages.dev/",
    "websiteVerified": True,
    "totalMinted": 1605,
    "balanceOf_user": 0,
    "agentRegistryUint": 552192074493313695968015109214105588393044541999,
    "registry_bytes": True,
    "sourcifyVerified": False,
    "xVerified": False,
    "velocityVerified": False,
    "launchNote": "Umur peluncuran UNVERIFIED. Situs tanpa tanggal peluncuran dan tanpa tautan X. Deep-dive run 1231: (1) /skill.md /launch.json /api/stats /api/verify /llms.txt semua SPA fallback tanpa data; (2) binary search blok deploy via eth_getCode gagal (pruned node 'missing trie node'); (3) eth_getLogs first-mint gagal di 4 RPC publik (-32005 limit/rate exceeded, jendela 100 blok pun ditolak); (4) BscScan V2 free tier tidak mencakup BSC (diketahui 14 Nov); (5) Ankr 401. First-mint log belum terverifikasi.",
    "baselineNote": "EARLY LEAD dilaporkan sekali run 1231 WIB 2026-11-18 (temuan sweep route 3). Agent-shaped: registry bytes di bytecode + agentRegistry() = registry exact; situs 'exclusively for Agent ID (.ai) holders', first mint FREE kuota 3.000, mint #2-5 0,0008 BNB, max 5/wallet; totalMinted 1604->1605 live (minting aktif). Kaki: website TERVERIFIKASI (situs mencetak kontrak persis + tautan BscScan); umur UNVERIFIED; free% UNVERIFIED (free view revert, tanpa counter gratis); X/discussion UNVERIFIED; slot user TERBUKA (balanceOf 0, first mint gratis per situs, quote on-chain tak terbaca). BUKAN kandidat/strong lead; TIDAK di-preview/di-mint. Bila umur terverifikasi >24 jam -> age-excluded, lapor sekali + hapus; bila umur <24 jam + free% >70% + slot terbuka -> strong lead.",
    "firstSeenBlock": BLOCK,
    "firstSeenWib": "2026-11-18 ~12:31 WIB (sweep route 3)",
    "lastReadBlock": BLOCK,
    "lastReadWib": NOW,
    "supplyView": "totalMinted",
    "currentRatePerMin": None,
    "velocityLegPasses": False,
}
# ---- checked (log only, tidak masuk watchlist aktif) ----
snap["contracts"]["checked-0x0dac-1231"] = {
    "address": "0x0daca11f7676641f061d1cf25fe6e5ac9f1171e5",
    "status": "checked-not-a-contract-2026-11-18",
    "note": "Run 1231 triage (Boltbook EN/ZH baru): codelen 2 (0x, EOA/bukan kontrak), semua view None. Bukan alamat kontrak. Log only.",
    "lastReadBlock": BLOCK, "lastReadWib": NOW}
snap["contracts"]["checked-0x5082-1231"] = {
    "address": "0x50823fd4c14435b8b13e8b03f4d1cfee099687bc",
    "status": "checked-age-excluded-2026-11-18",
    "note": "Run 1231 triage (Boltbook EN/ZH baru): agent-shaped (agentRegistry() exact + mint + MAX_SUPPLY 3333, totalMinted 176, mintOpen 1) TAPI verifiedAt Sourcify 2026-11-10T02:29:54Z (8 hari lalu, umur >=24 jam), free views revert, tanpa quote. Age-excluded, BUKAN lead/kandidat. Log only.",
    "lastReadBlock": BLOCK, "lastReadWib": NOW}
snap["contracts"]["checked-0xa14f-1231"] = {
    "address": "0xa14ffdb8f9ffb5cd7003c969db0da6eee025292c",
    "status": "checked-not-agent-shaped-2026-11-18",
    "note": "Run 1231 triage (Sourcify feed top baru, verifiedAt 2026-11-18T05:35:55Z): token ERC-20 biasa (totalSupply 21000e18, 12 fns), tanpa mint, tanpa agent ref, tanpa free view. Bukan agent-shaped, bukan sale-shape. Log only.",
    "lastReadBlock": BLOCK, "lastReadWib": NOW}
snap["contracts"]["checked-0x88ab-1231"] = {
    "address": "0x88ab1d80a3899b5323ac6c7ea6a605582638ff45",
    "status": "checked-not-agent-shaped-2026-11-18",
    "note": "Run 1231 triage (Sourcify feed baru, verifiedAt 2026-11-18T05:34:43Z): 17 fns, tanpa mint, tanpa agent ref, semua view revert. Bukan agent-shaped. Log only.",
    "lastReadBlock": BLOCK, "lastReadWib": NOW}
snap["contracts"]["checked-0xae26-1231"] = {
    "address": "0xae267022c580a394cb81a6e572d68482be9484ae",
    "status": "checked-not-agent-shaped-2026-11-18",
    "note": "Run 1231 triage (Sourcify feed baru, verifiedAt 2026-11-18T05:32:29Z): 2 fns, codelen 914. Bukan agent-shaped. Log only.",
    "lastReadBlock": BLOCK, "lastReadWib": NOW}
snap["contracts"]["checked-0xf449-1231"] = {
    "address": "0xf449d172c66b2fe8387ddda50546c468f6a019cd",
    "status": "checked-not-agent-shaped-2026-11-18",
    "note": "Run 1231 triage (Sourcify feed baru, verifiedAt 2026-11-18T05:32:27Z): 2 fns, codelen 914. Bukan agent-shaped. Log only.",
    "lastReadBlock": BLOCK, "lastReadWib": NOW}
snap["contracts"]["checked-0x4ba4-1231"] = {
    "address": "0x4ba4a4a76349cd860b9d3f641b2b4f3da37e2b37",
    "status": "checked-not-agent-shaped-2026-11-18",
    "note": "Run 1231 triage (Sourcify feed baru, verifiedAt 2026-11-18T05:22:32Z): token ERC-20 biasa (totalSupply 5.000.000e18, 18 fns), tanpa mint, tanpa agent ref. Bukan agent-shaped, bukan sale-shape. Log only.",
    "lastReadBlock": BLOCK, "lastReadWib": NOW}
snap["contracts"]["checked-0x8b51-1231"] = {
    "address": "0x8b5128b4e01328d3e17c0bf0b5e0ed5006327777",
    "status": "checked-not-agent-shaped-2026-11-18",
    "note": "Run 1231 triage (Sourcify feed baru, verifiedAt 2026-11-18T05:21:40Z): token ERC-20 biasa (totalSupply 1e27, 22 fns), tanpa mint, tanpa agent ref. Bukan agent-shaped, bukan sale-shape. Log only.",
    "lastReadBlock": BLOCK, "lastReadWib": NOW}

snap["contracts"].setdefault("bsccat", {})["runNote1231_1118"] = (
    f"Run 1231: freeMinted 529 (1201: 526, +3), totalSupply mentah 5,29e26; pool views lain revert. DIAM.")
snap["contracts"].setdefault("pepe", {})["runNote1231_1118"] = (
    "Run 1231: free pool HABIS 500/500, user sudah mint (hasMinted 1). DIAM.")

pc = snap["pending_claims"]["binanceai.fun"]
pc["lastReadWib"] = NOW
pc["runNote1231_1118"] = (f"Run 1231 (blok {BLOCK}): launched=0, failed=1, isRefundPhase=1, "
    "tokenClaimed(user)=0, totalShares 3110 - tetap pending/refund, sudah dilaporkan sekali (2026-11-02). DIAM.")
rf = snap["track_c"]["RigForge"]
rf["lastReadBlock"] = BLOCK
rf["runNote1231_1118"] = (f"Run 1231 (blok {BLOCK}): openedAt 0, freeSharesLeft 621 (1201: 621, flat), "
    "freeClaimed 379 (1201: 379, flat) - pool BELUM dibuka, tanpa perubahan status. DIAM.")

snap["runNote1231_1118"] = (
    "Run 1231 (blok re-read %d, interval ~28,6 mnt vs 1201): 0 kandidat baru, 0 strong lead baru, 1 early lead baru (DGF CARD), 0 track-B dibuka, 0 track-C lead. "
    "Velocity: tidak ada yang lolos (terbanyak EIM +12, Mine Card +9, ARKYN +4, AgentNOVA +3 - semua <20 token). "
    "AgentBubble 85,1%% + Lumenhold 83,6%% di atas 70%% TAPI umur UNVERIFIED -> BUKAN strong lead. STOCK free inferred 62,0%% (<70%%); Matrix 61,6%%; AGCLUB 59,3%%; PunchCard 23,7%%. "
    "PUNNY 0xaFAE0Bf373ad87E88555afe1605111F66C99062C: freeMinted 293/999 = 29,3%% (+2 sejak 1201), umur ~16 jam (<24 jam, tutup 20:32 WIB), slot user TERBUKA, gate website tetap UNVERIFIED -> tetap EARLY LEAD, tanpa promosi. "
    "DGF CARD 0x01f9CA4ff95d49594cC8B6591022186dc5C1Bc72 (dgnft.pages.dev, temuan sweep route 3): agent-shaped (registry bytes + agentRegistry exact), totalMinted 1604->1605 live, website TERVERIFIKASI (situs mencetak kontrak persis); umur UNVERIFIED (deep-dive: tanpa tanggal di situs, /skill.md dkk SPA fallback, eth_getCode binary search gagal pruned node, eth_getLogs ditolak 4 RPC publik -32005, BscScan free tidak mencakup BSC, Ankr 401); free%% UNVERIFIED (free view revert); X/discussion UNVERIFIED; slot user TERBUKA (balanceOf 0). EARLY LEAD dilaporkan sekali, BUKAN kandidat/strong lead, TIDAK di-preview/di-mint. "
    "Triage 8 alamat baru lain: Boltbook 0x0daca11f (EOA, bukan kontrak); 0x50823fd4 (agent-shaped TAPI verifiedAt 2026-11-10, age-excluded); Sourcify top 0xa14ffdb8/0x88ab1d80/0xae267022/0xf449d172/0x4ba4a4a7/0x8b5128b4 (token biasa/tanpa mint/tanpa agent ref -> bukan agent-shaped, bukan sale-shape). Semua log only. "
    "Route 3/6: sweep EN+ZH + Square + Odaily/PANews hanya proyek lama (Agentic Gangster 9 Nov, RIGBYPASS 10 Nov, Agent Pioneers 11 Nov, ONLYAI Crystals 6 Nov, Anubis/Osiris 2 Nov, UFO/NEBULA/YAMA/NOVRA/ORBITA 7-10 Nov) - semua umur >24 jam; DRIFTWIRE/Agent Island/BAHUANG3 tak terverifikasi sebagai peluncuran baru. DappBay tidak dipakai (tidak ada proyek baru yang butuh gate-check selain DGF, yang websitenya sudah terverifikasi langsung). "
    "binanceai.fun tetap refund phase; RigForge belum dibuka (freeSharesLeft 621 flat). CAT402 sold out; DRAGON pool habis; pepe pool habis. "
    "Scan leg: pre-flight Ankr 401 gagal ke-52 berturut-turut main job (elapsed 6,8 dtk); watermark TETAP 134086385, gap ~170.273 blok. DIAM." % BLOCK)
snap["checkedNotSaleShape1231_1118"] = (
    "Sourcify feed top BARU vs 1201 (verifiedAt 2026-11-18T05:35:55Z, top 0xa14ffdb8f9ffb5cd7003c969db0da6eee025292c): "
    "0xa14f/0x88ab/0xae26/0xf449/0x4ba4/0x8b51 -> token biasa/tanpa mint/tanpa agent ref, bukan sale-shape, bukan agent-shaped (lihat entri checked-*-1231). "
    "Perbaikan newleads run ini: agent_ref kini mencakup AGENT_ID_REGISTRY, hasAgentId, AGENT_ID (celah 1201 sudah ditutup).")
snap["last_run_wib"] = NOW
snap["last_run_note"] = ("Run 1231: 1 early lead baru (DGF CARD, umur+free%+X unverified, website terverifikasi), 0 kandidat/strong lead baru, 0 track-B dibuka, 0 track-C lead; "
    "PUNNY 29,3% (+2, umur ~16 jam, slot terbuka, gate UNVERIFIED) tetap early lead; velocity tidak ada yang lolos; "
    "scan leg FAST-FAIL Ankr 401 ke-52; re-read 276 calls blok 134256658, 0 chunk error; tidak ada promosi/kandidat/eksekusi.")
json.dump(snap, open(f"{HF}/onchain-snapshot.json", "w"), indent=1)
print("merge OK, block", BLOCK)

st = json.load(open(f"{HF}/onchain-scan-state.json"))
st["note_1231_scan"] = ("Run 2026-11-18 12:31 WIB: driver TIDAK diluncurkan - pre-flight ankr_getLogs gagal deterministik HTTP 401 Unauthorized (elapsed 6,8 dtk, head 134256658); "
    "401 auth-wide, gagal total ke-52 berturut-turut main job. Watermark TETAP 134086385; gap ~170.273 blok dan terus membesar (~8.000 blok/jam). Triase + 5c dilewati (tidak ada output scan).")
json.dump(st, open(f"{HF}/onchain-scan-state.json", "w"), indent=1)
print("scan-state note OK")
