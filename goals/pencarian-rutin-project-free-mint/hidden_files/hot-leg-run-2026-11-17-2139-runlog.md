# free-mint-hot-leg run 2026-11-17 21:39 WIB

- Elapsed 18.8 s (target < 2 min). Script: hot-leg-2026-11-17-2139-run.py (adapted from 2124 run).
  Output: hot-leg-run-2026-11-17-2139.json, hot-leg-run-2026-11-17-2139-reread.json.
- Leg 1 Sourcify feed: 20 contracts, 3 new (0x85222E96..., 0xE3d86A1b..., 0x5f51140A...),
  all shape-checked S1=false S2=false (no mint/quote/free/agent). No sale shape.
- Leg 2 Boltbook EN 44.578 byte HTTP 200, ZH 42.757 byte HTTP 200; 3 new addresses
  (0x4342dB88..., 0x8b411Ba4..., 0xa9d139CE...). Sourcify ABI returned 0 fns for all three,
  so on-chain probe run 2139 was added: 0x4342dB88... eth_getCode 0x = NOT a contract
  (status corrected to checked-not-contract); 0x8b411Ba4... and 0xa9d139CE... are plain
  ERC-20s (name/symbol/totalSupply only, all sale views revert). None is a lead.
- Leg 4 re-read vs 2129: PunchCard totalSupply/totalMinted 1254->1255, freeMinted 1236->1237
  (22.3% free, far below the >70% strong-lead bar); bsccat freeMinted 513->514 (routine
  progress, no tier change). DRAGON mintOpen null->err revert and several bsccat views
  null->err revert are RPC read artifacts (views absent on those contracts), not state
  changes. No sellout, no slot loss, no age-exclusion, no pending-claim opening.
- Threshold check: PunchCard 22.3%, AGCLUB 58.8%, Matrix 58.6%, PIXELFROGS 15.1% -
  none above 70%. No promotion, no direct mint.
- Bridge (read-only): 116 contracts, 0 not in snapshot, 7 same_owner_discarded.
  No complementary-scan promotion.
- Poffzi FCFS: no process found (informational only; watchdog owns it).
- Executions: none - no preview, no mint, no claim. No chat report (nothing new per
  dedupe/reporting rule; routine +1 mint progress is not a reportable change).
