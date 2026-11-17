#!/usr/bin/env python3
"""Snapshot update for free-mint-search run 2026-11-14 05:31 WIB.
Updates Kicks (sold out), FIND/LumenFindings (opened exp8), focus-set
re-reads, and adds PIXEL BOYZ bridge complement. No other keys touched."""
import json

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
P = BASE + "onchain-snapshot.json"
s = json.load(open(P))
c = s["contracts"]

# --- Kicks: early lead -> strong lead verified -> sold out unused ---
k = c.get("Kicks", {})
k.update({
    "status": "sold-out-free-2026-11-14",
    "totalMinted": 222, "freeMinted": 222, "FREE_CAP": 222, "MAX_SUPPLY": 333,
    "mintOpen": 1, "freeCount_user": 0, "balanceOf_user": 0,
    "lastReadBlock": 133436887, "lastReadWib": "2026-11-14 ~06:07 WIB",
    "firstMintBlock": 133425944,
    "firstMintTx": "0x12e930120f00222f6931bbe6c84724d7322a5b3c22cb4cfd81f74d4fe1ec800d",
    "firstMintWib": "2026-11-14 04:44:48 WIB",
    "ageVerified": "first mint Transfer-from-zero blok 133425944 (04:44:48 WIB) + 0 log di 133423359-133425558; umur ~1 jam 22 mnt saat sold-out, <24 jam TER VERIFIKASI",
    "website": "https://kicks-mint.netlify.app/",
    "gate": "website_passed_method_I_2026-11-14",
    "gateEvidence": "tokenURI/metaURI on-chain -> kicks-mint.netlify.app; situs mencetak kontrak persis 0x5726...730A8 (2x di HTML) + cocok identitas (KICKS 333, free 222, 1/wallet, Agent ID only, paid 0.0001 BNB)",
    "audit": "Binance hasResult=false (no result, isSupported=true, riskAlert=null) run 0531 - diungkap sebagai tidak ada hasil, bukan pass",
    "runNote0531": "Run 0531: STRONG LEAD terverifikasi (umur <24h + free 196/222=88,3% + slot user terbuka + gate website LOLOS + audit tanpa hasil) - TAPI free pool HABIS sebelum preview: freeMinted 222/222 blok 133436887 ~06:07 WIB. TIDAK ADA mint (pool habis). Paid phase (0.0001 BNB) TIDAK dieksekusi (tanpa otorisasi paid). Dilaporkan sekali sebagai sold-out; dihapus dari watchlist aktif.",
})
c["Kicks"] = k

# --- FIND / LumenFindings: upcoming -> opened exp8, watchlist-only ---
f = c.get("LumenFindings", {})
f.update({
    "address": "0x4158B701EaA30E8FaDBaA526F70780A38318c1C4",
    "status": "watchlist-only-opened-2026-11-14",
    "agentIdRegistry": "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F",
    "currentExperiment": 8,
    "expStart_8_wib": "2026-11-14 04:00 WIB",
    "expEnd_8_wib": "2026-11-14 07:00 WIB",
    "specimens_8": 172, "participants_8": 172, "isSealed_8": 0,
    "totalSpecimens": 1920, "MAX_PER_EXPERIMENT": 10,
    "priceFor_user": 0, "holdsAgentId_user": 1, "specimensOf_8_user": 0,
    "website": "https://lumenresearch.ltd/",
    "websiteNote": "baseTokenURI on-chain -> lumenresearch.ltd (method I pointer); BELUM dicek apakah situs mencetak kontrak - gate belum dinilai",
    "freePctNote": "Tidak ada free-cap view (MAX_PER_EXPERIMENT=10 = per-wallet, bukan cap exp) -> kaki % UNVERIFIED; bukan kandidat/strong lead",
    "lastReadBlock": 133433004, "lastReadWib": "2026-11-14 ~05:35 WIB",
    "runNote0531": "Run 0531: exp8 BUKA (04:00-07:00 WIB), agent-shaped, slot gratis user terbuka (priceFor 0, specimensOf 0), diskusi Boltbook ZH 05:00-05:04 WIB. % free UNVERIFIED (tanpa cap) + velocity baseline baru (172) -> watchlist-only, TIDAK dilaporkan sebagai lead/kandidat.",
})
c["LumenFindings"] = f

