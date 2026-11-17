#!/usr/bin/env python3
"""Merge run 2031 reads into onchain-snapshot.json. Read-only on chain; writes snapshot only."""
import json, shutil
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
snap=json.load(open(BASE+"onchain-snapshot.json"))
rr=json.load(open(BASE+"run-2026-11-16-2031-reread.json"))
BLOCK=rr["block"]  # 133924439
INTERVAL_MIN=114.1  # 1901 block 133924439 -> 2031 block 133939647 (+15208 blok x ~0,45 dtk)
byaddr={}
for k,v in snap.get("contracts",{}).items():
    if isinstance(v,dict) and v.get("address"): byaddr[v["address"].lower()]=(k,v)
tc=snap.setdefault("track_c",{})
def supply_of(v):
    # prefer totalMinted when present (RAVE case), else totalSupply
    if v.get("totalMinted") is not None: return v.get("totalMinted")
    return v.get("totalSupply")
def new_supply(views):
    if views.get("totalMinted") is not None: return views.get("totalMinted")
    return views.get("totalSupply")
notes=[]
for name, r in rr["reads"].items():
    addr=r["address"].lower(); views=r.get("views")
    if views is None:
        notes.append(f"{name}: READ-FAIL all views"); continue
    # track_c items (RigForge, DogeRageFi) live in track_c, not contracts
    ent=None; where=None
    if addr in byaddr: ent=byaddr[addr]; where="contracts"
    else:
        for k,v in tc.items():
            if isinstance(v,dict) and (v.get("address") or "").lower()==addr:
                ent=(k,v); where="track_c"; break
    if ent is None:
        notes.append(f"{name}: no snapshot entry, skipped"); continue
    key, e = ent
    prev_sup = supply_of(e)
    ns = new_supply(views)
    minted = (ns - prev_sup) if isinstance(ns,int) and isinstance(prev_sup,int) else None
    prev_rate = e.get("currentRatePerMin")
    rate = (minted/INTERVAL_MIN) if minted is not None else None
    ratio = (rate/prev_rate) if (rate is not None and prev_rate not in (None,0)) else None
    vel = bool(minted is not None and minted>=20 and ratio is not None and ratio>=1.5)
    # update supply fields present in views
    for f in ["totalSupply","totalMinted","freeMinted","freeClaimed","FREE_SUPPLY","FREE_CAP","FREE_MAX","MAX_SUPPLY","mintOpen","mintOpensAt","paused","isFreePhase","freeRemaining","paidMinted","mintPrice","freeMintsLeft","FREE_MINT_CAP","PRICE","TOKEN_PRICE","remainingSupply","totalShares","launched","failed","isRefundPhase","claimOpen","totalSpecimens","currentExperiment","genesisStart","genesisOpen","freeSharesLeft","openedAt","freeSupply","maxSupply","saleStart","saleOpen","saleEnd","mintStart"]:
        if f in views and views[f] is not None: e[f]=views[f]
    for f in ["balanceOf_user","freeMintedPerWallet_user","mintedPerWallet_user","mintedByWallet_user","hasAgentId_user","holdsAgentId_user","freeUsed_user","freeClaimed_user","mintsBy_user","mintCountOf_user","mintedBy_user","hasFreeClaimed_user","tokenClaimed_user","freeBooked_user","priceFor_user","priceFor_user_1","mintPriceFor_user_1","cost_user_1","freeClaimedByAgent_masgayut","freeClaimedByAgent_masgayut_ai"]:
        if f in views and views[f] is not None: e[f]=views[f]
    e["previousTotalSupply"]=prev_sup
    e["mintedInInterval"]=minted
    e["intervalMinutes"]=INTERVAL_MIN
    e["previousRatePerMin"]=prev_rate
    e["currentRatePerMin"]=rate
    e["velocityRatio"]=ratio
    e["velocityLegPasses"]=vel
    e["lastReadBlock"]=BLOCK
    e["lastReadWib"]="2026-11-16 ~20:31 WIB"
    free=e.get("freeMinted") if e.get("freeMinted") is not None else e.get("freeClaimed")
    cap=e.get("FREE_SUPPLY") if e.get("FREE_SUPPLY") is not None else (e.get("FREE_CAP") if e.get("FREE_CAP") is not None else e.get("FREE_MAX"))
    pct=(round(100*free/cap,1) if isinstance(free,int) and isinstance(cap,int) and cap else None)
    if pct is not None: e["freePctVerified"]=pct
    _tail=(f"free={free}/{cap} ({pct}%)" if pct is not None else f"free={free}/{cap} (free% UNVERIFIED)")
    e["runNote2031_1116"]=(f"Run 2031 (blok {BLOCK}, interval ~{INTERVAL_MIN} mnt vs run 1901): "
        f"{prev_sup}->{ns} (+{minted}, {(f'{rate:.3f}' if rate is not None else '?')}/mnt vs prev {prev_rate} = {(round(ratio,2) if ratio is not None else '?')}x) -> velocity {'LOLOS' if vel else 'GAGAL'}; " + _tail)
    notes.append(e["runNote2031_1116"])
