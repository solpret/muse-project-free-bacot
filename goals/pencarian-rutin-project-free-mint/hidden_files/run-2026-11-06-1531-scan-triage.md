# Run 2026-11-06 1531 WIB — Scan leg (route 4) + 5c triage — Worker B

## Scan outcome — SUCCEEDED
- **Pre-flight: OK 10.3s** (head via dataseed 6.4s; ankr_getLogs 50-block chunk, 313 logs). Head at pre-flight 131981412 (16:03 WIB). No no_proxy set; Ankr via existing proxy env.
- **Window scanned (actual, script's own head read): 131980476–131981475 (1000 blocks, cap 1000).** Head advanced +63 blocks between pre-flight and scan start; window is the most recent 1000 at scan start, as instructed.
- **Skipped gap (backfill owns): 131975549–131980475 = 4,927 blocks** (watermark 131975548 → window start − 1). NOT scanned; never by enlarging the window.
- **Watermark NOT advanced by this run** (shared `onchain-scan-state.json` last_scanned_block=131975548, backfill owns it).
- **Chunks 20/20, enrich 182/182, 40 Ankr calls, 0 errors, `partial: false`.** Scan ran ~16:03–16:17 WIB (~14 min); per-chunk + per-contract progress logged with flush throughout (no stall; longest quiet gap < 2 min). Note: many enrich Sourcify reads returned `error:IncompleteRead` this run (flaky Sourcify, not a scan failure) — registry-bytes + name/symbol reads still completed for all 182.
- **Counts: 182 NFT contracts (178 ERC721 + 4 ERC1155), 2750 NFT mints, 478 ERC-20 mint contracts (excluded).** HIVE Agents NOT found in window.
- **No previews, mints, claims, approvals, signatures, or transactions.** Read-only leg.

## First-seen triage — 0 contracts
First-seen = absent from BOTH `onchain-scan-seen.json` (8266 entries, `contracts` dict, case-insensitive match) AND snapshot `contracts`/`track_c` addresses (550). Verified independently: **182/182 scan contracts already in seen, 0 in snapshot-only**. BOBBIE (`0x3BF121…`) and AgentPad Agent (`0x71f860…`) — the run-1501 early leads — re-appeared in this window but are already in seen (added by parent after run 1501), so they are NOT first-seen again and are NOT re-reported. **No EARLY leads, no new contracts to triage.** Triage detail file is an empty object (no first-seen input).

## Leg 5c — ERC-20 shape-check (S1/S2)
- Scan output: 478 ERC-20 mint contracts; **49 with window mint_count ≥ 10**; **49 already checked** (combined dedupe: `checked` sub-dict + legacy top-level keys of `track-c-scan-checked.json`); **0 newly checked** (cap 20 — 0 dropped as sampling limit, nothing new to cover).
- **0 sale-shape hits (S1=0, S2=0).** No new addresses to record; `run-2026-11-06-1531-5c-checked.json` records the counts with an empty `checked` list (parent merges; this leg did NOT write the shared store).

## Files written by Worker B (run 1531)
- `run-2026-11-06-1531-scan.log` — pre-flight + per-chunk/enrich progress + outcome
- `run-2026-11-06-1531-scan.json` — scan output (`partial: false`)
- `run-2026-11-06-1531-preflight.py` — pre-flight script (adapted from 1501)
- `run-2026-11-06-1531-firstseen.py` + `run-2026-11-06-1531-firstseen.json` — first-seen computation (empty list)
- `run-2026-11-06-1531-triage.py` / `run-2026-11-06-1531-triage-detail.json` / `run-2026-11-06-1531-triage.log` — triage (no input contracts)
- `run-2026-11-06-1531-5c.py` / `run-2026-11-06-1531-5c-checked.json` / `run-2026-11-06-1531-5c.log` — leg 5c results + script
- `run-2026-11-06-1531-scan-triage.md` — this file

## Shared state NOT modified
`onchain-scan-state.json`, `onchain-scan-seen.json`, `onchain-snapshot.json`, `track-c-scan-checked.json`, `hot-leg-seen.json` — all read-only this run; parent merges (nothing new to merge: 0 first-seen, 0 newly checked 5c addresses).
