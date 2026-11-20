#!/usr/bin/env python3
"""Merge run 2026-11-18 12:01 WIB re-read into onchain-snapshot.json (lean merge).
Read-only legs only. Never writes scan-bridge.json. No preview/mint/claim.
Adds PUNNY as EARLY LEAD (first-seen this run). Corrects the 1131 registry-bytes
reason for Mechfarm (typo'd literal in newleads script) - outcome unchanged:
Mechfarm stays age-excluded since 2026-11-05 (firstMint 2026-11-03 17:11 WIB)."""
import json
HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
snap = json.load(open(f"{HF}/onchain-snapshot.json"))
reread = json.load(open(f"{HF}/run-2026-11-18-1201-reread.json"))
prev = json.load(open(f"{HF}/run-2026-11-18-1131-reread.json"))
reads = reread["reads"]
prev_reads = prev["reads"]
NOW = "2026-11-18 ~12:01 WIB"
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
        snap["contracts"][key]["runNote1201_1118"] = text
    else:
        print("NOTE MISS", key)

# headline notes (values from 1201 re-read vs 1131)
pun = reads.get("PUNNY", {}).get("views", {})
note("PUNNY", f"Run 1201 (blok {BLOCK}): totalMinted 286->291 (+5), freeMinted 291/999 = 29,1% (<50% kandidat, <70% strong lead). Umur ~15 jam 33 mnt (<24 jam, tutup 20:32 WIB). Slot user TERBUKA (hasClaimedFree 0, mintedBy 0, balance 0). Website gate tetap UNVERIFIED (1131). Tetap EARLY LEAD, tanpa promosi.")
note("HIVE Agents", f"Run 1201 (blok {BLOCK}): totalSupply 1263 FLAT, balanceOf(user)=1, minted-by-user. DIAM.")
note("Bubblebruin", f"Run 1201 (blok {BLOCK}): totalSupply 2620->2621 (+1), freeClaimed 2615/7777 = 33,6%, balanceOf(user)=1, minted-by-user. DIAM.")
note("Agent Bubble", f"Run 1201 (blok {BLOCK}): freeMinted 1889/2222 = 85,0% (>70%) TAPI umur UNVERIFIED -> BUKAN strong lead. totalSupply 2034 FLAT, balanceOf(user)=0. Tetap watchlist-only.")
note("Lumenhold", f"Run 1201 (blok {BLOCK}): freeClaimed 1253/1500 = 83,5% (>70%) TAPI umur UNVERIFIED -> BUKAN strong lead. totalSupply 1257->1258 (+1). Tetap watchlist-only-age-unverified.")
note("Matrix Agents", f"Run 1201 (blok {BLOCK}): freeMinted 616/1000 = 61,6% (<70%), totalSupply 613 FLAT -> velocity GAGAL. Umur UNVERIFIED. Bukan strong lead/kandidat.")
note("AGCLUB", f"Run 1201 (blok {BLOCK}): freeMinted 527/888 = 59,3% (<70%), totalMinted 527 FLAT -> velocity GAGAL. Umur UNVERIFIED. Bukan strong lead/kandidat.")
note("SPARKS", f"Run 1201 (blok {BLOCK}): totalSupply 1181->1182 (+1) -> velocity GAGAL (<20 token). Free% UNVERIFIED. Bukan kandidat.")
note("STOCK AGENT", f"Run 1201 (blok {BLOCK}): totalSupply 673->689 (+16, <20) -> velocity GAGAL. Free inferred (1111-422)/1111 = 62,0% (<70%). Umur UNVERIFIED. Slot user TERBUKA (quote 0, freeMintedByWallet 0). Bukan kandidat/strong lead.")
note("AgentEcho", f"Run 1201 (blok {BLOCK}): totalSupply 374->380 (+6, <20) -> velocity GAGAL. Bukan kandidat.")
note("Everything Is Mine (EIM)", f"Run 1201 (blok {BLOCK}): totalMinted 688->694 (+6, <20) -> velocity GAGAL. Free% UNVERIFIED, umur UNVERIFIED. Bukan kandidat.")
note("Mine Card", f"Run 1201 (blok {BLOCK}): totalSupply 1268->1276 (+8, <20) -> velocity GAGAL. Bukan kandidat. DIAM.")
note("THE WALL", f"Run 1201 (blok {BLOCK}): totalSupply 5433->5471 (+38, 1,094/mnt, 8,91x vs prev 0,123) -> velocity LOLOS TAPI TIDAK promosi: umur UNVERIFIED (post Boltbook pertama 2026-11-08, first mint belum terverifikasi), free-pct UNVERIFIED (freeMinted/freeLeft revert, FREE_SUPPLY null), website gate GAGAL 2026-11-08 (thewall-agentic.xyz tidak mencetak kontrak). Tetap watchlist-only.")
note("PunchCard", f"Run 1201 (blok {BLOCK}): totalSupply 1334->1338 (+4) -> velocity GAGAL. freeMinted 1316/5555 = 23,7%. Bukan kandidat. DIAM.")
note("CAT402", f"Run 1201 (blok {BLOCK}): freeCatsClaimed 100/100 - SOLD OUT (sudah diketahui). DIAM.")
note("DRAGON", f"Run 1201 (blok {BLOCK}): freeMinted 1000/1000 - pool gratis HABIS (sudah diketahui), balanceOf(user)=1. DIAM.")

