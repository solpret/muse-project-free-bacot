#!/usr/bin/env python3
"""2331 run: snapshot + scan-state + seen + track-c-checked updates. Bookkeeping only."""
import json
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
snap = json.load(open(BASE + "onchain-snapshot.json"))
# --- HIVE Agents (route-1 read, block 131081461, ~23:32:14 WIB) ---
h = snap["contracts"]["HIVE Agents"]
h.update({
    "previousTotalSupply": 672, "totalSupply": 687, "mintedInInterval": 15,
    "intervalMinutes": 30.07, "currentRatePerMin": 0.499, "previousRatePerMin": 0.201,
    "velocityNote": "Run 23:31 WIB: +15 tokens in ~30.07 min (23:02:10->23:32:14) = 0.499/min, ratio vs prior 0.201/min = 2.48x (>=1.5x) BUT 15 < 20 tokens, so the velocity leg still FAILS (outcome unchanged vs 23:01 - no change report). Stored as new baseline.",
    "velocityVerified": False, "freePctInference": 68.7,
    "freePctNote": "Inference only: totalSupply 687 + totalPaid 0 -> 687/1000 FREE_SUPPLY = 68.7%; no freeClaimed view on contract.",
    "lastReadBlock": 131081461, "lastReadWib": "2026-11-01T23:32:14+07:00",
    "baselineNote": "Deep-sweep lead; % is inference from totalSupply + totalPaid=0, not a freeClaimed view; START_TIME 2026-11-01 16:00 WIB; free slot open for user wallet; X unverified; velocity FAILS at 23:31 WIB run (+15 tokens, 2.48x but <20 tokens) - outcome unchanged vs 23:01 WIB fail, so no change report. Still NOT a candidate (X unverified); already reported as watchlist lead 2026-11-01 ~19:36 WIB.",
})
# --- Bubblebruin ---
b = snap["contracts"]["Bubblebruin"]
b.update({
    "previousTotalSupply": 728, "totalSupply": 754, "freeClaimed": 753,
    "mintedInInterval": 26, "intervalMinutes": 30.07, "currentRatePerMin": 0.865,
    "previousRatePerMin": 1.084,
    "velocityNote": "Run 23:31 WIB: +26 tokens in ~30.07 min (23:02:10->23:32:14) = 0.865/min, ratio vs prior 1.084/min = 0.80x (< 1.5x), so the velocity leg still FAILS. Stored as new baseline.",
    "velocityVerified": False, "freePctVerified": 9.68,
    "lastReadBlock": 131081461, "lastReadWib": "2026-11-01T23:32:14+07:00",
    "baselineNote": "EARLY lead reported once 2026-11-01 run 20:31 WIB. Never auto-minted/previewed. Promotes to strong lead only on all 3 strong-lead legs; to candidate only on ALL criteria + safety. At 23:31 WIB: 753/7777 = 9.68% verified free (far below 50% strong leg), age still UNVERIFIED, X still UNVERIFIED, slot open by read, velocity still fails (0.80x).",
})
# --- New EARLY leads (first mints 23:18 WIB, verified via Ankr logs from block 131060000: no earlier mints) ---
early = {
    "Zapcourier": {"address": "0x672c1dF4F7121DaCBD3504995441C47d2fAbCdDC", "symbol": "VOLTVX", "totalSupply": 104, "FREE_SUPPLY": 712, "MAX_SUPPLY": 890, "first_block": 131079654, "window_mints": 78, "window_minters": 78},
    "Mothwraith": {"address": "0x11fa2C4b71EcE40f242992a08C4ACC6C23c99Ca0", "symbol": "MOTHWR", "totalSupply": 89, "FREE_SUPPLY": 869, "MAX_SUPPLY": 1087, "first_block": 131079663, "window_mints": 67, "window_minters": 67},
    "Cryonyx": {"address": "0x787b522d48084A83b8B1b0C206aA4A12B1FD1cc2", "symbol": "CRYONX", "totalSupply": 94, "FREE_SUPPLY": 809, "MAX_SUPPLY": 1012, "first_block": 131079646, "window_mints": 72, "window_minters": 72},
    "Cathodex": {"address": "0x0AC5591d1B980C7bE16861d722E59E21E2624868", "symbol": "CATHDX", "totalSupply": 101, "FREE_SUPPLY": 763, "MAX_SUPPLY": 954, "first_block": 131079661, "window_mints": 83, "window_minters": 83},
    "Malabao": {"address": "0x2C215262635E66c798c5a1Ba4411fA9F06852bDD", "symbol": "MALABA", "totalSupply": 93, "FREE_SUPPLY": 844, "MAX_SUPPLY": 1056, "first_block": 131079671, "window_mints": 70, "window_minters": 70},
}
for name, e in early.items():
    snap["contracts"][name] = {
        "address": e["address"], "status": "early-lead-reported-2026-11-01",
        "name": name, "symbol": e["symbol"], "kind": "ERC721",
        "totalSupply": e["totalSupply"], "freeClaimed": e["totalSupply"],
        "FREE_SUPPLY": e["FREE_SUPPLY"], "MAX_SUPPLY": e["MAX_SUPPLY"],
        "freePctVerified": round(100 * e["totalSupply"] / e["FREE_SUPPLY"], 2),
        "mintOpen": True, "userMintedBy": 0, "userFreeUsed": 0, "userBalance": 0,
        "userSlotNote": "Slot open by mintedBy(user)=0 + freeUsed(user)=0 reads at block 131081717; NOT preview-verified (early leads are never previewed).",
        "firstSeenBlock": e["first_block"], "scanWindow": "131079442-131081441",
        "scanMints": e["window_mints"], "scanMinters": e["window_minters"],
        "lastReadBlock": 131082023, "lastReadWib": "2026-11-01T23:39:00+07:00",
        "xVerified": False, "velocityVerified": False,
        "launchNote": "First mint verified on-chain: first Transfer-from-zero at block %d, 2026-11-01 23:18 WIB (Ankr getLogs from block 131060000: no earlier mints); no project-stated launch time found; Sourcify verifiedAt 2026-11-01T16:18:35Z (verification time, NOT launch time). First-seen by this job in run 23:31 WIB via Sourcify feed + scan cross-check." % e["first_block"],
        "baselineNote": "EARLY lead reported once 2026-11-01 run 23:31 WIB. Never auto-minted/previewed. Agent-shape verified: Sourcify ABI (mint + quote + freeClaimed/freeFor/freeLeft/freeUsed + FREE_SUPPLY) and AGENT_ID() reads the registry 0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F on-chain. Promotes to strong lead only on all 3 strong-lead legs; to candidate only on ALL criteria + safety. Free % far below 50%; X unverified; velocity not yet computable (first baseline stored this run).",
        "previousTotalSupply": None, "mintedInInterval": None, "intervalMinutes": None,
        "currentRatePerMin": None, "previousRatePerMin": None,
        "velocityNote": "First baseline stored run 23:31 WIB (totalSupply %d at block 131082023); no previous rate yet, so velocity leg is NOT passed on velocity alone." % e["totalSupply"],
    }
