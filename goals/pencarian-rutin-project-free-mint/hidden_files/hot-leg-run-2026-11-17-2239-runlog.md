# Hot-leg run 2026-11-17 22:39 WIB (scheduled 22:39:38) — 1 REPORTABLE CHANGE (sellout)

Elapsed 19.1s (target <2 min). Script: hot-leg-run-2026-11-17-2239.py (cloned from 2234 run, PREV_* -> 2234); output JSON: hot-leg-run-2026-11-17-2239.json; reread: hot-leg-run-2026-11-17-2239-reread.json (block 134145532, 111 calls, 0 errors).

## Leg 1 — Sourcify feed
- 20 contracts, top 0x14A34231612242C19dB494764D9601D423F27777 (verified 2026-11-17T15:42:40Z, exact_match).
- 1 new: 0x14A34231612242C19dB494764D9601D423F27777. Shape-check: S1=False S2=False (22 fns, mint=False, quote=False, freeview=False, regfn=False) -> NOT sale shape. Recorded in hot-leg-seen.json (15988 -> 15990 with Boltbook new below). No lead.

## Leg 2 — Boltbook
- EN 46,266 bytes / ZH 46,448 bytes, 11 addresses each, 1 new: 0xa8ae91fd46188a887229151399b7e750b6f7961e. Shape-check: no-abi-from-sourcify -> S1/S2 False, NOT sale shape. Recorded in hot-leg-seen.json. No new leads.

## Leg 3 — on-chain verify new sale-shape
- None (no shape hits). No preview/mint/claim.

## Leg 4 — re-read vs 2234
- 2 value-changes:
  - **BoldLeonidas totalSupply 1075 -> 1111 = MAX_SUPPLY 1111 — SOLD OUT (reportable, reported once this run; see below).** Verified independently on 2 endpoints (bsc-dataseed1 + publicnode): totalSupply 1111 = MAX_SUPPLY 1111, mintOpen 1, balanceOf_user 0. Lonjakan akhir: 898 (main job 21:31) -> 998 -> 1075 (22:34) -> 1111 (22:39). User free slot (mintPriceFor(user,1)=0) lost; user never minted. Recorded in hot-leg-reported.json as 0x84bc...#sellout-20261117-2239.
  - MORFO totalMinted 1082 -> 1083 (+1). Minor, not reportable.
- PEPE unchanged (freeMinted 500/500, hasMinted_user 1).
- binanceai-mint unchanged: launched 0, failed 1, isRefundPhase 1 (refund/failed already reported 2026-11-02 20:24).
- Thresholds: AGCLUB 58.8%, Matrix 58.7%, PunchCard 22.8%, PIXELFROGS 15.1% — all below the >70% strong-lead bar; no promotion. Ledgera_free_pct null.
- BSCCat: freeMinted 519, totalSupply 519M tokens — unchanged vs 2234. No change.

## Bridge (read-only)
- scan-bridge.json: 116 contracts, 0 not in snapshot, 7 same_owner_discarded. Nothing to report; no "temuan pelengkap scan" promotion.

## Other
- Poffzi FCFS: NO PROCESS FOUND (expected — sale ended 16 Nov, terminal state).
- Executions: none — no preview, no mint, no claim (read-only run).

## Outcome
REPORTABLE: Bold Leonidas sold out (totalSupply 1111/1111 MAX_SUPPLY; user free slot lost, user balance 0). Reported once this run; later runs stay silent on it. Everything else silent — no new lead, candidate, pending claim, or blocked auto-mint/auto-claim.
