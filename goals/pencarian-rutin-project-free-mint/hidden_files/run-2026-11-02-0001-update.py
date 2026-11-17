#!/usr/bin/env python3
"""00:01 run snapshot update (part 1: re-reads + new leads; scan part applied separately)."""
import json
P = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/onchain-snapshot.json"
s = json.load(open(P))
BLK = 131085547
WIB = "2026-11-02T00:02:33+07:00"
# HIVE: 687 -> 697, +10 in 30.32 min = 0.330/min, prev 0.499 -> 0.66x, <20 -> FAIL, outcome unchanged
h = s["contracts"]["HIVE Agents"]
h.update({"totalSupply": 697, "previousTotalSupply": 687, "mintedInInterval": 10,
          "intervalMinutes": 30.32, "currentRatePerMin": 0.330, "previousRatePerMin": 0.499,
          "freePctInference": 69.7, "lastReadBlock": BLK, "lastReadWib": WIB,
          "velocityNote": "Run 00:01 WIB: +10 tokens in ~30.32 min (23:32:14->00:02:33) = 0.330/min, ratio vs prior 0.499/min = 0.66x (<1.5x) and <20 tokens, so the velocity leg still FAILS (outcome unchanged vs 23:31 - no change report). Stored as new baseline.",
          "freePctNote": "Inference only: totalSupply 697 + totalPaid 0 -> 697/1000 FREE_SUPPLY = 69.7%; no freeClaimed view on contract."})
# Bubblebruin: 754 -> 761, +7 in 30.32 min = 0.231/min, prev 0.865 -> 0.27x FAIL; user slot USED (own mint 23:44)
b = s["contracts"]["Bubblebruin"]
b.update({"totalSupply": 761, "freeClaimed": 760, "freePctVerified": 9.77,
          "previousTotalSupply": 754, "mintedInInterval": 7, "intervalMinutes": 30.32,
          "currentRatePerMin": 0.231, "previousRatePerMin": 0.865,
          "lastReadBlock": BLK, "lastReadWib": WIB,
          "velocityNote": "Run 00:01 WIB: +7 tokens in ~30.32 min = 0.231/min, ratio vs prior 0.865/min = 0.27x (<1.5x), so the velocity leg still FAILS. Stored as new baseline."})
# 5 early leads: first computable rate this run (no previous rate at run start -> velocity NOT passed on velocity alone)
five = {
 "Zapcourier": (183, 104, 79, 25.70),
 "Mothwraith": (154, 89, 65, 17.72),
 "Cryonyx": (160, 94, 66, 19.78),
 "Cathodex": (179, 101, 78, 23.46),
 "Malabao": (167, 93, 74, 19.79),
}
for nm, (tot, prev, minted, pct) in five.items():
    c = s["contracts"][nm]
    rate = round(minted / 23.55, 3)
    c.update({"totalSupply": tot, "freeClaimed": tot, "freePctVerified": pct,
              "previousTotalSupply": prev, "mintedInInterval": minted, "intervalMinutes": 23.55,
              "currentRatePerMin": rate, "previousRatePerMin": None,
              "lastReadBlock": BLK, "lastReadWib": WIB,
              "velocityNote": f"Run 00:01 WIB: +{minted} tokens in ~23.55 min (23:39:00->00:02:33) = {rate}/min; no previous rate at run start, so velocity is NOT passed on velocity alone (first computable rate stored as baseline). Free % {pct} still far below the 50% strong-lead leg; X still unverified."})
