import json
from datetime import datetime, timezone, timedelta
B="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
snap=json.load(open(B+"onchain-snapshot.json"))
rr=json.load(open(B+"run-2026-11-08-2201-reread.json"))
contracts=snap.get("contracts",{})
reread=rr.get("reread",{})
tc_read=rr.get("track_c",{})
print("block", rr.get("block"), "reread n=", len(reread), "tc n=", len(tc_read))
# interval: prev run block 132409469 (21:31 WIB) -> this block; ~0.45s/block
INTERVAL = (rr["block"]-132409469)*0.45/60.0
print(f"interval ~{INTERVAL:.1f} min (block-derived)")

def supply(v):
    return v.get("totalSupply") if v.get("totalSupply") is not None else v.get("totalMinted")
changes=[]; degraded=[]; batchfail=[]; vel_pass=[]
freepool_changes=[]; slot_changes=[]
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
        changes.append((name, old_ts, new_ts, new_ts-old_ts, e.get("status")))
    prev_rate = e.get("currentRatePerMin") or e.get("previousRatePerMin")
    if old_ts is not None and prev_rate is not None and prev_rate>0:
        minted = new_ts-old_ts
        cur = minted/INTERVAL
        if cur >= 1.5*prev_rate and minted>=20:
            vel_pass.append((name, old_ts, new_ts, minted, round(prev_rate,3), round(cur,3), round(cur/prev_rate,2), e.get("status")))
    # free pool: freeClaimed/freeMinted vs FREE_SUPPLY / free cap
    cap = e.get("FREE_SUPPLY") or e.get("FREE_CAP") or e.get("freeSupply")
    old_fc = e.get("freeClaimed") if e.get("freeClaimed") is not None else e.get("freeMinted")
    new_fc = r.get("freeClaimed") if r.get("freeClaimed") is not None else r.get("freeMinted")
    if cap and old_fc is not None and new_fc is not None and old_fc!=new_fc:
        freepool_changes.append((name, old_fc, new_fc, cap, round(100*new_fc/cap,2), e.get("status")))
    # user slot: balanceOf or freeClaimed(user)
    old_bal = e.get("userBalance") if e.get("userBalance") is not None else e.get("balanceOf")
    new_bal = r.get("balanceOf_user")
    old_fcu = e.get("userFreeUsed")
    new_fcu = r.get("freeClaimed_user")
    if (old_bal is not None and new_bal is not None and old_bal!=new_bal) or \
       (old_fcu is not None and new_fcu is not None and old_fcu!=new_fcu):
        slot_changes.append((name, old_bal, new_bal, old_fcu, new_fcu, e.get("status")))
print("CHANGES", len(changes))
for c in sorted(changes, key=lambda x:-abs(x[3]))[:50]: print("  ", c)
print("DEGRADED", len(degraded), degraded)
print("BATCHFAIL", len(batchfail), batchfail)
print("VEL_PASS", len(vel_pass))
for v in vel_pass: print("  ", v)
print("FREEPOOL_CHANGES", len(freepool_changes))
for f in freepool_changes: print("  ", f)
print("SLOT_CHANGES", len(slot_changes))
for s in slot_changes: print("  ", s)
# focus items
for name in ["Pressure","HELIX","Pokechain","BAHUANG2","HIVE Agents","Oddlode Drills","402","NUMBI","GLOOP","Jinchan","Ink Koi","NEKART","MONOLITH","TRACE","Wisp Agent","NUSA"]:
    e=contracts.get(name); r=reread.get(name)
    print("FOCUS", name, "| snap:", json.dumps(e)[:350] if e else None, "| new:", json.dumps(r) if r else None)
# track_c changes
tc=snap.get("track_c",{})
tc_changes=[]; tc_degraded=[]
for name, e in tc.items():
    if not isinstance(e,dict): continue
    r=tc_read.get(name)
    if not r: continue
    if r.get("_batch_fail"): tc_degraded.append(name); continue
    old_fm=e.get("freeMinted"); new_fm=r.get("freeMinted")
    if old_fm is not None and new_fm is not None and old_fm!=new_fm:
        tc_changes.append((name, old_fm, new_fm, e.get("status")))
print("TC_CHANGES", len(tc_changes))
for t in tc_changes: print("  ", t)
print("TC_DEGRADED", len(tc_degraded), tc_degraded)
for name in ["NUSA"]:
    e=tc.get(name); r=tc_read.get(name)
    print("TC-FOCUS", name, "| snap:", json.dumps(e)[:400] if e else None, "| new:", json.dumps(r) if r else None)
# age sweep: firstMintWib >48h before now and status not terminal
now = datetime(2026,11,8,22,25,tzinfo=timezone(timedelta(hours=7)))
TERM=("sold-out","age-excluded","minted-by-user","excluded","promotion-discarded","same-owner-discarded","paid-only")
age_new=[]
for name, e in contracts.items():
    if not isinstance(e,dict): continue
    st=str(e.get("status") or "")
    if any(x in st for x in TERM): continue
    fmw=e.get("firstMintWib")
    if not fmw: continue
    try:
        dt=datetime.strptime(str(fmw)[:19], "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone(timedelta(hours=7)))
    except Exception:
        try:
            dt=datetime.fromisoformat(str(fmw)).astimezone(timezone(timedelta(hours=7)))
        except Exception:
            continue
    age_h=(now-dt).total_seconds()/3600
    if age_h>48:
        r=reread.get(name) or {}
        age_new.append((name, fmw, round(age_h,1), st, supply(r)))
print("AGE_NEW", len(age_new))
for a in age_new: print("  ", a)
json.dump({"changes":changes,"degraded":degraded,"batchfail":batchfail,"vel_pass":vel_pass,
           "freepool_changes":freepool_changes,"slot_changes":slot_changes,
           "tc_changes":tc_changes,"tc_degraded":tc_degraded,"age_new":age_new,
           "block":rr.get("block"),"interval_min":round(INTERVAL,1)},
          open(B+"run-2026-11-08-2201-analysis.json","w"), indent=1)
print("analysis written")
