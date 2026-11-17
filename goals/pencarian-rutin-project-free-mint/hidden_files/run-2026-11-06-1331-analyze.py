import json, urllib.request, datetime
def blk_ts(n):
    body=json.dumps({"jsonrpc":"2.0","id":1,"method":"eth_getBlockByNumber","params":[hex(n),False]}).encode()
    req=urllib.request.Request("https://bsc-dataseed1.bnbchain.org",data=body,headers={"Content-Type":"application/json"})
    with urllib.request.urlopen(req,timeout=10) as r: return int(json.load(r)["result"]["timestamp"],16)
tz=datetime.timezone(datetime.timedelta(hours=7))
t1=blk_ts(131959349); t2=blk_ts(131962334)
def fmt(ts): return datetime.datetime.fromtimestamp(ts,tz).strftime("%H:%M:%S")
print("block 131959349",fmt(t1)," block 131962334",fmt(t2)," interval_min",round((t2-t1)/60,2))
snap=json.load(open("onchain-snapshot.json"))
r31=json.load(open("run-2026-11-06-1301-reread-lean.json"))
r33=json.load(open("run-2026-11-06-1331-reread-lean.json"))
print("r31 block",r31["block"],"r33 block",r33["block"])
iv=(t2-t1)/60
# supply view: prefer totalSupply else totalMinted else freeMinted
def supply(d):
    for k in ("totalSupply","totalMinted","freeMinted"):
        if d.get(k) is not None: return k,d[k]
    return None,None
for name in sorted(r33["reread"].keys()):
    a=r31["reread"].get(name,{}); b=r33["reread"][name]
    ka,va=supply(a); kb,vb=supply(b)
    e=snap["contracts"].get(name,{})
    prev_rate=e.get("currentRatePerMin")
    if va is not None and vb is not None:
        d=vb-va; rate=d/iv; ratio=(rate/prev_rate) if prev_rate else None
        print(f"{name}: {ka} {va}->{vb} (+{d}, {rate:.3f}/mnt, prev {prev_rate}, ratio {ratio if ratio is None else round(ratio,2)}x, >=20:{d>=20}, vel_pass:{d>=20 and ratio is not None and ratio>=1.5})")
    else:
        print(f"{name}: read-fail (1301 {ka}={va}, 1331 {kb}={vb}) snap totalSupply={e.get('totalSupply')} status={e.get('status')}")
print("--- track_c changes vs 1301 ---")
for name in sorted(r33["track_c"].keys()):
    a=r31["track_c"].get(name,{}); b=r33["track_c"][name]
    diff={k:(a.get(k),b.get(k)) for k in set(a)|set(b) if a.get(k)!=b.get(k)}
    if diff: print(name, diff)
    else: print(name, "no change")
print("--- StarAgent snapshot entry ---")
print(json.dumps(snap["contracts"].get("StarAgent-7d39",{}), indent=1)[:2000])
