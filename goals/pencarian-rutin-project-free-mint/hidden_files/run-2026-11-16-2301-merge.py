#!/usr/bin/env python3
"""Merge run 2301 reads into onchain-snapshot.json. Fresh script for 2301.
Reads run-2026-11-16-2301-reread.json (block 133952481) vs run 2201 (block 133948375).
Interval = (133952481-133948375)*0.45/60 = 30.80 min. Also adds Woof Agent early lead
and 8 Sourcify feedshape results to track_c. Read-only on chain; writes snapshot only."""
import json
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
snap=json.load(open(BASE+"onchain-snapshot.json"))
rr=json.load(open(BASE+"run-2026-11-16-2301-reread.json"))
fs=json.load(open(BASE+"run-2026-11-16-2301-feedshape.json"))
BLOCK=rr["block"]
INTERVAL_MIN=round((133957032-133952481)*0.45/60,2)
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
FIELDS=["totalSupply","totalMinted","freeMinted","freeClaimed","FREE_SUPPLY","FREE_CAP","FREE_MAX","MAX_SUPPLY","mintOpen","mintOpensAt","paused","isFreePhase","freeRemaining","paidMinted","mintPrice","freeMintsLeft","FREE_MINT_CAP","PRICE","TOKEN_PRICE","remainingSupply","totalShares","launched","failed","isRefundPhase","claimOpen","totalSpecimens","currentExperiment","genesisStart","genesisOpen","freeSharesLeft","openedAt","freeSupply","maxSupply","saleStart","saleOpen","saleEnd","mintStart","started_raw","failed_raw"]
UFIELDS=["balanceOf_user","freeMintedPerWallet_user","mintedPerWallet_user","mintedByWallet_user","hasAgentId_user","holdsAgentId_user","freeUsed_user","freeClaimed_user","mintsBy_user","mintCountOf_user","mintedBy_user","hasFreeClaimed_user","tokenClaimed_user","freeBooked_user","freeDone_user","priceFor_user","priceFor_user_1","mintPriceFor_user_1","cost_user_1","freeClaimedByAgent_masgayut","freeClaimedByAgent_masgayut_ai"]
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
        note=f"Run 2301: launched={views.get('launched')}, failed={views.get('failed')}, isRefundPhase={views.get('isRefundPhase')}, totalShares={views.get('totalShares')}, tokenClaimed(user)={views.get('tokenClaimed_user')} (blok {BLOCK}) - tetap fase refund, klaim BELUM terbuka. DIAM."
    elif name=="RigForge":
        note=f"Run 2301: freeSharesLeft={views.get('freeSharesLeft')}, openedAt={views.get('openedAt')}, freeClaimed={views.get('freeClaimed')}, freeBooked(user)={views.get('freeBooked_user')} (blok {BLOCK}). DIAM."
    elif name=="DogeRageFi":
        note=f"Run 2301: totalMinted={views.get('totalMinted')}, freeSupply={views.get('freeSupply')}, mintOpen={views.get('mintOpen')}, bal_user={views.get('balanceOf_user')} (blok {BLOCK}). Watchlist-only-age-unverified. DIAM."
    elif name=="Zero":
        note=f"Run 2301: totalSupply/freeClaimed={'gagal dibaca lagi (None); nilai lama dipertahankan, velocity tidak dihitung' if views.get('totalSupply') is None else 'terbaca'}; balanceOf(user)={views.get('balanceOf_user')}. DIAM."
    elif name=="PXIO":
        note=(f"Run 2301 (blok {BLOCK}, interval ~{INTERVAL_MIN} mnt vs run 2231): supply {prev_sup}->{ns} (+{minted}), rate {round(rate,3)}/mnt vs prev {prev_rate} = {round(ratio,2)}x, velocity {'LOLOS' if vel else 'GAGAL'}; free% + umur tetap UNVERIFIED. Tetap EARLY lead. DIAM.")
    elif pct is not None:
        note=(f"Run 2301 (blok {BLOCK}, interval ~{INTERVAL_MIN} mnt vs run 2231): supply {prev_sup}->{ns} (+{minted}), rate {None if rate is None else round(rate,3)}/mnt vs prev {prev_rate} = {None if ratio is None else round(ratio,2)}x, velocity {'LOLOS' if vel else 'GAGAL'}; free={free}/{cap} ({pct}%)")
    else:
        note=(f"Run 2301 (blok {BLOCK}, interval ~{INTERVAL_MIN} mnt vs run 2231): supply {prev_sup}->{ns} (+{minted}), rate {None if rate is None else round(rate,3)}/mnt vs prev {prev_rate} = {None if ratio is None else round(ratio,2)}x, velocity {'LOLOS' if vel else 'GAGAL'}; free% UNVERIFIED")
    e["runNote2301_1116"]=note
