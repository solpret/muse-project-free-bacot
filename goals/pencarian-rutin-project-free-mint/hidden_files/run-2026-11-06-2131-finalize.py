#!/usr/bin/env python3
"""Finalize run 2026-11-06 2131 WIB (parent).
Merges leg-1 re-read, velocity rows, scan output + 5c,
Sourcify feed shape results (discovery subagent), Boltbook/web findings,
Sourcify verify (BNBFLY + CLEP), targeted re-reads (StarAgent/Tampesta/Jolly/MERGEBORN).
CHANGES THIS RUN:
- StarAgent-7d39 AGE-EXCLUDED (first mint ~2026-11-04 21:26 WIB est.; 48h deadline
  ~21:26 WIB PASSED during this run; fresh reads totalSupply 1789->1797, mintOpen 1,
  still minting, not sold out) -> excluded + report once. (Deferred from run 2031.)
- BNBFLY Agent Pass 0x7fe03C... NEW EARLY LEAD (reported once): agent-shaped
  (AGENT_ID()=registry, NeedAgentID, claim() no-arg nonpayable, claimOpen=1,
  soulbound, Sourcify verified); first mints verified on-chain (scan window
  132024944-132025943: 15 mints/15 minters, first block 132024991 = 21:30:09 WIB;
  CLAIM_START 21:27:09 WIB; totalSupply 17); age ~0.5h; hasSBT(user)=0 BUT claim
  requires msg.sender.balance >= MIN_BALANCE 0.044 BNB (source-verified) while the
  user wallet holds 0.001048 BNB -> slot NOT open for this wallet as-is. Website
  UNVERIFIED (A/G/H/I/J tried; contractURI null; tokenURI no external_url).
  NOTE: backfill recorded it in scan-seen during this run and its triage verdict
  read "not-agent-shaped/no-free-path" - contradicted by its own agent_shaped=true
  and by claim() being the free path; never previously reported as early, so it is
  reported once now (dedupe = never twice, not never-at-all).
- CLEPSYDRA (CLEP) 0x9e2738... NEW TRACK-C LEAD (S2) but GATE FAILED -> reported
  once, NOT previewed/minted: token+claimFree() no-arg nonpayable + free views
  (freeClaimed/freeTaken/FREE_PER_WALLET/FREE_TOKENS) + AGENT_ID()=registry;
  free pool 99,760,000/100,000,000 CLEP (240,000 claimed by 12 wallets);
  user slot open (freeTaken=0, claimed=0); age VERIFIED (startTime 21:24:34 WIB,
  first FreeClaim block 132024503 = 21:26:30 WIB, ~50 min old). Website gate
  FAILED after methods A,B,C,D,E,G,J,K,L,M (no site in ABI/source/metadata, no
  search hits, BscScan token page lists NO website/social links, 7 holders).
  BscScan 7 holders/7 transfers vs 12 on-chain FreeClaimed events: unresolved
  index discrepancy, on-chain primary.
- BINANCEAI still refund/failed (launched 0, failed 1, isRefundPhase 1).
- Velocity: 1 passed (Sprouts-1831 4.08x +26) BUT free% UNVERIFIED -> stays early
  lead, no promotion. Forklings free 51.0% (>=50%) BUT velocity FAILS (1.33x, +1)
  and gate still FAILED -> stays strong-lead-gate-blocked, no re-report.
- Scan OK (1000 blok 132024944-132025943, 175 NFT, 500 ERC20, 40 Ankr, 0 error,
  0 true first-seen new to triage). 5c: 66 ERC-20 mint>=10, 2 new checked, 0 sale shape.
- Jolly: entry persists in snapshot despite Nov 5 run 2331 age-exclusion note
  ("DIHAPUS dari snapshot"); already reported once - NO re-report, NO re-exclusion;
  read updated (3712/5000). Left as-is, discrepancy noted.
- IMARS opened null->1 (sale-shape S1 confirmed Nov 3) BUT age still UNVERIFIED
  -> watchlist-only, NOT a lead. SENBAZURU opened null->1, launched 0 -> still not open.
SEEN FILE: NOT written by this finalize. The 2031 finalize's seen-merge used
lowercase keys against mixed-case stored keys (would duplicate 175 entries);
backfill owns seen + watermark this run and already recorded the window.
0 preview/mint/claim/approve/sign/transaksi unless a verified candidate
passes ALL gates + safety (none this run).
"""
import json, shutil, os

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TS = "2026-11-06-2131"
NOW_WIB = "2026-11-06 run 2131"

