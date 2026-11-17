import json, pathlib, copy
base=pathlib.Path.home()/"workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
snap=json.load(open(base/"onchain-snapshot.json"))
def load(f):
    try: return json.load(open(base/f))
    except Exception: return {}
read=load("run-2026-11-02-0701-read.json"); extra=load("run-2026-11-02-0701-read-extra.json"); cilok=load("run-2026-11-02-0701-cilok.json"); v2=load("run-2026-11-02-0701-verify2.json"); v3=load("run-2026-11-02-0701-verify3.json"); verify=load("run-2026-11-02-0701-verify.json")
def gi(d, *names):
    for n in names:
        v=d.get(n) if isinstance(d,dict) else None
        if isinstance(v, dict): v=v.get("int")
        if v is not None: return v
    return None
# (source, key, block, wib, interval_min)
GROUPS={
 "main": (read, 131142029, "2026-11-02T07:06:15+07:00", 32.92),
 "extra": (extra, 131142202, "2026-11-02T07:07:33+07:00", 33.15),
 "cilok": (cilok, 131142261, "2026-11-02T07:07:59+07:00", 32.97),
 "v2": (v2, 131142281, "2026-11-02T07:08:08+07:00", 33.07),
 "v3": (v3, 131142288, "2026-11-02T07:08:12+07:00", 32.50),
}
MAP={
 "HIVE Agents": ("main","HIVE"), "Bubblebruin": ("main","Bubblebruin"), "Zapcourier": ("main","Zapcourier"),
 "Mothwraith": ("main","Mothwraith"), "Cryonyx": ("main","Cryonyx"), "Cathodex": ("main","Cathodex"), "Malabao": ("main","Malabao"),
 "Slimelings": ("main","Slimelings"), "Voltabyte": ("main","Voltabyte"), "Saturnin": ("main","Saturnin"), "Kirinova": ("main","Kirinova"),
 "Ghostbloom": ("main","Ghostbloom"), "Junepup": ("main","Junepup"), "Vorpry": ("main","Vorpry"),
 "Gourdwick": ("main","Gourdwick"), "Kitsunaru": ("main","Kitsunaru"), "Nightsable": ("main","Nightsable"), "Lensorb": ("main","Lensorb"), "Nimaluo": ("main","Nimaluo"),
 "Agents NormiePunks": ("extra","Agents NormiePunks"), "Medusine": ("extra","Medusine"), "Hotpotsage": ("extra","Hotpotsage"), "Mummyrelic": ("extra","Mummyrelic"), "Ravenhex": ("extra","Ravenhex"), "Orbitmarshal": ("extra","Orbitmarshal"),
 "Cilok Cats: White Paw Genesis": ("cilok","Cilok"), "Gearpixel": ("cilok","Gearpixel"), "Skelebop": ("cilok","Skelebop"),
 "Orbitty": ("main","Orbitty"), "Neonwolfy": ("main","Neonwolfy"), "Sphinxel": ("main","Sphinxel"), "Witchlet": ("main","Witchlet"), "Venuspi": ("main","Venuspi"), "Neonraven": ("main","Neonraven"), "Griffinko": ("main","Griffinko"), "Tangpinku": ("main","Tangpinku"),
 "NULLSECTOR": ("v2","NULLSECTOR"), "Onimaru": ("v2","Onimaru"), "Rootlinks": ("v2","Rootlinks"),
 "PIXEL FROGS": ("v3","Bd14"), "Orchard Agent": ("v3","D1dc"),
}
for name,(grp,key) in MAP.items():
    if name not in snap["contracts"]: continue
    src,blk,wib,interval = GROUPS[grp][0], GROUPS[grp][1], GROUPS[grp][2], GROUPS[grp][3]
    d=src.get(key,{})
    old=snap["contracts"][name]
    tot=gi(d, "totalSupply()", "totalSupply", "totalMinted()", "totalMinted")
    free=gi(d, "freeClaimed()", "freeClaimed", "totalFreeMinted()", "freeMinted()")
    cap=gi(d, "FREE_SUPPLY()", "freeCap()", "FREE_CAP()", "freeCap")
    oldtot=old.get("totalSupply", old.get("totalMinted"))
    prev_rate=old.get("currentRatePerMin")
    old["previousTotalSupply"]=oldtot
    if tot is not None:
        # keep the field name the contract used
        if "totalSupply" in old: old["totalSupply"]=tot
        elif "totalMinted" in old: old["totalMinted"]=tot
        else: old["totalSupply"]=tot
    if free is not None and "freeClaimed" in old: old["freeClaimed"]=free
    if free is not None and old.get("freeMinted") is not None: old["freeMinted"]=free
    if cap is not None:
        if "FREE_SUPPLY" in old: old["FREE_SUPPLY"]=cap
        if "freeCap" in old: old["freeCap"]=cap
        if "FREE_CAP" in old: old["FREE_CAP"]=cap
    if free is not None and cap:
        old["freePctVerified"]=round(free/cap*100,2)
    minted = (tot-oldtot) if (tot is not None and oldtot is not None) else None
    rate = (minted/interval) if minted is not None else None
    passes = bool(rate is not None and prev_rate is not None and minted is not None and minted>=20 and rate>=1.5*prev_rate)
    # Mirror Pair / special: skip velocity (handled below)
    old["mintedInInterval"]=minted; old["intervalMinutes"]=round(interval,2)
    old["previousRatePerMin"]=prev_rate; old["currentRatePerMin"]=round(rate,3) if rate is not None else None
    old["velocityLegPasses"]=passes
    old["velocityNote"]=f"Run 07:01 WIB: +{minted} tokens in ~{interval:.2f} min = {rate:.3f}/min" if rate is not None else "Run 07:01 WIB: velocity not computable"
    if passes: old["velocityNote"]+=f", ratio vs prior {prev_rate} = {rate/prev_rate:.2f}x, so the velocity leg PASSES."
    else: old["velocityNote"]+=f", so the velocity leg still FAILS."
    old["lastReadBlock"]=blk; old["lastReadWib"]=wib
