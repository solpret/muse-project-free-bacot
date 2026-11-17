#!/usr/bin/env python3
"""Run 0131 snapshot update. Read-only except snapshot write."""
import json, copy
P="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/onchain-snapshot.json"
d=json.load(open(P))
C=d["contracts"]
READ_WIB="2026-11-02T01:34:17+07:00"; READ_BLK=131097717; INTERVAL=27.07
def vel(name, new_total, prev_rate, note_extra=""):
    old=C[name]; prev=old.get("totalSupply") or old.get("totalMinted")
    minted=new_total-prev
    rate=round(minted/INTERVAL,3)
    ratio=round(rate/prev_rate,2) if prev_rate else None
    passes = (ratio is not None and ratio>=1.5 and minted>=20)
    old["previousTotalSupply"]=prev; old["mintedInInterval"]=minted; old["intervalMinutes"]=INTERVAL
    old["currentRatePerMin"]=rate; old["previousRatePerMin"]=prev_rate
    old["velocityNote"]=f"Run 01:31 WIB: +{minted} tokens in ~{INTERVAL} min (01:07:13->{READ_WIB[11:19]}) = {rate}/min, ratio vs prior {prev_rate} = {ratio}x{' and >=20 tokens' if minted>=20 else ' and <20 tokens'}, so the velocity leg {'PASSES' if passes else 'still FAILS'}. Stored as new baseline."+note_extra
    old["velocityLegPasses"]=passes
    return old
# HIVE (inference)
h=C["HIVE Agents"]; vel("HIVE Agents",742,0.404)
h.update({"totalSupply":742,"freePctInference":74.2,"lastReadBlock":READ_BLK,"lastReadWib":READ_WIB})
h["velocityNote"]="Run 01:31 WIB: +14 tokens in ~27.07 min = 0.517/min, ratio vs prior 0.404/min = 1.28x and <20 tokens, so the velocity leg still FAILS (outcome unchanged vs 01:01 - no change report). Stored as new baseline."
# NFTs with freeClaimed views
updates={
 "Bubblebruin":(792,791,7777,0.259),
 "Zapcourier":(304,304,712,3.355),
 "Mothwraith":(270,270,869,2.76),
 "Cryonyx":(290,290,809,2.803),
 "Cathodex":(312,312,763,3.312),
 "Malabao":(283,283,844,3.142),
 "Voltabyte":(179,179,925,1.617),
 "Saturnin":(149,149,838,1.266),
 "Kirinova":(216,216,711,2.461),
 "Ghostbloom":(172,172,942,1.125),
 "Junepup":(192,192,724,1.336),
}
for nm,(tot,free,cap,prevrate) in updates.items():
    vel(nm,tot,prevrate)
    C[nm].update({"totalSupply":tot,"freeClaimed":free,"freePctVerified":round(free/cap*100,2),"lastReadBlock":READ_BLK,"lastReadWib":READ_WIB})
# Slimelings (velocity was passing, now fails)
s=C["Slimelings"]; vel("Slimelings",590,6.832)
s.update({"totalSupply":590,"mintedCount":581,"freeCount":577,"lastReadBlock":READ_BLK,"lastReadWib":READ_WIB})
s["velocityNote"]="Run 01:31 WIB: +229 tokens in ~27.07 min = 8.46/min, ratio vs prior 6.832/min = 1.24x (<1.5x), so the velocity leg now FAILS (was passing at 01:01). Free % still UNVERIFIED and X still unverified, so this leg flip is recorded here only, NOT a promotion and NOT a candidate - remains EARLY only, never previewed/minted. Stored as new baseline."
s["velocityLegPasses"]=False
# Vorpry
v=C["Vorpry"]; vel("Vorpry",180,1.688)
v.update({"totalSupply":180,"totalMinted":180,"openLeft":1623,"lastReadBlock":READ_BLK,"lastReadWib":READ_WIB})
# Mirror Pair unchanged
C["Mirror Pair"].update({"lastReadBlock":READ_BLK,"lastReadWib":READ_WIB})
# REMOVALS: Compass, Windmill, Fountain - free quota exhausted, now paid-only
removed={}
for nm in ("Compass Agent","Windmill Agent","Fountain Agent"):
    if nm in C: removed[nm]=C.pop(nm)
