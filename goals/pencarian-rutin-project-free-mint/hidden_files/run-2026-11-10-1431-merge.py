#!/usr/bin/env python3
"""Merge run 1431 reread+vel into snapshot + pending-swaps WNO.
Main events: WNO track-C lead DIRECT MINT (1 share -> 1.000.000 WNO, tx verified);
SEVENFOLD new candidate legs pass but AUDIT-BLOCKED (MORROW HIGH RISK, fresh audit);
Orbit Signal + Claf Eye EARLY leads baru; AgenticGangsterNFT free pool sold out.
Does NOT re-report anything (reporting is the parent run's final message)."""
import json, shutil, copy
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TS = "2026-11-10-1431"
BLOCK = 132739023
NOW = "2026-11-10 14:31 WIB"
snap = json.load(open(f"{BASE}/onchain-snapshot.json"))
rr = json.load(open(f"{BASE}/run-{TS}-reread.json"))
vel = json.load(open(f"{BASE}/run-{TS}-vel.json"))
shutil.copy(f"{BASE}/onchain-snapshot.json", f"{BASE}/onchain-snapshot.json.bak-1431-premerge")

updated = 0
for name, entry in snap.get("contracts", {}).items():
    if not isinstance(entry, dict):
        continue
    f = rr.get("reread", {}).get(name)
    if not f:
        continue
    row = vel.get("rows", {}).get(name, {})
    for k in ("totalSupply", "totalMinted", "freeClaimed", "freeMinted", "FREE_SUPPLY",
              "MAX_SUPPLY", "mintOpen", "balanceOf_user", "freeClaimed_user"):
        if f.get(k) is not None:
            entry[k] = f[k]
    entry["lastReadBlock"] = BLOCK
    entry["lastReadWib"] = NOW
    if row.get("minted") is not None:
        entry["previousTotalSupply"] = row.get("prev")
        entry["mintedInInterval"] = row.get("minted")
        entry["intervalMinutes"] = 30.0
        entry["currentRatePerMin"] = row.get("rate")
        entry["velocityRatio"] = row.get("ratio")
        entry["velocityLegPasses"] = row.get("passes")
    updated += 1

def note(name, text):
    e = snap["contracts"].get(name)
    if isinstance(e, dict):
        e["runNote1431_1110"] = text

def dyn_note(name, extra=""):
    row = vel.get("rows", {}).get(name, {})
    f = rr.get("reread", {}).get(name, {})
    e = snap["contracts"].get(name, {})
    if not row:
        return None
    minted = row.get("minted"); rate = row.get("rate"); ratio = row.get("ratio")
    passes = row.get("passes")
    fm = f.get("freeMinted"); fc = f.get("freeClaimed")
    cap = e.get("FREE_SUPPLY") or e.get("FREE_CAP") or e.get("agentFreeCap") or e.get("MAX_SUPPLY")
    freetxt = ""
    if fm is not None and cap:
        freetxt = f"; freeMinted {fm}/{cap} = {fm/cap*100:.1f}%"
    elif fc is not None and cap:
        freetxt = f"; freeClaimed {fc}/{cap} = {fc/cap*100:.1f}%"
    vtxt = "velocity LOLOS" if passes else "velocity GAGAL"
    return (f"Run 1431 (blok {BLOCK}): totalSupply {row.get('prev')}->{row.get('new')} "
            f"(+{minted}, {rate}/mnt vs prev {row.get('prev_rate')} = {ratio}x) {vtxt}{freetxt}; "
            f"bal_user={f.get('balanceOf_user')}; status {e.get('status')}.{extra}")