# ---- E5F8: agent-gated NFT, BELUM LAUNCH -> watchlist-only (upcoming), BUKAN early lead ----
snap["contracts"]["E5F8-0xe5f8"] = {
    "address": "0xe5f8f8c424821908752332d527428258EcfC245b",
    "name": "E5F8-0xe5f8",
    "kind": "ERC721",
    "status": "watchlist-only-not-launched-2026-11-18",
    "totalMinted": 1,
    "ownerTestMinted": 1,
    "OWNER_TEST_CAP": 3,
    "MAX_SUPPLY": 3333,
    "MAX_PER_WALLET": 5,
    "PRICE": 100000000000000,
    "mintLive": 0,
    "mintOpen": 0,
    "paused": 0,
    "hasAgentId_user": 1,
    "agentRegistryUint": 552192074493313695968015109214105588393044541999,
    "registry_bytes": True,
    "sourcifyVerifiedAt": "2026-11-18T05:03:04Z",
    "balanceOf_user": 0,
    "xVerified": False,
    "velocityVerified": False,
    "launchNote": "BELUM LAUNCH: mintLive=0, mintOpen=0; satu-satunya mint (totalMinted 1) adalah ownerTestMinted=1 (owner test mint), BUKAN public first mint. Umur peluncuran UNVERIFIED (verifiedAt Sourcify bukan launch time).",
    "baselineNote": "Triage run 1201 WIB 2026-11-18 (Sourcify feed top baru). Agent-shaped: AGENT_ID_REGISTRY + hasAgentId() + mint() + registry bytes; TAPI tanpa fungsi freeMint, tanpa FREE_SUPPLY/free view, PRICE 0,0001 BNB (berbayar), mint belum dibuka. BUKAN early lead (tidak ada public first mint) dan BUKAN track-C (bukan sale-shape). Dipantau sebagai upcoming watchlist item; bila mint dibuka, cek ulang free path + umur + gate website sebelum klasifikasi apa pun.",
    "firstSeenBlock": BLOCK,
    "firstSeenWib": "2026-11-18 ~12:01 WIB (Sourcify feed)",
    "lastReadBlock": BLOCK,
    "lastReadWib": NOW,
    "supplyView": "totalMinted",
    "currentRatePerMin": None,
    "velocityLegPasses": False,
}
# ---- checked (log only, tidak masuk watchlist aktif) ----
snap["contracts"]["checked-0xc442-1201"] = {
    "address": "0xc442e8ba26B9E5088d1D70Dc8EDFCdE4d2E911B0",
    "status": "checked-not-agent-shaped-2026-11-18",
    "note": "Run 1201 triage (Boltbook EN baru): Sourcify ABI kosong (n_fns 0), registry bytes True saja, totalMinted 186/MAX_SUPPLY 5555, semua free view revert, tanpa fungsi agent/free. BUKAN agent-shaped (bytecode saja tanpa bukti konkret agent/free-mint). Log only.",
    "lastReadBlock": BLOCK, "lastReadWib": NOW}
snap["contracts"]["checked-0x6e7b-1201"] = {
    "address": "0x6e7b7875a6de6aceed67545b47486c5c7631ac84",
    "status": "checked-not-a-contract-2026-11-18",
    "note": "Run 1201 triage (Boltbook): codelen 2 (0x, EOA/bukan kontrak), semua view None. Bukan alamat kontrak. Log only.",
    "lastReadBlock": BLOCK, "lastReadWib": NOW}
