# Run 2101 discovery legs — 2026-11-07 ~21:01 WIB (read-only; no snapshot writes, no mint/preview)

## 1. BOLTBOOK (route 2) — boltbook.fun EN (?lang=en) + ZH, files boltbook-2026-11-07-2101-en.html (47.394 B) / -zh.html (45.906 B)
- NOTE: bare https://boltbook.fun/ returned 0 bytes twice via curl; ?lang=en works (HTTP 200). Hot-leg 21:04 files had EN readable, so this looks like a transient/empty-body quirk, not a site outage.
- Front-page contract addresses vs snapshot (537 addrs): 2 in snapshot (BOLT 0xBbDd…7777 footer; WAR3 0x1aa9…bbe in snapshot), 8 "new" — ALL dispositioned, none a free-mint lead:
  - 0x2df7435f… — Agentdragon, SOLD OUT 2.000/2.000 (posts crypto19.ai + lloyd.ai) — excluded sold out.
  - 0x6e108326… — $VAULT VaultCrack, Flap memecoin — out of scope (not a free-mint NFT).
  - 0xe0df49c281… — HELM helm.ai, 291/555, price 0.0002 BNB, freeLeft 264, mintOpen true, pace slowing; PAID mint + 0x1103-owner cluster (gate failed + same-owner discarded per run 2001) — not free, not a lead.
  - 0x8269Ea16… — BoltRewards footer link, infrastructure, not a project.
  - 0x9f2cd403… / 0xba56663c… / 0x93870065… — S38 "…ffff" memecoin farm factory/helper/dumper (post 0x1412.ai) — out of scope.
  - 0x89c9cbbd… — a Ripstack claim TX hash, not a contract.
- No new free-mint project post on the front page; other posts are rechecks of known items (HOPKIN, Polar Bear, STRAWBS, WAR3, Thetavox, ONI, HELM). Author pages not opened — no new project named. 0 new leads.

## 2. WEB/SOCIAL SWEEP (route 3/5b) — EN + ZH browser.search
- EN: Binance Square guide (Oct 22), AiCoin experiment (Oct 29), WHALE NFT (contract A 0x8a3e… SOLD OUT 5.000/5.000 at block 132.055.360; WHALE B 0xf81b… already in snapshot as WHALE-B), Nidavellir (NEW — see below), 22-project Substack list (Oct 28, old).
- ZH: Agent ID tutorial (blokwiki), AGENT MAO (known; site 530 paused), Agent Periodic Lab (already in snapshot as bridge-0xfe5a…), Ptah (known, soulbound).
- NEW FIND — NIDAVELLIR ("Gull" NFT), site https://nidavellirbsc.vercel.app/mint.html, contract 0xd527109571b039298b65bCB26313dcbED0978c97:
  - Website VERIFIED: mint page prints the exact contract + registry 0x60B9… + mint/free rules (method G standard met). /skill.md, /launch.json, /api/stats, /api/verify all 404.
  - On-chain (block 132214769): totalSupply 1121 / MAX_SUPPLY 4444 (25,2%, matches site), mintOpen=1, name "Nidavellir Gold", Sourcify NOT verified (404).
  - FREE SLOT CLOSED for user: freeWindowOpen()=0, freeRemaining(user 0xeb23…)=0, remainingFor(user)=5 (paid only, 0,001 BNB each). Free quota valid only within first 1.000 slots; supply already 1.121 — window closed. NOT a lead/candidate; do not report as one.
  - Launch time UNVERIFIED: first-mint getLogs probe over last 400k blocks in 20k chunks FAILED on every chunk — all public RPC endpoints returned OSError/Timeout (see proc_601d043c2533 output) — inconclusive, not proof of age; 0 mints in last 1.000 blocks (head 132215752, single 1k-block call OK). Moot for candidacy (no free slot), but age stays unverified.
  - Files: run-2026-11-07-2101-nidavellir-mint.html, run-2026-11-07-2101-nidavellir-verify.py, run-2026-11-07-2101-nidavellir-binanceai.json, run-2026-11-07-2101-nidavellir-free.py, run-2026-11-07-2101-nidavellir-free.json. FREE_SUPPLY_LIMIT()/PRICE() reads returned null (function names from site docs did not resolve on-chain) — not decisive.

## 3. SOURCIFY 5a — run-2026-11-07-2101-sourcify.py (copied from 2001, sed 2001→2101)
- Feed 20 contracts (verifiedAt 13:20–14:01 UTC): 20 checked, 0 hits (S1/S2), 0 skipped. 11 abi-unavailable, 9 no-shape (mint=[] free=[] reg=False). Additions listed in run-2026-11-07-2101-sourcify.json (NOT appended to track-c-scan-checked.json — state files not written by this leg). No on-chain verification needed (no pass).

## 4. COMPLEMENTS (route 6)
- (6a) Binance Square search-index (#AgentID #bnbchain + free-mint): hits Ptah (known), Square guide, Typefully, AGENT MAO (known/paused), thecolony.ai MINTS index (mints-bnb.pages.dev/projects.json, updated 2026-11-07 17:46 IST). MINTS diff vs snapshot: 39 "not in snapshot" — ALL added 2026-10-29–11-06, none added today; includes excluded Worldygg / Laser Agents / PIXEL and bridge finding M3MO. 0 new launches; not reported as leads.
- (6b) Odaily newsflash (crawled <1 min ago): latest ~14 items all macro/BTC/ETH — no Agent ID free-mint announcement. PANews homepage: no Agent ID free-mint item. 0 site links, 0 contracts.
- (6c) DappBay: not used — no project found via another route needed a DappBay website check (Nidavellir site already verified directly).

## 5. BRIDGE — scan-bridge.json (read-only), file run-2026-11-07-2101-bridge.json
- File UNCHANGED since 2026-11-06 02:48 (identical to run 2001 input). 115 contracts; address-level: 82 already in snapshot, 33 not in snapshot — all 33 are seeded Nov 3–6 findings already reported via scan, none new this run. 0 promotions. 7 same_owner_discarded (Cryptlichor, Owlagent, Rimeagent, Octagent, Astragent, Pandadroid, Krillfarm) — never promoted/reported as leads. (Run 2001 reported in_snapshot=1 because its script compared snapshot keys/names, not addresses; operative fact — file unchanged, no new contracts — is the same.)

## 6. TRACK-B — binanceai re-check (block 132214769)
- launched()=0, failed()=1, isRefundPhase()=1, totalShares()=3110, tokenClaimed(user)=0, tokenBalance(user)=0 — IDENTICAL to runs 1701–2001. Still refund/failed phase; already reported once — NOT re-reported. No preview/claim attempted.
- File: run-2026-11-07-2101-nidavellir-binanceai.json (binanceai section).

## RESULT
- 0 new candidates, 0 new strong leads, 0 new early leads, 0 new track-C leads, 0 track-B openings. 1 new site found (Nidavellir) but free window closed — not a lead. Per the silence rule: nothing to report to chat from this leg.
