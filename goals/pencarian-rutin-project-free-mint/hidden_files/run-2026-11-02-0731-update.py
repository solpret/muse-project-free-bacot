#!/usr/bin/env python3
"""Run 0731 snapshot update. Read-only inputs; writes snapshot + seen + scan-state + track-c-checked."""
import json, pathlib, datetime
base = pathlib.Path.home()/"workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
snap = json.load(open(base/"onchain-snapshot.json"))
def load(f):
    try: return json.load(open(base/f))
    except Exception: return {}
read=load("run-2026-11-02-0731-read.json"); extra=load("run-2026-11-02-0731-read-extra.json")
cilok=load("run-2026-11-02-0731-cilok.json"); v2=load("run-2026-11-02-0731-verify2.json")
v3=load("run-2026-11-02-0731-verify3.json"); vnew=load("run-2026-11-02-0731-verify-new.json")
def gi(d, *names):
    for n in names:
        v=d.get(n) if isinstance(d,dict) else None
        if isinstance(v, dict): v=v.get("int")
        if v is not None: return v
    return None
def parse_wib(s):
    return datetime.datetime.fromisoformat(s)
# (source, key, block, wib)
GROUPS={
 "main": (read, 131146733, "2026-11-02T07:42:49+07:00"),
 "extra": (extra, 131146906, "2026-11-02T07:43:08+07:00"),
 "cilok": (cilok, 131147617, "2026-11-02T07:48:13+07:00"),
 "v2": (v2, 131146956, "2026-11-02T07:43:13+07:00"),
 "v3": (v3, 131146959, "2026-11-02T07:43:32+07:00"),
 "vnew": (vnew, 131147012, "2026-11-02T07:43:43+07:00"),
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
 "PIXEL FROGS": ("v3","Bd14"), "Hachiko": ("v3","C48c"), "Orchard Agent": ("v3","D1dc"),
 "GrimHarvest": ("vnew","C43F"), "NightshadeClub": ("vnew","2C02"), "TheWickedVault": ("vnew","2760"),
}
for name,(grp,key) in MAP.items():
    if name not in snap["contracts"]: continue
    src,blk,wib = GROUPS[grp][0], GROUPS[grp][1], GROUPS[grp][2]
    d=src.get(key,{})
    old=snap["contracts"][name]
    tot=gi(d, "totalSupply()", "totalSupply", "totalMinted()", "totalMinted")
    free=gi(d, "freeClaimed()", "freeClaimed", "totalFreeMinted()", "freeMinted()")
    cap=gi(d, "FREE_SUPPLY()", "freeCap()", "FREE_CAP()", "freeCap")
    oldtot=old.get("totalSupply", old.get("totalMinted"))
    prev_rate=old.get("currentRatePerMin")
    old["previousTotalSupply"]=oldtot
    if tot is not None:
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
    try: interval=(parse_wib(wib)-parse_wib(old.get("lastReadWib","2026-11-02T07:06:15+07:00"))).total_seconds()/60
    except Exception: interval=36.6
    minted = (tot-oldtot) if (tot is not None and oldtot is not None) else None
    rate = (minted/interval) if (minted is not None and interval) else None
    passes = bool(rate is not None and prev_rate is not None and minted is not None and minted>=20 and rate>=1.5*prev_rate)
    old["mintedInInterval"]=minted; old["intervalMinutes"]=round(interval,2)
    old["previousRatePerMin"]=prev_rate; old["currentRatePerMin"]=round(rate,3) if rate is not None else None
    old["velocityLegPasses"]=passes
    old["velocityNote"]=f"Run 07:31 WIB: +{minted} tokens in ~{interval:.2f} min = {rate:.3f}/min" if rate is not None else "Run 07:31 WIB: velocity not computable"
    old["velocityNote"]+= f", ratio vs prior {prev_rate} = {rate/prev_rate:.2f}x, so the velocity leg PASSES." if passes else ", so the velocity leg still FAILS."
    old["lastReadBlock"]=blk; old["lastReadWib"]=wib
