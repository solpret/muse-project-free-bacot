#!/usr/bin/env python3
"""Velocity + sellout + slot analysis run 1201 from reread.json vs snapshot. Read-only; writes analysis json only."""
import json
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
snap=json.load(open(f"{BASE}/onchain-snapshot.json"))
r=json.load(open(f"{BASE}/run-2026-11-08-1201-reread.json"))
blk=r["block"]; prev_blk=132329835
interval_min=(blk-prev_blk)*0.45/60.0
print(f"interval blocks {blk-prev_blk} ~= {interval_min:.1f} min")
NONPROMO=("minted-by-user","discarded","sold-out","age-excluded","excluded")
vel_pass=[]; sellout_new=[]; slot_changed=[]; movers=[]
for name,d in r.get("reread",{}).items():
    s=snap.get("contracts",{}).get(name)
    if not s: continue
    ts=d.get("totalSupply"); prev=s.get("totalSupply")
    if ts is None or prev is None: continue
    minted=ts-prev
    if minted!=0: movers.append((name,prev,ts,minted))
    # velocity
    pr=s.get("currentRatePerMin") or s.get("previousRatePerMin") or 0
    rate=minted/interval_min if interval_min>0 else 0
    ratio=(rate/pr) if pr and pr>0 else None
    passes = (ratio is not None and ratio>=1.5 and minted>=20)
    if passes:
        vel_pass.append({"name":name,"address":s.get("address"),"status":s.get("status"),"minted":minted,"rate":round(rate,4),"prev_rate":pr,"ratio":round(ratio,2)})
    # sellout: totalSupply==MAX_SUPPLY or freeClaimed==FREE_SUPPLY
    ms=s.get("MAX_SUPPLY"); fs=s.get("FREE_SUPPLY"); fc=d.get("freeClaimed")
    sold=False
    if ms and ts>=ms: sold=True
    if fs and fc is not None and fc>=fs: sold=True
    if sold and "sold-out" not in str(s.get("status")):
        sellout_new.append({"name":name,"address":s.get("address"),"status":s.get("status"),"totalSupply":ts,"MAX_SUPPLY":ms,"freeClaimed":fc,"FREE_SUPPLY":fs})
    # slot: balanceOf user
    bal=d.get("balanceOf_user"); old=s.get("balanceOf_user")
    if bal is not None and old is not None and bal!=old:
        slot_changed.append({"name":name,"address":s.get("address"),"status":s.get("status"),"balance_old":old,"balance_new":bal})
promotable=[v for v in vel_pass if not any(k in str(v["status"]) for k in NONPROMO)]
print("velocity pass:",len(vel_pass),"promotable:",len(promotable))
for v in vel_pass: print("  VEL",v)
print("sellout new:",len(sellout_new))
for x in sellout_new: print("  SOLD",x)
print("slot changed:",len(slot_changed))
for x in slot_changed: print("  SLOT",x)
print("movers:",len(movers))
# track_c changes
tc_changes=[]
for name,d in r.get("track_c",{}).items():
    s=snap.get("track_c",{}).get(name)
    if not s or not isinstance(s,dict): continue
    old_ts=s.get("totalSupply") or s.get("totalMinted") or s.get("sharesMinted")
    new_ts=d.get("totalSupply") or d.get("totalMinted") or d.get("sharesMinted")
    if old_ts is not None and new_ts is not None and old_ts!=new_ts:
        tc_changes.append({"name":name,"status":s.get("status"),"old":old_ts,"new":new_ts,"note":d})
print("track_c supply changes:",len(tc_changes))
for x in tc_changes: print("  TC",x["name"],x["status"],x["old"],"->",x["new"])
json.dump({"block":blk,"interval_min":round(interval_min,1),"velocity_pass":vel_pass,"promotable":promotable,"sellout_new":sellout_new,"slot_changed":slot_changed,"movers":movers,"track_c_changes":tc_changes}, open(f"{BASE}/run-2026-11-08-1201-analysis.json","w"), indent=1)
print("wrote run-2026-11-08-1201-analysis.json")
