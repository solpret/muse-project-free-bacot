# FREE BACOT run 2026-11-06-1431 — route 4 scan + route 5c triage

## Scan summary (route 4)

- **Fix verified before run:** `onchain_nft_scan.py` contains per-contract
  `enrich i/n` logging with flush + JSON rewrite after EACH contract
  (atomic temp+replace, `"partial": true`; final write `"partial": false`).
- **Pre-flight:** OK, 8.2 s total (head via dataseed 4.6 s; `ankr_getLogs`
  50-block chunk 3.6 s, 1000 logs page-capped). Head at pre-flight 131969891.
  No `no_proxy` set; Ankr via existing proxy env.
- **Window scanned:** 131968930–131969929 (1000 blocks, head at scan start
  131969929; 20/20 chunks, 40 Ankr calls, 0 errors). Enrichment 194/194
  with per-contract logging; total runtime ~18 min. Final JSON
  `onchain-scan-2026-11-06-1431.json` written with `"partial": false` —
  **first fully successful main scan since the 1301/1331/1401
  enrichment-stall failures; the partial-write fix works as designed**
  (partial JSON was already on disk from enrich 1 onward).
- **Counts:** 194 NFT contracts (ERC721 188, ERC1155 6), 460 ERC-20 mint
  contracts. `hive_agents_found: false`.
- **Watermark:** shared `onchain-scan-state.json` `last_scanned_block`
  = 131939548 (backfill position) — **NOT advanced by this run**.
  Gap left for backfill: 131939549–131968929 (~29,381 blocks) plus any
  blocks after window head. Backfill owns the watermark.
- **Run log:** `run-2026-11-06-1431-scan.log` (pre-flight + per-chunk +
  per-contract enrich progress).

## First-seen triage (7 true first-seen: absent from both
## `onchain-scan-seen.json` [9,667 contracts] and `onchain-snapshot.json`
## [554 contracts])

### 🟢 EARLY LEAD 1 — WeZards (WEZARDS) `0xe4d7Ec33Fcf7D93cBE7F4D46d0ef35F437956aab`
- Agent-shaped: YES — `agentRegistry()` = `0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F`
  (exact), verified Sourcify ABI (46 fns).
- Free path: `mintAgenticFree()` nonpayable, no-arg; `FREE_ALLOCATION` 2500,
  `freeMinted` 27, `remainingFreeAllocation` **2473** (27/2500 claimed =
  1.08%); `MINT_PRICE` 0.001 BNB (paid leg only); `gasFeePerNFT` 0;
  `mintOpen` = 1; `hasClaimedFree(user)` = 0 → **user slot open**.
- First mints verified on-chain in this run: 16 mints / 16 distinct minters
  in-window; first mint block 131968955 = **2026-11-06 14:29:47 WIB**
  (tx `0xf658979ee0d6df8bdfc4b86e31a62717a7323fac0c19209cc133894c614c2753`).
  Zero mint logs for this contract back to block 131940000 (~11:00 WIB),
  so launch ≈ 14:29:47 WIB, age ~35 min at triage → **≤48 h VERIFIED**.
- Fresh re-read 15:06:50 WIB: totalMinted 27, freeMinted 27,
  remainingFreeAllocation 2473, mintOpen 1 (unchanged since triage).
- Legs: age ✓ ≤48 h; free-quota % 1.08% (< 25% strong-lead threshold, <
  50% candidate threshold); user slot ✓ open; X discussion unverified;
  website UNVERIFIED in this sub-task (`contractURI()` reverts → method H
  gives no link; name search found no WeZards site — generic Agent ID
  articles only). **Tier: EARLY lead** (never auto-mint/preview).
  Parent: add to snapshot watchlist; website/X checks via main-run
  routes 2/3/6 + methods (A)–(N).

### 🟢 EARLY LEAD 2 — AgentB (AGENTB) `0xc047F826E9E53D853c5683290EE50B6F02496529`
- Agent-shaped: YES — `registry()` = `0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F`
  (exact), verified Sourcify ABI (17 fns), bytecode registry hit.
- Free by construction: `mint()` nonpayable, no-arg; ABI has NO price/quote/
  paid-mint function at all (no payable fn); `hasMinted(address)` view.
  `MAX_SUPPLY` 10000, `totalMinted` 341 at triage → **382 at 15:06:50 WIB**
  (still minting fast). `hasMinted(user)` = 0 → **user slot open**.
- First mint (binary search, Ankr): block ~131965391 =
  **2026-11-06 14:03:03 WIB**; 63 mints / 63 distinct minters in-window.
  Age ~1 h at triage → **≤48 h VERIFIED**.
- Free-quota % leg: UNVERIFIED (no free-allocation/free view on-chain —
  never substitute total-supply %: 382/10000 is total %, not free %).
  So NOT a strong lead (leg b unverified); X discussion unverified;
  website not checked in this sub-task. **Tier: EARLY lead.**
- Note: same-name pair with `0x06ec…` below (launched 14:03 vs 14:24);
  per OG rule the earlier (this one) is the pair OG — with the user's
  caveat that one dev can run two same-name contracts. No `owner()` fn
  in ABI, so common-owner check was not possible.

### 🟢 EARLY LEAD 3 — AgentB (AGENTB) `0x06ecAE09523DA3698640728cc205305df5C33988`
- Agent-shaped: YES — `registry()` = `0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F`
  (exact), verified Sourcify ABI (19 fns incl. `contractURI`, `variantOf`).
