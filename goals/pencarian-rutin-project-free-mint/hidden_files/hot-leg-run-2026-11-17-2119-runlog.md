# free-mint-hot-leg run 2026-11-17 21:19 WIB

- Elapsed 18.8 s; block 134134686. No executions (read-only run).
- Leg 1 Sourcify feed: 20 contracts, 0 new (same top as 21:14 — 0x3d2633E575F9Af79435eF66984562f5DF4bb9D44, verifiedAt 2026-11-17T14:13:03Z).
- Leg 2 Boltbook EN (45.430 byte, HTTP 200) + ZH (43.784 byte, HTTP 200): EN 11 full-address contracts, 0 new; ZH 15 contracts, 3 new — 2 shape-checked, 1 tx-hash-prefix artifact.
- Leg 3 shape-check: 2 targets — 0xF3bCDb28c32900335C5A30c30f96c8AEb93b91AA and 0xeb178dD18BF3154FF9FF50123DC97E12633feE36 — both S1=False S2=False (n_fns 0, no mint/quote/free views/agent ref). Recorded in hot-leg-seen.json as checked-not-sale-shape. 0xe2b3445c78a0db8cc03320647a4a2d5dab81ca1a recorded as checked-not-contract (first 40 hex chars of a 66-char tx hash in a Boltbook post, regex artifact). Seen now 15.932 entries.
- Leg 4 re-read vs 21:14 run: routine +1 increments only — AgentBubble freeMinted 1846 -> 1847, totalSupply/totalMinted 1991 -> 1992; AgentNOVA totalSupply 714 -> 715; PunchCard totalSupply/totalMinted 1244 -> 1248, freeMinted 1226 -> 1230. No sellout, no slot loss, no promotion. bsccat and pepe unchanged.
- Thresholds: PunchCard 22,1%, AGCLUB 58,8%, Matrix 58,5%, PIXELFROGS 15,1% — none above the >70% strong-lead bar; user slot open on PunchCard (mintPriceFor 0, mintedCount 0).
- Pending claims unchanged (no diff vs 21:14): binanceai-mint launched 0 / failed 1 / refund phase 1; RigForge freeSharesLeft 627.
- Bridge scan: 116 contracts, 0 not in snapshot, 7 same_owner_discarded — no complementary finding to report.
- Poffzi FCFS: no process found (informational; no sale armed).
- Result: nothing to report to main chat (no new lead, candidate, pending claim, change, or blocked auto-mint/auto-claim).
- State files: hot-leg-run-2026-11-17-2119.json, hot-leg-run-2026-11-17-2119-reread.json, hot-leg-2026-11-17-2119-boltbook-en/zh.html, hot-leg-2026-11-17-2119-run.py, hot-leg-run-2026-11-17-2119-stdout.txt.
