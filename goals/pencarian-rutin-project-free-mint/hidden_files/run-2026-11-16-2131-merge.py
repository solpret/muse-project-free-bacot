#!/usr/bin/env python3
"""Merge run 2131 reads into onchain-snapshot.json. Read-only on chain; writes snapshot only.
Fresh script for 2131 (the 2031 clone carried stale hardcoded 2031 blocks - not reused)."""
import json, shutil
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
snap=json.load(open(BASE+"onchain-snapshot.json"))
rr=json.load(open(BASE+"run-2026-11-16-2131-reread.json"))
BLOCK=rr["block"]  # 133944864
INTERVAL_MIN=round((133944864-133939647)*0.45/60, 2)  # 39.13 vs run 2031
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
    e["lastReadWib"]="2026-11-16 ~21:31 WIB"
    free=e.get("freeMinted") if e.get("freeMinted") is not None else e.get("freeClaimed")
    cap=e.get("FREE_SUPPLY") if e.get("FREE_SUPPLY") is not None else (e.get("FREE_CAP") if e.get("FREE_CAP") is not None else e.get("FREE_MAX"))
    pct=(round(100*free/cap,1) if isinstance(free,int) and isinstance(cap,int) and cap else None)
    if pct is not None: e["freePctVerified"]=pct
    vel_summary[name]=(minted, None if rate is None else round(rate,3), None if ratio is None else round(ratio,2), vel, pct)
    e["runNote2131_1116"]=(f"Run 2131 (blok {BLOCK}, interval ~{INTERVAL_MIN} mnt vs run 2031): "
        f"supply {prev_sup}->{ns} (+{minted}), rate {rate if rate is None else round(rate,3)}/mnt vs prev {prev_rate} = {ratio if ratio is None else round(ratio,2)}x, "
        f"velocity {'LOLOS' if vel else 'GAGAL'}; free={free}/{cap} ({pct}% )" if pct is not None else f"free% UNVERIFIED; ")
    if name=="BinanceAI-mint":
        e["runNote2131_1116"]=f"Run 2131: launched=0, failed=1, isRefundPhase=1, totalShares=3110, tokenClaimed(user)=0 (blok {BLOCK}) - tetap fase refund, klaim BELUM terbuka. DIAM."
    if name=="RigForge":
        e["runNote2131_1116"]=f"Run 2131: freeSharesLeft 636 FLAT, openedAt 0, freeClaimed 364, freeBooked(user)=10.000 RIG (blok {BLOCK}). DIAM."
    if name=="DogeRageFi":
        e["runNote2131_1116"]=f"Run 2131: totalMinted 229 (+1), freeSupply 432/666, mintOpen 1, bal_user 0 (blok {BLOCK}). Watchlist-only-age-unverified. DIAM."
    if name=="Zero":
        e["runNote2131_1116"]=f"Run 2131: totalSupply/freeClaimed gagal dibaca lagi (None); balanceOf(user)=0. Nilai lama dipertahankan, velocity tidak dihitung. DIAM."
print("velocity summary:")
for k,v in vel_summary.items(): print(" ",k,v)
print("notes:", notes)
# --- new entries: Nova / Aero A2 / F018 / Xuanwu ---
snap["contracts"]["NovaAgent-e471"]={
 "address":"0xe471c0e3e61837d3aa4b19bc6c2ac402f91e9b6f","name":"Nova Agent","kind":"ERC721",
 "status":"checked-not-lead-2026-11-16","totalSupply":4901,"totalMinted":4901,"PRE_MINT":4900,
 "MAX_SUPPLY":5000,"mintedBy_user":0,"balanceOf_user":0,
 "baselineNote":"Boltbook EN run 2131, post tetternice.ai (recheck 21:24): klaim 4.901/5.001 free (98%). Verifikasi sendiri run 2131: PRE_MINT 4900 dari totalSupply 4901 (hanya 1 mint publik), mint(1) value 0 REVERT 0x3c6b4b28, free views semua revert, Sourcify 404 (unverified), bytecode IDENTIK dgn Aero A1 0x62f8... (checked-not-lead run 1901). Klaim 98% free = framing PRE_MINT, BUKAN kuota gratis. Bukan lead, bukan kandidat. DIAM.",
 "firstSeenBlock":133944864,"lastReadBlock":133944864,"lastReadWib":"2026-11-16 ~21:31 WIB"}
