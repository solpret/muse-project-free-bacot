#!/usr/bin/env python3
"""Merge for free-mint-search run 2026-11-13 08:31 WIB.
Applies fresh reads (verify block 133266858, triage block 133267373,
triage2 block 133267661), discovery (Sourcify feed 0 new; Boltbook EN
re-fetched via browser after curl 0-byte; ZH 43187 byte), pre-flight
(Ankr 401 fast-fail), bridge (116 contracts, 0 new, 7 same-owner-discarded),
Boltbook post triage (ONLYAI age-excluded, PIXEL BOYZ same-phase drain,
BANDIT/ELYBIRDS agent-gate evidence noted, NDAEMN not-agent-gated,
DacityCoin + Foxglow age-excluded). Backup taken before running.
Writes onchain-snapshot.json. No preview/mint."""
import json
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
NOW = "2026-11-13 ~09:15 WIB"
s = json.load(open(BASE + "onchain-snapshot.json"))
C = s.setdefault("contracts", {})
T = s.setdefault("track_c", {})
EX = s.setdefault("excluded", {})

# --- Zero: 117 -> 172/500 = 34.4%; still early lead, no promotion ---
z = C["Zero"]
z.update({
    "totalMinted": 172, "freeMinted": 172, "freePct": 34.4,
    "freePctNote": "172/500 FREE_CAP (verified on-chain run 0831, block 133266858)",
    "freeClaimed_user": 0, "mintsBy_user": 0, "balanceOf_user": 0,
    "holdsAgentId_user": 1,
    "lastReadBlock": 133266858, "lastReadWib": NOW,
    "previousRatePerMin": 0.0, "currentRatePerMin": 2.42,
    "previousTotalSupply": 117, "mintedInInterval": 55,
    "intervalMinutes": 22.7, "velocityRatio": None,
    "velocityLegPasses": False,
    "velocityNote": "Run 0831: 117 (0801, blok 133263835) -> 172 (+55 in ~22,7 mnt = 2,42/mnt, >=20 token). First interval rate recorded; velocity cannot pass yet (no previous rate to compare - baseline was 0).",
    "runNote0831": "Run 0831 (blok 133266858): free 172/500 = 34,4% (naik dari 117), umur ~1 jam (mintOpensAt 07:55:03 WIB), slot user TERBUKA, website tetap UNVERIFIED. BUKAN kandidat (<50%), BUKAN strong lead (<70%). Early lead, TIDAK di-preview/TIDAK di-mint. DIAM.",
})

# --- Agentx: 628 -> 639/1111 = 57.5%; velocity NO LONGER passes ---
ax = C["Agentx"]
ax.update({
    "totalMinted": 639, "freeMinted": 639, "freePct": 57.5,
    "freePctNote": "639/1111 FREE_CAP (verified on-chain run 0831, block 133266858)",
    "lastReadBlock": 133266858, "lastReadWib": NOW,
    "velocityLegPasses": False,
    "velocityNote": "Run 0831: 628 (0801) -> 639 (+11 in ~22,7 mnt = 0,48/mnt) vs prev interval 2,91/mnt = 0,17x < 1,5x -> velocity TIDAK LOLOS lagi (melambat). Status tetap candidate-gate-blocked (sudah dilaporkan sekali run 0801); melambatnya velocity BUKAN perubahan tier yang dilaporkan.",
    "previousRatePerMin": 2.91, "currentRatePerMin": 0.48,
    "previousTotalSupply": 628, "mintedInInterval": 11,
    "intervalMinutes": 22.7, "velocityRatio": 0.17,
    "runNote0831": "Run 0831 (blok 133266858): free 639/1111 = 57,5%, umur ~9,9 jam, slot TERBUKA, gate website tetap GAGAL (tidak di-recheck run ini; re-check terakhir 0801). Kandidat gate-blocked SUDAH dilaporkan (hot-leg 0809 + main 0801) - TANPA perubahan reportable, DIAM. TIDAK di-preview/TIDAK di-mint.",
})

# --- JNTM: 306 -> 313/1000 = 31.3%; quote STILL NULL ---
T["JNTM"].update({
    "freeClaimed": 313, "freeLeft": 687, "totalMinted": 318, "paidMinted": 5,
    "quote_user_1": None,
    "quoteNote": "quote(address,uint256) dengan (user,1) NULL run ini (juga NULL sejak run 0724) - gratis via quote BELUM terverifikasi; safety (c) TIDAK terpenuhi -> TIDAK di-preview/TIDAK di-mint.",
    "lastReadBlock": 133266858, "lastReadWib": NOW,
    "runNote0831": "Run 0831 (blok 133266858): free 313/1000 = 31,3% (naik dari 306), umur ~2,9 jam, slot TERBUKA. Gate PENDING (L) + quote NULL - TIDAK ADA perubahan, DIAM.",
})

