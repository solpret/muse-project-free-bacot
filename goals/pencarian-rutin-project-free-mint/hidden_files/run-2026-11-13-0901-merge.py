#!/usr/bin/env python3
"""Merge for free-mint-search run 2026-11-13 09:01 WIB.
Applies fresh reads (verify ~blok 133269xxx, triage blok 133269544),
discovery (Sourcify feed 3 new, all not-sale-shaped; Boltbook EN+ZH 4 new
addresses = tx-hash false positives), pre-flight (Ankr 401 fast-fail),
bridge (116 contracts, 0 new, 7 same-owner-discarded), Boltbook post triage
(SEVENFOLD age-excluded, THYRK age-excluded + user holds 1), web sweep
(EN+ZH: all hits already in snapshot), OLIVER age deep-dive (historical
eth_call missing-trie-node; BscScan deploy-time route via browser; slot
verified open via freeClaimedByAgent(bytes32)=0).
OLIVER age verdict is read from run-2026-11-13-0901-oliver-age.json
(field 'age_verdict': 'lt24h' with 'deploy_wib' OR 'unverified').
Backup taken before running. Writes onchain-snapshot.json. No preview/mint
in this script itself (a strong-lead OLIVER promotion, if the verdict is
lt24h, is executed by the run operator under STRONG-LEAD DIRECT MINT)."""
import json, shutil
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
NOW = "2026-11-13 ~09:25 WIB"
shutil.copy(BASE + "onchain-snapshot.json", BASE + "onchain-snapshot-2026-11-13-0901.bak")
s = json.load(open(BASE + "onchain-snapshot.json"))
C = s.setdefault("contracts", {})
T = s.setdefault("track_c", {})
EX = s.setdefault("excluded", {})
age = json.load(open(BASE + "run-2026-11-13-0901-oliver-age.json"))
VERDICT = age.get("age_verdict", "unverified")

# --- Zero: 172 -> 183/500 = 36.6%; still early lead ---
z = C["Zero"]
z.update({
    "totalMinted": 183, "freeMinted": 183, "freePct": 36.6,
    "freePctNote": "183/500 FREE_CAP (verified on-chain run 0901, blok ~133269544; totalSupply() reverts on this contract, totalMinted used)",
    "freeClaimed_user": 0, "mintsBy_user": 0, "balanceOf_user": 0,
    "holdsAgentId_user": 1,
    "lastReadBlock": 133269544, "lastReadWib": NOW,
    "previousRatePerMin": 2.42, "currentRatePerMin": 0.32,
    "previousTotalSupply": 172, "mintedInInterval": 11,
    "intervalMinutes": 34, "velocityRatio": 0.13,
    "velocityLegPasses": False,
    "velocityNote": "Run 0901: 172 (0831, blok 133266858) -> 183 (+11 in ~34 mnt = 0,32/mnt) vs prev 2,42/mnt = 0,13x < 1,5x -> velocity GAGAL (melambat).",
    "runNote0901": "Run 0901 (blok 133269544): free 183/500 = 36,6% (naik dari 172), umur ~1,5 jam (mintOpensAt 07:55:03 WIB), slot user TERBUKA, website tetap UNVERIFIED. BUKAN kandidat (<50%), BUKAN strong lead (<70%). Early lead, TIDAK di-preview/TIDAK di-mint. DIAM.",
})

# --- Agentx: 639 -> 645/1111 = 58.1%; velocity still fails ---
ax = C["Agentx"]
ax.update({
    "totalMinted": 645, "freeMinted": 645, "freePct": 58.1,
    "freePctNote": "645/1111 FREE_CAP (verified on-chain run 0901, blok ~133269544)",
    "lastReadBlock": 133269544, "lastReadWib": NOW,
    "velocityLegPasses": False,
    "velocityNote": "Run 0901: 639 (0831) -> 645 (+6 in ~34 mnt = 0,18/mnt) vs prev 0,48/mnt = 0,37x < 1,5x -> velocity TIDAK LOLOS (tetap melambat). Status tetap candidate-gate-blocked (sudah dilaporkan sekali); bukan perubahan tier.",
    "previousRatePerMin": 0.48, "currentRatePerMin": 0.18,
    "previousTotalSupply": 639, "mintedInInterval": 6,
    "intervalMinutes": 34, "velocityRatio": 0.37,
    "runNote0901": "Run 0901 (blok ~133269544): free 645/1111 = 58,1%, umur ~10,5 jam, slot TERBUKA, gate website tetap GAGAL (re-check terakhir 0801). Kandidat gate-blocked SUDAH dilaporkan - TANPA perubahan reportable, DIAM. TIDAK di-preview/TIDAK di-mint.",
})

