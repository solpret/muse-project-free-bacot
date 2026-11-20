# Run 2026-11-06 1501 WIB — Scan leg (route 4) + 5c triage — Worker C

## Scan outcome — SUCCEEDED
- **Pre-flight: OK 8.6s** (head via dataseed 6.4s; ankr_getLogs 50-block chunk, 300 logs). Head at pre-flight 131976746 (15:27:33 WIB). No no_proxy set; Ankr via existing proxy env.
- **Window scanned (actual, script's own head read): 131975781–131976780 (1000 blocks, cap 1000).** Head advanced +34 blocks between pre-flight and scan start; window is the most recent 1000 at scan start, as instructed.
- **Skipped gap (backfill owns): 131963549–131975780 = 12,232 blocks** (watermark 131963548 → window start − 1). NOT scanned; never by enlarging the window.
- **Watermark NOT advanced by this run** (shared `onchain-scan-state.json` last_scanned_block=131963548, backfill owns it).
- **Chunks 20/20, enrich 233/233, 40 Ankr calls, 0 errors, `partial: false`.** Scan ran ~15:28–15:47 WIB (~19.7 min); per-chunk + per-contract progress logged with flush throughout (no stall; longest quiet gap < 2 min).
- **Counts: 233 NFT contracts (226 ERC721 + 7 ERC1155), 1726 NFT mints, 512 ERC-20 mint contracts (excluded).** HIVE Agents NOT found in window.
- **No previews, mints, claims, approvals, signatures, or transactions.** Read-only leg.

## First-seen triage — 5 contracts
First-seen = absent from BOTH `onchain-scan-seen.json` (8255 entries, nested `contracts` + legacy top-level keys combined) AND snapshot `contracts` keys (554). Registry address itself excluded.

### 1. BOBBIE — EARLY LEAD ✅
- Contract: `0x3BF121dC4c5a1Ba567F3eE801d0e447601726207` — BOBBIE / BOBBIE
- **Agent-shape: PASS.** Sourcify exact_match, verifiedAt 2026-11-06T07:08:08Z (14:08:08 WIB), 94 fns. `agentRegistry()` returns exactly `0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F`; `FREE_SUPPLY` 2000; `freeAllocated`/`freeUsed`; `mint()` + `quote(address,uint256,bool)` + `mintStartsAt`/`mintEndsAt`. Registry-bytes hit True.
- **Launch age: VERIFIED ≤48h.** `mintStartsAt()` on-chain = 1793950809 = **2026-11-06 14:40:09 WIB**. Address-filtered Ankr getLogs [131900000, 131975981] found **9 prior mints**, earliest block 131971127 = **14:46:04 WIB** — consistent with mintStartsAt (no mints before it in the checked range). First mint in scan window: block 131975982 = 15:22:30 WIB, 2 mints / 2 minters. Age at scan ~45–67 min.
- **Free pool / user slot (reads only):** FREE_SUPPLY 2000, freeAllocated 94→97 during triage; `mintedBy(user)=0`, `freeUsed(user)=0`; `quote(user,1,·)` first return word = 1 (raw quote tuple — ambiguous, recorded as-is, NOT interpreted as a price). `mintEndsAt` = 2026-11-07 00:40:09 WIB.
- **Anomaly (stated, not resolved):** totalMinted read 68 → 70 → 77 during triage, but only ~13 Transfer mints observed in [131900000, window] — likely settleMint/reserved minting without Transfer events. Does not change the launch-age verdict (anchored by mintStartsAt + earliest Transfer mint).
- **Caveats:** `mint()` is payable and takes a voucher (`mint(uint8, uint256, address, uint256, bytes)`); the free path may need a voucher — NOT verified by this leg, NOT previewed/minted (early lead only).
- **Legs:** age ✓ verified ≤48h; free pool open ✓; user slot open ✓ by reads; X/discussion UNVERIFIED (not checked by this leg); velocity not yet (first snapshot entry pending parent merge); website/gate NOT checked by this leg.

### 2. AgentPad Agent — EARLY LEAD (free-shape only, NO registry evidence — parent decides)
- Contract: `0x71f86082C3b32601f865c63980a9B686e887EAB1` — AgentPad Agent / AGENT
- **Agent-shape: PARTIAL — free-mint shape PASS, registry FAIL.** Sourcify exact_match, verifiedAt 2026-11-06T08:26:55Z (15:26:55 WIB), 52 fns. `mintFree()` nonpayable, no-arg; `claimFree(uint256)` payable; `freeCapPerWallet` 10; `freeMintedBy`; `mintPaid` + `paidPriceWei` 1012292118582791 wei (~0.00101 BNB, paid path exists). **No Agent ID registry reference in ABI or bytecode** (registry_bytes_hit False, no agentRegistry/agentId fn) — unlike registry-based early leads. The body test lists free-mint function/free-supply constant as an alternative shape element, so it is reported as an early lead with this caveat stated; parent decides promotion.
- **Genuinely new: VERIFIED.** Address-filtered Ankr getLogs [131900000, 131976626] found **0 prior mints**. First mint block 131976627 = **15:27:20 WIB** (25 s after verification), 1 mint / 1 minter in window; totalMinted 6 (5 more mints after the window read). Age ~20 min ≤48h VERIFIED.
- **User slot:** `freeMintedBy(user)=0`, `mintOpen`=true.
- **Legs:** age ✓ verified; free shape ✓ (`mintFree` nonpayable); user slot open ✓ by read; registry ✗ none found; X/discussion UNVERIFIED; velocity not yet; website/gate NOT checked by this leg.

### 3. Viking — NOT agent-shaped (log only)
- Contract: `0x7776CE863A142f94094EfF8A84d21F06138A49FD` — Viking / VIKING. First window mint block 131976253 = 15:24:31 WIB, 5 mints / 5 minters.
- Sourcify not_verified (no ABI); registry_bytes_hit False; all agent views revert; MAX_SUPPLY 1111, totalMinted 27. Owner 0xf5c6ee4d1b236ccbbc1f950255ea2deb0a09d77a, not in same-owner-discards. Not a lead.

### 4. Niu Lai (NIULAI) NFT — NOT agent-shaped (log only)
- Contract: `0x9aF2025482d998cF5A1b4235fBDBE8711359f925` — Niu Lai / NIULAI. First window mint block 131975873 = 15:21:40 WIB, 4 mints / 4 minters.
- Sourcify not_verified (no ABI); registry_bytes_hit False; no free view; PRICE 0.001 BNB, MAX_SUPPLY 5555, totalSupply 21 vs 4 window mints (bulk supply predates the window — NOT genuinely new). Owner 0xcbcadc7c9897d21fa6e3a8f941f9f271a39598e3.
- Owner appears in `same-owner-discards.json`, BUT that entry is an explicit EXCEPTION ("owner ini belum terbukti sama dengan project lain, jadi TIDAK dibuang oleh aturan same-owner") — NOT a discard reason.
- Same name as tracked track_c NIULAI sale `0x15e47c22df42D94Fa2f0aD078Fec5Bea6453d5cF`, but a DIFFERENT contract — no linkage claimed. Not a lead.

### 5. DNA EATER — AGE-EXCLUDED (log only)
- Contract: `0xbA15f996307190bd738b66e7fe94abdF9a8951Fa` — DNA EATER / DNAEATER. First window mint block 131976297 = 15:24:51 WIB, 1 mint / 1 minter.
- Registry-bytes hit True and ABI has `AGENT_ID`, but Sourcify verifiedAt **2026-10-28T13:16:11Z** → age ~9 days, **>48h → age-excluded**. No free funcs (ABI 41 fns: mint, mintPriceWei, canMint, grades). totalSupply 7. Not a lead.

## Leg 5c — ERC-20 shape-check (S1/S2)
- Scan output: 512 ERC-20 mint contracts; **57 with window mint_count ≥ 10**; **38 already checked** (combined dedupe: `checked` sub-dict + legacy top-level keys of `track-c-scan-checked.json`); **19 newly checked** (cap 20 — 0 dropped as sampling limit, all new ones covered).
- **0 sale-shape hits (S1=0, S2=0).** All 19 Sourcify not_verified (no ABI → no-shape). 17/19 have registry_bytes=True in bytecode but no ABI — registry bytes alone ≠ sale shape (same pattern as recent runs).
- Newly checked addresses recorded in `run-2026-11-06-1501-5c-checked.json` (parent merges into `track-c-scan-checked.json`; this leg did NOT write the shared store).

## Files written by Worker C (run 1501)
- `run-2026-11-06-1501-scan.log` — pre-flight + per-chunk/enrich progress + outcome
- `run-2026-11-06-1501-scan.json` — scan output (`partial: false`)
- `run-2026-11-06-1501-firstseen.json` — the 5 first-seen contracts (raw scan entries)
- `run-2026-11-06-1501-triage-detail.json` / `run-2026-11-06-1501-triage.log` — per-contract views + owner + discards check
- `run-2026-11-06-1501-abi.json` / `run-2026-11-06-1501-abi.log` — Sourcify ABI (curl, `?fields=abi`) + verifiedAt + fn lists
- `run-2026-11-06-1501-verify.json` / `run-2026-11-06-1501-verify.log` — zero-mints-before checks (address-filtered Ankr) + first-mint timestamps + free-pool reads
- `run-2026-11-06-1501-extra.log` — BOBBIE freeUsed/quote, AgentPad mintFree payability
- `run-2026-11-06-1501-5c-checked.json` / `run-2026-11-06-1501-5c.log` / `run-2026-11-06-1501-5c.py` — leg 5c results + script

## Shared state NOT modified
`onchain-scan-state.json`, `onchain-scan-seen.json`, `onchain-snapshot.json`, `track-c-scan-checked.json`, `hot-leg-seen.json` — all read-only this run; parent merges (2 early leads → snapshot/seen; 19 addresses → checked store).
