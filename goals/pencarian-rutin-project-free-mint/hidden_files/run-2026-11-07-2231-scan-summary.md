# Free Bacot run 2231 — scan leg (route 4) + 5c summary
Run: Sat 2026-11-07 ~22:31 WIB. Worker: scan leg only. No chat report sent.

## Pre-flight: PASS
- Head via fast_rpc batch (bsc-dataseed1): 132225827; small ankr_getLogs (50 blocks) OK, 210 logs, 4.4s total.
- Pre-flight files: run-2026-11-07-2231-preflight.py/.log/.json
- Canonical onchain_nft_scan.py already carries the 2201 batch patch (rpc_call via fast_rpc.batch, lines 34/51-57) — verified before running; no re-patch, no patched copy needed this run. Script ran clean on first attempt.

## Scan: SUCCESS (first attempt, no retry)
- Window: 132224859–132225858 (1000 blocks, most recent only; head at scan start 132225858).
- Result: 117 NFT contracts (112 ERC721 + 5 ERC1155, 1275 NFT mints), 371 ERC-20 mint contracts, 39 Ankr calls, partial=False, HIVE Agents NOT found in window.
- Errors: 1 transient — `ERROR TransferSingle chunk 132225309-132225358: Remote end closed connection without response` (chunk still completed; counts present in that chunk's line). No stall; log phase ~7 min (20 chunks), enrichment ~10 min; total ~17 min.
- Output: onchain-scan-2026-11-07-2231.json; progress: run-2026-11-07-2231-scan-progress.log (22 chunk lines incl. header).

## Watermark / gap (NOT advanced — backfill owns it)
- onchain-scan-state.json and onchain-snapshot.json NOT written by this leg (mtimes predate the run: state 15:51:36Z, snapshot 15:33:12Z).
- Skipped gap this run: window taken from head-999 per the 1000-block cap; backfill owns the watermark and closes the gap gradually.

## Triage: 1 first-seen, 0 EARLY leads
- First-seen = absent from BOTH onchain-scan-seen.json and onchain-snapshot.json (registry address excluded).
- 0xcfE5E4925A76A3AA11aFA79e04c6fad3611cee40 — REWARD (RWD), ERC721, 4 mints / 4 minters, first mint 22:33:02 WIB (block 132225284). Registry bytes hit + agentRegistry() matches the registry address, Sourcify ABI fetch hit IncompleteRead transport error (8977/15578 bytes) — but owner 0xcbcadc7c9897d21fa6e3a8f941f9f271a39598e3 is in same-owner-discards.json → SAME-OWNER DISCARD (same owner as FREEDROP 2201). Not reported, not in snapshot (per bridge rule). No free views live.
- Tri333 (0x157D860e30b6c6d4dC0abe3bD6e66e659A9d524f) appears in this window (enrich 5/117) but is NOT first-seen — already in snapshot / minted by user 22:46 WIB (Tri333 #590) — correctly excluded from first-seen.
- Seen file: appended 154 new contracts (total nested now 11,574). Triage files: run-2026-11-07-2231-triage-scan.py/.log/.json.

## 5c (track-C shape check): 0 hits
- ERC-20 total 371; mint_count >= 10: 58; already checked 51; new checked 7 (cap 20, dropped_sampling_limit 0).
- All 7: S1=false, S2=false → no-shape. 6 Sourcify not_verified with registry_bytes=true (factory template common; unverified = unknown free shape, not agent-shaped on bytecode alone). 1 verified (0x55769Fc8537e4cB2021a8F637741e57d4120F547, mint_count 12): ABI has mint() only, no quote/free/gate fns, registry_bytes=false.
- Checked: 0x068875a0b78ecc5088209d381447d5B8356794a5 (51), 0xDAD2ab4FEDEf842176af4d617AF1A9bcCa5688d2 (44), 0xa50CAc8627d0A961b1354C41b312C483289147Fc (44), 0xaE6608a9796C1d0c5a295633aB694DF35aaE51f4 (23), 0xBAeFD63E8296d4CaABA25003d061EeC8E2a72F89 (13), 0x55769Fc8537e4cB2021a8F637741e57d4120F547 (12), 0xB68CA6A183E39d4a09B06E6318c63572af54269E (10).
- Merged into track-c-scan-checked.json (list now 2,666). 5c files: run-2026-11-07-2231-5c.py/.log/.json.

## Bottom line for parent
- No EARLY lead, no track-C lead material from this scan leg. Nothing to report to chat from route 4/5c this run.
- Note: canonical onchain_nft_scan.py now carries the batch patch, so the 2201 workaround (patched copy) is no longer needed — first-attempt success this run confirms it.
