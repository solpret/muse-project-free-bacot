# On-chain NFT discovery scanner — prototype test (2026-11-01, READ-ONLY)

## What was built

Script: `onchain_nft_scan.py` (same folder as this report).

How to run it:

```text
python3 onchain_nft_scan.py [--blocks 300] [--chunk 50] [--out out.json]
```

What it does, in order:

1. Reads the latest BSC block via the `fast_rpc` dataseed pool.
2. Scans the last N blocks in chunks via Ankr `ankr_getLogs`, imported as a
   module (the Ankr CLI truncates output at 4000 chars and must NOT be used
   for log scans). The call is chain-wide: no contract-address filter, only
   a topics filter, so it finds contracts nobody posted about.
3. Classifies mint events:
   - ERC-721 mint = topic0 Transfer, topic1 (from) = zero address, 4 topics.
   - ERC-20 mint = same, but 3 topics (value in data) — counted separately
     and excluded from NFT results, proving the filter separates them.
   - ERC-1155 mint = topic0 TransferSingle, topic2 (from) = zero address.
4. Groups by contract (mint count, distinct minters, first/last block).
5. Per distinct NFT contract, runs cheap agent-shape checks: `eth_getCode`
   with a substring test for the Agent ID registry address bytes
   (`60b9262456de011f7d15a54cdd8c48baaa8b022f`); Sourcify ABI lookup
   (`/v2/contract/56/<address>?fields=abi`) with a scan for free-shaped
   function/variable names and mint functions; `name()` / `symbol()` reads.
   A failed read is recorded UNVERIFIED, never zero.
6. Prints an explicit verdict on the validation target (HIVE Agents).

Selectors, keccak-verified with pycryptodome on 2026-11-01:

- Transfer: `0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef`
- TransferSingle: `0xc3d58168c5ae7397731d063d5bbf3d657854427343f4c083240f7aacaa2d0f62`
  - WARNING: a draft selector `0xc3d58168c4e7...` seen in task notes is
    WRONG — it does not match
    `keccak256("TransferSingle(address,address,address,uint256,uint256)")`.
    The script uses the keccak-computed value above.
- name(): `0x06fdde03`, symbol(): `0x95d89b41`.

Rate-limit behaviour: 2.2 s spacing between Ankr calls (under the 30
req/min Freemium cap); on a 429 it sleeps 30 s and retries once, then
records the error and stops that leg. It never hammers.

## Probe run (10 blocks, before the full test)

- Window: blocks 131051565–131051574.
- Result: 20 NFT mints across 13 contracts, plus 19 ERC-20 mint contracts
  (correctly excluded). 2 Ankr calls, zero errors. The TransferSingle
  positional-wildcard filter `[selector, null, zero]` was accepted by Ankr
  (no fallback needed).
- Registry-bytes hits included real agent-shaped contracts (e.g. Andvari's
  Gold, Bobaloo, Potionix, Hyper Shark Agent). NOTE: the SPACE ID Agent ID
  registry contract itself (`0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F`)
  appears as a "contract" with 2 mints — those are Agent ID registrations,
  and its registry-bytes hit is trivially true. The routine wiring MUST
  exclude the registry address itself from leads.
- HIVE Agents was NOT in this 10-block window — expected, not a filter
  failure: at ~0.5 mints/min, a 30-second window should usually contain
  zero HIVE mints.

## Full test run (300 blocks) — VALIDATION PASSED

- Window: blocks 131051362–131051661 (300 blocks, ~15 min), latest block
  131051661 at scan time. Full output preserved at
  `onchain_nft_scan_2026-11-01_300blocks.json` (same folder; `/tmp` copies
  are ephemeral and were not relied on).
- Cost: 12 Ankr calls, 0 errors, 0 rate-limit hits. Wall-clock ~6 minutes
  (launch to output file), dominated by the per-contract check phase, not
  by Ankr.
- Totals: 167 NFT contracts, 12,808 NFT mints (12,797 ERC-721 + 11
  ERC-1155 across 2 contracts), plus 222 ERC-20 mint contracts correctly
  excluded by the 3-topic/4-topic filter.
- Sourcify: 48 verified / 119 not verified. Registry-bytes hit: 136/167.
  That hit rate (81%) is a WARNING, not a triumph: the agent-mint factory
  template is so common that registry bytes alone barely discriminate.
  The routine must combine it with free-shaped ABI evidence and
  first-seen filtering (see recommendation), never report on registry
  bytes alone.

### Validation target: HIVE Agents — CAUGHT

`0x1458b0C132Fb51BDC65B1Ca7a3BE484BCd9A2f77` appears with 1 mint by 1
minter (`0x97ed...d274f`) at block 131051436, registry-bytes hit true,
Sourcify verified, free-shaped functions `FREE_PER_WALLET`, `FREE_SUPPLY`,
`freeMintedBy`, name "HIVE Agents", symbol "HIVEA". This matches the
known live state (totalSupply 562–564, slowing) — exactly one mint in a
15-minute window is consistent with its slowing rate, and the scanner
still caught it. Validation PASSED, no fudging needed.