# --- OBFG: 618 -> 621/1230 = 50.5% ---
T["OBFG"].update({
    "totalSupply": 621, "totalMinted": 621, "freeMinted": 621, "freePct": 50.5,
    "freePctNote": "621/1230 FREE_SUPPLY (verified on-chain run 0831, block 133266858) - untuk track-C % hanya info, bukan gate.",
    "lastReadBlock": 133266858, "lastReadWib": NOW,
    "runNote0831": "Run 0831: 621/1230 = 50,5% (naik dari 618), umur ~13,5 jam <24 jam, slot TERBUKA, gate-blocked SUDAH dilaporkan 12 Nov - TANPA perubahan reportable, DIAM.",
})

# --- SolNFT: 327 -> 328/333 = 98.5% (5 slot tersisa) ---
C["SolNFT"].update({
    "totalMinted": 328, "freeMinted": 328, "freePctVerified": 98.5,
    "lastReadBlock": 133266858, "lastReadWib": NOW,
    "runNote0831": "Run 0831 (blok 133266858): freeMinted 328/333 = 98,5% (5 slot tersisa), mintOpen 1, slot user TERBUKA. Gate-blocked SUDAH dilaporkan 23:30 12 Nov - TANPA perubahan reportable, DIAM.",
})

# --- AgentMuse: freeClaimed 176 -> 192/888 ---
T["AgentMuse"].update({
    "freeClaimed": 192, "bookedTotal": 19200000000000000000000000,
    "lastReadBlock": 133266858, "lastReadWib": NOW,
    "runNote0831": "Run 0831: freeClaimed 192/888 (naik dari 176), bookedOf(user)=FREE_OSK utuh. Minted-by-user, DIAM.",
})

# --- AgentLabs: totalSpecimens 1494 -> 1522, experiment 2 berjalan ---
C["AgentLabs"].update({
    "totalSpecimens": 1522, "currentExperiment": 2,
    "lastReadBlock": 133266858, "lastReadWib": NOW,
    "runNote0831": "Run 0831 (blok 133266858): experiment 2 BERJALAN (currentExperiment 2, totalSpecimens 1522 vs 1494). specimensOf(user)/participants/isSealed/experimentEnd NULL run ini - slot user di experiment 2 UNVERIFIED. Early lead, TIDAK di-preview/TIDAK di-mint. DIAM.",
})

# --- OUTY / MECHA / Pickgrid / PX24-group / HIVE / NOTV: flat ---
C["OUTY"].update({"minted": 11, "freeSold": 11, "lastReadBlock": 133266858,
                  "lastReadWib": NOW,
                  "runNote0831": "Run 0831: freeSold tetap 11/1500. FREE_FEE 0,0001 BNB TETAP - BUKAN gas-only; bukan kandidat/lead, DIAM."})
C["MECHA"].update({"totalMinted": 1899, "freeClaimed": 1898,
                   "freePctVerified": 42.7, "lastReadBlock": 133266858,
                   "lastReadWib": NOW,
                   "runNote0831": "Run 0831: totalMinted 1899, freeClaimed 1898/4444 = 42,7% (<50%/<70%); gate website TIDAK DITEMUKAN (tetap). DIAM."})
C["Pickgrid Pickaxe"].update({"freeMinted": 216, "lastReadBlock": 133266858,
                              "lastReadWib": NOW,
                              "runNote0831": "Run 0831: free 216/300 = 72% TAPI umur UNVERIFIED - TIDAK BISA promosi ke strong lead, watchlist-only, DIAM."})
for nm, ts in [("PX24", 520), ("SKRR", 504), ("ME30", 268), ("CY24", 451)]:
    C[nm].update({"totalSupply": ts, "lastReadBlock": 133266858,
                  "lastReadWib": NOW,
                  "runNote0831": "Run 0831 (blok 133266858): totalSupply %d, mintOpen 1, costOf(user,1)=0, umur TETAP UNVERIFIED - watchlist-only, DIAM." % ts})
C["HIVE Agents"].update({"totalSupply": 1263, "lastReadBlock": 133266858,
                         "lastReadWib": NOW,
                         "runNote0831": "Run 0831: totalSupply 1263 flat, balanceOf(user)=1; minted-by-user, bukan kandidat. DIAM."})