d["_removed_0131"]=removed
# NEW EARLY wave 5
VWIB="2026-11-02T01:40:33+07:00"; VBLK=131098540
wave={
 "Gourdwick":("0x0ae19c56570d1d8b7878c309c13847a737738ead","GOURDW",150,868,1086,131094644,"2026-11-02 01:10:48 WIB",150,150),
 "Kitsunaru":("0x96838f487f3551db0a25a401ab221843b72b715e","KITSUN",139,865,1082,131094661,"2026-11-02 01:10:56 WIB",139,139),
 "Nightsable":("0xc4f2797f050835daf3d24c1764eca60ac4168f21","NIGHTS",138,794,993,131094669,"2026-11-02 01:10:59 WIB",136,136),
 "Lensorb":("0x1edfd1e6c6b132e88f5b09b1dbe025037b5b0539","LENSOR",123,776,971,131094679,"2026-11-02 01:11:04 WIB",122,122),
 "Nimaluo":("0xd531f1b8b56882c48ab5fe9be8c4855a54c90f26","NIMALU",153,828,1035,131094697,"2026-11-02 01:11:12 WIB",153,153),
}
for nm,(addr,sym,tot,free_sup,max_sup,fb,fts,logs,minters) in wave.items():
    C[nm]={
     "address":addr,"status":"early-lead-reported-2026-11-02","name":nm,"symbol":sym,"kind":"ERC721",
     "totalSupply":tot,"freeClaimed":tot,"FREE_SUPPLY":free_sup,"MAX_SUPPLY":max_sup,
     "freePctVerified":round(tot/free_sup*100,2),"mintOpen":True,
     "userMintedBy":0,"userFreeUsed":0,"userBalance":0,
     "userSlotNote":"Slot open by read: mintedBy(user)=0, freeUsed(user)=0, quote(user,1)=0, balance 0 - NOT preview-verified (early leads are never previewed).",
     "firstSeenBlock":fb,"scanMints":logs,"scanMinters":minters,
     "lastReadBlock":VBLK,"lastReadWib":VWIB,"xVerified":False,"velocityVerified":False,
     "launchNote":f"First mint verified on-chain: first Transfer-from-zero at block {fb}, {fts} (Ankr getLogs address-filtered from block 131060000; {logs} logs in range vs totalSupply {tot} at verify time - Nightsable/Lensorb logs trail supply by 2/1, stated plainly, first block still verified); no project-stated launch time found; Sourcify verifiedAt is verification time, NOT launch time. First-seen by this job in run 01:31 WIB via Boltbook agata.ai post + Sourcify feed.",
     "baselineNote":"EARLY lead reported once 2026-11-02 run 01:31 WIB. Never auto-minted/previewed. Agent-shape verified: Sourcify ABI (mint + quote + freeClaimed/freeFor/freeLeft/freeUsed + FREE_SUPPLY) and AGENT_ID() reads the registry 0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F on-chain. Free % far below 50%; X unverified (Boltbook discussion exists via the agata.ai wave post, but no project X account found); velocity not yet computable (first baseline stored this run).",
     "previousTotalSupply":None,"mintedInInterval":None,"intervalMinutes":None,"currentRatePerMin":None,"previousRatePerMin":None,
     "velocityNote":"First baseline stored run 01:31 WIB; no previous rate yet, so velocity leg is NOT passed on velocity alone.",
    }
