#!/usr/bin/env python3
"""Run 0201 snapshot update. Applies read + verify results; scan triage applied separately if it adds items."""
import json
HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
snap = json.load(open(HF + "onchain-snapshot.json"))
read = json.load(open(HF + "run-2026-11-02-0201-read.json"))
verify = json.load(open(HF + "run-2026-11-02-0201-verify.json"))
jinli = json.load(open(HF + "run-2026-11-02-0201-jinli-verify.json"))
def gi(x, k):
    v = x.get(k, {}) if isinstance(x, dict) else None
    return v.get("int") if isinstance(v, dict) else None
READ_WIB = "2026-11-02T02:07:58+07:00"
READ_BLOCK = read["block"]
# --- velocity updates for pre-existing NFT contracts (interval from stored lastReadWib) ---
from datetime import datetime
fmt = "%Y-%m-%dT%H:%M:%S+07:00"
def mins(a, b): return (datetime.strptime(b, fmt) - datetime.strptime(a, fmt)).total_seconds() / 60
NFT_MAP = [("HIVE Agents", "HIVE"), ("Bubblebruin", "Bubblebruin"), ("Zapcourier", "Zapcourier"),
           ("Mothwraith", "Mothwraith"), ("Cryonyx", "Cryonyx"), ("Cathodex", "Cathodex"),
           ("Malabao", "Malabao"), ("Voltabyte", "Voltabyte"), ("Saturnin", "Saturnin"),
           ("Kirinova", "Kirinova"), ("Ghostbloom", "Ghostbloom"), ("Junepup", "Junepup"),
           ("Gourdwick", "Gourdwick"), ("Kitsunaru", "Kitsunaru"), ("Nightsable", "Nightsable"),
           ("Lensorb", "Lensorb"), ("Nimaluo", "Nimaluo")]
for name, key in NFT_MAP:
    old = snap["contracts"][name]; new_ts = gi(read[key], "totalSupply()")
    dt = mins(old["lastReadWib"], READ_WIB); minted = new_ts - old["totalSupply"]
    rate = minted / dt; prev_rate = old.get("currentRatePerMin")
    passes = bool(prev_rate is not None and rate >= 1.5 * prev_rate and minted >= 20)
    old["previousTotalSupply"] = old["totalSupply"]; old["totalSupply"] = new_ts
    old["mintedInInterval"] = minted; old["intervalMinutes"] = round(dt, 2)
    old["previousRatePerMin"] = prev_rate; old["currentRatePerMin"] = round(rate, 3)
    old["velocityLegPasses"] = passes; old["lastReadBlock"] = READ_BLOCK; old["lastReadWib"] = READ_WIB
    if name == "HIVE Agents":
        old["freePctInference"] = round(new_ts / 1000 * 100, 1)
        old["velocityNote"] = f"Run 02:01 WIB: +{minted} tokens in ~{dt:.2f} min = {rate:.3f}/min, ratio vs prior {prev_rate} = {rate/prev_rate:.2f}x and <20 tokens, so the velocity leg still FAILS (outcome unchanged vs 01:31 - no change report). Stored as new baseline."
    elif name in ("Gourdwick", "Kitsunaru", "Nightsable", "Lensorb", "Nimaluo"):
        old["freeClaimed"] = gi(read[key], "freeClaimed()")
        old["freePctVerified"] = round(old["freeClaimed"] / old["FREE_SUPPLY"] * 100, 2)
        old["velocityNote"] = f"Run 02:01 WIB: +{minted} tokens in ~{dt:.2f} min = {rate:.3f}/min; first computable rate (previous rate was null), so the velocity leg is NOT passed on velocity alone. Stored as new baseline."
        old["velocityLegPasses"] = False
    else:
        old["freeClaimed"] = gi(read[key], "freeClaimed()")
        if old.get("FREE_SUPPLY"): old["freePctVerified"] = round(old["freeClaimed"] / old["FREE_SUPPLY"] * 100, 2)
        old["velocityNote"] = f"Run 02:01 WIB: +{minted} tokens in ~{dt:.2f} min = {rate:.3f}/min, ratio vs prior {prev_rate} = {rate/prev_rate:.2f}x, so the velocity leg still FAILS. Stored as new baseline."
    old["velocityVerified"] = False