# RAVE: fix stale totalSupply 84 -> 355 (totalMinted already 355 at 1801; verify fresh 355)
rave=None
for k,v in snap.get("contracts",{}).items():
    if (v.get("address") or "").lower()=="0x7c40B78992d86EDfFB5553C74dB5EF427100bb95".lower():
        rave=v; break
if rave is not None:
    rave["totalSupply"]=355
    rave["runNote2031_1116"]="Run 1901: totalMinted 355 FLAT vs 1801 (355); totalSupply snapshot yang basi (84) dikoreksi ke 355. freeMinted 355/3000=11,8%. Early lead sudah dilaporkan 14 Nov; umur+X+website unverified. DIAM."
    notes.append(rave["runNote2031_1116"])
# Punch Card verify (fresh read, not in reread ITEMS)
pc=None
for k,v in snap.get("contracts",{}).items():
    if (v.get("address") or "").lower()=="0x1d4ef0587dd3ff3875a141d4711c60bca40587c4":
        pc=v; break
if pc is not None:
    prev=pc.get("totalSupply"); prev_rate=pc.get("currentRatePerMin")
    minted=785-prev if isinstance(prev,int) else None
    rate=minted/INTERVAL_MIN if minted is not None else None
    ratio=(rate/prev_rate) if (rate is not None and prev_rate not in (None,0)) else None
    pc["previousTotalSupply"]=prev; pc["totalSupply"]=785; pc["freeMinted"]=784
    pc["mintedInInterval"]=minted; pc["intervalMinutes"]=INTERVAL_MIN
    pc["previousRatePerMin"]=prev_rate; pc["currentRatePerMin"]=rate; pc["velocityRatio"]=ratio
    pc["velocityLegPasses"]=bool(minted is not None and minted>=20 and ratio is not None and ratio>=1.5)
    pc["freePctVerified"]=round(100*784/5555,1)
    pc["lastReadBlock"]=133940845; pc["lastReadWib"]="2026-11-16 ~20:31 WIB"
    pc["runNote2031_1116"]=f"Run 2031 (verify, blok 133940845): totalSupply {prev}->785 (+{minted}, {rate:.3f}/mnt vs prev {prev_rate} = {ratio if ratio is None else round(ratio,2)}x) -> velocity LOLOS (>=20 token DAN >=1.5x); freeMinted 784/5555=14,1% (<50% kandidat, <70% strong lead) -> tetap EARLY lead saja, TANPA promosi (umur <24j terverifikasi + website terverifikasi, X unverified). DIAM."
    notes.append(pc["runNote2031_1116"])
# Feedshape 4 new -> track_c checked-not-sale-shape
fs=json.load(open(BASE+"run-2026-11-16-2031-feedshape.json"))
for addr, d in fs.items():
    key="feedshape-"+addr[2:6].lower()+"-2031"
    tc[key]={"address":addr,"status":"checked-not-sale-shape-2026-11-16-2031","shape":d.get("shape"),
             "fns":d.get("fns"),"mint":d.get("mint"),"quote":d.get("quote"),"free_views":d.get("free_views"),
             "registry":d.get("registry"),"token":d.get("token"),"mintFree":d.get("mintFree"),
             "lastReadWib":"2026-11-16 ~20:31 WIB",
             "baselineNote":"Sourcify feed run 2031 (verifiedAt 11:25-11:34Z, baru vs hot-leg 1819): bukan sale-shape S1/S2 (tanpa free views / tanpa registry ref). Bukan lead. DIAM."}
