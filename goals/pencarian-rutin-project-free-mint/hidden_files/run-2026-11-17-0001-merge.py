#!/usr/bin/env python3
"""Merge run 0001 (2026-11-17 00:01 WIB) reads into onchain-snapshot.json.
Prev baseline: run 2331 reread block 133960864. Head now 133964440 (curl).
Interval = (133964440-133960864)*0.45/60 = 26.82 min. Read-only on chain; writes snapshot only."""
import json
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
snap=json.load(open(BASE+"onchain-snapshot.json"))
rr=json.load(open(BASE+"run-2026-11-17-0001-reread.json"))
BLOCK=133964440
INTERVAL_MIN=round((BLOCK-133960864)*0.45/60,2)
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
FIELDS=["totalSupply","totalMinted","freeMinted","freeClaimed","FREE_SUPPLY","FREE_CAP","FREE_MAX","MAX_SUPPLY","mintOpen","mintOpensAt","paused","isFreePhase","freeRemaining","paidMinted","mintPrice","freeMintsLeft","FREE_MINT_CAP","PRICE","TOKEN_PRICE","remainingSupply","totalShares","launched","failed","isRefundPhase","claimOpen","totalSpecimens","currentExperiment","genesisStart","genesisOpen","freeSharesLeft","openedAt","freeClaimed","freeSupply","maxSupply","saleStart","saleOpen","saleEnd","mintStart"]
UFIELDS=["balanceOf_user","freeMintedPerWallet_user","mintedPerWallet_user","mintedByWallet_user","hasAgentId_user","holdsAgentId_user","freeUsed_user","freeClaimed_user","mintsBy_user","mintCountOf_user","mintedBy_user","hasFreeClaimed_user","tokenClaimed_user","freeBooked_user","freeDone_user","priceFor_user","priceFor_user_1","mintPriceFor_user_1","cost_user_1"]
# single-call verifications run 0001 (batch nulls resolved)
VERIFIED={"AgentNOVA": {"totalSupply": 683},
          "Zephyra": {"totalMinted": "REVERT"},
          "Pengu": {"totalMinted": "REVERT", "freeMinted": "REVERT"},
          "Kryntar": {"totalMinted": "REVERT", "standardRemaining": "REVERT", "legendaryRemaining": "REVERT", "mintOpen": "REVERT"},
          "Zero": {"totalSupply": "REVERT", "freeClaimed": "REVERT"},
          "ALIEN": {"freeMinted": "REVERT", "freeClaimed": "REVERT"}}
