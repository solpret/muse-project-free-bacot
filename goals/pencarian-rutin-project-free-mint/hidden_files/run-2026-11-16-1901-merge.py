#!/usr/bin/env python3
"""Merge run 1901 reads into onchain-snapshot.json. Read-only on chain; writes snapshot only."""
import json, shutil
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
snap=json.load(open(BASE+"onchain-snapshot.json"))
rr=json.load(open(BASE+"run-2026-11-16-1901-reread.json"))
BLOCK=rr["block"]  # 133924439
INTERVAL_MIN=27.5  # 1831 block 133920769 -> 1901 block 133924439 (+3670 blok x ~0,45 dtk)
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
    e["lastReadWib"]="2026-11-16 ~19:01 WIB"
    free=e.get("freeMinted") if e.get("freeMinted") is not None else e.get("freeClaimed")
    cap=e.get("FREE_SUPPLY") if e.get("FREE_SUPPLY") is not None else (e.get("FREE_CAP") if e.get("FREE_CAP") is not None else e.get("FREE_MAX"))
    pct=(round(100*free/cap,1) if isinstance(free,int) and isinstance(cap,int) and cap else None)
    if pct is not None: e["freePctVerified"]=pct
    _tail=(f"free={free}/{cap} ({pct}%)" if pct is not None else f"free={free}/{cap} (free% UNVERIFIED)")
    e["runNote1901_1116"]=(f"Run 1901 (blok {BLOCK}, interval ~{INTERVAL_MIN} mnt vs run 1831): "
        f"{prev_sup}->{ns} (+{minted}, {(f'{rate:.3f}' if rate is not None else '?')}/mnt vs prev {prev_rate} = {(round(ratio,2) if ratio is not None else '?')}x) -> velocity {'LOLOS' if vel else 'GAGAL'}; " + _tail)
    notes.append(e["runNote1901_1116"])
# RAVE: fix stale totalSupply 84 -> 355 (totalMinted already 355 at 1801; verify fresh 355)
rave=None
for k,v in snap.get("contracts",{}).items():
    if (v.get("address") or "").lower()=="0x7c40b78992d86edfffe5553c74db5ef427100bb95".lower():
        rave=v; break
if rave is not None:
    rave["totalSupply"]=355
    rave["runNote1901_1116"]="Run 1901: totalMinted 355 FLAT vs 1801 (355); totalSupply snapshot yang basi (84) dikoreksi ke 355. freeMinted 355/3000=11,8%. Early lead sudah dilaporkan 14 Nov; umur+X+website unverified. DIAM."
    notes.append(rave["runNote1901_1116"])
# Punch Card verify (fresh read, not in reread ITEMS)
pc=None
for k,v in snap.get("contracts",{}).items():
    if (v.get("address") or "").lower()=="0x1d4ef0587dd3ff3875a141d4711c60bca40587c4":
        pc=v; break
if pc is not None:
    prev=pc.get("totalSupply"); prev_rate=pc.get("currentRatePerMin")
    minted=651-prev if isinstance(prev,int) else None
    rate=minted/INTERVAL_MIN if minted is not None else None
    ratio=(rate/prev_rate) if (rate is not None and prev_rate not in (None,0)) else None
    pc["previousTotalSupply"]=prev; pc["totalSupply"]=651; pc["freeMinted"]=650
    pc["mintedInInterval"]=minted; pc["intervalMinutes"]=INTERVAL_MIN
    pc["previousRatePerMin"]=prev_rate; pc["currentRatePerMin"]=rate; pc["velocityRatio"]=ratio
    pc["velocityLegPasses"]=bool(minted is not None and minted>=20 and ratio is not None and ratio>=1.5)
    pc["freePctVerified"]=round(100*650/5555,1)
    pc["lastReadBlock"]=BLOCK; pc["lastReadWib"]="2026-11-16 ~19:01 WIB"
    pc["runNote1901_1116"]=f"Run 1901 (verify, blok {BLOCK}): totalSupply {prev}->651 (+{minted}, {rate:.3f}/mnt vs prev {prev_rate} = {ratio if ratio is None else round(ratio,2)}x) -> velocity GAGAL; freeMinted 650/5555=11,7% (<50% kandidat, <70% strong lead) -> tetap EARLY lead saja, TANPA promosi. DIAM."
    notes.append(pc["runNote1901_1116"])
# Feedshape 4 new -> track_c checked-not-sale-shape
fs=json.load(open(BASE+"run-2026-11-16-1901-feedshape.json"))
for addr, d in fs.items():
    key="feedshape-"+addr[2:6].lower()+"-1901"
    tc[key]={"address":addr,"status":"checked-not-sale-shape-2026-11-16-1901","shape":d.get("shape"),
             "fns":d.get("fns"),"mint":d.get("mint"),"quote":d.get("quote"),"free_views":d.get("free_views"),
             "registry":d.get("registry"),"token":d.get("token"),"mintFree":d.get("mintFree"),
             "lastReadWib":"2026-11-16 ~19:01 WIB",
             "baselineNote":"Sourcify feed run 1901 (verifiedAt 11:25-11:34Z, baru vs hot-leg 1819): bukan sale-shape S1/S2 (tanpa free views / tanpa registry ref). Bukan lead. DIAM."}
