# Deep free-mint discovery sweep — 2026-11-01 evening WIB (READ-ONLY)

No previews, mints, approvals, signatures, or transactions performed.
Wallet for free-quota checks: 0xeb237F6f9FB4e826739F0954e9768914F28b2c2E (Agent ID masgayut).
Read blocks: 131048685 (~19:35 WIB), 131049321 (~19:45 WIB), 131049767 (~19:55 WIB),
HIVE Agents settle ~20:00 WIB. Reads via ~/workspace/fast_exec/fast_rpc.py race(),
ambiguous items settled with direct _single calls (REVERT = view absent, not zero).

## Verdict summary: ZERO candidates pass all 7 legs. Top watchlist item: HIVE Agents.

## 1. Stale leads (task 1)

### LMWR — Lumen Wraiths — EXCLUDED (free sold out)
- Contract (full, recovered from Boltbook ranjha.ai post): 0xaDC5BB4E4F4D14B8F8f0172D77E6dbDbd8EdC6f2
- Site: not found. X account: not found (project-stated handle nowhere surfaced).
- Launch: earliest evidence = ranjha.ai post ("2d ago" at Nov 1 crawl) at block 130490933
  with 787 minted; routine logs first mention it Oct 31 06:01 (cryptoismic mention, no
  contract in readable text). Best estimate Oct 29-30 → likely >48h at Nov 1 evening,
  but no project-stated launch timestamp → age formally UNVERIFIED, and moot anyway:
- On-chain read (block 131049321): name Lumen Wraiths, symbol LMWR, totalSupply 2888,
  freeMinted 2888, FREE_CAP 2888, FREE_PER_WALLET 4, MAX_PER_WALLET 20, MAX_SUPPLY 10000,
  PRICE 0.01 BNB, freeLeftFor(user) 0, mintCost(user,1) 0.01 BNB, balanceOf(user) 0.
- Free quota: 2888/2888 = 100% claimed → FREE SOLD OUT (19:01 run: 1653 → now 2888).
- Legs: (1) BSC yes; (2) free quota NO (sold out, paid 0.01 now); (3) Agentic yes
  (Agent ID gate, checks registry 0x60B9...022F); (4) X account NO; (5) age UNVERIFIED
  (likely >48h); (6) % was 57.2% at 19:01, now 100% but sold out; (7) velocity n/a.
