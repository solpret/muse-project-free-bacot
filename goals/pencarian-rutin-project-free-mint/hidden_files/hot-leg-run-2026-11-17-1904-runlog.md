# free-mint-hot-leg run 2026-11-17 19:04 WIB (31.5 s, read-only, no executions)

- Leg 1 Sourcify feed: 20 contracts, 2 new (newest verifiedAt 2026-11-17T12:07:49Z). Shape-check: both S1/S2 false (0xaaaDa2e714d6f0F242EcdE66A03BA5489D778a65, 0x171d4FfCEFE78c96B1195D172D0DB1Bf22b14A70 — no mint, no quote, no free views, no agent ref); recorded checked-not-sale-shape in hot-leg-seen.json (now 15.858 entries).
- Leg 2 Boltbook EN (46.218 byte, HTTP 200) + ZH (45.983 byte, HTTP 200): 0 new contracts; 0 hits on all 8 sweep keywords (EN + ZH).
- Leg 3 shape-check: no new S1/S2 contracts, nothing to verify on-chain.
- Leg 3b CAT402 re-check (sale 0xdAba96c14B38725b23502BE6dFE021c08B7a5fB1, found 18:59 run): UNCHANGED — still pre-launch: gateStart 0, freeWindowOpen 0, windowOpen 0, totalCatsMinted 0, paidCatsSold 0, freeCatsClaimed 0, freeCatsRemaining 100/100, registry() still exact Agent ID registry 0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F, isFreeEligible(user) true, freeClaimedBy(user) false, quoteBuy(1) 0,001 BNB. Age still unverified → stays watchlist-only, never reported as lead, never previewed/minted.
- Leg 4 re-read (block 134116876) vs 18:59, 16/16 OK: only small drifts — PunchCard +8 mints (totalSupply/freeMinted 1192→1200 / 1178→1186, free% ~21,4% of MAX_SUPPLY 5555), PXIO-Miners +34 (totalSupply 13130→13164), MineCard +10 (923→933), RigForge +1 free claim (freeClaimed 369→370, freeSharesLeft 631→630; user already claimed 11 Nov, no new change). No sellout, no user slot lost, no pending claim opened (binanceai-mint unchanged: launched 0, failed 1, refund phase 1), no age-exclusion.
- Threshold check: no item above strong-lead bar >70% (AGCLUB ~58,8% freeMinted 522, age unverified; Matrix 58,4%, already age-excluded 16 Nov; PunchCard ~21,4%; HANAMI-BLOOM 13,0%). No promotion, no preview, no mint, no claim.
- Bridge scan (read-only): 116 contracts, 0 outside snapshot, 7 same_owner_discarded. Nothing to report as scan complement.
- Poffzi FCFS liveness (informational): NO PROCESS FOUND (pgrep matched only its own shell line).
- Result: silent run — nothing new to report to main chat.