# Specials
sl=snap["contracts"]["Slimelings"]; sl["mintedCount"]=1893-0  # totalSupply 1893; mintedCount/freeCount from main read not re-read in detail; keep prior fields except totals
# Slimelings main-read totals: totalSupply 1893 (already set via MAP? Slimelings key in main read has totalSupply only) -> velocity computed above from totalSupply
vp=snap["contracts"]["Vorpry"]; vp["totalSupply"]=239; vp["totalMinted"]=239; vp["openLeft"]=1564
mp=snap["contracts"]["Mirror Pair"]; mp["lastReadBlock"]=131146733; mp["lastReadWib"]="2026-11-02T07:42:49+07:00"; mp["velocityNote"]="Run 07:31 WIB: mintedPairs still 2 (was 2) - no new pair; velocity not computable."
# Hachiko free pool exhausted (minted-by-user, kept, record only)
h=snap["contracts"]["Hachiko"]; h["totalSupply"]=1007; h["freeClaimed"]=1000; h["freePctVerified"]=100.0
# Minted this run
snap["contracts"]["SynapseSquad"]={
 "address":"0xD65913933ada0b429de8f17eDBAdf5FA24aa94E2","status":"minted-by-user-2026-11-02","name":"SynapseSquad","symbol":"SYNP","kind":"ERC721",
 "totalSupply":184,"freeClaimed":162,"FREE_SUPPLY":313,"MAX_SUPPLY":448,"freePctVerified":51.76,"mintOpen":True,
 "userMintedBy":1,"userFreeUsed":1,"userBalance":1,
 "userSlotNote":"Slot USED by user mint 2026-11-02 (tx 0x2d3b776d60d91f278f0f89c6546b02bc78b32a3baaaceb26cead85c6da49081c, token #184); next mint is paid, NOT authorized",
 "firstSeenBlock":131004468,"firstMintWib":"2026-11-01 13:54:16 WIB","scanMints":None,
 "lastReadBlock":131148212,"lastReadWib":"2026-11-02T08:0x+07:00","xVerified":False,"velocityVerified":False,
 "launchNote":"First mint verified on-chain: first Transfer-from-zero at block 131004468, 2026-11-01 13:54:16 WIB (Ankr getLogs from block 130900000, 183 logs; 0 logs in 130800000-131004467 chunk); no project-stated launch time found; Sourcify verifiedAt is verification time, NOT launch time. First-seen by this job in run 07:31 WIB via Sourcify feed.",
 "baselineNote":"STRONG-LEAD DIRECT MINT executed in run 07:31 WIB (reported once via mint outcome): age verified ~42h, free 161/313 = 51.44% verified at pre-mint block 131148070, user slot open (mintedBy 0, freeUsed 0, freeLeft 1, quote 0). X UNVERIFIED (not required under strong-lead direct-mint rule). Audit hasResult=false disclosed as no result, no risk hits. Preview clean 000000000. Never previewed as a lead.",
 "mintTx":"0x2d3b776d60d91f278f0f89c6546b02bc78b32a3baaaceb26cead85c6da49081c","mintBlock":131148212,"mintGas":136212,"mintTokenId":184}
snap["contracts"]["SeanceSociety"]={
 "address":"0x8F8705A91cb8af615CE35179B0D33200AdE71DAb","status":"minted-by-user-2026-11-02","name":"SeanceSociety","symbol":"SEANCE","kind":"ERC721",
 "totalSupply":331,"freeClaimed":323,"FREE_SUPPLY":483,"MAX_SUPPLY":690,"freePctVerified":66.87,"mintOpen":True,
 "userMintedBy":1,"userFreeUsed":1,"userBalance":1,
 "userSlotNote":"Slot USED by user mint 2026-11-02 (tx 0xa17ad0cfdd543ed812bea785cd935fae97b65514c57eb68f01879ac332bc5665, token #326); next mint is paid, NOT authorized",
 "firstSeenBlock":131001129,"firstMintWib":"2026-11-01 13:29:12 WIB",
 "lastReadBlock":131148255,"lastReadWib":"2026-11-02T08:0x+07:00","xVerified":False,"velocityVerified":False,
 "launchNote":"First mint verified on-chain: first Transfer-from-zero at block 131001129, 2026-11-01 13:29:12 WIB (Ankr getLogs from block 130900000, 325 logs; 0 logs in 130800000-131001128 chunk); no project-stated launch time found; Sourcify verifiedAt is verification time, NOT launch time. First-seen by this job in run 07:31 WIB via Sourcify feed.",
 "baselineNote":"STRONG-LEAD DIRECT MINT executed in run 07:31 WIB (reported once via mint outcome): age verified ~42.5h, free 317/483 = 65.63% verified at pre-mint block 131148070, user slot open (mintedBy 0, freeUsed 0, freeLeft 1, quote 0). X UNVERIFIED (not required under strong-lead direct-mint rule). Audit hasResult=false disclosed as no result, no risk hits. Preview clean 000000000. Never previewed as a lead.",
 "mintTx":"0xa17ad0cfdd543ed812bea785cd935fae97b65514c57eb68f01879ac332bc5665","mintBlock":131148255,"mintGas":136212,"mintTokenId":326}
