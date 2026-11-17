#!/usr/bin/env python3
"""Merge run 1001 (2026-11-08) results into snapshot / seen / tc-checked.
Tailored for this run: generic reread+velocity update, TWO new entries
(Zigzoo early lead via Boltbook; NovaAgent watchlist-only-unverified),
5c merge. SCAN WAS PARTIAL (timeout 700s at enrich 103/156) -> watermark
NOT advanced (rule: scan gagal -> watermark tidak maju). Preserves all
existing snapshot keys. Run once."""
import json, datetime, shutil

HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
WIB = datetime.timezone(datetime.timedelta(hours=7))
NOW = datetime.datetime.now(WIB).strftime("%Y-%m-%d %H:%M:%S WIB")

for f in ("onchain-snapshot.json", "onchain-scan-seen.json", "onchain-scan-state.json"):
    shutil.copy(f"{HF}/{f}", f"{HF}/{f}.bak-1001")
print("backups written .bak-1001")

snap = json.load(open(f"{HF}/onchain-snapshot.json"))
rr = json.load(open(f"{HF}/run-2026-11-08-1001-reread.json"))
vv = json.load(open(f"{HF}/run-2026-11-08-1001-velocity.json"))
scan = json.load(open(f"{HF}/onchain-scan-2026-11-08-1001.json"))
seen = json.load(open(f"{HF}/onchain-scan-seen.json"))
state = json.load(open(f"{HF}/onchain-scan-state.json"))
tc = json.load(open(f"{HF}/track-c-scan-checked.json"))
f5 = json.load(open(f"{HF}/run-2026-11-08-1001-5c.json"))

REREAD_BLOCK = rr["block"]
contracts = snap["contracts"]

# ---- 1. reread + velocity update for existing entries ----
vel_by_addr = {}
for row in vv.get("rows", []):
    a = (row.get("address") or "").lower()
    if a:
        vel_by_addr[a] = row

updated = 0
for key, entry in contracts.items():
    row = rr["reread"].get(key)
    if row:
        if row.get("totalSupply") is not None:
            entry["totalSupply"] = row["totalSupply"]
        for f in ("totalMinted", "freeClaimed", "freeMinted", "FREE_SUPPLY",
                  "MAX_SUPPLY", "mintOpen", "freeClaimed_user", "balanceOf_user"):
            if row.get(f) is not None:
                entry[f] = row[f]
        entry["lastReadBlock"] = REREAD_BLOCK
        entry["lastReadWib"] = "2026-11-08 run 1001"
        updated += 1
    vrow = vel_by_addr.get((entry.get("address") or "").lower())
    if vrow:
        cur = vrow.get("curSupply")
        if cur is not None:
            entry["previousTotalSupply"] = vrow.get("prevSupply")
            entry["currentRatePerMin"] = vrow.get("ratePerMin")
            entry["previousRatePerMin"] = vrow.get("prevRatePerMin")
            entry["velocityRatio"] = vrow.get("ratioVsPrev")
            entry["run1001_velocity"] = (
                f"Run 1001 (blok {REREAD_BLOCK}, interval {vrow.get('intervalMin')} mnt): "
                f"{vrow.get('prevSupply')}->{cur} (+{vrow.get('mintedInInterval')}, "
                f"{vrow.get('ratePerMin')}/mnt vs prev {vrow.get('prevRatePerMin')} = "
                f"{vrow.get('ratioVsPrev')}x) -> velocity "
                f"{'LOLOS' if vrow.get('passes') else 'GAGAL'}."
            )
        else:
            entry["run1001_velocity"] = (
                f"Run 1001 (blok {REREAD_BLOCK}): no fresh supply read "
                f"(degradasi RPC) - nilai lama dipertahankan, BUKAN perubahan state."
            )
print("reread-updated entries:", updated)

# ---- 1b. track_c fresh reads (totalSupply + lastRead only) ----
tc_updated = 0
for key, entry in snap.get("track_c", {}).items():
    if not isinstance(entry, dict):
        continue
    row = rr.get("track_c", {}).get(key)
    if row and row.get("totalSupply") is not None:
        entry["totalSupply"] = row["totalSupply"]
        entry["lastReadBlock"] = REREAD_BLOCK
        entry["lastReadWib"] = "2026-11-08 run 1001"
        tc_updated += 1
print("track_c updated:", tc_updated)