# ---- SEVENFOLD: candidate legs pass, audit-blocked ----
sev = snap["contracts"]["SEVENFOLD"]
sev["freePctVerified"] = round(1703/3000*100, 1)  # 56.8; snapshot 49.6 was stale (freeMinted 1488 era)
sev["freePctNote"] = "Recompute run 1431: freeMinted segar 1703 / agentFreeCap 3000 = 56,8% (nilai snapshot 49,6% basi dari freeMinted 1488)."
sev["status"] = "candidate-reported-2026-11-10-audit-blocked"
sev["auditNote1431"] = ("Binance audit segar run 1431: sale 0x4ca724a354db4f743607ecc1a5f117b2e617c8ae hasResult=false "
    "(tanpa hasil, bukan lolos); token MORROW 0x1f4e976b899df67cB4F69BB21aFa0Aee274153Fe hasResult=true, riskLevel 4 HIGH, "
    "RISK hit 'High Risk Found' isHit=true + CAUTION 'Contract Code Not Verified' + 'Newly Created Token'; tax 0/0.")
sev["velocityVerified"] = True
note("SEVENFOLD", (dyn_note("SEVENFOLD") or "") +
     " KANDIDAT BARU run ini (free 1703/3000 = 56,8% >=50% + velocity LOLOS 5,99x/39 token + umur TERVERIFIKASI mintStart 2026-11-10 07:33:08 WIB "
     "+ website TERVERIFIKASI + slot user TERBUKA segar (mintedBy=0, freeUsedByWallet=0, bal=0) + diskusi Boltbook angka live) TAPI MINT DIBLOKIR audit: "
     "token MORROW riskLevel 4 HIGH, RISK hit 'High Risk Found' (audit segar run 1431). TIDAK preview/mint. Status diubah ke candidate-reported-2026-11-10-audit-blocked.")
note("THYRK", (dyn_note("THYRK") or "") + " Sudah minted-by-user (#6849 run 1231 + 20 THYRK pending swap) -> velocity lolos tidak relevan, TANPA promosi.")
note("DRIFTWIRE", (dyn_note("DRIFTWIRE") or "") + " Sudah minted-by-user (#745 run 1231) -> velocity lolos tidak relevan, TANPA promosi.")
note("Rose Genesis", (dyn_note("Rose Genesis") or "") + " TANPA promosi: umur UNVERIFIED + free path UNVERIFIED (tanpa free views) + xVerified false -> tetap watchlist-only-mature-newly-noticed.")
note("Cinder Agents", (dyn_note("Cinder Agents") or "") + " Tetap early lead (freeMinted 100/500 = 20,0% <25% + umur unverified + website belum dinilai).")
note("Pickgrid Pickaxe", (dyn_note("Pickgrid Pickaxe") or "") + " Tetap early lead (freeMinted 142 = totalSupply 142; free cap tidak terverifikasi -> free% UNVERIFIED; umur + website unverified).")
note("PanduAGENT Phase 2", (dyn_note("PanduAGENT Phase 2") or "") + " Tetap early lead (freeMinted 224 = totalSupply 224; free% UNVERIFIED; umur + website unverified).")
note("Arcane Stones", (dyn_note("Arcane Stones") or "") + " Tetap early lead (free views None -> free% UNVERIFIED; umur UNVERIFIED; website terverifikasi; slot terbuka bal=0).")
note("Forge Pass", (dyn_note("Forge Pass") or "") + " Tetap early lead (freeMinted 508/20000 = 2,5% <25%; umur + website UNVERIFIED). Velocity LOLOS run ini tapi % jauh di bawah ambang strong lead.")
note("Golden Agents", (dyn_note("Golden Agents") or "") + " Tetap early lead (free views None -> free% UNVERIFIED; umur + website UNVERIFIED). Velocity LOLOS run ini.")
note("SonoWaves", (dyn_note("SonoWaves") or "") + " Tetap watchlist-only-age-unverified (freeMinted 219/2260 = 9,7% <25%). Velocity LOLOS run ini.")
note("BN Agent File", (dyn_note("BN Agent File") or "") + " Tetap watchlist-only-mature-newly-noticed (totalSupply gagal baca run ini; free% UNVERIFIED). Velocity LOLOS dari totalMinted.")
note("Orbit Atlas", (dyn_note("Orbit Atlas") or "") + " Tetap watchlist-only-unverified (totalSupply 236->412, +176; free views None; umur + website + agent-shape UNVERIFIED).")
note("ELSY AGENT", (dyn_note("ELSY AGENT") or "") + " Pasca-mint terverifikasi: bal_user=2 (#880/#881), totalSupply 881->1049. TIDAK di-auto-list (own market tidak live).")
note("HIVE Agents", (dyn_note("HIVE Agents") or "") + " Minted-by-user; tanpa perubahan.")

