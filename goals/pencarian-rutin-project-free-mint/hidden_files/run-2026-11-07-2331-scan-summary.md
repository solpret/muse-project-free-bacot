# Free Bacot run 2331 — scan leg (route 4) + 5c summary
Run: Sat 2026-11-07 ~23:31 WIB. Worker: scan leg only. No chat report sent.

## Pre-flight: PASS
- Head via fast_rpc batch (bsc-dataseed1): 132233407; small ankr_getLogs (50 blocks) OK, 216 logs, 4.9s total.
- Pre-flight files: run-2026-11-07-2331-preflight.py/.log/.json
- Canonical onchain_nft_scan.py already carries the 2201 batch patch (rpc_call via fast_rpc.batch) — verified in run 2301; no re-patch, no patched copy needed this run. Script ran clean on first attempt.

## Scan: SUCCESS, no errors (first attempt, no retry)
- Window claimed: 132232440–132233439 (1000 blocks, most recent only; head at scan start 132233439; pre-flight head 132233407 at 23:33 WIB).
- EFFECTIVE coverage: FULL. 20/20 chunk lines, 0 ERROR lines, errors list empty, partial=False. Max first_block seen in output: NFT 132233438, ERC-20 132233432 — i.e. coverage reaches to within 1–7 blocks of to_block. No Transfer/TransferSingle chunk failure, unlike run 2301's breaking Transfer error.
- Result: 142 NFT contracts (136 ERC721 + 6 ERC1155, 953 NFT mints), 442 ERC-20 mint contracts, 40 Ankr calls, partial=False, HIVE Agents NOT found in window.
- Duration: ~17m25s (16:34:10–16:51:35 UTC / 23:34:10–23:51:35 WIB); log phase ~5 min (20 chunk lines), enrichment ~12 min. No stall.
- No re-run needed: first attempt succeeded with full coverage.
- Output: onchain-scan-2026-11-07-2331.json; progress: run-2026-11-07-2331-scan-progress.log.

## Watermark / gap (NOT advanced — backfill owns it)
- onchain-snapshot.json and onchain-scan-state.json NOT written by this leg. Snapshot mtime unchanged (16:26:31Z, pre-run). State mtime moved to 16:51:08Z during the scan — by another process (backfill/other leg), not by this leg.
- No hole inside this run's window. Uncovered by design (window cap): blocks 132229414–132232439 (~3,026 blocks) between run 2301's window end (132229413) and this window's start (132232440), plus run 2301's 150-block Transfer hole (132229264–132229413) — both remain backfill's job; routine scans do not re-cover them.

## Triage: 1 first-seen, 0 EARLY leads
- First-seen = absent from BOTH onchain-scan-seen.json and onchain-snapshot.json (registry address excluded; 1 first-seen + 140 known + 1 registry = 142).
- 0x56155fd1818b31256E7f435956D6dff5C732f35f — OinkHash Pigs (OINK), ERC721, 21 mints / 21 minters, first mint 23:26:44 WIB (block 132232444). NOT agent-shaped (no registry bytes, no free shape, Sourcify error:IncompleteRead).
- No same-owner discards among first-seen; no deep checks needed (no registry/free signal). No free views live.
- Seen file: appended 169 new contracts (total nested now 11,926); first-seen address verified present in seen file. Triage files: run-2026-11-07-2331-triage-scan.py/.log/.json.

## 5c (track-C shape check): 0 hits
- ERC-20 total 442; mint_count >= 10: 47; already checked 36; new checked 11 (cap 20, dropped_sampling_limit 0).
- All 11: S1=false, S2=false → no-shape. 9 Sourcify not_verified with registry_bytes=true (factory template common; unverified = unknown free shape, not agent-shaped on bytecode alone); 2 verified (0xFEc8b048EfB92DaAA0fA096c7c27FB55990dD339, no mint/quote/free/gate fns; 0x84d3e0cCa0742c39ACcCE5BbF677C1fcE908140D, mint fn only, no quote/free/gate) with registry_bytes=false.
- Checked: 0xcC7F7E4C6080EBe63756562cA173d72a2b69A6D0 (90), 0xF82E981AF02E7ee87e2C90cc5bae34c605715aFE (54), 0x05A96366b4554933e3238B8caE7F4406f0550d59 (51), 0xea22F3B7253Ae40f9181AF69a54F95852113bC81 (19), 0x1552bB1C2Ad4B9Fa7d0d03BC0100FeF884E0Bf4f (17), 0xFEc8b048EfB92DaAA0fA096c7c27FB55990dD339 (12), 0xFD7afe6f0462966E911B1DaE22D55Bd6030f69D8 (12), 0x614dE853F21C8FFF482331A0B3Fa13ED134EAB36 (12), 0x8Db2DBC15dBD3982Ad82E7f9cFf5065966e9e50c (11), 0x84d3e0cCa0742c39ACcCE5BbF677C1fcE908140D (10), 0x19023937c55cbAA54ECd85554c5bA033B1791bE5 (10).
- Merged into track-c-scan-checked.json (list now 2,739; all 11 of this run's addresses verified present with per-address records). 5c files: run-2026-11-07-2331-5c.py/.log/.json.

## Bottom line for parent
- No EARLY lead, no track-C lead material from this scan leg. Nothing to report to chat from route 4/5c this run.
- No hole to record for this run's window (full coverage). The standing backfill gap (blocks 132229264–132232439, incl. run 2301's 150-block hole) is unchanged and remains with backfill.