# --- JNTM: free 313 -> 316/1000 = 31.6%; paid surged 5 -> 59; quote STILL NULL ---
T["JNTM"].update({
    "freeClaimed": 316, "freeLeft": 684, "totalMinted": 375, "paidMinted": 59,
    "quote_user_1": None,
    "quoteNote": "quote(address,uint256) dengan (user,1) NULL run ini (juga NULL sejak run 0724) - gratis via quote BELUM terverifikasi; safety (c) TIDAK terpenuhi -> TIDAK di-preview/TIDAK di-mint.",
    "lastReadBlock": 133269544, "lastReadWib": NOW,
    "runNote0901": "Run 0901 (blok 133269544): free 316/1000 = 31,6% (naik dari 313); paidMinted melonjak 5 -> 59 (totalMinted 375) - penjualan berbayar yang bergerak, bukan free. Umur ~3,4 jam, slot TERBUKA. Gate PENDING (L) + quote NULL - TIDAK ADA perubahan, DIAM.",
})

# --- OBFG: 621 -> 628/1230 = 51.1%; age ~14h ---
T["OBFG"].update({
    "totalSupply": 628, "totalMinted": 628, "freeMinted": 628, "freePct": 51.1,
    "freePctNote": "628/1230 FREE_SUPPLY (verified on-chain run 0901, blok ~133269544) - untuk track-C % hanya info, bukan gate.",
    "lastReadBlock": 133269544, "lastReadWib": NOW,
    "runNote0901": "Run 0901: 628/1230 = 51,1% (naik dari 621), umur ~14 jam <24 jam, slot TERBUKA, gate-blocked SUDAH dilaporkan 12 Nov - TANPA perubahan reportable, DIAM.",
})

# --- SolNFT: 328 -> 332/333 = 99.7% (1 slot left) ---
C["SolNFT"].update({
    "totalMinted": 332, "freeMinted": 332, "freePctVerified": 99.7,
    "lastReadBlock": 133269544, "lastReadWib": NOW,
    "runNote0901": "Run 0901 (blok ~133269544): freeMinted 332/333 = 99,7% (1 slot tersisa), mintOpen 1, slot user TERBUKA. Gate-blocked SUDAH dilaporkan 23:30 12 Nov - belum sold out, TANPA perubahan reportable, DIAM.",
})

# --- AgentMuse: freeClaimed 192 -> 201/888 ---
T["AgentMuse"].update({
    "freeClaimed": 201, "bookedTotal": 20100000000000000000000000,
    "lastReadBlock": 133269544, "lastReadWib": NOW,
    "runNote0901": "Run 0901: freeClaimed 201/888 (naik dari 192), bookedOf(user)=FREE_OSK utuh. Minted-by-user, DIAM.",
})

# --- AgentLabs: totalSpecimens 1522 -> 1545, experiment 2 berjalan ---
C["AgentLabs"].update({
    "totalSpecimens": 1545, "currentExperiment": 2,
    "lastReadBlock": 133269544, "lastReadWib": NOW,
    "runNote0901": "Run 0901 (blok ~133269544): experiment 2 BERJALAN (currentExperiment 2, totalSpecimens 1545 vs 1522). Early lead, TIDAK di-preview/TIDAK di-mint. DIAM.",
})

# --- OUTY / MECHA / Pickgrid / PX24-group / HIVE / NOTV / DragonAgent: flat ---
C["OUTY"].update({"minted": 11, "freeSold": 11, "lastReadBlock": 133269544,
                  "lastReadWib": NOW,
                  "runNote0901": "Run 0901: freeSold tetap 11/1500. FREE_FEE 0,0001 BNB TETAP - BUKAN gas-only; bukan kandidat/lead, DIAM."})