# New early leads (first baselines; velocity not yet computable)
early_new={
 "Critter Agent": {"address":"0x4fc39B2c1620f2561d01232f87E25581CFD72A51","symbol":"CRAT","totalSupply":296,"freeMinted":296,"FREE_SUPPLY":33333,"MAX_SUPPLY":88888,"freePctVerified":None,"firstSeenBlock":131145976,"firstMintWib":"2026-11-02 07:35:51 WIB","scanMints":69,"scanMinters":69,"note":"Agent-shape verified: Sourcify ABI (mint + quote + freeClaimed/freeMinted + REGISTRY) and REGISTRY() reads the registry on-chain. Free % UNVERIFIED as a free-quota % (freeMinted 296 vs freeSupply 33333 is not used as a verified free-quota % without a free-cap view matching the template; quote(user,1)=0, mintedBy 0, freeClaimed(user) 0, balance 0 - slot open by read, NOT preview-verified)."},
 "LanternLords": {"address":"0xC9c0De69ea301cA9479149554bf325aE3342584B","symbol":"LNTRN","totalSupply":139,"freeClaimed":131,"FREE_SUPPLY":539,"MAX_SUPPLY":770,"freePctVerified":24.3,"firstSeenBlock":131002528,"firstMintWib":"2026-11-01 13:39:43 WIB","scanMints":14,"scanMinters":14,"note":"Agent-shape verified: Sourcify ABI (mint + quote + freeClaimed/freeFor/freeLeft/freeUsed + FREE_SUPPLY) and AGENT_ID() reads the registry on-chain. Age ~42h verified (exclusion due ~2026-11-02 13:39 WIB if still unsold)."},
 "Plutopop": {"address":"0xE4cA7AaA82253717C0d897C10d58D59821631509","symbol":"PLUTOPOP","totalSupply":144,"freeClaimed":136,"FREE_SUPPLY":856,"MAX_SUPPLY":1071,"freePctVerified":15.89,"firstSeenBlock":131144199,"firstMintWib":"2026-11-02 07:22:32 WIB","scanMints":90,"scanMinters":82,"note":"Agent-shape verified: Sourcify ABI (mint + quote + freeClaimed/freeFor/freeLeft/freeUsed + FREE_SUPPLY) and AGENT_ID() reads the registry on-chain."},
 "Krakenbo": {"address":"0x46c1815082ccf1273e3c07548ef2004046Bb7Fc0","symbol":"KRAKENBO","totalSupply":150,"freeClaimed":142,"FREE_SUPPLY":903,"MAX_SUPPLY":1129,"freePctVerified":15.72,"firstSeenBlock":131144193,"firstMintWib":"2026-11-02 07:22:29 WIB","scanMints":97,"scanMinters":89,"note":"Agent-shape verified: Sourcify ABI (mint + quote + freeClaimed/freeFor/freeLeft/freeUsed + FREE_SUPPLY) and AGENT_ID() reads the registry on-chain."},
 "Ghoulipop": {"address":"0xb2d236EC0473792eC6727e5bf41084Df3eA0137F","symbol":"GHOULIPOP","totalSupply":159,"freeClaimed":151,"FREE_SUPPLY":791,"MAX_SUPPLY":989,"freePctVerified":19.09,"firstSeenBlock":131144191,"firstMintWib":"2026-11-02 07:22:28 WIB","scanMints":117,"scanMinters":109,"note":"Agent-shape verified: Sourcify ABI (mint + quote + freeClaimed/freeFor/freeLeft/freeUsed + FREE_SUPPLY) and AGENT_ID() reads the registry on-chain."},
 "Servobun": {"address":"0xbd297cb5158F4DcA02C336A59556FDBfa6609A70","symbol":"SERVOBUN","totalSupply":165,"freeClaimed":157,"FREE_SUPPLY":851,"MAX_SUPPLY":1064,"freePctVerified":18.45,"firstSeenBlock":131144181,"firstMintWib":"2026-11-02 07:22:24 WIB","scanMints":79,"scanMinters":79,"note":"Agent-shape verified: Sourcify ABI (mint + quote + freeClaimed/freeFor/freeLeft/freeUsed + FREE_SUPPLY) and AGENT_ID() reads the registry on-chain."},
 "Glacier Agent": {"address":"0xD8F2d1f5158135232f69Fe0605A406A51d86Ce6B","symbol":"GLAC","totalSupply":None,"totalMinted":402,"FREE_SUPPLY":458,"MAX_SUPPLY":1637,"freePctVerified":None,"firstSeenBlock":131143243,"firstMintWib":"2026-11-02 07:15:22 WIB","scanMints":146,"scanMinters":66,"note":"Agent-shape verified: Sourcify ABI (mint + costFor + agentIdRegistry + FREE_SUPPLY) and agentIdRegistry() reads the registry on-chain. Free % UNVERIFIED (no free total view; totalMinted 402 vs FREE_SUPPLY 458 NOT used as a %). costFor(1)=0, mintedBy(user)=0, balance 0 - slot open by read, NOT preview-verified."},
 "Xianyulo": {"address":"0x5bF46eF8E5e09fFFfd928e30077b4d4674CBA4b0","symbol":"XIANYULO","totalSupply":169,"freeClaimed":161,"FREE_SUPPLY":834,"MAX_SUPPLY":1043,"freePctVerified":19.3,"firstSeenBlock":131144188,"firstMintWib":"2026-11-02 07:22:27 WIB","scanMints":98,"scanMinters":96,"note":"Agent-shape verified: Sourcify ABI (mint + quote + freeClaimed/freeFor/freeLeft/freeUsed + FREE_SUPPLY) and AGENT_ID() reads the registry on-chain. First-mint logs 169 = totalSupply 169, so all mints ever are in range."},
}
for nm, e in early_new.items():
    d={"address":e["address"],"status":"early-lead-reported-2026-11-02","name":nm,"symbol":e["symbol"],"kind":"ERC721",
     "totalSupply":e.get("totalSupply"),"totalMinted":e.get("totalMinted"),"freeClaimed":e.get("freeClaimed"),"freeMinted":e.get("freeMinted"),
     "FREE_SUPPLY":e["FREE_SUPPLY"],"MAX_SUPPLY":e["MAX_SUPPLY"],"freePctVerified":e["freePctVerified"],"mintOpen":True,
     "userMintedBy":0,"userFreeUsed":0,"userBalance":0,
     "userSlotNote":"Slot open by read: mintedBy(user)=0, quote(user,1)=0, balance 0 - NOT preview-verified (early leads are never previewed).",
     "firstSeenBlock":e["firstSeenBlock"],"scanMints":e["scanMints"],"scanMinters":e.get("scanMinters"),
     "lastReadBlock":131148730,"lastReadWib":"2026-11-02T07:56:57+07:00","xVerified":False,"velocityVerified":False,
     "launchNote":f"First mint verified on-chain: first Transfer-from-zero at block {e['firstSeenBlock']}, {e['firstMintWib']} (Ankr getLogs from block 130900000); no project-stated launch time found; Sourcify verifiedAt is verification time, NOT launch time. First-seen by this job in run 07:31 WIB via Sourcify feed + scan cross-check.",
     "baselineNote":f"EARLY lead reported once 2026-11-02 run 07:31 WIB. Never auto-minted/previewed. {e['note']} Free % far below 50%; X unverified; velocity not yet computable (first baseline stored this run).",
     "previousTotalSupply":None,"mintedInInterval":None,"intervalMinutes":None,"currentRatePerMin":None,"previousRatePerMin":None,"velocityLegPasses":False,
     "velocityNote":"Run 07:31 WIB: first baseline stored; velocity not yet computable."}
    snap["contracts"][nm]=d
