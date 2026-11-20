# Hot-leg run 2026-11-17 23:14 WIB (scheduled 23:14:38) — SILENT (no reportable change)

Script elapsed 34.3s (WITHIN the <2 min target; leg-4 RPC 20.1s). Script: hot-leg-run-2026-11-17-2314.py (cloned from 2304 run, PREV_* -> 2304); output JSON: hot-leg-run-2026-11-17-2314.json; reread: hot-leg-run-2026-11-17-2314-reread.json (block 134150263, 28 items, 0 RPC errors, 128 calls).

## Leg 1 — Sourcify feed
- Feed top 0x1e20710795233f3e5FA896E83f51CF161Ce14D44 (verified 2026-11-17T16:14:38Z). 3 new vs seen: 0x1e20710795233f3e5FA896E83f51CF161Ce14D44 (21 fns), 0xCFF056C3342daff0d5e1206A255B112b0dA543e5 (51 fns), 0xB4478B51137a4c13B460c813E9954e12E4D561c0 (40 fns) — all S1=False S2=False (mint=False, quote=False, freeview=False, regfn=False). No shape hits, no lead.
- Seen: 16003 -> 16006.

## Leg 2 — Boltbook
- EN 44,650 bytes / ZH 44,798 bytes, 6 / 6 addresses (identical sets), 0 new. No lead.

## Leg 3 — on-chain verify new sale-shape
- None (no shape hits). No preview/mint/claim.

## Leg 4 — re-read vs 2304 (28 items)
- Value-changes (mint-count increments only, none tier-changing):
  - Kryntar totalMinted 1368 -> 1369, standardRemaining 743 -> 742 (legendaryRemaining 111, mintOpen 1).
  - RigForge freeClaimed 373 -> 374, freeSharesLeft 627 -> 626 (freeBooked_user 10000000000000000000000).
- Thresholds: PunchCard 23.0%, AGCLUB 58.8%, Matrix 58.8%, PIXELFROGS 15.1%, XCOPY 40.6%, ALIEN 46.7% — all below the >70% strong-lead bar; no promotion.
- Unchanged: PEPE freeMinted 500/500, soldShares 501, opened 0, hasMinted_user 1; BSCCat freeMinted 519, totalSupply 519000000000000000000000000, balanceOf_user 0 (sale views still revert, same as 2304 — no change); binanceai-mint launched 0, failed 1, isRefundPhase 1 (unchanged, already in refund/failed phase).
- BNBG totalMinted still null (same as 2304) — persistent read anomaly, not a state change.

## Bridge (read-only)
- scan-bridge.json: 116 contracts, 0 not in snapshot, 7 same_owner_discarded. Nothing to report; no "temuan pelengkap scan" promotion.

## Other
- Poffzi FCFS: NO PROCESS FOUND (expected — sale ended 16 Nov, terminal state).
- Executions: none — no preview, no mint, no claim (read-only run).
