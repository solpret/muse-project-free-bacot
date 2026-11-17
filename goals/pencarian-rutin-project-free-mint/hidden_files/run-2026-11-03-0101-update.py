import json, copy
BASE=""
snap=json.load(open("onchain-snapshot.json"))
read=json.load(open("run-2026-11-03-0101-read.json"))
rd=json.load(open("run-2026-11-03-0101-river-deco.json"))
agent3=json.load(open("run-2026-11-03-0101-agent3.json"))
READ_BLOCK=read["block"]  # 131285442
INTERVAL_MIN=29.0  # snapshot lastRead ~00:34 WIB -> route1 read ~01:03 WIB
# Route 1 updates
for name, v in snap["contracts"].items():
    if str(v.get("status","")).startswith("minted-by-user"): continue
    r=read.get(name)
    if not r: continue
    old_ts=v.get("totalSupply")
    new_ts=r.get("totalSupply()")
    if new_ts is not None:
        if old_ts is not None and new_ts!=old_ts:
            prev_rate=v.get("currentRatePerMin")
            rate=round((new_ts-old_ts)/INTERVAL_MIN,3) if new_ts>old_ts else 0.0
            v["previousTotalSupply"]=old_ts
            v["mintedInInterval"]=new_ts-old_ts
            v["intervalMinutes"]=INTERVAL_MIN
            if prev_rate is not None: v["previousRatePerMin"]=prev_rate
            v["currentRatePerMin"]=rate
            # velocity leg: >=1.5x prev AND >=20 tokens
            if prev_rate and prev_rate>0 and rate>=1.5*prev_rate and (new_ts-old_ts)>=20:
                v["velocityLegPasses"]=True
            else:
                v["velocityLegPasses"]=False
        v["totalSupply"]=new_ts
    fc=r.get("freeClaimed()"); fs=r.get("FREE_SUPPLY()")
    if fc is not None: v["freeClaimed"]=fc
    if fs is not None: v["FREE_SUPPLY"]=fs
    if fc is not None and fs: v["freePctVerified"]=round(100*fc/fs,2)
    mb=r.get("mintedBy(address)"); fu=r.get("freeUsed(address)"); bal=r.get("balanceOf(address)")
    if mb is not None: v["userMintedBy"]=mb
    if fu is not None: v["userFreeUsed"]=fu
    if bal is not None: v["userBalance"]=bal
    v["lastReadBlock"]=READ_BLOCK
    v["lastReadWib"]="2026-11-03T01:03:00+07:00"
# River / Deco / Aura / Moth extra reads (block 131285686)
for name, key in [("River Agent","River Agent"),("Deco Agent","Deco Agent"),("Aura Agents","Aura Agents"),("Moth Agent","Moth Agent")]:
    v=snap["contracts"].get(name)
    if not v: continue
    d=rd[key]
    tm=d.get("totalMinted()"); ts=d.get("totalSupply()")
    new_total=tm if tm is not None else ts
    old_total=v.get("totalMinted") if v.get("totalMinted") is not None else v.get("totalSupply")
    if new_total is not None:
        if old_total is not None and new_total!=old_total:
            v["previousTotalSupply"]=old_total
            v["mintedInInterval"]=new_total-old_total
            v["intervalMinutes"]=30.0
            v["currentRatePerMin"]=round((new_total-old_total)/30.0,3)
            v["velocityLegPasses"]=False  # no previous rate to ratio against
        v["totalMinted"]=tm if tm is not None else v.get("totalMinted")
        if ts is not None: v["totalSupply"]=ts
    if d.get("FREE_SUPPLY()") is not None: v["FREE_SUPPLY"]=d["FREE_SUPPLY()"]
    if d.get("mintedBy(address)") is not None: v["userMintedBy"]=d["mintedBy(address)"]
    v["lastReadBlock"]=131285686
    v["lastReadWib"]="2026-11-03T01:05:00+07:00"