for f in ["onchain-snapshot.json", "track-c-scan-checked.json"]:
    shutil.copy(f"{BASE}/{f}", f"{BASE}/{f}.bak-20261106-2131")

snap = json.load(open(f"{BASE}/onchain-snapshot.json"))
reread = json.load(open(f"{BASE}/run-{TS}-reread-lean.json"))
vel = json.load(open(f"{BASE}/run-{TS}-velocity.json"))
BLOCK = vel.get("block_now") or reread.get("block") or 132025904
merged_nft = 0
merged_tc = 0

# --- 1. Leg-1 NFT re-read merge (non-None only, match by address) ---
addr2name = {}
for name, e in snap.get("contracts", {}).items():
    if not isinstance(e, dict):
        continue
    a = (e.get("address") or "").lower()
    if a:
        addr2name[a] = name
for name, vals in reread.get("reread", {}).items():
    if not isinstance(vals, dict):
        continue
    a = (vals.get("address") or "").lower()
    key = addr2name.get(a) or (name if name in snap.get("contracts", {}) and isinstance(snap["contracts"].get(name), dict) else None)
    if not key:
        continue
    e = snap["contracts"][key]
    for k, v in vals.items():
        if k in ("address",):
            continue
        if v is not None:
            e[k] = v
    e["lastReadBlock"] = BLOCK
    e["lastReadWib"] = NOW_WIB
    merged_nft += 1

# --- 2. Leg-1 track_c re-read merge (match by sale address) ---
sale2name = {}
for name, e in snap.get("track_c", {}).items():
    if not isinstance(e, dict):
        continue
    s = (e.get("sale") or "").lower()
    if s:
        sale2name[s] = name
for name, vals in reread.get("track_c", {}).items():
    if not isinstance(vals, dict):
        continue
    s = (vals.get("sale") or vals.get("address") or "").lower()
    key = sale2name.get(s) or (name if name in snap.get("track_c", {}) and isinstance(snap["track_c"].get(name), dict) else None)
    if not key:
        continue
    e = snap["track_c"][key]
    for k, v in vals.items():
        if k in ("address", "sale"):
            continue
        if v is not None:
            e[k] = v
    e["lastReadBlock"] = BLOCK
    e["lastReadWib"] = NOW_WIB
    merged_tc += 1

# --- 3. Velocity rows merge ---
vel_by_name = {}
for row in vel.get("rows", []):
    vel_by_name[row[0]] = row
for name, row in vel_by_name.items():
    e = snap.get("contracts", {}).get(name)
    if not isinstance(e, dict):
        continue
    if row[4] is not None:
        e["mintedInInterval"] = row[4]
    if row[5] is not None:
        e["currentRatePerMin"] = row[5]
    if row[6] is not None:
        e["previousRatePerMin"] = row[6]
    e["velocityLegPasses"] = bool(row[8])
    e["intervalMinutes"] = vel.get("interval_min")
    e["velocityNote"] = f"Run 2131: view {row[1]}, {row[2]}->{row[3]} (+{row[4]}), rate {row[5]}/mnt vs prev {row[6]} = {row[7]}x, passes={row[8]}"

# --- 4. Scan seen maintenance: SKIPPED this run (see docstring) ---
added_seen = 0
scan = None
scan_path = f"{BASE}/run-{TS}-scan.json"
if os.path.exists(scan_path):
    scan = json.load(open(scan_path))