C["MECHA"].update({"totalMinted": 1899, "freeClaimed": 1898,
                   "freePctVerified": 42.7, "lastReadBlock": 133269544,
                   "lastReadWib": NOW,
                   "runNote0901": "Run 0901: totalMinted 1899, freeClaimed 1898/4444 = 42,7% (<50%/<70%); gate website TIDAK DITEMUKAN (tetap). DIAM."})
C["Pickgrid Pickaxe"].update({"freeMinted": 216, "lastReadBlock": 133269544,
                              "lastReadWib": NOW,
                              "runNote0901": "Run 0901: free 216/300 = 72% TAPI umur UNVERIFIED - TIDAK BISA promosi ke strong lead, watchlist-only, DIAM."})
for nm, ts in [("PX24", 520), ("SKRR", 504), ("ME30", 268), ("CY24", 455)]:
    C[nm].update({"totalSupply": ts, "lastReadBlock": 133269544,
                  "lastReadWib": NOW,
                  "runNote0901": "Run 0901 (blok ~133269544): totalSupply %d, mintOpen 1, costOf(user,1)=0, umur TETAP UNVERIFIED - watchlist-only, DIAM." % ts})
C["HIVE Agents"].update({"totalSupply": 1263, "lastReadBlock": 133269544,
                         "lastReadWib": NOW,
                         "runNote0901": "Run 0901: totalSupply 1263 flat, balanceOf(user)=1; minted-by-user, bukan kandidat. DIAM."})
T["NOTV"].update({"totalSupply": 0, "totalMinted": 0, "lastReadBlock": 133269544,
                  "lastReadWib": NOW,
                  "runNote0901": "Run 0901: masih 0/2000, freeStart 18:00 WIB 13 Nov - BELUM buka, DIAM."})
C["Dragon Agent"].update({"totalSupply": 967, "lastReadBlock": 133269544, "lastReadWib": NOW,
           "runNote0901": "Run 0901 (blok ~133269544): totalSupply 967 flat vs 0831. Free views TIDAK ADA (NULL) -> free % UNVERIFIED; price 0,000475 BNB, balanceOf(user)=0. Early lead SUDAH dilaporkan sekali 2026-11-09 - TIDAK dilaporkan ulang, DIAM."})

# --- OLIVER: fresh reads + slot verified open via bytes32 probe ---
ol = C["Oliver Agents"]
ol.update({
    "totalSupply": 944, "freeMinted": 894, "freeRemaining": 106,
    "paidMinted": 50, "mintedCount": 944,
    "freeClaimedByAgent_user": 0,
    "balanceOf_user": 0,
    "lastReadBlock": 133269544, "lastReadWib": NOW,
})
if VERDICT == "lt24h":
    ol["status"] = "strong-lead-2026-11-13"
    ol["ageVerified"] = True
    ol["launchWib"] = age.get("deploy_wib")
    ol["runNote0901"] = ("Run 0901: PROMOSI KE STRONG LEAD - umur TERVERIFIKASI <24 jam via waktu deploy "
        "on-chain (BscScan creation txn %s, deploy %s WIB; launch >= deploy -> umur <24 jam). "
        "Free 894/1000 = 89,4% (>70%), slot user TERBUKA (freeClaimedByAgent(bytes32)=0, balanceOf=0), "
        "website TERVERIFIKASI. Lihat run log untuk hasil direct-mint." % (age.get("creation_tx", "?"), age.get("deploy_wib", "?")))
    ol["launchNote"] = ("Umur TERVERIFIKASI run 0901: deploy %s WIB (BscScan creation txn %s). "
        "Launch tidak mungkin sebelum deploy, jadi umur <= %.1f jam < 24 jam. "
        "Rute gagal sebelumnya: first-mint via Ankr getLogs (401 sejak 9 Nov), historical eth_call "
        "(missing trie node, pruned state). Website + X sudah terverifikasi sejak 12 Nov."
        % (age.get("deploy_wib", "?"), age.get("creation_tx", "?"), age.get("age_hours_upper_bound", 0)))