# pending claims
d["pending_claims"]["binanceai.fun"].update({"totalShares_last":3104,"lastCheckBlock":READ_BLK,"lastCheckWib":READ_WIB})
hp=d["pending_claims"]["hive-pollen"]; hp.update({"pollenAgents":7522,"pollenSlice_raw":"13294336612603031108747","pollenSlice_estimate":"~13,294 HIVE at 18 decimals (shrinks as more agents join; agentInfo claimable reads 0 pre-launch, so the slice is an estimate, not a fixed claimable)","paidSold":1009,"lastCheckBlock":READ_BLK,"lastCheckWib":READ_WIB})
# track_c updates
tc=d["track_c"]
tc["BNBbaby"].update({"sharesMinted":7518,"freeMinted":7243,"paidShares":275,"lastCheckBlock":READ_BLK,"lastCheckWib":READ_WIB})
tc["DOG"].update({"sharesMinted":950,"lastCheckBlock":READ_BLK,"lastCheckWib":READ_WIB})
tc["BNBPIG"].update({"sharesMinted":3529,"freeMinted":3394,"paidShares":135,"lastCheckBlock":READ_BLK,"lastCheckWib":READ_WIB})
tc["SAMBARIO"].update({"cardsSold":184,"freeCardsRemaining":3149,"lastCheckBlock":READ_BLK,"lastCheckWib":READ_WIB})
tc["a7Be"].update({"sharesMinted":351,"freeSharesMinted":341,"lastCheckBlock":READ_BLK,"lastCheckWib":READ_WIB})
tc["NIUBI"].update({"sharesMinted":34,"freeMinted":33,"lastCheckBlock":READ_BLK,"lastCheckWib":READ_WIB})
tc["QILIN"].update({"cardsSold":4710,"freeCardsRemaining":337,"lastCheckBlock":READ_BLK,"lastCheckWib":READ_WIB})
tc["SAFU Tower"].update({"freeClaimed_total":4444,"lastCheckBlock":READ_BLK,"lastCheckWib":READ_WIB})
tc["零元购"].update({"soldFree":72,"freeRemaining":1928,"totalSold":73,"soldPaid":1,"lastCheckBlock":READ_BLK,"lastCheckWib":READ_WIB})
# NEW track-C leads
tc["RuninAI"]={
 "address":"0xfB50746BCc9D585AEb49cd410Fa0100b657ce9e6","status":"track-c-lead-reported-2026-11-02","name":"RuninAI","symbol":"RUNINAI","kind":"ERC20-sale-S2-variant",
 "freeClaimed":3025,"freeShares":4444,"freeRemaining":1419,"maxShares":5000,"phase":1,"sold_paid":99,
 "perShare_raw":"50000000000000000000000","perShare_readable":"50,000 RUNINAI",
 "startedAt":1793552290,"startedAtWib":"2026-11-01T23:58:10+07:00","endsAtWib":"2026-11-05T23:58:10+07:00","launched_LP":False,"pair":"0x0000000000000000000000000000000000000000",
 "userSlotNote":"Slot open by read: freeClaimedById(user Agent ID)=false, mintedById=0, remainingFor(user)=9, freeTokensOf(user)=0, balance 0 - NOT preview-verified (track-C leads are never previewed/minted). Quota semantics: quotaPerId reads 9, so the exact free-share count for the user is NOT asserted as 1 - only that the slot is unused.",
 "xNote":"No project X account found (web search for RuninAI/contract found only generic Agent-ID material; Boltbook discussion exists via piash55.ai post + comment rechecks, but discussion alone without a project X account does not make a candidate). Project site named in the post: runinai.com (not fetched for a site inspection - lead only, no inspection needed for a lead).",
 "shapeNote":"S2-VARIANT (deviation stated plainly): contract IS the token (RuninAI/RUNINAI, 18 decimals, totalSupply on the same contract) + claimFree() (no-arg) + free views (freeClaimed, freeShares, freeClaimedById) + Agent ID gate via DELEGATION: identity() returns 0x135e3f94813198f345f09eaa79aae2c936aaded1, whose REGISTRY() reads 0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F on-chain and identityOf(user) is non-zero. Deviation vs strict S2: free function is claimFree(), not mintFree(); gate is via the identity contract, not a registry function on the token itself. launched()=false refers to the LP launch (pair is still the zero address), NOT sale openness - the sale is claiming (freeClaimed rose 1,727 -> 3,025 across the Boltbook post and this run's reads).",
 "baselineNote":"TRACK-C LEAD reported once 2026-11-02 run 01:31 WIB. Never auto-minted/previewed (lead only, NOT a candidate: no project X account). Source: Boltbook piash55.ai post (11m before the run) + comment rechecks + Sourcify-verified ABI + fresh on-chain reads. Age VERIFIED <=48h via on-chain startedAt 2026-11-01 23:58:10 WIB (~1.8h at verification), corroborated by the first Transfer (initial supply) at the same timestamp.",
 "lastCheckBlock":131098540,"lastCheckWib":VWIB}