# --- Pending claims re-check ---
snap["pending_claims"]["binanceai.fun"].update({
    "totalShares_last": 3091, "lastCheckBlock": 131081461, "lastCheckWib": "2026-11-01T23:32:14+07:00",
    "note": "Seeded per user auto-claim approval 2026-11-01 ~20:27 WIB; dedicated 1h binanceai-claim-watch disabled as subsumed by routine track-B tracking. Already known to user (mint + blocked claim reported); do NOT re-report as a new pending claim - report only on open/claim/block/refund changes. Re-checked 23:31 run: launched still false, isRefundPhase false, failed false, totalShares 3091 (unchanged), MINT holds 13,358,000,000 TOKEN, pair reserves 0/0 - still PENDING, never previewed while not open.",
})
hp = snap["pending_claims"]["hive-pollen"]
hp.update({
    "pollenAgents": 7443, "pollenSlice_raw": "13435442697836893725648",
    "pollenSlice_estimate": "~13,435 HIVE at 18 decimals (shrinks as more agents join; agentInfo claimable reads 0 pre-launch, so the slice is an estimate, not a fixed claimable)",
    "lastCheckBlock": 131081461, "lastCheckWib": "2026-11-01T23:32:14+07:00",
    "note": "First verified as the user's entitlement in run 22:31 WIB (accounts(user) = paid 0, pollen true, claimed false, paidValue 0; agentInfo pollen true, claimed false). Reported once as PENDING CLAIM 22:31 run. Re-checked 23:31 run: launched still false, phase 1, accounts words [0, 1, 0, 0] unchanged, pollenAgents 7443 (was 7421), slice ~13,435 (was ~13,475) - still PENDING, never previewed while not open. Next triggers: launched flips true (-> auto-claim check), refund/failed phase (-> report once + remove).",
})
# --- Track C ---
bb = snap["track_c"]["BNBbaby"]
bb.update({"sharesMinted": 5564, "freeMinted": 5332, "paidShares": 232,
           "lastCheckBlock": 131081461, "lastCheckWib": "2026-11-01T23:32:14+07:00",
           "freePoolNote": "No free cap: free share open to every Agent-ID wallet until 18,888 total shares; headroom 13,324 shares at read time",
           "xNote": "NOT a candidate: Boltbook discussion exists (receipt-bearing posts 2026-11-01), but NO project X account/handle found - re-checked 23:31 run (web search returns only unrelated BabyBNB/BabySwap tokens) - candidate needs X account + discussion",
           "boundary": "LEAD ONLY. NEVER auto-minted, NEVER previewed in this run. Track-C auto-mint (approved 2026-11-01 ~22:41 WIB) does NOT trigger: BNBbaby is a lead, not a candidate (no X account), so no preview/mint was attempted."})