# --- 5. 5c checked merge ---
added5c = 0
c5_path = f"{BASE}/run-{TS}-5c-checked.json"
if os.path.exists(c5_path):
    checked5c = json.load(open(c5_path))
    tcchecked = json.load(open(f"{BASE}/track-c-scan-checked.json"))
    if isinstance(tcchecked, dict) and "checked" in tcchecked and isinstance(tcchecked["checked"], dict):
        checked_dict = tcchecked["checked"]
        store = tcchecked
    else:
        checked_dict = tcchecked if isinstance(tcchecked, dict) else {}
        store = {"checked": checked_dict}
    existing_lower = {k.lower() for k in checked_dict.keys()}
    for r in checked5c.get("checked", []):
        a = r["address"].lower()
        if a not in existing_lower:
            checked_dict[r["address"]] = {"run": "2026-11-06-2131", "S1": r.get("S1"), "S2": r.get("S2"),
                                           "sourcify": r.get("sourcify"), "mint_count": r.get("mint_count")}
            existing_lower.add(a)
            added5c += 1
    json.dump(store, open(f"{BASE}/track-c-scan-checked.json", "w"), indent=1)

# --- 6. Targeted re-reads ---
targ = {}
targ_path = f"{BASE}/run-{TS}-targeted.json"
if os.path.exists(targ_path):
    targ = json.load(open(targ_path))
_tp = snap.get("contracts", {}).get("Tampesta-6aA5")
if isinstance(_tp, dict) and "Tampesta-6aA5" in targ:
    _t = targ["Tampesta-6aA5"]
    _tp["totalSupply"] = _t.get("totalSupply()")
    _tp["totalMinted"] = _t.get("totalMinted()")
    _tp["maxSupply"] = _t.get("maxSupply()")
    _tp["phase"] = _t.get("phase()")
    _tp["paused"] = _t.get("paused()")
    _tp["status"] = "watchlist-only-2026-11-06"
    _tp["runNote2131"] = ("Run 2131: totalSupply 440->499 (totalMinted 501), phase 1, paused 0, "
        "maxSupply 2222; free views (freeClaimed/freeMinted/FREE_SUPPLY) all null, quote null -> "
        "free% + slot STILL UNVERIFIED; stays watchlist-only, no promotion. Boltbook post 21:12 WIB "
        "(belski.ai, 438/2222, 'free 2x via puzzle') carries no contract address.")
    _tp["lastReadBlock"] = BLOCK
    _tp["lastReadWib"] = NOW_WIB
_mg = snap.get("contracts", {}).get("MERGEBORN")
if isinstance(_mg, dict) and "MERGEBORN" in targ:
    _mg["freeMinted"] = targ["MERGEBORN"].get("freeMinted()")
    _mg["runNote2131"] = ("Run 2131: freeMinted 683 (was ~655-657/800 per Boltbook); still "
        "strong-lead-gate-blocked (website unverified); no change, no re-report.")
    _mg["lastReadBlock"] = BLOCK
    _mg["lastReadWib"] = NOW_WIB
_jy = snap.get("contracts", {}).get("Jolly")
if isinstance(_jy, dict) and "Jolly" in targ:
    _jy["totalMinted"] = targ["Jolly"].get("totalMinted()")
    _jy["freeMinted"] = targ["Jolly"].get("freeMinted()")
    _jy["runNote2131"] = ("Run 2131: totalMinted/freeMinted 3710->3712 (74.24% of FREE_SUPPLY 5000). "
        "Already AGE-EXCLUDED run 2331 Nov 5 (first mint 2026-11-03 23:27:33 WIB, deadline Nov 5 "
        "23:27:33, reported once) - entry persists in snapshot contracts despite that note; "
        "NO re-report, NO re-exclusion; read updated only. Discrepancy noted for a later cleanup.")
    _jy["lastReadBlock"] = BLOCK
    _jy["lastReadWib"] = NOW_WIB

