import json, math
from datetime import datetime, timezone
B="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
snap=json.load(open(B+"onchain-snapshot.json"))
rr=json.load(open(B+"run-2026-11-08-2131-reread.json"))
contracts=snap.get("contracts",{})
reread=rr.get("reread",{})
tc_read=rr.get("track_c",{})
print("block", rr.get("block"), "reread n=", len(reread), "tc n=", len(tc_read))
# snapshot timestamp: last_run 2031 ~20:31; interval minutes from snapshot fields
# use snapshot last_run_wib and run start 21:31 -> ~60 min; try to find interval in entries
# compute per contract
def supply(v):
    # prefer totalSupply, fallback totalMinted
    return v.get("totalSupply") if v.get("totalSupply") is not None else v.get("totalMinted")
changes=[]; degraded=[]; batchfail=[]
vel_pass=[]
for name, e in contracts.items():
    if not isinstance(e,dict): continue
    r=reread.get(name)
    if r is None: continue
    if r.get("_batch_fail"): batchfail.append(name); continue
    old_ts = e.get("totalSupply") if e.get("totalSupply") is not None else e.get("totalMinted")
    new_ts = supply(r)
    if new_ts is None:
        degraded.append(name); continue
    if old_ts is not None and new_ts!=old_ts:
        changes.append((name, old_ts, new_ts, new_ts-old_ts, e.get("status"), e.get("firstMintWib")))
    # velocity: snapshot stores previous rate? fields currentRatePerMin/previousRatePerMin/mintedInInterval/intervalMinutes
    prev_rate = e.get("currentRatePerMin") or e.get("previousRatePerMin")
    interval = 60.0  # ~20:31 -> 21:31
    if old_ts is not None and prev_rate is not None and prev_rate>0:
        minted = new_ts-old_ts
        cur = minted/interval
        if cur >= 1.5*prev_rate and minted>=20:
            vel_pass.append((name, old_ts, new_ts, minted, round(prev_rate,3), round(cur,3), round(cur/prev_rate,2), e.get("status")))
print("CHANGES", len(changes))
for c in sorted(changes, key=lambda x:-x[3])[:40]: print("  ", c)
print("DEGRADED", len(degraded), degraded[:40])
print("BATCHFAIL", len(batchfail), batchfail[:20])
print("VEL_PASS", len(vel_pass))
for v in vel_pass: print("  ", v)
# focus items
for name in ["Pressure","HELIX","Pokechain","BAHUANG2","HIVE Agents","Oddlode Drills","402"]:
    e=contracts.get(name); r=reread.get(name)
    print("FOCUS", name, "| snap:", json.dumps(e)[:400] if e else None, "| new:", json.dumps(r) if r else None)
# track_c changes
tc=snap.get("track_c",{})
tc_changes=[]
for name, e in tc.items():
    if not isinstance(e,dict): continue
    r=tc_read.get(name)
    if not r: continue
    old_fm=e.get("freeMinted"); new_fm=r.get("freeMinted")
    if old_fm is not None and new_fm is not None and old_fm!=new_fm:
        tc_changes.append((name, old_fm, new_fm, e.get("status")))
print("TC_CHANGES", len(tc_changes))
for t in tc_changes: print("  ", t)
# NUSA specifically
for name in ["NUSA"]:
    e=tc.get(name); r=tc_read.get(name)
    print("TC-FOCUS", name, "| snap freeMinted", e.get("freeMinted") if e else None, "MAX_FREE", e.get("MAX_FREE") if e else None, "| new:", json.dumps(r) if r else None)
json.dump({"changes":changes,"degraded":degraded,"batchfail":batchfail,"vel_pass":vel_pass,"tc_changes":tc_changes,"block":rr.get("block")}, open(B+"run-2026-11-08-2131-analysis.json","w"), indent=1)
print("analysis written")