# Track B pending claim re-check (reread)
pc_claim=snap.get("pending_claims",{}).get("binanceai.fun")
if pc_claim is not None:
    pc_claim["launched"]=0; pc_claim["failed"]=1; pc_claim["isRefundPhase"]=1; pc_claim["tokenClaimed_user"]=0
    pc_claim["lastReadBlock"]=133939647; pc_claim["lastReadWib"]="2026-11-16 ~20:31 WIB"
    pc_claim["runNote2031_1116"]="Run 2031: launched=0, failed=1, isRefundPhase=1, totalShares=3110, tokenClaimed(user)=0 (blok 133939647) - tetap fase refund, klaim BELUM terbuka. DIAM."
    notes.append(pc_claim["runNote2031_1116"])
# PXIO Miners - EARLY LEAD baru run 2031 (Boltbook EN/ZH, post drhmwt.ai ~2 mnt)
snap["contracts"]["PXIO Miners"]={"address":"0x58e8f1b34B60687B36BCdc78e02a2fd443De71Ab",
    "status":"early-lead-2026-11-16","name":"PXIO Miners","symbol":"PXIOM","kind":"ERC721",
    "totalSupply":538,"totalMinted":538,"MAX_SUPPLY":16666,"mintOpen":1,
    "freeMinted":None,"FREE_SUPPLY":None,
    "firstSeenBlock":133939007,"firstSeenWib":"2026-11-16 ~20:54 WIB",
    "lastReadBlock":133940166,"lastReadWib":"2026-11-16 ~20:31 WIB",
    "xVerified":False,"velocityVerified":False,
    "website":"https://pxio.fun","xUrl":"https://x.com/pxiofun",
    "baselineNote":"EARLY LEAD dilaporkan sekali run 2031: agent-shaped (Sourcify exact_match verifiedAt 2026-11-16T12:21:19Z; agentRegistry()+hasAgentId()+mint()+quote() di ABI; registry bytes di bytecode) + first mints terverifikasi on-chain run ini (totalSupply 520->533->538, mintOpen 1, minting aktif) + mint pertama GRATIS terverifikasi (quote(user,1)=0, unitPrice(1)=0; mint #2+ 0,0003 BNB; canMint(user)=1, mintableBy(user)=30, hasAgentId(user)=1, mintedBy(user)=0, bal_user=0). Website TERVERIFIKASI metode (I): contractURI external_link https://pxio.fun + X https://x.com/pxiofun on-chain; pxio.fun HTTP 200 dan js/mint.js mencetak kontrak persis. Diskusi publik: post Boltbook drhmwt.ai (b/alpha) ~20:54 WIB + X https://x.com/pxiofun. Umur UNVERIFIED (first-mint block tidak terverifikasi: eth_getLogs publik -32005 limit exceeded 200/1000-blok; binary-search eth_call historis None; Ankr 401; BscScan V2 free tidak mencakup BSC) - bukti same-day saja (Sourcify 19:21 WIB + post Boltbook). free% UNVERIFIED (tanpa view freeSupply/freeLeft/freeClaimed; 538/16666=3,2% hanya inferensi totalSupply, BUKAN counter gratis). BUKAN kandidat (<50%), BUKAN strong lead (<70% + umur unverified). TIDAK PERNAH di-preview/di-mint (early lead).",
    "runNote2031_1116":"Run 2031: PXIO Miners baru dari Boltbook - EARLY LEAD (dilaporkan sekali). quote(user,1)=0 (mint pertama gratis), supply 538/16666, website pxio.fun terverifikasi (mint.js mencetak kontrak), umur + free% UNVERIFIED."}
notes.append("PXIO Miners 0x58e8... -> EARLY LEAD baru run 2031 (dilaporkan sekali).")
snap["last_run"]="2026-11-16 ~20:31 WIB"
json.dump(snap, open(BASE+"onchain-snapshot.json","w"), indent=1)
print("contracts:", len(snap.get("contracts",{})), "track_c:", len(tc))
for n in notes: print("-", n)
print("MERGE DONE")