# --- 7. Age exclusions: StarAgent ---
excluded = snap.setdefault("excluded", {})
_sa = snap.get("contracts", {}).pop("StarAgent-7d39", None)
if _sa is not None:
    excluded["StarAgent-7d39"] = {"address": "0x7d390e37Ed41A359f276D8764ca15432704B99b7",
        "name": "Star Agent", "symbol": "STAR", "track": "A", "status": "excluded-age-2026-11-06",
        "note": ("AGE-EXCLUDED run 2131: first mint ~2026-11-04 21:26 WIB (estimated from block "
            "anchor 131959349 = 13:17:43 WIB, run 1331); 48h deadline ~2026-11-06 21:26 WIB PASSED "
            "during this run. Fresh re-reads: totalSupply 1789 (main leg, block 132025904) -> 1797 "
            "(targeted, block 132027425), mintOpen 1, still minting, NOT sold out. Previously "
            "early-lead-reported-run2131 (Nov 5). Removed from active watchlist per 48h rule; "
            "report once."),
        "previousStatus": _sa.get("status"), "totalSupply": 1797,
        "firstMintWib": "2026-11-04 ~21:26 WIB (ESTIMASI)", "deadlineWib": "2026-11-06 ~21:26 WIB"}

# --- 8. New early lead: BNBFLY Agent Pass ---
snap["contracts"]["BNBFLY Agent Pass"] = {
    "address": "0x7fe03C055588bd5018825175D791103c5CBEd8be",
    "name": "BNBFLY Agent Pass", "symbol": "BFLY-PASS", "kind": "ERC721",
    "status": "early-lead-reported-2026-11-06",
    "totalSupply": 17, "totalMinted": 17, "claimOpen": 1,
    "CLAIM_START": 1793975229, "CLAIM_START_wib": "2026-11-06 21:27:09",
    "CLAIM_END_wib": "2026-11-09 21:27:09", "CLAIM_WINDOW": 259200,
    "MIN_BALANCE": 44000000000000000,
    "hasSBT_user": 0, "balanceOf_user": 0,
    "firstSeenBlock": 132024991, "firstMintWib": "2026-11-06 21:30:09",
    "scanMints": 15, "scanMinters": 15,
    "sourcify": "verified",
    "agentShaped": True,
    "launchNote": ("Launch VERIFIED <=48h: CLAIM_START on-chain 2026-11-06 21:27:09 WIB; first mint "
        "block 132024991 = 21:30:09 WIB (scan window + backfill triage agree; 15 mints/15 minters in "
        "scan window, 17 total by 21:56 triage); age ~0.5h at report."),
    "freeNote": ("Free path = claim() no-arg nonpayable (ABI-verified) + claimOpen=1 + NeedAgentID "
        "(AGENT_ID()=registry 0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F). BUT source-verified gate: "
        "claim() reverts LowBalance unless msg.sender.balance >= MIN_BALANCE 0.044 BNB; user wallet "
        "holds 0.001048 BNB -> slot NOT open for this wallet as-is (hasSBT=0). Soulbound "
        "(non-transferable). Free % UNVERIFIED (no free-cap view)."),
    "gateNote": ("Website UNVERIFIED run 2131: (A) contract-address search no hit; (G) 'BNBFLY' name "
        "search no project hit; (H) contractURI() null; (I) tokenURI (base64 JSON) has name/description/"
        "image only, no external_url; (J) ABI has no website/siteURL functions; (C) Sourcify source "
        "(contracts/bnbfly/AgentSBT.sol) has no project URL. X/discussion UNVERIFIED. -> EARLY only, "
        "NOT strong lead (slot blocked by MIN_BALANCE + free% unverified), NOT candidate, "
        "NOT previewed/minted."),
    "xVerified": False, "velocityVerified": False,
    "lastReadBlock": 132027977, "lastReadWib": NOW_WIB}

