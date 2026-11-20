# HOG ORBIT — gate evaluation, run 0031 (Sun 2026-11-08 ~00:31–00:55 WIB)

Contract: 0x7bc0b487febcbb1caa781148bf05a8cd72d02ec5 (HOG ORBIT, HOG, ERC721, MAX_SUPPLY 1500)
Source of flag: hot-leg 0024 — freeLeft 1126→1093, used 407/1500 = 27.1%, crossed the 25% strong-lead threshold.
This leg did NOT preview or mint. Parent decides/executes.

## 1. Fresh on-chain re-read (single-call, block 132243968)
- totalSupply 418 (reread LEAN row: 417; run 0001: 398, +19–20 this run)
- freeLeft 1086 → free used = 1500 − 1086 = 414 → **27.6% of free quota** (≥25% ✓). Note: 418 − 414 = 4 paid mints so far (price 0.0002 BNB); at run 2301 paid = 0.
- MAX_SUPPLY 1500, mintOpen 1, price 200000000000000 wei = 0.0002 BNB, bogo 0
- User slot: freeOf(user,1) = 1, costOf(user,1) = 0, mintedBy(user) = 0, mintsLeft(user) = 10, balanceOf(user) = 0 → **slot OPEN** ✓
- owner = treasury = 0x11038f4aa771d9d48b8ac7a184e37a8e5324a9dd (deployer group 0x1103, same as HELM/GACHA/OMENS)
- agentIds() = 0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F (exact Agent ID registry) ✓
- FREE_SUPPLY() / totalMinted() revert (no such views — expected, not a state change)
- tokenURI(1) = **https://hog-orbit.pages.dev/meta/1.json** — CHANGED vs run 2301 (which recorded "/1.json"). Owner setBaseURI power exists; base URI now points at the project site.
- Velocity this run: +19, rate 0.4101/min, ratio 0.32 vs prev 1.2817 → velocity FAILS (pace cooled). Velocity is NOT a strong-lead leg; recorded only.

## 2. Launch age — VERIFIED ≤48h
- First mint block 132198351 = 2026-11-07 19:10:57 WIB (scan/backfill-observed first mint, 1901 scan + backfill-132197166-132199165; corroborated by Sourcify verifiedAt 2026-11-07T12:10:47Z = 19:10:47 WIB).
- Age at this run ≈ 5h40m ≤ 48h ✓
- Caveats: no project-stated launch timestamp found (Boltbook post gives no launch time; site says "Mint opens soon" in one label while mint is open on-chain — cosmetic inconsistency). First-mint Transfer event via chunked eth_getLogs could NOT be re-run this run: bsc-dataseed + dataseed1 both return -32005 "limit exceeded" even for 100-block windows; Ankr eth_getLogs requires an API key per run 0001. Age rests on the scan-observed first-mint block + Sourcify verifiedAt (both ~19:10 WIB Nov 7), which agree to the minute.
- First-seen block from scan-seen/onchain-scan-seen.json is a lower bound, NOT launch time — not used as launch time here.

## 3. MANDATORY WEBSITE GATE — VERIFIED (changed vs run 2301)
- Site: https://hog-orbit.pages.dev/ — HTTP 200, 25,581 bytes, fetched this run (saved: hog-orbit-site-0031.html).
- Footer prints the EXACT contract: "Contract: 0x7bc0B487feBCBB1caA781148bf05A8Cd72D02Ec5 on BscScan" (checksummed, matches on-chain address).
- JS config on the same page: CFG = {"name": "HOG ORBIT", "address": "0x7bc0B487feBCBB1caA781148bf05A8Cd72D02Ec5", "supply": 1500, ...}.
- Visible copy: "HOG ORBIT — 1,500 pig astronauts drifting through the BNB galaxy", "1,500 supply", "0.0002 BNB", "First mint FREE", "10 per wallet", "Binance Agent ID ready", "Your first NFT is free. Every one after that is 0.0002 BNB. Up to 10 per wallet", "Got a Binance Agent ID? Use the Agent ID tab, or paste the prompt into your Binance AI wallet (max 10 per Agent ID)."
- Method (I) tokenURI: /meta/1.json (HTTP 200, 578B; saved: hog-orbit-meta-1-0031.json) — name "HOG ORBIT #1", external_url "https://hog-orbit.pages.dev" — corroborates the same site.
- /skill.md, /launch.json, /llms.txt: all return the same 25,581B index page (SPA fallback) — those docs do not exist as separate files.
- No X link on the site; no project X account found anywhere (X is optional, never a blocker).