for nm,addr,fc,started in (("JUBAO","0x1ed3BF35e4DA25b1289C27ddbD82f0A38DDCee8b",15,1793549525),("ZCMAO","0x8362e6a5F38427d8d719EA47f08890784F6023DC",16,1793549494),("JINLONG","0x2Df4Ef534cbBe1a8F647e24D0f8C75ECe74D8288",15,1793549461)):
    import datetime
    sw=datetime.datetime.fromtimestamp(started, datetime.timezone(datetime.timedelta(hours=7))).strftime("%Y-%m-%dT%H:%M:%S+07:00")
    old=tc.get(nm,{})
    old.update({"status":"track-c-lead-reported-2026-11-02","freeClaimed_total":fc,"freeRemaining":4444-fc,
     "shapeNote":"S2-VARIANT, PROMOTED from checked-not-a-lead by this run's deeper verification (supersedes the 23:31 WIB rejection, which checked only the token contract's own ABI/bytecode for a registry reference): contract IS the token + claimFree() + freeClaimed/FREE_SHARES + Agent ID gate via DELEGATION: identity() returns an identity contract whose REGISTRY() reads 0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F on-chain and identityOf(user) is non-zero. launched()=false refers to the LP launch (pair not yet formed), NOT sale openness - the sale is claiming (freeClaimed rose from 6-7 to "+str(fc)+").",
     "ageNote":f"VERIFIED <=48h (this run): on-chain startedAt {sw} (~2.6h at verification), corroborated by the first Transfer (initial supply) within seconds of startedAt. Previously UNVERIFIED because no first-mint verification had been run; now verified.",
     "userSlotNote":"Slot open by read: freeClaimedById(user Agent ID)=false, mintedById=0, balance 0 - NOT preview-verified (track-C leads are never previewed/minted).",
     "xNote":"No project X account found in this run's searches - lead only, NOT a candidate.",
     "boundary":"LEAD ONLY. NEVER auto-minted, NEVER previewed. Track-C auto-mint does NOT trigger: lead, not candidate (no X account).",
     "lastCheckBlock":131099607,"lastCheckWib":"2026-11-02T01:47:00+07:00"})
    tc[nm]=old
d["timestamp_wib"]="2026-11-02T01:31:00+07:00"
d["note"]=d.get("note","")+" Run 2026-11-02 01:31 WIB: HIVE 742 (+14, velocity still FAILS 1.28x, <20 tokens - unchanged, still strong lead, NOT a candidate: X unverified), Bubblebruin 791/7777 = 10.17% (EARLY, user slot USED), Zapcourier/Mothwraith/Cryonyx/Cathodex/Malabao free % 42.7/31.1/35.8/40.9/33.5% (all still below 50% strong leg, velocity FAILING, X unverified - remain EARLY), Slimelings velocity now FAILS (1.24x, was passing at 01:01; free % unverified + X unverified - NOT promoted, remains EARLY), Voltabyte/Saturnin/Kirinova/Ghostbloom/Junepup velocity FAILING (0.75/1.17/1.10/1.05/0.97x) with free % 19.4/17.8/30.4/18.3/26.5% (X unverified - remain EARLY), Vorpry velocity FAILING 1.18x (free % unverified, X unverified - remains EARLY), Mirror Pair still 2 pairs. REMOVED (reported once + removed): Compass Agent, Windmill Agent, Fountain Agent - free quota exhausted: totalMinted 327/327/446 exceeds FREE_SUPPLY 324/324/435 and currentPrice()/costFor(1) moved from 0 to 0.0005 BNB, so the user's next mint would be PAID, not free (user mintedBy still 0 - the free lane closed for everyone, not a used slot). NEW: 5 EARLY leads (Gourdwick, Kitsunaru, Nightsable, Lensorb, Nimaluo - wave 1511-1515, deployer 0xa054..., first mints 01:10:48-01:11:12 WIB verified, AGENT_ID()=registry, slot open, free % 15.9-18.5%, X unverified - never previewed/minted) + 4 NEW Track-C LEADS (RuninAI 0xfB50... - free 3025/4444, startedAt 2026-11-01 23:58:10 WIB, gate via identity-contract delegation, NO project X account; JUBAO/ZCMAO/JINLONG - promoted from checked-not-a-lead by identity-delegation verification, free 15/16/15 of 4444, startedAt ~23:11-23:12 WIB, NO project X account - all lead only, never previewed/minted). BNBbaby/DOG/BNBPIG/SAMBARIO/a7Be/零元购 still LEAD only (slot open, no X; no auto-mint); NIUBI still watchlist-only (age unverified); QILIN user slot still used; SAFU freeClaimed total 4444. binanceai.fun still pending (launched false, totalShares 3104); hive-pollen still pending (launched false, pollenAgents 7522, slice ~13,294). SCAN: see run log (in progress at snapshot write; watermark NOT advanced in this update - see run log for final scan outcome)."
json.dump(d, open(P,"w"), indent=1)
print("snapshot updated; contracts:", len(d["contracts"]), "track_c:", len(d["track_c"]), "removed:", list(removed.keys()))