# Slimelings (special fields)
old = snap["contracts"]["Slimelings"]; prev = old["totalSupply"]; new_ts = gi(read["Slimelings"], "totalSupply()")
dt = mins(old["lastReadWib"], READ_WIB); minted = new_ts - prev; rate = minted / dt; prev_rate = old["currentRatePerMin"]
old["previousTotalSupply"] = prev; old["totalSupply"] = new_ts; old["mintedCount"] = gi(read["Slimelings"], "mintedCount()")
old["freeCount"] = gi(read["Slimelings"], "freeCount()"); old["mintedInInterval"] = minted
old["intervalMinutes"] = round(dt, 2); old["previousRatePerMin"] = prev_rate; old["currentRatePerMin"] = round(rate, 3)
old["velocityLegPasses"] = bool(rate >= 1.5 * prev_rate and minted >= 20)
old["velocityNote"] = f"Run 02:01 WIB: +{minted} tokens in ~{dt:.2f} min = {rate:.2f}/min, ratio vs prior {prev_rate} = {rate/prev_rate:.2f}x and >=20 tokens, so the velocity leg now PASSES. BUT free % still UNVERIFIED and X still unverified, so this is recorded here only: NOT a promotion and NOT a candidate - remains EARLY only, never previewed/minted. Stored as new baseline."
old["lastReadBlock"] = READ_BLOCK; old["lastReadWib"] = READ_WIB
# Vorpry
old = snap["contracts"]["Vorpry"]; prev = old["totalSupply"]; new_ts = gi(read["Vorpry"], "totalSupply()")
dt = mins(old["lastReadWib"], READ_WIB); minted = new_ts - prev; rate = minted / dt; prev_rate = old["currentRatePerMin"]
old["previousTotalSupply"] = prev; old["totalSupply"] = new_ts; old["openLeft"] = gi(read["Vorpry"], "openLeft()")
old["mintedInInterval"] = minted; old["intervalMinutes"] = round(dt, 2); old["previousRatePerMin"] = prev_rate
old["currentRatePerMin"] = round(rate, 3); old["velocityLegPasses"] = False
old["velocityNote"] = f"Run 02:01 WIB: +{minted} tokens in ~{dt:.2f} min = {rate:.3f}/min, ratio vs prior {prev_rate} = {rate/prev_rate:.2f}x, so the velocity leg still FAILS. Stored as new baseline."
old["lastReadBlock"] = READ_BLOCK; old["lastReadWib"] = READ_WIB
# Mirror Pair
old = snap["contracts"]["Mirror Pair"]; old["mintedPairs"] = gi(read["MirrorPair"], "mintedPairs()")
old["totalBonds"] = gi(read["MirrorPair"], "totalBonds()"); old["lastReadBlock"] = READ_BLOCK; old["lastReadWib"] = READ_WIB
old["velocityNote"] = "Run 02:01 WIB: mintedPairs still 2 (was 2) - no new pair; velocity not computable."
# Bubblebruin user slot (already used, unchanged)
snap["contracts"]["Bubblebruin"]["userMintedBy"] = 1
# --- new early leads from Sourcify verify (baseline = verify totals, head 131103100) ---
VERIFY_WIB = "2026-11-02T02:14:59+07:00"; VERIFY_BLOCK = verify["head"]
def add_early(key, name, symbol, addr, vkey, first_block, first_ts_wib, free_pct, note_extra):
    v = verify[vkey]
    snap["contracts"][name] = {
        "address": addr, "status": "early-lead-reported-2026-11-02", "name": name, "symbol": symbol, "kind": "ERC721",
        "totalSupply": v["totalSupply()"] if v["totalSupply()"] is not None else v["totalMinted()"],
        "freeClaimed": v["freeClaimed()"], "FREE_SUPPLY": v["FREE_SUPPLY()"], "MAX_SUPPLY": v["MAX_SUPPLY()"],
        "freePctVerified": free_pct, "mintOpen": bool(v["mintOpen()"]) if v["mintOpen()"] is not None else None,
        "userMintedBy": v["mintedBy_user"], "userFreeUsed": v["freeUsed_user"], "userBalance": v["balance_user"],
        "userSlotNote": "Slot open by read: mintedBy(user)=0, freeUsed(user)=0, quote(user,1)=0, balance 0 - NOT preview-verified (early leads are never previewed)." if vkey != "SourcifyNFT-a233" else "Slot open by read: mintedBy(user)=0, quote(user,1)=0, balance 0, freePerWallet=2 - NOT preview-verified (early leads are never previewed).",
        "firstSeenBlock": first_block, "scanMints": v["first_mints"]["count"], "scanMinters": v["first_mints"]["distinct_minters"],
        "lastReadBlock": VERIFY_BLOCK, "lastReadWib": VERIFY_WIB, "xVerified": False, "velocityVerified": False,
        "launchNote": f"First mint verified on-chain: first Transfer-from-zero at block {first_block}, {first_ts_wib} (Ankr getLogs address-filtered from block 131060000; {v['first_mints']['count']} logs in range vs totalSupply/totalMinted {v['totalSupply()'] if v['totalSupply()'] is not None else v['totalMinted()']} at verify time - logs trail supply where counts differ, stated plainly, first block still verified); no project-stated launch time found; Sourcify verifiedAt is verification time, NOT launch time. First-seen by this job in run 02:01 WIB via Sourcify feed.",
        "baselineNote": "EARLY lead reported once 2026-11-02 run 02:01 WIB. Never auto-minted/previewed. " + note_extra,
        "previousTotalSupply": None, "mintedInInterval": None, "intervalMinutes": None, "currentRatePerMin": None,
        "previousRatePerMin": None, "velocityNote": "First baseline stored run 02:01 WIB; no previous rate yet, so velocity leg is NOT passed on velocity alone.",
        "velocityLegPasses": False}
