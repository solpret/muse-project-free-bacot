# free-mint-hot-leg run 2026-11-17 18:19 WIB

- Elapsed 12.4 s (target <2 min). Read-only; no preview, no mint, no claim.
- Leg 1 Sourcify feed: 20 contracts, 0 new (top unchanged vs 18:14 run:
  0x2D41EF31DcFFa1d27CC25B8BfddC796b6ef6B4ff, verifiedAt 2026-11-17T11:15:42Z).
- Leg 2 Boltbook EN 44.771 byte HTTP 200 + ZH 43.090 byte HTTP 200: 0 new
  contracts in either language; no new full-address lead to shape-check.
- Leg 3 shape-check: 0 targets, 0 S1/S2 hits. hot-leg-seen.json unchanged
  (15.838 entries, 0 added).
- Leg 4 re-read (block 134110478, 117 calls, 0 chunk errors): only change vs
  18:14 run is PunchCard incremental minting — totalSupply/totalMinted
  1160 -> 1163, freeMinted 1146 -> 1149. PunchCard free% 20.7%, far below the
  >70% strong-lead bar; user slot still open (mintPriceFor 0, mintedCount 0,
  balanceOf 0, mintOpen 1). No promotion, no sellout, no slot loss.
- Threshold check: AGCLUB 58.8%, Matrix 58.4%, PIXELFROGS 15.1%, Ledgera
  freeClaimed 2695 — none above 70% => no strong-lead promotion.
- binanceai-mint pending claim unchanged: launched 0, failed 1,
  isRefundPhase 1, totalShares 3110, tokenClaimed(user) 0.
- bsccat / pepe: no changes vs 18:14.
- Bridge (scan-bridge.json, read-only): 116 contracts, 0 not in snapshot,
  7 same-owner-discarded. No complementary finding to promote.
- Poffzi FCFS: no process found (informational only; sale ended 16 Nov).
- Result: SILENT — no new lead, candidate, pending claim, change, or blocked
  auto-mint/auto-claim. Nothing reported to main chat.
- Files: hot-leg-run-2026-11-17-1819.json,
  hot-leg-run-2026-11-17-1819-reread.json,
  hot-leg-2026-11-17-1819-boltbook-en.html,
  hot-leg-2026-11-17-1819-boltbook-zh.html, hot-leg-2026-11-17-1819-run.py.
