# free-mint-hot-leg run 2026-11-18 02:59 WIB

- Elapsed 41.3 s (main script), block 134179965. No preview, no mint, no claim.
- Leg 1 Sourcify feed (20 contracts): 2 new — 0xDDAEf9AFa92F86Bd89132F18FCA79B10Ed25e99c
  (verifiedAt 2026-11-17T19:59:16Z, 20 fns) and 0x4dF3b7C7d63261368489b330C36913cEee5D0044
  (verifiedAt 2026-11-17T19:59:14Z, 14 fns). Shape-check: both S1 false, S2 false, no
  mint/quote/free views, no agent ref — NOT sale shape. Recorded in hot-leg-seen.json.
- Leg 2 Boltbook EN 44.154 byte (HTTP 200) + ZH 42.576 byte (HTTP 200): 6 / 10
  full-address contracts, 0 new.
- Leg 3: no shape hits.
- Leg 4 re-read vs 02:54 run (read-only, snapshot NOT rewritten):
  - Stromboat freeMinted/totalMinted 162 -> 168 (+6). AgentNOVA totalSupply 743 -> 747 (+4).
    Routine movement only.
  - Matrix, PunchCard, RigForge, bsccat, pepe, binanceai-mint pending claim: no changes.
    binanceai-mint refund/failed phase already reported 2026-11-02 20:24 WIB, no re-report.
  - RPC DEGRADATION: main leg-4 chunks 2-3 (calls 20-59, 16 items: AGCLUB, BNBG, SPARKS,
    Ledgera, BoldLeonidas, RaceAgents, CPASS, REOPIR, RAVE, MORFO, AgentNOVA, Zephyra,
    Pengu, Kryntar, ONI, HAPPE) returned all-None with zero chunk errors; a 40-call
    retry batch also returned all-None. Single-call probes proved the contracts fine
    (AGCLUB totalMinted 525, SPARKS totalSupply 1158 on both dataseed endpoints), so this
    was a batch-transport failure, NOT a state change. Re-read in chunks of 10 recovered
    all 40 values — all unchanged vs 02:54 except AgentNOVA (+4, already counted above).
    The raw all-None diff was preserved in the run JSON as leg4_changes_vs_0254_raw_unreliable
    and replaced by the corrected diff. Lesson for next runs: if a whole chunk returns
    all-None with no error, re-read in smaller chunks before trusting the diff.
  - Threshold check: PunchCard 23,2%, AGCLUB 59,1%, Matrix 59,0%, PIXELFROGS 15,1%,
    AgentBubble 84,4% but launch age still UNVERIFIED — no strong-lead promotion.
- Bridge (read-only): 116 contracts, 0 not in snapshot, 7 same_owner_discarded — no
  complement finding, nothing to promote.
- Poffzi FCFS: no process found (informational only; sale ended 16 Nov).
- Result: SILENT run — no new lead, candidate, pending claim, change, or blocked
  auto-mint/auto-claim to report.
- Files: hot-leg-2026-11-18-0259-run.py, hot-leg-run-2026-11-18-0259.json,
  hot-leg-run-2026-11-18-0259-reread.json, hot-leg-run-2026-11-18-0259-retry.json,
  hot-leg-run-2026-11-18-0259-retry2.json, boltbook EN/ZH html snapshots,
  hot-leg-2026-11-18-0259-run.stdout.log / .stderr.log (empty). hot-leg-seen.json
  +2 contracts (0xDDAEf9AFa92F86Bd89132F18FCA79B10Ed25e99c,
  0x4dF3b7C7d63261368489b330C36913cEee5D0044, checked-not-sale-shape).
