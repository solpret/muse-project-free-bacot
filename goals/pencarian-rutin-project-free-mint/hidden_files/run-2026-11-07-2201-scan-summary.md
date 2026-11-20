# Free Bacot run 2201 — scan leg (route 4) + 5c summary
Run: Sat 2026-11-07 ~22:01 WIB. Worker: scan leg only. No chat report sent.

## Pre-flight: PASS
- Head via fast_rpc batch (bsc-dataseed1): 132221526; small ankr_getLogs (50 blocks) OK, 251 logs, 13.8s total.
- Pre-flight files: run-2026-11-07-2201-preflight.py/.log/.json

## Scan attempt 1: FAILED (clean, fast — not a stall)
- onchain_nft_scan.py --blocks 1000 --chunk 50 crashed at startup after ~32s: eth_blockNumber via fast_rpc._single timed out (8s) on ALL 4 dataseeds.
- Verified afterwards: _single fails at 8s even with timeout=15, while fast_rpc.batch() to the same endpoint succeeds in 4.3s (head 132222300). Root cause is the _single connection path, not the endpoints — same pattern as the historical scan stalls (Ankr/direct tests healthy, scan connection stuck).

## Scan attempt 2: SUCCESS (patched script)
- Workaround: local copy onchain_nft_scan_2201.py with rpc_call routed via fast_rpc.batch (fresh connection) instead of _single; everything else byte-identical. Original onchain_nft_scan.py untouched.
- Window: 132221382–132222381 (1000 blocks, head at scan start 132222381).
- Result: 110 NFT contracts (868 NFT mints), 483 ERC-20 mint contracts, 40 Ankr calls, 0 errors, partial=False, HIVE Agents NOT found in window.
- Duration: log phase ~7 min (20 chunks × ~20s), enrichment ~9 min; total ~17 min.
- Output: onchain-scan-2026-11-07-2201.json; progress: run-2026-11-07-2201-scan-progress.log (attempt-1 traceback + attempt-2 chunks/enrichment).

## Watermark / gap (NOT advanced — backfill owns it)
- Watermark in onchain-scan-state.json still 132197165 (backfill-owned; a backfill run was active during this run and may have touched the file — this leg did not write it).
- Skipped gap this run: 132197166–132221381 = 24,216 blocks (window taken from head-999 per the 1000-block cap; gap closes gradually via backfill, not by enlarging the window).
- onchain-snapshot.json NOT written by this leg (mtime predates the run).

## Triage: 3 first-seen, 0 EARLY leads
- First-seen = absent from BOTH onchain-scan-seen.json and onchain-snapshot.json (registry address excluded).
- 0xEF47c2f2bEDAbF7D547A32d91563302567474035 — OPC NFT Green Card (OPCNFT), ERC721, 54 mints / 1 minter, first mint 22:10:21 WIB. NOT agent-shaped (no registry bytes, no free shape, Sourcify not_verified). Not a lead.
- 0x9293756219863F27Daa1363C7BB92C3b3874Ac2b — FREEDROP (FDROP), ERC721, 42 mints / 42 minters, first mint 22:03:48 WIB. Registry bytes hit + agentRegistry() matches, but owner 0xcbcadc7c9897d21fa6e3a8f941f9f271a39598e3 is in same-owner-discards.json → SAME-OWNER DISCARD. Not reported, not in snapshot (per bridge rule).
- 0x4123F0f5ca048780C0c91aBC0c7ac12c77a0bF69 — dotBots (DOTBOT), ERC721, 2 mints / 2 minters, first mint 22:08:06 WIB. Registry() matches; extra verification: Sourcify IS verified (curl 200, 20,583 bytes; the urllib IncompleteRead was a transport artifact). Verified ABI has NO free-mint/free view — mint is paid (unitPrice 0.000136 BNB, tier USD prices, Underpaid error). Live: mintOpen=true, unitPrice=136000000000000 wei, canMint(user)=true, totalMinted 129/2222 MAX_SUPPLY. PAID-ONLY confirmed → NOT a lead.
- Seen file: appended 221 new contracts (total nested now 11,416). Triage files: run-2026-11-07-2201-triage-scan.py/.log/.json.

## 5c (track-C shape check): 0 hits
- ERC-20 total 483; mint_count >= 10: 57; already checked 49; new checked 8 (cap 20, dropped_sampling_limit 0).
- All 8: Sourcify not_verified, S1=false, S2=false → no-shape. All 8 have registry_bytes=true (factory template common; unverified = unknown free shape, not agent-shaped on bytecode alone).
- Checked: 0x3D27E30be05466Dd61c653d618fe439033EAeCf6 (59), 0xE83c2c2123ad350B00E5680d03Df38a3A6036199 (38), 0x7d23aA25fe7027B7eF001fA39AeE50D1db11ED16 (22), 0xB07A65d141A203CAF9b10fDF221c10b1C27A2594 (20), 0xf10922717eE279B36F60Db754c5389b494165E8b (19), 0x76Ff1CfBd38c93c7c88a2674615b89eE81E5Fc94 (19), 0x302B2E51b2Ee5563c9Ea13D25DE9f06DAB4244D1 (11), 0x76fB7Da2055bd41f5857C364b1651bF485dB361B (11).
- Merged into track-c-scan-checked.json (list now 2,659). 5c files: run-2026-11-07-2201-5c.py/.log/.json.

## Bottom line for parent
- No EARLY lead, no track-C lead material from this scan leg. Nothing to report to chat from route 4/5c this run.
- Actionable follow-up (for parent/main agent, not this leg): the unpatched onchain_nft_scan.py is broken as long as fast_rpc._single stalls — every future run will fail at eth_blockNumber unless the batch patch is adopted into the canonical script (or _single is fixed). The patched copy onchain_nft_scan_2201.py works and is preserved for reference.
