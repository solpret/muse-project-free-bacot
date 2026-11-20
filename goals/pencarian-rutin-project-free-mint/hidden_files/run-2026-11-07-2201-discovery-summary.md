# Run 2201 discovery legs — 2026-11-07 ~22:01–22:22 WIB (read-only; no snapshot writes, no mint/preview/claim)

## 1. HOT-LEG 2149 FOLLOW-UP (priority) — files run-2026-11-07-2201-hotleg-verify.json / -hotleg-abi.json
Both contracts were NOT in the snapshot and NOT in hot-leg-reported.json (checked first).

### 0xa46D33862124Da90385cEb58acba63718729DEe0 — NOT a lead (0 mints; watchlist-only)
- S1 shape confirmed by hot-leg 2149 (mint + quote + freeMinted + agent ref). Sourcify exact_match, verifiedAt 2026-11-07T14:48:15Z (21:48 WIB).
- Fresh read block 132222086: totalSupply 0, totalMinted 0, MAX_SUPPLY 100, FREE_CAP 50, FREE_PER_WALLET 1, freeMintedTotal 0, mintActive 1, agentRegistry = registry 0x60B9…022F, owner shared with 0x9293… (see below). User slot open (freeMinted(user) 0, mintedCount(user) 0, balanceOf(user) 0; quote tier-free 0 per hot-leg targeted read 21:5x).
- name()/symbol()/contractURI()/tokenURI(1) all return null (revert) — no project name known on-chain.
- NOT an early lead: there are NO mints yet, so no first mints to verify. Age UNVERIFIED, free% 0%.
- MANDATORY WEBSITE GATE FAILED (methods tried): (A) raw contract-address search — no relevant hit; (B) not on Boltbook front page (came from Sourcify feed); (C) Sourcify v2 summary response carries no URLs/metadata; (D)/(G) no project name known, no same-family pattern to test; (H) contractURI null; (I) tokenURI null; (J) ABI fetch failed this run (Sourcify IncompleteRead/timeout — transport degraded tonight); (E) deployer group: same owner as 0x9293… (rarity-mint contract below), no links in metadata. X account: none found — optional, never gates. Gate failure is moot for now (0 mints, not a lead) but recorded so a later promotion re-checks it.
- Disposition: watchlist-only. Parent to add to snapshot watchlist for tracking (this leg is read-only and cannot write the snapshot).

### 0x2df7435f5bce0577bee213e13da68313c74d7d0b (Agentdragon, AGENTDRAGON) — SOLD OUT, NOT a lead
- S1 shape confirmed by hot-leg 2149 (mint + quote + freeClaimed/freeFor/freeLeft/freeUsed + agent ref). Sourcify exact_match, verifiedAt 2026-11-03T13:39:31Z.
- Fresh read block 132222086: totalSupply 2000 = MAX_SUPPLY 2000, FREE_SUPPLY 2000, freeClaimed 1994, mintOpen 1 (moot — no supply left), PRICE 0.00007 BNB (paid lane). Boltbook front page: "free lane closed — 2,000/2,000, verified on 2 RPCs". User slot per hot-leg targeted read 21:5x (freeLeft 2, freeUsed 0, mintedBy 0, quote 0, balanceOf 0) is irrelevant — totalSupply is at cap, nothing can mint.
- Age UNVERIFIED via getLogs (first-mint scan hit the script deadline; not pursued further — sold-out disposition does not need age).
- Gate FAILED (no verified website: A no hits, B Boltbook post carries contract + discussion only, G name search no site) — moot, sold out.
- Disposition: sold out; recorded, NOT chat-reported (never reported as a lead before, so there is no change to report).

### 0x9293756219863F27Daa1363C7BB92C3b3874Ac2b — agent-shaped, NOT an early lead (first mints unverified)
- Found by the Sourcify 2201 retry pass (see §4): ABI has mint + freeMinted + agentRegistry + rarity tiers (rarity_common/uncommon/rare/epic/legendary, rarityOf/rarityName), agent_mint_shape TRUE, S1/S2 FALSE (no quote function). Sourcify verifiedAt 2026-11-07T14:40:26Z. NOT in snapshot, NOT in scan-seen.
- Fresh read block 132223565: totalSupply = totalMinted = 167/500, mintActive 1, agentRegistry verified, owner = SAME owner as 0xa46d… (sibling contracts, same deployer group). name()/symbol()/contractURI()/baseURI() null. freeMinted()/freeClaimed() no-arg and FREE_SUPPLY() return null → free-quota % UNVERIFIED (167/500 = 33,4% of MAX_SUPPLY only, not a free %). User slot: mintedCount(user) 0, balanceOf(user) 0; free price unverifiable (no quote function).
- First-mint check: Transfer(from=0) getLogs NOT found in the last 10.000 blocks (~75 min, 10 chunks of 1000) → first mints NOT verified on-chain in this run → NOT an early lead per the rule (first mints must be verified in-run). Age UNVERIFIED (no MINT_START/startTime views). Limitation: deeper back-scan to the deployment block was not done this run (unbounded chunk walk); parent/main job may run it.
- Disposition: watchlist-only. Parent to add to snapshot watchlist for tracking.