# ---- 2a. new entry: Zigzoo (EARLY LEAD, Boltbook discovery) ----
contracts["Zigzoo"] = {
    "address": "0x09ada5a12293c30d75b97c56e34967e8a4326a3c",
    "status": "early-lead-reported-2026-11-08",
    "name": "Zigzoo",
    "symbol": "ZIGZOO",
    "kind": "ERC721",
    "totalSupply": 1047,
    "freeClaimed": None,
    "FREE_SUPPLY": None,
    "MAX_SUPPLY": 5000,
    "freePctVerified": None,
    "mintOpen": 1,
    "mintActive": 1,
    "currentPrice": 0,
    "priceFor_user": 0,
    "userBalance": 0,
    "mintCount_user": 0,
    "holdsAgentId_user": 1,
    "userSlotNote": "Slot open by read: balanceOf(user)=0, mintCount(user)=0, priceFor(user)=0, holdsAgentId(user)=1, mintActive=1, currentPrice=0 - NOT preview-verified (early leads are never previewed).",
    "firstSeenBlock": 132019038,
    "discovery": "Boltbook post 2026-11-08 ~10:08 WIB (NEW verified free lane) + on-chain triage run 1001",
    "lastReadBlock": 132319156,
    "lastReadWib": "2026-11-08 run 1001 (triage)",
    "xVerified": False,
    "velocityVerified": False,
    "launchNote": "First mint verified on-chain: first Transfer-from-zero at block 132019038, 2026-11-06 20:45:29 WIB (Ankr getLogs address-filtered, probed back to an empty window; timestamp via fast_rpc, NOT Ankr). Age ~37,6h at triage -> VERIFIED <=48h (age-excludes 2026-11-08 20:45:29 WIB if not sold out). No project-stated launch time found; Sourcify verifiedAt 2026-11-06T13:28:21Z (verification time, NOT launch time). First READ by this job in run 1001 (Boltbook route). NOTE: contract was already in onchain-scan-seen.json since Nov 6 block 132006885 (deployment-seen by an earlier scan) but was NEVER triaged or reported before - no prior snapshot entry, no prior report - so this is its first report, not a duplicate.",
    "baselineNote": "EARLY lead reported once 2026-11-08 run 1001. Never auto-minted/previewed. Agent-shape verified: Sourcify verified 'match' (partial, not exact) ABI 47 fns (agentIdRegistry, holdsAgentId, DEFAULT_AGENT_ID_REGISTRY, mint() no-arg, mintActive, currentPrice, priceFor/priceForCount) + registry ref in ABI text. Owner 0x262e8e5e4584d8ab840fd950a6e2e0a414d4097 - absent from snapshot and same-owner discards. free% UNVERIFIED: no global free counter readable (no freeClaimed/freeMinted/FREE_SUPPLY/freeLeft views in ABI; all revert). Website gate UNVERIFIED (methods A-K,M,N tried, see runNote1001). Promotes to strong lead only on all 3 strong-lead legs; to candidate only on ALL criteria + safety.",
    "freePctNote": "UNVERIFIED: totalSupply 1047/5000 (Boltbook post said 1.045 at ~10:08 WIB; fresh triage read 1047). No readable global free counter; priceFor(user)=0, mintCount(user)=0.",
    "runNote1001": "Run 1001: EARLY LEAD (temuan Boltbook, first-read job ini). First mint 2026-11-06 20:45:29 WIB, totalSupply 1047, agent-shaped, free% unverified, website gate unverified, slot terbuka. Dilaporkan sekali sebagai EARLY, TIDAK di-preview/di-mint.",
}

