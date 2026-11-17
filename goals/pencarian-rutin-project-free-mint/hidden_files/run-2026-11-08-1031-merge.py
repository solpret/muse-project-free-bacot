#!/usr/bin/env python3
"""Merge run 1031 (2026-11-08) results into snapshot / seen / tc-checked.
Tailored for this run: generic reread+velocity update, TWO new entries
(Cedar Kiln EARLY LEAD via Boltbook + helper-gate sim; Rose Genesis
watchlist-only-mature-newly-noticed), APASS age-exclusion record,
5c merge (1 address). SCAN WAS PARTIAL (enrich 77/79, 1 failed Transfer
chunk, timeout) -> watermark NOT advanced. Preserves all existing
snapshot keys. Run once."""
import json, datetime, shutil

HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
WIB = datetime.timezone(datetime.timedelta(hours=7))
NOW = datetime.datetime.now(WIB).strftime("%Y-%m-%d %H:%M:%S WIB")

for f in ("onchain-snapshot.json", "onchain-scan-seen.json", "onchain-scan-state.json"):
    shutil.copy(f"{HF}/{f}", f"{HF}/{f}.bak-1031")
print("backups written .bak-1031")

snap = json.load(open(f"{HF}/onchain-snapshot.json"))
rr = json.load(open(f"{HF}/run-2026-11-08-1031-reread.json"))
vv = json.load(open(f"{HF}/run-2026-11-08-1031-velocity.json"))
scan = json.load(open(f"{HF}/onchain-scan-2026-11-08-1031.json"))
seen = json.load(open(f"{HF}/onchain-scan-seen.json"))
state = json.load(open(f"{HF}/onchain-scan-state.json"))
tc = json.load(open(f"{HF}/track-c-scan-checked.json"))
f5 = json.load(open(f"{HF}/run-2026-11-08-1031-5c.json"))

REREAD_BLOCK = rr["block"]
contracts = snap["contracts"]

# lookup reread rows by key AND by address
rr_by_key = rr.get("reread", {})
rr_by_addr = {}
for k, row in rr_by_key.items():
    a = (row.get("address") or "").lower()
    if a:
        rr_by_addr[a] = row

vel_by_addr = {}
for row in vv.get("rows", []):
    a = (row.get("address") or "").lower()
    if a:
        vel_by_addr[a] = row

updated = 0
for key, entry in contracts.items():
    if not isinstance(entry, dict):
        continue
    row = rr_by_key.get(key) or rr_by_addr.get((entry.get("address") or "").lower())
    if row:
        if row.get("totalSupply") is not None:
            entry["totalSupply"] = row["totalSupply"]
        for f in ("totalMinted", "freeClaimed", "freeMinted", "FREE_SUPPLY",
                  "MAX_SUPPLY", "mintOpen", "freeClaimed_user", "balanceOf_user"):
            if row.get(f) is not None:
                entry[f] = row[f]
        entry["lastReadBlock"] = REREAD_BLOCK
        entry["lastReadWib"] = "2026-11-08 run 1031"
        updated += 1
    vrow = vel_by_addr.get((entry.get("address") or "").lower())
    if vrow:
        cur = vrow.get("curSupply")
        if cur is not None:
            entry["previousTotalSupply"] = vrow.get("prevSupply")
            entry["currentRatePerMin"] = vrow.get("ratePerMin")
            entry["previousRatePerMin"] = vrow.get("prevRatePerMin")
            entry["velocityRatio"] = vrow.get("ratioVsPrev")
            entry["run1031_velocity"] = (
                f"Run 1031 (blok {REREAD_BLOCK}, interval {vrow.get('intervalMin')} mnt): "
                f"{vrow.get('prevSupply')}->{cur} (+{vrow.get('mintedInInterval')}, "
                f"{vrow.get('ratePerMin')}/mnt vs prev {vrow.get('prevRatePerMin')} = "
                f"{vrow.get('ratioVsPrev')}x) -> velocity "
                f"{'LOLOS' if vrow.get('velocityPasses') else 'GAGAL'}."
            )
print("reread-updated entries:", updated)

# ---- 1b. track_c fresh reads ----
tc_updated = 0
for key, entry in snap.get("track_c", {}).items():
    if not isinstance(entry, dict):
        continue
    row = rr.get("track_c", {}).get(key)
    if row and row.get("totalSupply") is not None:
        entry["totalSupply"] = row["totalSupply"]
        entry["lastReadBlock"] = REREAD_BLOCK
        entry["lastReadWib"] = "2026-11-08 run 1031"
        tc_updated += 1
