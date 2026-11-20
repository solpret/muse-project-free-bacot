# free-mint-hot-leg run 2026-11-18 03:34 WIB

- Elapsed 22.3 s, block 134184521. No preview, no mint, no claim.
- Leg 1 Sourcify feed (20 contracts, new top 0xC4b03274969eF7D449b3aC3ED5d1A9C723ba447F verifiedAt 2026-11-17T20:34:26Z — one new verification since 03:29): shape-checked, NOT sale shape (S1=false, S2=false, has_mint=false, has_quote=false, free_views=[], agent_ref=false, is_token=true, 15 fns) — plain ERC-20, recorded in hot-leg-seen.json as checked-not-sale-shape, never a lead.
- Leg 2 Boltbook EN 44.370 byte (HTTP 200) + ZH 42.852 byte (HTTP 200): 13 full-address contracts EN, 0 new. Figures all already known: FIND exp39 151/300 (seals 04:00 WIB — age-excluded, DIAM), Lion's Share 1.153/1.450 flat, STOCK AGENT 540/2.222, "Sold out 11.000/11.000" post (teguhap18.ai, no new contract attached). No new free-mint post.
- Leg 3: no shape hits, no leads.
- Leg 4 re-read vs 03:29 (read-only, snapshot NOT rewritten; 125 calls, 0 chunk errors, 0 nulls — no transient-null retry needed):
  - Only diff: AgentNOVA totalSupply 748 -> 749 (one mint; leg-4 reads only totalSupply for it — no free-pool/slot view, not a sellout, slot loss, age-exclusion, or pending-open change, so not reportable).
  - No other movement: Matrix freeMinted 592 / freeRemaining 408 / totalSupply 589 (unchanged), REOPIR 585 (unchanged), PunchCard 23,2% (1290/5555, slot open but age-excluded), AGCLUB 59,2%, AgentBubble 84,4% but launch age still UNVERIFIED — no strong-lead promotion. binanceai launched still 0, failed 1, isRefundPhase 1, totalShares 3110 — refund/failed phase already reported 2026-11-02 20:24 WIB, unchanged, no re-report.
- Bridge (read-only): 116 contracts, 0 not in snapshot, 7 same_owner_discarded — no complement finding, nothing to promote.
- Poffzi FCFS: no process found (informational only; sale ended 16 Nov).
- Result: SILENT run — no new lead, candidate, pending claim, change, or blocked auto-mint/auto-claim to report.
- Files: hot-leg-2026-11-18-0334-run.py, hot-leg-run-2026-11-18-0334.json, hot-leg-run-2026-11-18-0334-reread.json, boltbook EN/ZH html snapshots, hot-leg-2026-11-18-0334-run.stdout.log / .stderr.log. hot-leg-seen.json 16.122 -> 16.123 entries.