add_early(None, "Agents NormiePunks", "NPUNK", "0xa233C45f881A6982647b63c61D7a5f9a3F90C5f4", "SourcifyNFT-a233", 131102533, "2026-11-02 02:09:59 WIB", None,
          "Agent-shape verified: Sourcify ABI (mint + quote + agentRegistry + requireAgentId/hasAgentId) and agentRegistry() reads the registry 0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F on-chain. Free % UNVERIFIED (no freeClaimed/FREE_SUPPLY view; freePerWallet 2); X unverified; velocity not yet computable.")
add_early(None, "Medusine", "MEDUSI", "0x8E878C801b9F37cc0Cb6FF3C4597Af8FC057988b", "SourcifyNFT-8E87", 131102467, "2026-11-02 02:09:30 WIB", 3.23,
          "Agent-shape verified: Sourcify ABI (mint + quote + freeClaimed/freeFor/freeLeft/freeUsed + FREE_SUPPLY) and AGENT_ID() reads the registry 0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F on-chain. Free % 3.23% verified, far below 50%; X unverified; velocity not yet computable.")
add_early(None, "Hotpotsage", "HOTPOT", "0xEbAdb5Be9692b0BF25E8A5F3351C35DdC58f195d", "SourcifyNFT-EbAd", 131102478, "2026-11-02 02:09:34 WIB", 3.32,
          "Agent-shape verified: Sourcify ABI (mint + quote + freeClaimed/freeFor/freeLeft/freeUsed + FREE_SUPPLY) and AGENT_ID() reads the registry 0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F on-chain. Free % 3.32% verified, far below 50%; X unverified; velocity not yet computable.")
add_early(None, "Mummyrelic", "MUMMYR", "0xB330e582f45c0243e5Eb1B56958b56273f26a9eB", "SourcifyNFT-B330", 131102477, "2026-11-02 02:09:34 WIB", 2.55,
          "Agent-shape verified: Sourcify ABI (mint + quote + freeClaimed/freeFor/freeLeft/freeUsed + FREE_SUPPLY) and AGENT_ID() reads the registry 0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F on-chain. Free % 2.55% verified, far below 50%; X unverified; velocity not yet computable.")
