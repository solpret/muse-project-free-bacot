import json, datetime, re
snap=json.load(open('onchain-snapshot.json'))
rr=json.load(open('run-2026-11-08-1101-reread.json'))
NOW=datetime.datetime(2026,11,8,11,1,tzinfo=datetime.timezone(datetime.timedelta(hours=7)))
BLOCK_SEC=0.45
old_block=132323930
new_block=rr['block']
interval_min=(new_block-old_block)*BLOCK_SEC/60.0
print(f"interval: {new_block-old_block} blocks ~ {interval_min:.1f} min")
contracts=snap.get('contracts',{})
reread=rr['reread']
vel_pass=[]; soldout_new=[]; slot_changed=[]; unreadable=0; updated=0
EXEMPT_AGE={'minted-by-user'}
for name, e in contracts.items():
    if not isinstance(e,dict): continue
    d=reread.get(name)
    if d is None: continue
    updated+=1
    new_sup=d.get('totalSupply')
    if new_sup is None: new_sup=d.get('totalMinted')
    old_sup=e.get('totalSupply')
    if old_sup is None: old_sup=e.get('totalMinted')
    # velocity
    if isinstance(new_sup,int) and isinstance(old_sup,int):
        minted=new_sup-old_sup
        rate=minted/interval_min if interval_min>0 else 0
        prev_rate=e.get('previousRatePerMin') or e.get('prevRatePerMin') or 0
        if prev_rate and prev_rate>0 and rate>=1.5*prev_rate and minted>=20:
            vel_pass.append((name, old_sup, new_sup, minted, round(rate,3), round(prev_rate,3), e.get('status')))
        e['_new_supply']=new_sup; e['_minted_interval']=minted; e['_rate']=round(rate,4)
    else:
        unreadable+=1
    # sold out (free pool)
    fc=d.get('freeClaimed'); fs=d.get('FREE_SUPPLY')
    if fc is None: fc=e.get('freeClaimed')
    if fs is None: fs=e.get('FREE_SUPPLY')
    if isinstance(fc,int) and isinstance(fs,int) and fs>0 and fc>=fs and 'sold-out' not in str(e.get('status','')) and 'soldout' not in str(e.get('status','')):
        soldout_new.append((name, fc, fs, e.get('status')))
    # slot change: user balance / freeClaimed_user
    nb=d.get('balanceOf_user'); ob=e.get('userBalance')
    nfc=d.get('freeClaimed_user'); ofc=e.get('freeClaimed_user') if 'freeClaimed_user' in e else e.get('userFreeUsed')
    if (isinstance(nb,int) and isinstance(ob,int) and nb!=ob) or (isinstance(nfc,int) and isinstance(ofc,int) and nfc!=ofc):
        slot_changed.append((name, ob, nb, ofc, nfc, e.get('status')))
print(f"reread matched: {updated}, unreadable supply: {unreadable}")
print("VELOCITY PASS:", len(vel_pass))
for v in vel_pass: print('  ', v)
print("SOLDOUT NEW:", len(soldout_new))
for v in soldout_new: print('  ', v)
print("SLOT CHANGED:", len(slot_changed))
for v in slot_changed: print('  ', v)
# age sweep: verified launch >48h, active watchlist/lead status, not sold out
def parse_launch(e):
    for k in ('firstMintWib','startTimeWib'):
        v=e.get(k)
        if isinstance(v,str):
            try:
                dt=datetime.datetime.fromisoformat(v.replace('Z','+00:00'))
                if dt.tzinfo is None:
                    dt=dt.replace(tzinfo=datetime.timezone(datetime.timedelta(hours=7)))
                return dt
            except: pass
    return None
REMOVE_STATUSES=('watchlist','early-lead','strong-lead','lead-gate','track-c-lead')
remove=[]
kept_verified=0; unverified=0
for name, e in contracts.items():
    if not isinstance(e,dict): continue
    st=str(e.get('status',''))
    if not any(s in st for s in ('watchlist','early-lead','strong-lead','lead')): continue
    if any(x in st for x in ('minted-by-user','sold-out','soldout','age-excluded','excluded','paid-only','same-owner-discarded','non-lead','holder-gate')): continue
    lt=parse_launch(e)
    if lt is None:
        unverified+=1; continue
    kept_verified+=1
    age_h=(NOW-lt).total_seconds()/3600
    if age_h>48:
        remove.append((name, lt, round(age_h,1), st))
print(f"AGE SWEEP: verified-launch active={kept_verified}, unverified-launch={unverified}, REMOVE={len(remove)}")
for r in remove: print('  REMOVE:', r)
# track_c diffs
tc=snap.get('track_c',{})
tc_rr=rr['track_c']
tc_changes=[]
for name, e in tc.items():
    if not isinstance(e,dict): continue
    d=tc_rr.get(name)
    if d is None: continue
    old_ts=e.get('totalSupply'); new_ts=d.get('totalSupply')
    if isinstance(old_ts,int) and isinstance(new_ts,int) and old_ts!=new_ts:
        tc_changes.append((name, old_ts, new_ts, e.get('status')))
print("TRACK_C supply changes:", len(tc_changes))
for c in tc_changes: print('  ', c)
json.dump({'interval_min':interval_min,'vel_pass':vel_pass,'soldout_new':soldout_new,'slot_changed':slot_changed,'age_remove':remove,'tc_changes':tc_changes,'unreadable':unreadable,'matched':updated}, open('run-2026-11-08-1101-analysis.json','w'), indent=1)
