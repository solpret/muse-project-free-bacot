# Free Bacot run 0031 — scan leg (route 4) + 5c summary
Run: Sun 2026-11-08 ~00:31 WIB. Worker: scan leg only. No chat report sent.

## Pre-flight: PASS
- Head via fast_rpc batch (bsc-dataseed1): 132241305; small ankr_getLogs (50 blocks) OK, 241 logs, 28.1s total (<60s).
- Pre-flight files: run-2026-11-08-0031-preflight.py/.log/.json

## Scan: SUCCESS on retry (first attempt failed transiently, no retry-aggression)
- Attempt 1 (17:34 UTC): FAILED at the very first step — `eth_blockNumber` via fast_rpc.batch timed out on all healthy endpoints (`batch failed on all healthy endpoints: timed out`). No Ankr call made, no output written. Endpoints re-verified healthy immediately after (dataseed1/publicnode/dataseed2 all OK, head ~132241600), so ONE retry was run.
- Attempt 2 (retry, 17:35–17:59 UTC): SUCCESS, no errors. Window claimed: 132240684–132241683 (1000 blocks, most recent only; head at scan start 132241683).
- EFFECTIVE coverage: FULL. 20/20 chunk lines, 0 chunk ERROR lines, errors list empty, partial=False. Max first_block seen in output: NFT 132241682, ERC-20 132241680 — coverage reaches to within 1–3 blocks of to_block. No Transfer/TransferSingle chunk failure.
- Result: 134 NFT contracts (132 ERC721 + 2 ERC1155), 345 ERC-20 mint contracts, 40 Ankr calls, partial=False, HIVE Agents NOT found in window.
- Total NFT mints in window: (see onchain-scan-2026-11-08-0031.json; contracts list). Duration: ~24 min (log phase ~5 min, enrichment ~19 min — slower than run 0001's ~15 min; Sourcify flaky during enrichment as before, retried inline by the script).
- No re-run needed beyond the single retry: second attempt succeeded with full coverage.
- Output: onchain-scan-2026-11-08-0031.json; progress: run-2026-11-08-0031-scan-progress.log.
- Note: the background wait-loop used to monitor the scan matched its own command line via pgrep and had to be SIGTERM'd after the scan process itself had already exited; the scan output was complete (partial=False) before that. No effect on results.

## Watermark / gap (NOT advanced by this leg — backfill owns it)
- onchain-snapshot.json and onchain-scan-state.json NOT written by this leg. Snapshot mtime unchanged (17:22:02 UTC, pre-run).
- last_scanned_block was 132232465 at run start and reads 132238015 at run end — advanced by BACKFILL during this run, not by this leg. State mtime moved during the run by backfill.
- No hole inside this run's window. Uncovered by design (window cap): blocks 132237361–132240683 (~3,323 blocks) between run 0001's window end (132237360) and this window's start (132240684) — plus the standing gap below the backfill watermark — remain backfill's job; routine scans do not re-cover them.

## Triage: 2 first-seen, 0 EARLY leads
- First-seen = absent from BOTH onchain-scan-seen.json and onchain-snapshot.json (registry address excluded; 2 first-seen + 131 known + 1 registry = 134).
- 0x41D45A7CB5963f5eb92756f60A25F12a5fc7D9A0 — LifePass (LIFE), ERC721, 200 mints / 200 minters, first mint 00:28:50 WIB (block 132240721). NOT agent-shaped (no registry bytes, no free shape, Sourcify not_verified). Large mint count but no agent signal — record only, not a lead.
- 0x85443fF1818d76E64E755901EA33b6bDEB315495 — NetGain Membership (NGNFT), ERC721, 1 mint / 1 minter, first mint 00:33:52 WIB (block 132241392). NOT agent-shaped (no registry bytes, no free shape, Sourcify error:IncompleteRead).
- No same-owner discards among first-seen; no deep checks needed (no registry/free signal). No free views live.
- Seen file: appended 134 new contracts (total nested now 12,211 per triage script); both first-seen addresses verified present in seen file. Triage files: run-2026-11-08-0031-triage-scan.py/.log/.json.

## 5c (track-C shape check): 0 hits
- ERC-20 total 345; mint_count >= 10: 42; already checked 38; new checked 4 (cap 20, dropped_sampling_limit 0).
- All 4: S1=false, S2=false → no-shape. All 4 Sourcify not_verified with registry_bytes=true (factory template common; unverified = unknown free shape, not agent-shaped on bytecode alone).
- Checked: 0xcf9025C5ADFf731ba0Da0FA42DA274E77DC7d5d4 (64), 0x65Ea7b772aa117B2e6EDEDa3B368b49b7Beb205A (55), 0x9BD7CC5F1EF691D875C1c112c43f6630bBBD732f (53), 0xfda6492fcA94DF0A407f7B8a339a7D1C0DfB07d3 (29).
- Merged into track-c-scan-checked.json (all 4 verified present with source run-2026-11-08-0031-5c, status checked-not-sale-shape). 5c files: run-2026-11-08-0031-5c.py/.log/.json.

## Bottom line for parent
- No EARLY lead, no track-C lead material from this scan leg. Nothing to report to chat from route 4/5c this run.
- No hole to record for this run's window (full coverage). The standing backfill gap (blocks below 132240684 not covered by routine windows) is unchanged and remains with backfill.
- Transient RPC note: fast_rpc batch to all dataseed endpoints timed out once at 17:34 UTC, healthy again within a minute; single retry succeeded. No Ankr-side failure this run.