add_early(None, "Ravenhex", "RAVENH", "0xB44050254A25dAA8077C14BbB20d0a595e6CECE2", "SourcifyNFT-B440", 131102460, "2026-11-02 02:09:26 WIB", 3.68,
          "Agent-shape verified: Sourcify ABI (mint + quote + freeClaimed/freeFor/freeLeft/freeUsed + FREE_SUPPLY) and AGENT_ID() reads the registry 0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F on-chain. Free % 3.68% verified, far below 50%; X unverified; velocity not yet computable.")
add_early(None, "Orbitmarshal", "ORBITM", "0x74C2214fDCc10c303302592151c50965903aa7a9", "SourcifyNFT-74C2", 131102450, "2026-11-02 02:09:22 WIB", 2.77,
          "Agent-shape verified: Sourcify ABI (mint + quote + freeClaimed/freeFor/freeLeft/freeUsed + FREE_SUPPLY) and AGENT_ID() reads the registry 0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F on-chain. Free % 2.77% verified, far below 50%; X unverified; velocity not yet computable.")
# Kiln Agent is DELIBERATELY NOT added: verified free-tier at 02:14 WIB (costFor 0) but re-checked paid-only at ~02:27 WIB (totalMinted 418 = FREE_SUPPLY 418, costFor(1) = currentPrice = 0.0005 BNB). Reporting it as an early lead now would present a paid mint as free, so it is recorded in the run log only, never reported as a lead and never added to the snapshot.
add_early(None, "Lighthouse Agent", "LIGHT", "0x011F1aeaF230A5E8dee20168654644DA4DE3C4B5", "SourcifyNFT-011F", 131101588, "2026-11-02 02:02:54 WIB", None,
          "Agent-shape verified: Sourcify ABI (mint + costFor/currentPrice + FREE_SUPPLY) and agentIdRegistry() reads the registry 0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F on-chain; costFor(1)=0 and currentPrice()=0 at verify time (free tier). Free % UNVERIFIED (no freeClaimed view; totalMinted 101 vs FREE_SUPPLY 483 is NOT used as a free % because a paid lane PRICE 0.0005 BNB exists); X unverified; velocity not yet computable.")
# fix Lighthouse totalSupply field (totalMinted-based) and user slot note
snap["contracts"]["Lighthouse Agent"]["userSlotNote"] = "Slot open by read: mintedBy(user)=0, costFor(1)=0, currentPrice()=0, balance 0 - NOT preview-verified (early leads are never previewed)."
# --- track_c updates from read ---
tc = snap["track_c"]
tc["BNBbaby"].update({"sharesMinted": gi(read["BNBbaby"], "sharesMinted()"), "freeMinted": gi(read["BNBbaby"], "freeMinted()"), "paidShares": gi(read["BNBbaby"], "paidShares()")})
tc["DOG"].update({"sharesMinted": gi(read["DOG"], "sharesMinted()")})
tc["BNBPIG"].update({"sharesMinted": gi(read["BNBPIG"], "sharesMinted()"), "freeMinted": gi(read["BNBPIG"], "freeMinted()"), "paidShares": gi(read["BNBPIG"], "paidShares()")})
tc["SAMBARIO"].update({"cards": f"totalCards 7777, cardsSold {gi(read['SAMBARIO'], 'cardsSold()')}, cardsRemaining {gi(read['SAMBARIO'], 'cardsRemaining()')}, freeCardCap 3333, freeCardsRemaining {gi(read['SAMBARIO'], 'freeCardsRemaining()')}, freeGiven {gi(read['SAMBARIO'], 'freeGiven()')}"})
tc["a7Be"].update({"sharesMinted": gi(read["a7Be"], "sharesMinted()"), "freeSharesMinted": gi(read["a7Be"], "freeSharesMinted()")})
tc["NIUBI"].update({"sharesMinted": gi(read["NIUBI"], "sharesMinted()"), "freeMinted": gi(read["NIUBI"], "freeMinted()")})
tc["QILIN"].update({"cards": f"totalCards 10000, cardsSold {gi(read['QILIN'], 'cardsSold()')}, cardsRemaining {gi(read['QILIN'], 'cardsRemaining()')}, freeCardCap 5000, freeCardsRemaining {gi(read['QILIN'], 'freeCardsRemaining()')}, freeGiven {gi(read['QILIN'], 'freeGiven()')}"})
tc["SAFU Tower"].update({"freeClaimed_total": gi(read["SAFU"], "freeClaimed()")})
tc["零元购"].update({"soldFree": gi(read["ZeroYuanGou"], "soldFree()"), "totalSold": gi(read["ZeroYuanGou"], "totalSold()"), "freeRemaining": 2000 - gi(read["ZeroYuanGou"], "soldFree()")})
tc["RuninAI"].update({"freeClaimed": gi(read["RuninAI"], "freeClaimed()"), "freeRemaining": 4444 - gi(read["RuninAI"], "freeClaimed()"), "sold_paid": gi(read["RuninAI"], "sold()")})
for nm in ("JUBAO", "ZCMAO", "JINLONG"):
    tc[nm].update({"freeClaimed_total": gi(read[nm], "freeClaimed()")})
