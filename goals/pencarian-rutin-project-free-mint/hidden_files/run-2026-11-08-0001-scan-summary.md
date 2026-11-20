# Free Bacot run 0001 — scan leg (route 4) + 5c summary
Run: Sun 2026-11-08 ~00:01 WIB. Worker: scan leg only. No chat report sent.

## Pre-flight: PASS
- Head via fast_rpc batch (bsc-dataseed1): 132237334; small ankr_getLogs (50 blocks) OK, 401 logs, 4.5s total.
- Pre-flight files: run-2026-11-08-0001-preflight.py/.log/.json
- Canonical onchain_nft_scan.py already carries the 2201 batch patch (rpc_call via fast_rpc.batch) — verified present before running; no re-patch, no patched copy needed this run. Script ran clean on first attempt.

## Scan: SUCCESS, no errors (first attempt, no retry)
- Window claimed: 132236361–132237360 (1000 blocks, most recent only; head at scan start 132237360; pre-flight head 132237334 at 00:03 WIB).
- EFFECTIVE coverage: FULL. 20/20 chunk lines, 0 chunk ERROR lines, errors list empty, partial=False. Max first_block seen in output: NFT 132237340, ERC-20 132237357 — i.e. coverage reaches to within 20/3 blocks of to_block. No Transfer/TransferSingle chunk failure.
- Result: 125 NFT contracts (120 ERC721 + 5 ERC1155, 1105 NFT mints), 348 ERC-20 mint contracts, 40 Ankr calls, partial=False, HIVE Agents NOT found in window.
- Duration: ~14m57s (17:03:34–17:18:31 UTC / 00:03:34–00:18:31 WIB); log phase ~5 min (20 chunk lines), enrichment ~10 min. No stall. Sourcify was flaky during enrichment (many error:IncompleteRead / error:RemoteDisconnected, retried inline by the script) but every contract still got a verdict.
- No re-run needed: first attempt succeeded with full coverage.
- Output: onchain-scan-2026-11-08-0001.json; progress: run-2026-11-08-0001-scan-progress.log.

## Watermark / gap (NOT advanced — backfill owns it)
- onchain-snapshot.json and onchain-scan-state.json NOT written by this leg. Snapshot mtime unchanged (16:55:11Z, pre-run). State mtime moved to 17:07:27Z during the scan — by another process (backfill/other leg), not by this leg.
- No hole inside this run's window. Uncovered by design (window cap): blocks 132233440–132236360 (~2,921 blocks) between run 2331's window end (132233439) and this window's start (132236361) — plus the standing gap 132229264–132232439 (incl. run 2301's 150-block hole 132229264–132229413) — all remain backfill's job; routine scans do not re-cover them.

## Triage: 1 first-seen, 0 EARLY leads
- First-seen = absent from BOTH onchain-scan-seen.json and onchain-snapshot.json (registry address excluded; 1 first-seen + 123 known + 1 registry = 125).
- 0xA791B93157fD62b68fAcd7a4785F27F2E8C53Bb3 — TCG-VAULT Founder (TCGVF), ERC721, 1 mint / 1 minter, first mint 00:02:02 WIB (block 132237149). NOT agent-shaped (no registry bytes, no free shape, Sourcify error:IncompleteRead).
- No same-owner discards among first-seen; no deep checks needed (no registry/free signal). No free views live.
- Seen file: appended 145 new contracts (total nested now 12,075); first-seen address verified present in seen file. Triage files: run-2026-11-08-0001-triage-scan.py/.log/.json.

## 5c (track-C shape check): 0 hits
- ERC-20 total 348; mint_count >= 10: 50; already checked 46; new checked 4 (cap 20, dropped_sampling_limit 0).
- All 4: S1=false, S2=false → no-shape. All 4 Sourcify not_verified with registry_bytes=true (factory template common; unverified = unknown free shape, not agent-shaped on bytecode alone).
- Checked: 0x158eaAf511Cb9e4A6C13FB482bD5951932333363 (71), 0xC44DeFc3f6572D4a015B45aDa65C10e6DbF5FdeB (64), 0x4fD2FAdaB69E2dDD875C672d91286d338E902363 (35), 0x12fE5fFBE0F9a97898855ED9525E8FE1A22727A5 (12).
- Merged into track-c-scan-checked.json (list now 2,781; all 4 of this run's addresses verified present with per-address records). 5c files: run-2026-11-08-0001-5c.py/.log/.json.

## Bottom line for parent
- No EARLY lead, no track-C lead material from this scan leg. Nothing to report to chat from route 4/5c this run.
- No hole to record for this run's window (full coverage). The standing backfill gap (blocks 132229264–132236360 except run 2331's covered 132232440–132233439) is unchanged and remains with backfill.