vel_summary={}
for name, r in rr["reads"].items():
    addr=r["address"].lower(); views=r.get("views") or {}
    ent=byaddr.get(addr)
    if ent is None:
        print(name,"no snapshot entry, skipped"); continue
    key, e = ent
    prev_sup = supply_of(e)
    ns = new_supply(views)
    # apply single-call verifications: confirmed values override None; REVERT keeps old value
    vrf = VERIFIED.get(name, {})
    for f, val in vrf.items():
        if val != "REVERT":
            views[f] = val
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
    e["lastReadWib"]="2026-11-17 ~00:01 WIB"
    free=e.get("freeMinted") if e.get("freeMinted") is not None else e.get("freeClaimed")
    cap=e.get("FREE_SUPPLY") if e.get("FREE_SUPPLY") is not None else (e.get("FREE_CAP") if e.get("FREE_CAP") is not None else e.get("FREE_MAX"))
    pct=(round(100*free/cap,1) if isinstance(free,int) and isinstance(cap,int) and cap else None)
    if pct is not None: e["freePctVerified"]=pct
    vel_summary[name]=(minted, None if rate is None else round(rate,3), None if ratio is None else round(ratio,2), vel, pct)
    if name=="BinanceAI-mint":
        note=f"Run 0001: launched={views.get('launched')}, failed={views.get('failed')}, isRefundPhase={views.get('isRefundPhase')}, totalShares={views.get('totalShares')}, tokenClaimed(user)={views.get('tokenClaimed_user')} (blok {BLOCK}) - tetap fase refund, klaim BELUM terbuka. DIAM."
    elif name=="RigForge":
        note=f"Run 0001: freeSharesLeft={views.get('freeSharesLeft')}, openedAt={views.get('openedAt')}, freeClaimed={views.get('freeClaimed')}, freeBooked(user)={views.get('freeBooked_user')} (blok {BLOCK}). Belum buka. DIAM."
    elif name in VERIFIED:
        note=(f"Run 0001 (blok {BLOCK}, interval ~{INTERVAL_MIN} mnt vs run 2331): supply {prev_sup}->{ns} (+{minted}), "
              f"rate {None if rate is None else round(rate,3)}/mnt vs prev {prev_rate} = {None if ratio is None else round(ratio,2)}x, velocity {'LOLOS' if vel else 'GAGAL'}; "
              f"verifikasi single-call: {vrf} (REVERT = view revert di 3 endpoint, nilai lama dipertahankan, velocity tidak dihitung dari nilai revert). DIAM.")
    elif name=="PXIO Miners" or name=="PXIO":
        note=(f"Run 0001 (blok {BLOCK}, interval ~{INTERVAL_MIN} mnt vs run 2331): supply {prev_sup}->{ns} (+{minted}), "
              f"rate {None if rate is None else round(rate,3)}/mnt vs prev {prev_rate} = {None if ratio is None else round(ratio,2)}x, velocity {'LOLOS' if vel else 'GAGAL'}; "
              f"free% + umur tetap UNVERIFIED (free views revert). Tetap EARLY lead, BUKAN strong lead/kandidat. DIAM.")
    elif pct is not None:
        note=(f"Run 0001 (blok {BLOCK}, interval ~{INTERVAL_MIN} mnt vs run 2331): supply {prev_sup}->{ns} (+{minted}), rate {None if rate is None else round(rate,3)}/mnt vs prev {prev_rate} = {None if ratio is None else round(ratio,2)}x, velocity {'LOLOS' if vel else 'GAGAL'}; free={free}/{cap} ({pct}%)")
    else:
        note=(f"Run 0001 (blok {BLOCK}, interval ~{INTERVAL_MIN} mnt vs run 2331): supply {prev_sup}->{ns} (+{minted}), rate {None if rate is None else round(rate,3)}/mnt vs prev {prev_rate} = {None if ratio is None else round(ratio,2)}x, velocity {'LOLOS' if vel else 'GAGAL'}; free% UNVERIFIED")
    e["runNote0001_1117"]=note
print("interval_min:", INTERVAL_MIN)
print("velocity summary:")
for k,v in vel_summary.items(): print(" ",k,v)
# pending claim binanceai.fun
pc=snap.get("pending_claims",{}).get("binanceai.fun")
if pc:
    pc["lastReadWib"]="2026-11-17 ~00:01 WIB"
    pc["runNote0001"]="Run 0001: launched=0, failed=1, isRefundPhase=1, totalShares=3110, tokenClaimed(user)=0 (blok 133964440) - tetap pending/refund, sudah dilaporkan sekali (fase refund 2 Nov), DIAM."
snap["last_run_wib"]="2026-11-17 ~00:01 WIB"
snap["last_run"]="2026-11-17 ~00:01 WIB"
snap["runNote0001_1117"]="Run 0001 (00:01 WIB): re-read 47/47 OK (blok 133964440, interval ~26.8 mnt vs run 2331). Velocity LOLOS: PXIO Miners +785 (29.3/mnt, ~2.8x) - tetap EARLY lead (free% + umur UNVERIFIED). Lainnya velocity GAGAL (maks Punch Card +4, LumenFindings +8, ALIEN +5). Threshold >70%: tidak ada yang tembus (AGCLUB 57.9%, Matrix 56.6%, Ledgera 53.8%, RaceAgents 63.0%; AgentBubble 74.3% tapi umur unverified). Ankr pre-flight GAGAL HTTP 401 (lagi) -> scan FAST-FAIL, watermark TETAP 132512564. Sourcify 0 baru, Boltbook 0 baru, shape-check 0 target. Sweep EN+ZH + Odaily: hanya proyek lama (Agentic Gangster 9 Nov, RIGBYPASS, MOLT, First-Dollar Grove, AGENT COSMOS, Agent Zet free habis, Xuanwu Seed) - 0 baru. Zephyra/Pengu/Kryntar/Zero totalMinted dkk REVERT di 3 endpoint (nilai lama dipertahankan). Vezlune/Poffzi tetap sold-out-free. binanceai tetap refund. Bridge 116 kontrak, 0 di luar snapshot. DIAM (tanpa laporan chat)."
json.dump(snap, open(BASE+"onchain-snapshot.json","w"), indent=1)
print("snapshot saved")
