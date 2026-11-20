# Hot-leg run 2026-11-18 00:29 WIB — run log

- Run: free-mint-hot-leg 2026-11-18 00:29 WIB (script run-hot-leg-2026-11-18-0029.py, pattern of 00:24 run).
- Elapsed 126.9 s — slightly over the <2 min target (RPC slow: chunk 1 took 47 s via bsc-dataseed.binance.org; all 7 chunks via that endpoint). Logged, run ended, no pile-up.
- Leg 1 Sourcify feed (limit 20, sort desc): top 0x8a44912eCe6b103B56efF98F657e24D7C4016B04, verified 2026-11-17T17:30:41Z. 1 new contract; shape-check S1 false / S2 false (has mint, no quote, no free views, no agent ref, not token) — NOT a sale shape. Recorded in hot-leg-seen.json (16,034 entries). No leg-3 on-chain verify needed (no S1/S2 hit). No lead, no candidate.
- Leg 2 Boltbook EN + ZH (boltbook.fun, direct fetch, HTTP 200, 45,436 / 45,624 bytes): 12 EN / 13 ZH full addresses, 0 new (all already in hot-leg-seen). Figures: THYRK 4.414/7.896 free (55.9%), Chipmunks 3.363/6.659 (50.5%), Navigara 949/2.162 (43.9%) — all three names already in the main snapshot (tracked by the main 30-min job, not new here); "1% Club opened at midnight — 24 minted in 20 min / free 1/10" — no contract address attached to the figure and not in the snapshot; no shape-checkable lead from the front page (all page addresses already seen). Noted for the main job's Boltbook sweep; no report from this run.
- Bridge leg (read-only): 116 contracts, 0 not in snapshot, 7 same_owner_discarded. No complementary-scan finding to promote.
- Leg 4 re-read (25-item focus set + BSCCAT + PEPE), block 134160159, 25/25 OK, 0 chunk errors. Only change vs 00:24 run: RaceAgents freeMinted 631 → 632, totalSupply 631 → 632 (+1 mint — no threshold crossing, no sellout, no slot change; no report). BSCCAT: no changes. PEPE: no changes.
- Threshold check: PunchCard 23.1%, AGCLUB 58.9%, Matrix 58.8% (age-excluded 16 Nov), PIXELFROGS 15.1% — none above the 70% strong-lead bar. No promotion, no strong lead, no candidate.
- Poffzi FCFS: NO PROCESS FOUND (expected — no sale armed; Poffzi sale ended 16 Nov).
- Executions: none — no preview, no mint, no claim (read-only run). No chat report (nothing new: no lead, candidate, pending claim, change, or blocked auto-mint/claim).
- Outputs: hot-leg-run-2026-11-18-0029.json, hot-leg-run-2026-11-18-0029-reread.json, run-hot-leg-2026-11-18-0029.py, this runlog. Main snapshot / main seen files untouched.