# Boltbook: Aero Agent 0x62f8... = baru vs snapshot+seen+track_c -> checked-not-lead
snap["contracts"]["AeroAgent-62f8"]={"address":"0x62f8eeb8843d20eb1fec57fc65484159f4ca93f2","status":"checked-not-lead-2026-11-16-1901",
    "name":"Aero Agent","kind":"ERC721","totalSupply":4900,"totalMinted":4900,"MAX_SUPPLY":5000,"mintOpen":None,
    "freeMinted":None,"FREE_SUPPLY":None,"AGENT_ID":552192074493313695968015109214105588393044541999,
    "lastReadBlock":133925375,"lastReadWib":"2026-11-16 ~19:01 WIB",
    "baselineNote":"Boltbook EN/ZH run 1901, post sirenia.ai (b/alpha): totalSupply 4.900, mint(1) value 0 REVERT dari 2 wallet, supply FLAT vs recheck 18:54 - bukan free mint. Verifikasi sendiri run 1901: freeMinted/FREE_SUPPLY/mintOpen/priceFor semua revert (view tidak ada), Sourcify 404 (unverified), 4900/5000=98%. Bukan lead (paid-only/tanpa jalur gratis). DIAM.",
    "runNote1901_1116":"Run 1901: Aero Agent baru dari Boltbook - mint(1) value 0 revert (Boltbook + verifikasi on-chain), tanpa free view, Sourcify unverified, 98% minted -> checked-not-lead, TIDAK dilaporkan, TIDAK di-preview/di-mint."}
notes.append("Boltbook Aero Agent 0x62f8... -> checked-not-lead (mint value 0 revert, tanpa free view, Sourcify 404, 98%).")
# ALIEN opened (verify run 1901): totalSupply 77, free views revert
al=snap["contracts"].get("ALIEN")
if al is not None:
    al["totalSupply"]=77; al["FREE_SUPPLY"]=1000; al["MAX_SUPPLY"]=1300; al["mintOpen"]=1; al["isFreePhase"]=1
    al["status"]="watchlist-only-opened-age-free-unverified-2026-11-16"
    al["lastReadBlock"]=133925375; al["lastReadWib"]="2026-11-16 ~19:01 WIB"
    al["runNote1901_1116"]="Run 1901: ALIEN BUKA (totalSupply 0->59 reread ->77 verify, +18 dlm ~15 mnt, isFreePhase 1, mintOpen 1). freeMinted/mintStart/totalMinted revert di 3 endpoint (view tidak ada) -> free% UNVERIFIED (77/1000=7,7% hanya inferensi totalSupply, BUKAN counter gratis terverifikasi) + umur UNVERIFIED -> watchlist-only, BUKAN lead/kandidat, TIDAK di-preview/di-mint. DIAM."
    notes.append(al["runNote1901_1116"])
# Vezlune opened 19:00:11 WIB, free pool 100/100 SOLD OUT
vz=snap["contracts"].get("Vezlune")
if vz is not None:
    vz["totalSupply"]=100; vz["totalMinted"]=100; vz["freeMinted"]=100; vz["FREE_SUPPLY"]=100; vz["MAX_SUPPLY"]=700
    vz["mintOpen"]=1; vz["saleOpen"]=1; vz["saleStart"]=1794830411
    vz["status"]="sold-out-free-2026-11-16"
    vz["lastReadBlock"]=133925375; vz["lastReadWib"]="2026-11-16 ~19:01 WIB"
    vz["runNote1901_1116"]="Run 1901: Vezlune BUKA 19:00:11 WIB (saleStart 1794830411) dan free pool LANGSUNG HABIS: freeMinted 100/100. Tidak pernah dilaporkan sebagai lead (pre-launch watchlist-only) -> DIAM, dicatat sold-out-free, tidak dibaca ulang sebagai kandidat."
    notes.append(vz["runNote1901_1116"])
# Track B pending claim re-check (reread)
pc_claim=snap.get("pending_claims",{}).get("binanceai.fun")
if pc_claim is not None:
    pc_claim["launched"]=0; pc_claim["failed"]=1; pc_claim["isRefundPhase"]=1; pc_claim["tokenClaimed_user"]=0
    pc_claim["lastReadBlock"]=133924439; pc_claim["lastReadWib"]="2026-11-16 ~19:01 WIB"
    pc_claim["runNote1901_1116"]="Run 1901: launched=0, failed=1, isRefundPhase=1, totalShares=3110, tokenClaimed(user)=0 (blok 133924439) - tetap fase refund, klaim BELUM terbuka. DIAM."
    notes.append(pc_claim["runNote1901_1116"])
snap["last_run"]="2026-11-16 ~19:01 WIB"
json.dump(snap, open(BASE+"onchain-snapshot.json","w"), indent=1)
print("contracts:", len(snap.get("contracts",{})), "track_c:", len(tc))
for n in notes: print("-", n)
print("MERGE DONE")