# new track_c leads
tc["JINLI"] = {"address": "0xd7a2567929da32cab052cf287522cd6e3d3ecfa2", "status": "track-c-lead-reported-2026-11-02", "name": "JINLI", "symbol": "JINLI", "kind": "ERC20-sale-S2-variant",
    "freeClaimed": gi(jinli, "freeClaimed()") if False else jinli["freeClaimed()"], "FREE_SHARES": jinli["FREE_SHARES()"], "freeRemaining": jinli["FREE_SHARES()"] - jinli["freeClaimed()"],
    "PAID_SHARES": jinli["PAID_SHARES()"], "phase": jinli["phase()"], "sold_paid": jinli["sold()"], "perShare_readable": "300,000 JINLI", "price_paid": "0.002 BNB",
    "startedAt": jinli["startedAt()"], "startedAtWib": "2026-11-02T01:55:26+07:00", "endsAtWib": "2026-11-05T01:55:26+07:00",
    "launched_LP": False, "pair": jinli["pair_raw"],
    "userSlotNote": "Slot open by read: freeClaimedById(user Agent ID)=false, mintedById=0, remainingQuota=9, balance 0 - NOT preview-verified (track-C leads are never previewed/minted).",
    "saleShape": "S2-VARIANT via identity delegation: contract IS the token (JINLI, 18 decimals, totalSupply on same contract) + claimFree() no-arg + freeClaimed/FREE_SHARES + identity() whose REGISTRY() reads 0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F on-chain, Sourcify exact_match.",
    "ageNote": "VERIFIED <=48h: startedAt() 2026-11-02 01:55:26 WIB, corroborated by first Transfer (initial supply) at 01:50:02 WIB, ~5 min before startedAt; Boltbook nira.ai post 02:06 WIB (free 553/3000 at post time, 1319/3000 at this run's verify) corroborates a launch-night window.",
    "xNote": "NO project X account found (web search found only generic Agent-ID material; Boltbook nira.ai post + jinli.tech site are discussion/site evidence, not a project X account) -> lead ONLY, NOT a candidate."}
biao = verify["TrackC-1646"]
tc["BIAO"] = {"address": "0x16469C174cd827A5e21f4bf3eE3711f2bB42e275", "status": "track-c-lead-reported-2026-11-02", "name": "BIAO", "symbol": "BIAO", "kind": "ERC20-sale-S2-variant",
    "freeClaimed": biao["freeClaimed()"], "FREE_SHARES": biao["FREE_SHARES()"], "freeRemaining": biao["FREE_SHARES()"] - biao["freeClaimed()"],
    "MAX_PAID": biao["MAX_PAID()"], "phase": biao["phase()"], "sold_paid": biao["sold()"], "perShare_readable": "50,000 BIAO", "price_paid": "0.002 BNB",
    "startedAt": biao["startedAt()"], "startedAtWib": "2026-11-02T02:01:06+07:00",
    "launched_LP": False, "pair": biao["pair()"],
    "userSlotNote": "Slot open by deduction stated plainly: freeClaimed() total = 0, so no Agent ID has claimed free yet, hence the user's per-user free flag must be false; a direct freeClaimedById(uint256) read was NOT completed because the numeric agentId encoding for this contract could not be resolved (its freeClaimedById takes uint256, not the bytes32 identityOf used by RuninAI/JUBAO) - NOT preview-verified (track-C leads are never previewed/minted). User is an Agent ID holder (registry balanceOf(user)=1, handle 'masgayut').",
    "saleShape": "S2-VARIANT direct: contract IS the token (BIAO, 18 decimals, totalSupply on same contract) + claimFree() no-arg + freeClaimed/FREE_SHARES + REGISTRY() reads 0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F on-chain, Sourcify exact_match.",
    "ageNote": "VERIFIED <=48h: startedAt() 2026-11-02 02:01:06 WIB, corroborated by first Transfer (initial supply) at the same timestamp (block 131101349); age ~14 min at verify.",
    "xNote": "NO project X account found (web search found only generic Agent-ID material) -> lead ONLY, NOT a candidate."}
