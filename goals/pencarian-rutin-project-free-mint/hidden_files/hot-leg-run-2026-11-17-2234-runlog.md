# Hot-leg run 2026-11-17 22:34 WIB (scheduled 22:34:38) — SILENT

Elapsed 24.3s (target <2 min). Script: hot-leg-run-2026-11-17-2234.py; output JSON: hot-leg-run-2026-11-17-2234.json; reread: hot-leg-run-2026-11-17-2234-reread.json (block 134144829, 117 calls, 0 errors).

## Leg 1 — Sourcify feed
- 20 contracts, top 0xa85c056af39818C936E9DBDA07C5C941d751dE10 (verified 2026-11-17T15:34:26Z, exact_match).
- 1 new: 0xa85c056af39818C936E9DBDA07C5C941d751dE10. Shape-check: S1=False S2=False (32 fns, mint=True, quote=False, freeview=False, regfn=False) → NOT sale shape. Recorded in hot-leg-seen.json (15987 → 15988). No lead.

## Leg 2 — Boltbook
- EN 45,997 bytes / ZH 47,025 bytes, 9 addresses each, 0 new. No new leads.

## Leg 3 — on-chain verify new sale-shape
- None (no shape hits). No preview/mint/claim.

## Leg 4 — re-read vs 2229
- Only 2 minor value-changes, neither a reportable change type:
  - SPARKS totalSupply 1151 → 1152 (+1).
  - BoldLeonidas totalSupply 998 → 1075 (+77 in 5 min; also +72 in the 2224→2229 window), mintOpen 1, balanceOf_user 0. No free-pool view in the hot-leg ITEMS set, so no free-% assessment from this leg; main 30-min job tracks it. User slot not taken.
- PEPE unchanged (freeMinted 500/500, hasMinted_user 1).
- binanceai-mint unchanged: launched 0, failed 1, isRefundPhase 1 (refund/failed already reported 2026-11-02 20:24).
- Thresholds: AGCLUB 58.8%, Matrix 58.7%, PunchCard 22.8%, PIXELFROGS 15.1% — all below the >70% strong-lead bar; no promotion. Ledgera_free_pct null (FREE_SUPPLY not in ITEMS; Ledgera unchanged this run).
- BSCCat: freeMinted 518 → 519, totalSupply 518M → 519M tokens (verified via reread files). NOTE: bsccat_changes_vs_2229 in the run JSON reads {} because the 2229 run JSON has NO bsccat_probe key (later variant dropped it), so the probe comparison found no previous probe. The real +1 change is confirmed from the reread files. This run's JSON restores the bsccat_probe key, so the next run's comparison will work again. Minor +1 mint, not reportable.

## Bridge (read-only)
- scan-bridge.json: 116 contracts, 0 not in snapshot, 7 same_owner_discarded. Nothing to report; no "temuan pelengkap scan" promotion.

## Other
- Poffzi FCFS: NO PROCESS FOUND (expected — sale ended 16 Nov, terminal state).
- Executions: none — no preview, no mint, no claim (read-only run).

## Outcome
SILENT — no new lead, candidate, pending claim, change, or blocked auto-mint/auto-claim. No chat report.