q = snap["track_c"]["QILIN"]
q.update({"cards": "totalCards 10000, cardsSold 4254, cardsRemaining 5746, freeCardCap 5000, freeCardsRemaining 785, freeGiven 4215",
          "lastCheckBlock": 131081461, "lastCheckWib": "2026-11-01T23:32:14+07:00"})
s = snap["track_c"]["SAFU Tower"]
s.update({"freeClaimed_total": "3611 (no-arg freeClaimed() verified by this run; was 3192 at 23:01 run - free claims still landing; 3611/18444 = 19.6%)",
          "lastCheckBlock": 131081461, "lastCheckWib": "2026-11-01T23:32:14+07:00"})
snap["track_c"]["DOG"] = {
    "sale": "0xA74bEF84304D8838db798faE96fb873dd46fB4C1",
    "token": "0xF54E80a86FCF71Fa2F86Eb9bC2f21f36B94961b7",
    "status": "track-c-lead-reported-2026-11-01",
    "saleShape": "PASS (S1): mint(uint256) + quote(address,uint256) -> (freeCount,cost) + freeClaimed(bytes32) + registry() = 0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F, Sourcify verified (verifiedAt 2026-11-01T16:18:35Z, verification time NOT launch time)",
    "sharesMinted": 12, "FREE_SHARES": 4000, "MAX_SHARES": 12000,
    "deadline": "2026-11-04T23:18:00+07:00 (deadline() 1793809097; sale end, not launch)",
    "poolOpen": False, "saleFailed": False,
    "freePoolNote": "sharesMinted 12 of 12000 MAX with FREE_SHARES 4000; total free claimed not directly countable (freeClaimed is per-agent), but at most 12 shares minted in total, so the free pool is overwhelmingly open",
    "userSlot": {"freeClaimed": False, "sharesByWallet": 0, "quote_freeCount": 1, "quote_cost": 0,
                 "note": "quote(user,1) = (freeCount 1, cost 0); quote(user,0) reverts (zero-quantity error, irrelevant)"},
    "ageNote": "VERIFIED <=48h: first Minted event on-chain block 131079656, 2026-11-01 23:18 WIB (Ankr getLogs, Minted(address,bytes32,uint256,uint256,uint256)); 12 Minted events total, matching sharesMinted 12; no project-stated launch time found, but launch cannot predate the first mint, so age at report time is under 1 hour",
    "xNote": "NOT a candidate: web search for the sale contract, DOG token, and related names found no project X account and no readable discussion - candidate needs X account + discussion",
    "boundary": "LEAD ONLY. NEVER auto-minted, NEVER previewed in this run. Track-C auto-mint (approved 2026-11-01 ~22:41 WIB) does NOT trigger: DOG is a lead, not a candidate (no X account), so no preview/mint was attempted.",
    "lastCheckBlock": 131081717, "lastCheckWib": "2026-11-01T23:39:00+07:00",
}
for sym, addr, started in [("JUBAO", "0x1ed3BF35e4DA25b1289C27ddbD82f0A38DDCee8b", 1793549525),
                           ("ZCMAO", "0x8362e6a5F38427d8d719EA47f08890784F6023DC", 1793549494),
                           ("JINLONG", "0x2Df4Ef534cbBe1a8F647e24D0f8C75ECe74D8288", 1793549461)]:
    snap["track_c"][sym] = {
        "token": addr, "status": "checked-not-a-lead-2026-11-01",
        "saleShape": "FAILS S2/track-C shape: single-contract token+sale (claimFree + freeClaimed + FREE_SHARES 4444 + PAID_SHARES 10000 + pair) BUT no Agent ID registry reference or AgentGate in ABI (identity() only) AND registry address bytes absent from bytecode - all shape elements are required",
        "freeClaimed_total": "6-7 of 4444 FREE_SHARES (per contract: JUBAO 7, ZCMAO 7, JINLONG 6)",
        "launched": False, "phase": 1, "sold": 0,
        "startedAtNote": "startedAt() %d (~2026-11-01 23:12 WIB) read on-chain, but launched() is false and the agent-gate leg already fails, so this is not a lead regardless of age" % started,
        "userSlotNote": "User slot UNVERIFIABLE via address views: freeClaimedById/mintedById/remainingQuota/identity(address) all revert (they take an agent ID, not a wallet address); leads are never previewed, so no sim was run",
        "xNote": "No project X account found in this run's searches",
        "lastCheckBlock": 131081717, "lastCheckWib": "2026-11-01T23:39:00+07:00",
    }
