# Hot-leg run 2026-11-17 22:54 WIB (scheduled 22:54:38) — SILENT (no reportable change)

Script elapsed 100.7s (target <2 min; script alone inside target, whole run overran due to a crashed first script attempt + manual pre-poll). Script: hot-leg-run-2026-11-17-2254.py (cloned from 2249 run, PREV_* -> 2249; XCOPY/ARKYN/ALIEN added to focus set); output JSON: hot-leg-run-2026-11-17-2254.json; reread: hot-leg-run-2026-11-17-2254-reread.json (block 134148323, 28 items, 0 RPC errors).

## Leg 1 — Sourcify feed
- Manual pre-poll top 0x8ef164928864261bd2569af683841Ef864C3175c (verified 2026-11-17T15:52:16Z): ABI 50 fns, withdraw/operator vault (withdraw, depositBnb, fee, owner), no mint/quote/free-view/registry -> NOT sale shape. Recorded in hot-leg-seen.json before script start.
- Script re-poll (feed had advanced): top 0x814c27C311a7CE9Dc15d23Af875aC442F1887777 (verified 2026-11-17T16:00:49Z). 5 new vs seen: 0x814c27C311a7CE9Dc15d23Af875aC442F1887777 (22 fns), 0xff601781eb21db65293aB859a30273Bd2bB39c39 (98 fns), 0xC23910cE9B0AD5ee806BAe33E6084e93e51Df20F (62 fns), 0x04dd46D3bCf44a3B1d43675Af90710aFb29c0c31 (98 fns), 0x17540f660e4Df4187a334108C233f69A40df50d7 (15 fns) — all S1=False S2=False (mint=False, quote=False, freeview=False, regfn=False). No shape hits, no lead.
- Seen: 15995 -> 16000 (5 added by script + 0x8ef1... added manually).

## Leg 2 — Boltbook
- Manual: EN returned 0 bytes on 2 curl attempts (transient); ZH 45,499 bytes, 7 addresses, 0 new.
- Script retry: EN 45,822 bytes / ZH 46,033 bytes, 8 / 8 addresses (identical sets; EN now includes 0xA0D84A525809CD97573218C42C4E7Bc324fCD60f, already in seen), 0 new. No lead.

## Leg 3 — on-chain verify new sale-shape
- None (no shape hits). No preview/mint/claim.

## Leg 4 — re-read vs 2249 (28 items)
- Value-changes (mint-count increments only, none tier-changing):
  - Matrix freeMinted 587 -> 588, totalSupply 584 -> 585, freeRemaining 413 -> 412 (free 58.8%).
  - Ledgera freeClaimed 2699 -> 2702, totalSupply 2706 -> 2709.
  - MORFO totalMinted 1083 -> 1084. Zephyra totalMinted 978 -> 980.
  - PunchCard freeMinted 1272 -> 1274, totalMinted/totalSupply 1290 -> 1292 (free 22.9%, slot open, mintPriceFor(user,1)=0, balanceOf_user 0).
- New focus items (first read this run, baseline for next):
  - XCOPY totalSupply 446/1100 MAX (40.5% of max), mintOpen 1, balanceOf_user 0; freeMinted/freeClaimed views revert (free % unverifiable via those views). Early-lead reported 02:31 today; age still <24h if launch ~02:30 but free % unknown -> no strong-lead promotion.
  - ARKYN totalMinted 1974; totalSupply/mintOpen/freeMinted revert; free % null; age unverified.
  - ALIEN totalSupply 455 vs FREE_SUPPLY 1000 (45.5%), mintOpen 1, balanceOf_user 0; totalMinted/freeMinted revert.
- Thresholds: PunchCard 22.9%, AGCLUB 58.8%, Matrix 58.8%, PIXELFROGS 15.1% — all below the >70% strong-lead bar; no promotion. Ledgera_free_pct null.
- Unchanged: BoldLeonidas totalSupply 1111/1111 (sellout already reported once); PEPE freeMinted 500/500, opened 0, hasMinted_user 1; BSCCat freeMinted 519 (pool not open); binanceai-mint launched 0, failed 1, isRefundPhase 1 (refund/failed already reported 2026-11-02); JADE cost_user_1 0.0005 BNB (paid, unchanged); RigForge freeSharesLeft 627, openedAt 0.

## Bridge (read-only)
- scan-bridge.json: 116 contracts, 0 not in snapshot, 7 same_owner_discarded. Nothing to report; no "temuan pelengkap scan" promotion.

## Other
- Poffzi FCFS: NO PROCESS FOUND (expected — sale ended 16 Nov, terminal state).
- First script attempt crashed at threshold check (pct() on ARKYN totalSupply error-string + PREV_* self-reference from global sed); fixed PREV_* to 2249 and hardened pct() to numeric-only; full re-run succeeded. Lesson: when cloning, fix PREV_* with targeted replaces, never a global sed of the old run tag.
- Executions: none — no preview, no mint, no claim (read-only run).