- Answer to "correctly excluded or missed while young": the routine never resolved its
  contract while it was young (only a nameless mention Oct 31 06:01, then the 19:01
  run's 1653/2888 mention still without contract/site/X/launch) — a genuine discovery
  miss in process. By Nov 1 evening it is sold out regardless, so nothing is lost now.

### Night Shift Agents — EXCLUDED (age + no site/X + % unverified; user-cancelled Oct 29)
- Contract (full, recovered from clean Boltbook ranjha.ai post "8 gas-only .ai mints",
  matching the truncated 0x427a…cf14 from run logs): 0x427aed3f7427b48e45f5e648105aa1b77724cf14
- Site: not found. X account: not found.
- Launch: first evidence = ranjha post at block 130034103 with 1092/10000 (post also
  lists a project whose window closes Oct 28, placing it ~Oct 27-28) → >48h old at
  Nov 1 evening → age EXCLUDED. Run logs also record it as user-cancelled 2026-10-29.
- On-chain reads (blocks 131049321 + settle 131049767): name Night Shift Agents,
  symbol NIGHT, totalSupply 8091, MAX_SUPPLY 10000, mintOpen true, quote(user,1) = 0
  (user's first mint still free), balanceOf(user) 0. FREE_SUPPLY / freeClaimed /
  freeLeft views REVERT (absent): free = 1 per wallet, no global free cap.
- Free quota % leg: UNVERIFIED — 8091/10000 = 80.9% is TOTAL supply %, not free-quota
  %; no distinguishable free cap exists, so total % must not be substituted.
- Legs: (1) yes; (2) user slot open (quote 0) but not a candidate for other legs;
  (3) yes (Agent ID gate); (4) NO; (5) NO (>48h); (6) UNVERIFIED; (7) n/a.

## 2. Fresh finds (task 2, all from Boltbook agent posts)

### Wave 1408-1412 (5 factory lanes, deployer 0xa054275580c6d1c9077543907ac5798f2494ecce) — EXCLUDED (free sold out)
- Gourdsentinel 1408 0x337d1669f9d0cf0903184ee8d1832aeb52f295fd (GRDSNT, MAX 939)
- Neonronin 1409 0x5b982aa9bc4b13ec075fc8771b5f5b22d6c9fafa (NNRONN, MAX 946)
- Cogwright 1410 0x0edea6f95561a65ba22add7e90ac816a9bf7cd5e (CGWRGT, MAX 895)
- Ringfarer 1411 0x85bb268325609cad57db8738dc5f11002b29c5d9 (RNGFRR, MAX 1050)
- Jackalpharos 1412 0xcdda8204d8705e12de56460d22c856adc3f77c41 (JCKLPH, MAX 1118)
- All Sourcify exact_match, FREE_SUPPLY 200, FREE_PER_WALLET 1, mint(uint256) value 0.
- Timeline (free claimed / 200): ~19:05 WIB: 157/149/121/140/158 (275 seats left);
  ~19:25: 177/172/137/158/180 (176 left); ~19:35: 200/200/192/194/200 (14 left);
  ~19:55: ALL 200/200, quote(user,1) = 0.00005 BNB, freeLeft(user) 0 → FREE SOLD OUT.
- Site: none found. X account: none found. Launch: no project-stated time (first
  Boltbook evidence today evening) → UNVERIFIED. The whole wave lived and died in
  ~1 hour — a 30-minute cadence sweep can only catch such waves if it reads the
  Boltbook front page every run.

### AgentRadiant / DataDynasty / NeuralHarbor (Alphapedia scan trio, today 19:07-19:15 WIB) — watchlist-only (fail %)
- AgentRadiant 0x216729a1b9a734352dc7817ffef9ecbe5c857f76 (RDNT, MAX 1815):
  totalSupply 263, FREE_SUPPLY 1270, freeClaimed 264 (1-unit discrepancy vs
  totalSupply, as read), mintOpen true, quote(user,1) 0, freeLeft(user) 1, balance 0.
  Free % = 264/1270 = 20.8% → FAILS ≥50%. (Sourcify: not verified, 404.)
- DataDynasty 0x6c449d581548ad896c4ae42b7337092cbf21215e (DDYN, MAX 1820):
  totalSupply 85, FREE_SUPPLY 1274, freeClaimed 85, quote 0, freeLeft 1 → 6.7% FAIL.
- NeuralHarbor 0x63902292888bd65adc1f45f37cd37f666f11c043 (NHRB, MAX 1750):
  totalSupply 106, FREE_SUPPLY 1225, freeClaimed 106, quote 0, freeLeft 1 → 8.7% FAIL.
- totalMinted() reverts on all three (view absent; totalSupply is the supply view).
- Site/X/launch: none found for any → age UNVERIFIED, X account NO. User free slots
  open, but % + age + X all fail → watchlist-only.

### KENRAI (KNRI) — watchlist-only (% unverified, age unverified, no site/X)
- Contract 0xb57b295d59eef53f3009154f645a3dec648b9ff8, Sourcify exact_match
  (verifiedAt 2026-10-31T19:46:07Z — verification time is NOT launch time).
- Read (block 131048685): totalMinted 2911, MAX_SUPPLY 8888, agentMintOpen true,
  agentClaimed(user) false, balanceOf(user) 0, price (public) 0.0006 BNB.
  Free = 1 per wallet via agentMint(); NO free-cap view exists → % leg UNVERIFIED.
- Launch: first Boltbook evidence Nov 1 morning (KENRAI 1928 in a morning post,
  #2643 at block 131030596) → no project-stated launch time → UNVERIFIED.
  Site/X: none found. User agent slot still open, but not a candidate.

### AGENT NFT (agent币, AGENT) — EXCLUDED (free sold out)
- Contract 0x02a3ac26012cc7017f5cf4e4d481ee243f9cceb4, Sourcify exact_match.
  First-free path needs Agent ID + per-wallet 22-bit PoW (POW_BITS 22, MINT_WINDOW
  172800s = 48h). Author tied NO official site to it.
- Reads: 14:08 WIB (author): freeMinted 3295/4000, genesisMinted 3425/6666.
  ~19:45 WIB (this sweep): freeMinted 4000, freeCap 4000, freeRemaining 0,
  genesisMinted 4190, maxSupply 6666, mintOpen true → FREE SOLD OUT.
  totalSupply()/start()/end() REVERT (views absent).
- Launch: post cites end time 2026-11-02 06:00 UTC; start = end − 48h window =
  2026-10-31 06:00 UTC (13:00 WIB) is a DERIVATION, not a direct read → age
  formally UNVERIFIED (moot: sold out). No site/X found.
- Note: the routine never surfaced this project at all — it went 82% → sold out
  during Nov 1 without ever appearing in run logs. Genuine discovery miss, though
  the missing project X account would have blocked candidacy anyway.

### PIXEL CAT CLUB (PCAT) — watchlist-only
- Contract 0x9b9e0a4358449eebf4437877a9b36e26c24ce703, site CLAIMED by a Boltbook
  recheck as https://pixelcat.pages.dev/ (not verified by me against the site).
- Reads: 11:56 WIB (Boltbook recheck): 1128/10000, mintOpen true, free 2 per wallet.
  ~19:45 WIB (this sweep): totalSupply 1518, freeMinted 1518, MAX_SUPPLY 10000,
  mintOpen true, balanceOf(user) 0. FREE_SUPPLY / freeClaimed / quote / freeLeft
  all REVERT (views absent) → no free cap → % leg UNVERIFIED; user quote unverified.
- Launch: "listed this morning inside a six-project overnight batch post" →
  no project-stated launch time → UNVERIFIED. X account: none found.

### Wise Owl Society (OWLS) — watchlist-only (permit-gated)
- Contract 0x1cf9e60218493149ace7dc953497c07175aa625e, Sourcify exact_match
  (verifiedAt 2026-10-31T13:17:51Z — suggestive, NOT launch time).
- Reads (~19:55 WIB): totalSupply 2535 (1958 at ~15:30 WIB, 2311 at block 131026157),
  MAX_SUPPLY 10000, paused false, MINT_PRICE 0.002 BNB, PAID_MINT_PRICE 0.0028 BNB,
  priceFor(user) 0, mintsRemaining(user) 8, mintedCount(user) 0, isAgent(user) true,
  balanceOf(user) 0.
- Catch: mint(bytes32 xPostHash, uint256 deadline, bytes signature) — the free
  path needs a SIGNED PERMIT (tied to an X post hash), so priceFor 0 alone does NOT
  verify a plain free mint for the user. No free-cap view → % UNVERIFIED.
  Age UNVERIFIED (strict). Site/X: none found.

### HIVE Agents (HIVEA) — TOP WATCHLIST ITEM (5/7 legs verified; NOT a candidate)
- Contract 0x1458b0C132Fb51BDC65B1Ca7a3BE484BCd9A2f77, Sourcify "match"
  (verifiedAt 2026-11-01T08:24:59Z = 15:24 WIB). DIFFERENT project from the Hive
  pollen launch (Mint 0x3E9B...) — do not conflate.
- Verified launch: START_TIME() = 1793523600 = 2026-11-01 16:00 WIB (contract's own
  configured start; ~4h old at read time) → age leg PASSES (verified ≤48h).
- Free quota: FREE_SUPPLY 1000, FREE_PER_WALLET 1, totalSupply 562, totalPaid 0
  → with ZERO paid mints, all 562 mints are free → 562/1000 = 56.2% → PASSES ≥50%.
  freeMintedBy(user) 0, quote(1) 0, currentPrice 0 → user free slot OPEN.
  Trajectory: 8 (17:20 WIB post, "just started") → 527 (~19:05, Boltbook comment
  recheck at block 131043331) → 562 (~20:00, this sweep).
- Failing/unverified legs: (4) project X account NOT FOUND; X discussion NOT
  VERIFIED — the one twitterapi.io search for "HIVE Agents BSC" returned only the
  DIFFERENT Hive pollen project (@hive_agentic, Mint 0x3E9B...), no discussion of
  this NFT; (7) velocity UNVERIFIED (single own read; external reads show SLOWING:
  ~4.9/min then ~0.6/min, not increasing). Site: none found (hiveagents.dev is an
  unrelated AI-agency business; hive-agentic.site belongs to the other Hive project).
- Verdict: watchlist-only under the strict 7-leg rule. Closest actionable lead:
  ~438 free seats left at ~20:00 WIB, slowing. Note for parent: a user-named
  instruction would exempt the X + age legs per standing rules — that decision
  is the parent's/user's, not this sweep's.

## 3. Upcoming / out-of-scope notes (not candidates)
- ShibAgent (SAGENT): Boltbook front page — mint NOT started yet (free 1 share per
  Agent ID, 4444 free shares, then paid) → upcoming only; also a token-share mint,
  not an NFT.
- ONLYAI Crystals: opens 2026-11-06 18:00 UTC, first mint free → upcoming only.
- CharMasks: trio post mentions claimFree still reverting with start 20:00 WIB —
  NOT investigated in this sweep (CharMasks #1529 previously recorded
  non-transferable); needs its own check, not a candidate here.
- SCOUT mention (Boltbook): "supply around 1,400 out of 5,000", no contract/site/
  launch → unactionable, recorded only.
- Token-share leads (NOT NFTs, noted only): "币安大牛" Daniu sale
  0x3fe6a6a2f00cd7def01c67c41f1e290206e5622e (529/2222 free shares at post time);
  JAGENTREN 0x316dbf6761c57053bc477c9e90c7920e0b87e13d (1 free share, locked to
  listing); MOCHI (577 free shares left at post time). None pursued as NFT leads.
- Dream Circuit (from b/alpha "5 mints open" post): contract not recovered — unpursued.

## 4. Which discovery source actually worked
- WORKED — Boltbook front page + author pages (ranjha.ai, wave posts, Alphapedia
  scan post, b/alpha board): every single find above. The routine's prior sweeps
  only sampled Boltbook via search snippets and never read author pages/front page
  systematically — that is the gap.
- EMPTY — Binance Agentic Hub page (https://web3.binance.com/en/agentic-hub?chain=bsc):
  skills marketing only, no project listings.
- EMPTY for launches — agents.net (directory only; Fluffies already known/excluded)
  and agentstreet.trade (hire marketplace for ERC-8004 agents, not mint launches).
- WEAK — generic web search: resurfaced old/known material + the PCAT site claim;
  no new contract that Boltbook had not already shown.
- X (twitterapi.io): 1 search used (budget ≤10; credits nearly exhausted, so no
  further X spend). Result: only the unrelated Hive pollen project — zero discussion
  evidence for any new NFT lead. X cannot fix discovery for factory lanes that have
  no X account at all.

## 5. What could NOT be verified / safety notes
- Two web-search results in this sweep failed a safety check and were NOT used at
  all (one Night Shift search, one Lumen Wraiths X search). No verdict depends on
  them: Night Shift's full contract was recovered independently from a clean
  Boltbook author page, and LMWR is sold out regardless of X.
- KENRAI / trio / PCAT / Wise Owl launch times remain UNVERIFIED (strict rule) —
  first-Boltbook-evidence dates are suggestive only and are not presented as launch.
- AGENT NFT's start is derived (end − 48h window), not directly read.
- HIVE Agents' 56.2% uses totalSupply + totalPaid=0 as the free counter because the
  contract has no freeClaimed view; the inference is stated, not hidden.
- Velocity leg: only HIVE Agents has multi-point data, and it shows slowing, not
  increasing. No project gets a velocity PASS from this sweep.