T["NOTV"].update({"totalSupply": 0, "totalMinted": 0, "lastReadBlock": 133266858,
                  "lastReadWib": NOW,
                  "runNote0831": "Run 0831: masih 0/2000, freeStart 18:00 WIB 13 Nov - BELUM buka, DIAM."})

# --- Dragon Agent: totalSupply 967 (snapshot totalMinted 187 stale dari backfill) ---
da = C["Dragon Agent"]
da.update({"totalSupply": 967, "lastReadBlock": 133266858, "lastReadWib": NOW,
           "runNote0831": "Run 0831 (blok 133266858): totalSupply 967 (962 di run 0001-0231; totalMinted 187 di snapshot adalah nilai stale backfill 11-09). Free views TIDAK ADA di kontrak (freeMinted/freeClaimed NULL) -> free % UNVERIFIED; price 0,000475 BNB, MAX_PER_WALLET 15, balanceOf(user)=0. Early lead SUDAH dilaporkan sekali 2026-11-09 (baselineNote) - TIDAK dilaporkan ulang, DIAM."})

# --- ONLYAI -> excluded (age-excluded; silent, never reported by this job) ---
EX["ONLYAI"] = {
    "address": "0x156482AD3F0eebD8E3F70d494ebD1dA3F738f5Ba",
    "name": "ONLYAI Crystals", "symbol": "ONLYAI", "kind": "ERC721",
    "status": "age-excluded-2026-11-13",
    "totalSupply": 2685, "MAX_SUPPLY": 5555, "mintOpensAt": 1793988000,
    "mintOpensAtWib": "2026-11-07 01:00:00 WIB",
    "agentIdRegistry": "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F",
    "mintsBy_user": 0, "holdsAgentId_user": 1, "balanceOf_user": 0,
    "website": "onlyaitoken.pages.dev",
    "note": "Run 0831 triage (temuan Boltbook front page, post 'Jumat pagi'): totalSupply 2685/5555 = 48,3%, mintOpensAt on-chain 1793988000 = 2026-11-07 01:00 WIB (cocok stated launch 6 Nov 18:00 UTC) -> umur ~152 jam (>=24 jam) -> AGE-EXCLUDED. Slot user TERBUKA (mintsBy 0, holdsAgentId 1) tapi umur menggugurkan. Website onlyaitoken.pages.dev (dikutip search-index; belum diverifikasi mencetak kontrak oleh job ini). TIDAK PERNAH dilaporkan oleh job ini (bukan di snapshot sebelumnya) -> SILENT per aturan age-exclusion item belum-pernah-dilaporkan. TIDAK di-preview/TIDAK di-mint.",
    "lastReadBlock": 133267373, "lastReadWib": NOW,
}

# --- DacityCoin -> excluded (age-excluded; silent) ---
EX["DacityCoin"] = {
    "address": "0x90ddd762f407b3edf43f732cd5a68a9e4695a6bd",
    "name": "DacityCoin", "kind": "ERC721",
    "status": "age-excluded-2026-11-13",
    "totalMinted": 1765, "agentFreeUsed": 1730,
    "mintStart": 1794386374, "mintStartWib": "2026-11-11 15:39:34 WIB",
    "mintEnd": 1794818374, "mintEndWib": "2026-11-16 15:39:34 WIB",
    "note": "Run 0831 triage2 (temuan Boltbook post AGENTX): totalMinted 1765, agentFreeUsed 1730/9999, mintStart on-chain 1794386374 = 2026-11-11 15:39:34 WIB -> umur ~41 jam (>=24 jam) -> AGE-EXCLUDED. Agent-shaped (AGENT_ID ref di ABI, Sourcify verified 2026-11-11T08:56:09Z). TIDAK PERNAH dilaporkan oleh job ini -> SILENT. TIDAK di-preview/TIDAK di-mint.",
    "lastReadBlock": 133267661, "lastReadWib": NOW,
}

# --- Foxglow -> excluded (age-excluded; silent) ---
EX["Foxglow"] = {
    "address": "0x6e159c9cd56beadb523b80d195dde39c042a1d48",
    "name": "Foxglow", "kind": "ERC721",
    "status": "age-excluded-2026-11-13",
    "totalSupply": 3343, "freeClaimed": 3342, "FREE_SUPPLY": 7000,
    "MAX_SUPPLY": 7777, "mintOpen": 1,
    "note": "Run 0831 triage2 (temuan Boltbook post AGENTX): totalSupply 3343, freeClaimed 3342/7000 = 47,7%, mintOpen 1. Sourcify verifiedAt 2026-10-29T16:00:00Z -> umur >=15 hari (>=24 jam) -> AGE-EXCLUDED. Agent-shaped (AGENT_ID ref di ABI). TIDAK PERNAH dilaporkan oleh job ini -> SILENT. TIDAK di-preview/TIDAK di-mint.",
    "lastReadBlock": 133267661, "lastReadWib": NOW,
}