### Methods (A)–(N) — all attempted this run
- (A) raw contract-address search: no hits.
- (B) Boltbook post RcFhqL1Ue2-q (lloyd.ai, 22:49 WIB Nov 7, re-read from 2301 file): links only Boltbook-internal pages + bscscan 0x8269… + gang.fun (unrelated) + x.com/bolt_book (Boltbook's own X). No project site/X in the post. Post text: "HOG launched with no Agent-ID gate… there is no secondary market yet".
- (C) Sourcify metadata: v2 contract endpoint returns match data only (exact_match, verifiedAt 2026-11-07T12:10:47Z), no URLs in payload; files/tree endpoint path invalid (error page). Full ABI on file locally has no URLs.
- (D) same-family patterns: HELM helm.ai = unrelated autonomous-driving company (fetched HTTP 200, run 2301); GACHA/OMENS addresses never printed; no sibling site. The HOG site itself is the .pages.dev family pattern.
- (E) owner()/deployer-group: 0x11038f4aa771d9d48b8ac7a184e37a8e5324a9dd — factory wave (same 0x1103 template as HELM/GACHA/OMENS), but a website IS now verified, so the gate passes on the site, not on the group.
- (F) twitterapi.io: DEAD, never called. No handle found anywhere to confirm via browser; X optional.
- (G) project-name search + site: filters (vercel/pages/deed): no hits in search index — the site was found via tokenURI, not search.
- (H) contractURI: function does NOT exist in the ABI → no external_link. N/A.
- (I) tokenURI external_url: https://hog-orbit.pages.dev — CONFIRMED, site prints exact contract (see above).
- (J) ABI site-function grep (58-entry ABI): only setBaseURI + tokenURI match site/URL keywords; no website/siteURL/domain/external function.
- (K) GitHub code search: search-index query no relevant hits (only unrelated ORBIT/HOG homonyms); true code search needs auth — limitation stated.
- (L) BscScan token-info via live browser: NOT attempted — subagents cannot do live browser work. Recorded as unattempted, not as absence. (Not needed: gate already verified via the site itself.)
- (M) site: filters: no hits (see G).
- (N) registry profile + author-bio hop: agentIds() = registry; no project Agent ID profile identifiable; Boltbook author lloyd.ai profile links only Boltbook-internal; no site in bio hop. No linkage — but no longer needed.

## 4. Binance audit (query-token-audit skill, read-only)
- File: run-2026-11-08-0031-hog-audit.json
- code 000000, success true, **hasResult: false**, isSupported true, riskLevel -1, riskLevelEnum LOW, extraInfo null, no riskItems, riskAlert null.
- Disclosure: NO RESULT — never a pass, and no specific risk hit. Parent must weigh the absence of audit coverage.

## 5. Strong-lead legs — ALL THREE ✓ + gate ✓
- (a) verified age ≤48h: YES (~5h40m)
- (b) ≥25% free quota claimed: YES (414/1500 = 27.6%)
- (c) user free slot open: YES (freeOf=1, costOf=0, mintedBy=0, mintOpen=1)
- Website gate: VERIFIED (https://hog-orbit.pages.dev prints exact contract)
- Agent-shaped: YES (agentIds = registry, Sourcify exact_match)

## 6. VERDICT — GO (conditional on parent's execution-time guards)
HOG ORBIT is a **confirmed STRONG LEAD**, eligible for direct mint under the strong-lead direct-mint rule.
Recommendation: **GO** — parent to execute ONLY with fresh execution-time guards: (1) re-read freeLeft + costOf(user,1) fresh at execution (owner powers live: setFree/setMintOpen/setPrice/setTreasury/teamMint can close or change the free pool at any time; freeLeft must still be >0 and quote still 0); (2) clean preview (000000000, value 0, no authority/allowance/risk, simulated balance change = 1 NFT); (3) audit disclosed as NO RESULT (above). No preview or mint was run by this leg.
Risks/disclosures: owner powers live (see above); Binance audit has NO RESULT (not a pass); no project X account (optional); velocity cooled this run (ratio 0.32 — not a strong-lead leg); site label "Mint opens soon" contradicts open on-chain mint (cosmetic); 4 paid mints have occurred (price lane live); no secondary market yet per the Boltbook post.
If the parent executes: report tx + on-chain verification + post-mint marketplace and rarity checks (NFT). If any execution-time guard fails: report once + reason, stop, no paid fallback.
Status change for parent/snapshot: HOG ORBIT status was watchlist-only-website-gate-failed-2026-11-07 → now strong lead (website gate verified this run). Do NOT re-report as a new lead by any other leg (dedupe: this file is the record).
