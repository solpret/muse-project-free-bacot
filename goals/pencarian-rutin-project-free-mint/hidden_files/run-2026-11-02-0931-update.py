import json, shutil
B="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
shutil.copy(B+"onchain-snapshot.json", B+"onchain-snapshot-2026-11-02-0931.bak.json")
snap=json.load(open(B+"onchain-snapshot.json"))
r=json.load(open(B+"run-2026-11-02-0931-read.json"))
READ_BLOCK=r["block"]; READ_WIB="2026-11-02T09:47:10+07:00"; INTERVAL=19.73
def iv(d,k):
    try: return d[k]["int"]
    except: return None
def words(d,k):
    try: return d[k].get("words")
    except: return None
for name,e in snap["contracts"].items():
    d=r.get(name)
    if not d: continue
    ts=iv(d,"totalSupply()"); tm=iv(d,"totalMinted()")
    fc=iv(d,"freeClaimed()"); fm=iv(d,"freeMinted()")
    fs=iv(d,"FREE_SUPPLY()") or iv(d,"FREE_CAP()")
    cur=ts if ts is not None else tm
    prev=e.get("totalSupply") if e.get("totalSupply") is not None else e.get("totalMinted")
    if cur is not None: e["previousTotalSupply"]=prev
    if ts is not None: e["totalSupply"]=ts
    if tm is not None: e["totalMinted"]=tm
    if fc is not None: e["freeClaimed"]=fc
    if fm is not None: e["freeMinted"]=fm
    if fs is not None:
        if iv(d,"FREE_SUPPLY()") is not None: e["FREE_SUPPLY"]=fs
        if iv(d,"FREE_CAP()") is not None: e["FREE_CAP"]=fs
    if fc is not None and fs: e["freePctVerified"]=round(100*fc/fs,2)
    elif fm is not None and fs: e["freePctVerified"]=round(100*fm/fs,2)
    mb=iv(d,"mintedBy(address)"); fu=iv(d,"freeUsed(address)"); bal=iv(d,"balanceOf(address)")
    if mb is not None: e["userMintedBy"]=mb
    if fu is not None: e["userFreeUsed"]=fu
    if bal is not None: e["userBalance"]=bal
    # velocity
    if cur is not None and prev is not None:
        delta=cur-prev; e["mintedInInterval"]=delta; e["intervalMinutes"]=INTERVAL
        rate=round(delta/INTERVAL,3); prev_rate=e.get("currentRatePerMin")
        e["previousRatePerMin"]=prev_rate; e["currentRatePerMin"]=rate
        if prev_rate is None:
            e["velocityLegPasses"]=False
            e["velocityNote"]=f"Run 09:31 WIB (read block {READ_BLOCK}): +{delta} tokens in ~{INTERVAL} min = {rate}/min; no previous rate yet (first rate stored) -> velocity leg NOT computable, FAILS."
        else:
            ratio=round(rate/prev_rate,2) if prev_rate else None
            passes=(delta>=20 and rate>=1.5*prev_rate)
            e["velocityLegPasses"]=passes
            e["velocityNote"]=f"Run 09:31 WIB (read block {READ_BLOCK}): +{delta} tokens in ~{INTERVAL} min = {rate}/min, ratio vs prior {prev_rate} = {ratio}x -> velocity leg {'PASSES' if passes else 'FAILS'}."
    e["lastReadBlock"]=READ_BLOCK; e["lastReadWib"]=READ_WIB
# Mirror Pair special
mp=snap["contracts"].get("Mirror Pair")
if mp:
    mp["lastReadBlock"]=READ_BLOCK; mp["lastReadWib"]=READ_WIB
    mp["velocityNote"]="Run 09:31 WIB: mintedPairs still 2 (was 2) - no new pair; velocity not computable."
# New early leads
snap["contracts"]["Strawhex"]={
 "address":"0x61C360b0fA3fef5c61728756e0fb574c66D73663","status":"early-lead-reported-2026-11-02","name":"Strawhex","symbol":"STRWHX","kind":"ERC721",
 "totalSupply":57,"freeClaimed":57,"FREE_SUPPLY":954,"MAX_SUPPLY":1193,"freePctVerified":5.97,"mintOpen":True,
 "userMintedBy":0,"userFreeUsed":0,"userBalance":0,
 "userSlotNote":"Slot open by read: mintedBy(user)=0, freeUsed(user)=0, quote(user,1)=0, balance 0 - NOT preview-verified (early leads are never previewed).",
 "firstSeenBlock":131163645,"scanMints":54,"scanMinters":54,"lastReadBlock":131163645,"lastReadWib":"2026-11-02T09:48:24+07:00",
 "xVerified":False,"velocityVerified":False,
 "launchNote":"First mint verified on-chain: first Transfer-from-zero at block 131163645, 2026-11-02 09:48:24 WIB (Ankr getLogs as module, address-filtered from block 131060000; 54 logs = totalSupply 54-57 range at verify time, so all mints ever are in range; 54 distinct minters). Age ~minutes at verify time, VERIFIED ≤48h. No project-stated launch time found; Sourcify verifiedAt 2026-11-02T02:48:39Z (verification time, NOT launch time). First-seen by this job in run 09:31 WIB via Sourcify feed.",
 "baselineNote":"EARLY lead reported once 2026-11-02 run 09:31 WIB. Never auto-minted/previewed. Agent-shape verified: Sourcify exact_match ABI (mint + quote + freeClaimed/freeFor/freeLeft/freeUsed + FREE_SUPPLY + AGENT_ID) and AGENT_ID() reads the registry 0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F on-chain. Free % 5.97, far below 50%; X unverified (web search found no project X account/discussion); velocity not yet computable (first baseline stored this run).",
 "supplyView":"totalSupply"}