# --- NDAEMN -> contracts checked-not-agent-shaped (mint passes from plain wallet) ---
C["NDAEMN"] = {
    "address": "0xa55d0dd67e443790fef78fe003e1c800201c1d08",
    "name": "Neon Daemon Guild", "symbol": "NDAEMN", "kind": "ERC721",
    "status": "checked-not-agent-shaped-2026-11-13",
    "totalSupply": 550, "freeClaimed": 545, "FREE_SUPPLY": 7000,
    "MAX_SUPPLY": 7777, "mintOpen": 1,
    "note": "Run 0831 triage2 (temuan Boltbook post AGENTX): totalSupply 550, freeClaimed 545/7000 = 7,8%, mintOpen 1, Sourcify verified 2026-11-12T04:46:10Z (34 fns: mint, freeClaimed/freeFor/freeLeft/freeUsed, quote). BUKAN agent-shaped: TIDAK ADA referensi registry Agent ID di ABI, DAN penulis Boltbook memverifikasi mint(1) value 0 LOLOS dari plain wallet tanpa Agent ID (juga mint(2)/mint(3) lolos) - bukan gate Agent ID. BUKAN lead/kandidat; dicatat checked, TIDAK dilaporkan.",
    "lastReadBlock": 133267661, "lastReadWib": NOW,
}

# --- BANDIT: agent-gate evidence (Boltbook) vs 0201 label; no promotion ---
b = T["Feed-0x2d61"]
b["note0831"] = ("Run 0831: penulis Boltbook memverifikasi LANGSUNG (blok 133,265,097/138): "
    "totalMinted/agentFreeUsed 137, sim claimAgentFree() value 0 LOLOS dari Agent wallet dan "
    "revert 'no agent id' dari plain wallet - Agent ID gate NYATA. Ini melengkapi/mengkoreksi "
    "label 0201 'not-agent-shaped' (cek itu S1/S2-shape via Sourcify ABI: 47 fns, mint + agent_ref, "
    "tanpa quote/free views). TAPI: entri snapshot sudah ada (bukan first-seen) -> BUKAN early lead; "
    "137/1000 = 13,7% (<50%/<70%) -> BUKAN kandidat/strong lead; umur launch UNVERIFIED. "
    "TIDAK ada promosi, TIDAK dilaporkan, TIDAK di-preview/di-mint.")
b["lastReadWib"] = NOW

# --- ELYBIRDS: agent-gate evidence (Boltbook); no promotion ---
e = C["checked-0x4362-2131"]
e["note0831"] = ("Run 0831: penulis Boltbook memverifikasi LANGSUNG (blok 133,265,097/138): "
    "totalSupply 1578, sim mint(1) value 0 LOLOS dari Agent wallet dan revert 'Agent ID required' "
    "dari plain wallet - Agent ID gate NYATA. Ini melengkapi label 11-11 'checked-not-sale-shape' "
    "(cek itu S1/S2-shape; Sourcify saat itu unverified, fn_count 0). TAPI: entri snapshot sudah ada "
    "(bukan first-seen) -> BUKAN early lead; 1578/7777 = 20,3% (<50%/<70%) -> BUKAN kandidat/strong "
    "lead; umur launch UNVERIFIED. TIDAK ada promosi, TIDAK dilaporkan, TIDAK di-preview/di-mint.")
e["lastReadWib"] = NOW

# --- OLIVER: age STILL unverified (launch time not found) ---
ol = C["Oliver Agents"]
ol["runNote0831"] = ("Run 0831: penulis Boltbook baca 942 total / 892 free = 89,2% FREE_MAX (108 tersisa, "
    "~6/jam). Website TERVERIFIKASI (oliveragents.pages.dev mencetak kontrak persis). TAPI umur launch "
    "TETAP UNVERIFIED: search-index (2 query) tidak menemukan waktu launch; koroborasi first-mint "
    "terblokir Ankr 401 (outage sejak 9 Nov). First-seen job ini 2026-11-12 13:01 WIB BUKAN launch time. "
    "Tanpa umur terverifikasi <24 jam -> TIDAK BISA promosi ke strong lead walau >70% + website lolos. "
    "Watchlist-only, TIDAK dilaporkan ulang, TIDAK di-preview/di-mint. Verifikasi umur tetap terbuka run berikut.")