tc["兕"] = {"address": "0x071f76c1868039e2f042Dca1890EcB0364D8494a", "status": "track-c-lead-reported-2026-11-02", "name": "兕", "symbol": "兕", "kind": "ERC20-sale-S2-variant",
    "FREE_POOL": 3000, "soldFree": 60, "freeRemaining": 2940, "TOTAL_CAP": 44444, "soldPaid": 0,
    "phase": None, "price_paid": "0.001 BNB (currentPrice)", "startTime": 1793559600, "startTimeWib": "2026-11-02T02:00:00+07:00", "deadlineWib": "2026-11-16T02:00:00+07:00",
    "launched_LP": False, "pair": "0x0000000000000000000000000000000000000000",
    "userSlotNote": "Slot open by read, with a stated caveat: freeQuotaOf=1 and freeUsedOf/freeUsedById/hasMintedById=0 under ALL FOUR label encodings tried (padded 'masgayut', keccak('masgayut'), keccak('masgayut.ai'), identityOf bytes32 0x9341...) - the same read standard used for 零元购; balance 0 - NOT preview-verified (track-C leads are never previewed/minted).",
    "saleShape": "S2-VARIANT (non-listed free-view names, stated plainly): contract IS the token (兕, 18 decimals, totalSupply on same contract) + freeMint(bytes32,bytes32) + freeQuotaOf/freeUsedById/freeUsedOf + REGISTRY() reads 0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F on-chain, Sourcify verified. Deviation vs strict S1/S2: free function is freeMint (not mint/mintFree/claimFree) and free views are freeQuotaOf/freeUsedById (not in the strict S1 list).",
    "ageNote": "VERIFIED <=48h: startTime() 2026-11-02 02:00:00 WIB; sale live (soldFree 60, soldPaid 0); age ~30 min at verification.",
    "xNote": "NO project X account found (contract-address web search returned only unrelated BscScan pages) -> lead ONLY, NOT a candidate."}
# --- pending claims ---
snap["pending_claims"]["binanceai.fun"].update({"launched": False, "totalShares_last": gi(read["TrackB_MINT"], "totalShares()"), "lastCheckBlock": READ_BLOCK, "lastCheckWib": READ_WIB})
snap["pending_claims"]["hive-pollen"].update({"launched": False, "pollenAgents": gi(read["Pollen_MINT"], "pollenAgents()"), "paidSold": gi(read["Pollen_MINT"], "paidSold()"),
    "pollenSlice_raw": str(gi(read["Pollen_MINT"], "pollenSlice()")), "pollenSlice_estimate": "~13,280 HIVE at 18 decimals (shrinks as more agents join; agentInfo claimable reads 0 pre-launch, so the slice is an estimate, not a fixed claimable)", "lastCheckBlock": READ_BLOCK, "lastCheckWib": READ_WIB})
snap["timestamp_wib"] = "2026-11-02T02:01:00+07:00"
json.dump(snap, open(HF + "onchain-snapshot.json", "w"), indent=1)
print("contracts:", len(snap["contracts"]), "track_c:", len(snap["track_c"]))
print("new:", [k for k in snap["contracts"] if k in ("Agents NormiePunks", "Medusine", "Hotpotsage", "Mummyrelic", "Ravenhex", "Orbitmarshal", "Kiln Agent", "Lighthouse Agent")])
print("new track_c:", [k for k in ("JINLI", "BIAO") if k in snap["track_c"]])
