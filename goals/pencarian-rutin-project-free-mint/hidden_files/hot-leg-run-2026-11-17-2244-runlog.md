# Hot-leg run 2026-11-17 22:44 WIB (scheduled 22:44:38) — SILENT (no reportable change)

Elapsed 29.7s (target <2 min). Script: hot-leg-run-2026-11-17-2244.py (cloned from 2239 run, PREV_* -> 2239); output JSON: hot-leg-run-2026-11-17-2244.json; reread: hot-leg-run-2026-11-17-2244-reread.json (block 134146242, 111 calls, 0 errors).

## Leg 1 — Sourcify feed
- 20 contracts, top 0xa607CD1B7E0e3Bd3aF25CBbd02a18dd10FB31993 (verified 2026-11-17T15:45:41Z, exact_match).
- 2 new: 0xa607CD1B7E0e3Bd3aF25CBbd02a18dd10FB31993 (10 fns, mint=True, quote=False, freeview=False, regfn=False) and 0x92CA7597851ecBB744191b90C5178380c646348b (62 fns, mint=False). Shape-check: S1=False S2=False for both -> NOT sale shape. Recorded in hot-leg-seen.json (15990 -> 15992). No lead.

## Leg 2 — Boltbook
- EN 45,990 bytes / ZH 45,969 bytes, 11 / 9 addresses, 0 new. No new leads.

## Leg 3 — on-chain verify new sale-shape
- None (no shape hits). No preview/mint/claim.

## Leg 4 — re-read vs 2239
- 1 value-change:
  - **PunchCard totalMinted/totalSupply 1287 -> 1288, freeMinted 1269 -> 1270 (+1).** Minor, not reportable (free 22.9%, far below the >70% strong-lead bar; slot still open, mintPriceFor(user,1)=0, balanceOf_user 0).
- BoldLeonidas unchanged (totalSupply still 1111/1111 MAX_SUPPLY — sellout already reported once at 22:39, recorded in hot-leg-reported.json as 0x84bc...#sellout-20261117-2239; stay silent).
- PEPE unchanged (freeMinted 500/500, hasMinted_user 1).
- BSCCat unchanged (freeMinted 519, totalSupply 519M tokens; non-existent-function reverts identical to 2239).
- binanceai-mint unchanged: launched 0, failed 1, isRefundPhase 1 (refund/failed already reported 2026-11-02 20:24).
- Thresholds: AGCLUB 58.8%, Matrix 58.7%, PunchCard 22.9%, PIXELFROGS 15.1% — all below the >70% strong-lead bar; no promotion. Ledgera_free_pct null.

## Bridge (read-only)
- scan-bridge.json: 116 contracts, 0 not in snapshot, 7 same_owner_discarded. Nothing to report; no "temuan pelengkap scan" promotion.

## Other
- Poffzi FCFS: NO PROCESS FOUND (expected — sale ended 16 Nov, terminal state).
- Executions: none — no preview, no mint, no claim (read-only run).

## Outcome
SILENT — no new lead, candidate, pending claim, change, or blocked auto-mint/auto-claim. Only a +1 PunchCard mint, below every reporting threshold.