# ---- AgenticGangsterNFT: free pool sold out 111/111 -> excluded ----
gang = snap["contracts"].pop("AgenticGangsterNFT", None)
if gang is not None:
    gang["status"] = "excluded-free-sold-out-2026-11-10"
    gang["runNote1431_1110"] = ("Run 1431: free pool HABIS 111/111 (run 1401: 69/111; totalSupply 70->116, +46 dalam 30 mnt, 5 di antaranya paid). "
        "Status sebelumnya watchlist-only-age-unverified-2026-11-09 (umur UNVERIFIED + freeMint butuh EIP-712 challenge server). "
        "Perubahan dilaporkan sekali run ini; entri dipindah ke excluded.")
    snap.setdefault("excluded", {})["AgenticGangsterNFT"] = gang

# ---- Orbit Signal: EARLY lead baru ----
snap["contracts"]["Orbit Signal"] = {
    "address": "0x32ef9524771fac05585af142702e4d7a6b5f7ad9",
    "status": "early-lead-reported-2026-11-10",
    "name": "Orbit Signal", "symbol": "CO06", "kind": "ERC721",
    "totalSupply": 324, "MAX_SUPPLY": 995, "MAX_PER_WALLET": 10,
    "mintOpen": 1, "price": 50000000000000,
    "costOf_user_1": 0, "mintedBy_user": 0, "balanceOf_user": 0,
    "owner": "0x3fBE2B54baF80D33E2Ef6E46Cb972959536Eca17",
    "treasury": "0x3fBE2B54baF80D33E2Ef6E46Cb972959536Eca17",
    "freePctVerified": None,
    "freePctNote": "UNVERIFIED: tanpa free view (tanpa freeMinted/freeClaimed/FREE_SUPPLY); 324/995 = 32,6% adalah % total-supply, BUKAN % kuota gratis.",
    "xVerified": False, "velocityVerified": False,
    "launchNote": "Umur UNVERIFIED: Sourcify verifiedAt 2026-11-10T02:39:54Z (09:39 WIB); postingan Boltbook pertama ~14:41-14:45 WIB hari ini; first-mint block belum dibaca (Ankr 401 + getLogs -32005).",
    "baselineNote": ("EARLY lead run 1431 (Boltbook front page, post tale.ai / grandtheftauto6.ai / quyennuong.ai ~14:41-14:45 WIB; "
        "totalSupply 317/995 saat post, 324 saat verifikasi parent; +33 dalam 102 mnt). Agent-shaped: Sourcify exact_match, "
        "mintWithAgentTokenId + agentIds + agentTokenIdOf. Slot user terbuka (costOf(user,1)=0, mintedBy=0). Owner 0x3fBE... TIDAK di discards. "
        "Website/umur/free% UNVERIFIED -> EARLY only, TIDAK preview/mint. Promosi ke strong lead bila 3 kaki terpenuhi."),
    "lastReadBlock": BLOCK, "lastReadWib": NOW,
    "currentRatePerMin": None, "velocityLegPasses": False,
}