print("track_c updated:", tc_updated)

# ---- 2a. new entry: Cedar Kiln (EARLY LEAD, Boltbook discovery) ----
contracts["Cedar Kiln"] = {
    "address": "0x7ac89Ff65D1e4aa9C2BBCdEE0bBafAaa092B02bE",
    "helper": "0x6AA2C9B7C73BF6351E41EaD32Dd082951336953e",
    "token": "0xbed2d450d57e53ab597b3d349f086d861ee83a66",
    "status": "early-lead-reported-2026-11-08",
    "name": "Cedar Kiln",
    "symbol": "CEDAR",
    "kind": "ERC721",
    "totalSupply": None,
    "freeClaimed": None,
    "FREE_SUPPLY": None,
    "MAX_SUPPLY": 10000,
    "freePctVerified": None,
    "mintOpen": None,
    "userBalance": 0,
    "firstSeenBlock": 132321293,
    "discovery": "Boltbook post 2026-11-08 ~10:4x WIB (free mint through helper contract) + on-chain triage run 1031",
    "lastReadBlock": 132323930,
    "lastReadWib": "2026-11-08 run 1031 (triage)",
    "xVerified": False,
    "velocityVerified": False,
    "launchNote": "First mint VERIFIED on-chain: first Transfer-from-zero at block 132321293, 2026-11-08 10:33:14 WIB (Ankr getLogs address-filtered; 7 mint logs in 132321000-132321999, 0 in 132320000-132320999; timestamp via fast_rpc, NOT Ankr). Age ~45 mnt at triage -> VERIFIED <=48h. NOTE: contract address already in onchain-scan-seen.json since block 131257091 (deployment-seen by an earlier scan; provenance of that entry unverified - historical eth_getCode fails 'missing trie node') but NEVER triaged or reported before - no prior snapshot entry, no prior report - so this is its first report, not a duplicate (Zigzoo precedent run 1001).",
    "baselineNote": "EARLY lead reported once 2026-11-08 run 1031. Never auto-minted/previewed. Agent-shape verified BEHAVIORALLY (concrete AgentGate): helper mint(uint256) value 0 simulates OK from user Agent-ID wallet (mint(1) + mint(2), fresh eth_call run 1031) and reverts 0x41aaf0fd from dead address (no Agent ID). Collection + helper Sourcify unverified; NO registry address in bytecode (collection + helper) or storage slots 0-7; no free views / no totalSupply / no owner() readable on collection (all revert) - minimal ERC721 (name/symbol/balanceOf/tokenURI only). Helper owner() readable. tokenURI(1) = https://cedar-kiln.vercel.app/metadata/0.json (site linkage, method I). free% UNVERIFIED: no global free counter; site counter '0/10000 Quarks minted' is stale/broken (on-chain ~90+ minted at triage) and '1000 Free-phase quarks left' has no verifiable total. Website gate PENDING (browser task cedar-kiln.vercel.app/skill.md + contract print check; skill.md 404 via text fetch). X: not found (optional). Promotes to strong lead only on all 3 strong-lead legs (age OK; free% >=25% + slot open still needed); to candidate only on ALL criteria + safety.",
    "freePctNote": "UNVERIFIED: no readable free counter (freeClaimed/freeMinted/FREE_SUPPLY/freeLeft all revert on collection + helper). Site claims 1000 free-phase quarks left; unverifiable on-chain.",
    "runNote1031": "Run 1031: EARLY LEAD (temuan Boltbook, first-read job ini). First mint 2026-11-08 10:33:14 WIB, helper-gated free mint verified by fresh sim (mint(1)/(2) value 0 OK from user, revert 0x41aaf0fd from dead), free% unverified, website gate pending, slot terbuka. Dilaporkan sekali sebagai EARLY, TIDAK di-preview/di-mint.",
}