snap["contracts"]["checked-0xaf7c-1201"] = {
    "address": "0xaf7cd30f597fe2e26efdf29389e5d6be1cb63959",
    "status": "checked-not-a-lead-2026-11-18",
    "note": "Run 1201 triage (Boltbook): agent-shaped (AGENT_ID + FREE_SUPPLY/free views) TAPI verifiedAt Sourcify 2026-11-01 (17 hari lalu, umur >=24 jam), free pool HABIS (freeClaimed 678 = FREE_SUPPLY 678), quote user 50000000000000 wei (>0, berbayar), totalSupply 742/MAX 969, mintOpen 1. BUKAN lead/kandidat. Log only.",
    "lastReadBlock": BLOCK, "lastReadWib": NOW}
snap["contracts"]["checked-0xd48e-1201"] = {
    "address": "0xd48e6f6ffd746493b6bcd753c67c716660953624",
    "status": "checked-not-agent-shaped-2026-11-18",
    "note": "Run 1201 triage (Boltbook): Sourcify ABI kosong (n_fns 0), registry bytes True saja, totalMinted 4900/MAX_SUPPLY 5000, semua free view revert, tanpa fungsi agent/free. BUKAN agent-shaped. Log only.",
    "lastReadBlock": BLOCK, "lastReadWib": NOW}

snap["contracts"].setdefault("bsccat", {})["runNote1201_1118"] = (
    f"Run 1201: freeMinted 526 (flat vs 1131), totalSupply mentah 5,26e26; pool views lain revert. DIAM.")
snap["contracts"].setdefault("pepe", {})["runNote1201_1118"] = (
    "Run 1201: free pool HABIS 500/500, user sudah mint (hasMinted 1). DIAM.")

pc = snap["pending_claims"]["binanceai.fun"]
pc["lastReadWib"] = NOW
pc["runNote1201_1118"] = (f"Run 1201 (blok {BLOCK}): launched=0, failed=1, isRefundPhase=1, "
    "tokenClaimed(user)=0, totalShares 3110 - tetap pending/refund, sudah dilaporkan sekali (2026-11-02). DIAM.")
rf = snap["track_c"]["RigForge"]
rf["lastReadBlock"] = BLOCK
rf["runNote1201_1118"] = (f"Run 1201 (blok {BLOCK}): openedAt 0, freeSharesLeft 621 (1131: 622), "
    "freeClaimed 379 (1131: 378) - pool BELUM dibuka, tanpa perubahan status. DIAM.")