# ---- Claf Eye: EARLY lead baru ----
snap["contracts"]["Claf Eye"] = {
    "address": "0x1c759c4e075103b5b250db5114b832b17b99c456",
    "status": "early-lead-reported-2026-11-10",
    "name": "The Claf Eye", "symbol": "EYE", "kind": "ERC721",
    "totalSupply": 2730, "MAX_SUPPLY": 18000, "MAX_PER_WALLET": 30,
    "costFor_user_1": 0, "mintedBy_user": 0, "balanceOf_user": 0,
    "PRICE_FIRST": 300000000000000, "PRICE_2_10": 300000000000000,
    "agentRegistry": "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F",
    "owner": "0x99990955d75409786f58ac9fea5bf62571b51fe1",
    "treasury": "0x1950cd97e13cdee606764fd253ee6bb89fa8be2b",
    "website": "https://claf.markets", "x": "https://x.com/clafmarkets",
    "freePctVerified": None,
    "freePctNote": "UNVERIFIED: tanpa free view; 2730/18000 = 15,2% adalah % total-supply, BUKAN % kuota gratis. (Post Boltbook menyebut 611 saat post; bacaan segar parent 2730 — angka post basi/tertinggal.)",
    "xVerified": False, "velocityVerified": False,
    "launchNote": "Umur UNVERIFIED: post Boltbook menyebut launched 06:45 UTC (13:45 WIB) hari ini — belum koroborasi on-chain (Ankr 401 + getLogs -32005).",
    "websiteNote": ("Website UNVERIFIED: WEBSITE() on-chain = https://claf.markets + contractURI metadata menyebut situs + X, TAPI homepage claf.markets "
        "(14.352 byte) TIDAK mencetak kontrak EYE; /llms.txt + /skill.md mengembalikan fallback HTML SPA. Metode (J) gagal: URL ada, situs tidak mencetak kontrak."),
    "baselineNote": ("EARLY lead run 1431 (Boltbook front page, post bunnysuny.ai; totalSupply 611/18000 saat post, 2730 saat verifikasi parent). "
        "Agent-shaped: Sourcify exact_match, agentRegistry() = registry persis + hasAgentId. Slot user terbuka (costFor(user,1)=0, mintedBy=0). "
        "Owner 0x9999... TIDAK di discards. Website/umur/free% UNVERIFIED -> EARLY only, TIDAK preview/mint."),
    "lastReadBlock": BLOCK, "lastReadWib": NOW,
    "currentRatePerMin": None, "velocityLegPasses": False,
}