# ---- 2b. new entry: Rose Genesis (watchlist-only, mature newly noticed) ----
contracts["Rose Genesis"] = {
    "address": "0x7aA9eF2f304ef97d93b35f7E51E6F2c82e61333a",
    "status": "watchlist-only-mature-newly-noticed-2026-11-08",
    "name": "Rose Genesis",
    "symbol": "ROSE",
    "kind": "ERC721",
    "totalSupply": 105,
    "totalMinted": None,
    "freeClaimed": None,
    "FREE_SUPPLY": None,
    "MAX_SUPPLY": 3333,
    "freePctVerified": None,
    "mintOpen": None,
    "userBalance": 0,
    "firstSeenBlock": 132323097,
    "discovery": "On-chain scan run 1031 (first-seen in window 132322860-132323859; absent from seen file + snapshot before this run)",
    "lastReadBlock": 132323930,
    "lastReadWib": "2026-11-08 run 1031 (triage)",
    "xVerified": False,
    "velocityVerified": False,
    "launchNote": "First OBSERVED mint in scan window: block 132323097 (1 mint / 1 minter in-window). NOT a first-mint: totalSupply already 105 at triage, so minting predates this window (true first mint unverified - may sit in unscanned gap 132320880-132322800). Age UNVERIFIED -> NOT early/strong/candidate until first mint verified <=48h.",
    "baselineNote": "Watchlist-only-mature-newly-noticed, added run 1031. Never reported as lead, never previewed/minted. Agent-shape verified: AGENT_ID_REGISTRY() returns 0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F exactly + registry bytes in bytecode (scan). Free path UNVERIFIED: no free views, price() reverts, Sourcify unknown (RemoteDisconnected). Website/X unverified.",
    "runNote1031": "Run 1031: watchlist-only-mature-newly-noticed (scan first-seen, agent-shaped, tapi totalSupply 105 membuktikan minting sudah berjalan sebelum window - bukan first mint).",
}

# ---- 2c. APASS age-exclusion record (never in snapshot; record only) ----
age_ex = snap.get("age_exclusions")
if not isinstance(age_ex, list):
    age_ex = []
    snap["age_exclusions"] = age_ex
age_ex.append({
    "name": "AgentPad Pass (APASS)",
    "address": "0x01c106835091c09d5c69737631af133530093c89",
    "firstMintBlock": 131187779,
    "firstMintWib": "2026-11-02 ~12:50 WIB (estimated from block: BNBbaby first mint 131049616 = 2026-11-01 19:33 WIB; +138163 blocks x 0.45s)",
    "ageHours": "~142",
    "totalSupply": 4826,
    "MAX_SUPPLY": 10000,
    "status_before": "seen-only (first-seen scan, tidak pernah masuk snapshot / tidak pernah dilaporkan sebagai lead)",
    "removed_run": "2026-11-08 run 1031",
    "reason": "First mint terverifikasi on-chain via Ankr getLogs (1 Transfer-from-zero in seen window 131187511-131189510, tx 0xeb7fca0cb6f43b95...); umur ~142 jam (>48 jam) dan belum sold out (4826/10000) -> AGE-EXCLUDED per aturan umur 48 jam; bukan lead/kandidat; tidak dilaporkan ke chat (hanya dicatat, preseden BAYC sale run 1801 / PIXEL BOYZ run 1831). Catatan: mint() no-arg value 0 simulasi OK dari wallet user dan revert 0xf947691f dari dead address (gate nyata), PRICE=0, tokenURI(1) base64 menunjuk hark.site (bukan situs proyek); umur yang menggugurkan, bukan bentuknya. Tidak ada fase/batch mint baru yang terverifikasi."
})
print("age_exclusions now:", len(age_ex))

