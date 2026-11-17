import json
from datetime import datetime, timezone, timedelta
B="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
snap=json.load(open(B+"onchain-snapshot.json"))
rr=json.load(open(B+"run-2026-11-08-2131-reread.json"))
contracts=snap.get("contracts",{}); reread=rr.get("reread",{})
NOW=datetime(2026,11,8,21,31,tzinfo=timezone(timedelta(hours=7)))
INTERVAL_MIN=55.0  # wall-clock 2031 (~20:36 reread) -> 2131 (~21:36 reread); block diff 5343 blocks
changes=[]; vel=[]
for name,e in contracts.items():
    if not isinstance(e,dict): continue
    r=reread.get(name)
    if not r or r.get("_batch_fail"): continue
    for view in ("totalSupply","totalMinted"):
        old=e.get(view); new=r.get(view)
        if old is not None and new is not None and new!=old:
            changes.append({"name":name,"view":view,"old":old,"new":new,"delta":new-old,"status":e.get("status"),"firstMint":e.get("firstMintWib")})
    # velocity on totalMinted preferred, else totalSupply
    old = e.get("totalMinted") if e.get("totalMinted") is not None else e.get("totalSupply")
    new = r.get("totalMinted") if r.get("totalMinted") is not None else r.get("totalSupply")
    prev = e.get("currentRatePerMin") or e.get("previousRatePerMin")
    if old is not None and new is not None and prev:
        minted=new-old; cur=minted/INTERVAL_MIN
        if cur>=1.5*prev and minted>=20:
            vel.append({"name":name,"minted":minted,"prev_rate":round(prev,3),"cur_rate":round(cur,3),"ratio":round(cur/prev,2),"status":e.get("status")})
print("PER-VIEW CHANGES", len(changes))
for c in sorted(changes,key=lambda x:-x["delta"])[:30]: print(" ",c)
print("VEL_PASS (interval 55min)", len(vel))
for v in vel: print(" ",v)
# age sweep: firstMintWib parse
def parse_fm(s):
    try: return datetime.strptime(s,"%Y-%m-%d %H:%M:%S WIB").replace(tzinfo=timezone(timedelta(hours=7)))
    except Exception: return None
LOW_EXCLUDE=("sold-out","age-excluded","minted-by-user","excluded","promotion-discarded","same-owner-discarded","paid-only")
cands=[]
for name,e in contracts.items():
    if not isinstance(e,dict): continue
    fm=parse_fm(e.get("firstMintWib") or "")
    if not fm: continue
    age_h=(NOW-fm).total_seconds()/3600
    st=str(e.get("status") or "")
    if age_h>48:
        cands.append({"name":name,"age_h":round(age_h,1),"firstMint":e.get("firstMintWib"),"status":st,"already_out":any(x in st for x in LOW_EXCLUDE)})
print("AGE>48h total", len(cands))
for c in sorted(cands,key=lambda x:-x["age_h"]):
    print(" ", c)
json.dump({"changes":changes,"vel":vel,"age_cands":cands,"interval_min":INTERVAL_MIN},open(B+"run-2026-11-08-2131-analysis2.json","w"),indent=1)
print("written")