# Pending claims
pc=snap["pending_claims"]
pc["binanceai.fun"].update({"launched":False,"tokenClaimed":False,"totalShares":3107,"totalShares_last":3107,"lastCheckBlock":131146733,"lastCheckWib":"2026-11-02T07:42:49+07:00"})
pc["hive-pollen"].update({"launched":False,"phase":1,"pollenAgents":7592,"paidSold":1019,"lastCheckBlock":131146733,"lastCheckWib":"2026-11-02T07:42:49+07:00"})
# Track-C updates (values from 0731 reads)
tc=snap["track_c"]
def upd_tc(k, **kw):
    if k in tc and isinstance(tc[k], dict): tc[k].update(kw)
    elif k in tc: tc[k]=kw
upd_tc("BNBbaby", sharesMinted=10373, freeMinted=10012, lastReadBlock=131146733, lastReadWib="2026-11-02T07:42:49+07:00")
upd_tc("DOG", sharesMinted=1198, lastReadBlock=131146733, lastReadWib="2026-11-02T07:42:49+07:00")
upd_tc("QILIN", cardsSold=4961, freeCardsRemaining=95, freeGiven=4905, lastReadBlock=131146733, lastReadWib="2026-11-02T07:42:49+07:00")
upd_tc("SAMBARIO", cardsSold=205, freeCardsRemaining=3128, freeGiven=205, lastReadBlock=131146733, lastReadWib="2026-11-02T07:42:49+07:00")
upd_tc("a7Be", sharesMinted=444, freeSharesMinted=431, lastReadBlock=131146733, lastReadWib="2026-11-02T07:42:49+07:00")
upd_tc("NIUBI", sharesMinted=69, freeMinted=68, lastReadBlock=131146733, lastReadWib="2026-11-02T07:42:49+07:00")
upd_tc("零元购", soldFree=76, soldPaid=11, totalSold=87, lastReadBlock=131146733, lastReadWib="2026-11-02T07:42:49+07:00")
upd_tc("JUBAO", freeClaimed=19, lastReadBlock=131146733, lastReadWib="2026-11-02T07:42:49+07:00")
upd_tc("ZCMAO", freeClaimed=38, lastReadBlock=131146733, lastReadWib="2026-11-02T07:42:49+07:00")
upd_tc("JINLONG", freeClaimed=152, lastReadBlock=131146733, lastReadWib="2026-11-02T07:42:49+07:00")
upd_tc("BIAO", freeClaimed=0, lastReadBlock=131146906, lastReadWib="2026-11-02T07:43:08+07:00")
upd_tc("兕", soldFree=74, lastReadBlock=131146906, lastReadWib="2026-11-02T07:43:08+07:00")
upd_tc("Velmora", freeClaimedShares=275, remainingShares=24724, totalClaimedShares=275, lastReadBlock=131147617, lastReadWib="2026-11-02T07:48:30+07:00")
snap["timestamp_wib"]="2026-11-02T08:05:00+07:00"
snap["note"]="Run 07:31 WIB: 2 strong-lead direct mints (SynapseSquad #184, SeanceSociety #326); 8 new early leads (Critter Agent, LanternLords, Plutopop, Krakenbo, Ghoulipop, Servobun, Glacier Agent, Xianyulo); MummyMania + ZombieZone age-excluded (>48h, never added); Voyager paid lane (costFor 0.0005 BNB, checked only); Super Dino free pool exhausted (checked only). Track-C leads NOT executed this run: new user rule (07:51/07:57 WIB) makes lead direct mint effective from the NEXT runs; leads re-verified this run (pools open, slots open) for next-run execution."
json.dump(snap, open(base/"onchain-snapshot.json","w"), indent=1, ensure_ascii=False)
print("contracts:", len(snap["contracts"]), "track_c:", len(snap["track_c"]))
# Seen file + scan state + track-c-checked
scan=json.load(open(base/"onchain-scan-2026-11-02-0731.json"))
tri=json.load(open(base/"run-2026-11-02-0731-scan-triage.json"))
seen=json.load(open(base/"onchain-scan-seen.json"))
for c in tri["first_seen"]:
    seen["contracts"][c["address"].lower()]=c["first_block"]