snap["timestamp_wib"] = "2026-11-01T23:31:00+07:00"
snap["note"] = snap["note"] + " Run 2026-11-01 23:31 WIB: HIVE 687 (+15, velocity still FAILS: 2.48x but <20 tokens - outcome unchanged, no change report; still strong lead, NOT a candidate: X unverified), Bubblebruin 754/7777 = 9.68% verified free (still EARLY, age + X unverified, velocity still fails 0.80x), binanceai.fun still pending (launched false, totalShares 3091), hive-pollen still pending (launched false, pollenAgents 7443, slice ~13,435), BNBbaby still LEAD only (5564 shares, free 5332, user slot open, NO X account found again - Track-C auto-mint NOT triggered, never previewed/minted), QILIN still checked-not-a-lead (user free used, freeCardsRemaining 785), SAFU Tower still checked-not-a-lead (freeClaimed total 3611, S2 partial, no X). NEW: 5 EARLY leads (Zapcourier, Mothwraith, Cryonyx, Cathodex, Malabao - agent-shaped ERC-721 batch, first mints 23:18 WIB verified via Ankr logs from block 131060000 with no earlier mints; free % 10-15%, X unverified, velocity baseline stored, never previewed/minted) and 1 NEW Track-C LEAD DOG (sale 0xA74b..., token DOG 0xF54e..., sharesMinted 12, FREE_SHARES 4000, user quote freeCount 1 cost 0, first Minted event 23:18 WIB, NO X account - lead only, never previewed/minted). Scan SUCCEEDED this run: window 131079442-131081441 (2000 blocks, capped; head 131081441 minus last_scanned 131074195 = 7246 > 2000, so only the most recent 2000 scanned; skipped gap 131074196-131079441 recorded, never scanned), 80 Ankr calls, 0 errors, 520 NFT contracts, 912 ERC20-mint contracts; first-seen triage: 181 first-seen, 40 verified+free/registry, 35 of the other 35 triaged as continuations (totals far above window mints, or pre-window first mints: Pagoda 22:42 WIB, AgentDrill 22:38 WIB; InkPress single-minter 16 logs from 23:05 WIB, not a public launch) - only the 5-name batch passed the first-mint test; Sourcify feed cross-check: same 5 NFTs + DOG sale in the 30-address poll (no double report). Track-C ERC-20 backlog: top 20 by window mint_count >=10 (skipping 10 previously checked + snapshot-known) shape-checked, 0 sale-shape passes (12 Sourcify-unverified, 8 verified non-sale); remainder beyond 20 dropped as sampling limit, stated. Watermark advanced to 131081441; seen file updated. NO track-A candidate, NO track-B opening/claim/block, NO track-C candidate - no auto-mint/auto-claim triggered (leads are never previewed/minted; early leads are never previewed/minted)."
json.dump(snap, open(BASE + "onchain-snapshot.json", "w"), indent=1, ensure_ascii=False)
# --- scan state ---
state = {"last_scanned_block": 131081441, "last_scan_window_from": 131079442,
         "last_scan_wib": "2026-11-01T23:31:00+07:00", "ankr_calls": 80, "errors": [],
         "nft_contracts": 520,
         "note": "Run 23:31 WIB scan: 2000 blocks (capped; head 131081441 minus last_scanned 131074195 = 7246 > 2000, so only the most recent 2000 scanned; skipped gap 131074196-131079441 recorded, never scanned). Scan wall time ~16.5 min. Next run scans from last_scanned_block+1, capped at 2000 blocks."}
