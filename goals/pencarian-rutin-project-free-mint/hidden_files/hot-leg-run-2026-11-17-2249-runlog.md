# Hot-leg run 2026-11-17 22:49 WIB (scheduled 22:49:38) — SILENT (no reportable change)

Elapsed 26.3s (target <2 min). Script: hot-leg-run-2026-11-17-2249.py (cloned from 2244 run, PREV_* -> 2244); output JSON: hot-leg-run-2026-11-17-2249.json; reread: hot-leg-run-2026-11-17-2249-reread.json (block 134146695, 111 calls, 0 errors).

## Leg 1 — Sourcify feed
- 20 contracts, top 0x61d25a659677f8dD770683698FD584e1B46E2ddc (verified 2026-11-17T15:51:30Z, exact_match).
- 1 new: 0x61d25a659677f8dD770683698FD584e1B46E2ddc (7 fns, mint=False, quote=False, freeview=False, regfn=False). Shape-check: S1=False S2=False -> NOT sale shape. Recorded in hot-leg-seen.json (15992 -> 15994, with the Boltbook one below). No lead.

## Leg 2 — Boltbook
- EN 44,990 bytes / ZH 45,473 bytes, 9 / 9 addresses, 1 new.
- New: 0x72ec6f6e06e6f79ff312e92b7451d829405327bd (ZH only). Shape-check: no ABI from Sourcify -> NOT sale shape. Recorded in hot-leg-seen.json. No lead.

## Leg 3 — on-chain verify new sale-shape
- None (no shape hits). No preview/mint/claim.

## Leg 4 — re-read vs 2244
- 1 value-change:
  - **PunchCard totalMinted/totalSupply 1288 -> 1290, freeMinted 1270 -> 1272 (+2).** Minor, not reportable (free 22.9%, far below the >70% strong-lead bar; slot still open, mintPriceFor(user,1)=0, balanceOf_user 0).
- BoldLeonidas unchanged (totalSupply still 1111/1111 MAX_SUPPLY — sellout already reported once at 22:39, recorded in hot-leg-reported.json as 0x84bc...#sellout-20261117-2239; stay silent).
- PEPE unchanged (freeMinted 500/500, hasMinted_user 1).
- BSCCat unchanged (freeMinted 519, totalSupply 519M tokens; non-existent-function reverts identical to 2244).
- binanceai-mint unchanged: launched 0, failed 1, isRefundPhase 1 (refund/failed already reported 2026-11-02 20:24).
- Thresholds: AGCLUB 58.8%, Matrix 58.7%, PunchCard 22.9%, PIXELFROGS 15.1% — all below the >70% strong-lead bar; no promotion. Ledgera_free_pct null.

## Bridge (read-only)
- scan-bridge.json: 116 contracts, 0 not in snapshot, 7 same_owner_discarded. Nothing to report; no "temuan pelengkap scan" promotion.

## Other
- Poffzi FCFS: NO PROCESS FOUND (expected — sale ended 16 Nov, terminal state).
- Executions: none — no preview, no mint, no claim (read-only run).

## Outcome
SILENT — no new lead, candidate, pending claim, change, or blocked auto-mint/auto-claim. Only a +2 PunchCard mint, below every reporting threshold.
