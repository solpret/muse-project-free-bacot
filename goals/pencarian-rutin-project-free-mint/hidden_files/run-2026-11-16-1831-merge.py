#!/usr/bin/env python3
"""Merge run 1831 reads into onchain-snapshot.json. Read-only on chain; writes snapshot only."""
import json, shutil
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
snap=json.load(open(BASE+"onchain-snapshot.json"))
rr=json.load(open(BASE+"run-2026-11-16-1831-reread.json"))
BLOCK=rr["block"]  # 133920769
INTERVAL_MIN=32.6  # 1801 block 133916418 -> 1831 block 133920769 (+4351 blok x ~0,45 dtk)
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
    for f in ["totalSupply","totalMinted","freeMinted","freeClaimed","FREE_SUPPLY","FREE_CAP","FREE_MAX","MAX_SUPPLY","mintOpen","mintOpensAt","paused","isFreePhase","freeRemaining","paidMinted","mintPrice","freeMintsLeft","FREE_MINT_CAP","PRICE","TOKEN_PRICE","remainingSupply","totalShares","launched","failed","isRefundPhase","claimOpen","totalSpecimens","currentExperiment","genesisStart","genesisOpen"]:
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
    e["lastReadWib"]="2026-11-16 ~18:31 WIB"
    free=e.get("freeMinted", e.get("freeClaimed"))
    cap=e.get("FREE_SUPPLY", e.get("FREE_CAP", e.get("FREE_MAX")))
    pct=(round(100*free/cap,1) if isinstance(free,int) and isinstance(cap,int) and cap else None)
    if pct is not None: e["freePctVerified"]=pct
    e["runNote1831_1116"]=(f"Run 1831 (blok {BLOCK}, interval ~{INTERVAL_MIN} mnt vs run 1801): "
        f"{prev_sup}->{ns} (+{minted}, {(f'{rate:.3f}' if rate is not None else '?')}/mnt vs prev {prev_rate} = {(round(ratio,2) if ratio is not None else '?')}x) -> velocity {'LOLOS' if vel else 'GAGAL'}; "
        f"free={free}/{cap} ({pct}%)" if pct is not None else f"free={free}")
    notes.append(e["runNote1831_1116"])
# RAVE: fix stale totalSupply 84 -> 355 (totalMinted already 355 at 1801; verify fresh 355)
rave=None
for k,v in snap.get("contracts",{}).items():
    if (v.get("address") or "").lower()=="0x7c40b78992d86edfffe5553c74db5ef427100bb95".lower():
        rave=v; break
if rave is not None:
    rave["totalSupply"]=355
    rave["runNote1831_1116"]="Run 1831: totalMinted 355 FLAT vs 1801 (355); totalSupply snapshot yang basi (84) dikoreksi ke 355. freeMinted 355/3000=11,8%. Early lead sudah dilaporkan 14 Nov; umur+X+website unverified. DIAM."
    notes.append(rave["runNote1831_1116"])
# Punch Card verify (fresh read, not in reread ITEMS)
pc=None
for k,v in snap.get("contracts",{}).items():
    if (v.get("address") or "").lower()=="0x1d4ef0587dd3ff3875a141d4711c60bca40587c4":
        pc=v; break
if pc is not None:
    prev=pc.get("totalSupply"); prev_rate=pc.get("currentRatePerMin")
    minted=643-prev if isinstance(prev,int) else None
    rate=minted/INTERVAL_MIN if minted is not None else None
    ratio=(rate/prev_rate) if (rate is not None and prev_rate not in (None,0)) else None
    pc["previousTotalSupply"]=prev; pc["totalSupply"]=643; pc["freeMinted"]=642
    pc["mintedInInterval"]=minted; pc["intervalMinutes"]=INTERVAL_MIN
    pc["previousRatePerMin"]=prev_rate; pc["currentRatePerMin"]=rate; pc["velocityRatio"]=ratio
    pc["velocityLegPasses"]=bool(minted is not None and minted>=20 and ratio is not None and ratio>=1.5)
    pc["freePctVerified"]=round(100*642/5555,1)
    pc["lastReadBlock"]=BLOCK; pc["lastReadWib"]="2026-11-16 ~18:31 WIB"
    pc["runNote1831_1116"]=f"Run 1831 (verify, blok {BLOCK}): totalSupply {prev}->643 (+{minted}, {rate:.3f}/mnt vs prev {prev_rate} = {ratio if ratio is None else round(ratio,2)}x) -> velocity GAGAL; freeMinted 642/5555=11,6% (<50% kandidat, <70% strong lead) -> tetap EARLY lead saja, TANPA promosi. DIAM."
    notes.append(pc["runNote1831_1116"])
# Feedshape 4 new -> track_c checked-not-sale-shape
fs=json.load(open(BASE+"run-2026-11-16-1831-feedshape.json"))
for addr, d in fs.items():
    key="feedshape-"+addr[2:6].lower()+"-1831"
    tc[key]={"address":addr,"status":"checked-not-sale-shape-2026-11-16-1831","shape":d.get("shape"),
             "fns":d.get("fns"),"mint":d.get("mint"),"quote":d.get("quote"),"free_views":d.get("free_views"),
             "registry":d.get("registry"),"token":d.get("token"),"mintFree":d.get("mintFree"),
             "lastReadWib":"2026-11-16 ~18:31 WIB",
             "baselineNote":"Sourcify feed run 1831 (verifiedAt 11:25-11:34Z, baru vs hot-leg 1819): bukan sale-shape S1/S2 (tanpa free views / tanpa registry ref). Bukan lead. DIAM."}
# Boltbook 2 'new' addresses -> checked, not leads
tc["boltbook-SPEC-1831"]={"address":"0x639329f5dc4317c44D9Fed961a1217ba845012F7","status":"checked-not-lead-2026-11-16-1831",
    "lastReadWib":"2026-11-16 ~18:31 WIB",
    "baselineNote":"Boltbook EN/ZH run 1831: SPEC contract LumenFindings (disebut di post FIND exp28 hi5.ai) - age-excluded run 1231, bukan proyek baru. Bukan lead. DIAM."}
tc["boltbook-DEGEN-1831"]={"address":"0xe332e73084e22b4075ee3f427fc6361930f5b341","status":"checked-not-lead-2026-11-16-1831",
    "lastReadWib":"2026-11-16 ~18:31 WIB",
    "baselineNote":"Boltbook EN/ZH run 1831: token DEGEN (BSC) biasa, post verifikasi cskh.ai - bukan free mint Agent ID, bukan sale-shape. Bukan lead. DIAM."}
snap["last_run"]="2026-11-16 ~18:31 WIB"
json.dump(snap, open(BASE+"onchain-snapshot.json","w"), indent=1)
print("contracts:", len(snap.get("contracts",{})), "track_c:", len(tc))
for n in notes: print("-", n)
print("MERGE DONE")
