# Scan triage — run 2026-11-08 18:01 WIB (free-mint-search, scan legs only)

Read-only triage. Snapshot (onchain-snapshot.json), scan state/watermark
(onchain-scan-state.json) and seen file (onchain-scan-seen.json) were NOT
written by this run — parent to advance/add. No preview/mint/sign anywhere.

## (4) Pre-flight + scan

- Pre-flight: PASS. One 50-block ankr_getLogs chunk, head 132381433,
  248 logs, 8.2 s (< 60 s). Ankr via module import, proxy env untouched
  (no_proxy never set).
- Scan: COMPLETE, SCAN_EXIT=0, ~610 s. Command:
  `python3 .../onchain_nft_scan.py --chunk 50 --blocks 1000 --out .../onchain-scan-2026-11-08-1801.json`
- Window scanned: 132380479–132381478 (17:57:22–18:04:51 WIB; block
  timestamps via dataseed eth_getBlockByNumber, NOT Ankr).
  Chunks 20/20, no stall, no kill. Ankr calls 40, errors [], partial=false.
- Result: 134 NFT contracts (131 ERC721 + 3 ERC1155), 954 NFT mints,
  285 ERC-20 mint contracts. HIVE Agents NOT in window.
- Watermark before: 132377461. Skipped gap this run: 132377462–132380478
  (3.017 blok, backfill OFF). Earlier gap 132373210–132376461 (3.252 blok,
  run 1731) also still unscanned. Parent: advance watermark to 132381478.

## Triage — first-seen (absent from seen file 286 entries + snapshot contracts 512)

- First-seen: 60 contracts (registry address 0x60B926… excluded).
- Fresh vs historic (totalSupply/totalMinted read fresh per contract,
  batched 8 + single-call fallback; one batch hit dataseed rate limit
  -32005, retried chunked; 3 totalSupply reverts fell back to totalMinted):
  - FRESH (totalSupply == window mints): 0.
  - HISTORIC (totalSupply/totalMinted >> window mints): 59.
  - Supply UNREAD (totalSupply AND totalMinted revert): 1 — DIE Butterfly
    Cards 0x8e6236cfbEc0708CeA1e9E763Fc55966A6b5C813 (1 mint, registry=False,
    not agent-shaped).
- Verdict: ZERO early-lead candidates. No first-seen contract had its first
  mints verified on-chain in this run — every one minted before this window.
  Nothing to promote, nothing to report as a new lead from this scan.
- Agent-shaped (registry bytes hit): 49 of 60; not agent-shaped: 11
  (Twelve Zodiac Fragment, AGENT888, BNBeeTitan Genesis Pass,
  GuardianUnicorn, DIE Butterfly Cards, Stickman, GOEFR, GOEFS, Mizukairo,
  青铜, BNB Guardian AI).
- Same-owner-discarded: 22 of 60 (never promote/report as lead):
  - owner 0x11038f4a… (5): OBSIDIAN CARD 0x57E3F981…, THE KEY 0xA4835228…,
    ALL ACCESS 0xc3Ce0067…, GOLDEN TICKET 0x1De1A2Bc…, ORBIT PASS
    0x51D3C010… — totalSupply 279–370 vs 51–120 window mints; same
    mintWithAgentTokenId/freeLeft template wave (10 prior discards).
  - owner 0x53043412… (5): Cryptopus, Quackle, Wavelith, Starfishy,
    Turtlenova.
  - owner 0xd76d5918… (4): Strawgrim, Dronefarm, Cogniplex, Hexrotta.
  - owner 0x190f1f0c… (4): Krakenbo, Bailansloth, Jovibub, Hydrabit.
  - owner 0x75d251ba… (3): Shadow Ghouls, Aurum Pass, Luna Phase Agents.
  - owner 0xa0542755… (1): Periscopa (totalSupply 5052).
  - owner 0x1e1e3f44… (2): Contexa, Logiphon (Logiphon also a discarded
    contract). owner 0x310cea29… (2): Toolsmyth, Homunqul (also discarded
    contract). owner 0xb35349ee… (1): Parsewick. owner 0x293fc9e1… (2):
    Hot Springs, PRICKLY (both also discarded contracts).
  - Total flagged lines 23 incl. MONOLITH; MONOLITH corrected below → 22.