snap["contracts"]["Voltmohawk"]={
 "address":"0x06aB825D14454174819E1c08a6E72C4b5bBF78fE","status":"early-lead-reported-2026-11-02","name":"Voltmohawk","symbol":"VOLTMH","kind":"ERC721",
 "totalSupply":59,"freeClaimed":59,"FREE_SUPPLY":956,"MAX_SUPPLY":1195,"freePctVerified":6.17,"mintOpen":True,
 "userMintedBy":0,"userFreeUsed":0,"userBalance":0,
 "userSlotNote":"Slot open by read: mintedBy(user)=0, freeUsed(user)=0, quote(user,1)=0, balance 0 - NOT preview-verified (early leads are never previewed).",
 "firstSeenBlock":131163664,"scanMints":56,"scanMinters":56,"lastReadBlock":131163664,"lastReadWib":"2026-11-02T09:48:33+07:00",
 "xVerified":False,"velocityVerified":False,
 "launchNote":"First mint verified on-chain: first Transfer-from-zero at block 131163664, 2026-11-02 09:48:33 WIB (Ankr getLogs as module, address-filtered from block 131060000; 56 logs in range vs totalSupply 59 at verify time - logs trail supply by 3, stated plainly, first block still verified; 56 distinct minters). Age ~minutes at verify time, VERIFIED ≤48h. No project-stated launch time found; Sourcify verifiedAt 2026-11-02T02:48:39Z (verification time, NOT launch time). First-seen by this job in run 09:31 WIB via Sourcify feed.",
 "baselineNote":"EARLY lead reported once 2026-11-02 run 09:31 WIB. Never auto-minted/previewed. Agent-shape verified: Sourcify exact_match ABI (mint + quote + freeClaimed/freeFor/freeLeft/freeUsed + FREE_SUPPLY + AGENT_ID) and AGENT_ID() reads the registry 0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F on-chain. Free % 6.17, far below 50%; X unverified (web search found no project X account/discussion); velocity not yet computable (first baseline stored this run).",
 "supplyView":"totalSupply"}
# DROID track-C watchlist-only
snap.setdefault("track_c",{})["DROID"]={
 "sale":"0xFcF6388DD3bcC674c095273aB479C7e54dd5E177","token":"0x89d5715b8e4147C82aD8886b952c2A9Bd2f2F00A","site":"https://droidbnb.vercel.app/",
 "status":"watchlist-only-age-slot-unverified-2026-11-02",
 "saleShape":"NOT VERIFIED: mint + token contracts are Sourcify-UNVERIFIED (404), so no verified ABI exists to pass S1/S2. Concrete partial evidence only: claimFree() selector 0xf366afc9 per Boltbook post, FREE_SHARES()=2000, freeMinted()=168, paused()=0, token() reads the DROID token address, registry bytes present in mint bytecode (weak discriminator per known limit, 81% hit rate).",
 "FREE_SHARES":2000,"freeMinted":168,"poolRemainingEstimate":1832,
 "userSlot":{"freeUsed":0,"note":"freeUsed(user)=0 hints slot open, but freeClaimed(address)/claimedShares/hasClaimed/quote/cost all REVERT without an ABI, so the user slot is NOT verified - stated plainly."},
 "ageNote":"UNVERIFIED: no project-stated launch time found; site /skill.md, /launch.json, /api/stats, /api/verify all 404; first-claim time not verified on-chain. Boltbook post by aqu.ai (~09:42 WIB, 'klaim gratis 50.000.000 lewat claimFree, pool buka di 5.000 share') is discussion evidence only, NOT launch verification - and its '5.000 share' figure conflicts with on-chain FREE_SHARES()=2000, stated plainly.",
 "xNote":"X set aside for track C (reference only); no project X account checked as a gate.",
 "boundary":"WATCHLIST ONLY. Never reported as a lead, never previewed/minted. Promotes to lead only on verified sale shape + free pool + user slot + verified age <=48h.",
 "lastCheckBlock":131164692,"lastCheckWib":"2026-11-02T10:00:00+07:00"}
# Pending claims
pc=snap.setdefault("pending_claims",{})
if "binanceai.fun" in pc:
    pc["binanceai.fun"]["totalShares"]=3108; pc["binanceai.fun"]["totalShares_last"]=3108
    pc["binanceai.fun"]["launched"]=False; pc["binanceai.fun"]["lastCheckBlock"]=READ_BLOCK; pc["binanceai.fun"]["lastCheckWib"]=READ_WIB
if "hive-pollen" in pc:
    pc["hive-pollen"]["pollenAgents"]=7644; pc["hive-pollen"]["paidSold"]=1024
    pc["hive-pollen"]["pollenSlice_raw"]="13082155939298796441653"; pc["hive-pollen"]["pollenSlice_estimate"]="~13,082 HIVE at 18 decimals (shrinks as more agents join)"
    pc["hive-pollen"]["launched"]=False; pc["hive-pollen"]["lastCheckBlock"]=READ_BLOCK; pc["hive-pollen"]["lastCheckWib"]=READ_WIB
json.dump(snap, open(B+"onchain-snapshot.json","w"), indent=1)
print("contracts now", len(snap["contracts"]), "track_c", len(snap["track_c"]))
for n in ["Cryonyx","Malabao","Slimelings","Vesperfang","Ioforge","Krakenbo"]:
    e=snap["contracts"][n]; print(n, e.get("totalSupply"), e.get("freePctVerified"), e.get("velocityNote"))
