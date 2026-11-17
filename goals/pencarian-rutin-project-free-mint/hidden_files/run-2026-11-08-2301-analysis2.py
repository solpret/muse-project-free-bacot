"""Run 2201 analysis v2 — STRICT per-view deltas (no totalSupply/totalMinted mixing).
Corrects analysis.py v1 which compared snapshot totalSupply vs new totalMinted.
"""
import json
B="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
snap=json.load(open(B+"onchain-snapshot.json"))
rr=json.load(open(B+"run-2026-11-08-2301-reread.json"))
contracts=snap.get("contracts",{})
reread=rr.get("reread",{})
INTERVAL=(rr["block"]-132416224)*0.45/60.0
ts_changes=[]; tm_changes=[]; fc_changes=[]; fm_changes=[]
vel=[]
for name,e in contracts.items():
    if not isinstance(e,dict): continue
    r=reread.get(name)
    if not r or r.get("_batch_fail"): continue
    # per-view
    if e.get("totalSupply") is not None and r.get("totalSupply") is not None and e["totalSupply"]!=r["totalSupply"]:
        ts_changes.append((name,e["totalSupply"],r["totalSupply"],r["totalSupply"]-e["totalSupply"]))
    if e.get("totalMinted") is not None and r.get("totalMinted") is not None and e["totalMinted"]!=r["totalMinted"]:
        tm_changes.append((name,e["totalMinted"],r["totalMinted"],r["totalMinted"]-e["totalMinted"]))
    if e.get("freeClaimed") is not None and r.get("freeClaimed") is not None and e["freeClaimed"]!=r["freeClaimed"]:
        fc_changes.append((name,e["freeClaimed"],r["freeClaimed"],r["freeClaimed"]-e["freeClaimed"]))
    if e.get("freeMinted") is not None and r.get("freeMinted") is not None and e["freeMinted"]!=r["freeMinted"]:
        fm_changes.append((name,e["freeMinted"],r["freeMinted"],r["freeMinted"]-e["freeMinted"]))
    # velocity on like-for-like minted delta (totalMinted preferred)
    old=None; new=None
    if e.get("totalMinted") is not None and r.get("totalMinted") is not None:
        old,new=e["totalMinted"],r["totalMinted"]
    elif e.get("totalSupply") is not None and r.get("totalSupply") is not None:
        old,new=e["totalSupply"],r["totalSupply"]
    prev_rate=e.get("currentRatePerMin") or e.get("previousRatePerMin")
    if old is not None and new is not None and prev_rate and prev_rate>0:
        minted=new-old; cur=minted/INTERVAL
        if cur>=1.5*prev_rate and minted>=20:
            vel.append((name,old,new,minted,round(prev_rate,3),round(cur,3),round(cur/prev_rate,2),e.get("status")))
print(f"interval {INTERVAL:.1f} min")
print("TS_CHANGES (totalSupply->totalSupply)", len(ts_changes))
for c in sorted(ts_changes,key=lambda x:-abs(x[3]))[:30]: print("  ",c)
print("TM_CHANGES (totalMinted->totalMinted)", len(tm_changes))
for c in sorted(tm_changes,key=lambda x:-abs(x[3]))[:30]: print("  ",c)
print("FC_CHANGES (freeClaimed->freeClaimed)", len(fc_changes))
for c in sorted(fc_changes,key=lambda x:-abs(x[3]))[:30]: print("  ",c)
print("FM_CHANGES (freeMinted->freeMinted)", len(fm_changes))
for c in sorted(fm_changes,key=lambda x:-abs(x[3]))[:30]: print("  ",c)
print("VEL_PASS strict", len(vel))
for v in vel: print("  ",v)
# free % now, like-for-like cap from snapshot FREE_SUPPLY/FREE_CAP
print("FREE_PCT_NOW (cap from snapshot, new free view same-view only):")
for name,e in contracts.items():
    if not isinstance(e,dict): continue
    r=reread.get(name)
    if not r: continue
    cap=e.get("FREE_SUPPLY") or e.get("FREE_CAP")
    val=None
    if e.get("freeClaimed") is not None and r.get("freeClaimed") is not None: val=r["freeClaimed"]
    elif e.get("freeMinted") is not None and r.get("freeMinted") is not None: val=r["freeMinted"]
    if cap and val is not None:
        pct=100*val/cap
        if pct>=25:
            print(f"  {name}: {val}/{cap} = {pct:.1f}% status={e.get('status')} bal_user={r.get('balanceOf_user')} snap_bal={e.get('userBalance')}")
json.dump({"ts_changes":ts_changes,"tm_changes":tm_changes,"fc_changes":fc_changes,
           "fm_changes":fm_changes,"vel_pass":vel,"interval_min":round(INTERVAL,1)},
          open(B+"run-2026-11-08-2301-analysis2.json","w"),indent=1)
print("analysis2 written")
