# Free Bacot run 2026-11-08 0801 — Route 4 scan + triage + 5c (subagent)

## 1. Pre-flight — PASS
- Head via fast_rpc batch (bsc-dataseed1): 132302330
- Small ankr_getLogs (50 blocks): 248 logs, total 7.6 s (< 60 s)
- Log: `run-2026-11-08-0801-preflight.py` / `.json`

## 2. Scan — PARTIAL (killed by watchdog hard cap, enrichment stall pattern)
- Command: `python3 onchain_nft_scan.py --chunk 50 --blocks 1000 --out onchain-scan-2026-11-08-0801.json`
- Window scanned: **132301401–132302400** (1000 blocks, most recent; cap applied)
- Skipped gap: **132293853–132301400 (7.548 blocks)** — watermark 132293852 → head 132302330 = 8.478 blocks > cap 1000; gap NOT covered (backfill disabled by user ~06:28 WIB, so it regrows)
- Chunk phase: 20/20 OK. Enrichment: **70/124, then killed** — watchdog hard cap 780 s reached (kill -9, same stall pattern as runs 1301/1331/0731: chunk phase fine, enrichment stalls)
- Output: `onchain-scan-2026-11-08-0801.json` — **partial=true**, 70 contracts enriched, 122 ERC721 + 2 ERC1155 found in window (124 total), 269 ERC20-mint contracts, 40 Ankr calls, 0 errors
- **54 contracts unenriched — addresses lost for this run** (partial JSON only holds enriched contracts; same known limitation as run 0731, where 119 were lost)
- Watermark NOT advanced by this run (parent decision; state file untouched)
- Progress log: `run-2026-11-08-0801-scan-progress.log` (last lines: enrich 70/124 Un-Written, enrich 71/124 started, then WATCHDOG kill)

## 3. Triage first-seen — 1 true first-seen: HokiPanda = STRONG LEAD
- First-seen = absent from BOTH `onchain-scan-seen.json` (11.380 contracts) AND snapshot (465 entries, addresses + excluded). Registry address in scan (infrastructure, excluded).
- **HokiPanda (HPANDA) 0x4b61A7767dA68f18266907b2Eb7C9A1EE3d24517**
  - Sourcify **exact_match** (60 fns); `agentIdRegistry()` = 0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F (exact registry); free views FREE_CAP / FREE_PER_WALLET / freeMinted / freeCount / freeMint; mintOpen
  - True first mint **verified**: block **132301321**, **2026-11-08 08:03:25 WIB** (tokenId 1 → 0x9678d46a5f529d0d3e42062ccd5024e4a51a80d6; tx 0x1dd860c7dc38810b50fcd41b7ea29a056447158010e6b5ed26864b8f99a552b1). Correction: scan `first_block` 132301457 (08:04:26) was first IN-WINDOW mint only — pre-window chunk 132300401–132301400 had 3 mints, chunk 132299401–132300400 had 0. Block timestamps via dataseed (never Ankr).
  - Free quota **verified**: freeMinted **83 / FREE_CAP 111 = 74,77%** (≥25% strong-lead leg, also ≥50%); FREE_PER_WALLET 1; totalMinted 83; paidMintedCount 0; paidUnlocked false; PRICE 0,00005 BNB (paid path exists, free path open)
  - User slot **open**: freeCount(user 0xeb23…) = 0, balanceOf(user) = 0; mintOpen = 1
  - Mint velocity in window: 43 mints / 43 distinct minters in scan window; totalMinted 83 at triage (~08:25 WIB) — minting fast
  - Owner **0x13333df46ab3e95f4166370d571e7b73aad06370** (= treasury); NOT in bridge `same_owner_discarded`, NOT known factory group 0xa054275580c6d1c9077543907ac5798f2494ecce
  - Age at triage: ~22 menit → **≤48 h verified**
  - **Classification: STRONG LEAD** (all 3 legs: age verified ≤48 h + free% 74,77% verified ≥25% + user slot open). NOT previewed/minted by this run — parent decides website gate + direct mint.
  - Full evidence: `run-2026-11-08-0801-triage-scan.json` (+ `.log`, `run-2026-11-08-0801-firstmint.json`)
- No other first-seen among the 70 enriched. (54 unenriched contracts could hide further first-seen — unknown, stated as a gap, not as zero.)
- Note: Dafeiyu + HokiKoi (run 0731 early leads) re-appeared in this window as known snapshot entries — not re-reported.

## 4. 5c ERC-20 backlog — 0 sale-shape hits
- ERC20 total 269; mint_count ≥ 10: **54**; already checked: 48; **new checked: 6** (cap 20 not reached); dropped sampling limit: 0
- New 6: 0x118B738DeA1882Ba155cac035C0097e2Cc12d7f1 (44), 0x0FFEee3f166C2763E81F21FC425b474d90Ad8157 (36), 0xDADF0B19c1d04704E0903cFe1c18925F321dCa44 (29), 0x5Cc44b4B474880c84C5F084647bAd30C65b2E00f (19), 0x0A52B92010b944Aa36Eaaa35eF4FAfb2Ad84b302 (16), 0xBF091DCeb3dDf042Ca17088015fb18CFeD9D89e1 (14)
- All 6: Sourcify **not_verified** (no ABI → no S1/S2), registry_bytes=True (factory-template noise, known non-discriminating). **0 S1/S2 hits.**
- Newly checked addresses recorded in `run-2026-11-08-0801-5c.json` for **parent merge** into `track-c-scan-checked.json` (this run did NOT write the shared file).
- Script/log: `run-2026-11-08-0801-5c.py` / `.log`

## 5. Flags for parent
- **baw session LOGGED OUT early** (MEMORY update 08:15–08:19 WIB: 5× NOT_LOGGED_IN 10003000; needs QR re-sign-in) — any HokiPanda direct-mint decision cannot execute via baw until re-login. This run did no baw work.
- Scan partial: 54/124 window contracts unenriched; next run's window will overlap part of this window's tail only if watermark stays — the unenriched addresses are unrecoverable from this run.
- Skipped gap 132293853–132301400 (7.548 blocks) remains unscanned by main scan (backfill off).

## Files written (all in `~/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/`)
- `run-2026-11-08-0801-preflight.py`, `run-2026-11-08-0801-preflight.json`
- `run-2026-11-08-0801-scan-progress.log`, `run-2026-11-08-0801-scan-watchdog.sh`, `run-2026-11-08-0801-scan-start.txt`
- `onchain-scan-2026-11-08-0801.json` (partial=true, 70/124 enriched)
- `run-2026-11-08-0801-triage-scan.py`, `run-2026-11-08-0801-triage-scan.log`, `run-2026-11-08-0801-triage-scan.json`
- `run-2026-11-08-0801-firstmint.py`, `run-2026-11-08-0801-firstmint.json`
- `run-2026-11-08-0801-5c.py`, `run-2026-11-08-0801-5c.log`, `run-2026-11-08-0801-5c.json`
- `run-2026-11-08-0801-scan-summary.md` (this file)
- Shared files NOT edited: `onchain-snapshot.json`, `onchain-scan-state.json`, `onchain-scan-seen.json`, `track-c-scan-checked.json` (read-only as instructed).
