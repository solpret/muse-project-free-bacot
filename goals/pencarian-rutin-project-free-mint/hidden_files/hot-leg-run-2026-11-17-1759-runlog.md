# Hot-leg run 2026-11-17 17:59 WIB (scheduled 17:59:38)

Elapsed 18.1s, block 134107824. Read-only; no preview/mint/claim.

## Leg 1 — Sourcify feed
20 contracts, top 0xe4bE56028a25b435E4281053CbF8CB849c3fC278 (verifiedAt 2026-11-17T10:54:24Z, same top as 1754 run — feed unchanged). 0 new vs hot-leg-seen. No shape hits.

## Leg 2 — Boltbook
EN 45,774 bytes / ZH 45,786 bytes, 9 addresses each (same set both languages), all already seen. No new contracts.

## Leg 3 — on-chain verify of new sale-shape hits
None (no shape hits).

## Leg 4 — re-read (25 focus items + BSCCat probe + PEPE)
One change vs 1754 re-read, routine minting only:
- PunchCard freeMinted 1099 -> 1113, totalMinted/totalSupply 1113 -> 1127 (+14 in 5 min; free 1113/5555 = 20.0%, far below the >70% strong-lead bar; slot open: mintPriceFor(user,1)=0, mintedCount(user)=0, balanceOf(user)=0, mintOpen=1). Routine minting, no promotion.
- PEPE unchanged (freeMinted 500, soldShares 501, FREE_SHARES 500, opened 0, costOf(1) 0.005 BNB, hasMinted(user)=1).
- BSCCat unchanged (freeMinted 509, totalSupply 509e27, balanceOf(user)=0; other views revert as before). Website gate PASS carried from 0239 run, site not re-read.
- Thresholds: AGCLUB 58.8%, Matrix 58.4%, PIXELFROGS 15.1%, PunchCard 20.0% — none above 70%, no promotion. No sellout, slot loss, or age-exclusion.

## Bridge (read-only)
116 contracts, 0 not in snapshot, 7 same_owner_discarded. No bridge contract newly promoting or changing; nothing to report as "temuan pelengkap scan".

## Outcome
Nothing reportable: no new lead, candidate, pending claim, sellout, slot loss, age-exclusion, or blocked auto-mint/auto-claim. Silent per body rules.
Files: hidden_files/hot-leg-run-2026-11-17-1759.py, hot-leg-run-2026-11-17-1759.json, hot-leg-run-2026-11-17-1759-reread.json.