ol["lastReadWib"] = NOW

# --- PIXEL BOYZ: remove stale contracts duplicate (already in excluded) ---
if "PIXEL BOYZ" in C:
    del C["PIXEL BOYZ"]
pb = EX["PIXEL BOYZ"]
pb["excludedNote0831"] = ("Run 0831 triage (blok 133267373): totalMinted 5922 (5433 di snapshot), "
    "freeAllocationRemaining 86 (1.533 pada 11-07), freeSaleActive 1, walletFreeRemaining(user) 2, "
    "freeMintedByWallet(user) 0, hasAgentId(user) 1. FASE YANG SAMA (freeSale 6.000) terus terkuras "
    "sejak Nov 2-3 - BUKAN fase/batch baru. Umur ~10-11 hari -> TETAP age-excluded, TIDAK dilaporkan "
    "ulang. Entri duplikat di contracts (watchlist-only-pelengkap-scan-2026-11-08) DIHAPUS run ini "
    "(bookkeeping; vonis excluded sudah ada sejak 11-07).")
pb["lastReadWib"] = NOW

# --- Run notes + timestamps ---
s["timestamp_wib"] = NOW
s["last_run_wib"] = NOW
s["last_run_note"] = ("Run 0831: SILENT - tidak ada item baru yang dilaporkan. Zero 172/500=34,4% (early lead, "
    "bukan promosi); Agentx 639/1111=57,5% velocity MELAMBAT (0,48/mnt vs 2,91) tapi tetap kandidat "
    "gate-blocked sudah-dilaporkan; JNTM 313/1000 quote tetap NULL; OBFG 621/1230=50,5%; Sol 328/333=98,5%; "
    "AgentMuse 192/888; AgentLabs exp 2 (1522); OUTY/MECHA/Pickgrid/PX24-group/HIVE flat; NOTV belum buka; "
    "binanceai launched 0; DragonAgent 967 (nilai snapshot stale diperbaiki). BARU DITEMUKAN: ONLYAI "
    "age-excluded SILENT (launch 7 Nov 01:00 WIB, umur ~152 jam); DacityCoin age-excluded SILENT (launch "
    "11 Nov 15:39 WIB, ~41 jam); Foxglow age-excluded SILENT (verified 29 Okt); NDAEMN checked-not-agent-shaped "
    "(mint lolos plain wallet); PIXEL BOYZ fase-lama terkuras (86 tersisa) tetap excluded + duplikat contracts "
    "dihapus; BANDIT/ELYBIRDS bukti agent-gate dari Boltbook dicatat, tanpa promosi; OLIVER 89,2% tapi umur "
    "TETAP UNVERIFIED. Scan fast-fail Ankr 401 (watermark TETAP 132512564). Boltbook EN re-fetch via browser "
    "(curl 0-byte); ZH 43187 byte, 0 alamat baru. Bridge 116 kontrak, 0 baru, 7 same-owner-discarded. "
    "Sourcify feed 20, 0 baru vs hot-leg-seen.")
s["runNote0831"] = s["last_run_note"]
s["runNote0831_scan"] = ("Run 0831 SCAN FAST-FAIL: pre-flight ankr_getLogs 1 chunk 50 blok GAGAL HTTP 401 "
    "Unauthorized (~29 dtk incl. blockNumber) - kelanjutan outage sejak 2026-11-09 (~4,5 hari; kuota freemium "
    "Ankr 0% s.d. 1 Des 2026). Driver penuh TIDAK dijalankan. Watermark TETAP 132512564; gap ke head "
    "~750.000+ blok dan membesar. 5c dilewati (tanpa output scan). 0 first-seen, 0 lead, 0 eksekusi.")
s["runNote0831_bridge"] = "Run 0831 BRIDGE (read-only): 116 kontrak, 0 not-in-snapshot, 7 same-owner-discarded - tidak ada temuan pelengkap scan, tidak ada promosi."
s["runNote0831_binanceai"] = ("Run 0831 (blok 133266858): binanceai.fun MINT launched()=0, tokenClaimed(user)=0, "
    "claimable NULL; TOKEN balanceOf(user)=0. Tetap belum buka/pending-refund (sudah dilaporkan sekali) - tanpa aksi, DIAM.")
json.dump(s, open(BASE + "onchain-snapshot.json", "w"), indent=1)
print("MERGE OK; contracts:", len(C), "track_c:", len(T), "excluded:", len(EX))
