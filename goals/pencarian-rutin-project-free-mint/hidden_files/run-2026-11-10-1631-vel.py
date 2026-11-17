#!/usr/bin/env python3
"""Velocity analysis run 1601 (view-aware). Interval ~30 min (blok 132749741 16:01 -> 1631 read).
Reads snapshot (pre-merge 0901 values) + reread.json. Writes run-2026-11-10-1631-vel.json."""
import json
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
snap=json.load(open(f"{BASE}/onchain-snapshot.json"))
rr=json.load(open(f"{BASE}/run-2026-11-10-1631-reread.json"))
INTERVAL=30.0
out={"interval_min":INTERVAL,"block":rr["block"],"passes":[],"rows":{}}
for name,entry in snap["contracts"].items():
    if not isinstance(entry,dict): continue
    fresh=rr["reread"].get(name)
    if not fresh: continue
    view="totalMinted" if str(entry.get("supplyView","")).startswith("totalMinted") else "totalSupply"
    new=fresh.get(view); prev=entry.get(view)
    row={"view":view,"prev":prev,"new":new}
    if new is not None and prev is not None and new<=10**7 and prev<=10**7:
        minted=new-prev; rate=minted/INTERVAL; prev_rate=entry.get("currentRatePerMin")
        ratio=(rate/prev_rate) if prev_rate else None
        passes=bool(ratio is not None and ratio>=1.5 and minted>=20)
        row.update({"minted":minted,"rate":round(rate,3),"prev_rate":prev_rate,
                    "ratio":(round(ratio,2) if ratio is not None else None),"passes":passes})
        if passes: out["passes"].append(name)
    out["rows"][name]=row
# key six free %
for name in ["SEVENFOLD","FCAT Agents","JINCHAN Agents","Roguefall","Sakura","THYRK"]:
    e=snap["contracts"].get(name,{})
    f=rr["reread"].get(name,{})
    print(name, "view=",out["rows"].get(name,{}).get("view"), out["rows"].get(name,{}),
          "| fresh freeMinted=",f.get("freeMinted"),"freeClaimed=",f.get("freeClaimed"),
          "bal=",f.get("balanceOf_user"), "| snap free%=",e.get("freePctVerified"))
print("PASSES:", out["passes"])
# sellout scan: free pool exhausted where cap known
print("--- sellout scan (freeMinted/freeClaimed vs cap) ---")
for name,entry in snap["contracts"].items():
    if not isinstance(entry,dict): continue
    f=rr["reread"].get(name,{})
    cap=entry.get("FREE_SUPPLY") or entry.get("agentFreeCap") or entry.get("FREE_CAP")
    fm=f.get("freeMinted")
    if cap and fm is not None and fm>=cap and "sold-out" not in str(entry.get("status","")):
        print(" SELLOUT?", name, fm, "/", cap, "status:", entry.get("status"))
    fc=f.get("freeClaimed")
    if cap and fc is not None and fc>=cap and "sold-out" not in str(entry.get("status","")):
        print(" SELLOUT?(claimed)", name, fc, "/", cap, "status:", entry.get("status"))
json.dump(out,open(f"{BASE}/run-2026-11-10-1631-vel.json","w"),indent=1)