# Niuniubo sold out -> remove
removed=[]
if "Niuniubo" in snap["contracts"]:
    del snap["contracts"]["Niuniubo"]; removed.append("Niuniubo (sold out 318/318)")
# Add scan agent-shaped watchlist-only (NOT early: pre-window mints exist, age unverified)
snap["contracts"]["Cryptlichor"]={
 "address":"0xb792Bf600DF37EB7638fb16434E813FC0c90C3C8","name":"Cryptlichor","symbol":"LICH","kind":"ERC721",
 "status":"watchlist-only-not-early-2026-11-03","totalSupply":397,"freeClaimed":396,"FREE_SUPPLY":1691,"freePctVerified":23.42,
 "mintOpen":True,"userMintedBy":0,"userFreeUsed":0,"userBalance":0,
 "firstSeenBlock":131283679,
 "launchNote":"NOT first-mint: Ankr pre-window walk 131270000-131283647 found 302 from-zero mints before the scan window, so launch age UNVERIFIED (true first mint not established). Scan window mints 58/58 minters.",
 "baselineNote":"NOT reported as an early lead (first mints predate the scan window; age unverified). Agent-shape verified: Sourcify verified ABI (mint + quote + freeClaimed/freeFor/freeLeft/freeUsed + agent registry ref) and scan registry-bytes hit. Tracked watchlist-only; slot user open by mintedBy(user)=0 + quote(user,1)=0 at block 131288028, NOT preview-verified.",
 "lastReadBlock":131288028,"lastReadWib":"2026-11-03T01:22:00+07:00","xVerified":False,"velocityVerified":False}
snap["contracts"]["Gondolux"]={
 "address":"0xD37aF310F2Da74c8baBe301F2A8F8494f40e0C14","name":"Gondolux","symbol":"GONDOLUX","kind":"ERC721",
 "status":"watchlist-only-not-early-2026-11-03","totalSupply":3534,"freeClaimed":3532,"FREE_SUPPLY":4000,"freePctVerified":88.3,
 "mintOpen":True,"userMintedBy":0,"userFreeUsed":0,"userBalance":0,
 "firstSeenBlock":131283842,
 "launchNote":"NOT first-mint: Ankr pre-window walk 131270000-131283647 found 62 from-zero mints before the scan window, while totalSupply 3534 far exceeds the 77 mints counted in walk+window, so most mints predate 131270000 and launch age is UNVERIFIED. Strong-lead legs (b) 88.3% and (c) slot open are met, but leg (a) verified age is NOT met, so NOT a strong lead and NOT reported as one.",
 "baselineNote":"NOT reported as an early/strong lead (age unverified). Agent-shape verified: Sourcify verified ABI (mint + quote + freeClaimed/freeFor/freeLeft/freeUsed + agent registry ref). Tracked watchlist-only; slot user open by mintedBy(user)=0 + quote(user,1)=0 at block 131288028, NOT preview-verified.",
 "lastReadBlock":131288028,"lastReadWib":"2026-11-03T01:22:00+07:00","xVerified":False,"velocityVerified":False}
snap["contracts"]["Gachagent"]={
 "address":"0xE23d1DC8F47f6a56F436d73c52862f40F26e9D39","name":"Gachagent","symbol":"GAGENT","kind":"ERC721",
 "status":"watchlist-only-not-early-2026-11-03","totalSupply":1917,"totalMinted":1917,"freeMinted":1906,"FREE_SUPPLY":2343,"freePctNote":"freeMinted 1906/2343 = 81.35% (totalMinted-based free view; no freeClaimed view)",
 "mintOpen":True,
 "firstSeenBlock":131283929,
 "launchNote":"NOT first-mint: Ankr pre-window walk 131270000-131283647 found 27 from-zero mints before the scan window, so launch age UNVERIFIED. User slot UNVERIFIED: freeMint lane exists but quote(user,1)=0.001 BNB (paid quote path) and no per-user free view read succeeded at block 131288028.",
 "baselineNote":"NOT reported as an early/strong lead (age unverified + user slot unverified). Agent-shape verified: Sourcify verified ABI (freeMint + freeMinted/freeLeft + FREE_SUPPLY + agent registry ref). Tracked watchlist-only, NOT preview-verified.",
 "lastReadBlock":131288028,"lastReadWib":"2026-11-03T01:22:00+07:00","xVerified":False,"velocityVerified":False}