## 2. BOLTBOOK (route 2) — files boltbook-2026-11-07-2201-en.html (45.911 B, HTTP 200 via ?lang=en; bare / returned 302, 0 B) / -zh.html (46.122 B, HTTP 200); verify file run-2026-11-07-2201-boltbook-verify.json
- EN and ZH address sets IDENTICAL (7 addresses), 0 new project addresses.
- In snapshot: Thetavox 0x37d39f…, Horus AI 0x794ad6…, BOLT 0xbbdd8c… (rechecks owned by parent leg 1).
- Not in snapshot, dispositioned: 0x8269ea16… = BoltRewards footer link (infrastructure); 0x95578773… = SanDisk Corp (SNDK) four.meme memecoin, 45-byte EIP-1167 proxy, LP burned (out of scope); 0x9a88a8b8… = a TX HASH in the AMBER day-3 post, not a contract; 0xc9747b35… = Nomio (NOMIO) — PAID-ONLY: mint() 0.00027 BNB, "No free lane: mint() at value 0 reverts for every wallet" (Boltbook dual-RPC post); hot-leg 2149 shape S1/S2 false. NOT a lead.
- Front-page posts noted (no new contract): "Top 3 free lanes: DinoAgent closes ~01:20 WIB, Tri333 +371, Ink Koi cooling" (all three already in snapshot); Thetavox #944 free mint; Paw Gang operator guide (328/3.333); Horus recheck 1.885/2.000 free; ORBITA pace check #4 (676 sold); WAR3 +224/36 min, agent slots 2.079/3.000, mintEnd 12 Nov; "Horus: Agentdragon just proved it".

