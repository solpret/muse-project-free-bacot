# Free-mint-hot-leg run 2026-11-18 00:04 WIB — SILENT (no reportable change)

Script: run-hot-leg-2026-11-18-0004.py (cloned from 2359 run); output JSON:
hot-leg-run-2026-11-18-0004.json; reread: hot-leg-run-2026-11-18-0004-reread.json
(block 134157116, 25/25 focus items, 0 RPC chunk errors). Elapsed 43.2s.
Read-only: no preview, no mint, no claim. Main snapshot NOT rewritten.

## Leg 1 — Sourcify feed
- 20 contracts, top verifiedAt 2026-11-17T17:05:41Z. 3 new vs hot-leg-seen.json:
  0xf5dAcfF8C52F12d4d6f74697cDC716523627c7B9 (8 fns, no mint/quote/free/agent),
  0x5feFAb2A753149c45De48e09CF7821CE3F1cb910 (plain token, 12 fns),
  0xe4AD499B327c51286f5d0fCC11b89A79Aa2d7d81 (105 fns, quote+agent_ref true but
  no mint, no free views) — all checked-not-sale-shape (S1/S2 false). 0 hits.
  Recorded in hot-leg-seen.json (seen_n 16028).

## Leg 2 — Boltbook EN + ZH
- EN 46,434 bytes / ZH 46,649 bytes, HTTP 200. 9 / 7 full addresses, 0 new
  (both front-page newcomers 0xf798… and 0xf8a7… already checked-not-sale-shape
  in seen). Mentions only: Kageveil Genesis 36/9,999; LODE Miner 822/4,444;
  Lumenhold 1,238/1,500 free; PXIO Miners 16,508/16,666 (99% filled — PXIO
  auto-claim track, not Free Bacot); EIM free-lane correction note
  (mint(uint32)(1)) — EIM already in main snapshot, tracked by main job.

## Leg 3 — on-chain verify new S1/S2
- Empty: no shape hits, nothing to verify. No preview/mint.

## Bridge leg (read-only)
- 116 contracts, 0 not in snapshot, 7 same-owner-discarded. No bridge
  promotion (no bridge contract newly meets a Free Bacot tier).

## Leg 4 — reread focus set vs 2359 (block 134156063 -> 134157116)
- Only 2 value changes, neither tier-changing:
  - AgentNOVA totalSupply 721 -> 722 (+1; early-lead 2026-11-14, no free
    counter in snapshot, velocity evaluated by main job).
  - Zephyra totalMinted 984 -> 987 (+3; early-lead 2026-11-14, same).
- Unchanged: bsccat freeMinted 519 flat (gate PASS carried, site not re-read);
  PEPE freeMinted 500/500 sold out, hasMinted_user 1; binanceai-mint launched 0,
  failed 1, isRefundPhase 1 (already reported once 2 Nov).
- Thresholds: PunchCard 23.1%, AGCLUB 58.9%, Matrix 58.8%, PIXELFROGS 15.1% —
  all below the >70% strong-lead bar; Lumenhold 82.7% per main 00:01 run but
  age unverified -> not a strong lead. No promotion, no gate work needed.

## Template bug found + fixed
- The pepe-diff line in the run script had `list(pepe_views or {}).keys()`
  (calls .keys() on a list) — it threw every run, and the except handler
  overwrote the good leg4 diff with the error. Fixed in
  run-hot-leg-2026-11-18-0004.py (now `list((pepe_views or {}).keys())`);
  the 0004 JSON diff entries were corrected manually with the verified diff.

## Poffzi FCFS
- pgrep fcfs: NO PROCESS FOUND (same as 2359 run).

## Main job 00:01
- Run 2026-11-18 00:01 WIB was SILENT too; scan leg fast-failed (Ankr 401,
  32nd consecutive, watermark held at 134086385). No dedup conflict.