# ---- WNO -> track_c minted ----
snap.setdefault("track_c", {})["WNO"] = {
    "sale": "0x8C969a4CD49E4774908e667702C3d7C3ece164D0",
    "token": "0x8C969a4CD49E4774908e667702C3d7C3ece164D0",
    "name": "War Need Over", "symbol": "WNO", "kind": "ERC20-sale-S1",
    "status": "minted-by-user-2026-11-10",
    "saleShape": ("PASS (S1): mint(uint256,address) + quote(address,uint256)->(cost,freeShares,paidShares) + free views "
        "(FREE_SHARES/totalFreeShares/freeUsed) + registry() = 0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F, Sourcify exact_match (verifiedAt 2026-11-09T16:40:24Z)"),
    "website": "https://warneedover.netlify.app/",
    "site": "https://warneedover.netlify.app/",
    "mintTx": "0xbcaf2ff53785ae3c595d7ccfc9e817404822d9957e91f5ea647b6c7c807712a3",
    "mintBlock": 132743227, "mintGas": 122283,
    "FREE_SHARES": 3000, "MAX_SHARES": 6000, "MAX_PER_TX": 20,
    "TOKENS_PER_SHARE": "1000000000000000000000000", "PRICE": "1000000000000000",
    "freeRemaining_at_mint": 2437, "totalFreeShares_at_mint": 563,
    "quote_user_1": 0, "freeUsed_user": 1, "sharesOf_user": 1, "balanceOf_user": 1000000000000000000000000,
    "launchNote": ("Umur TERVERIFIKASI (bounded): Sourcify verifiedAt 2026-11-09 23:40 WIB + pengumuman launch The Colony 2026-11-10 10:56 WIB "
        "oleh deployer sendiri ('I wrote the contract and deployed it', 416 share claimed saat post) + freeSold 416->563 koroborasi on-chain. "
        "Blok first-mint TIDAK terbaca run ini: BscScan fetch 403 + browser bot-wall + Etherscan V2 tidak dukung BSC gratis + BscScan API proxy-HTML + eth_getLogs -32005 (NodeReal/dataseed)."),
    "auditNote1431": ("Binance audit segar run 1431: hasResult=true, riskLevel 2 LOW, isVerified=true, tax 0/0, 0 hit RISK "
        "(hanya CAUTION 'Newly Created Token'). Preview bersih (simulationCode 000000000, balance +1e24 WNO, tanpa allowance/authority/risk)."),
    "baselineNote": ("TRACK-C LEAD DIRECT MINT run 1431 (The Colony post 10:56 WIB; 1 share gratis -> 1.000.000 WNO, tx 0xbcaf2ff53785ae3c595d7ccfc9e817404822d9957e91f5ea647b6c7c807712a3, "
        "blok 132743227, gas 122283, receipt 1; verifikasi: balance 0->1e24, sharesOf 0->1, freeUsed 0->1). Website gate LOLOS (llms.txt + homepage mencetak kontrak + registry persis). "
        "Same-owner-discards BERSIH (kontrak + treasury 0x8d57... tidak ada di discards). Pair PCS V2 WNO/WBNB + WNO/USDT = 0x0 (belum ada) -> TIDAK bisa swap; "
        "didaftarkan ke pending-swaps.json (delta 1.000.000 WNO) untuk pantauan open trade. Marketplace/rarity TIDAK berlaku (bukan NFT)."),
    "lastReadBlock": BLOCK, "lastReadWib": NOW,
}

# ---- track_c lastRead updates + notes ----
for name, entry in snap.get("track_c", {}).items():
    if not isinstance(entry, dict):
        continue
    if name in rr.get("track_c", {}):
        entry["lastReadBlock"] = BLOCK
        entry["lastReadWib"] = NOW
tc = snap.get("track_c", {})
if isinstance(tc.get("YAMA"), dict):
    tc["YAMA"]["runNote1431_1110"] = ("Run 1431: baca ulang track_c GAGAL lagi (semua view null, sama seperti run 1401 — degradasi transport, BUKAN nol). "
        "Status lead-reported-audit-blocked-2026-11-10 dipertahankan; deadline umur ~15:18 WIB hari ini. TIDAK preview/mint.")
if isinstance(tc.get("NUSA"), dict):
    tc["NUSA"]["runNote1431_1110"] = ("Run 1431: freeMinted 370 (tetap vs run 1401), freeClaimed(user)=0, gate FAILED (website tidak terverifikasi), deadline 17:05 WIB hari ini. TIDAK ada perubahan; TIDAK preview/mint.")
if isinstance(tc.get("FOUNT"), dict):
    tc["FOUNT"]["runNote1431_1110"] = "Run 1431: freeMinted 1000 (tetap), totalSupply 1e27, bal_user=0. Tetap watchlist-only-boltbook; umur UNVERIFIED. TIDAK ada perubahan."

snap["last_run"] = 1
snap["last_run_wib"] = NOW
snap["last_run_note"] = ("Run 1431: re-read 656 kontrak + 75 track_c (696,8 dtk, blok 132739023). Velocity LOLOS 8 (Golden Agents, AgenticGangsterNFT, "
    "BN Agent File, THYRK, SEVENFOLD, SonoWaves, DRIFTWIRE, Forge Pass) — tanpa promosi kecuali SEVENFOLD (kandidat baru, audit-blocked). "
    "MINT 1: WNO track-C lead direct mint (1 share -> 1.000.000 WNO, tx 0xbcaf2f...712a3, blok 132743227, gas 122283, receipt 1). "
    "EARLY LEAD BARU 2: Orbit Signal + Claf Eye. SELLOUT 1: AgenticGangsterNFT 111/111 -> excluded. "
    "Scan fast-fail Ankr 401 (preflight 4,3 dtk); watermark TIDAK dimajukan. Feed Sourcify 20/20, 0 S1/0 S2. "
    "binanceai.fun tetap refund/failed (sudah dilaporkan sekali). Bridge: 3 kontrak, semua sudah di snapshot.")