# v2 freeMinted plain keys
snap["contracts"]["Onimaru"]["freeMinted"]=993; snap["contracts"]["Onimaru"]["freePctVerified"]=round(993/3000*100,2)
snap["contracts"]["Rootlinks"]["freeMinted"]=259; snap["contracts"]["Rootlinks"]["freePctVerified"]=round(259/1000*100,2)
# Slimelings special fields
sl=snap["contracts"]["Slimelings"]; sl["mintedCount"]=1805; sl["freeCount"]=1791
# Vorpry
vp=snap["contracts"]["Vorpry"]; vp["openLeft"]=1564
# Mirror Pair unchanged pairs
mp=snap["contracts"]["Mirror Pair"]; mp["lastReadBlock"]=131142029; mp["lastReadWib"]="2026-11-02T07:06:15+07:00"; mp["velocityNote"]="Run 07:01 WIB: mintedPairs still 2 (was 2) - no new pair; velocity not computable."
# Hachiko minted
h=snap["contracts"]["Hachiko"]
h.update({"status":"minted-by-user-2026-11-02","totalSupply":914,"freeClaimed":914,"freePctVerified":91.4,"mintOpen":True,"userBalance":1,
 "userSlotNote":"Slot USED by strong-lead direct mint 2026-11-02 ~07:04 WIB (tx 0xd697bb3e5d19d56b4575ee4bf77033ef26093e1465c346783e98d1d2db0ff642, token #839); do not re-report as slot change",
 "mintTx":"0xd697bb3e5d19d56b4575ee4bf77033ef26093e1465c346783e98d1d2db0ff642","mintBlock":131141784,"mintGas":141831,"mintTokenId":839,
 "lastReadBlock":131142288,"lastReadWib":"2026-11-02T07:08:12+07:00","mintedInInterval":None,"intervalMinutes":None,"currentRatePerMin":None,"previousRatePerMin":None,"velocityLegPasses":False,
 "velocityNote":"Run 07:01 WIB: minted-by-user (strong-lead direct mint this run); velocity no longer tracked. Fresh totalSupply 914 at v3 block 131142288 (848 at post-mint verify, block 131141784); user slot USED (mintedByAgent 1, freeUsedByAgent 1, balance 1, ownerOf #839 = user wallet, receipt status 1)."})
# Removals
for gone in ["BINANCE HACK","Meadow Agent","Volcano Agent"]:
    snap["contracts"].pop(gone, None)
