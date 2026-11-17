#!/usr/bin/env python3
"""Merge run 2201 reads into onchain-snapshot.json. Fresh script for 2201 (NOT a clone of 2131:
the 2131 script carries 2131-specific hardcoded entries/notes - Nova/Aero/Xuanwu/F018,
DogeRageFi +1, BinanceAI totalShares 3110, RigForge 636 FLAT - which are stale for 2201).
Read-only on chain; writes snapshot only."""
import json
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
snap=json.load(open(BASE+"onchain-snapshot.json"))
rr=json.load(open(BASE+"run-2026-11-16-2201-reread.json"))
BLOCK=rr["block"]  # 133948375
INTERVAL_MIN=round((133948375-133944864)*0.45/60, 2)  # 26.33 vs run 2131
byaddr={}
for k,v in snap.get("contracts",{}).items():
    if isinstance(v,dict) and v.get("address"): byaddr[v["address"].lower()]=(k,v)
tc=snap.setdefault("track_c",{})
def supply_of(v):
    if v.get("totalMinted") is not None: return v.get("totalMinted")
    return v.get("totalSupply")
def new_supply(views):
    if views.get("totalMinted") is not None: return views.get("totalMinted")
    return views.get("totalSupply")
FIELDS=["totalSupply","totalMinted","freeMinted","freeClaimed","FREE_SUPPLY","FREE_CAP","FREE_MAX","MAX_SUPPLY","mintOpen","mintOpensAt","paused","isFreePhase","freeRemaining","paidMinted","mintPrice","freeMintsLeft","FREE_MINT_CAP","PRICE","TOKEN_PRICE","remainingSupply","totalShares","launched","failed","isRefundPhase","claimOpen","totalSpecimens","currentExperiment","genesisStart","genesisOpen","freeSharesLeft","openedAt","freeSupply","maxSupply","saleStart","saleOpen","saleEnd","mintStart"]
UFIELDS=["balanceOf_user","freeMintedPerWallet_user","mintedPerWallet_user","mintedByWallet_user","hasAgentId_user","holdsAgentId_user","freeUsed_user","freeClaimed_user","mintsBy_user","mintCountOf_user","mintedBy_user","hasFreeClaimed_user","tokenClaimed_user","freeBooked_user","priceFor_user","priceFor_user_1","mintPriceFor_user_1","cost_user_1","freeClaimedByAgent_masgayut","freeClaimedByAgent_masgayut_ai"]
notes=[]
vel_summary={}
for name, r in rr["reads"].items():
    addr=r["address"].lower(); views=r.get("views")
    if views is None:
        notes.append(f"{name}: READ-FAIL all views"); continue
    ent=None; where=None
    if addr in byaddr: ent=byaddr[addr]; where="contracts"
    else:
        for k,v in tc.items():
            if isinstance(v,dict) and (v.get("address") or (v.get("sale")) or "").lower()==addr:
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
    for f in FIELDS+UFIELDS:
        if f in views and views[f] is not None: e[f]=views[f]
    e["previousTotalSupply"]=prev_sup
    e["mintedInInterval"]=minted
    e["intervalMinutes"]=INTERVAL_MIN
    e["previousRatePerMin"]=prev_rate
    e["currentRatePerMin"]=rate
    e["velocityRatio"]=ratio
    e["velocityLegPasses"]=vel
    e["lastReadBlock"]=BLOCK
    e["lastReadWib"]="2026-11-16 ~22:01 WIB"
    free=e.get("freeMinted") if e.get("freeMinted") is not None else e.get("freeClaimed")
    cap=e.get("FREE_SUPPLY") if e.get("FREE_SUPPLY") is not None else (e.get("FREE_CAP") if e.get("FREE_CAP") is not None else e.get("FREE_MAX"))
    pct=(round(100*free/cap,1) if isinstance(free,int) and isinstance(cap,int) and cap else None)
    if pct is not None: e["freePctVerified"]=pct
    vel_summary[name]=(minted, None if rate is None else round(rate,3), None if ratio is None else round(ratio,2), vel, pct)
    if pct is not None:
        note=(f"Run 2201 (blok {BLOCK}, interval ~{INTERVAL_MIN} mnt vs run 2131): "
            f"supply {prev_sup}->{ns} (+{minted}), rate {rate if rate is None else round(rate,3)}/mnt vs prev {prev_rate} = {ratio if ratio is None else round(ratio,2)}x, "
            f"velocity {'LOLOS' if vel else 'GAGAL'}; free={free}/{cap} ({pct}%)")
    else:
        note=(f"Run 2201 (blok {BLOCK}, interval ~{INTERVAL_MIN} mnt vs run 2131): "
            f"supply {prev_sup}->{ns} (+{minted}), rate {rate if rate is None else round(rate,3)}/mnt vs prev {prev_rate} = {ratio if ratio is None else round(ratio,2)}x, "
            f"velocity {'LOLOS' if vel else 'GAGAL'}; free% UNVERIFIED")
    if name=="BinanceAI-mint":
        note=f"Run 2201: launched={views.get('launched')}, failed={views.get('failed')}, isRefundPhase={views.get('isRefundPhase')}, totalShares={views.get('totalShares')}, tokenClaimed(user)={views.get('tokenClaimed_user')} (blok {BLOCK}) - tetap fase refund, klaim BELUM terbuka. DIAM."
    if name=="RigForge":
        note=f"Run 2201: freeSharesLeft={views.get('freeSharesLeft')}, openedAt={views.get('openedAt')}, freeClaimed={views.get('freeClaimed')}, freeBooked(user)={views.get('freeBooked_user')} (blok {BLOCK}). DIAM."
    if name=="DogeRageFi":
        note=f"Run 2201: totalMinted={views.get('totalMinted')}, freeSupply={views.get('freeSupply')}, mintOpen={views.get('mintOpen')}, bal_user={views.get('balanceOf_user')} (blok {BLOCK}). Watchlist-only-age-unverified. DIAM."
    if name=="Zero":
        note=f"Run 2201: totalSupply/freeClaimed={'gagal dibaca lagi (None); nilai lama dipertahankan, velocity tidak dihitung' if views.get('totalSupply') is None else 'terbaca'}; balanceOf(user)={views.get('balanceOf_user')}. DIAM."
    e["runNote2201_1116"]=note
print("velocity summary:")
for k,v in vel_summary.items(): print(" ",k,v)
print("notes:", notes)
# --- new feedshape entry 2201: 0x04c2... only new Sourcify contract vs 2131 ---
fs=json.load(open(BASE+"run-2026-11-16-2201-feedshape.json"))
for addr, r in fs.items():
    key="feedshape-"+addr[2:6].lower()+"-2201"
    tc[key]={"address":addr,"status":"checked-not-sale-shape-2026-11-16-2201",
             "shape":r.get("shape"),"fns":r.get("fns"),"mint":r.get("mint"),"quote":r.get("quote"),
             "free_views":r.get("free_views"),"registry":r.get("registry"),"token":r.get("token"),
             "mintFree":r.get("mintFree"),"lastReadWib":"2026-11-16 ~22:01 WIB",
             "baselineNote":"Sourcify feed run 2201, shape-check S1/S2."}
snap["last_run"]="2026-11-16 ~22:01 WIB"
snap["last_run_block"]=BLOCK
json.dump(snap, open(BASE+"onchain-snapshot.json","w"), indent=1)
print("snapshot saved. contracts:", len(snap["contracts"]), "track_c:", len(tc))
