# free-mint-hot-leg run 2026-11-18 03:04 WIB

- Elapsed 43.5 s, block 134181035. No preview, no mint, no claim.
- Leg 1 Sourcify feed (20 contracts, top verifiedAt 2026-11-17T20:06:59Z): 3 new —
  0x3b0697Da968AFAE90032C23A371374695eDcE763 (6 fns, no mint/quote/free/agent),
  0x986E4c99BCB756cBB41ADDe36C17b40272748740 (15 fns, no mint/quote/free/agent),
  0x62a7AC33ca463331858693b8Aa05B16688bA29E0 (36 fns, mint + agent ref, but no quote
  and no free views). All S1 false, S2 false — NOT sale shape. Recorded in
  hot-leg-seen.json (now 16.114 entries).
- Leg 2 Boltbook EN 44.102 byte (HTTP 200) + ZH 42.580 byte (HTTP 200): 12 / 13
  full-address contracts, 1 "new" — 0xf46ddc460fb62d2c0c7a2b11731c34a732b006bd is the
  first 40 hex chars of a 66-char tx hash in a post (regex artifact, recorded
  checked-not-contract, never shape-checked). Figures: LumenFindings exp39
  145/300, MINE 1107/8.888, MechaWar 193/7.777 (already known from ~02:20 WIB read)
  — no new free-mint post.
- Leg 3: no shape hits.
- Leg 4 re-read vs 03:01 main run (read-only, snapshot NOT rewritten; diff vs the
  02:59 reread is unreliable — that file holds the all-None chunk artifact for 16
  items, preserved in the run JSON as leg4_changes_vs_0259_raw_unreliable and
  replaced by the corrected diff vs 03:01):
  - Routine +1 movements only: AGCLUB 525->526 (free 526/888 = 59,2%), CPASS
    1773->1774, Kryntar 1371->1372, RAVE 366->367, REOPIR 581->582, RaceAgents
    635->636, Stromboat 168->169.
  - Unchanged: JADE, AgentBubble, DRAGON (free sold out 1000/1000, minted-by-user),
    Matrix, BNBG, SPARKS, Ledgera, BoldLeonidas, AgentNOVA, Zephyra, Pengu, ONI,
    HAPPE, PIXELFROGS, Flare-bd6f, PunchCard, RigForge, binanceai-mint, bsccat, pepe.
  - Recovered reads (null in 03:01, not changes): Kryntar mintOpen 1,
    standardRemaining 739, legendaryRemaining 111; Stromboat MAX_SUPPLY 1333,
    FREE_SUPPLY 667. No chunk errors this run.
  - binanceai-mint: launched 0, failed 1, isRefundPhase 1 — refund phase already
    reported 2026-11-02 20:24 WIB, no re-report. RigForge: freeSharesLeft 625,
    openedAt 0 — still not opened.
  - Threshold check: PunchCard 23,2%, AGCLUB 59,2%, Matrix 59,0%, PIXELFROGS 15,1%,
    AgentBubble 84,4% but launch age still UNVERIFIED — no strong-lead promotion.
    PunchCard slot open (mintPriceFor 0, mintedCount 0) but age-excluded, no action.
- Bridge (read-only): 116 contracts, 0 not in snapshot, 7 same_owner_discarded — no
  complement finding, nothing to promote.
- Poffzi FCFS: no process found (informational only; sale ended 16 Nov).
- Result: SILENT run — no new lead, candidate, pending claim, change, or blocked
  auto-mint/auto-claim to report.
- Files: hot-leg-2026-11-18-0304-run.py, hot-leg-run-2026-11-18-0304.json,
  hot-leg-run-2026-11-18-0304-reread.json, boltbook EN/ZH html snapshots,
  hot-leg-2026-11-18-0304-run.stdout.log / .stderr.log (empty). hot-leg-seen.json
  +3 contracts (feed) +1 tx-hash artifact.
