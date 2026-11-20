# free-mint-hot-leg run 2026-11-18 03:29 WIB

- Elapsed 46.7 s, block 134184030. No preview, no mint, no claim.
- Leg 1 Sourcify feed (20 contracts, top verifiedAt 2026-11-17T20:21:56Z — same top as 03:24, no new verifications in 5 min): 0 new. Recorded nothing.
- Leg 2 Boltbook EN 44.549 byte (HTTP 200) + ZH 42.911 byte (HTTP 200): 12 / 12 full-address contracts, 1 new — 0xeef7fced309ab0a08e781d5656476a45583298c2, verified a tx-hash regex artifact (full 66-char hash 0xeef7...e9b3d6a0e174a7c301d0dee1 in a post), recorded as checked-not-contract, never shape-checked. Figures: FIND exp39 151/300 (was 150/300 at 03:24, seals 04:00 WIB — age-excluded, DIAM), Lion's Share 1.153/1.450 flat, STOCK AGENT 540/2.222, one "Sold out 11.000/11.000" post (teguhap18.ai, no new contract attached) — all already known. No new free-mint post.
- Leg 3: no shape hits, no leads.
- Leg 4 re-read vs 03:24 (read-only, snapshot NOT rewritten; 125 calls, 0 chunk errors; null-retry attempted 0 — this run had no nulls):
  - The only diffs vs 03:24 are null→value recoveries of the 03:24 transient RPC nulls, all matching the values the 03:24 targeted retry had already confirmed: PunchCard (9 views: totalSupply 1312 / freeMinted 1290 / mintOpen 1 / mintPriceFor 0 / mintedCount 0), RigForge (freeSharesLeft 625 / freeClaimed 375), PIXELFROGS (456 / 454 / freeLeft 2546 / mintOpen 0), Flare-bd6f totalSupply 4900, HAPPE freeMinted 222. NOT state changes.
  - Real movement: none. Matrix freeMinted 592 / freeRemaining 408 / totalSupply 589 (unchanged), REOPIR 585 (unchanged), Stromboat 175 (unchanged), bsccat/pepe unchanged, binanceai launched still 0 (pending claim, not open).
- Threshold check: PunchCard 23,2% (1290/5555, slot open but age-excluded), AGCLUB 59,2%, Matrix 59,2%, AgentBubble 84,4% but launch age still UNVERIFIED — no strong-lead promotion. PIXELFROGS 15,1%.
- Bridge (read-only): 116 contracts, 0 not in snapshot, 7 same_owner_discarded — no complement finding, nothing to promote.
- Poffzi FCFS: no process found (informational only; sale ended 16 Nov).
- Result: SILENT run — no new lead, candidate, pending claim, change, or blocked auto-mint/auto-claim to report.
- Files: hot-leg-2026-11-18-0329-run.py, hot-leg-run-2026-11-18-0329.json, hot-leg-run-2026-11-18-0329-reread.json, boltbook EN/ZH html snapshots, hot-leg-2026-11-18-0329-run.stdout.log / .stderr.log. hot-leg-seen.json 16.121 -> 16.122 entries. Note: this run's script compares the leg-4 diff against the 0324 reread file (fixed vs the 0324 script's hardcoded 0314 comparison) and carries a built-in transient-null retry against bsc-dataseed1.defibit.io.
