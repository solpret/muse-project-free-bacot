#!/usr/bin/env python3
"""Merge run 2231 reads into onchain-snapshot.json. Fresh script for 2231.
Reads run-2026-11-16-2231-reread.json (block 133952481) vs run 2201 (block 133948375).
Interval = (133952481-133948375)*0.45/60 = 30.80 min. Also adds Woof Agent early lead
and 8 Sourcify feedshape results to track_c. Read-only on chain; writes snapshot only."""
import json
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
snap=json.load(open(BASE+"onchain-snapshot.json"))
rr=json.load(open(BASE+"run-2026-11-16-2231-reread.json"))
fs=json.load(open(BASE+"run-2026-11-16-2231-feedshape.json"))
BLOCK=rr["block"]
INTERVAL_MIN=round((133952481-133948375)*0.45/60,2)
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
vel_summary={}
for name, r in rr["reads"].items():
    addr=r["address"].lower(); views=r.get("views")
    if views is None:
        print(name,"READ-FAIL"); continue
    ent=None; where=None
    if addr in byaddr: ent=byaddr[addr]; where="contracts"
    else:
        for k,v in tc.items():
            if isinstance(v,dict) and (v.get("address") or (v.get("sale")) or "").lower()==addr:
                ent=(k,v); where="track_c"; break
    if ent is None:
        print(name,"no snapshot entry, skipped"); continue
    key, e = ent
    prev_sup = supply_of(e)
    ns = new_supply(views)
    minted = (ns - prev_sup) if isinstance(ns,int) and isinstance(prev_sup,int) else None
    # PXIO: snapshot totalMinted was set None run 2201 so series uses totalSupply (see run 2201 note)
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
    e["lastReadWib"]="2026-11-16 ~22:31 WIB"
    free=e.get("freeMinted") if e.get("freeMinted") is not None else e.get("freeClaimed")
    cap=e.get("FREE_SUPPLY") if e.get("FREE_SUPPLY") is not None else (e.get("FREE_CAP") if e.get("FREE_CAP") is not None else e.get("FREE_MAX"))
    pct=(round(100*free/cap,1) if isinstance(free,int) and isinstance(cap,int) and cap else None)
    if pct is not None: e["freePctVerified"]=pct
    vel_summary[name]=(minted, None if rate is None else round(rate,3), None if ratio is None else round(ratio,2), vel, pct)
    if name=="BinanceAI-mint":
        note=f"Run 2231: launched={views.get('launched')}, failed={views.get('failed')}, isRefundPhase={views.get('isRefundPhase')}, totalShares={views.get('totalShares')}, tokenClaimed(user)={views.get('tokenClaimed_user')} (blok {BLOCK}) - tetap fase refund, klaim BELUM terbuka. DIAM."
    elif name=="RigForge":
        note=f"Run 2231: freeSharesLeft={views.get('freeSharesLeft')}, openedAt={views.get('openedAt')}, freeClaimed={views.get('freeClaimed')}, freeBooked(user)={views.get('freeBooked_user')} (blok {BLOCK}). DIAM."
    elif name=="DogeRageFi":
        note=f"Run 2231: totalMinted={views.get('totalMinted')}, freeSupply={views.get('freeSupply')}, mintOpen={views.get('mintOpen')}, bal_user={views.get('balanceOf_user')} (blok {BLOCK}). Watchlist-only-age-unverified. DIAM."
    elif name=="Zero":
        note=f"Run 2231: totalSupply/freeClaimed={'gagal dibaca lagi (None); nilai lama dipertahankan, velocity tidak dihitung' if views.get('totalSupply') is None else 'terbaca'}; balanceOf(user)={views.get('balanceOf_user')}. DIAM."
    elif name=="PXIO":
        note=(f"Run 2231 (blok {BLOCK}, interval ~{INTERVAL_MIN} mnt vs run 2201): supply {prev_sup}->{ns} (+{minted}), rate {round(rate,3)}/mnt vs prev {prev_rate} = {round(ratio,2)}x, velocity {'LOLOS' if vel else 'GAGAL'} (turun dari LOLOS run 2201); free% + umur tetap UNVERIFIED. Tetap EARLY lead. DIAM.")
    elif pct is not None:
        note=(f"Run 2231 (blok {BLOCK}, interval ~{INTERVAL_MIN} mnt vs run 2201): supply {prev_sup}->{ns} (+{minted}), rate {None if rate is None else round(rate,3)}/mnt vs prev {prev_rate} = {None if ratio is None else round(ratio,2)}x, velocity {'LOLOS' if vel else 'GAGAL'}; free={free}/{cap} ({pct}%)")
    else:
        note=(f"Run 2231 (blok {BLOCK}, interval ~{INTERVAL_MIN} mnt vs run 2201): supply {prev_sup}->{ns} (+{minted}), rate {None if rate is None else round(rate,3)}/mnt vs prev {prev_rate} = {None if ratio is None else round(ratio,2)}x, velocity {'LOLOS' if vel else 'GAGAL'}; free% UNVERIFIED")
    e["runNote2231_1116"]=note
