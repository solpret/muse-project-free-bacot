# Hot-leg run 2026-11-17 17:54 WIB (scheduled 17:54:38)

Elapsed 26.9s, block 134107166. Read-only; no preview/mint/claim.

## Leg 1 — Sourcify feed
20 contracts, top 0xe4bE56028a25b435E4281053CbF8CB849c3fC278 (verifiedAt 2026-11-17T10:54:24Z).
2 new vs hot-leg-seen: 0xe4bE56028a25b435E4281053CbF8CB849c3fC278 (4 fns, no mint/quote/free-view/registry),
0xee1086e453e0F856Fd2F751075996545B202A694 (9 fns, no mint). Both S1=False S2=False,
recorded in hot-leg-seen.json (15828 -> 15830). No shape hits.

## Leg 2 — Boltbook
EN 46,681 bytes / ZH 46,857 bytes, 5 addresses each (same set both languages), all
already seen. No new contracts.

## Leg 3 — on-chain verify of new sale-shape hits
None (no shape hits).

## Leg 4 — re-read (25 focus items + BSCCat probe + PEPE)
Changes vs 1749 re-read (3, all routine minting):
- MORFO totalMinted 1071 -> 1072 (+1).
- Kryntar totalMinted 1366 -> 1367, standardRemaining 745 -> 744 (+1).
- PunchCard freeMinted 1064 -> 1099, totalMinted/totalSupply 1078 -> 1113 (+35 in
  5 min; free 1099/5555 = 19.8%, far below the >70% strong-lead bar; slot open:
  mintPriceFor(user,1)=0, mintedCount(user)=0, balanceOf(user)=0, mintOpen=1).
  Routine minting, no promotion.
- PEPE unchanged (freeMinted 500, soldShares 501, FREE_SHARES 500, opened 0,
  costOf(1) 0.005 BNB, hasMinted(user)=1).
- BSCCat unchanged (freeMinted 509, totalSupply 509e27, balanceOf(user)=0; other
  views revert as before). Website gate PASS carried from 0239 run, site not re-read.
- Thresholds: AGCLUB 58.8%, Matrix 58.4%, PIXELFROGS 15.1%, PunchCard 19.8% — none
  above 70%, no promotion. No sellout, slot loss, or age-exclusion.

## Bridge (read-only)
116 contracts, 0 not in snapshot, 7 same_owner_discarded. No bridge contract newly
promoting or changing; nothing to report as "temuan pelengkap scan".

## Outcome
Nothing reportable: no new lead, candidate, pending claim, sellout, slot loss,
age-exclusion, or blocked auto-mint/auto-claim. Silent per body rules.
Files: hidden_files/hot-leg-run-2026-11-17-1754.py, hot-leg-run-2026-11-17-1754.json,
hot-leg-run-2026-11-17-1754-reread.json.
