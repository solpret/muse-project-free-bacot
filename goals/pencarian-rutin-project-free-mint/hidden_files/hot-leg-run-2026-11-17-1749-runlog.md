# Hot-leg run 2026-11-17 17:49 WIB (scheduled 17:49:38)

Elapsed 17.2s, block 134106493. Read-only; no preview/mint/claim.

## Leg 1 — Sourcify feed
20 contracts, top 0xCBa620D62B0a27d4E0f95a7b7351c332d18A5E39 (verifiedAt 2026-11-17T10:48:03Z).
3 new vs hot-leg-seen: 0xCBa620D62B0a27d4E0f95a7b7351c332d18A5E39 (28 fns, mint but no
quote/free-view/registry), 0x43F95F3819F02151f350fdDb90CA55f4471E301E (39 fns, no mint),
0xeebf17320962869C97a8Da8842EB064e7F8cE5fc (10 fns, no mint). All S1=False S2=False,
recorded in hot-leg-seen.json (15825 -> 15828). No shape hits.

## Leg 2 — Boltbook
EN 47,582 bytes / ZH 47,780 bytes, 5 addresses each (same set both languages), all
already seen. No new contracts.

## Leg 3 — on-chain verify of new sale-shape hits
None (no shape hits).

## Leg 4 — re-read (25 focus items + BSCCat probe + PEPE)
True changes vs 1744 re-read (see correction note below):
- BoldLeonidas totalSupply 887 -> 888 (routine +1).
- PunchCard freeMinted 1039 -> 1064, totalSupply/totalMinted 1053 -> 1078 (+25 in
  5 min; free 1064/5555 = 19.2%, far below the >70% strong-lead bar; slot open:
  mintPriceFor(user,1)=0, mintedCount(user)=0, balanceOf(user)=0, mintOpen=1).
  Routine minting, no promotion.
- PEPE unchanged (freeMinted 500, soldShares 501, FREE_SHARES 500, opened 0,
  costOf(1) 0.005 BNB, hasMinted(user)=1).
- BSCCat unchanged (freeMinted 509, totalSupply 509e27, balanceOf(user)=0; other
  views revert as before). Website gate PASS carried from 0239 run, site not re-read.
- binanceai-mint unchanged: launched 0, failed 1, isRefundPhase 1, totalShares 3110,
  tokenClaimed(user)=0. Refund/failed phase already reported 2026-11-02 20:24 WIB;
  not re-reported.
- Thresholds: AGCLUB 58.8%, Matrix 58.4%, PIXELFROGS 15.1%, PunchCard 19.2% — none
  above 70%, no promotion.

## Bridge (read-only)
116 contracts, 0 not in snapshot, 7 same_owner_discarded. No bridge contract newly
promoting or changing; nothing to report as "temuan pelengkap scan".

## Correction — change-detection pointer bug (fixed this run)
The run initially printed 25 spurious "read-availability-change" entries: PREV_REREAD
pointed at the 1744 main run JSON, which no longer embeds reads (the 1744 script
switched to a leg4_reread_file pointer). Corrected by diffing the 1744 and 1749
-reread.json files directly (only the 2 changes above are real). The 1749 run JSON's
leg4_changes_vs_1509 was overwritten with the corrected list + note, and the 1749
script's PREV_REREAD now points at the -reread file, so the next clone's sed chain
(1749->1754, 1744->1749) yields PREV_REREAD = hot-leg-run-2026-11-17-1749-reread.json.

## Outcome
Nothing reportable: no new lead, candidate, pending claim, sellout, slot loss,
age-exclusion, or blocked auto-mint/auto-claim. Silent per body rules.
Files: hidden_files/hot-leg-run-2026-11-17-1749.py, hot-leg-run-2026-11-17-1749.json,
hot-leg-run-2026-11-17-1749-reread.json.
