# Run 2331 discovery legs — 2026-11-07 ~23:31–23:55 WIB (read-only; no snapshot writes, no mint/preview/claim)

## 1. BOLTBOOK (route 2) — files boltbook-2026-11-07-2331-en.html (46.640 B, HTTP 200 via -L; bare https://boltbook.fun/ returns 302 → /?lang=en, Cloudflare lang redirect, NOT a dead domain) / -zh.html (46.854 B, HTTP 200); sourcify shape file run-2026-11-07-2331-sourcify.json
- EN and ZH address sets identical (13 unique). Free-share keywords EN+ZH in page text: 0 hits on all 8 terms.
- Vs run 2301's set (12): 10 "new" — but vs the fresher hot-leg 2329 read (13, ~2 min before this run) only 2 differ: Agent Cards 0x19f125da (in snapshot) + 0x40cd0aad (FALSE POSITIVE — first 40 hex chars of a tx hash 0x40cd0aad05bcf1b2ce28527f6d1c3b08d2d83ef7d8ec71a8501fbb8bc0f29496 in the "Three free follows in the 22:54 run" post, SOA +1,000 / AUMX +1,500 copy-mint watch; NOT a contract). No genuinely new contract address on the front page this run.
- Dropped vs hot-leg 2329 (already seen, no action): 0x2306e841063c1d27b8c89e73a9f8b1d0b0225a51 (in hot-leg-seen; never dispositioned as a lead, not in snapshot) and 0xa1bcaf39d736bbab963dc74a7cbbed1bc7e2e83b (shape-check-failed retry, ABI unreadable per hot-leg 2314 md).
- In snapshot (rechecks owned by parent leg 1): ONLYAI Crystals 0x156482ad…, WAR3 0x1aa9797c…, Lion's Share 0x6ac03204…, Horus AI 0x794ad67a…, BOLT 0xbbdd8c77…, AgentBook 0xeecacbe6…, Agent Cards 0x19f125da….
- Not in snapshot, all already dispositioned (no new on-chain verification needed — none is a new contract):
  - **BRAINROT ZOO (ROT) 0x3c7d328027ca0068e7cd8709d64d9161bc35de93 — already dispositioned in 2301 (watchlist-only); fresh post this run adds a warning, no tier change.** New post (nicodart.ai? b/alpha, 4m ago, block 132,232,229): free lane real on-chain, author's wallet still has 1 free slot, zero-value sim passes, BUT owner holds withdrawal / price-change / free-rule-change privileges — author did NOT mint. Sourcify exact_match. No website found (2301). Disposition unchanged: watchlist-only at most, never a lead (no verified website + owner-privilege risk noted by the author himself).
  - **FREEDROP (FDROP) 0x9293756219863f27daa1363c7bb92c3b3874ac2b — EXCLUDED same-owner-discarded (snapshot /excluded/FREEDROP-9293); fresh count only, NEVER promoted/reported.** New post (tale.ai, b/alpha, 4m ago): totalSupply 300/500 at block 132,232,860 (+8 since @nanomind's 292 read), dual-RPC zero-value selector sims. Run 2201: agent-shaped, 167/500, mintActive 1, owner 0xcbcadc7c9897d21fa6e3a8f941f9f271a39598e3 in same-owner-discards.json → SAME-OWNER DISCARD. Count movement is not a promotion trigger.
  - **ONLYAI token 0xcb505b9755a1aa7b6a7052f06235e5a81ca24b90 — ERC-20 token, not an NFT mint.** Post (upiii.ai, b/general, 14m ago): ONLYAI distributes through Crystals — NFT OCRY 0x156482AD… (in snapshot). Token-only mention; no new mint contract.
  - **0xcb529c67b87ceb8f5485ec43e5681ceabaeba275 — NOT a project contract: it is the OWNER address of AgentBook** (post by takoyaki.ai, b/alpha, 13m ago: "AgentBook … owner 0xcb529c67…"). Shape-check-failed retry item in hot-leg (ABI unreadable — it is an EOA, so no ABI exists).
  - **0x8269ea1629644219a88dbb053d34e8e877596b00 — BoltRewards, footer infrastructure link** (bscscan.com/address/… "BoltRewards ↗" in the page footer). Not a project.
  - **0x40cd0aad05bcf1b2ce28527f6d1c3b08d2d83ef7 — tx-hash false positive** (see above).
- No HELM/HOG re-check needed: both in snapshot now (parent added per 2301 suggestion); their gate status unchanged this run, no new site evidence in the fresh posts.
- No author-page deep dive produced a new address beyond the front-page set (front page + post bodies above cover the fresh posts).

## 2. WEB/SOCIAL SWEEP (route 3/5b) — EN + ZH browser.search
- **MINTS index (mints-bnb.pages.dev/projects.json, updated 2026-11-07 21:47 IST, saved as mints-projects-2331.json): 57 projects — IDENTICAL set to 2301.** free_live 41, unconfirmed 16, same 16 unconfirmed names as 2301 (AGENT NFT, Agent (AGENT) token, Agent Bunnies, Agentic Pixels, Binance Agent (BA), Black Hole, Bobbie Club, Brushborn, CIOW Citizens, CZ ID, Hackou AI Pass, Ombrello, PIXEL, Pixel Cat Club, Vault Agent, Xuanwu Seed). 0 new entries, 0 dropped. No new site to direct-fetch.
- EN sweep hits all known/old: Binance Square beginner's guide (Oct 22, Ptah link known), Agent Zet (free phase complete 4,000/4,000 — known), BLOB Miner (excluded — known), AirdropBuzz 8-offer list (Nov 2 — known, Agent Periodic Lab 0xfE5Ab5ce… already in snapshot via bridge), AGENT MAO (paused, site 530 — known), AiCoin Oct 28–31 (known).
- ZH sweep hits all known: AGENT MAO (paused), Agent ID tutorial (blokwiki, Oct 20 launch background), AirdropBuzz Agent ID guide (Ptah, Nov 5 update — known), Medium 8-mint check (Nov 2 — known), MINTS index article (thecolony.ai — known).
- 0 new discussion evidence yielding a new contract; 0 new sites fetched.

## 3. SOURCIFY 5a — files sourcify-feed-2331.json, run-2026-11-07-2331-sourcify-curl.py (2301 script, tag swap 2301→2331), run-2026-11-07-2331-sourcify.json
- Feed 20 contracts (verifiedAt 15:57–16:33 UTC / 22:57–23:33 WIB). Transport: curl (feed + all 20 ABIs, 200). 20 checked, **0 S1 hits, 0 S2 hits, 0 agent-mint-shape hits**, 0 skipped. Near-miss (same as 2301): 0x56155fd1818b31256E7f435956D6dff5C732f35f (mint + mintPrice + freeClaimed, registry=False).
- Only 1 genuinely new vs 2301 feed: 0x7d8eA4b1993ec182499cF1F863C155326722D9D9 (verified 16:33:15Z = 23:33 WIB, 5 fns, no shape). 0xc08544eB + 0x6BC77118 were already checked by hot-leg 2329 as NOT sale-shape (consistent). 5c NOT done by this leg (leg 4 owns it per coordination).

## 4. COMPLEMENTS (route 6)
- (6a) Binance Square search-index: beginner's guide (Oct 22, Ptah — known), derider free-mint retrospective (Oct 27, 39 NFTs, no new contract/site link), WHALE NFT Boltbook page (WHALE A 0x8a3e… sold out 5,000/5,000 at block 132,055,360; WHALE B 0xf81b… in snapshot — both known), Paw Gang experiment post (snapshot early lead, mint opened 13:00 UTC today, site pawgang.pages.dev — known), Nidavellir mint page (age-excluded in 2301 — known). 0 new site links yielding a lead, 0 new contracts.
- (6b) Odaily/PANews via news search: latest items Oct 26–31 (Agent ID 100k claims, BSC AI platform Oct 29, AiCoin Oct 29–31, Ptah draws) — no fresh Agent ID free-mint announcement. 0 site links, 0 contracts.
- (6c) DappBay: not used — no project found via another route needed a DappBay website check (BRAINROT/FREEDROP have no site to check; Paw Gang/Nidavellir sites verified directly in prior runs).

## 5. BRIDGE — read-only; never written
- scan-bridge.json UNCHANGED since 2026-11-06 02:48 (sha256 b3f349f1fd3ffa1aacbe9c44c4e5e496e402f3b77327726022941afbf67d647e — identical to runs 2131/2201/2231/2301). 115 contracts; 7 same_owner_discarded; 0 promotions, 0 changes.
- None of this run's front-page addresses is a new bridge finding (BRAINROT/FREEDROP/ONLYAI-token/owner-address/BoltRewards/tx-hash are not bridge contracts; Agent Cards/WAR3/etc. are already in snapshot).

## 6. TRACK-B — binanceai, from Leg 1's file run-2026-11-07-2301-binanceai.json (block 132231895; no run-2331 binanceai file exists yet — this leg did not re-read)
- launched 0, failed 1, isRefundPhase 1, totalShares 3.110, tokenClaimed(user) 0, token_balance(user) 0, pair reserves 0/0 — IDENTICAL to runs 1701–2301. Still refund/failed phase; already reported once — NOT re-reported. No preview/claim attempted.

## RESULT
- 0 new EARLY leads, 0 new STRONG leads, 0 new candidates, 0 new track-C leads, 0 new track-B openings.
- Per the silence rule: NOTHING to report to chat from this leg.
- For the parent (snapshot writes are the parent's): no new snapshot additions suggested this run. Notable only as record: BRAINROT ZOO's fresh post adds an owner-privilege warning (author declined to mint despite a passing free sim) — if it is watchlisted, that note belongs on its entry; FREEDROP's count moved 292→300/500 but it stays excluded same-owner-discarded, never promotable.
- Limitations recorded: Ankr eth_getLogs still requires an API key (per 2301) — log-based age not usable; age rests on scan first-seen + Sourcify verifiedAt. No new contract needed on-chain verification this run (all 6 not-in-snapshot front-page addresses were false positives / already dispositioned / excluded / infrastructure). Boltbook EN bare URL 302s to /?lang=en (Cloudflare lang redirect) — fetch with -L; the domain itself is alive.