else:
    ol["runNote0901"] = ("Run 0901: free 894/1000 = 89,4 persen (naik dari 892), freeRemaining 106, paid beku 50. "
        "Slot user TERVERIFIKASI TERBUKA run ini (freeClaimedByAgent(bytes32 agentId)=0 - probe sebelumnya pakai "
        "uint256, salah signature). Website + X terverifikasi. TAPI umur launch TETAP UNVERIFIED: historical "
        "eth_call gagal (missing trie node, pruned state) + Ankr getLogs 401 + BscScan creation-txn tidak "
        "terbaca (%s). Tanpa umur terverifikasi <24 jam -> TIDAK BISA promosi ke strong lead. Watchlist-only, DIAM."
        % age.get("bscscan_note", "browser task tanpa hasil"))
    ol["launchNote"] = ("Umur TETAP UNVERIFIED run 0901 (deep-dive diulang): historical eth_call binary-search "
        "gagal missing trie node; Ankr getLogs 401; Sourcify verifiedAt 10:52:35 WIB 12 Nov BUKAN launch time; "
        "BscScan creation-txn %s. Slot kini terverifikasi terbuka (bytes32 probe). Website + X terverifikasi."
        % age.get("bscscan_note", "tidak terbaca"))

# --- SEVENFOLD -> excluded (age-excluded; mintStart 10 Nov) ---
EX["SEVENFOLD"] = {
    "address": "0x4ca724a354db4f743607ecc1a5f117b2e617c8ae",
    "name": "SEVENFOLD", "kind": "ERC721",
    "status": "age-excluded-2026-11-13",
    "totalSupply": 2144, "freeMinted": 2143, "MAX_SUPPLY": 7777,
    "mintStart": 1794270788, "mintStartWib": "2026-11-10 ~07:33 WIB",
    "note": ("Run 0901 triage (temuan Boltbook front page, post SEVENFOLD flat): totalSupply 2144, "
        "freeMinted 2143, MAX 7777, mintOpen 1, mintStart on-chain 1794270788 = 2026-11-10 ~07:33 WIB "
        "-> umur ~73 jam (>=24 jam) -> AGE-EXCLUDED. Agent-shaped (Sourcify verified 2026-11-10T00:37:01Z, "
        "98 fns, agentFreeCap/agentFreeUsed/freeMintX, REGISTRY fn). TIDAK PERNAH dilaporkan oleh job ini "
        "-> SILENT. TIDAK di-preview/TIDAK di-mint."),
    "lastReadBlock": 133269544, "lastReadWib": NOW,
}

# --- THYRK: contracts -> excluded (age-excluded; first-seen bound) ---
th = C.pop("THYRK", None)
EX["THYRK"] = {
    "address": "0x4D90fFC3075FB8897EDFf6d7c6269c906664a20e",
    "name": "THYRK", "kind": "ERC721",
    "status": "age-excluded-2026-11-13",
    "totalSupply": 4338, "freeMinted": 4237, "MAX_SUPPLY": 7777,
    "balanceOf_user": 1,
    "note": ("Run 0901 triage (temuan Boltbook front page, post THYRK flat): totalSupply 4338, freeMinted 4237 "
        "(54,5% dari MAX 7777), agentIdRegistry = registry Binance persis, balanceOf(user)=1 (user SUDAH pegang 1). "
        "Umur: first-seen job ini (hot leg) 2026-11-10 05:24 WIB + Sourcify verifiedAt 2026-11-09T22:19:52Z "
        "-> launch pasti sebelum 10 Nov 05:24 WIB -> umur >= ~76 jam (>=24 jam) -> AGE-EXCLUDED, dihapus dari "
        "contracts aktif. Early lead SUDAH dilaporkan hot leg 10 Nov; exclusion ini bookkeeping (melewati 24 jam "
        "sejak 11 Nov, tanpa fase/batch baru) - TIDAK dilaporkan ulang ke chat utama. TIDAK di-preview/TIDAK di-mint."),
    "lastReadBlock": 133269544, "lastReadWib": NOW,
}