snap["runNote1431_1110"] = (
    "Run 1431 (2026-11-10 14:31-~15:35 WIB, blok 132739023, interval 30 mnt vs run 1401): re-read 656 kontrak + 75 track_c (696,8 dtk). "
    "Velocity LOLOS: ['Golden Agents', 'AgenticGangsterNFT', 'BN Agent File', 'THYRK', 'SEVENFOLD', 'SonoWaves', 'DRIFTWIRE', 'Forge Pass'] — "
    "tanpa promosi kecuali SEVENFOLD (lihat bawah). "
    "TRACK-C LEAD DIRECT MINT 1: War Need Over (WNO) 0x8C969a4CD49E4774908e667702C3d7C3ece164D0 — 1 share gratis -> 1.000.000 WNO, "
    "tx 0xbcaf2ff53785ae3c595d7ccfc9e817404822d9957e91f5ea647b6c7c807712a3, blok 132743227, gas 122283, receipt status 1, verifikasi on-chain lengkap "
    "(balance 0->1e24, sharesOf 0->1, freeUsed 0->1, totalFreeShares 563->564). S1 PASS + website gate LOLOS (llms.txt/homepage mencetak kontrak+registry) + "
    "audit LOW 0 RISK hit + quote 0 segar + preview bersih + discards bersih + sesi baw login. Umur bounded (verifiedAt 2026-11-09 23:40 WIB + pengumuman The Colony "
    "2026-11-10 10:56 WIB; blok first-mint tidak terbaca: BscScan 403/bot-wall, Ankr 401, getLogs -32005). Pair PCS V2 belum ada (WBNB/USDT = 0x0) -> TIDAK swap; "
    "WNO didaftarkan pending-swaps.json (delta 1.000.000). "
    "KANDIDAT BARU (audit-blocked): SEVENFOLD — free 1703/3000 = 56,8% + velocity LOLOS 5,99x + umur terverifikasi (mintStart 2026-11-10 07:33:08 WIB) + website "
    "terverifikasi + slot terbuka + diskusi Boltbook angka live; TAPI audit segar: token MORROW riskLevel 4 HIGH, RISK hit 'High Risk Found' -> TIDAK preview/mint. "
    "EARLY LEAD BARU 2 (Boltbook): Orbit Signal 0x32ef9524771fac05585af142702e4d7a6b5f7ad9 (324/995, costOf 0, agent-shaped exact_match; umur/free%/website UNVERIFIED) + "
    "Claf Eye 0x1c759c4e075103b5b250db5114b832b17b99c456 (2730/18000, costFor 0, agentRegistry persis, WEBSITE()/X() on-chain tapi situs tidak mencetak kontrak -> website UNVERIFIED). "
    "Forge Pass sudah early-lead-reported (hot leg) — BUKAN temuan baru run ini; tetap early (2,5%). NovaAgent tetap watchlist-only-unverified (free views revert, tanpa Transfer logs; klaim Boltbook 98% tak terverifikasi). "
    "Mechfarm 0x1fab... tetap strong-lead-gate-failed (website gagal; tanpa bukti website baru). "
    "SELLOUT 1: AgenticGangsterNFT free 111/111 (run 1401: 69/111) -> dipindah ke excluded, dilaporkan sekali. "
    "YAMA: baca ulang GAGAL lagi (semua null); audit-blocked dipertahankan; deadline umur ~15:18 WIB hari ini. NUSA: freeMinted 370 tetap, gate FAILED, deadline 17:05 WIB. "
    "FOUNT: freeMinted 1000 tetap. Cinder 20,0% / Pickgrid free% unverified / PanduAGENT free% unverified / Arcane Stones free% unverified — semua tetap early. "
    "ELSY pasca-mint: bal_user=2 terverifikasi. binanceai.fun tetap refund/failed (sudah dilaporkan sekali). Bridge: 3 kontrak, semua sudah di snapshot, tanpa temuan pelengkap baru. "
    "Scan: preflight GAGAL Ankr 401 (4,3 dtk) -> fast-fail; watermark TIDAK dimajukan; gap ke head tidak dicatat sebagai backfill (backfill nonaktif). "
    "Feed Sourcify 20/20 dicek, 0 S1/0 S2. Boltbook EN 45.771 B (fetch ulang parent ~15:3x WIB; SEVENFOLD sudah tidak di front page saat itu — bukti diskusi dari sapuan route 2 subagent). "
    "Route 6: Square tanpa lead baru; Odaily/PANews tanpa pengumuman Agent ID/free-mint; DappBay tidak dipakai (tidak ada kandidat yang membutuhkan). "
    "Subagent B (verifikasi item live) selesai tapi laporan lengkapnya tidak tiba sebagai handoff ke parent; semua itemnya sudah diverifikasi independen oleh parent dari reread/audit segar.")