json.dump(seen, open(base/"onchain-scan-seen.json","w"), indent=1)
print("seen contracts:", len(seen["contracts"]))
state={"last_scanned_block": scan["to_block"], "last_scan_window_from": scan["from_block"], "last_scan_window_to": scan["to_block"],
 "last_scan_wib": "2026-11-02T07:57:00+07:00", "ankr_calls": scan["ankr_calls"], "errors": scan["errors"],
 "nft_contracts": len(scan["contracts"]), "erc20_mint_contracts": scan["erc20_mint_contracts"],
 "skipped_gap": [131142011, 131144677],
 "note": "Window capped at 2000 blocks; gap 131142011-131144677 not scanned (bounded cap, never retro-scanned beyond it). Prior gaps carried in earlier state files."}
json.dump(state, open(base/"onchain-scan-state.json","w"), indent=1)
checked=json.load(open(base/"track-c-scan-checked.json"))
if isinstance(checked, list):
    s=set(x.lower() for x in checked); s.update(e["address"].lower() for e in tri["erc20_candidates"][:20]); checked=sorted(s)
else:
    for e in tri["erc20_candidates"][:20]: checked[e["address"].lower()]=True
json.dump(checked, open(base/"track-c-scan-checked.json","w"), indent=1)
print("track-c-checked:", len(checked))