## 3. WEB/SOCIAL SWEEP (route 3/5b) — EN + ZH browser.search
- 0 new projects. All hits known/old/excluded:
  - **Agent Zet 0xFF8BfeF2c0d16BDa6E8667812bCa35Ecb42A1a37 — PAID-ONLY, excluded.** Site (agentzet.vercel.app) states free phase complete 4.000/4.000, 0 free slots remaining; verified on-chain block 132222635: totalSupply 4.124 = site's 4.124/4.444, MAX_SUPPLY 4.444, balanceOf(user) 0. File run-2026-11-07-2201-agentzet.json.
  - **Coracle Agents 0x2FCefA216dA37751E102399aCbe1dCC86Dc96eCf — SOLD OUT + PAID-ONLY for user, excluded.** NEW name from search; site coracle-agents.pages.dev verified (prints exact NFT contract + market 0x598f… + owner; /skill.md, /launch.json, /llms.txt, /api/* all return the same SPA index). On-chain block 132222635: totalSupply 10.000 = MAX_SUPPLY 10.000 (SOLD OUT), mintOpen 1, mintPrice 0.0005 BNB, mintedByWallet(user) 2 (both free mints already used), quote(user,1) 0.0005 BNB, balanceOf(user) 0, hasAgentId(user) 1. Site counters were blank (JS) — on-chain read settles it. File run-2026-11-07-2201-coracle.json.
  - **Piggy Agent 0x70385fa94577cb845983d9b6752f2dde2486c837 — SOLD OUT + PAID-ONLY + age >48h, excluded.** NEW name from search; site piggyagent.space prints the exact contract + X @piggyagentnft. On-chain block 132223419: totalSupply 10.000 = MAX_SUPPLY 10.000 (SOLD OUT; site text "No Piggy minted yet" is stale), FREE_SUPPLY 1.000 exhausted with supply, mintedBy(user) 1, quote(user) 0.00067 BNB, balanceOf(user) 0. Sourcify exact_match verifiedAt 2026-10-24T15:48:09Z (age >48h anyway). File run-2026-11-07-2201-piggy.json.
  - Nidavellir 0xd527… — excluded, free window closed (run 2101). AGENT MAO — known/paused (site 530). AgentForge 0xf11e… (Square, 27 Oct) and Pixel Fox 0x9134… (25 Oct) — old, >48h. Teapawt 26 Oct list (Subsonic Tribe etc.) — old. Agent Periodic Lab 0xfE5A… — bridge contract, known. Ptah — known, soulbound. AgentID AGI — Ethereum ERC-20, out of scope (BSC only).
  - **TRACE (tracea.cc) — website verified, contract NOT established, not a lead.** Site + skill.md (tracea.cc/agent/skill.md) read; neither prints a contract address (skill directs a CLI tarball with a bundled manifest — NOT downloaded/installed, per read-only scope). Cannot verify on-chain → upcoming/unverified, not a lead.

## 4. SOURCIFY 5a — files sourcify-feed-2201.json, run-2026-11-07-2201-sourcify.py/.json, run-2026-11-07-2201-sourcify-retry.json
- Feed 20 contracts (verifiedAt 14:31–15:04 UTC / 21:31–22:04 WIB): 20 checked, 0 S1/S2 hits, 0 skipped. 8 readable ABIs all no-shape; 12 abi-unavailable (Sourcify transport degraded tonight: IncompleteRead / RemoteDisconnected / timeout — same pattern as run 2131).
- Retry pass (same ?fields=abi endpoint, 2 tries): 5 of 12 ABIs recovered, 7 still unavailable. 1 agent_mint_shape hit: 0x92937562… (handled in §1 — not an early lead). No other near-miss with partial shape. Additions listed in the output files; NOT appended to track-c-scan-checked.json (parent owns that file).
- 5c NOT done by this leg (leg 4 owns it per coordination).

## 5. COMPLEMENTS (route 6)
- (6a) Binance Square search-index: hits are the Oct 22 guide (Ptah), AirdropBuzz Nov 2 (Agent Periodic Lab — known), derider Oct 27 post (general), AiCoin Oct 29 experiment, WHALE NFT Boltbook alphapedia — WHALE A 0x8a3e… SOLD OUT 5.000/5.000 on 2026-11-07 ~03:10 WIB (not in snapshot — recorded sold-out, not a lead); WHALE B 0xf81b… in snapshot as WHALE-B. 0 new site links, 0 new contracts.
- (6b) Odaily newsflash (crawled 15:11 UTC): latest items all macro/BTC/ETH/Pearl — no Agent ID announcement. PANews homepage (15:21 UTC): CFTC/stock-perpetuals, market plunge — no Agent ID free-mint item. 0 site links, 0 contracts.
- (6c) DappBay: not used — no project found via another route needed a DappBay website check (a46d/2df7 gate outcomes are already settled by sold-out/0-mint status + the other methods).

## 6. BRIDGE — file run-2026-11-07-2201-bridge.json (read-only; never written)
- scan-bridge.json UNCHANGED since 2026-11-06 02:48 (sha256 b3f349f1fd3ffa1aacbe9c44c4e5e496e402f3b77327726022941afbf67d647e — identical to run 2131). 115 contracts; 82 in snapshot, 33 not in snapshot — same seeded Nov 3–6 findings already reported via scan, none new. 0 promotions, 0 changes. 7 same_owner_discarded — never promoted/reported as leads. None of the new addresses in this run (a46d, 2df7, 9293, Coracle, Piggy, Agent Zet, Nomio) is in the bridge.

## 7. TRACK-B — binanceai re-check (block 132222635), file run-2026-11-07-2201-binanceai.json
- launched() 0, failed() 1, isRefundPhase() 1, totalShares() 3.110, tokenClaimed(user) 0, tokenBalance(user) 0, pair reserves 0/0 — IDENTICAL to runs 1701–2131. Still refund/failed phase; already reported once — NOT re-reported. (totalSupply() reverts on the MINT contract — expected, not a state change.) No preview/claim attempted.

## 8. PAW GANG / AGENTBOOK — no change check by this leg
- Re-reads of snapshot items are owned by parent leg 1; this leg performed no re-read of Paw Gang 0x587C… or AgentBook and reports no change to either.

## RESULT
- 0 new EARLY leads, 0 new STRONG leads, 0 new candidates, 0 new track-C leads, 0 track-B openings.
- Per the silence rule: NOTHING to report to chat from this leg.
- For the parent (snapshot writes are the parent's): consider adding to the snapshot watchlist — 0xa46D… (0-mint S1, gate failed, sibling of 0x9293…), 0x92937562… (agent-shaped, 167/500, age + free% unverified, first-mint block not located in last 10.000 blocks) — and recording as excluded (sold out / paid-only): Agentdragon 0x2df7…, Coracle 0x2FCe…, Piggy 0x7038…, Agent Zet 0xFF8B…, Nomio 0xC974…, WHALE A 0x8a3e….
- Limitations recorded: Sourcify ABI transport degraded (12/20 feed ABIs unavailable first pass; 7 still unavailable after retry — shape coverage incomplete for this feed window); 0x9293… first-mint block not located within the last 10.000 blocks (deeper back-scan not run); TRACE contract address not established from public pages (CLI manifest not downloaded).