# NEW EARLY lead: Slimelings
s["contracts"]["Slimelings"] = {
 "address": "0x3815A26a6981BAAd0b850f7522B7a8BDDdB6B70C",
 "status": "early-lead-reported-2026-11-02",
 "name": "Slimelings", "symbol": "SLIME", "kind": "ERC721",
 "totalSupply": 52, "mintedCount": 50, "freeCount": 46, "maxSupply": 10000,
 "mintedBy": 0, "freeClaimed_user": False, "quote_user_1": [0, 0],
 "remainingForWallet_user": 5, "hasAgentId_user": True, "isEligible_user": True,
 "userSlotNote": "Slot open by read: mintedBy(user)=0, freeClaimed(user)=false, quote(user,1)=(0,0), remainingForWallet(user)=5, hasAgentId=1 — NOT preview-verified (early leads are never previewed).",
 "firstSeenBlock": 131083738, "scanMints": 52, "scanMinters": 46,
 "lastReadBlock": BLK, "lastReadWib": WIB, "xVerified": False, "velocityVerified": False,
 "launchNote": "First mint verified on-chain: first Transfer-from-zero at block 131083738, 2026-11-01 23:48:59 WIB (Ankr getLogs from block 130900000; 52 mints in range = totalSupply 52, so all mints ever are in range); no project-stated launch time found; Sourcify verifiedAt 2026-11-01T17:01:40Z (verification time, NOT launch time). First-seen by this job in run 00:01 WIB via Sourcify feed.",
 "baselineNote": "EARLY lead reported once 2026-11-02 run 00:01 WIB. Never auto-minted/previewed. Agent-shape verified: Sourcify ABI (mint + quote + freeClaimed/freeCount + agentId) and agentId() reads the registry 0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F on-chain; gatingEnabled true. Free % UNVERIFIED (no free-cap view; freeCount()=46 is ambiguous, not used as a %); X unverified; velocity not yet computable (first baseline stored this run).",
 "previousTotalSupply": None, "mintedInInterval": None, "intervalMinutes": None,
 "currentRatePerMin": None, "previousRatePerMin": None,
 "velocityNote": "First baseline stored run 00:01 WIB (totalSupply 52 at block 131085547); no previous rate yet, so velocity leg is NOT passed on velocity alone."}
# Pending claims
s["pending_claims"]["binanceai.fun"].update({"totalShares_last": 3093, "lastCheckBlock": BLK, "lastCheckWib": WIB,
  "note": "Seeded per user auto-claim approval 2026-11-01 ~20:27 WIB; dedicated 1h binanceai-claim-watch disabled as subsumed by routine track-B tracking. Already known to user (mint + blocked claim reported); do NOT re-report as a new pending claim - report only on open/claim/block/refund changes. Re-checked 00:01 run: launched still false, isRefundPhase false, failed false, totalShares 3093 (was 3091), MINT holds 13,358,000,000 TOKEN, pair reserves 0/0 - still PENDING, never previewed while not open."})
hp = s["pending_claims"]["hive-pollen"]
hp.update({"pollenAgents": 7463, "pollenSlice_raw": "13399437223636607262494",
  "pollenSlice_estimate": "~13,399 HIVE at 18 decimals (shrinks as more agents join; agentInfo claimable reads 0 pre-launch, so the slice is an estimate, not a fixed claimable)",
  "paidSold": 1008, "lastCheckBlock": BLK, "lastCheckWib": WIB,
  "note": "First verified as the user's entitlement in run 22:31 WIB (accounts(user) = paid 0, pollen true, claimed false, paidValue 0; agentInfo pollen true, claimed false). Reported once as PENDING CLAIM 22:31 run. Re-checked 00:01 run: launched still false, phase 1, accounts words [0, 1, 0, 0] unchanged, pollenAgents 7463 (was 7443), slice ~13,399 (was ~13,435) - still PENDING, never previewed while not open. Next triggers: launched flips true (-> auto-claim check), refund/failed phase (-> report once + remove)."})
# Track C existing
s["track_c"]["BNBbaby"].update({"sharesMinted": 5908, "freeMinted": 5661, "paidShares": 247,
  "lastCheckBlock": BLK, "lastCheckWib": WIB})
s["track_c"]["DOG"].update({"sharesMinted": 56, "lastCheckBlock": BLK, "lastCheckWib": WIB})
s["track_c"]["QILIN"].update({"cards": "totalCards 10000, cardsSold 4458, cardsRemaining 5542, freeCardCap 5000, freeCardsRemaining 584, freeGiven 4416",
  "lastCheckBlock": BLK, "lastCheckWib": WIB})
s["track_c"]["SAFU Tower"].update({"freeClaimed_total": "3750 (no-arg freeClaimed() verified by this run; was 3611 at 23:31 run - free claims still landing; 3750/18444 = 20.3%)",
  "lastCheckBlock": BLK, "lastCheckWib": WIB})
