# Hot-leg run 2026-11-19 15:54 WIB — runlog

- Started 15:54:38 WIB (scheduled), script `run-hot-leg-2026-11-19-1554.py` (same pattern as 1549 run; diff vs 1549 reread + 1509 fallback; AUGENT leg3 recheck).
- Elapsed 176.4s — OVERRUN vs <2 min target (same as 1549: 204.7s; RPC latency dominates: leg4 chunks took 71–158s before bsccat/pepe). Logged, run ended; no pile-up.
- Block at end: 134475538. Reads leg4: 45/45 OK, 0 chunk errors. Executions: none — read-only, no preview/mint/claim.

## Leg 1 — Sourcify feed (limit 20, sort desc)
- Total 20, top verifiedAt 2026-11-19T08:54:23Z (0x8A4cD113725C134647B6f7a02735dA3914DFE456).
- 4 new contracts, all shape-checked, all S1=False / S2=False:
  - 0x8A4cD113725C134647B6f7a02735dA3914DFE456 (22 fns, agent_ref true, no mint/quote/free)
  - 0xe815b70280A1cEA907a238f261B8206AD7d7ABf2 (8 fns)
  - 0x7E9D6F3a8505E21F432De86347806ADF12ABe79a (54 fns, agent_ref true)
  - 0x0e998bb5a212deeFD3F3a1DC55ff109646bc4423 (17 fns, agent_ref true)
- No shape hits. Recorded in hot-leg-seen.json.

## Leg 2 — Boltbook EN + ZH (direct fetch)
- EN 45.383 byte, ZH 45.159 byte, 10 full addresses each, 1 new (same both langs):
  - 0x4A8E187475C85Fb5cF0F339e6bA1DE9A7edB8AF4 — Sourcify 404 / 0 fns, verifiedAt null — not sale-shape, recorded, not a lead.
- No new lead, no new sale-shape contract. AURUM AGENTS context unchanged (23/5.555 in front-page figures).

## Leg 3 — on-chain verify new S1/S2
- Empty: no new S1/S2 contracts this run, nothing to verify.
- Carried over (not re-checked by this run, already in seen): 1549 S1 hit 0x080AcBDFE6d7b114C27E7CcF6cdE1681d88bDEc9 — leg3 at 1549 returned all-null reads except freeLeft_user=0 / freeUsed_user=0; pool/slot still UNVERIFIED, still not a lead, never previewed/minted.

## AUGENT recheck (0xAAdD9058b3DaaB00439457D82c2C508a5cc1c393)
- freeClaimed 861 → 863 (+2 since 1549), freeClaimedByWallet(user)=0 (slot open), totalSupply 1e28, name/symbol AUGENT.
- FREE_SUPPLY / FREE_SHARES / freeSharesLeft / quote all still null → % unknown; launch age still UNVERIFIED.
- Watchlist-only, no promotion, no preview/mint.

## Bridge leg (read-only)
- scan-bridge.json: 116 contracts, 7 same_owner_discarded, 1 not in snapshot: DGF 0x01f9ca4ff95d49594cc8b6591022186dc5c1bc72 — already in leg-4 focus set; totalMinted 1731, unchanged vs 1549; does not meet any tier → no promotion, no report (temuan pelengkap scan, dicatat saja).

## Leg 4 — reread focus set (48 items + bsccat + pepe), diff vs 1549
- Only 2 trivial value changes, neither a reportable change:
  - ClafEye totalSupply 7264 → 7265 (+1)
  - EIM totalMinted 853 → 854 (+1)
- BSCCAT: no change. PEPE: no change.
- binanceai-mint pending: launched 0, failed 1, isRefundPhase 1, totalShares 3110, tokenClaimed(user) 0 — UNCHANGED; refund/failed phase already reported once 2026-11-02 20:24 WIB, no re-report.

## Threshold check (strong lead >70% + age <24h verified + slot open + website gate)
- STOCKAGENT 78.8% (freeLeft 235/1111, quote 0, slot open) — UNCHANGED vs 1549; age UNVERIFIED + website gate unverified → no promotion. 70% crossing reported 18 Nov 18:49; 75–78% observed-not-reported.
- Lumenhold 84.4% (freeClaimed 1266/1500) — UNCHANGED; age UNVERIFIED + website None + slot-free UNVERIFIED → no promotion.
- AgentBubble 93.5% but totalMinted 2222/2222 = SOLD OUT (already reported 03:59).
- PunchCard 24.4%, AGCLUB 59.7%, Matrix 65.2%, ALIEN 64.1%, Hivebyte 17.1%, THYRK 55.6% — below 70%.
- No strong lead, no track-A candidate, no track-C lead/candidate, no track-B opening. No promotion this run.

## Poffzi FCFS
- No process found (same as 1549). No action — status check only.

## Verdict
- NOTHING TO REPORT. No new lead, candidate, pending claim, change, or blocked auto-mint/auto-claim. Silent per body rules.
- State files: hot-leg-run-2026-11-19-1554.json, hot-leg-run-2026-11-19-1554-reread.json, hot-leg-2026-11-19-1554-boltbook-en/zh.html, hot-leg-seen.json updated (5 new addresses).
