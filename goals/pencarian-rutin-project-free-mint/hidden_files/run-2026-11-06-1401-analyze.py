import json, urllib.request, datetime
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
def blk_ts(n):
    for rpc in ["https://bsc-dataseed1.bnbchain.org","https://bsc.publicnode.com","https://bsc-dataseed2.bnbchain.org"]:
        try:
            body=json.dumps({"jsonrpc":"2.0","id":1,"method":"eth_getBlockByNumber","params":[hex(n),False]}).encode()
            req=urllib.request.Request(rpc,data=body,headers={"Content-Type":"application/json"})
            with urllib.request.urlopen(req,timeout=10) as r:
                return int(json.load(r)["result"]["timestamp"],16)
        except Exception:
            continue
    return None
tz=datetime.timezone(datetime.timedelta(hours=7))
def fmt(ts): return datetime.datetime.fromtimestamp(ts,tz).strftime("%Y-%m-%d %H:%M:%S") if ts else None
t1=blk_ts(131962334); t2=blk_ts(131965602)
print("block 131962334 ts:", fmt(t1), " block 131965602 ts:", fmt(t2))
if t1 and t2:
    iv=(t2-t1)/60; method="block-timestamp"
else:
    iv=(131965602-131962334)*0.45/60; method="ESTIMATE 3268 blocks x 0.45s/block (block timestamps unreadable, RPC 403/disconnect)"
print("interval_min:", round(iv,2), "method:", method)
snap=json.load(open(f"{BASE}/onchain-snapshot.json"))
r31=json.load(open(f"{BASE}/run-2026-11-06-1331-reread-lean.json"))
r33=json.load(open(f"{BASE}/run-2026-11-06-1401-reread-lean.json"))
v31=json.load(open(f"{BASE}/run-2026-11-06-1331-velocity.json"))
prev_rate={row[0]: row[5] for row in v31["rows"]}
def supply(d):
    for k in ("totalSupply","totalMinted","freeMinted"):
        if d.get(k) is not None: return k,d[k]
    return None,None
rows=[]
for name in sorted(r33["reread"].keys()):
    a=r31["reread"].get(name,{}); b=r33["reread"][name]
    ka,va=supply(a); kb,vb=supply(b)
    e=snap["contracts"].get(name,{})
    pr=prev_rate.get(name)
    if va is not None and vb is not None:
        d=vb-va; rate=d/iv; ratio=(rate/pr) if pr else None
        vel_pass = (d>=20 and ratio is not None and ratio>=1.5)
        rows.append([name, kb, va, vb, d, round(rate,4), pr, (round(ratio,2) if ratio is not None else None), vel_pass])
        print(f"{name}: {ka} {va}->{vb} (+{d}, {rate:.3f}/mnt, prev {pr}, ratio {ratio if ratio is None else round(ratio,2)}x, >=20:{d>=20}, vel_pass:{vel_pass})")
    else:
        rows.append([name, kb, va, vb, None, None, pr, None, False])
        print(f"{name}: read-fail (1331 {ka}={va}, 1401 {kb}={vb}) snap totalSupply={e.get('totalSupply')} status={e.get('status')}")
print("--- track_c changes vs 1331 ---")
tc_changes={}
for name in sorted(r33["track_c"].keys()):
    a=r31["track_c"].get(name,{}); b=r33["track_c"][name]
    diff={k:(a.get(k),b.get(k)) for k in set(a)|set(b) if a.get(k)!=b.get(k)}
    tc_changes[name]=diff
    if diff: print(name, diff)
    else: print(name, "no change")
out={"interval_min": round(iv,2), "interval_method": method,
     "block_prev": 131962334, "block_now": 131965602,
     "block_ts_prev_wib": fmt(t1), "block_ts_now_wib": fmt(t2),
     "rows": rows, "track_c_changes": {k:{kk:list(vv) for kk,vv in v.items()} for k,v in tc_changes.items()}}
json.dump(out, open(f"{BASE}/run-2026-11-06-1401-velocity.json","w"), indent=1)
print("WROTE run-2026-11-06-1401-velocity.json")
print("VEL PASS:", [r[0] for r in rows if r[8]])