# New early leads
snap["contracts"]["GrimHarvest"]={
 "address":"0xC43Fc6F38629c39642C8E0EDEB7F647866321699","status":"early-lead-reported-2026-11-02","name":"GrimHarvest","symbol":"GRIM","kind":"ERC721",
 "totalSupply":463,"freeClaimed":435,"FREE_SUPPLY":990,"MAX_SUPPLY":1415,"freePctVerified":43.94,"mintOpen":True,
 "userMintedBy":0,"userFreeUsed":0,"userBalance":0,
 "userSlotNote":"Slot open by read: mintedBy(user)=0, freeUsed(user)=0, freeLeft(user)=1, quote(user,1)=0, balance 0 - NOT preview-verified (early leads are never previewed).",
 "firstSeenBlock":130968988,"scanMints":463,"scanMinters":435,"lastReadBlock":131142332,"lastReadWib":"2026-11-02T07:08:31+07:00",
 "xVerified":False,"velocityVerified":False,
 "launchNote":"First mint verified on-chain: first Transfer-from-zero at block 130968988, 2026-11-01 09:28:06 WIB (Ankr getLogs full range from block 130900000; 463 logs = totalSupply 463, so all mints ever are in range); no project-stated launch time found; Sourcify verifiedAt 2026-11-02T00:06:32Z (verification time, NOT launch time). First-seen by this job in run 07:01 WIB via Sourcify feed.",
 "baselineNote":"EARLY lead reported once 2026-11-02 run 07:01 WIB. Never auto-minted/previewed. Agent-shape verified: Sourcify ABI (mint + quote + freeClaimed/freeFor/freeLeft/freeUsed + FREE_SUPPLY) and AGENT_ID() reads the registry 0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F on-chain. Free % 43.94%, below 50%; X unverified; velocity not yet computable (first baseline stored this run).",
 "previousTotalSupply":None,"mintedInInterval":None,"intervalMinutes":None,"currentRatePerMin":None,"previousRatePerMin":None,"velocityLegPasses":False,
 "velocityNote":"Run 07:01 WIB: first baseline stored (totalSupply 463); velocity not yet computable."}
snap["contracts"]["NightshadeClub"]={
 "address":"0x2C027F14d36a080E5e058CF39407EAc2503B90Cc","status":"early-lead-reported-2026-11-02","name":"NightshadeClub","symbol":"NSHD","kind":"ERC721",
 "totalSupply":488,"freeClaimed":446,"FREE_SUPPLY":983,"MAX_SUPPLY":1405,"freePctVerified":45.37,"mintOpen":True,
 "userMintedBy":0,"userFreeUsed":0,"userBalance":0,
 "userSlotNote":"Slot open by read: mintedBy(user)=0, freeUsed(user)=0, freeLeft(user)=1, quote(user,1)=0, balance 0 - NOT preview-verified (early leads are never previewed).",
 "firstSeenBlock":130968970,"scanMints":488,"scanMinters":446,"lastReadBlock":131142332,"lastReadWib":"2026-11-02T07:08:31+07:00",
 "xVerified":False,"velocityVerified":False,
 "launchNote":"First mint verified on-chain: first Transfer-from-zero at block 130968970, 2026-11-01 09:27:57 WIB (Ankr getLogs full range from block 130900000; 488 logs = totalSupply 488, so all mints ever are in range); no project-stated launch time found; Sourcify verifiedAt 2026-11-02T00:06:23Z (verification time, NOT launch time). First-seen by this job in run 07:01 WIB via Sourcify feed.",
 "baselineNote":"EARLY lead reported once 2026-11-02 run 07:01 WIB. Never auto-minted/previewed. Agent-shape verified: Sourcify ABI (mint + quote + freeClaimed/freeFor/freeLeft/freeUsed + FREE_SUPPLY) and AGENT_ID() reads the registry 0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F on-chain. Free % 45.37%, below 50%; X unverified; velocity not yet computable (first baseline stored this run).",
 "previousTotalSupply":None,"mintedInInterval":None,"intervalMinutes":None,"currentRatePerMin":None,"previousRatePerMin":None,"velocityLegPasses":False,
 "velocityNote":"Run 07:01 WIB: first baseline stored (totalSupply 488); velocity not yet computable."}