# --- 9. New track-C lead (gate-blocked): CLEPSYDRA ---
snap.setdefault("track_c", {})["CLEPSYDRA"] = {
    "sale": "0x9e2738B3DD3773c6c71cA24Fbc92660B501C0B6b",
    "token": "0x9e2738B3DD3773c6c71cA24Fbc92660B501C0B6b",
    "name": "CLEPSYDRA", "symbol": "CLEP",
    "status": "track-c-lead-gate-blocked-2026-11-06",
    "saleShape": ("PASS (S2): contract IS the token (name/symbol/decimals/totalSupply) + "
        "claimFree() no-arg nonpayable + free views (freeClaimed/freeTaken/FREE_PER_WALLET/"
        "FREE_TOKENS) + AGENT_ID()=registry 0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F, "
        "Sourcify verified (Exact Match)"),
    "totalSupply": 1000000000000000000000000000,
    "FREE_TOKENS": 100000000000000000000000000,
    "FREE_PER_WALLET": 20000000000000000000000,
    "freeClaimed": 240000000000000000000000,
    "freePoolRemaining": 99760000000000000000000000,
    "freeClaimWallets": 12,
    "userSlot": {"freeTaken": False, "claimed": False, "balanceOf": 0},
    "startTime_wib": "2026-11-06 21:24:34",
    "firstFreeClaimWib": "2026-11-06 21:26:30",
    "firstFreeClaimBlock": 132024503,
    "listed": 0, "pair": "0x0000000000000000000000000000000000000000",
    "soldTokens": 0, "raised": 0, "HARDCAP": 10000000000000000000,
    "owner": "0x4e9ae7fe888b24878df990759eb543ac06409250",
    "ageNote": ("VERIFIED <=48h: startTime on-chain 2026-11-06 21:24:34 WIB + first FreeClaim event "
        "block 132024503 = 21:26:30 WIB (Ankr getLogs, 12 claims / 12 distinct wallets); ~50 min old "
        "at report. NOTE: dataseed eth_getLogs returned 0 for the same query twice (RPC degradation); "
        "Ankr is the reliable source here."),
    "gateNote": ("Website GATE FAILED run 2131 (methods A,B,C,D,E,G,J,K,L,M): (A) address search no hit; "
        "(G) 'CLEPSYDRA/CLEP' name search no project hit; (C) Sourcify source Clepsydra.sol has no "
        "project URL (only an OpenZeppelin forum link); (J) ABI has no WEBSITE/TWITTER/siteURL fns; "
        "(M) site:vercel/pages/deed filters no results; (K) GitHub address/name search no repo "
        "(search-index absence is not proof - true code search needs auth); (E) owner() = "
        "0x4e9ae7fe888b24878df990759eb543ac06409250, no group linkage found; (L) BscScan token page "
        "(live browser read) lists NO website/social links - Info tab only 'Click here to update the "
        "token information'; token shown CLEPSYDRA (CLEP), 1,000,000,000 max supply, reputation UNKNOWN, "
        "7 holders / 7 transfers (vs 12 on-chain FreeClaimed events - unresolved BscScan index lag/partial "
        "render, on-chain primary); (B) not on Boltbook front page; (N) no registry-profile/author hop "
        "source. X/discussion UNVERIFIED (X optional, never a blocker). -> LEAD reported once, "
        "NOT previewed, NOT minted (gate FAILED)."),
    "lastReadBlock": 132027977, "lastReadWib": NOW_WIB}

# --- 10. Run notes ---
snap["last_run"] = "2026-11-06 run 2131"
snap["last_run_wib"] = "2026-11-06 run 2131"
snap["timestamp_wib"] = "2026-11-06T22:15:00+07:00"

snap["runNote2131_1106"] = ("Run 2131 (21:31-~22:15 WIB): 0 candidate, 0 auto-mint/claim. 1 EARLY LEAD BARU "
    "(dilaporkan sekali): BNBFLY Agent Pass 0x7fe03C055588bd5018825175D791103c5CBEd8be (first mint 21:30:09 WIB, "
    "totalSupply 17, claimOpen=1, AGENT_ID=registry, claim() free; TAPI slot user TERBLOKIR MIN_BALANCE 0.044 BNB "
    "sementara wallet hanya 0.001048 BNB; website UNVERIFIED). 1 TRACK-C LEAD BARU (dilaporkan sekali, GATE GAGAL -> "
    "TIDAK di-preview/di-mint): CLEPSYDRA (CLEP) 0x9e2738B3DD3773c6c71cA24Fbc92660B501C0B6b (S2 lolos, free pool "
    "99.760.000/100.000.000 CLEP, slot user terbuka, umur TERVERIFIKASI ~50 mnt; website GAGAL metode A-N). "
    "1 AGE-EXCLUSION: StarAgent-7d39 (deadline ~21:26 WIB lewat; totalSupply 1797, masih minting) -> excluded + "
    "report once. Velocity: 1 passed (Sprouts-1831 4.08x +26) TAPI free% UNVERIFIED -> stays early lead. Forklings "
    "free 51.0% (>=50%) TAPI velocity GAGAL (1.33x, +1) + gate tetap FAILED -> stays strong-lead-gate-blocked. "
    "Tampesta totalSupply 499 (free%/slot tetap UNVERIFIED, puzzle-gated) -> watchlist-only. Jolly 3712/5000 - "
    "sudah age-excluded run 2331 Nov 5, tidak dilaporkan ulang. MERGEBORN freeMinted 683, tetap gate-blocked. "
    "BINANCEAI tetap refund/failed (launched 0, failed 1, isRefundPhase 1). IMARS opened null->1 (S1 terkonfirmasi "
    "Nov 3) TAPI umur tetap UNVERIFIED -> watchlist-only, BUKAN lead. SENBAZURU opened 1, launched 0 -> belum buka. "
    "Bridge: 115 discarded / 7 not_in_snapshot / 0 baru. Boltbook: semua alamat sudah dikenal; Oni 0x852f... "
    "(tanpa gate Agent ID, hot-leg-seen) bukan early lead, tidak masuk snapshot.")