# --- focus-set re-read values (run 0531, blok 133432988) ---
updates = {
    "WoozCode": {"totalSnippets": 164, "lastReadBlock": 133432988},
    "MORFO": {"totalMinted": 515, "lastReadBlock": 133432988},
    "Entropics Living Noise": {"totalMinted": 264, "lastReadBlock": 133432988},
    "DRAGON-0xad0d": {"totalSupply": 626, "freeClaimed": 622, "lastReadBlock": 133432988,
        "runNote0531": "Run 0531: freeClaimed 622/888 = 70,05% (melewati 70%) TAPI umur UNVERIFIED (semua view waktu revert/null) -> BUKAN strong lead; tetap watchlist-only-age-unverified."},
    "AngelEye-77D9": {"totalSupply": 5, "totalMinted": 5, "freeMinted": 1, "lastReadBlock": 133432988},
    "AngelEye-07bD": {"totalSupply": 5, "totalMinted": 5, "freeMinted": 1, "lastReadBlock": 133432988},
    "NovaRemnants-38C1": {"totalRemnants": 280, "lastReadBlock": 133432988},
    "Race Agents": {"totalSupply": 432, "freeMinted": 432, "lastReadBlock": 133432988},
    "AbsurdAgentNFT-72C1": {"totalMinted": 0, "mintOpen": 0, "lastReadBlock": 133432988},
    "B77D-0xB77D": {"totalMinted": 0, "mintOpen": 0, "lastReadBlock": 133432988},
    "AgentZENITH": {"totalSupply": 290, "lastReadBlock": 133432988},
    "First-Dollar Sparks": {"totalSupply": 194, "totalMinted": 194, "lastReadBlock": 133432988},
    "AgentBubble": {"totalSupply": 1431, "freeMinted": 1290, "lastReadBlock": 133432988},
    "HIVE Agents": {"totalSupply": 1263, "lastReadBlock": 133432988},
    "Zero": {"lastReadBlock": 133432988},
    "PX24": {"totalSupply": 527, "lastReadBlock": 133432988},
    "SKRR": {"totalSupply": 519, "lastReadBlock": 133432988},
}
for key, vals in updates.items():
    if key in c:
        c[key].update(vals)
        c[key]["lastReadWib"] = "2026-11-14 ~05:35 WIB"

# --- PIXEL BOYZ bridge complement (not a lead, watchlist only) ---
c["PIXEL BOYZ"] = {
    "address": "0xafb50403c0838d5b45f8748138ba33a70e23b8cf",
    "name": "PIXEL BOYZ", "symbol": "PBOYZ", "kind": "ERC721",
    "status": "watchlist-only-scan-bridge-2026-11-14",
    "source": "scan",
    "gate": "website_no_pointer_found",
    "same_owner_discarded": False,
    "note": "Temuan pelengkap scan (bridge): #3693 free, 1 entity only - BUKAN signal/lead, TIDAK auto-mint. Ditambahkan ke snapshot run 0531; dilaporkan hanya bila re-read rutin menunjukkan tier Free Bacot.",
    "firstSeenWib": "2026-11-14 ~05:31 WIB",
}

s["last_run_wib"] = "2026-11-14 ~06:07 WIB"
s["last_run"] = "2026-11-14T06:07+07:00"
s["runNote0531_1114"] = (
    "Run 0531 2026-11-14: Kicks 0x5726...730A8 STRONG LEAD terverifikasi (first mint 04:44:48 WIB, "
    "free 196/222=88,3%, slot user terbuka, gate website LOLOS via tokenURI->kicks-mint.netlify.app, "
    "audit Binance tanpa hasil) - free pool HABIS (222/222, blok 133436887 ~06:07 WIB) sebelum preview, "
    "TIDAK ADA mint; dilaporkan sekali sebagai sold-out. FIND exp8 (LumenFindings) BUKA 04:00-07:00 WIB, "
    "agent-shaped, slot gratis terbuka, % UNVERIFIED -> watchlist-only. DragonAgents 622/888=70,05% tapi umur "
    "UNVERIFIED -> bukan strong lead. Re-read 20/20 OK blok 133432988. Scan Ankr FAST-FAIL (preflight 401, 9,8 dtk); "
    "watermark tetap 132512564, gap ~920rb blok. Sourcify feed 0 baru vs 0501. Boltbook EN stale (12 Nov 23:23 UTC), "
    "ZH segar 05:07 WIB. Bridge: PIXEL BOYZ ditambahkan sbg temuan pelengkap scan (bukan lead). "
    "BinanceAI: launched 0/failed 1/refund 1 TETAP (sudah dilaporkan sekali). Crown sudah sold-out-free. "
    "AbsurdAgentNFT buka 17:00 WIB, B77D masih tutup. 0 kandidat baru, 0 eksekusi, 0 preview."
)
json.dump(s, open(P, "w"), indent=1)
print("snapshot updated; contracts:", len(s["contracts"]))
