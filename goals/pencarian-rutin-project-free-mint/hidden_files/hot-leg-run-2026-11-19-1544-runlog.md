# Hot-leg run 2026-11-19 15:44 WIB — SILENT (no new lead / candidate / change / promotion)

- Sourcify feed (limit 20): 20 contracts returned, verified 08:17–08:45 UTC — ALL 20 NEW vs hot-leg-seen (fresh window after the 15:09 run's 07:32–08:12 UTC window). Shape-check (all 20, no errors): S1=False, S2=False for every one — no sale-shape hit. Recorded checked-not-sale-shape. seen 17273 → 17294.
- Boltbook EN 200 (45.649 byte) + ZH 200 (45.358 byte; EN first fetch 302, followed redirect to ?lang=en): 4 EN / 5 ZH addresses, 1 NEW.
  - 0x7573fbacd2bae8250705362bf4f13440788b86d0: Sourcify 404 (unverified, no ABI); eth_getCode 0x = not a contract. Recorded shape-check-failed / checked-not-contract, not a lead.
  - (Note: script's byte counts 44.803/42.675 are Unicode char counts, not file bytes; files on disk are 45.649/45.358 byte.)
- Re-read leg (block 134473830, 54.1s total run, Quicknode batch; several reads rate-limited -32007 15/s):
  - STOCK AGENT 0xba7068233da805bdebcc167be361c219002e6b7f: totalSupply 875 flat vs 15:09; freeLeft 236 flat; FREE_SUPPLY now readable 1111 → free claimed 875/1111 = 78.8% (>70% leg) BUT age + website still UNVERIFIED → stays EARLY LEAD, no promotion, no execution. quote(user,1) rate-limited this run (was 0 at 15:09 — rate limit, not a state change); freeMintedByWallet(user)=0 flat.
  - binanceai-mint 0x46cb1D3efd4307506Cda7EbBa5a51be64746739E: launched=0, failed=1 now readable (was rate-limited at 15:09); isRefundPhase/totalShares/tokenClaimed(user) rate-limited this run. Consistent with last verified 15:01 WIB (launched=0, failed=1, refund=1). No change evidenced.
  - RigForge 0xa1cc0d7c0534f824f2cf6eeb865a8fede96c8f7d: freeSharesLeft 621, openedAt 0, freeClaimed 379 — unchanged, still not open.
  - AONE-sale 0x84D82E933D7781fe11245e7bbd3Eb23dbb963666: freeMinted 10000/10000 FREE_TOTAL — sold out (already reported).
  - bsccat 0x9dd4C7D3276609892cF723a90A5AF3f8df40C79A: freeMinted 554 → 557 (+3 mints, totalSupply 557.000.000) — mint activity only, no tier change (no sellout, no slot loss, no age-exclusion), run-log note only.
- Bridge leg (read-only): 116 contracts; 1 not in snapshot = DGF CARD 0x01f9ca4ff95d49594cc8b6591022186dc5c1bc72 (age-excluded, already reported once as scan finding, NOT a lead of this job). 7 same_owner_discarded — never promoted. No promotion/change.
- Execution: none. Chat report: NONE (silent run per body rules).
- Overrun note: run took 54.1s — inside the <2 min target. No pile-up.
- Files: hot-leg-run-2026-11-19-1544.py, hot-leg-run-2026-11-19-1544-reread.py (n/a — combined script), hot-leg-run-2026-11-19-1544-reread.json, hot-leg-run-2026-11-19-1544-sourcify-shape.json, hot-leg-run-2026-11-19-1544.json, hot-leg-2026-11-19-1544-boltbook-en.html, hot-leg-2026-11-19-1544-boltbook-zh.html, hot-leg-run-2026-11-19-1544-runlog.md. Snapshot NOT rewritten.
