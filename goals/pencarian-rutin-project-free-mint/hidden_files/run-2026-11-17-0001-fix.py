#!/usr/bin/env python3
"""Fix run 0001 merge: recompute minted/velocity from 2331 reread file (true
30-min baseline) instead of the lagging snapshot baseline. Corrects Punch Card,
PIXELFROGS, AgentBubble, ALIEN, SPARKS, PXIO numbers + notes. Also updates
track_c RigForge/DogeRageFi which the merge skipped."""
import json
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
snap=json.load(open(BASE+"onchain-snapshot.json"))
r2331=json.load(open(BASE+"run-2026-11-16-2331-reread.json"))["reads"]
r0001=json.load(open(BASE+"run-2026-11-17-0001-reread.json"))["reads"]
INTERVAL_MIN=26.82
BLOCK=133964440
def supply_of(views):
    if views is None: return None
    if views.get("totalMinted") is not None: return views.get("totalMinted")
    return views.get("totalSupply")
byaddr={}
for k,v in snap.get("contracts",{}).items():
    if isinstance(v,dict) and v.get("address"): byaddr[v["address"].lower()]=(k,v)
fixed=[]
for name, cur in r0001.items():
    addr=cur["address"].lower()
    if addr not in byaddr: continue
    key, e = byaddr[addr]
    prev_views=(r2331.get(name) or {}).get("views") or {}
    cur_views=cur.get("views") or {}
    # single-call verified value for AgentNOVA
    if name=="AgentNOVA": cur_views=dict(cur_views); cur_views["totalSupply"]=683
    ps, ns = supply_of(prev_views), supply_of(cur_views)
    minted=(ns-ps) if isinstance(ns,int) and isinstance(ps,int) else None
    prev_rate=e.get("previousRatePerMin")  # pre-merge currentRatePerMin, preserved by merge
    rate=(minted/INTERVAL_MIN) if minted is not None else None
    ratio=(rate/prev_rate) if (rate is not None and prev_rate not in (None,0)) else None
    vel=bool(minted is not None and minted>=20 and ratio is not None and ratio>=1.5)
    if minted != e.get("mintedInInterval") or vel != e.get("velocityLegPasses"):
        e["previousTotalSupply"]=ps
        e["mintedInInterval"]=minted
        e["currentRatePerMin"]=rate
        e["velocityRatio"]=ratio
        e["velocityLegPasses"]=vel
        free=e.get("freeMinted") if e.get("freeMinted") is not None else e.get("freeClaimed")
        cap=e.get("FREE_SUPPLY") if e.get("FREE_SUPPLY") is not None else (e.get("FREE_CAP") if e.get("FREE_CAP") is not None else e.get("FREE_MAX"))
        pct=(round(100*free/cap,1) if isinstance(free,int) and isinstance(cap,int) and cap else None)
        if name in ("PXIO","PXIO Miners"):
            note=(f"Run 0001 (blok {BLOCK}, interval ~{INTERVAL_MIN} mnt vs run 2331, baseline reread 2331): supply {ps}->{ns} (+{minted}), "
                  f"rate {None if rate is None else round(rate,3)}/mnt vs prev {prev_rate} = {None if ratio is None else round(ratio,2)}x, velocity {'LOLOS' if vel else 'GAGAL'}; "
                  f"free% + umur tetap UNVERIFIED (free views revert). Tetap EARLY lead, BUKAN strong lead/kandidat. DIAM. (Koreksi: baseline snapshot 2106 tertinggal dari reread 2331 = 2095; angka +796 ini yang benar.)")
        elif pct is not None:
            note=(f"Run 0001 (blok {BLOCK}, interval ~{INTERVAL_MIN} mnt vs run 2331, baseline reread 2331): supply {ps}->{ns} (+{minted}), rate {None if rate is None else round(rate,3)}/mnt vs prev {prev_rate} = {None if ratio is None else round(ratio,2)}x, velocity {'LOLOS' if vel else 'GAGAL'}; free={free}/{cap} ({pct}%) (Koreksi baseline: snapshot tertinggal dari reread 2331; angka interval ini yang benar.)")
        else:
            note=(f"Run 0001 (blok {BLOCK}, interval ~{INTERVAL_MIN} mnt vs run 2331, baseline reread 2331): supply {ps}->{ns} (+{minted}), rate {None if rate is None else round(rate,3)}/mnt vs prev {prev_rate} = {None if ratio is None else round(ratio,2)}x, velocity {'LOLOS' if vel else 'GAGAL'}; free% UNVERIFIED (Koreksi baseline: snapshot tertinggal dari reread 2331; angka interval ini yang benar.)")
        e["runNote0001_1117"]=note
        fixed.append((name, ps, ns, minted, None if rate is None else round(rate,3), None if ratio is None else round(ratio,2), vel))
print("fixed:", fixed)
# track_c updates skipped by merge
tc=snap.setdefault("track_c",{})
rf=tc.get("RigForge")
if isinstance(rf,dict):
    rf["freeSharesLeft"]=636; rf["openedAt"]=0; rf["freeClaimed"]=364
    rf["lastReadWib"]="2026-11-17 ~00:01 WIB"
    rf["runNote0001_1117"]=f"Run 0001: freeSharesLeft=636, openedAt=0, freeClaimed=364 (blok {BLOCK}). Belum buka. DIAM."
dr=tc.get("DogeRageFi")
if isinstance(dr,dict):
    dr["totalMinted"]=229; dr["freeSupply"]=432; dr["maxSupply"]=666; dr["mintOpen"]=1
    dr["lastReadWib"]="2026-11-17 ~00:01 WIB"
    dr["runNote0001_1117"]=f"Run 0001: totalMinted=229, freeSupply=432/666, mintOpen=1, bal_user=0 (blok {BLOCK}). Watchlist-only-age-unverified. DIAM."
# top-level note: correct PXIO number
snap["runNote0001_1117"]=snap["runNote0001_1117"].replace("PXIO Miners +785 (29.3/mnt, ~2.8x)","PXIO Miners +796 (29.7/mnt, 2.8x)")
json.dump(snap, open(BASE+"onchain-snapshot.json","w"), indent=1)
print("snapshot fixed + saved")