# Track C drift (route1 extra reads, block 131285442)
tc=snap.setdefault("track_c",{})
if "FU-hongbao" in tc: tc["FU-hongbao"]["freeGiven"]=646
if "Ikigai-Ihigi" in tc: tc["Ikigai-Ihigi"]["freeMinted"]=202
if "NIUBI" in tc: tc["NIUBI"]["freeMinted"]=84
if "DROID" in tc: tc["DROID"]["freeMinted"]=238
# pending claims
pc=snap.setdefault("pending_claims",{})
if "hive-pollen" in pc:
    pc["hive-pollen"]["launched"]=0; pc["hive-pollen"]["phase"]=1; pc["hive-pollen"]["pollenAgents"]=7826; pc["hive-pollen"]["paidSold"]=1050
snap["timestamp_wib"]="2026-11-03T01:22:00+07:00"
json.dump(snap, open("onchain-snapshot.json","w"), indent=1)
print("contracts now:", len(snap["contracts"]), "removed:", removed)
# scan seen append
seen=json.load(open("onchain-scan-seen.json"))
scan=json.load(open("onchain-scan-2026-11-03-0101.json"))
first=json.load(open("run-2026-11-03-0101-scan-firstseen.json"))
byaddr={c["address"].lower():c for c in scan["contracts"]}
added=0
for c in first:
    k=c["address"].lower()
    if k not in seen["contracts"]:
        seen["contracts"][k]=c.get("first_block"); added+=1
json.dump(seen, open("onchain-scan-seen.json","w"), indent=1)
print("seen contracts now:", len(seen["contracts"]), "added:", added)
# scan state
state=json.load(open("onchain-scan-state.json"))
state["last_scanned_block"]=131285647
state["last_scan_window_from"]=131283648
state["last_scan_window_to"]=131285647
state["last_scan_wib"]="2026-11-03T01:22:00+07:00"
state["last_scan_run"]="2026-11-03-0101"
state["ankr_calls_last_scan"]=80
state["errors_last_scan"]=0
state["contracts_in_window"]=286
state["erc20_mint_contracts_in_window"]=686
state["skipped_gap"]=state.get("skipped_gap","")+" ; 131281876-131283647 (1772 blocks, window capped at 2000; scan covered only most recent 2000 blocks 131283648-131285647)"
state["note"]="Scan 0101 run: window 131283648-131285647 (cap 2000 blocks; head-last=3772), 80 Ankr calls, 0 errors, 286 NFT contracts, 2506 NFT mints, 686 ERC-20 mint contracts. Skipped gap 131281876-131283647 recorded."
json.dump(state, open("onchain-scan-state.json","w"), indent=1)
# track-c checked append 5c
chk=json.load(open("track-c-scan-checked.json"))
five=json.load(open("run-2026-11-03-0101-trackc-5c.json"))
before=len(chk["checked"])
for e in five:
    if e["address"].lower() not in [a.lower() for a in chk["checked"]]:
        chk["checked"].append(e["address"])
chk["note"]=chk.get("note","")+" | Run 01:01 WIB: +20 5c shape-check (all fail shape, Sourcify ABI empty/404 or no sale shape; 0 S1/S2)."
json.dump(chk, open("track-c-scan-checked.json","w"), indent=1)
print("trackc checked now:", len(chk["checked"]), "added:", len(chk["checked"])-before)
