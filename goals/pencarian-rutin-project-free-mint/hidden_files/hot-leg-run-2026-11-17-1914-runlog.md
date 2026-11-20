# free-mint-hot-leg run 2026-11-17 19:14 WIB (28.7 s, read-only, no executions)

- Leg 1 Sourcify feed: 20 contracts, 2 new (newest verifiedAt 2026-11-17T12:15:12Z). Shape-check: 0x61ff3642780f7Ce76dE9ac39C40CCa0a9002a888 S1/S2 false (no mint, no quote, no free views, no agent ref); 0x49eAd256f97A512fA2bBb2c2d5a3AC20CD0D2435 S1/S2 false (mint only, no quote/free/agent); recorded checked in hot-leg-seen.json (now 15.861 entries).
- Leg 2 Boltbook EN (47.352 byte, HTTP 200) + ZH (47.672 byte, HTTP 200): 0 new contracts; 0 hits on all 8 sweep keywords (EN + ZH).
- Leg 3 shape-check: no new S1/S2 contracts, nothing to verify on-chain.
- Leg 3b CAT402 re-check (sale 0xdAba96c14B38725b23502BE6dFE021c08B7a5fB1): UNCHANGED vs 19:09 — still pre-launch: gateStart 0, freeWindowOpen 0, windowOpen 0, totalCatsMinted 0, paidCatsSold 0, freeCatsClaimed 0, freeCatsRemaining 100/100, registry() still exact Agent ID registry 0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F, isFreeEligible(user) true, freeClaimedBy(user) false, quoteBuy(1) 0,001 BNB. Age still unverified → stays watchlist-only, never reported as lead, never previewed/minted.
- Leg 4 re-read (block 134117867, +565 blocks vs 19:09), 16/16 OK: only small drifts — PunchCard +1 mint (totalSupply/freeMinted 1202→1203 / 1188→1189, free% ~21,4% of MAX_SUPPLY 5555), PXIO-Miners +26 (totalSupply 13182→13208), MineCard +2 (933→935). No sellout, no user slot lost, no pending claim opened (binanceai-mint unchanged: launched 0, failed 1, refund phase 1), no age-exclusion.
- Threshold check: no item above strong-lead bar >70% (AGCLUB ~58,8% freeMinted 522; Matrix 58,4%, already age-excluded 16 Nov; PunchCard ~21,4%; HANAMI-BLOOM 13,0%). No promotion, no preview, no mint, no claim.
- Bridge scan (read-only): 116 contracts, 0 outside snapshot, 7 same_owner_discarded. Nothing to report as scan complement.
- Result: silent run — nothing new to report to main chat.
