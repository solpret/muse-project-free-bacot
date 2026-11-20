# Free-mint-hot-leg run 2026-11-18 00:19 WIB — SILENT (no reportable change)

Script: run-hot-leg-2026-11-18-0019.py (cloned from 0004 run); output JSON:
hot-leg-run-2026-11-18-0019.json; reread: hot-leg-run-2026-11-18-0019-reread.json
(block 134158680, 25/25 focus items, 0 RPC chunk errors). Elapsed 35.2s.
Read-only: no preview, no mint, no claim. Main snapshot NOT rewritten.

## Leg 1 — Sourcify feed
- 20 contracts, top verifiedAt 2026-11-17T17:19:48Z. 4 new vs hot-leg-seen.json:
  0x78c9fEB7a6cf875E519d7063055C2A582cA4cFDC (8 fns, no mint/quote/free/agent),
  0xcaCFbd2a32CFc610887b30F4e912c05951587777 (plain token, 40 fns),
  0xed5ED3d7354d9ad17C8d4d63aE18bd8e90457915 (plain token, 18 fns),
  0x92feFfF691c7A685779F7Bf9d3E2cA52fCD43794 (8 fns, no mint/quote/free/agent)
  — all checked-not-sale-shape (S1/S2 false). 0 hits.
  Recorded in hot-leg-seen.json (seen_n 16032).

## Leg 2 — Boltbook EN + ZH
- EN 45,445 bytes / ZH 45,681 bytes, HTTP 200. 6 / 6 full addresses, 0 new
  (all already in seen). Mentions only: STARDUST (SDUST) free lane 396/500,
  pace collapsed after 22:10 (+2 in ~2h); PXIO Miners 80 seats left, 99.5%
  minted (PXIO auto-claim track, not Free Bacot); Forge Machine 358/2,280
  free (15.7%); EIM free-lane correction note (mint(uint32)(1)) — EIM
  already in main snapshot, tracked by main job. No full-address new lead.

## Leg 3 — on-chain verify new S1/S2
- Empty: no shape hits, nothing to verify. No preview/mint.

## Bridge leg (read-only)
- 116 contracts, 0 not in snapshot, 7 same-owner-discarded. No bridge
  promotion (no bridge contract newly meets a Free Bacot tier).

## Leg 4 — reread focus set vs 0004 (block 134157116 -> 134158680)
- 6 small value changes, none tier-changing:
  - AgentBubble freeMinted 1867 -> 1868, totalMinted 2012 -> 2013 (+1).
  - SPARKS totalSupply 1155 -> 1156 (+1).
  - MORFO totalMinted 1087 -> 1088 (+1).
  - AgentNOVA totalSupply 722 -> 723 (+1).
  - Zephyra totalMinted 987 -> 989 (+2).
  - RigForge freeSharesLeft 626 -> 625, freeClaimed 374 -> 375 (+1 free
    share claimed; pool still open, 625 left).
- Unchanged: bsccat freeMinted 519 flat (gate PASS carried, site not
  re-read); PEPE freeMinted 500/500 sold out, hasMinted_user 1;
  binanceai-mint launched 0, failed 1, isRefundPhase 1 (already reported
  once 2 Nov).
- Thresholds: PunchCard 23.1% (freeMinted 1281/5555, slot open:
  mintPriceFor 0, mintedCount 0, mintOpen 1), AGCLUB 58.9%, Matrix 58.8%,
  PIXELFROGS 15.1% — all below the >70% strong-lead bar. No promotion,
  no gate work needed. Lumenhold 82.7% per main 00:01 run but age
  unverified -> still not a strong lead (carried context, main job's item).

## Poffzi FCFS
- pgrep fcfs: NO PROCESS FOUND (same as 0004 run).
