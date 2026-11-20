# Hot-leg run 2026-11-17 23:04 WIB (scheduled 23:04:38) — SILENT (no reportable change)

Script elapsed 206.9s (OVER the <2 min target; leg-4 RPC alone took 107.7s — slow RPC, same cause as earlier overruns). Script: hot-leg-run-2026-11-17-2304.py (cloned from 2254 run, PREV_* -> 2254); output JSON: hot-leg-run-2026-11-17-2304.json; reread: hot-leg-run-2026-11-17-2304-reread.json (block 134149636, 28 items, 0 RPC errors).

## Leg 1 — Sourcify feed
- Feed top 0x5Ebb41B6F2B1b25bdE7A6101B0cC238D92b251f4 (verified 2026-11-17T16:10:10Z). 3 new vs seen: 0x5Ebb41B6F2B1b25bdE7A6101B0cC238D92b251f4 (6 fns), 0xB750406838c8a9E44AEc1119f61F3CD99f2c033b (no ABI from Sourcify), 0xae8376c6E15D979aC7cE813aADff459d8a2c777C (62 fns) — all S1=False S2=False (mint=False, quote=False, freeview=False, regfn=False). No shape hits, no lead.
- Seen: 16000 -> 16003.

## Leg 2 — Boltbook
- EN 44,807 bytes / ZH 45,006 bytes, 6 / 6 addresses (identical sets), 0 new. No lead.

## Leg 3 — on-chain verify new sale-shape
- None (no shape hits). No preview/mint/claim.

## Leg 4 — re-read vs 2254 (28 items)
- Value-changes (mint-count increments only, none tier-changing):
  - AgentBubble totalMinted 1996 -> 2008, freeMinted 1851 -> 1863, totalSupply 1996 -> 2008.
  - SPARKS totalSupply 1152 -> 1153. CPASS totalMinted 1770 -> 1771. MORFO totalMinted 1084 -> 1086. Zephyra totalMinted 980 -> 981.
  - PunchCard totalMinted 1292 -> 1293, freeMinted 1274 -> 1275 (free 23.0%, slot open, mintPriceFor(user,1)=0, balanceOf_user 0).
  - XCOPY totalMinted/totalSupply 446 -> 447 (40.6% of MAX 1100). ALIEN totalSupply 455 -> 467 (46.7% of FREE_SUPPLY 1000).
  - BNBG totalMinted 69 -> null: READ ANOMALY (view returned null this run), not a state change — re-check next run; do not treat as sellout/loss.
- Thresholds: PunchCard 23.0%, AGCLUB 58.8%, Matrix 58.8%, PIXELFROGS 15.1%, XCOPY 40.6%, ALIEN 46.7% — all below the >70% strong-lead bar; no promotion.
- Unchanged: PEPE freeMinted 500/500, opened 0, hasMinted_user 1; BSCCat freeMinted 519 (pool not open); BoldLeonidas sellout already reported once.

## Bridge (read-only)
- scan-bridge.json: 116 contracts, 0 not in snapshot, 7 same_owner_discarded. Nothing to report; no "temuan pelengkap scan" promotion.

## Other
- Poffzi FCFS: NO PROCESS FOUND (expected — sale ended 16 Nov, terminal state).
- Executions: none — no preview, no mint, no claim (read-only run).