# --- Run notes + timestamps ---
s["timestamp_wib"] = NOW
s["last_run_wib"] = NOW
s["last_run"] = "0901"
s["runNote0901"] = ("Run 0901: SILENT - tidak ada item baru yang dilaporkan. Agentx 645/1111=58,1% velocity GAGAL "
    "(0,18/mnt vs 0,48) tetap kandidat gate-blocked sudah-dilaporkan; Zero 183/500=36,6% velocity GAGAL (0,32 vs 2,42) "
    "tetap early lead; Sol 332/333=99,7% (1 slot tersisa) gate-blocked sudah-dilaporkan; JNTM 316/1000 quote tetap NULL "
    "(paid melonjak 5->59); OBFG 628/1230=51,1% umur ~14 jam; AgentMuse 201/888; AgentLabs exp 2 (1545); OUTY/MECHA/"
    "Pickgrid/PX24-group/HIVE flat; NOTV belum buka; binanceai launched 0; DragonAgent 967 flat. OLIVER 894/1000=89,4% "
    "slot TERBUKA terverifikasi (bytes32 probe) TAPI umur TETAP UNVERIFIED (historical eth_call missing-trie-node + "
    "BscScan Cloudflare bot-wall 09:15-09:21 WIB) -> TIDAK promosi ke strong lead. BARU: SEVENFOLD + THYRK age-excluded "
    "(SILENT, tidak pernah dilaporkan job ini / exclusion bookkeeping); 4 alamat Boltbook baru = hash transaksi, bukan "
    "kontrak. Sweep EN+ZH: 0 baru (semua sudah di snapshot). Scan fast-fail Ankr 401 (watermark TETAP 132512564). "
    "Bridge 116 kontrak, 0 baru, 7 same-owner-discarded.")
s["runNote0901_scan"] = ("Run 0901 SCAN FAST-FAIL: pre-flight ankr_getLogs 1 chunk 50 blok GAGAL HTTP 401 "
    "Unauthorized - kelanjutan outage sejak 2026-11-09 (~4,5 hari). Driver penuh TIDAK dijalankan. "
    "Watermark TETAP 132512564; gap ke head ~750.000+ blok dan membesar. 5c dilewati (tanpa output scan). "
    "0 first-seen, 0 lead, 0 eksekusi.")
s["runNote0901_bridge"] = ("Run 0901 BRIDGE (read-only): 116 kontrak, 0 not-in-snapshot, "
    "7 same-owner-discarded (same_owner_discarded=true) - tidak ada temuan pelengkap scan, tidak ada promosi.")
s["runNote0901_binanceai"] = ("Run 0901 (blok ~133269544): binanceai.fun MINT launched()=0, tokenClaimed(user)=0, "
    "claimable NULL; TOKEN balanceOf(user)=0. Tetap belum buka/pending-refund (sudah dilaporkan sekali) - tanpa aksi, DIAM.")
s["runNote0901_discovery"] = ("Run 0901 DISCOVERY: Sourcify feed 20, 3 baru vs hot-leg-seen, 0 sale-shape "
    "(2x n_fns 2 tanpa mint/quote/free/agent; 1x n_fns 55 tanpa mint/quote/free/agent). Boltbook EN 43862 byte + ZH "
    "42221 byte, 13 alamat, 4 'baru' vs seen = FALSE POSITIVE hash transaksi (0x1558 DROG burn tx, 0x8444 + 0x9adc "
    "AGN claim tx, 0xee7d tidak di front page; semua eth_call kosong + Sourcify unverified) - BUKAN kontrak, "
    "tidak masuk snapshot. Sweep web EN+ZH: Agentic Gangster / STAMP PASS / Meow Cards / RIGBYPASS / Horus AI / "
    "AGENT COSMOS / NOVRA / AGENT ID cards / First-Dollar Grove - SEMUA sudah ada di snapshot "
    "(sold-out / age-excluded / checked), 0 baru.")
json.dump(s, open(BASE + "onchain-snapshot.json", "w"), indent=1)
print("MERGE OK; contracts:", len(C), "track_c:", len(T), "excluded:", len(EX), "| OLIVER verdict:", VERDICT)