snap["runNote1201_1118"] = (
    "Run 1201 (blok re-read %d, interval ~34,7 mnt vs 1131): 0 kandidat baru, 0 strong lead baru, 0 early lead baru, 0 track-B dibuka, 0 track-C lead. "
    "Velocity: THE WALL LOLOS (+38, 1,094/mnt, 8,91x) TAPI TIDAK promosi (umur UNVERIFIED + free-pct UNVERIFIED + gate website GAGAL 2026-11-08); selain itu tidak ada yang lolos (terbanyak STOCK +16, AgentEcho +6, PunchCard +4, SPARKS +1 - semua <20 token). "
    "AgentBubble 85,0%% + Lumenhold 83,5%% di atas 70%% TAPI umur UNVERIFIED -> BUKAN strong lead. STOCK free inferred 62,0%% (<70%%); Matrix 61,6%%; AGCLUB 59,3%%; PunchCard 23,7%%. "
    "PUNNY 0xaFAE0Bf373ad87E88555afe1605111F66C99062C: freeMinted 291/999 = 29,1%% (+5 sejak 1131), umur ~15 jam 33 mnt (<24 jam, tutup 20:32 WIB), slot user TERBUKA, gate website tetap UNVERIFIED -> tetap EARLY LEAD, tanpa promosi. "
    "Triage 5 alamat baru: Sourcify top 0xe5f8f8c4 (agent-gated: AGENT_ID_REGISTRY + hasAgentId + registry bytes; TAPI mintLive=0/mintOpen=0, satu-satunya mint adalah ownerTestMinted=1, PRICE 0,0001 BNB berbayar, tanpa freeMint/FREE_SUPPLY -> BELUM LAUNCH, watchlist-only upcoming, BUKAN early lead); "
    "Boltbook 0xc442e8ba (ABI kosong, registry bytes saja -> bukan agent-shaped); 0x6e7b7875 (EOA, codelen 2, bukan kontrak); "
    "0xaf7cd30f (agent-shaped AGENT_ID + free views TAPI verifiedAt 2026-11-01, free pool HABIS 678/678, quote user >0 -> bukan lead); "
    "0xd48e6f6f (ABI kosong, registry bytes saja -> bukan agent-shaped). Semua log only kecuali 0xe5f8 (watchlist upcoming). "
    "CELAH DETEKSI SKRIP: newleads agent_ref hanya cocok {agentId, agentRegistry, registry, getAgentId, agentGate, AgentGate} - MELEWATKAN konstanta/fungsi AGENT_ID_REGISTRY, hasAgentId, AGENT_ID (kena 0xe5f8 + 0xaf7c; vonis run ini sudah dikoreksi manual, hasil tetap benar). Perbaiki di run berikut: tambah ketiganya ke agent_ref. "
    "Sourcify feed top BARU (verifiedAt 2026-11-18T05:03:04Z): 0xe5f8 (di atas) + 0x2ec4Ebfef83022382EF91E205CFAEca11216D5Fd (sudah shape-check hot-leg 1159: S1/S2 false, no mint, no agent ref -> checked-not-sale-shape). "
    "Boltbook EN/ZH: Kitebots 1.473/4.000 + BUBB recheck 2.034/2.222 (sama dengan hot-leg 1159); SUDOSAINTS tetap age-excluded; 0x37d39fcc = Thetavox (sudah di snapshot), 0xde536232 = Mechfarm (age-excluded), 0xe471c0e3 = NovaAgent-e471 (sudah di snapshot). "
    "Route 3/6: Square + web sweep hanya proyek lama (Oathbots 28 Okt, AgentForge 27 Okt, AGENT ID cards 25 Okt, Laser Agents 25 Okt, Agentic Gangster 9 Nov, AGENT COSMOS 13 hari lalu) - semua umur >24 jam, bukan kandidat; Odaily newsflash 18 Nov 05:12 UTC tanpa pengumuman free-mint Agent ID; DappBay tidak dipakai run ini (tidak ada proyek baru yang butuh gate-check; absen dari DappBay bukan bukti apa-apa). "
    "binanceai.fun tetap refund phase; RigForge belum dibuka (freeSharesLeft 621). CAT402 sold out; DRAGON pool habis; pepe pool habis. "
    "Scan leg: pre-flight Ankr 401 gagal ke-51 berturut-turut main job (elapsed 2,9 dtk); watermark TETAP 134086385, gap ~166.466 blok. DIAM." % BLOCK)
snap["checkedNotSaleShape1201_1118"] = (
    "Sourcify feed top BARU vs 1131 (verifiedAt 2026-11-18T05:03:04Z, top 0xe5f8f8c424821908752332d527428258EcfC245b): "
    "0xe5f8 -> agent-gated tapi belum launch (lihat entri E5F8-0xe5f8); "
    "0x2ec4Ebfef83022382EF91E205CFAEca11216D5Fd (top hot-leg 1159, verifiedAt 2026-11-18T04:59:33Z): S1=False S2=False, no mint, no agent ref, 16 fns -> checked-not-sale-shape.")
snap["last_run_wib"] = NOW
snap["last_run_note"] = ("Run 1201: 0 kandidat/strong/early lead baru, 0 track-B dibuka, 0 track-C lead; "
    "THE WALL velocity LOLOS tapi tanpa promosi (umur+free% unverified, gate gagal); PUNNY 29,1% (+5, umur ~15,5 jam, slot terbuka, gate UNVERIFIED) tetap early lead; 0xe5f8 agent-gated tapi belum launch (watchlist upcoming); "
    "scan leg FAST-FAIL Ankr 401 ke-51; re-read 276 calls blok 134252851, 0 chunk error; tidak ada promosi/kandidat/eksekusi.")
json.dump(snap, open(f"{HF}/onchain-snapshot.json", "w"), indent=1)
print("merge OK, block", BLOCK)

st = json.load(open(f"{HF}/onchain-scan-state.json"))
st["note_1201_scan"] = ("Run 2026-11-18 12:01 WIB: driver TIDAK diluncurkan - pre-flight ankr_getLogs gagal deterministik HTTP 401 Unauthorized (elapsed 2,9 dtk, head 134252851); "
    "401 auth-wide, gagal total ke-51 berturut-turut main job. Watermark TETAP 134086385; gap ~166.466 blok dan terus membesar (~8.000 blok/jam). Triase + 5c dilewati (tidak ada output scan).")
json.dump(st, open(f"{HF}/onchain-scan-state.json", "w"), indent=1)
print("scan-state note OK")