print("velocity summary:")
for k,v in vel_summary.items(): print(" ",k,v)
# --- Poffzi / Vezlune / BUBB special handling (run 2301) ---
poff = snap["contracts"].get("Poffzi")
if poff is not None:
    poff["status"] = "sold-out-free-2026-11-16"
    poff["totalSupply"] = 100; poff["totalMinted"] = 100; poff["freeMinted"] = 100
    poff["runNote2301_1116"] = ("Run 2301: POFFZI SOLD OUT GRATIS. Sale buka 23:00:11 WIB; trigger fcfs 23:00:17 WIB freeMinted 2 (98 tersisa, blok 133955842); "
      "preview 23:00:22 WIB (requestId 50e28f80acfe463a8be48e82e18bc1ee) mengembalikan struktur BARU baw (kunci expiresAt/gasLimit/parsedTx/requestId/requireConfirmation/risks/simulationResult/tokenInfos, tanpa simulationCode top-level) -> parser fcfs_fast fail-closed, loop TERMINAL, TIDAK ADA mint. "
      "Reread run 2301 (blok 133957032, ~23:04 WIB): freeMinted 97/100 (3 tersisa), freeDone(user)=0, slot user masih terbuka. Preview ulang manual ~23:06 WIB: 351805 SERVICE_ERROR 'execution reverted'. "
      "Baca ulang langsung blok 133957194 (~23:10 WIB): freeMinted 100/100, totalSupply 100 — KUOTA GRATIS HABIS (~10 mnt sejak buka, laju ~30/mnt). "
      "Audit hasResult=false (diungkapkan, bukan lolos); sesi baw CONNECTED+devMode. Website gate LOLOS (poffzi-orbit.pages.dev mencetak kontrak persis, diverifikasi 19:35 WIB). "
      "Keputusan re-arm parser SUDAH MOOT untuk Poffzi (pool gratis 0; hanya jalur berbayar 0.0015 BNB tersisa — BUKAN gratis, tidak dieksekusi di bawah otorisasi apa pun). "
      "Pelajaran: parser preview fcfs_fast.py WAJIB diperbaiki sebelum sale FCFS berikutnya (baca simulationResult.simulationCode bila ada). Dilaporkan sekali sebagai PERUBAHAN (sold out).")
    print("Poffzi -> sold-out-free")
vez = snap["contracts"].get("Vezlune")
if vez is not None:
    vez["status"] = "sold-out-free-2026-11-16"
    vez["runNote2301_1116"] = f"Run 2301 (blok {BLOCK}): totalSupply 101, freeMinted 100/100, mintOpen 1, bal_user 0 — terkonfirmasi sold-out-free (1 mint berbayar). DIAM."
    print("Vezlune -> sold-out-free confirmed")
bubb = snap["contracts"].get("Agent Bubble")
if bubb is not None:
    bubb["runNote2301_1116"] = (f"Run 2301 (blok {BLOCK}): totalSupply 1795, freeMinted 1651/2222 = 74,3% (>70%) TAPI umur UNVERIFIED -> BUKAN strong lead. mintOpen 1, bal_user 0. DIAM.")
    print("BUBB noted 74.3% age-unverified")
pc = snap["contracts"].get("pending_claims", {}).get("binanceai.fun")
if isinstance(pc, dict):
    pc["runNote2301_1116"] = f"Run 2301: launched=0, failed=1, isRefundPhase=1, totalShares=3110, tokenClaimed(user)=0 (blok {BLOCK}) - tetap pending/refund, sudah dilaporkan sekali (fase refund), DIAM"
    pc["lastReadWib"] = "2026-11-16 ~23:01 WIB"
    print("pending_claims binanceai noted")
# --- Sourcify feedshape results into track_c ---
for addr, res in fs.items():
    key="Feed-"+addr[2:6]
    shape=res.get("shape")
    status="checked-not-sale-shape-2026-11-16" if shape=="checked-not-sale-shape" else ("checked-abi-unavailable-2026-11-16" if shape=="abi-unavailable" else shape)
    tc[key]={"address":addr,"status":status,"S1":shape=="S1","S2":shape=="S2",
      "has_mint":res.get("mint"),"has_quote":res.get("quote"),"free_views":res.get("free_views"),
      "agent_ref":res.get("registry"),"is_token":res.get("token"),"n_fns":res.get("fns"),
      "note":f"Sourcify feed run 2301: {shape}."}
    print("track_c added:",key,status)
snap["last_run"]="2026-11-16 ~23:01 WIB"
snap["last_run_wib"]="2026-11-16 ~23:01 WIB"
snap["runNote2301"]="Run 2301 (23:01 WIB, blok reread 133957032, 41/41 OK, 91,7 dtk): 1 PERUBAHAN BESAR - Poffzi SOLD OUT GRATIS (freeMinted 100/100 blok 133957194 ~23:10 WIB; trigger 23:00:17 freeMinted 2, preview 23:00:22 struktur baw baru tak dikenali parser -> loop TERMINAL tanpa mint; preview ulang ~23:06 351805 reverted; pool habis ~10 mnt, laju ~30/mnt). Vezlune terkonfirmasi sold-out-free (100/100). BUBB 1651/2222=74,3% tapi umur unverified -> bukan strong lead. PXIO velocity dihitung di merge (lihat vel summary). Punch Card +8 velocity GAGAL (<20). BinanceAI tetap refund. RigForge tetap belum buka (freeSharesLeft 636 terkonfirmasi; artefak None hot-leg 2259 adalah baca gagal). Scan Ankr pre-flight FAIL 401 (watermark tetap 132512564, gap ~1,43jt blok). Boltbook EN+ZH 6 alamat unik, 0 baru. Sourcify 11 baru vs 2231: 6 not-sale-shape, 5 abi-unavailable (transport Sourcify). Sweep EN+ZH hanya proyek lama/sudah dikenal (Agentic Gangster pool habis, Xuanwu sold out, YAMA watchlist-only). Bridge 116 kontrak, 0 baru. TIDAK ADA kandidat/strong lead/early lead baru, TIDAK ADA eksekusi/preview selain preview baca-saja Poffzi."
json.dump(snap, open(BASE+"onchain-snapshot.json","w"), indent=1)
print("snapshot saved. contracts:",len(snap["contracts"]),"track_c:",len(tc))