snap["contracts"]["AeroAgent-e0a3"]={
 "address":"0xe0a32f2658fe46eff4755fdc4c8c67933e847c93","name":"Aero Agents A2","kind":"ERC721",
 "status":"checked-not-lead-2026-11-16","totalSupply":4901,"totalMinted":4901,"PRE_MINT":4901,
 "MAX_SUPPLY":5000,"mintedBy_user":0,"balanceOf_user":0,
 "baselineNote":"Boltbook EN run 2131, post shikifujin.ai: PRE_MINT 4.900/4.900 = seluruh supply milik tim, public mint reverts. Verifikasi sendiri run 2131: PRE_MINT 4901 = totalSupply 4901, mint(1) value 0 REVERT 0x3c6b4b28, free views revert, Sourcify 404. Bukan lead. DIAM.",
 "firstSeenBlock":133944864,"lastReadBlock":133944864,"lastReadWib":"2026-11-16 ~21:31 WIB"}
snap["contracts"]["XuanwuSeed-05fd"]={
 "address":"0x05fd19702029c473683d6188cD856e59038278F4","name":"Xuanwu Seed","kind":"ERC1155",
 "status":"checked-sold-out-2026-11-16","totalSupply":9909,"totalMinted":10000,"MAX_SUPPLY":10000,
 "mintOpen":1,"balanceOf_user":0,"mintCount_user":0,
 "baselineNote":"Sweep ZH run 2131 (seed.mchain.art, EX-00 Phase 2, first seed FREE, .ai-gated). Verifikasi sendiri run 2131: totalMinted 10000/10000 (totalSupply 9909, 91 consumed), quote(user,1)=0 + mintCount(user)=0 TAPI supply habis -> mint revert; Sourcify exact_match; site seed.mchain.art. SOLD OUT, bukan lead/kandidat. Umur tidak diverifikasi (tidak perlu - sold out). DIAM.",
 "firstSeenBlock":133944864,"lastReadBlock":133944864,"lastReadWib":"2026-11-16 ~21:31 WIB"}
# F018 -> track_c (S1 shape but free pool exhausted)
tc["F018-sale"]={
 "sale":"0xF0186519cff9830273Dc052451830308846D2813",
 "token":"0x0a98091ed4ffa64f2543cf85bf31aa34192724b6",
 "pair":"0xf8d4c559dccfdabe6664b11b95700a111fdd548d",
 "status":"checked-not-lead-free-pool-exhausted-2026-11-16",
 "saleShape":"S1 PASS (mint+quote+freeMinted+registry 0x60B9...022F, exact_match) TAPI free pool HABIS",
 "FREE_SHARES":333,"freeMinted":333,"freeRemaining":0,"SHARES":10000,"minted":4954,"paidMinted":4621,
 "remaining":5046,"TOKENS_PER_SHARE":2350000000000000000000,"PRICE":1000000000000000000,
 "started":1,"launched":0,"launchTime":0,"paidStart":1794837586,"freeBy_user":0,
 "baselineNote":"Sourcify feed run 2131 (verifiedAt 14:00:10Z), shape S1. Verifikasi sendiri: FREE_SHARES 333 = freeMinted 333, freeRemaining 0, mintFree() static call REVERT FREE_OUT. Pool gratis habis sebelum jadi lead; tidak pernah dilaporkan sebagai lead. DIAM.",
 "lastReadWib":"2026-11-16 ~21:31 WIB"}
# feedshape 9 contracts -> track_c checked-not-sale-shape
fs=json.load(open(BASE+"run-2026-11-16-2131-feedshape.json"))
for addr, r in fs.items():
    key="feedshape-"+addr[2:6].lower()+"-2131"
    tc[key]={"address":addr,"status":"checked-not-sale-shape-2026-11-16-2131",
             "shape":r.get("shape"),"fns":r.get("fns"),"mint":r.get("mint"),"quote":r.get("quote"),
             "free_views":r.get("free_views"),"registry":r.get("registry"),"token":r.get("token"),
             "mintFree":r.get("mintFree"),"lastReadWib":"2026-11-16 ~21:31 WIB",
             "baselineNote":"Sourcify feed run 2131, shape-check S1/S2."}
snap["last_run"]="2026-11-16 ~21:31 WIB"
snap["last_run_block"]=BLOCK
json.dump(snap, open(BASE+"onchain-snapshot.json","w"), indent=1)
print("snapshot saved. contracts:", len(snap["contracts"]), "track_c:", len(tc))
