# Free Bacot run 2301 — scan leg (route 4) + 5c summary
Run: Sat 2026-11-07 ~23:01 WIB. Worker: scan leg only. No chat report sent.

## Pre-flight: PASS
- Head via fast_rpc batch (bsc-dataseed1): 132229361; small ankr_getLogs (50 blocks) OK, 365 logs, 9.7s total.
- Pre-flight files: run-2026-11-07-2301-preflight.py/.log/.json
- Canonical onchain_nft_scan.py already carries the 2201 batch patch (rpc_call via fast_rpc.batch, lines 34/51-57) — verified before running; no re-patch, no patched copy needed this run. Script ran clean on first attempt.

## Scan: SUCCESS with 1 data-loss error (first attempt, no retry)
- Window claimed: 132228414–132229413 (1000 blocks, most recent only; head at scan start 132229413).
- EFFECTIVE Transfer coverage: 132228414–132229263 only (850 blocks). Chunk 132229264–132229313 failed with `ERROR Transfer chunk 132229264-132229313: Remote end closed connection without response` and the script's Transfer-error handler `break`s the chunk loop — the remaining 3 chunks (132229264–132229413, 150 blocks) were never scanned for Transfer or TransferSingle. Max first_block seen in output: NFT 132229235, ERC-20 132229261. No contract/ERC-20 in output has first_block >= 132229264. The output JSON still reports partial=False (script sets that on completion; the loss is visible only via the errors list + first_block ceiling). Unlike run 2231, whose error was TransferSingle (non-breaking), this run's error was Transfer (breaking).
- Result: 132 NFT contracts (125 ERC721 + 7 ERC1155, 558 NFT mints), 393 ERC-20 mint contracts, 34 Ankr calls, partial=False (see caveat above), HIVE Agents NOT found in window.
- Duration: ~19m35s (16:03:57–16:23:32 UTC); log phase ~5 min (17 chunk lines), enrichment ~14 min. No stall.
- No re-run: a full re-run would have finished after the next routine run's start and risked concurrent read-modify-write collisions on the shared seen / track-c files (other run-2301 legs were writing them concurrently). The 150-block hole is recorded here for the parent/backfill.
- Output: onchain-scan-2026-11-07-2301.json; progress: run-2026-11-07-2301-scan-progress.log (419 lines incl. header).

## Watermark / gap (NOT advanced — backfill owns it)
- onchain-scan-state.json and onchain-snapshot.json NOT written by this leg. Snapshot mtime unchanged (16:00:08Z, pre-run). State mtime moved to 16:21:39Z during the scan — by another process (backfill/other leg), not by this leg.
- Skipped gap this run: 150 blocks (132229264–132229413) lost to the Transfer error, on top of the usual head-999 cap; backfill owns the watermark and closes gaps gradually.

## Triage: 4 first-seen, 0 EARLY leads
- First-seen = absent from BOTH onchain-scan-seen.json and onchain-snapshot.json (registry address excluded; the registry itself accounts for the 132nd contract: 4 first-seen + 127 known + 1 registry).
- 0x09e685Ddc0a1cD96D1026FF8C5357360960F3444 — MooDengMarch (MOO), ERC721, 2 mints / 2 minters, first mint 22:58:15 WIB (block 132228646). NOT agent-shaped (no registry bytes, no free shape, Sourcify not_verified).
- 0x415102fDf8d7C4680292bdC1e8F6f65166Ac0820 — AgentCard Miner (ACPM), ERC721, 1 mint / 1 minter, first mint 22:56:43 WIB (block 132228442). NOT agent-shaped (no registry bytes, no free shape, Sourcify not_verified).
- 0x22E435d8923D807b3256276bBbf904deDbCaC43f — Rift Beasts (RBEAST), ERC721, 1 mint / 1 minter, first mint 22:58:17 WIB (block 132228650). NOT agent-shaped (no registry bytes, no free shape, Sourcify error:RemoteDisconnected).
- 0xeeF92a7BF64b640968A22f0c38c617F04e074a12 — Chizong Miner (CMINER), ERC721, 1 mint / 1 minter, first mint 22:58:53 WIB (block 132228730). NOT agent-shaped (no registry bytes, no free shape, Sourcify not_verified).
- No same-owner discards among first-seen; no deep checks needed (no registry/free signal on any). No free views live.
- Seen file: appended 168 new contracts (total nested now 11,750; 8 of the growth came from concurrent legs before triage wrote). Triage files: run-2026-11-07-2301-triage-scan.py/.log/.json.

## 5c (track-C shape check): 0 hits
- ERC-20 total 393; mint_count >= 10: 43; already checked 37; new checked 6 (cap 20, dropped_sampling_limit 0).
- All 6: S1=false, S2=false → no-shape. All 6 Sourcify not_verified with registry_bytes=true (factory template common; unverified = unknown free shape, not agent-shaped on bytecode alone).
- Checked: 0x79b00ce26695013F640F1F86D64e3805823D9250 (57), 0x061414036Dc544dB38Ed4E2cFD213C910c81a013 (54), 0x25f6E7138b2C8bA06FD51C3826D01830EED9F4Fe (40), 0x9050b8c3a4C5fC4Ca66A1B79E5545163Afc01192 (36), 0xb0eAFC1C6746541dD65C8D4CD6500B7Eeb68424b (28), 0xdD40BeBF8A367B399789e7dfCdFD05dc75835436 (10).
- Merged into track-c-scan-checked.json (list now 2,709 at verification; includes concurrent writes from other legs — all 6 of this run's addresses verified present with per-address records). 5c files: run-2026-11-07-2301-5c.py/.log/.json.

## Bottom line for parent
- No EARLY lead, no track-C lead material from this scan leg. Nothing to report to chat from route 4/5c this run.
- Needs parent attention: the 150-block Transfer hole (132229264–132229413) — first-seen contracts whose first mint fell in those blocks were missed this run and will only surface via backfill triage (routine scans will not re-cover them, since the next run's window starts at head-999). If the parent wants, a targeted re-scan of that slice (script currently only supports latest-N windows) or a backfill priority bump would close it.