# NEW Track-C leads
s["track_c"]["BNBPIG"] = {
 "sale": "0xfd3d4e0d7a81534addd11f96fdd8008f942097f9",
 "token": "0x936b97cd42f482ef96c7903448e2522dc9e1bd4f",
 "status": "track-c-lead-reported-2026-11-02",
 "saleShape": "PASS (S1): mint(uint256) + quote(address,uint256) + freeAvailable/freeClaimed + agentId() = registry 0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F, Sourcify verified",
 "sharesMinted": 1627, "freeMinted": 1554, "paidShares": 73, "MAX_SHARES": 15000, "MAX_FREE": 5000,
 "mintingOpen": True, "poolOpen": False,
 "freePoolNote": "freeMinted 1554/5000 MAX_FREE -> 3,446 free shares remaining > 0",
 "userSlot": {"freeAvailable": True, "freeClaimed": 0, "mintedBy": 0, "hasAgentId": True, "paidBy": 0, "paidRemainingFor": 14,
   "note": "quote(user,1) returns a multi-word tuple (not a single cost) as for BNBbaby; slot-open conclusion rests on freeAvailable/freeClaimed/mintedBy, stated plainly; quote(user,0) = 0"},
 "ageNote": "VERIFIED <=48h: first Minted event on-chain block 131066360, 2026-11-01 21:38:37 WIB (Ankr getLogs address-filtered, Minted(address,uint256,uint256,uint256,uint256)); 1,564 Minted events in range 131040000-131086500; 0 Minted events in earlier range 130900000-131039999; age ~2.4h at report time",
 "xNote": "NOT a candidate: Boltbook discussion exists (bunnysuny.ai receipt/analysis post 2026-11-01, 'third copy' of the fair-mint template), but NO project X account/handle found - candidate needs X account + discussion",
 "boundary": "LEAD ONLY. NEVER auto-minted, NEVER previewed in this run. Track-C auto-mint (approved 2026-11-01 ~22:41 WIB) does NOT trigger: BNBPIG is a lead, not a candidate (no X account), so no preview/mint was attempted.",
 "lastCheckBlock": BLK, "lastCheckWib": WIB}
s["track_c"]["SAMBARIO"] = {
 "sale": "0xe15e68C9198ee0A5780fba96016e1780204aF3B4",
 "token": "0x647a37bfd60348f9ee471aad3fb3e7ecd6584cd5",
 "status": "track-c-lead-reported-2026-11-02",
 "saleShape": "PASS (S1): mint(uint256,uint256) + quote(address,uint256) + freeCardsRemaining/freeClaimed + registry() = 0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F, Sourcify verified (QILIN-style card sale)",
 "cards": "totalCards 7777, cardsSold 11, cardsRemaining 7766, freeCardCap 3333, freeCardsRemaining 3322, freeGiven 11",
 "tokenName": "SAMBARIO", "tokenSymbol": "SAMBA", "tokensPerShare": 100000,
 "pricePerShare_paid": "0.0012 BNB",
 "gateOn": True, "paused": False,
 "userSlot": {"freeClaimed": 0, "quotaLeft": 10, "quote_user_1": 0,
   "note": "quote(user,1) = 0 (single-word cost); freeClaimed(user)=false, quotaLeft(user)=10"},
 "ageNote": "VERIFIED <=48h: first token mint Transfer-from-zero at block 131080465, 2026-11-01 23:24:26 WIB (Ankr getLogs address-filtered on the token contract; 11 transfers = cardsSold 11, so all sales are in range); age ~40 min at report time. Sale Minted-event topic differs from the BabyMint topic (0 Minted events on that topic), so the token-transfer route is the age evidence, stated plainly.",
 "xNote": "NOT a candidate: web search for SAMBARIO/SAMBA found no project X account and no readable discussion - candidate needs X account + discussion",
 "boundary": "LEAD ONLY. NEVER auto-minted, NEVER previewed in this run. Track-C auto-mint (approved 2026-11-01 ~22:41 WIB) does NOT trigger: SAMBARIO is a lead, not a candidate (no X account), so no preview/mint was attempted.",
 "lastCheckBlock": BLK, "lastCheckWib": WIB}
s["timestamp_wib"] = "2026-11-02T00:01:00+07:00"
json.dump(s, open(P, "w"), indent=1)
print("snapshot part 1 updated; contracts:", list(s["contracts"].keys()))
print("track_c:", list(s["track_c"].keys()))