# ---- 2b. new entry: NovaAgent (watchlist-only, UNVERIFIED) ----
contracts["NovaAgent"] = {
    "address": "0xa6909af663637cd988e712efbc2e73f7076d9154",
    "status": "watchlist-only-unverified-2026-11-08",
    "name": "NovaAgent",
    "symbol": None,
    "kind": "ERC721",
    "totalSupply": 4900,
    "totalMinted": 4900,
    "freeClaimed": None,
    "FREE_SUPPLY": None,
    "MAX_SUPPLY": 5000,
    "freePctVerified": None,
    "mintOpen": None,
    "userBalance": 0,
    "firstSeenBlock": None,
    "discovery": "Boltbook post 2026-11-08 10:07 WIB (4.900/5.000 free, 98%) + on-chain triage run 1001",
    "lastReadBlock": 132320064,
    "lastReadWib": "2026-11-08 run 1001 (triage)",
    "xVerified": False,
    "velocityVerified": False,
    "launchNote": "First mint UNVERIFIED: ZERO Transfer-from-zero logs in Ankr getLogs [130000000, 132320064] (~12 hari) AND zero TransferSingle logs in last 100k blocks, despite totalSupply 4900/5000 - mint history cannot be established. Sourcify http-404 (UNVERIFIED). No global free counter / quote / freeLeft functions (all revert on eth_call). Boltbook post claims 4.900/5.000 free (98%), 100 slots left, risk_level=high. Age UNVERIFIED -> NOT a lead/candidate until first mint verified <=48h. AGENT_ID() returns template constant 552192074493313695968015109214105588393044541999 (same as Chromeshade/Ninetailix template) but no registry-bytes hit and no verified ABI -> agent-shape NOT established.",
    "baselineNote": "Watchlist-only-unverified, added run 1001. Never reported as lead, never previewed/minted. Routes tried: Sourcify (404), Ankr getLogs Transfer + TransferSingle deep probe to block 130000000, template views (quote/freeLeft/freeClaimed/FREE_SUPPLY all revert). Stays on active unverified list; promote only if first mint + free% + slot verify.",
    "runNote1001": "Run 1001: watchlist-only-unverified (Boltbook claim 98% free tidak terverifikasi on-chain: first mint tidak ditemukan dalam 12 hari log, Sourcify unverified).",
}

# ---- 3. run notes ----
snap["runNote1001"] = (
    "Run 1001 (2026-11-08, blok reread 132318075, 707,6 dtk): reread 471 kontrak + 70 track_c; "
    "velocity 5 pass (Alchemister-0xCafEEDDF 4,28x +109; BOT-UNIT 1,89x +70; Gourdmare 3,13x +29; "
    "Vesperfang 2,70x +25; UNKNOWN-1Aeb 3,17x +22) tapi 0 promotable (free% unverified atau "
    "same-owner-discarded); soldOut 35 (set sama dengan run 0931, tanpa sellout baru); slotChanged 0. "
    "Age-sweep: remove=0, kept=56, unverified-launch=409. "
    "Track B binanceai tidak berubah (launched=0, failed=1, isRefundPhase=1, tokenClaimed_user=0, "
    "balance 0; sudah dilaporkan run 1701 2026-11-07). "
    "Boltbook EN+ZH: Zigzoo BARU (early lead, lihat runNote1001 Zigzoo); Chromeshade first mint "
    "2026-11-02 15:52:35 WIB -> AGE-EXCLUDED (>48h, 374/867 free 43,1%), tidak masuk snapshot, "
    "tidak dilaporkan; Ninetailix free pool HABIS (freeClaimed 518/518 FREE_SUPPLY, quote(user,1) "
    "0,00005 BNB, freeLeft(user)=0) -> bukan lead, tidak dilaporkan; NovaAgent unverified "
    "(watchlist-only); Voltoad age-excluded (tidak di-add lagi); PAWG 1.624/1.667 (early-lead-2026-11-07, "
    "free% unverified, tanpa perubahan); Deltavane 1.247/2.314 menurut post (watchlist-only, free% "
    "unverified on-chain, tanpa perubahan); WAR3 2.562/7.777; DinoAgent 777/777 sold out (sudah "
    "dilaporkan). Feed Sourcify: 4 kontrak (sama seperti run 0931), semuanya gagal S1/S2. "
    "Odaily newsflash EN: tidak ada item Agent-ID free-mint. Bridge: 115 kontrak, mtime 2026-11-06 "
    "02:48 UTC, tidak ada entri baru. Web sweep EN+ZH: hanya item lama (Substack 22 proyek, "
    "AgentForge 27 Okt, Pixel Fox 25 Okt, Laser Agents, AGENT MAO paused) - tidak ada proyek baru. "
    "EARLY LEAD x1: Zigzoo 0x09ada5a12293c30d75b97c56e34967e8a4326a3c (first mint 2026-11-06 20:45:29 WIB, "
    "totalSupply 1047, agent-shaped, free% unverified, website gate unverified, slot terbuka). "
    "Gate Zigzoo methods tried: (A) address search tanpa hit; (B) Boltbook posts tanpa link situs; "
    "(C) Sourcify metadata tanpa URL; (D) pola same-family tanpa hit; (G) name search tanpa situs proyek; "
    "(H) contractURI tidak ada di ABI; (I) tokenURI(1) revert, baseURI kosong; (J) ABI grep tanpa "
    "fungsi situs; (K) GitHub search-index absence saja (true code search butuh auth); (M) site: "
    "filters tanpa hit; (N) registry-profile hop tidak applicable. X: tidak ditemukan (opsional).")