snap["contracts"]["TheWickedVault"]={
 "address":"0x2760DB0Df38edA84Ce41710A95fBE1734C3F8F41","status":"early-lead-reported-2026-11-02","name":"TheWickedVault","symbol":"WICK","kind":"ERC721",
 "totalSupply":377,"freeClaimed":377,"FREE_SUPPLY":973,"MAX_SUPPLY":1390,"freePctVerified":38.75,"mintOpen":True,
 "userMintedBy":0,"userFreeUsed":0,"userBalance":0,
 "userSlotNote":"Slot open by read: mintedBy(user)=0, freeUsed(user)=0, freeLeft(user)=1, quote(user,1)=0, balance 0 - NOT preview-verified (early leads are never previewed).",
 "firstSeenBlock":130968968,"scanMints":377,"scanMinters":377,"lastReadBlock":131142332,"lastReadWib":"2026-11-02T07:08:31+07:00",
 "xVerified":False,"velocityVerified":False,
 "launchNote":"First mint verified on-chain: first Transfer-from-zero at block 130968968, 2026-11-01 09:27:57 WIB (Ankr getLogs full range from block 130900000; 377 logs = totalSupply 377, so all mints ever are in range); no project-stated launch time found; Sourcify verifiedAt 2026-11-02T00:06:13Z (verification time, NOT launch time). First-seen by this job in run 07:01 WIB via Sourcify feed.",
 "baselineNote":"EARLY lead reported once 2026-11-02 run 07:01 WIB. Never auto-minted/previewed. Agent-shape verified: Sourcify ABI (mint + quote + freeClaimed/freeFor/freeLeft/freeUsed + FREE_SUPPLY) and AGENT_ID() reads the registry 0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F on-chain. Free % 38.75%, below 50%; X unverified; velocity not yet computable (first baseline stored this run).",
 "previousTotalSupply":None,"mintedInInterval":None,"intervalMinutes":None,"currentRatePerMin":None,"previousRatePerMin":None,"velocityLegPasses":False,
 "velocityNote":"Run 07:01 WIB: first baseline stored (totalSupply 377); velocity not yet computable."}
# Pending claims: values only
pc=snap.setdefault("pending_claims",{})
if "binanceai.fun" in pc: pc["binanceai.fun"]["launched"]=False; pc["binanceai.fun"]["totalShares"]=3107
if "hive-pollen" in pc: pc["hive-pollen"]["launched"]=False; pc["hive-pollen"]["pollenAgents"]=7587; pc["hive-pollen"]["paidSold"]=1019
# Track C values only (keys as in snapshot)
tc=snap.setdefault("track_c",{})
def upd(k, **kw):
    if k in tc: tc[k].update(kw)
upd("BNBbaby", sharesMinted=10244, freeMinted=9894, paidShares=350)
upd("DOG", sharesMinted=1182)
upd("QILIN", cardsSold=4938, freeCardsRemaining=109, freeGiven=4891)
upd("SAMBARIO", cardsSold=205)
upd("a7Be", sharesMinted=438, freeSharesMinted=425)
upd("NIUBI", sharesMinted=68, freeMinted=67)
upd("JUBAO", freeClaimed=18); upd("ZCMAO", freeClaimed=37); upd("JINLONG", freeClaimed=129)
snap["timestamp_wib"]="2026-11-02T07:01:00+07:00"
snap["note"]=("Run 07:01 WIB: Hachiko minted-by-user (strong-lead direct mint, tx 0xd697bb3e5d19d56b4575ee4bf77033ef26093e1465c346783e98d1d2db0ff642, #839); "
 "BINANCE HACK removed (free pool exhausted 60/60); Meadow Agent removed (totalMinted 381 = FREE_SUPPLY, costFor 0.0005 BNB); Volcano Agent removed (totalMinted 469 > FREE_SUPPLY 468, costFor 0.0005 BNB); "
 "3 new EARLY leads added (GrimHarvest, NightshadeClub, TheWickedVault); no new strong lead, no new candidate, no track-B change, no new track-C lead/candidate. Scan leg pending at snapshot write; scan state/seen updated separately after scan completes.")
json.dump(snap, open(base/"onchain-snapshot.json","w"), indent=1, ensure_ascii=False)
print("contracts now:", len(snap["contracts"]), sorted(snap["contracts"].keys()))
for n in ["NULLSECTOR","Neonwolfy","Griffinko","PIXEL FROGS","Orchard Agent"]:
    c=snap["contracts"][n]; print(n, c.get("totalSupply", c.get("totalMinted")), c.get("mintedInInterval"), c.get("currentRatePerMin"), c.get("velocityLegPasses"))