json.dump(snap, open(f"{BASE}/onchain-snapshot.json", "w"), indent=1)
print("SNAPSHOT WRITTEN. contracts:", len(snap.get("contracts", {})), "track_c:", len(snap.get("track_c", {})),
      "excluded:", len(snap.get("excluded", {})))

# ---- pending-swaps: append WNO ----
ps_path = "/home/hatch/workspace/asset-sell-watch/pending-swaps.json"
ps = json.load(open(ps_path))
entries = ps["entries"]
if any(e.get("symbol") == "WNO" for e in entries):
    print("WNO already in pending-swaps, skipped")
else:
    entries.append({
        "token": "0x8C969a4CD49E4774908e667702C3d7C3ece164D0",
        "symbol": "WNO",
        "sale_contract": "0x8C969a4CD49E4774908e667702C3d7C3ece164D0",
        "amount_human": 1000000,
        "amount_to_sell_raw": "1000000000000000000000000",
        "decimals": 18,
        "reason": "no_pair",
        "open_condition": "PCS V2 pair WNO/WBNB terbentuk + cadangan likuiditas > 0 + quote >= 2x gas + guard swap penuh",
        "registered_at": "2026-11-10 ~15:30 WIB",
        "last_update": "2026-11-10",
        "notes": ("Mint gratis 1 share track-C lead direct mint run free-mint-search 1431 (tx 0xbcaf2ff53785ae3c595d7ccfc9e817404822d9957e91f5ea647b6c7c807712a3, "
            "blok 132743227, receipt 1, gas 122283). Hanya delta 1.000.000 WNO hasil mint ini yang dijual. Audit Binance saat mint: hasResult=true, riskLevel 2 LOW, "
            "isVerified=true, tax 0/0, 0 hit RISK (hanya CAUTION Newly Created Token). Preview bersih (simulationCode 000000000, balance +1e24). "
            "Pair PCS V2 WNO/WBNB + WNO/USDT = 0x0 saat cek (belum ada pair) — situs/post menyebut '$WNO has no market yet'. "
            "Free pool saat mint: 2.437/3.000 tersisa; sale tetap buka (MAX_SHARES 6000). Monitor wajib cek pair + quote + transferability segar sebelum eksekusi."),
    })
    json.dump(ps, open(ps_path, "w"), indent=1)
    print("WNO appended to pending-swaps. total entries:", len(entries))
print("MERGE DONE")