snap["runNote1001_scan"] = (
    "Run 1001 SCAN PARTIAL (partial=true): pre-flight OK 10,0 dtk (head 132320568, 194 logs/50 blok). "
    "Window 132319880-132320879 (1000 blok, cap) - chunks 20/20 selesai TAPI enrichment terhenti di "
    "103/156 oleh timeout 700 dtk (SCAN_EXIT=124 via timeout). 40 panggilan Ankr, 0 error. "
    "102 NFT + 267 ERC-20 mint di JSON (54 kontrak chunk belum ter-enrich, tidak di JSON). "
    "Watermark TIDAK dimajukan (aturan scan gagal/partial): tetap 132313490. Skipped gap "
    "132313491-132319879 (backfill dinonaktifkan user; window scan hanya 1000 blok terbaru). "
    "True first-seen (absent seen+snapshot): 3 - startest 0x44C6B5e82cB99438b9307020eb6B4117003Ebf86 "
    "(15 mints), Swarm Agent 0xD612Ded8F2b4818c0A9d2465f06eBf1B745f0E17 (6 mints), Vikings Valley "
    "Drakkar 0xD71eA6E00CE042b1855071D7634e9BB1B1443193 (2 mints) - ketiganya Sourcify not_verified "
    "+ tanpa registry -> BUKAN agent-shaped, tidak masuk snapshot, tidak dilaporkan. "
    "5c: 267 ERC20, mint_count>=10: 6 baru dicek, 0 dibuang sampling limit, 0 hit S1/S2.")
snap["last_run"] = "free-mint-search 2026-11-08 1001 WIB"

json.dump(snap, open(f"{HF}/onchain-snapshot.json", "w"), indent=1)
print("snapshot contracts now:", len(snap["contracts"]))

# ---- 4. seen file: append scan contracts (partial JSON only) ----
added = 0
for c in scan["contracts"]:
    a = (c.get("address") or "").lower()
    if a and a not in seen.get("contracts", {}):
        seen["contracts"][a] = c.get("first_block")
        added += 1
json.dump(seen, open(f"{HF}/onchain-scan-seen.json", "w"), indent=1)
print("seen appended:", added, "| seen total:", len(seen["contracts"]))

# ---- 5. scan-state: watermark NOT advanced (partial scan) ----
state["last_scan_wib"] = NOW
state["note_1001_scan"] = snap["runNote1001_scan"]
state["last_scan_window_from"] = scan["from_block"]
state["last_scan_window_to"] = scan["to_block"]
state["ankr_calls"] = scan.get("ankr_calls")
state["errors"] = scan.get("errors", [])
state["nft_contracts"] = len(scan["contracts"])
state["erc20_mint_contracts"] = len(scan.get("erc20_mint_contracts_list", []))
state["skipped_gap"] = "132313491-132319879 (backfill dinonaktifkan user; window scan hanya 1000 blok terbaru; scan partial - watermark tetap 132313490)"
json.dump(state, open(f"{HF}/onchain-scan-state.json", "w"), indent=1)
print("watermark KEPT at:", state["last_scanned_block"], "(partial scan)")

# ---- 6. track-c-scan-checked merge (5c) ----
checked_list = {a.lower() for a in tc.get("checked", [])}
top_keys = {k.lower() for k in tc.keys() if k != "checked"}
merged = 0
for c in f5["checked"]:
    a = c["address"]
    if a.lower() in checked_list or a.lower() in top_keys:
        continue
    tc[a] = {"source": "run-2026-11-08-1001-5c", "status": "checked-not-sale-shape",
             "mint_count": c.get("mint_count"),
             "note": f"S1=False S2=False (Sourcify {c.get('sourcify')}, registry_bytes={c.get('registry_bytes')}, fns={c.get('fns')})"}
    merged += 1
json.dump(tc, open(f"{HF}/track-c-scan-checked.json", "w"), indent=1)
print("tc-checked merged:", merged)
print("MERGE DONE")