print("velocity summary:")
for k,v in vel_summary.items(): print(" ",k,v)
# --- Woof Agent early lead (new from Boltbook run 2231) ---
woof_addr="0xBb9bA68C8E99651450F099C431eb530a71C712bE"
snap.setdefault("contracts",{})["Woof Agent"]={
 "address":woof_addr,"name":"Woof Agent","symbol":"WOOF",
 "status":"early-lead-2026-11-16",
 "totalSupply":99,"totalMinted":99,"freeMinted":99,"MAX_SUPPLY":1111,
 "mintOpen":1,"balanceOf_user":0,
 "freePctVerified":8.9,
 "website":"https://woof-agent.vercel.app",
 "website_evidence":"site HTTP 200, mencetak kontrak persis 2x (run 2231)",
 "agent_shaped":"registry bytes TRUE (0x60B9...22F di bytecode 11028 byte) + mintFree() + freeMinted counter",
 "age_verified":False,
 "age_note":"first-mint log TIDAK terverifikasi run ini: Ankr 401; eth_getLogs publik 0 log mint 20.000 blok terakhir (dataseed) + rate-limit publicnode; umur UNVERIFIED",
 "user_slot":"UNVERIFIED - freeMintedBy/mintedBy/freeClaimed/hasFreeMint revert (fungsi tidak ada); balanceOf(user)=0; mintFree() value 0 hanya dari wallet poster Boltbook, bukan wallet user",
 "discussion":"Boltbook front page EN+ZH, post tesnetra.ai ~4 mnt sebelum fetch 2231: 'Woof Agent (WOOF, BSC) recheck: 88/1,111 - mintFree() value 0 passes from my wallet, 1 free then 0.00035 BNB'",
 "x_verified":False,
 "velocityLegPasses":False,"currentRatePerMin":None,
 "lastReadBlock":133953124,"lastReadWib":"2026-11-16 ~22:31 WIB",
 "runNote2231_1116":"Run 2231: EARLY LEAD baru dari Boltbook. Agent-shaped (registry bytes TRUE), website terverifikasi (woof-agent.vercel.app mencetak kontrak persis), free 99/1111=8,9% (<50%, <70%), mintOpen=1, bal_user=0. Umur UNVERIFIED (log first-mint tak terambil: Ankr 401 + RPC publik gagal/rate-limit). Slot gratis user UNVERIFIED (view per-wallet revert). BUKAN kandidat, BUKAN strong lead. TIDAK di-preview/di-mint. Dilaporkan sekali sebagai EARLY lead run 2231."
}
# --- Sourcify feedshape results into track_c ---
for addr, res in fs.items():
    key="Feed-"+addr[2:6]
    shape=res.get("shape")
    status="checked-not-sale-shape-2026-11-16" if shape=="checked-not-sale-shape" else ("checked-abi-unavailable-2026-11-16" if shape=="abi-unavailable" else shape)
    tc[key]={"address":addr,"status":status,"S1":shape=="S1","S2":shape=="S2",
      "has_mint":res.get("mint"),"has_quote":res.get("quote"),"free_views":res.get("free_views"),
      "agent_ref":res.get("registry"),"is_token":res.get("token"),"n_fns":res.get("fns"),
      "note":f"Sourcify feed run 2231: {shape}."}
    print("track_c added:",key,status)
snap["last_run"]="2026-11-16 ~22:31 WIB"
snap["last_run_wib"]="2026-11-16 ~22:31 WIB"
snap["runNote2231"]="Run 2231 (22:31 WIB, blok 133952481): 1 EARLY LEAD baru - Woof Agent 0xBb9b...712bE (agent-shaped registry bytes, website woof-agent.vercel.app terverifikasi, free 99/1111=8,9%, umur + slot user UNVERIFIED). PXIO velocity LOLOS->GAGAL (1,32x). Punch Card +11 velocity GAGAL (<20). Scan Ankr pre-flight FAIL 401 (watermark tetap 132512564, gap ~1,44jt blok). Boltbook 5 alamat baru vs 2201, 4 sudah dikenal, 1 Woof baru. Sourcify 8 baru vs 2201: 5 not-sale-shape, 3 abi-unavailable. Poffzi masih pra-launch (buka 23:00:11 WIB). BinanceAI tetap refund. DIAM selain Woof."
json.dump(snap, open(BASE+"onchain-snapshot.json","w"), indent=1)
print("snapshot saved. contracts:",len(snap["contracts"]),"track_c:",len(tc))