- CORRECTION — MONOLITH is NOT same-owner-discarded: its owner
  0xcbcadc7c… appears in same-owner-discards.json only under a single
  EXCEPTION entry (BNB Faucet: "owner ini belum terbukti sama dengan
  project lain, jadi TIDAK dibuang"). Do not treat MONOLITH as discarded.

### MONOLITH (MNTH) 0xcdA4A0EF9C0a626b2450168fd8F90f62C51A569b — detail

- Agent-shaped: YES (registry bytes, Sourcify verified, agentRegistry()
  returns exactly 0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F,
  hasAgentId(agent wallet)=1, freeMint + freeUsed in ABI).
- Window: 4 mints / 4 minters, first block 132380984. totalSupply 37,
  totalMinted 39, paidMinted 0, mintActive=1, MAX_SUPPLY 5555,
  price=0.0005 BNB. freeUsed() reverts without address arg (not read).
- Walk-back (Ankr, address-filtered Transfer-from-zero):
  132370000–132380478 = 11 mints, earliest block 132377160 (17:32:27 WIB);
  132340000–132369999 = 0; 132300000–132339999 = 0.
  24 of 39 totalMinted are unaccounted for (before block 132300000,
  ~08:00 WIB, OR totalMinted counts non-Transfer dev/reserve mints).
- Verdict: HISTORIC re-find, launch time UNVERIFIED, first mints NOT
  verified in this run → NOT an early lead, NOT a strong lead
  (age unverified + free % unverified). Record only; parent decides
  whether to deep-dive / watchlist. VerifiedAt 2026-11-08T11:05:47Z is
  NOT launch time.

### Oddlode Drills (DRILL) 0xce18531F9F639ca2351CA15FB2032D925b917472 — re-find

- Already MINTED BY USER at run 1631 (tx
  0xf515f49ce73580ec7f6cf541b1170e6122380f5de45e58e53e47eaf3b8beeb1a,
  block 132376388, token #814). This window: 1 mint, totalSupply now
  1002 (free cap 1000 → free pool likely exhausted). Do NOT re-report.

### Other first-seen agent-shaped, not discarded (all HISTORIC, no action)

- 山海经·八荒异兽·贰 BAHUANG2 0x57CC350b… (40 mints, totalMinted 486,
  freeMint/paidMint split); SpookySatoshi 0xA27de101… (ts 422);
  Tensortug 0xDdD2b550… (ts 293); Ore Raiders 0x4142045F… (ts 1880);
  PlanPilots 0x94ABb4Db… (ts 127); BotVoyager 0x2729Cc31… (ts 124);
  DinoEra 0xb7ae3eF5… (ts 74); CortexCove 0xF9D6C1df… (ts 144);
  AgentVertex 0xAD260537… (ts 138); Animora 0x150699b4… (ts 391);
  Golemar 0x4e067288… (ts 393); Autopoiet 0xC5c66b64… (ts 314);
  Saturndroid 0xb884dc59… (ts 625); Krakenbo 0x46c18150… (ts 672);
  Jolly 0xDC11764a… (totalMinted 3792); ONI 0x74BDA11E… (totalMinted 142);
  Aegis Core Protocol 0x5491f234… (ts 1969); Soul Agent 0x8fdB9411…
  (ts 2109); Bailansloth 0xD382652f… (ts 460); Jovibub 0x9e79f749…
  (ts 394); DGF CARD 0x01f9CA4f… (totalMinted 1534); Hydrabit
  0x1de7691D… (ts 430). Full 60-row table with mint counts, first/last
  blocks, registry, sourcify, free_shaped, mint_funcs, totalSupply and
  owner is in /tmp/first_seen_1801_enriched.json (working copy; parent
  to add the 60 to onchain-scan-seen.json).

## (5a) Sourcify cross-check

- Poll: https://sourcify.dev/server/v2/contracts/56?limit=20&sort=desc —
  20 recently verified, all exact_match, verifiedAt 10:35–11:08 UTC.
- Mint-shaped + agent-gated (S1-loose): 3 — all already in the scan
  window, deduped to ONE finding each, none new:
  - MONOLITH 0xcdA4A0EF… (see above; historic, age unverified).
  - ORBIT PASS 0x51D3C010… (registry=True, in scan; same-owner-discarded).
  - THE KEY 0xA4835228… (registry=True, in scan; same-owner-discarded).
- Sale-shaped but NOT a track-C lead — SaleV12
  0x7047aED5293a7fD0Bc3CFB281C0699939761a3C7 (verifiedAt 10:39:41Z):
  ABI has buy/claimFree + costFor + FREE_SHARES/freeClaimed/freeMinted,
  token() = 0x2cdc5f77279fb03226ffe6ccbC6546d50a949841,
  FREE_SHARES 500, freeMinted 0, TOTAL_SHARES 5000, TOKEN_PER_SHARE 500,
  saleStart=0 (not started), saleEnd=259200, finalized=0, soldOut=0,
  agentSigner=0x80dcc413…, owner=0x01bb717a….
  FAILS S1 registry/AgentGate leg: no agentRegistry view, bytecode has
  NO registry bytes (checked via eth_getCode); agentSigner alone is not
  a registry reference. Also NOT in the scan window (no mints observed)
  and sale not started. Record as checked, not a lead. Not in snapshot
  track_c.
- Other 16: no mint/sale shape (incl. 0x3d8Fe931… ownerMint/price only,
  0x43A28693… claim only, 0x61722A16… claim/manualMint/quoteFee without
  free views or registry). verifiedAt is NOT launch time for any of them.

## (5c) Track-C backlog

- Scan output erc20_mint_contracts_list: 47 entries with window
  mint_count >= 10 (sorted desc; top: 0xE07150DD… 1194, 0x78573aB4…
  795, 0x10834340… 741).
- Already in track-c-scan-checked.json: 45. Newly shape-checked this run
  (Sourcify ABI sale-shape S1/S2): 2 — 0xb50dC583cC6F83750c36789F52d51E12dA664444
  (mc 62; mint/minter/closeMinting, quoteToken, no free views, no
  registry → NO HIT) and 0xEBbA172c2Dfdd677873102390bfd54aFe0B40D5f
  (mc 20; mintTo/minter, no quote, no free views → NO HIT).
- Hits S1/S2: 0. Dropped by sampling limit: 0 (all 47 covered: 45
  previously checked + 2 new).
- NOTE: track-c-scan-checked.json was NOT written (read-only task) —
  parent to append the 2 newly checked addresses:
  0xb50dC583cC6F83750c36789F52d51E12dA664444 and
  0xEBbA172c2Dfdd677873102390bfd54aFe0B40D5f.

## For parent (main run)

- Scan legs complete, no new early/strong/track-C lead from this window.
  No chat report is produced by this scan alone.
- Bookkeeping still to do by parent: advance watermark 132377461 →
  132381478; add the 60 first-seen contracts to onchain-scan-seen.json;
  append the 2 newly 5c-checked addresses to track-c-scan-checked.json.
- Open anomaly (no action taken): MONOLITH totalMinted 39 vs 15 Transfer
  mints observed in blocks ≥132340000 — 24 mints unaccounted for
  (pre-132300000 or non-Transfer dev/reserve mints); first mint unpinned.

## Files

- Scan output: ~/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/onchain-scan-2026-11-08-1801.json
- This triage: ~/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/run-2026-11-08-1801-scan-triage.md
- Working copies (enriched first-seen table, 5c results, MONOLITH/SaleV12
  state): /tmp/first_seen_1801_enriched.json, /tmp/fivec_1801.json,
  /tmp/monolith_state.json, /tmp/salev12_state.json, /tmp/monolith_walkback.json