- Free by construction: `mint()` nonpayable, no-arg; no price/quote/paid
  function in ABI. `MAX_SUPPLY` 10000, `totalMinted` 153 at triage →
  **186 at 15:06:50 WIB** (still minting). `hasMinted(user)` = 0 →
  **user slot open**.
- First mint (binary search, Ankr): block ~131968198 =
  **2026-11-06 14:24:06 WIB**; 19 mints / 19 distinct minters in-window.
  Age ~40 min at triage → **≤48 h VERIFIED**.
- Free-quota % leg: UNVERIFIED (no free view; total % 186/10000 is not
  free %). NOT a strong lead. X discussion unverified; website not
  checked in this sub-task. **Tier: EARLY lead** (later twin of the
  14:03 AgentB above).

### PAID-ONLY — RigOrb (RORB) `0x72D977237f7b3931A08434cEBD0D3814fE13539e`
- `AGENT_ID_REGISTRY()` exact match, verified ABI (37 fns), but tiered
  paid mint only: `PRICE_2_TO_10` / `PRICE_11_TO_15` / `PRICE_16_TO_20` /
  `PRICE_21_TO_30`, `priceAt`/`priceFor`, `TIER_*`; NO free view, NO free
  mint fn. `totalSupply` 1387 vs 3 in-window mints → launched well before
  the window. Owner `0x332eee23d818a05be0aa59651b991fad994b2419`, not in
  discards. **PAID-ONLY — not a lead, not added to snapshot.**

### Not agent-shaped (log only, not leads, not added to snapshot)
- **SANRAT Racers (SRACERS)** `0x8ebD4589F2d5bA4E50bFf69b40aD10722de461AC` —
  Sourcify no-abi, registry bytes False, 384 mints by **1 minter**,
  totalSupply 1280 / MAX_SUPPLY 10000, owner
  `0xe24ab7746daf859a1aa6c0db43c3056522c7599a` (not in discards).
  Bulk single-minter mint, not Agent ID–shaped.
- **bBroker (RWA)** `0x94bfa3AA4D95683385Fc9a345548179539cB1822` — no-abi,
  registry False, 4 mints / 2 minters.
- **EDUMARK** `0x3A1320343CA0B1a58B2eBbd973feB079e6A7Ad00` — no-abi,
  registry False, totalMinted 494, 1 mint in-window, owner
  `0xa4a368cdd4dd6f0a0a14b29d268b1dd76fd566c8` (not in discards).

## Route 5c — ERC-20 backlog (track C)
- Scan output: 460 ERC-20 mint contracts; **77 with window mint_count ≥ 10**.
- Already in `track-c-scan-checked.json`: **44**. New (never checked): **33**.
  **20 checked this run (cap 20)**, top by mint_count (111 → 12).
  Remaining **13 new unchecked** (sampling limit, dropped per body rule).
  (Note: the 5c script's own printout said "57 already checked" — that
  figure wrongly counts the 13 cap-dropped addresses; the correct
  accounting is 44 already / 33 new / 20 checked / 13 dropped, and the
  counts field in `run-2026-11-06-1431-5c-checked.json` carries the same
  wrong 57 — read 44 here instead.)
- **Sale-shape hits: 0.** All 20 were Sourcify not_verified/no-abi
  (0 fns) → no mint/quote/free-view fns to test; plain ERC-20s, not
  track C.
- Caveat: `eth_getCode` returned None for all 20 inside the 5c script
  (`registry_bytes: None`), but a direct re-test afterwards returned a
  12,374-char bytecode normally — transient/script-level failure, and
  verdicts are unaffected (no ABI ⇒ no S1/S2 possible regardless of
  registry bytes). 5c script needs a retry on eth_getCode before the
  next run.
- Newly checked addresses recorded in `run-2026-11-06-1431-5c-checked.json`
  (parent merges into `track-c-scan-checked.json`); the shared file was
  NOT overwritten by this worker. Full per-address results in that file;
  todo list (33 new ≥10) in `run-2026-11-06-1431-5c-todo.json`.

## Files produced (this run)
- `onchain-scan-2026-11-06-1431.json` — scan output (`partial: false`)
- `run-2026-11-06-1431-scan.log` — pre-flight + chunk + enrich + triage/5c logs
- `run-2026-11-06-1431-triage-lean.json` — lean field probes for the 7 first-seen
- `run-2026-11-06-1431-followup.json` — WeZards free-pool fields + AgentB registry/mint ABI
- `run-2026-11-06-1431-wezards-firstmint.json` — (superseded) first-mint search file
- `run-2026-11-06-1431-5c-todo.json` — 33 new ERC-20 ≥10 (20 checked, 13 dropped by cap)
- `run-2026-11-06-1431-5c-checked.json` — 5c shape-check results (20 checked, 0 hits)
- This file: `run-2026-11-06-1431-scan-triage.md`

## Parent actions needed
1. Report the 3 EARLY leads once (WeZards, AgentB 0xc047…, AgentB 0x06ec…)
   and add them to the snapshot watchlist (this worker did NOT write the
   snapshot or the seen file).
2. Merge the 20 newly checked 5c addresses into `track-c-scan-checked.json`
   (367 → 387).
3. Website/X verification for the 3 early leads via main-run routes
   (methods A–N); WeZards has no contractURI link, AgentBs have no
   `owner()` — deployer/website linkage still open.
