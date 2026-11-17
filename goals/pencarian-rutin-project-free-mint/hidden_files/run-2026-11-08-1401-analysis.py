"""Analysis run 1401: velocity/sellout/age/promotion from reread JSON. Read-only vs snapshot (writes run-1401-analysis.json only)."""
import json, datetime
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
snap=json.load(open(f"{BASE}/onchain-snapshot.json"))
rr=json.load(open(f"{BASE}/run-2026-11-08-1401-reread.json"))
block=rr["block"]
# interval vs lastReadWib 14:05 -> now ~14:3x; use snapshot lastReadWib per contract? Use fixed: last run 1331 read at 14:05 WIB, this read block 132351271 (~14:24 WIB?) -> interval ~30 min approx from block diff
# Use previousTotalSupply stored in snapshot + intervalMinutes stored (48.0 stale) -> recompute from block timestamps? Keep simple: interval = minutes between snapshot lastRead (14:05) and now (14:28) ~ 23 min? Use block-based: prev block 132346499, now 132351271 = 4772 blocks * 0.45s = 35.8 min.
INTERVAL_MIN=(block-132346499)*0.45/60
print(f"block {block} interval ~{INTERVAL_MIN:.1f} min vs run 1331")
out={"block":block,"interval_min":round(INTERVAL_MIN,1),"velocity_pass":[],"sellout_new":[],"age_excluded":[],"promotions":[],"changes":[],"degraded":[]}
contracts=snap["contracts"]
for name,e in contracts.items():
    r=rr["reread"].get(name)
    if r is None: continue
    ts=r.get("totalSupply")
    prev=e.get("totalSupply")
    if ts is None:
        out["degraded"].append(name); continue
    minted=ts-prev if isinstance(prev,int) else None
    if minted is None: continue
    rate=minted/INTERVAL_MIN if INTERVAL_MIN>0 else 0
    prev_rate=e.get("currentRatePerMin")
    ratio=(rate/prev_rate) if prev_rate else None
    vel = (ratio is not None and ratio>=1.5 and minted>=20)
    # free % from freeClaimed if present
    fc=r.get("freeClaimed"); fs=e.get("FREE_SUPPLY") or r.get("FREE_SUPPLY")
    freepct=(fc/fs*100) if (isinstance(fc,int) and isinstance(fs,int) and fs) else None
    if vel:
        out["velocity_pass"].append({"name":name,"minted":minted,"rate":round(rate,4),"prev_rate":prev_rate,"ratio":round(ratio,2) if ratio else None,"freePct":round(freepct,1) if freepct is not None else None,"status":e.get("status")})
    # sellout: freeClaimed >= FREE_SUPPLY or totalSupply>=MAX_SUPPLY with mintOpen 0? use freeClaimed>=FREE_SUPPLY
    if isinstance(fc,int) and isinstance(fs,int) and fs and fc>=fs and "sold-out" not in str(e.get("status")):
        out["sellout_new"].append({"name":name,"freeClaimed":fc,"FREE_SUPPLY":fs,"status":e.get("status")})
    if minted!=0 or (isinstance(freepct,(int,float))):
        out["changes"].append({"name":name,"prev":prev,"now":ts,"minted":minted,"freeClaimed":fc,"freePct":round(freepct,1) if freepct is not None else None,"bal":r.get("balanceOf_user"),"status":e.get("status")})
print(json.dumps(out,indent=1)[:6000])
json.dump(out,open(f"{BASE}/run-2026-11-08-1401-analysis.json","w"),indent=1)
