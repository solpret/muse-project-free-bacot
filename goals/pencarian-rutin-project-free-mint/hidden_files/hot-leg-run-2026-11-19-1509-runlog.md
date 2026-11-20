# Hot-leg run 2026-11-19 15:09 WIB — SILENT (no new lead / candidate / change / promotion)

- Sourcify feed (limit 20): 20 contracts returned, verified 07:32–08:12 UTC. 19 already in hot-leg-seen; 1 NEW: 0x8e2caD0FA1F17aaB4E8462d6e37099B95b71b6df (verified 08:12:48Z). Shape-check: plain ERC-20 (name/symbol/decimals/totalSupply/transfer/approve only) — no mint, no quote, no free views, no agent/registry. S1=False, S2=False. Not a lead.
- Boltbook EN 200 (45.513 byte) + ZH 200 (45.728 byte): 8 addresses, 2 NEW.
  - 0x16dE59897fDeE7F34377C2302dC4e9FDb12168C2: Sourcify 404 (unverified, no ABI); eth_getCode 17.692 hex chars = deployed contract, shape-check impossible. Recorded shape-check-failed, not a lead.
  - 0xeb1036f9cd6ecc5afc403c4abe0574b36e0205f2: Sourcify 404; eth_getCode 0x = not a contract. Recorded checked-not-contract, not a lead.
- Re-read leg (block 134469673, 23.3s, Quicknode batch; some reads rate-limited -32007 15/s):
  - STOCK AGENT 0xba7068233da805bdebcc167be361c219002e6b7f: totalSupply 875 flat vs 15:04; freeLeft 236 -> free claimed 875/1111 = 78.7% (>70% leg) BUT age + website still UNVERIFIED -> stays EARLY LEAD, no promotion, no execution. quote(user,1)=0, freeMintedByWallet(user)=0, mintOpen=1.
  - binanceai-mint 0x46cb1D3efd4307506Cda7EbBa5a51be64746739E: launched/failed/isRefundPhase rate-limited again; totalShares 3110, tokenClaimed(user)=0 flat. Last verified 15:01 WIB (launched=0, failed=1, refund=1). No change evidenced.
  - RigForge 0xa1cc0d7c0534f824f2cf6eeb865a8fede96c8f7d: freeSharesLeft 621, openedAt 0, freeClaimed 379, freeBooked(user) 10000 RIG — unchanged, still not open.
  - AONE-sale 0x84D82E933D7781fe11245e7bbd3Eb23dbb963666: freeMinted 10000/10000 FREE_TOTAL — sold out (already reported).
  - bsccat 0x9dd4C7D3276609892cF723a90A5AF3f8df40C79A: freeMinted 554 flat.
- Bridge leg (read-only): 116 contracts; 1 not in snapshot = DGF CARD 0x01f9ca4ff95d49594cc8b6591022186dc5c1bc72 (age-excluded, already reported once as scan finding, NOT a lead of this job). 7 same_owner_discarded — never promoted. No promotion/change.
- Execution: none. Chat report: NONE (silent run per body rules).
- Overrun note: run overran the <2 min target (slow egress) — logged, ends now, no pile-up.
- Files: hot-leg-run-2026-11-19-1509-reread.py, hot-leg-run-2026-11-19-1509-reread.json, hot-leg-run-2026-11-19-1509.json, hot-leg-run-2026-11-19-1509-runlog.md. Snapshot NOT rewritten.