snap["runNote2131_scan_1106"] = ("Run 2131 scan SUKSES. Pre-flight OK 3.8 dtk (head 132025903, 242 logs / 50 blok). "
    "Window 132024944-132025943 (1000 blok, cap 1000), 40 panggilan Ankr, 0 error, partial=false. 175 NFT, 500 ERC-20 "
    "mint. 0 true first-seen baru untuk triase (BNBFLY sudah tercatat di seen oleh backfill selama run ini; triase "
    "backfill 132024438-132027026 menilainya 'not-agent-shaped/no-free-path' - vonis itu dibantah verifikasi run ini "
    "dan BNBFLY dilaporkan sekali sebagai EARLY). Watermark TIDAK dimajukan (backfill owns it); seen file TIDAK "
    "ditulis finalize ini (bug kunci case-sensitive 2031 dihindari; backfill sudah mencatat window). 5c: 66 ERC-20 "
    "mint_count>=10, 64 sudah dicek, 2 baru dicek (0x0349fd89..., 0x00901a07...), 0 sale shape. Sourcify feed: 20 "
    "contracts, 19 baru dicek, 2 shape-pass (BNBFLY NFT agent-shape + CLEP S2) + 3 near-miss factory-wave spot-sale "
    "berbayar (0x5b503755..., 0xAe343d6B..., 0xBfE2790C..., tanpa free views -> bukan lead). Boltbook/web: nothing new.")
snap["runNote2131_binanceai_1106"] = ("Run 2131: BINANCEAI launched=0, failed=1, isRefundPhase=1, "
    "totalShares=3110, tokenClaimed(user)=0, tokenBalance(user)=0 - tetap refund/failed, pending_claims kosong, "
    "tidak dilaporkan ulang.")
snap["runNote2131_age_exclusions_1106"] = ("Run 2131 AGE-EXCLUSIONS (1 item, dilaporkan sekali): StarAgent-7d39 "
    "(first mint ~2026-11-04 21:26 WIB estimasi; deadline 48 jam ~2026-11-06 21:26 WIB lewat selama run ini; "
    "totalSupply segar 1797, mintOpen=1, belum sold out) -> DIHAPUS dari kontrak aktif, dipindah ke excluded "
    "(status excluded-age-2026-11-06). DIPERTAHANKAN: HIVE Agents (minted-by-user, grandfathered), Jolly (sudah "
    "age-excluded run 2331 Nov 5, dilaporkan sekali - tidak dilaporkan ulang), semua item minted-by-user lain.")

json.dump(snap, open(f"{BASE}/onchain-snapshot.json", "w"), indent=1)
print(f"FINALIZE DONE merged_nft={merged_nft} merged_tc={merged_tc} added_seen={added_seen} added5c={added5c}")
print(f"contracts={len(snap.get('contracts',{}))} track_c={len(snap.get('track_c',{}))} excluded={len(snap.get('excluded',{}))}")