json.dump(state, open(BASE + "onchain-scan-state.json", "w"), indent=1)
# --- seen file: append scan contracts (address -> first_block), keep existing ---
seen = json.load(open(BASE + "onchain-scan-seen.json"))
contracts = seen.setdefault("contracts", {})
scan = json.load(open(BASE + "onchain-scan-2026-11-01-2331.json"))
added = 0
for c in scan["contracts"]:
    a = c["address"].lower()
    if a not in contracts:
        contracts[a] = c["first_block"]; added += 1
# registry itself stays excluded (not a project); ensure it is not treated as a lead by marking in known list is unnecessary - body excludes it explicitly
json.dump(seen, open(BASE + "onchain-scan-seen.json", "w"), indent=1)
print("snapshot updated; scan state advanced to 131081441; seen contracts:", len(contracts), "added:", added)
# --- track-c checked file: merge 20 backlog results ---
chk = json.load(open(BASE + "track-c-scan-checked.json"))
backlog = json.load(open(BASE + "run-2026-11-01-2331-trackc-erc20.json"))
for o in backlog:
    chk["checked"][o["address"]] = {"mint_count": o["mint_count"], "distinct_minters": o.get("distinct_minters"),
        "shape_pass": bool(o.get("S1") or o.get("S2")), "S1": o.get("S1"), "S2": o.get("S2"),
        "error": o.get("error"), "fns_sample": o.get("fns_sample")}
chk["note"] = chk.get("note", "") + " Run 23:31 WIB: 20 more backlog ERC-20 contracts shape-checked (window mint_count >=10, sorted desc, skipping previously checked + snapshot-known), 0 sale-shape passes (12 Sourcify-unverified, 8 verified non-sale)."
json.dump(chk, open(BASE + "track-c-scan-checked.json", "w"), indent=1)
print("track-c checked total:", len(chk["checked"]))