### ERC-1155 path — validated end-to-end

2 contracts, 11 mints: `0xE6D3...bfbbfb3` (10 mints, 1 minter, verified,
no mint functions in ABI) and RAX Fragments `0x1436...9613` (1 mint,
`mintFragment`/`mintOperators`). Both registry False — correctly not
agent-shaped leads. The keccak-verified TransferSingle selector works;
the draft selector in task notes was wrong and was NOT used.

### Notable contracts in the window (evidence, not verdicts)

- Free-shaped + registry-hit shortlist (27 contracts, the routine's real
  lead pool): Genesis Seeds (GSEED, 50 mints/22 minters), sidecoo Daily
  (SCDAILY, `freeMint`), Arcadion, Maple Agent, Pixeloo, Byteshi,
  Wraithlet, sidecoo Agent Pass, FAMULI, Agentlings, Bobaloo, Skatoon,
  Fireflux, Chromecat, Cupcakia, Whalesong, Core Reactor, Koimatic,
  MothWire, Synklings, Jovibub, Skullbride, Dragonmonk, Egg, Potionix,
  Tangpingo, and HIVE Agents. Full per-contract evidence is in the JSON.
- Cross-validation with the earlier Boltbook sweep: the scanner
  independently re-found KENRAI (9 mints/9 minters, `agentMint`),
  AgentRadiant (RDNT, 1 mint), Wise Owl Society (OWLS, 1 mint,
  permit-gated functions), Night Shift Agents (NIGHT, 1 mint), Swarm
  Threshold (6 mints), sidecoo Daily, Agentlings, StonkRobotics Entry,
  Synklings, Ptah Proof of Agent. Two independent discovery layers
  agreeing is a strong signal the scanner sees the same scene.
- Correctly NOT leads: two "Card Agent" contracts with 6,000 mints each
  from a single minter (owner bulk-minting, registry False); BNB WOLF
  (167 mints/49 minters, registry False); the SPACE ID Agent ID registry
  itself (15 mints — Agent ID registrations, must be excluded from leads
  by address, not by shape).
- Andvari's Gold: 109 mints / 109 distinct minters, registry True,
  Sourcify NOT verified — the highest genuine minter breadth in the
  window, but with no ABI its free shape is unknown. This is the
  prototype's sharpest limitation (see below).

### Prototype limitations (stated plainly)

- Unverified contracts (119/167, 71%) cannot be free-shape-checked from
  an ABI that does not exist; their `free_shaped` is always empty. They
  need either bytecode-level function analysis or a direct free-view
  probe — neither is in this prototype.
- `freezeMetadata` matched the naive substring "free" in the test output;
  the script has since been fixed to a curated test that excludes
  `freeze*` names. Test-run JSON still lists `freezeMetadata` entries —
  ignore those when reading it.
- First-seen block in a window is a LOWER bound on launch, not a launch
  time: a contract minting before the window looks "new" to one run.
  Only a persistent seen-set across runs gives true first-seen.
- Ankr credit cost per chain-wide call is UNVERIFIED (the connector doc's
  ~700 credits/call figure is for per-contract log calls, not chain-wide
  calls). Countable cost is 12 calls per 300 blocks; monitor real usage
  on the first wired runs before assuming the monthly budget.
- The scanner reads mints, not free quotas: a minting contract is a lead,
  never a candidate. Free quota, %, age, and X still need their own
  verification before any candidate/auto-mint decision.

## Other non-Boltbook sources (all tested, read-only)

### BscScan ERC-721 transfers page — BLOCKED (403)

`https://bscscan.com/tokentxns-erc721` via text fetch returned HTTP 403
(access denied), consistent with the earlier 403 on a BscScan contract
page. BscScan is therefore NOT usable as a routine text source. A live
browser read would be needed to test whether the page renders there at
all; that check is out of scope for this subagent and is left for the
parent. No further BscScan endpoint was attempted after the denial.

### Sourcify recently-verified feed — WORKS, verified live

Endpoint (documented at docs.sourcify.dev, then fetched live):

```text
GET https://sourcify.dev/server/v2/contracts/56?limit=10&sort=desc
```

Live result: 10 most recently verified BSC contracts with address,
`verifiedAt`, and match type. The 10 fetched were verified
2026-11-01T12:36–12:46Z (19:36–19:46 WIB) — minutes fresh. Parameters:
`limit` (max 200), `sort=desc` (most recent first, default),
`afterMatchId` for paging. Filter test on 3 of the 10 ABIs: one had 30
functions and no mint function (correctly rejectable); one had
`mint`/`minter`; one had `MINT_FEE`/`mint`/`mintOpen`/`mintPrice`/
`mintedBy`/`setMintOpen` (mint-shaped). So the feed + ABI-shape filter
is a workable second leg. Caveats: `verifiedAt` is NOT launch time (a
contract can be verified hours after deployment), and Sourcify asks users
not to bulk-crawl the lookup API — polling the latest 10–50 every 30
minutes is light use, not a bulk crawl, but the poll size should stay
small. The full database is also available as daily Parquet / BigQuery,
which needs GCP setup and is NOT recommended for the routine.