# ---- 3. run notes ----
snap["runNote1031"] = (
    "Run 1031 (2026-11-08, blok reread 132323930, interval 43,91 mnt): reread 473 kontrak + 70 track_c; "
    "velocity 5 pass (Zhenzhu ERC-20 artefak; Weldagent free% 6,86% + same-owner-discarded; NULLRAID + WAR3 "
    "minted-by-user; Lambdwyn free%+umur unverified) tapi 0 promotable; soldOut 35 (set sama dengan run 1001, "
    "tanpa sellout baru); slotChanged 0. Age-sweep: remove=0, kept=56, unverified-launch=410. "
    "Track B binanceai tidak berubah (blok 132325785: launched=0, failed=1, isRefundPhase=1, tokenClaimed_user=0, "
    "balance 0; sudah dilaporkan run 1701 2026-11-07). Track C: 70 item, 6 hanya berubah totalSupply; BNBbaby "
    "umur ~159 jam >48 jam tapi status minted-by-user (grandfathered, bukan kandidat REMOVE). Bridge: 115 kontrak, "
    "33 belum ada di snapshot (temuan pelengkap scan, semua umur >48 jam, bukan lead baru); file bridge terakhir "
    "diubah 2026-11-06, tidak ada entri baru sejak run 1001. "
    "Boltbook EN+ZH + discovery: Cedar Kiln BARU (EARLY lead, lihat entri snapshot); APASS first mint 2026-11-02 "
    "~12:50 WIB -> AGE-EXCLUDED (~142 jam, 4826/10000, dicatat saja); Paw Gang tradingOpen TRUE ~10:39 WIB "
    "(totalMinted 1.698); OinkHash Pigs v3 + HokiPanda free pool HABIS; REWARD ~16-17 free tersisa (excluded); "
    "Ghostling sudah age-excluded (tidak di-add lagi); DinoAgent sold out 777/777; Gloop pre-launch (buka 19:00 WIB). "
    "Sourcify feed 20 kontrak -> 0 S1 / 0 S2 / 0 mint-shaped. Sweep EN+ZH + Square/Odaily/PANews: 0 proyek baru; "
    "BNAGENT + SWARM share sale BERBAYAR (1 USDT/share, tanpa free) -> bukan track-C. "
    "EARLY LEAD x1: Cedar Kiln 0x7ac89Ff65D1e4aa9C2BBCdEE0bBafAaa092B02bE (first mint 2026-11-08 10:33:14 WIB, "
    "helper mint(1)/(2) value 0 OK dari wallet user + revert 0x41aaf0fd dari dead = AgentGate konkret, free% "
    "unverified, website gate pending browser, slot terbuka). Dilaporkan sekali sebagai EARLY. "
    "Scan first-seen lain: PANDORA 0xdb8A4102C49a41cfAeD7673A3F155f19853Af5e8 (12 mint/12 minter, agentRegistry()=registry, "
    "tapi price()=0,001 BNB + totalSupply 111 -> PAID-ONLY + mature, tidak masuk snapshot, tidak dilaporkan); "
    "Rose Genesis 0x7aA9eF2f304ef97d93b35f7E51E6F2c82e61333a (agent-shaped, 1 mint in-window, totalSupply 105 -> "
    "mature-newly-noticed, watchlist-only).")
snap["runNote1031_scan"] = (
    "Run 1031 SCAN PARTIAL (partial=true): pre-flight OK 6,8 dtk (head 132323800, 196 logs/50 blok). "
    "Window 132322860-132323859 (1000 blok, cap) - chunks 20/20 selesai TAPI enrichment terhenti di 77/79 "
    "oleh timeout 780 dtk (SCAN_EXIT=124 via timeout; 2 kontrak terakhir tidak ter-enrich, tidak di JSON). "
    "18 panggilan Ankr, errors: Transfer chunk 132323310-132323359 Remote end closed connection (50 blok "
    "Transfer logs tidak ter-scan di dalam window - hole, bukan auto-retry). 76 NFT + 167 ERC-20 mint di JSON. "
    "Watermark TIDAK dimajukan (aturan scan gagal/partial): tetap 132313490. Skipped gap 132320880-132322800 "
    "(1921 blok; backfill dinonaktifkan user; window scan hanya 1000 blok terbaru). "
    "True first-seen (absent seen+snapshot): 2 - PANDORA (12 mint, agent-shaped, PAID-ONLY 0,001 BNB) + "
    "Rose Genesis (1 mint, agent-shaped, mature totalSupply 105). Cedar Kiln collection ada di window "
    "(1 mint) tapi sudah ada di seen file (blok 131257091, deployment-seen) - ditriase via Boltbook, bukan scan. "
    "5c: 167 ERC20, mint_count>=10: 24, 23 sudah dicek, 1 baru dicek (0xe2cf5f8795635EA9B55E072a6fAaBDB07416bb97, "
    "mint_count 10), 0 hit S1/S2.")
snap["last_run"] = "free-mint-search 2026-11-08 1031 WIB"

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
state["note_1031_scan"] = snap["runNote1031_scan"]
state["last_scan_window_from"] = scan["from_block"]
state["last_scan_window_to"] = scan["to_block"]
state["ankr_calls"] = scan.get("ankr_calls")
state["errors"] = scan.get("errors", [])
state["nft_contracts"] = len(scan["contracts"])
state["erc20_mint_contracts"] = len(scan.get("erc20_mint_contracts_list", []))
state["skipped_gap"] = "132320880-132322800 (1921 blok; backfill dinonaktifkan user; window scan hanya 1000 blok terbaru; scan partial - watermark tetap 132313490)"
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
    tc[a] = {"source": "run-2026-11-08-1031-5c", "status": "checked-not-sale-shape",
             "mint_count": c.get("mint_count"),
             "note": f"S1={c.get('S1')} S2={c.get('S2')} (Sourcify {c.get('sourcify')}, registry_bytes={c.get('registry_bytes')})"}
    merged += 1
json.dump(tc, open(f"{HF}/track-c-scan-checked.json", "w"), indent=1)
print("tc-checked merged:", merged)
print("MERGE DONE")