### Independent keyless public RPC eth_getLogs — BLOCKED / UNUSABLE

- PublicNode (`https://bsc-rpc.publicnode.com`): HTTP 403 on `eth_getLogs`.
- Blockmachine keyless endpoint (`https://rpc-bsc.blockmachine.io`):
  request timed out after 25 s.
- This matches the published finding that BSC public nodes switch off
  `eth_getLogs`. Conclusion: there is no usable keyless public-RPC log
  source; Ankr (already connected) is the log source.

### Other keyless feeds considered — NOT applicable

- CoinGecko keyless API / CoinMarketCap keyless API: market + DEX token
  data (CoinMarketCap even has a DEX "new tokens" list) — tokens and
  pools, NOT NFT mints. No NFT launch feed.
- OpenSea tools (SeaDrop reader): needs a contract address first — a
  checker, not a discovery feed.
- oanor NFT API, NFTScan, Moralis, Alchemy NFT API, Bitquery streams:
  all need an API key or a paid plan — excluded by the task.
- GeckoTerminal / DexScreener: token pools only, no NFT mints.

## Verdict table

| Source | Verdict | Evidence |
|---|---|---|
| Ankr chain-wide mint scan (prototype) | WORKS | 10-block probe: 20 mints / 13 contracts, 0 errors |
| Sourcify recently-verified feed (chain 56) | WORKS | Live fetch: 10 contracts, minutes fresh; ABI filter tested |
| BscScan tokentxns-erc721 (text fetch) | BLOCKED (403) | 403, consistent with earlier BscScan 403 |
| Keyless public RPC eth_getLogs | BLOCKED / UNUSABLE | PublicNode 403; blockmachine 25 s timeout |
| CoinGecko / CoinMarketCap keyless | NOT APPLICABLE | Token/market data, no NFT mint feed |
| Key-gated NFT APIs (NFTScan, Moralis, Alchemy, Bitquery, oanor) | EXCLUDED | Need a key or paid plan |

## Recommendation for wiring into the 30-minute routine

The scanner is ready to become the routine's on-chain leg, and it maps
directly onto the standing FREE BACOT EARLY-LEAD TIER (approved
2026-11-01 ~19:55 WIB): a newly detected agent-mint-shaped contract whose
first mints verify on-chain in the run is reported ONCE as EARLY (never a
candidate), then promotes to strong lead on the 3 strong-lead legs and to
candidate only on ALL criteria + safety. Until now that tier had no
on-chain feed; this scanner is that feed.

Concrete wiring (each 30-minute run):

1. Run the scanner over blocks since the last run's watermark (store
   `last_scanned_block` in the snapshot; ~600 blocks per 30 minutes at
   3 s/block). At the measured pace this is the one scaling question:
   300 blocks took ~6 min, so a naive 600-block run takes ~12 min —
   acceptable inside a 30-minute cadence but wasteful. Optimize before
   wiring: (a) keep a persistent seen-contract set and full-check ONLY
   first-seen contracts (re-reads of known contracts need only mint
   counts for watchlist items); (b) batch `eth_call`s for name/symbol
   where the RPC helper supports it; (c) skip name/symbol for contracts
   with no free-shaped evidence. Steady-state estimate after (a): Ankr
   ~24 calls + full checks for ~50–100 new contracts ≈ 3–5 min per run.
   Measure the first wired run; do not promise faster until measured.
2. Lead rule per run: report ONCE as EARLY every contract that is
   (a) first-seen in this run, (b) agent-shaped (registry-bytes hit OR
   free-shaped ABI — either, not registry alone, given the 81% hit rate),
   (c) NOT the registry address itself, NOT on the excluded/known list,
   (d) NOT already in the seen-set. Log everything else; report only the
   shortlist. A contract is never re-reported as EARLY.
3. EARLY leads go to the snapshot watchlist; later runs track their mint
   counts (velocity), free quota (once ABI/views are known), and age.
   Promotion follows the existing tiers only: strong lead on the 3 legs,
   candidate on ALL criteria + safety, auto-mint only for candidates.
   Scan output alone NEVER previews or mints.
4. Second leg, same run: poll Sourcify
   `/v2/contracts/56?limit=50&sort=desc`, filter ABIs for agent/free
   shape, and cross-check against the scan set. A contract in BOTH sets
   is a stronger lead. Remember `verifiedAt` is not launch time, and
   keep the poll small (Sourcify asks users not to bulk-crawl).
5. Do NOT wire BscScan (403) or keyless public-RPC logs (403/timeout).
   Do NOT add X to this leg (credits nearly exhausted; the scan leg is
   valuable precisely because it needs no X).

What remains unverified and must be checked on the first wired runs:
Ankr credit cost per chain-wide call; sustained polling behaviour at
~48 runs/day; the optimized runtime after first-seen filtering; and a
bytecode-level free-shape check for the 71% unverified contracts.
